import ctypes
from ._ffi_client import (FfiClient, FfiHandle)
from ._proto import ffi_pb2 as proto_ffi
from ._proto import audio_frame_pb2 as proto_audio_frame


class AudioFrame():
    def __init__(self, info: proto_audio_frame.AudioFrameBufferInfo, ffi_handle: FfiHandle):
        self._info = info
        self._ffi_handle = ffi_handle

        data_len = self.num_channels * self.samples_per_channel
        self.data = ctypes.cast(info.data_ptr,
                                ctypes.POINTER(ctypes.c_int16 * data_len)).contents

    @staticmethod
    def create(sample_rate: int, num_channels: int, samples_per_channel: int):
        # TODO(theomonnom): There should be no problem to directly send audio date from a Python created ctypes buffer
        req = proto_ffi.FfiRequest()
        req.alloc_audio_buffer.sample_rate = sample_rate
        req.alloc_audio_buffer.num_channels = num_channels
        req.alloc_audio_buffer.samples_per_channel = samples_per_channel

        ffi_client = FfiClient()
        resp = ffi_client.request(req)

        info = resp.alloc_audio_buffer.buffer
        ffi_handle = FfiHandle(info.handle.id)

        return AudioFrame(info, ffi_handle)

    @property
    def sample_rate(self) -> int:
        return self._info.sample_rate

    @property
    def num_channels(self) -> int:
        return self._info.num_channels

    @property
    def samples_per_channel(self) -> int:
        return self._info.samples_per_channel
