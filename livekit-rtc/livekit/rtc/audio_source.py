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

import time
import asyncio

from ._ffi_client import FfiHandle, FfiClient
from ._proto import audio_frame_pb2 as proto_audio_frame
from ._proto import ffi_pb2 as proto_ffi
from .audio_frame import AudioFrame


class AudioSource:
    def __init__(
        self,
        sample_rate: int,
        num_channels: int,
        queue_size_ms: int = 1000,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        """
        Initializes a new instance of the audio source.

        Args:
            sample_rate (int): The sample rate of the audio source in Hz
            num_channels (int): The number of audio channels
            queue_size_ms (int, optional): The buffer size of the audio queue in milliseconds.
                Defaults to 1000 ms.
            loop (asyncio.AbstractEventLoop, optional): The event loop to use. Defaults to asyncio.get_event_loop().
        """
        self._sample_rate = sample_rate
        self._num_channels = num_channels
        self._loop = loop or asyncio.get_event_loop()

        req = proto_ffi.FfiRequest()
        req.new_audio_source.type = (
            proto_audio_frame.AudioSourceType.AUDIO_SOURCE_NATIVE
        )
        req.new_audio_source.sample_rate = sample_rate
        req.new_audio_source.num_channels = num_channels
        req.new_audio_source.queue_size_ms = queue_size_ms

        resp = FfiClient.instance.request(req)
        self._info = resp.new_audio_source.source
        self._ffi_handle = FfiHandle(self._info.handle.id)

        self._last_capture = self._q_size = 0.0
        self._join_handle: asyncio.TimerHandle | None = None
        self._join_fut: asyncio.Future[None] = self._loop.create_future()

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def num_channels(self) -> int:
        return self._num_channels

    @property
    def queued_duration(self) -> float:
        return max(self._q_size - time.monotonic() + self._last_capture, 0.0)

    def clear_queue(self) -> None:
        """Clears the audio queue, discarding all buffered audio data."""
        req = proto_ffi.FfiRequest()
        req.clear_audio_buffer.source_handle = self._ffi_handle.handle
        _ = FfiClient.instance.request(req)
        self._release_waiter()

    async def capture_frame(self, frame: AudioFrame) -> None:
        """Captures an AudioFrame.

        Used to push new audio data into the published Track. Audio data will
        be pushed in chunks of 10ms. It'll return only when all of the data in
        the buffer has been pushed.
        """

        now = time.monotonic()
        elapsed = 0.0 if self._last_capture == 0.0 else now - self._last_capture
        self._q_size += frame.samples_per_channel / self.sample_rate - elapsed

        # remove 50ms to account for processing time (e.g. using wait_for_playour for very small chunks)
        self._q_size -= 0.05
        self._last_capture = now

        if self._join_handle:
            self._join_handle.cancel()

        if self._join_fut.done():
            self._join_fut = self._loop.create_future()

        self._join_handle = self._loop.call_later(self._q_size, self._release_waiter)

        req = proto_ffi.FfiRequest()
        req.capture_audio_frame.source_handle = self._ffi_handle.handle
        req.capture_audio_frame.buffer.CopyFrom(frame._proto_info())

        queue = FfiClient.instance.queue.subscribe(loop=self._loop)
        try:
            resp = FfiClient.instance.request(req)
            cb = await queue.wait_for(
                lambda e: e.capture_audio_frame.async_id
                == resp.capture_audio_frame.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.capture_audio_frame.error:
            raise Exception(cb.capture_audio_frame.error)

    async def wait_for_playout(self) -> None:
        """Waits for the audio source to finish playing out all audio data."""

        if self._join_fut is None:
            return

        await asyncio.shield(self._join_fut)

    def _release_waiter(self) -> None:
        if not self._join_fut.done():
            self._join_fut.set_result(None)

        self._last_capture = 0.0
        self._q_size = 0.0
