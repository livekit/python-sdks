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

import asyncio
import ctypes
import os
import platform
import threading
from typing import Generic, List, Optional, TypeVar

import pkg_resources

from ._proto import ffi_pb2 as proto_ffi
from ._utils import Queue


def get_ffi_lib_path():
    # allow to override the lib path using an env var
    libpath = os.environ.get("LIVEKIT_LIB_PATH", "").strip()
    if libpath:
        return libpath

    if platform.system() == "Linux":
        libname = "liblivekit_ffi.so"
    elif platform.system() == "Darwin":
        libname = "liblivekit_ffi.dylib"
    elif platform.system() == "Windows":
        libname = "livekit_ffi.dll"
    else:
        raise Exception(
            f"no ffi library found for platform {platform.system()}. \
                Set LIVEKIT_LIB_PATH to specify a the lib path")

    libpath = pkg_resources.resource_filename(
        'livekit', os.path.join('resources', libname))
    return libpath


ffi_lib = ctypes.CDLL(get_ffi_lib_path())

# C function types
ffi_lib.livekit_ffi_request.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)),
    ctypes.POINTER(ctypes.c_size_t)
]
ffi_lib.livekit_ffi_request.restype = ctypes.c_uint64

ffi_lib.livekit_ffi_drop_handle.argtypes = [ctypes.c_uint64]
ffi_lib.livekit_ffi_drop_handle.restype = ctypes.c_bool

INVALID_HANDLE = 0


class FfiHandle:
    def __init__(self, handle: int) -> None:
        self.handle = handle

    def __del__(self):
        if self.handle != INVALID_HANDLE:
            assert ffi_lib.livekit_ffi_drop_handle(
                ctypes.c_uint64(self.handle))


T = TypeVar('T')


class FfiQueue(Generic[T]):
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subscribers: List[tuple[
            Queue[T], asyncio.AbstractEventLoop]] = []

    def put(self, item: T) -> None:
        with self._lock:
            for queue, loop in self._subscribers:
                loop.call_soon_threadsafe(queue.put_nowait, item)

    def subscribe(self, loop: Optional[asyncio.AbstractEventLoop] = None) \
            -> Queue[T]:
        with self._lock:
            queue = Queue[T]()
            loop = loop or asyncio.get_event_loop()
            self._subscribers.append((queue, loop))
            return queue

    def unsubscribe(self, queue: Queue[T]) -> None:
        with self._lock:
            # looping here is ok, since we don't expect a lot of subscribers
            for i, (q, _) in enumerate(self._subscribers):
                if q == queue:
                    self._subscribers.pop(i)
                    break


@ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t)
def ffi_event_callback(data_ptr: ctypes.POINTER(ctypes.c_uint8),  # type: ignore
                       data_len: ctypes.c_size_t) -> None:
    event_data = bytes(data_ptr[:int(data_len)])
    event = proto_ffi.FfiEvent()
    event.ParseFromString(event_data)
    ffi_client.queue.put(event)


class FfiClient:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._queue = FfiQueue[proto_ffi.FfiEvent]()

        # initialize request
        req = proto_ffi.FfiRequest()
        cb_callback = int(ctypes.cast(
            ffi_event_callback, ctypes.c_void_p).value)  # type: ignore
        req.initialize.event_callback_ptr = cb_callback
        self.request(req)

    @property
    def queue(self) -> FfiQueue[proto_ffi.FfiEvent]:
        return self._queue

    def request(self, req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        proto_data = req.SerializeToString()
        proto_len = len(proto_data)
        data = (ctypes.c_ubyte * proto_len)(*proto_data)

        resp_ptr = ctypes.POINTER(ctypes.c_ubyte)()
        resp_len = ctypes.c_size_t()
        handle = ffi_lib.livekit_ffi_request(
            data, proto_len, ctypes.byref(resp_ptr), ctypes.byref(resp_len))

        resp_data = bytes(resp_ptr[:resp_len.value])
        resp = proto_ffi.FfiResponse()
        resp.ParseFromString(resp_data)

        FfiHandle(handle)
        return resp


ffi_client = FfiClient()
