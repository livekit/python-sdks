# Copyright 2026 LiveKit, Inc.
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

from dataclasses import dataclass

from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video
from ._utils import get_address


@dataclass(frozen=True)
class EncodedVideoFrame:
    """One complete encoded access unit, without a container or RTP headers.

    ``data`` must contain a single frame in ``codec`` (Annex B for H.264/H.265).
    ``timestamp_us`` is its capture time in microseconds, increasing along the
    stream. The codec must match the publication and remain fixed for its lifetime.
    """

    data: bytes
    width: int
    height: int
    codec: proto_video.VideoCodec.ValueType
    frame_type: proto_video.EncodedFrameType.ValueType
    timestamp_us: int
    metadata: proto_video.FrameMetadata | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.data, bytes):
            raise TypeError("encoded frame data must be bytes")
        if not self.data:
            raise ValueError("encoded frame data must not be empty")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("encoded frame dimensions must be positive")


@dataclass(frozen=True)
class EncodedRateControl:
    """The latest bitrate and frame-rate targets requested by WebRTC."""

    target_bitrate_bps: int
    framerate_fps: float


@dataclass(frozen=True)
class EncodedVideoSourceFeedback:
    """Encoder feedback consumed since the previous call to ``take_feedback``."""

    keyframe_requested: bool
    rate_control: EncodedRateControl | None


class EncodedVideoSource:
    """Publish pre-encoded video without decoding or re-encoding it.

    Create a ``LocalVideoTrack`` with this source and publish it with a matching
    ``video_codec``, ``video_encoder=ENCODER_BACKEND_PRE_ENCODED`` and
    ``simulcast=False``. Feed complete access units at the intended playback rate;
    this source does not pace or buffer a file for playback.

    Poll ``take_feedback`` and forward keyframe and rate-control requests to the
    upstream encoder. A demuxer alone cannot produce a new keyframe or adapt the
    encoded bitrate. Call ``capture_frame`` from a single producer.
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a source with the initial encoded frame dimensions."""
        if width <= 0 or height <= 0:
            raise ValueError("encoded source dimensions must be positive")
        req = proto_ffi.FfiRequest()
        req.new_video_source.type = proto_video.VideoSourceType.VIDEO_SOURCE_ENCODED
        req.new_video_source.resolution.width = width
        req.new_video_source.resolution.height = height
        resp = FfiClient.instance.request(req)
        self._ffi_handle = FfiHandle(resp.new_video_source.source.handle.id)

    def capture_frame(self, frame: EncodedVideoFrame) -> bool:
        """Submit a frame; return whether the native source accepted it.

        The native implementation copies the payload before this call returns.
        Acceptance does not guarantee delivery to subscribers.
        """
        req = proto_ffi.FfiRequest()
        capture = req.capture_encoded_video_frame
        capture.source_handle = self._ffi_handle.handle
        capture.buffer.data_ptr = get_address(frame.data)
        capture.buffer.data_len = len(frame.data)
        capture.codec = frame.codec
        capture.frame_type = frame.frame_type
        capture.width = frame.width
        capture.height = frame.height
        capture.timestamp_us = frame.timestamp_us
        if frame.metadata is not None:
            capture.metadata.CopyFrom(frame.metadata)
        response: proto_ffi.FfiResponse = FfiClient.instance.request(req)
        return response.capture_encoded_video_frame.accepted

    def take_feedback(self) -> EncodedVideoSourceFeedback:
        """Consume pending feedback, including requests from late subscribers."""
        req = proto_ffi.FfiRequest()
        req.take_encoded_video_source_feedback.source_handle = self._ffi_handle.handle
        feedback = FfiClient.instance.request(req).take_encoded_video_source_feedback
        rate_control = None
        if feedback.HasField("rate_control"):
            rate_control = EncodedRateControl(
                target_bitrate_bps=feedback.rate_control.target_bitrate_bps,
                framerate_fps=feedback.rate_control.framerate_fps,
            )
        return EncodedVideoSourceFeedback(feedback.keyframe_requested, rate_control)

    async def aclose(self) -> None:
        """Release the native source handle."""
        self._ffi_handle.dispose()
