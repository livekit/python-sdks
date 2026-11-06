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
    metadata: proto_video_frame.FrameMetadata | None = None

    dropped_frames: int = 0
    """
    Frames this stream decoded but never delivered, counted since the stream
    was created.

    A frame is dropped when the SDK's internal queue overflows because this
    application did not read frames fast enough. No WebRTC stat reports the
    loss -- ``framesDecoded`` counts these frames and ``framesDropped`` does
    not -- so this counter is the only way to observe it.

    The value is cumulative and monotonic: compare it against the previous
    event's to see how many frames were lost in between. It stays at zero when
    the SDK in use predates the counter.
    """


def _close_discarded(event: VideoFrameEvent | None) -> None:
    if event is not None:
        event.frame.close()


def _dropped_frames(frame_received: proto_video_frame.VideoFrameReceived) -> int:
    """
    Reads the dropped-frame counter, tolerating an SDK that predates it.

    The field arrived with the native counter; an older `livekit_ffi` does not
    define it, and reporting zero is the honest answer there -- we have no
    information either way.

    `getattr` rather than attribute access so this also builds against the
    generated stubs from before the field existed. Once the vendored
    `rust-sdks` is bumped past it, this can become a plain read.
    """
    return int(getattr(frame_received, "dropped_frames", 0))


class VideoStream:
    """VideoStream is a stream of video frames received from a RemoteTrack.

    With ``zero_copy=True`` each frame reads the SDK's own pixel buffer instead
    of a copy of it, which removes a full frame-sized copy per frame. The
    buffer belongs to the SDK and is only valid while the frame is open; see
    :meth:`VideoFrame.close` and the ``zero_copy`` argument.
    """

    def __init__(
        self,
        track: Track,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        capacity: int = 0,
        format: Optional[proto_video_frame.VideoBufferType.ValueType] = None,
        zero_copy: bool = False,
        **kwargs: Any,
    ) -> None:
        self._loop = loop or asyncio.get_event_loop()
        self._zero_copy = zero_copy
        # The most recent borrowed frame handed to the application. Closed when
        # the next one is requested, so a plain `async for` never leaks a
        # buffer even if the application does not close frames itself.
        self._borrowed: VideoFrame | None = None
        # Only subscribe to video_stream_event to avoid unnecessary memory allocations
        # from other event types (room_event, track_event, etc.)
        self._ffi_queue = FfiClient.instance.queue.subscribe(
            self._loop,
            filter_fn=lambda e: e.WhichOneof("message") == "video_stream_event",
        )
        # A borrowed frame evicted by a bounded queue has to be closed, or its
        # SDK buffer stays out until the collector gets to it.
        self._queue: RingQueue[VideoFrameEvent | None] = RingQueue(
            capacity, on_discard=_close_discarded if zero_copy else None
        )
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
        zero_copy: bool = False,
    ) -> VideoStream:
        return VideoStream(
            participant=participant,
            track_source=track_source,
            loop=loop,
            capacity=capacity,
            format=format,
            zero_copy=zero_copy,
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
        zero_copy: bool = False,
    ) -> VideoStream:
        return VideoStream(
            track=track,
            loop=loop,
            capacity=capacity,
            format=format,
            zero_copy=zero_copy,
        )

    def __del__(self) -> None:
        # Tolerate a half-built stream: if __init__ raised before subscribing
        # (a failed FFI request, say), there is nothing to unsubscribe, and
        # raising from __del__ only produces an unraisable-exception warning
        # that hides the original error.
        ffi_queue = getattr(self, "_ffi_queue", None)
        if ffi_queue is not None:
            FfiClient.instance.queue.unsubscribe(ffi_queue)

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
        video_stream_from_participant.participant_handle = participant._ffi_handle.handle
        video_stream_from_participant.type = proto_video_frame.VideoStreamType.VIDEO_STREAM_NATIVE
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
                frame_received = video_event.frame_received
                owned_buffer_info = frame_received.buffer
                if self._zero_copy:
                    frame = VideoFrame._borrow_owned_info(owned_buffer_info)
                else:
                    frame = VideoFrame._from_owned_info(owned_buffer_info)
                metadata: proto_video_frame.FrameMetadata | None = None
                if frame_received.HasField("metadata"):
                    metadata = proto_video_frame.FrameMetadata()
                    metadata.CopyFrom(frame_received.metadata)

                event = VideoFrameEvent(
                    frame=frame,
                    timestamp_us=frame_received.timestamp_us,
                    rotation=frame_received.rotation,
                    metadata=metadata,
                    dropped_frames=_dropped_frames(frame_received),
                )

                self._queue.put(event)
            elif video_event.HasField("eos"):
                break

        FfiClient.instance.queue.unsubscribe(self._ffi_queue)

    async def aclose(self) -> None:
        self._ffi_handle.dispose()
        await self._task
        self._release_borrowed()
        # Frames still queued hold SDK buffers; release them with the stream.
        while (queued := self._queue.get_nowait()) is not None:
            queued.frame.close()

    def _release_borrowed(self) -> None:
        """Closes the borrowed frame handed out last, if there is one."""
        if self._borrowed is not None:
            self._borrowed.close()
            self._borrowed = None

    def _is_event(self, e: proto_ffi.FfiEvent) -> bool:
        return e.video_stream_event.stream_handle == self._ffi_handle.handle

    def __aiter__(self) -> AsyncIterator[VideoFrameEvent]:
        return self

    async def __anext__(self) -> VideoFrameEvent:
        # Asking for the next frame ends the previous one's borrow. This is
        # what keeps a plain `async for` from accumulating SDK buffers when
        # the application never closes frames itself.
        self._release_borrowed()

        if self._task.done():
            raise StopAsyncIteration

        item = await self._queue.get()
        if item is None:
            raise StopAsyncIteration

        if self._zero_copy:
            self._borrowed = item.frame

        return item
