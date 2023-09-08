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
from contextlib import contextmanager
from typing import Callable, Generic, List, TypeVar

import pkg_resources

from ._proto import ffi_pb2 as proto_ffi


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
    """ Queue where we can push events from another thread and 
    pop them from an event_loop."""

    def __init__(self, maxsize: int = 0) -> None:
        # Get the current event loop where the queue is created
        self._loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue[T](maxsize=maxsize)

    def put(self, item: T):
        self._loop.call_soon_threadsafe(self._queue.put_nowait, item)

    async def get(self) -> T:
        if self._loop != asyncio.get_running_loop():
            raise RuntimeError(f'{self!r} is bound to a different event loop')

        return await self._queue.get()

    async def wait_for(self, fnc: Callable[[T], bool]) \
            -> T:
        """ Wait for an event that matches the given function.
        The previous events are discarded.
        """

        while True:
            event = await self.get()
            if fnc(event):
                return event


@ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t)
def ffi_event_callback(data_ptr: ctypes.POINTER(ctypes.c_uint8),  # type: ignore
                       data_len: ctypes.c_size_t) -> None:
    event_data = bytes(data_ptr[:int(data_len)])
    event = proto_ffi.FfiEvent()
    event.ParseFromString(event_data)
    ffi_client._push_event(event)


class FfiClient:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subscribers: List[FfiQueue[proto_ffi.FfiEvent]] = []

        # initialize request
        req = proto_ffi.FfiRequest()
        cb_callback = int(ctypes.cast(
            ffi_event_callback, ctypes.c_void_p).value)  # type: ignore
        req.initialize.event_callback_ptr = cb_callback
        self.request(req)

    def subscribe(self) -> FfiQueue[proto_ffi.FfiEvent]:
        with self._lock:
            queue = FfiQueue[proto_ffi.FfiEvent]()
            self._subscribers.append(queue)
            return queue

    def unsubscribe(self, queue: FfiQueue[proto_ffi.FfiEvent]) -> None:
        with self._lock:
            self._subscribers.remove(queue)

    @contextmanager
    def observe(self):
        queue = self.subscribe()
        try:
            yield queue
        finally:
            self.unsubscribe(queue)

    def _push_event(self, event: proto_ffi.FfiEvent) -> None:
        # emit to subscribers (all queue, like a spmc)
        # this function is called from an undefined thread (from the Rust Tokio runtime)
        with self._lock:
            for queue in self._subscribers:
                queue.put(event)

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
