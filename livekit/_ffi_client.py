from ctypes import *
import platform
from ._proto import ffi_pb2 as proto_ffi
from ._proto import room_pb2 as proto_room
from pyee.asyncio import EventEmitter
import pkg_resources
import asyncio
import threading
import logging

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

ffi_lib = CDLL(libpath)

# C function types
ffi_lib.livekit_ffi_request.argtypes = [
    POINTER(c_ubyte), c_size_t, POINTER(POINTER(c_ubyte)), POINTER(c_size_t)]
ffi_lib.livekit_ffi_request.restype = c_size_t

ffi_lib.livekit_ffi_drop_handle.argtypes = [c_size_t]
ffi_lib.livekit_ffi_drop_handle.restype = c_bool

INVALID_HANDLE = 0


@CFUNCTYPE(c_void_p, POINTER(c_uint8), c_size_t)
def ffi_event_callback(data_ptr: POINTER(c_uint8), data_len: c_size_t):
    event_data = bytes(data_ptr[:data_len])
    event = proto_ffi.FfiEvent()
    event.ParseFromString(event_data)

    ffi_client = FfiClient()
    with ffi_client._lock:
        loop = ffi_client._event_loop

    loop.call_soon_threadsafe(dispatch_event, event)


def dispatch_event(event: proto_ffi.FfiEvent):
    ffi_client = FfiClient()
    which = event.WhichOneof('message')
    ffi_client.emit(which, getattr(event, which))


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FfiClient(EventEmitter, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._event_loop = None

        req = proto_ffi.FfiRequest()
        req.initialize.event_callback_ptr = cast(
            ffi_event_callback, c_void_p).value
        self.request(req)

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        with self._lock:
            if self._event_loop is not None and self._event_loop != loop:
                logging.warning(
                    "FfiClient is now using a different asyncio event_loop")

            self._event_loop = loop

    def request(self, req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        data = req.SerializeToString()
        data_len = len(data)
        data = (c_ubyte * data_len)(*data)

        resp_ptr = POINTER(c_ubyte)()
        resp_len = c_size_t()
        handle = ffi_lib.livekit_ffi_request(
            data, data_len, byref(resp_ptr), byref(resp_len))

        resp_data = bytes(resp_ptr[:resp_len.value])
        resp = proto_ffi.FfiResponse()
        resp.ParseFromString(resp_data)

        FfiHandle(handle)
        return resp


class FfiHandle:
    handle = INVALID_HANDLE

    def __init__(self, handle: int):
        self.handle = handle

    def __del__(self):
        if self.handle != INVALID_HANDLE:
            assert ffi_lib.livekit_ffi_drop_handle(
                c_size_t(self.handle))
