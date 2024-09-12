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

import asyncio
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional

from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from ._proto.track_pb2 import TrackSource
from ._utils import RingQueue, task_done_logger
from .participant import Participant
from .track import Track
from .video_frame import VideoFrame


@dataclass
class VideoFrameEvent:
    frame: VideoFrame
    timestamp_us: int
    rotation: proto_video_frame.VideoRotation


class VideoStream:
    """VideoStream is a stream of video frames received from a RemoteTrack."""

    def __init__(
        self,
        track: Track,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        capacity: int = 0,
        format: Optional[proto_video_frame.VideoBufferType.ValueType] = None,
        **kwargs,
    ) -> None:
        self._loop = loop or asyncio.get_event_loop()
        self._ffi_queue = FfiClient.instance.queue.subscribe(self._loop)
        self._queue: RingQueue[VideoFrameEvent | None] = RingQueue(capacity)
        self._track: Track | None = track
        self._format = format
        self._capacity = capacity
        self._format = format
        stream: Any = None
        if "participant" in kwargs:
            stream = self._create_owned_stream_from_participant(
                participant=kwargs["participant"], track_source=kwargs["track_source"]
            )
        else:
            stream = self._create_owned_stream()

        self._ffi_handle = FfiHandle(stream.handle.id)
        self._info = stream.info

        self._task = self._loop.create_task(self._run())
        self._task.add_done_callback(task_done_logger)

    @classmethod
    def from_participant(
        cls,
        *,
        participant: Participant,
        track_source: TrackSource.ValueType,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        format: Optional[proto_video_frame.VideoBufferType.ValueType] = None,
        capacity: int = 0,
    ) -> VideoStream:
        return VideoStream(
            participant=participant,
            track_source=track_source,
            loop=loop,
            capacity=capacity,
            format=format,
            track=None,  # type: ignore
        )

    @classmethod
    def from_track(
        cls,
        *,
        track: Track,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        format: Optional[proto_video_frame.VideoBufferType.ValueType] = None,
        capacity: int = 0,
    ) -> VideoStream:
        return VideoStream(
            track=track,
            loop=loop,
            capacity=capacity,
            format=format,
        )

    def __del__(self) -> None:
        FfiClient.instance.queue.unsubscribe(self._ffi_queue)

    def _create_owned_stream(self) -> Any:
        assert self._track is not None
        req = proto_ffi.FfiRequest()
        new_video_stream = req.new_video_stream
        new_video_stream.track_handle = self._track._ffi_handle.handle
        new_video_stream.type = proto_video_frame.VideoStreamType.VIDEO_STREAM_NATIVE
        if self._format is not None:
            new_video_stream.format = self._format
        new_video_stream.normalize_stride = True
        resp = FfiClient.instance.request(req)
        return resp.new_video_stream.stream

    def _create_owned_stream_from_participant(
        self, participant: Participant, track_source: TrackSource.ValueType
    ) -> Any:
        req = proto_ffi.FfiRequest()
        video_stream_from_participant = req.video_stream_from_participant
        video_stream_from_participant.participant_handle = (
            participant._ffi_handle.handle
        )
        video_stream_from_participant.type = (
            proto_video_frame.VideoStreamType.VIDEO_STREAM_NATIVE
        )
        video_stream_from_participant.track_source = track_source
        video_stream_from_participant.normalize_stride = True
        if self._format is not None:
            video_stream_from_participant.format = self._format
        resp = FfiClient.instance.request(req)
        return resp.video_stream_from_participant.stream

    async def _run(self) -> None:
        while True:
            event = await self._ffi_queue.wait_for(self._is_event)
            video_event = event.video_stream_event

            if video_event.HasField("frame_received"):
                owned_buffer_info = video_event.frame_received.buffer
                frame = VideoFrame._from_owned_info(owned_buffer_info)

                event = VideoFrameEvent(
                    frame=frame,
                    timestamp_us=video_event.frame_received.timestamp_us,
                    rotation=video_event.frame_received.rotation,
                )

                self._queue.put(event)
            elif video_event.HasField("eos"):
                break

        FfiClient.instance.queue.unsubscribe(self._ffi_queue)

    async def aclose(self) -> None:
        self._ffi_handle.dispose()
        await self._task

    def _is_event(self, e: proto_ffi.FfiEvent) -> bool:
        return e.video_stream_event.stream_handle == self._ffi_handle.handle

    def __aiter__(self) -> AsyncIterator[VideoFrameEvent]:
        return self

    async def __anext__(self) -> VideoFrameEvent:
        if self._task.done():
            raise StopAsyncIteration

        item = await self._queue.get()
        if item is None:
            raise StopAsyncIteration

        return item
