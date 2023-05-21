from ctypes import *
import sys, os
import livekit._proto.ffi_pb2 as proto 

basedir = os.path.abspath(os.path.dirname(__file__))
if sys.platform == "win32":
    libfile = 'livekit_ffi.dll'
elif sys.platform == "darwin":
    libfile = 'liblivekit_ffi.dylib'
else:
    libfile = 'liblivekit_ffi.so' 
libpath = os.path.join(basedir, libfile)

ffi_lib = CDLL(libpath)

# C function types
ffi_lib.livekit_ffi_request.argtypes = [POINTER(c_ubyte), c_size_t, POINTER(POINTER(c_ubyte)), c_size_t]
ffi_lib.livekit_ffi_request.restype = c_size_t

ffi_lib.livekit_ffi_drop_handle.argtypes = [c_size_t]
ffi_lib.livekit_ffi_drop_handle.restype = c_bool

INVALID_HANDLE = 0

class FfiClient:
    def __init__(self):
        pass

    def request(self, req: proto.FFIRequest) -> proto.FFIResponse: 
        data = bytearray(req.SerializeToString())
        data_len = len(data)
        resp_ptr = POINTER(c_ubyte)()
        resp_len = c_size_t()
        handle = ffi_lib.livekit_ffi_request(data, data_len, byref(resp_ptr), byref(resp_len))

        resp_data = bytearray(resp_ptr[:resp_len.value])
        resp = proto.FFIResponse()
        resp.ParseFromString(resp_data)

        FfiHandle(handle)
        return resp

class FfiHandle:
    handle = INVALID_HANDLE

    def __init__(self, handle: int):
        self.handle = handle

    def __del__(self):
        if self.handle != INVALID_HANDLE:
            assert(ffi_lib.livekit_ffi_drop_handle(c_size_t(self.handle)))