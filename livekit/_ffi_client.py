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
import platform
import threading

import pkg_resources
from pyee.asyncio import EventEmitter

from ._proto import ffi_pb2 as proto_ffi

os = platform.system().lower()
arch = platform.machine().lower()
lib_path = 'lib/{}/{}'.format(os, arch)

if os == "windows":
    lib_file = 'livekit_ffi.dll'
elif os == "darwin":
    lib_file = 'liblivekit_ffi.dylib'
else:
    lib_file = 'liblivekit_ffi.so'

libpath = pkg_resources.resource_filename('livekit', lib_path + '/' + lib_file)

ffi_lib = ctypes.CDLL(libpath)

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


@ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t)
def ffi_event_callback(data_ptr: ctypes.POINTER(ctypes.c_uint8),  # type: ignore
                       data_len: ctypes.c_size_t) -> None:
    event_data = bytes(data_ptr[:int(data_len)])
    event = proto_ffi.FfiEvent()
    event.ParseFromString(event_data)

    with ffi_client._lock:
        loop = ffi_client._event_loop

    loop.call_soon_threadsafe(dispatch_event, event)


def dispatch_event(event: proto_ffi.FfiEvent) -> None:
    which = str(event.WhichOneof('message'))
    ffi_client.emit(which, getattr(event, which))


class FfiClient(EventEmitter):
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()

        req = proto_ffi.FfiRequest()
        cb_callback = int(ctypes.cast(
            ffi_event_callback, ctypes.c_void_p).value)  # type: ignore
        req.initialize.event_callback_ptr = cb_callback
        self.request(req)

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        with self._lock:
            self._event_loop = loop

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


class FfiHandle:
    def __init__(self, handle: int) -> None:
        self.handle = handle

    def __del__(self):
        if self.handle != INVALID_HANDLE:
            assert ffi_lib.livekit_ffi_drop_handle(
                ctypes.c_uint64(self.handle))


ffi_client = FfiClient()
ffi_client.set_event_loop(asyncio.get_event_loop())
