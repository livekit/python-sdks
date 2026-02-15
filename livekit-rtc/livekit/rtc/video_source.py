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

from __future__ import annotations

from ._ffi_client import FfiHandle, FfiClient
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video
from .video_frame import VideoFrame


class VideoSource:
    def __init__(self, width: int, height: int, *, is_screencast: bool = False) -> None:
        """
        Create a new video source.

        Args:
            width (int): Initial width of the video source.
            height (int): Initial height of the video source.
            is_screencast (bool, optional): Optimize the WebRTC pipeline for screen content.
                Defaults to False.

                When True, WebRTC will:

                - Maintain resolution under congestion by dropping frames instead of
                  downscaling (keeps text crisp)
                - Disable quality scaling and denoising to preserve text/UI readability
                - Guarantee a minimum 1200 kbps bitrate floor
                - Enable zero-hertz mode, stopping frame transmission when the screen
                  is static to save bandwidth
                - Set content type to screen, adjusting encoder configuration throughout
                  the pipeline (VP9 inter-layer prediction, simulcast layer allocation, etc.)
        """
        req = proto_ffi.FfiRequest()
        req.new_video_source.type = proto_video.VideoSourceType.VIDEO_SOURCE_NATIVE
        req.new_video_source.resolution.width = width
        req.new_video_source.resolution.height = height
        req.new_video_source.is_screencast = is_screencast

        resp = FfiClient.instance.request(req)
        self._info = resp.new_video_source.source
        self._ffi_handle = FfiHandle(self._info.handle.id)

    def capture_frame(
        self,
        frame: VideoFrame,
        *,
        timestamp_us: int = 0,
        rotation: proto_video.VideoRotation.ValueType = proto_video.VideoRotation.VIDEO_ROTATION_0,
    ) -> None:
        req = proto_ffi.FfiRequest()
        req.capture_video_frame.source_handle = self._ffi_handle.handle
        req.capture_video_frame.buffer.CopyFrom(frame._proto_info())
        req.capture_video_frame.rotation = rotation
        req.capture_video_frame.timestamp_us = timestamp_us
        FfiClient.instance.request(req)

    async def aclose(self) -> None:
        self._ffi_handle.dispose()
