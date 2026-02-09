# Copyright 2023 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import signal
import asyncio
import sys
from contextlib import ExitStack
import ctypes
import importlib.resources
from .version import __version__
import logging
import os
import platform
import atexit
import threading
from typing import Callable, Generic, List, Optional, TypeVar

from ._proto import ffi_pb2 as proto_ffi
from ._utils import Queue, classproperty
from .log import logger

_resource_files = ExitStack()
atexit.register(_resource_files.close)


def _lib_name():
    if platform.system() == "Linux":
        return "liblivekit_ffi.so"
    elif platform.system() == "Darwin":
        return "liblivekit_ffi.dylib"
    elif platform.system() == "Windows":
        return "livekit_ffi.dll"
    return None


def get_ffi_lib():
    # allow to override the lib path using an env var
    libpath = os.environ.get("LIVEKIT_LIB_PATH", "").strip()
    if libpath:
        return ctypes.CDLL(libpath)

    libname = _lib_name()
    if libname is None:
        raise Exception(
            f"no ffi library found for platform {platform.system()}. "
            "Set LIVEKIT_LIB_PATH to specify the lib path"
        )

    res = importlib.resources.files("livekit.rtc.resources") / libname
    ctx = importlib.resources.as_file(res)
    path = _resource_files.enter_context(ctx)
    return ctypes.CDLL(str(path))


ffi_cb_fnc = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t)

INVALID_HANDLE = 0


class FfiHandle:
    def __init__(self, handle: int) -> None:
        self.handle = handle
        self._disposed = False

    def __del__(self):
        self.dispose()

    @property
    def disposed(self) -> bool:
        return self._disposed

    def dispose(self) -> None:
        if self.handle != INVALID_HANDLE and not self._disposed:
            self._disposed = True
            assert FfiClient.instance._ffi_lib.livekit_ffi_drop_handle(ctypes.c_uint64(self.handle))

    def __repr__(self) -> str:
        return f"FfiHandle({self.handle})"


T = TypeVar("T")


class FfiQueue(Generic[T]):
    def __init__(self) -> None:
        self._lock = threading.RLock()
        # Format: (queue, loop, filter_fn or None)
        self._subscribers: List[
            tuple[Queue[T], asyncio.AbstractEventLoop, Optional[Callable[[T], bool]]]
        ] = []

    def put(self, item: T) -> None:
        with self._lock:
            for queue, loop, filter_fn in self._subscribers:
                # If filter provided, skip items that don't match
                if filter_fn is not None:
                    try:
                        if not filter_fn(item):
                            continue
                    except Exception:
                        pass  # On filter error, deliver the item

                try:
                    loop.call_soon_threadsafe(queue.put_nowait, item)
                except Exception as e:
                    # this could happen if user closes the runloop without unsubscribing first
                    # it's not good when it does occur, but we should not fail the entire runloop
                    logger.error("error putting to queue: %s", e)

    def subscribe(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        filter_fn: Optional[Callable[[T], bool]] = None,
    ) -> Queue[T]:
        """Subscribe to FFI events.

        Args:
            loop: Event loop to use (defaults to current).
            filter_fn: Optional filter function. If provided, only items where
                      filter_fn(item) returns True will be delivered.
                      If None, receives all events (original behavior).

        Returns:
            Queue to receive events from.
        """
        with self._lock:
            queue = Queue[T]()
            loop = loop or asyncio.get_event_loop()
            self._subscribers.append((queue, loop, filter_fn))
            return queue

    def unsubscribe(self, queue: Queue[T]) -> None:
        with self._lock:
            # looping here is ok, since we don't expect a lot of subscribers
            for i, (q, _, _) in enumerate(self._subscribers):
                if q == queue:
                    self._subscribers.pop(i)
                    break


@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t)
def ffi_event_callback(
    data_ptr: ctypes.POINTER(ctypes.c_uint8),  # type: ignore
    data_len: ctypes.c_size_t,
) -> None:
    event_data = ctypes.string_at(data_ptr, int(data_len))
    event = proto_ffi.FfiEvent()
    event.ParseFromString(event_data)

    which = event.WhichOneof("message")
    if which == "logs":
        for record in event.logs.records:
            level = to_python_level(record.level)
            debug_env = os.environ.get("LIVEKIT_RTC_DEBUG", "").strip().lower()
            rtc_debug = debug_env in ("true", "1")

            if level == logging.DEBUG and not rtc_debug:
                # ignore the rtc debug logs by default
                if record.target == "libwebrtc" or record.target.startswith("livekit"):
                    continue

            if level is not None:
                logger.log(
                    level,
                    "%s:%s:%s - %s",
                    record.target,
                    record.line,
                    record.module_path,
                    record.message,
                )

        return  # no need to queue the logs
    elif which == "panic":
        print("FFI Panic: ", event.panic.message, file=sys.stderr, flush=True)
        # We are in a unrecoverable state, terminate the process
        os.kill(os.getpid(), signal.SIGTERM)
        return

    FfiClient.instance.queue.put(event)


def to_python_level(level: proto_ffi.LogLevel.ValueType) -> Optional[int]:
    if level == proto_ffi.LogLevel.LOG_ERROR:
        return logging.ERROR
    elif level == proto_ffi.LogLevel.LOG_WARN:
        return logging.WARN
    elif level == proto_ffi.LogLevel.LOG_INFO:
        return logging.INFO
    elif level == proto_ffi.LogLevel.LOG_DEBUG:
        return logging.DEBUG
    elif level == proto_ffi.LogLevel.LOG_TRACE:
        # Don't show TRACE logs inside DEBUG, it is too verbos
        # Python's logging doesn't have a TRACE level
        # return logging.DEBUG
        pass

    return None


class FfiClient:
    _instance: Optional["FfiClient"] = None

    @classproperty
    def instance(cls) -> "FfiClient":
        if cls._instance is None:
            cls._instance = FfiClient()
        return cls._instance

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._queue = FfiQueue[proto_ffi.FfiEvent]()

        try:
            self._ffi_lib = get_ffi_lib()
        except Exception as e:
            libname = _lib_name() or "livekit_ffi"
            raise ImportError(
                "failed to load %s: %s\n"
                "Install the livekit package with: pip install livekit\n"
                "Or set LIVEKIT_LIB_PATH to the path of the native library." % (libname, e)
            ) from None
        self._ffi_lib.livekit_ffi_initialize.argtypes = [
            ffi_cb_fnc,
            ctypes.c_bool,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self._ffi_lib.livekit_ffi_request.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)),
            ctypes.POINTER(ctypes.c_size_t),
        ]
        self._ffi_lib.livekit_ffi_request.restype = ctypes.c_uint64
        self._ffi_lib.livekit_ffi_drop_handle.argtypes = [ctypes.c_uint64]
        self._ffi_lib.livekit_ffi_drop_handle.restype = ctypes.c_bool
        self._ffi_lib.livekit_ffi_dispose.argtypes = []
        self._ffi_lib.livekit_ffi_dispose.restype = None

        self._ffi_lib.livekit_ffi_initialize(
            ffi_event_callback, True, b"python", __version__.encode("ascii")
        )

        ffi_lib = self._ffi_lib

        @atexit.register
        def _dispose_lk_ffi():
            ffi_lib.livekit_ffi_dispose()

    @property
    def queue(self) -> FfiQueue[proto_ffi.FfiEvent]:
        return self._queue

    def request(self, req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        proto_data = req.SerializeToString()
        proto_len = len(proto_data)
        data = (ctypes.c_ubyte * proto_len)(*proto_data)

        resp_ptr = ctypes.POINTER(ctypes.c_ubyte)()
        resp_len = ctypes.c_size_t()
        handle = self._ffi_lib.livekit_ffi_request(
            data, proto_len, ctypes.byref(resp_ptr), ctypes.byref(resp_len)
        )
        assert handle != INVALID_HANDLE

        resp_data = ctypes.string_at(resp_ptr, resp_len.value)
        resp = proto_ffi.FfiResponse()
        resp.ParseFromString(resp_data)
        FfiHandle(handle).dispose()
        return resp
