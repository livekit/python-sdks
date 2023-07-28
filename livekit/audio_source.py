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

from .audio_frame import AudioFrame

from ._ffi_client import FfiHandle, ffi_client
from ._proto import audio_frame_pb2 as proto_audio_frame
from ._proto import ffi_pb2 as proto_ffi


class AudioSource:
    def __init__(self) -> None:
        req = proto_ffi.FfiRequest()
        req.new_audio_source.type = proto_audio_frame.AudioSourceType.AUDIO_SOURCE_NATIVE

        resp = ffi_client.request(req)
        self._info = resp.new_audio_source.source
        self._ffi_handle = FfiHandle(self._info.handle.id)

    def capture_frame(self, frame: AudioFrame) -> None:
        req = proto_ffi.FfiRequest()

        req.capture_audio_frame.source_handle.id = self._ffi_handle.handle
        req.capture_audio_frame.buffer_handle.id = frame._ffi_handle.handle

        ffi_client.request(req)
