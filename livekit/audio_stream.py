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
from ._utils import RingQueue
from .audio_frame import AudioFrame
from .track import Track

DEFAULT_MAX_SIZE = 48000 * 2 * 5  # 5 second of audio at 48khz stereo (=960kb)


class AudioStream:
    def __init__(self, track: Track, capacity: int = DEFAULT_MAX_SIZE) -> None:
        self._track = track
        self._ffi_queue = ffi_client.subscribe()
        self._queue: RingQueue[AudioFrame] = RingQueue(capacity)

        req = proto_ffi.FfiRequest()
        new_audio_stream = req.new_audio_stream
        new_audio_stream.track_handle = track._ffi_handle.handle
        new_audio_stream.type = proto_audio_frame.AudioStreamType.AUDIO_STREAM_NATIVE
        resp = ffi_client.request(req)

        stream_info = resp.new_audio_stream.stream
        self._ffi_handle = FfiHandle(stream_info.handle.id)
        self._info = stream_info

        self._task = asyncio.create_task(self._run())

    async def _run(self):
        while True:
            event = await self._ffi_queue.wait_for(self._is_event)
            audio_event = event.audio_stream_event

            if audio_event.HasField('frame_received'):
                owned_buffer_info = audio_event.frame_received.frame
                frame = AudioFrame(owned_buffer_info)
                self._queue.put(frame)
            elif audio_event.HasField('eos'):
                break

    def __aiter__(self):
        return self

    def _is_event(self, e: proto_ffi.FfiEvent):
        return e.audio_stream_event.stream_handle == self._ffi_handle.handle

    async def __anext__(self):
        if self._task.done():
            raise StopAsyncIteration
        return await self._queue.get()
