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

from ._ffi_client import FfiHandle, ffi_client
from ._proto import audio_frame_pb2 as proto_audio_frame
from ._proto import ffi_pb2 as proto_ffi
from .audio_frame import AudioFrame


class AudioSource:
    def __init__(self, sample_rate: int, num_channels: int) -> None:
        req = proto_ffi.FfiRequest()
        req.new_audio_source.type = proto_audio_frame.AudioSourceType.AUDIO_SOURCE_NATIVE
        req.new_audio_source.sample_rate = sample_rate
        req.new_audio_source.num_channels = num_channels

        resp = ffi_client.request(req)
        self._info = resp.new_audio_source.source
        self._ffi_handle = FfiHandle(self._info.handle.id)

    async def capture_frame(self, frame: AudioFrame) -> None:
        req = proto_ffi.FfiRequest()

        req.capture_audio_frame.source_handle = self._ffi_handle.handle
        req.capture_audio_frame.buffer.CopyFrom(frame._proto_info())
        resp = ffi_client.request(req)
        future: asyncio.Future[proto_audio_frame.CaptureAudioFrameCallback] = \
            asyncio.Future()

        @ffi_client.on('capture_audio_frame')
        def on_capture_audio_frame(cb: proto_audio_frame.CaptureAudioFrameCallback):
            if cb.async_id == resp.capture_audio_frame.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'capture_audio_frame', on_capture_audio_frame)

        cb = await future
        if cb.error:
            raise Exception(cb.error)
