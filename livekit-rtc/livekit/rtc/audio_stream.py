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
from ._proto import audio_frame_pb2 as proto_audio_frame
from ._proto import ffi_pb2 as proto_ffi
from ._proto.track_pb2 import TrackSource
from ._utils import RingQueue, task_done_logger
from .audio_frame import AudioFrame
from .participant import Participant
from .track import Track


@dataclass
class AudioFrameEvent:
    """An event representing a received audio frame.

    Attributes:
        frame (AudioFrame): The received audio frame.
    """

    frame: AudioFrame


class AudioStream:
    """An asynchronous audio stream for receiving audio frames from a participant or track.

    The `AudioStream` class provides an asynchronous iterator over audio frames received from
    a specific track or participant. It allows you to receive audio frames in real-time with
    customizable sample rates and channel configurations.
    """

    def __init__(
        self,
        track: Track,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        capacity: int = 0,
        sample_rate: int = 48000,
        num_channels: int = 1,
        **kwargs,
    ) -> None:
        """Initialize an `AudioStream` instance.

        Args:
            track (Optional[Track]): The audio track from which to receive audio. If not provided,
                you must specify `participant` and `track_source` in `kwargs`.
            loop (Optional[asyncio.AbstractEventLoop], optional): The event loop to use.
                Defaults to the current event loop.
            capacity (int, optional): The capacity of the internal frame queue. Defaults to 0 (unbounded).
            sample_rate (int, optional): The sample rate for the audio stream in Hz.
                Defaults to 48000.
            num_channels (int, optional): The number of audio channels. Defaults to 1.
        Example:
            ```python
            audio_stream = AudioStream(
                track=audio_track,
                sample_rate=44100,
                num_channels=2,
            )

            audio_stream = AudioStream.from_track(
                track=audio_track,
                sample_rate=44100,
                num_channels=2,
            )
            ```
        """
        self._track: Track | None = track
        self._sample_rate = sample_rate
        self._num_channels = num_channels
        self._loop = loop or asyncio.get_event_loop()
        self._ffi_queue = FfiClient.instance.queue.subscribe(self._loop)
        self._queue: RingQueue[AudioFrameEvent | None] = RingQueue(capacity)

        self._task = self._loop.create_task(self._run())
        self._task.add_done_callback(task_done_logger)

        stream: Any = None
        if "participant" in kwargs:
            stream = self._create_owned_stream_from_participant(
                participant=kwargs["participant"], track_source=kwargs["track_source"]
            )
        else:
            stream = self._create_owned_stream()
        self._ffi_handle = FfiHandle(stream.handle.id)
        self._info = stream.info

    @classmethod
    def from_participant(
        cls,
        *,
        participant: Participant,
        track_source: TrackSource.ValueType,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        capacity: int = 0,
        sample_rate: int = 48000,
        num_channels: int = 1,
    ) -> AudioStream:
        """Create an `AudioStream` from a participant's audio track.

        Args:
            participant (Participant): The participant from whom to receive audio.
            track_source (TrackSource.ValueType): The source of the audio track (e.g., microphone, screen share).
            loop (Optional[asyncio.AbstractEventLoop], optional): The event loop to use. Defaults to the current event loop.
            capacity (int, optional): The capacity of the internal frame queue. Defaults to 0 (unbounded).
            sample_rate (int, optional): The sample rate for the audio stream in Hz. Defaults to 48000.
            num_channels (int, optional): The number of audio channels. Defaults to 1.

        Returns:
            AudioStream: An instance of `AudioStream` that can be used to receive audio frames.

        Example:
            ```python
            audio_stream = AudioStream.from_participant(
                participant=participant,
                track_source=TrackSource.MICROPHONE,
                sample_rate=24000,
                num_channels=1,
            )
            ```
        """
        return AudioStream(
            participant=participant,
            track_source=track_source,
            loop=loop,
            capacity=capacity,
            track=None,  # type: ignore
            sample_rate=sample_rate,
            num_channels=num_channels,
        )

    @classmethod
    def from_track(
        cls,
        *,
        track: Track,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        capacity: int = 0,
        sample_rate: int = 48000,
        num_channels: int = 1,
    ) -> AudioStream:
        """Create an `AudioStream` from an existing audio track.

        Args:
            track (Track): The audio track from which to receive audio.
            loop (Optional[asyncio.AbstractEventLoop], optional): The event loop to use. Defaults to the current event loop.
            capacity (int, optional): The capacity of the internal frame queue. Defaults to 0 (unbounded).
            sample_rate (int, optional): The sample rate for the audio stream in Hz. Defaults to 48000.
            num_channels (int, optional): The number of audio channels. Defaults to 1.

        Returns:
            AudioStream: An instance of `AudioStream` that can be used to receive audio frames.

        Example:
            ```python
            audio_stream = AudioStream.from_track(
                track=audio_track,
                sample_rate=44100,
                num_channels=2,
            )
            ```
        """
        return AudioStream(
            track=track,
            loop=loop,
            capacity=capacity,
            sample_rate=sample_rate,
            num_channels=num_channels,
        )

    def __del__(self) -> None:
        FfiClient.instance.queue.unsubscribe(self._ffi_queue)

    def _create_owned_stream(self) -> Any:
        assert self._track is not None
        req = proto_ffi.FfiRequest()
        new_audio_stream = req.new_audio_stream
        new_audio_stream.track_handle = self._track._ffi_handle.handle
        new_audio_stream.sample_rate = self._sample_rate
        new_audio_stream.num_channels = self._num_channels
        new_audio_stream.type = proto_audio_frame.AudioStreamType.AUDIO_STREAM_NATIVE
        resp = FfiClient.instance.request(req)
        return resp.new_audio_stream.stream

    def _create_owned_stream_from_participant(
        self, participant: Participant, track_source: TrackSource.ValueType
    ) -> Any:
        req = proto_ffi.FfiRequest()
        audio_stream_from_participant = req.audio_stream_from_participant
        audio_stream_from_participant.participant_handle = (
            participant._ffi_handle.handle
        )
        audio_stream_from_participant.sample_rate = self._sample_rate
        audio_stream_from_participant.num_channels = self._num_channels
        audio_stream_from_participant.type = (
            proto_audio_frame.AudioStreamType.AUDIO_STREAM_NATIVE
        )
        audio_stream_from_participant.track_source = track_source
        resp = FfiClient.instance.request(req)
        return resp.audio_stream_from_participant.stream

    async def _run(self):
        while True:
            event = await self._ffi_queue.wait_for(self._is_event)
            audio_event: proto_audio_frame.AudioStreamEvent = event.audio_stream_event

            if audio_event.HasField("frame_received"):
                owned_buffer_info = audio_event.frame_received.frame
                frame = AudioFrame._from_owned_info(owned_buffer_info)
                event = AudioFrameEvent(frame)
                self._queue.put(event)
            elif audio_event.HasField("eos"):
                self._queue.put(None)
                break

        FfiClient.instance.queue.unsubscribe(self._ffi_queue)

    async def aclose(self) -> None:
        """Asynchronously close the audio stream.

        This method cleans up resources associated with the audio stream and waits for
        any pending operations to complete.
        """
        self._ffi_handle.dispose()
        await self._task

    def _is_event(self, e: proto_ffi.FfiEvent) -> bool:
        return e.audio_stream_event.stream_handle == self._ffi_handle.handle

    def __aiter__(self) -> AsyncIterator[AudioFrameEvent]:
        return self

    async def __anext__(self) -> AudioFrameEvent:
        if self._task.done():
            raise StopAsyncIteration

        item = await self._queue.get()
        if item is None:
            raise StopAsyncIteration

        return item
