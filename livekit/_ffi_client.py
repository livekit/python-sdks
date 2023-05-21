import ctypes, sys, os
import livekit._proto.ffi_pb2 as proto 

basedir = os.path.abspath(os.path.dirname(__file__))
if sys.platform == "win32":
    libfile = 'livekit_ffi.dll'
elif sys.platform == "darwin":
    libfile = 'liblivekit_ffi.dylib'
else:
    libfile = 'liblivekit_ffi.so' 
libpath = os.path.join(basedir, libfile)

ffi_lib = ctypes.CDLL(libpath)

INVALID_HANDLE = 0

class FfiClient:
    def __init__(self):
        pass

    def request(self, req: proto.FFIRequest) -> proto.FFIResponse: 
        pass

class FfiHandle:
    handle = INVALID_HANDLE

    def __init__(self, handle: int):
        self.handle = handle

    def __del__(self):
        if self.handle != INVALID_HANDLE:
            assert(ffi_lib.livekit_ffi_drop_handle(self.handle))