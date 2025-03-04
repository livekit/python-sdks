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
    """
    Represents a real-time audio source with an internal audio queue.

    The `AudioSource` class allows you to push audio frames into a real-time audio
    source, managing an internal queue of audio data up to a maximum duration defined
    by `queue_size_ms`. It supports asynchronous operations to capture audio frames
    and to wait for the playback of all queued audio data.
    """

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
            sample_rate (int): The sample rate of the audio source in Hz.
            num_channels (int): The number of audio channels.
            queue_size_ms (int, optional): The buffer size of the audio queue in milliseconds.
                Defaults to 1000 ms.
            loop (asyncio.AbstractEventLoop, optional): The event loop to use. Defaults to
                `asyncio.get_event_loop()`.
        """
        self._sample_rate = sample_rate
        self._num_channels = num_channels
        self._loop = loop or asyncio.get_event_loop()

        req = proto_ffi.FfiRequest()
        req.new_audio_source.type = proto_audio_frame.AudioSourceType.AUDIO_SOURCE_NATIVE
        req.new_audio_source.sample_rate = sample_rate
        req.new_audio_source.num_channels = num_channels
        req.new_audio_source.queue_size_ms = queue_size_ms

        resp = FfiClient.instance.request(req)
        self._info = resp.new_audio_source.source
        self._ffi_handle = FfiHandle(self._info.handle.id)

        self._last_capture = 0.0
        self._q_size = 0.0
        self._join_handle: asyncio.TimerHandle | None = None
        self._join_fut: asyncio.Future[None] | None = None

    @property
    def sample_rate(self) -> int:
        """The sample rate of the audio source in Hz."""
        return self._sample_rate

    @property
    def num_channels(self) -> int:
        """The number of audio channels."""
        return self._num_channels

    @property
    def queued_duration(self) -> float:
        """The current duration (in seconds) of audio data queued for playback."""
        return max(self._q_size - time.monotonic() + self._last_capture, 0.0)

    def clear_queue(self) -> None:
        """
        Clears the internal audio queue, discarding all buffered audio data.

        This method immediately removes all audio data currently queued for playback,
        effectively resetting the audio source's buffer. Any audio frames that have been
        captured but not yet played will be discarded. This is useful in scenarios where
        you need to stop playback abruptly or prevent outdated audio data from being played.
        """
        req = proto_ffi.FfiRequest()
        req.clear_audio_buffer.source_handle = self._ffi_handle.handle
        _ = FfiClient.instance.request(req)
        self._release_waiter()

    async def capture_frame(self, frame: AudioFrame) -> None:
        """
        Captures an `AudioFrame` and queues it for playback.

        This method is used to push new audio data into the audio source. The audio data
        will be processed and queued. If the size of the audio frame exceeds the internal
        queue size, the method will wait until there is enough space in the queue to
        accommodate the frame. The method returns only when all of the data in the buffer
        has been pushed.

        Args:
            frame (AudioFrame): The audio frame to capture and queue.

        Raises:
            Exception: If there is an error during frame capture.
        """

        if frame.samples_per_channel == 0 or self._ffi_handle.disposed:
            return

        now = time.monotonic()
        elapsed = 0.0 if self._last_capture == 0.0 else now - self._last_capture
        self._q_size += frame.samples_per_channel / self.sample_rate - elapsed
        self._last_capture = now

        if self._join_handle:
            self._join_handle.cancel()

        if self._join_fut is None:
            self._join_fut = self._loop.create_future()

        self._join_handle = self._loop.call_later(self._q_size, self._release_waiter)

        req = proto_ffi.FfiRequest()
        req.capture_audio_frame.source_handle = self._ffi_handle.handle
        req.capture_audio_frame.buffer.CopyFrom(frame._proto_info())

        queue = FfiClient.instance.queue.subscribe(loop=self._loop)
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.capture_audio_frame.async_id == resp.capture_audio_frame.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.capture_audio_frame.error:
            raise Exception(cb.capture_audio_frame.error)

    async def wait_for_playout(self) -> None:
        """
        Waits for the audio source to finish playing out all audio data.

        This method ensures that all queued audio data has been played out before returning.
        It can be used to synchronize events after audio playback or to ensure that the
        audio queue is empty.
        """

        if self._join_fut is None:
            return

        await asyncio.shield(self._join_fut)

    def _release_waiter(self) -> None:
        if self._join_fut is None:
            return  # could be None when clear_queue is called

        if not self._join_fut.done():
            self._join_fut.set_result(None)

        self._last_capture = 0.0
        self._q_size = 0.0
        self._join_fut = None

    async def aclose(self) -> None:
        """Close the audio source

        This method cleans up resources associated with the audio source.
        """
        self._ffi_handle.dispose()
