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

from ._ffi_client import FfiHandle, ffi_client
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from .video_frame import VideoFrame


class VideoSource:
    def __init__(self) -> None:
        req = proto_ffi.FfiRequest()
        req.new_video_source.type = \
            proto_video_frame.VideoSourceType.VIDEO_SOURCE_NATIVE

        resp = ffi_client.request(req)
        self._info = resp.new_video_source.source
        self._ffi_handle = FfiHandle(self._info.handle.id)

    def capture_frame(self, frame: VideoFrame) -> None:
        req = proto_ffi.FfiRequest()
        req.capture_video_frame.source_handle = self._ffi_handle.handle
        req.capture_video_frame.buffer_handle = frame.buffer._ffi_handle.handle
        req.capture_video_frame.frame.rotation = frame.rotation
        req.capture_video_frame.frame.timestamp_us = frame.timestamp_us
        ffi_client.request(req)
