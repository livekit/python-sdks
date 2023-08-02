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

import ctypes

from ._ffi_client import FfiHandle, ffi_client
from ._proto import audio_frame_pb2 as proto_audio
from ._proto import ffi_pb2 as proto_ffi


class AudioFrame():
    def __init__(self, info: proto_audio.AudioFrameBufferInfo, ffi_handle: FfiHandle) -> None:
        self._info = info
        self._ffi_handle = ffi_handle

        data_len = self.num_channels * self.samples_per_channel
        self.data = ctypes.cast(info.data_ptr,
                                ctypes.POINTER(ctypes.c_int16 * data_len)).contents

    @staticmethod
    def create(sample_rate: int, num_channels: int, samples_per_channel: int) -> 'AudioFrame':
        # TODO(theomonnom): There should be no problem to directly send audio date from a Python created ctypes buffer
        req = proto_ffi.FfiRequest()
        req.alloc_audio_buffer.sample_rate = sample_rate
        req.alloc_audio_buffer.num_channels = num_channels
        req.alloc_audio_buffer.samples_per_channel = samples_per_channel

        resp = ffi_client.request(req)

        info = resp.alloc_audio_buffer.buffer
        ffi_handle = FfiHandle(info.handle.id)

        return AudioFrame(info, ffi_handle)

    def remix_and_resample(self, sample_rate: int, num_channels: int) -> 'AudioFrame':
        """ Resample the audio frame to the given sample rate and number of channels."""

        req = proto_ffi.FfiRequest()
        req.new_audio_resampler.CopyFrom(
            proto_audio.NewAudioResamplerRequest())

        resp = ffi_client.request(req)
        resampler_handle = FfiHandle(
            resp.new_audio_resampler.resampler.handle.id)

        resample_req = proto_ffi.FfiRequest()
        resample_req.remix_and_resample.resampler_handle = resampler_handle.handle
        resample_req.remix_and_resample.buffer_handle = self._ffi_handle.handle
        resample_req.remix_and_resample.sample_rate = sample_rate
        resample_req.remix_and_resample.num_channels = num_channels

        resp = ffi_client.request(resample_req)
        info = resp.remix_and_resample.buffer
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
