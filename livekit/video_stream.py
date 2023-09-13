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
from typing import Optional

from ._ffi_client import FfiHandle, ffi_client
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from ._utils import RingQueue
from .track import Track
from .video_frame import VideoFrame, VideoFrameBuffer


class VideoStream:
    def __init__(self, track: Track,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 capacity: int = 0) -> None:
        self._track = track
        self._loop = loop or asyncio.get_event_loop()
        self._ffi_queue = ffi_client.queue.subscribe(self._loop)
        self._queue: RingQueue[VideoFrame] = RingQueue(capacity)

        req = proto_ffi.FfiRequest()
        new_video_stream = req.new_video_stream
        new_video_stream.track_handle = track._ffi_handle.handle
        new_video_stream.type = proto_video_frame.VideoStreamType.VIDEO_STREAM_NATIVE
        resp = ffi_client.request(req)

        stream_info = resp.new_video_stream.stream
        self._ffi_handle = FfiHandle(stream_info.handle.id)
        self._info = stream_info.info

        self._task = self._loop.create_task(self._run())

    async def _run(self):
        while True:
            event = await self._ffi_queue.wait_for(self._is_event)
            video_event = event.video_stream_event

            if video_event.HasField('frame_received'):
                frame_info = video_event.frame_received.frame
                owned_buffer_info = video_event.frame_received.buffer

                frame = VideoFrame(frame_info.timestamp_us, frame_info.rotation,
                                   VideoFrameBuffer.create(owned_buffer_info))
                self._queue.put(frame)
            elif video_event.HasField('eos'):
                break

    async def close(self):
        del self._ffi_handle
        await self._task

    def __aiter__(self):
        return self

    def _is_event(self, e: proto_ffi.FfiEvent):
        return e.video_stream_event.stream_handle == self._ffi_handle.handle

    async def __anext__(self):
        if self._task.done():
            raise StopAsyncIteration
        return await self._queue.get()
