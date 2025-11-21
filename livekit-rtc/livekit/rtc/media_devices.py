# Copyright 2025 LiveKit, Inc.
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
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

import numpy as np
import threading

if TYPE_CHECKING:
    import sounddevice as sd  # type: ignore[import-not-found, import-untyped]

from . import AudioSource
from .audio_frame import AudioFrame
from .apm import AudioProcessingModule
from .audio_mixer import AudioMixer
from .audio_stream import AudioStream
from .track import Track

"""
Media device helpers built on top of the `sounddevice` library.

This module provides a small, Pythonic helper around native audio I/O for
LiveKit RTC usage:

- Capture the default audio input device and feed frames into `rtc.AudioSource`.
- Optionally enable audio processing via `rtc.AudioProcessingModule` (AEC,
  noise suppression, high-pass filter, AGC). Frames are processed in 10 ms
  chunks as required by APM.
- Play arbitrary audio frames to the default speaker. When AEC is enabled on
  the input, the `OutputPlayer` can feed the APM reverse stream so echo
  cancellation has access to render (speaker) audio.

Notes on AEC wiring:
- AEC requires feeding both capture (mic) and reverse (speaker) paths into
  the same APM instance. This module does not automatically capture output from
  other players. To enable AEC, the output player feeds APM's reverse stream
  and we set stream delays derived from PortAudio timing.
"""


DEFAULT_SAMPLE_RATE = 48000
DEFAULT_CHANNELS = 1
FRAME_SAMPLES = 480  # 10 ms at 48 kHz
BLOCKSIZE = 4800  # 100 ms I/O buffer size for sounddevice


class _AudioStreamIterator:
    """Adapter to convert AudioStream (AsyncIterator[AudioFrameEvent]) to AsyncIterator[AudioFrame].

    This adapter wraps an AudioStream and extracts the frame from each AudioFrameEvent,
    making it compatible with AudioMixer which expects AsyncIterator[AudioFrame].
    """

    def __init__(self, audio_stream: AudioStream) -> None:
        self._audio_stream = audio_stream

    def __aiter__(self) -> AsyncIterator[AudioFrame]:
        return self

    async def __anext__(self) -> AudioFrame:
        event = await self._audio_stream.__anext__()
        return event.frame

    async def aclose(self) -> None:
        await self._audio_stream.aclose()


def _ensure_loop(loop: Optional[asyncio.AbstractEventLoop]) -> asyncio.AbstractEventLoop:
    return loop or asyncio.get_event_loop()


class _APMDelayEstimator:
    """Thread-safe store for last known output (render) delay in seconds.

    The sounddevice callbacks are invoked on PortAudio's threads. This helper allows
    sharing the latest output delay measurement with the input callback so we can set
    APM's combined stream delay (render + capture).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._output_delay_sec: float = 0.0

    def set_output_delay(self, delay_sec: float) -> None:
        with self._lock:
            self._output_delay_sec = float(delay_sec)

    def get_output_delay(self) -> float:
        with self._lock:
            return self._output_delay_sec


@dataclass
class InputCapture:
    """Holds resources for an active audio input capture.

    Attributes:
        source: `rtc.AudioSource` that receives captured frames. This can be
            published as a `LocalAudioTrack`.
        input_stream: Underlying `sounddevice.InputStream`.
        task: Async task that drains a queue and calls `source.capture_frame`.
        apm: Optional `rtc.AudioProcessingModule` used to process 10 ms frames
            (AEC, NS, HPF, AGC). When performing echo cancellation, pass this
            instance to `open_output_player` so reverse frames are provided.
        delay_estimator: Internal helper used to combine capture and render delays.
    """

    source: AudioSource
    input_stream: "sd.InputStream"
    task: asyncio.Task
    apm: Optional[AudioProcessingModule]
    delay_estimator: Optional[_APMDelayEstimator]

    async def aclose(self) -> None:
        """Stop capture and close underlying resources."""
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        try:
            self.input_stream.stop()
            self.input_stream.close()
        except Exception:
            pass


class OutputPlayer:
    """Simple audio output helper using `sounddevice.OutputStream`.

    When `apm_for_reverse` is provided, this player will feed the same PCM it
    renders (in 10 ms frames) into the APM reverse path so that echo
    cancellation can correlate mic input with speaker output.

    The OutputPlayer includes an internal `AudioMixer` for convenient multi-track
    playback. Use `add_track()` and `remove_track()` to dynamically manage tracks,
    then call `start()` to begin playback.
    """

    def __init__(
        self,
        *,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        num_channels: int = DEFAULT_CHANNELS,
        blocksize: int = BLOCKSIZE,
        apm_for_reverse: Optional[AudioProcessingModule] = None,
        output_device: Optional[int] = None,
        delay_estimator: Optional[_APMDelayEstimator] = None,
    ) -> None:
        import sounddevice as sd  # type: ignore[import-not-found, import-untyped]

        self._sample_rate = sample_rate
        self._num_channels = num_channels
        self._blocksize = blocksize
        self._apm = apm_for_reverse
        self._buffer = bytearray()
        self._buffer_lock = asyncio.Lock()
        self._play_task: Optional[asyncio.Task] = None
        self._running = False
        self._delay_estimator = delay_estimator

        # Internal mixer for add_track/remove_track API
        self._mixer: Optional[AudioMixer] = None
        self._track_streams: dict[
            str, tuple[AudioStream, _AudioStreamIterator]
        ] = {}  # track.sid -> (AudioStream, adapter)

        def _callback(outdata: np.ndarray, frame_count: int, time_info: Any, status: Any) -> None:
            # Pull PCM int16 from buffer; zero if not enough
            bytes_needed = frame_count * 2
            # Important: Do not take asyncio locks in realtime callbacks. We keep the
            # critical section minimal and tolerate occasional underruns.
            available = len(self._buffer)
            if available >= bytes_needed:
                chunk = self._buffer[:bytes_needed]
                outdata[:, 0] = np.frombuffer(chunk, dtype=np.int16, count=frame_count)
                del self._buffer[:bytes_needed]
            elif available > 0:
                outdata[: available // 2, 0] = np.frombuffer(
                    self._buffer[:available], dtype=np.int16, count=available // 2
                )
                outdata[available // 2 :, 0] = 0
                del self._buffer[:available]
            else:
                outdata.fill(0)

            # Measure render (output) delay: time until DAC from current callback time
            try:
                output_delay_sec = float(time_info.outputBufferDacTime - time_info.currentTime)
                if self._delay_estimator is not None:
                    self._delay_estimator.set_output_delay(output_delay_sec)
            except Exception:
                pass

            if self._apm is not None:
                # Feed reverse stream in 10 ms frames for AEC
                num_chunks = frame_count // FRAME_SAMPLES
                for i in range(num_chunks):
                    start = i * FRAME_SAMPLES
                    end = start + FRAME_SAMPLES
                    if end > frame_count:
                        break
                    render_chunk = outdata[start:end, 0]
                    render_frame = AudioFrame(
                        render_chunk.tobytes(), self._sample_rate, 1, FRAME_SAMPLES
                    )
                    try:
                        self._apm.process_reverse_stream(render_frame)
                    except Exception:
                        # Ignore reverse stream errors in callback
                        pass

        self._stream = sd.OutputStream(
            callback=_callback,
            dtype="int16",
            channels=num_channels,
            device=output_device,
            samplerate=sample_rate,
            blocksize=blocksize,
        )

    async def add_track(self, track: Track) -> None:
        """Add an audio track to the internal mixer for playback.

        This creates an `AudioStream` from the track and adds it to the internal
        mixer. The mixer is created lazily on first track addition. Call `start()`
        to begin playback of all added tracks.

        Args:
            track: The audio track to add (typically from a remote participant).

        Raises:
            ValueError: If the track is not an audio track or has already been added.
        """
        if track.sid in self._track_streams:
            raise ValueError(f"Track {track.sid} already added to player")

        # Create mixer on first track addition
        if self._mixer is None:
            self._mixer = AudioMixer(sample_rate=self._sample_rate, num_channels=self._num_channels)

        # Create audio stream for this track
        stream = AudioStream(track, sample_rate=self._sample_rate, num_channels=self._num_channels)
        # Wrap the stream with an adapter to convert AudioFrameEvent to AudioFrame
        stream_iterator = _AudioStreamIterator(stream)

        self._track_streams[track.sid] = (stream, stream_iterator)
        self._mixer.add_stream(stream_iterator)

    async def remove_track(self, track: Track) -> None:
        """Remove an audio track from the internal mixer.

        This removes the track's stream from the mixer and closes it.

        Args:
            track: The audio track to remove.
        """
        entry = self._track_streams.pop(track.sid, None)
        if entry is None:
            return

        stream, stream_iterator = entry
        if self._mixer is not None:
            try:
                self._mixer.remove_stream(stream_iterator)
            except Exception:
                pass

        try:
            await stream.aclose()
        except Exception:
            pass

    async def start(self) -> None:
        """Start playback of all tracks in the internal mixer.

        This begins a background task that consumes frames from the internal mixer
        and sends them to the output device. Tracks can be added or removed
        dynamically using `add_track()` and `remove_track()`.

        Raises:
            RuntimeError: If playback is already started or no mixer is available.
        """
        if self._play_task is not None and not self._play_task.done():
            raise RuntimeError("Playback already started")

        if self._mixer is None:
            self._mixer = AudioMixer(sample_rate=self._sample_rate, num_channels=self._num_channels)

        async def _playback_loop():
            """Internal playback loop that consumes frames from the mixer."""
            self._running = True
            self._stream.start()
            try:
                async for frame in self._mixer:
                    if not self._running:
                        break
                    # Append raw PCM bytes for callback consumption
                    self._buffer.extend(frame.data.tobytes())
            finally:
                self._running = False
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass

        self._play_task = asyncio.create_task(_playback_loop())

    async def aclose(self) -> None:
        """Stop playback and close the output stream.

        This also cleans up all added tracks and the internal mixer.
        """
        self._running = False

        # Cancel playback task if running
        if self._play_task is not None and not self._play_task.done():
            self._play_task.cancel()
            try:
                await self._play_task
            except asyncio.CancelledError:
                pass

        # Clean up all track streams
        for stream, _ in list(self._track_streams.values()):
            try:
                await stream.aclose()
            except Exception:
                pass
        self._track_streams.clear()

        # Close mixer
        if self._mixer is not None:
            try:
                await self._mixer.aclose()
            except Exception:
                pass
            self._mixer = None

        # Close output stream
        try:
            self._stream.stop()
            self._stream.close()
        except Exception:
            pass


class MediaDevices:
    """High-level interface to native audio devices.

    - Device enumeration helpers.
    - Audio input capture into `rtc.AudioSource` with optional APM processing.
    - Audio output player that can feed APM reverse stream for AEC.

    Design notes:
    - APM operates on 10 ms frames; this module slices input/output audio into
      `FRAME_SAMPLES` for processing calls.
    - For AEC to be effective, render audio that could leak back into the mic
      should be played through `OutputPlayer` with the same `apm` instance.
    - Timing alignment: this helper does not attempt to set device latency on
      APM; for most setups the default behavior is acceptable.
    """

    def __init__(
        self,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        input_sample_rate: int = DEFAULT_SAMPLE_RATE,
        output_sample_rate: int = DEFAULT_SAMPLE_RATE,
        num_channels: int = DEFAULT_CHANNELS,
        blocksize: int = BLOCKSIZE,
    ) -> None:
        self._loop = _ensure_loop(loop)
        self._in_sr = input_sample_rate
        self._out_sr = output_sample_rate
        self._channels = num_channels
        self._blocksize = blocksize
        self._delay_estimator: Optional[_APMDelayEstimator] = None
        self._apm: Optional[AudioProcessingModule] = None

    # Device enumeration
    def list_input_devices(self) -> list[dict[str, Any]]:
        """List available input devices.

        Returns a list of dictionaries with the `sounddevice` metadata and an
        added `index` key corresponding to the device index.
        """
        import sounddevice as sd  # type: ignore[import-not-found, import-untyped]

        devices = sd.query_devices()
        result: list[dict[str, Any]] = []
        for idx, dev in enumerate(devices):
            if dev.get("max_input_channels", 0) > 0:
                result.append({"index": idx, **dev})
        return result

    def list_output_devices(self) -> list[dict[str, Any]]:
        """List available output devices with indices."""
        import sounddevice as sd  # type: ignore[import-not-found, import-untyped]

        devices = sd.query_devices()
        result: list[dict[str, Any]] = []
        for idx, dev in enumerate(devices):
            if dev.get("max_output_channels", 0) > 0:
                result.append({"index": idx, **dev})
        return result

    def default_input_device(self) -> Optional[int]:
        """Return the default input device index (or None)."""
        import sounddevice as sd  # type: ignore[import-not-found, import-untyped]

        dev = sd.default.device
        return dev[0] if isinstance(dev, (list, tuple)) else None

    def default_output_device(self) -> Optional[int]:
        """Return the default output device index (or None)."""
        import sounddevice as sd  # type: ignore[import-not-found, import-untyped]

        dev = sd.default.device
        return dev[1] if isinstance(dev, (list, tuple)) else None

    # Capture / Playback
    def open_input(
        self,
        *,
        enable_aec: bool = True,
        noise_suppression: bool = True,
        high_pass_filter: bool = True,
        auto_gain_control: bool = True,
        input_device: Optional[int] = None,
        queue_capacity: int = 50,
        input_channel_index: Optional[int] = None,
    ) -> InputCapture:
        """Open the default (or chosen) audio input device and start capture.

        Frames are sliced into 10 ms chunks. If any processing option is enabled,
        an `AudioProcessingModule` is created and applied to each frame before it
        is queued for `AudioSource.capture_frame`.

        To enable AEC end-to-end, call `open_output()` after opening the input
        device. The output player will automatically use the input's APM for
        reverse stream processing, enabling echo cancellation.

        Args:
            enable_aec: Enable acoustic echo cancellation.
            noise_suppression: Enable noise suppression.
            high_pass_filter: Enable high-pass filtering.
            auto_gain_control: Enable automatic gain control.
            input_device: Optional input device index (default system device if None).
            queue_capacity: Max queued frames between callback and async pump.
            input_channel_index: Optional zero-based device channel to capture. If provided,
                only that channel is opened (via sounddevice mapping) and used as mono input.

        Returns:
            InputCapture: Holder with `source`, `apm`, and `aclose()`.
        """
        import sounddevice as sd  # type: ignore[import-not-found, import-untyped]

        loop = self._loop
        source = AudioSource(self._in_sr, self._channels, loop=loop)
        apm: Optional[AudioProcessingModule] = None
        if enable_aec or noise_suppression or high_pass_filter or auto_gain_control:
            apm = AudioProcessingModule(
                echo_cancellation=enable_aec,
                noise_suppression=noise_suppression,
                high_pass_filter=high_pass_filter,
                auto_gain_control=auto_gain_control,
            )
        delay_estimator: Optional[_APMDelayEstimator] = (
            _APMDelayEstimator() if apm is not None else None
        )
        # Store the shared estimator and APM on the device helper so the output player can reuse them
        self._delay_estimator = delay_estimator
        self._apm = apm

        # Queue from callback to async task
        q: asyncio.Queue[AudioFrame] = asyncio.Queue(maxsize=queue_capacity)

        def _input_callback(
            indata: np.ndarray, frame_count: int, time_info: Any, status: Any
        ) -> None:
            # Slice into 10 ms frames, optionally APM, enqueue for async capture
            # Compute input (capture) delay using PortAudio timing; combine with last
            # measured output delay to provide APM stream delay in milliseconds.
            if apm is not None:
                try:
                    input_delay_sec = float(time_info.currentTime - time_info.inputBufferAdcTime)
                    output_delay_sec = (
                        float(delay_estimator.get_output_delay()) if delay_estimator else 0.0
                    )
                    total_delay_ms = int(max((input_delay_sec + output_delay_sec) * 1000.0, 0.0))
                    try:
                        apm.set_stream_delay_ms(total_delay_ms)
                    except Exception:
                        pass
                except Exception:
                    pass
            num_frames = frame_count // FRAME_SAMPLES
            for i in range(num_frames):
                start = i * FRAME_SAMPLES
                end = start + FRAME_SAMPLES
                if end > frame_count:
                    break
                chunk = indata[start:end, 0]
                frame = AudioFrame(
                    data=chunk.tobytes(),
                    samples_per_channel=FRAME_SAMPLES,
                    sample_rate=self._in_sr,
                    num_channels=self._channels,
                )
                if apm is not None:
                    try:
                        apm.process_stream(frame)
                    except Exception:
                        # Continue even if APM processing fails
                        pass
                try:
                    # Non-blocking: drop if full
                    if not q.full():
                        loop.call_soon_threadsafe(q.put_nowait, frame)
                except Exception:
                    pass

        # Note: input_channel_index is currently not used as sounddevice mapping
        # parameter is not supported in all versions.
        input_stream = sd.InputStream(
            callback=_input_callback,
            dtype="int16",
            channels=self._channels,
            device=input_device,
            samplerate=self._in_sr,
            blocksize=self._blocksize,
        )
        input_stream.start()

        async def _pump() -> None:
            # Drain queue into AudioSource
            while True:
                try:
                    frame = await q.get()
                except asyncio.CancelledError:
                    break
                try:
                    await source.capture_frame(frame)
                except Exception:
                    # Ignore capture errors to keep the pump alive
                    pass

        task = asyncio.create_task(_pump())
        return InputCapture(
            source=source,
            input_stream=input_stream,
            task=task,
            apm=apm,
            delay_estimator=delay_estimator,
        )

    def open_output(
        self,
        *,
        output_device: Optional[int] = None,
    ) -> OutputPlayer:
        """Create an `OutputPlayer` for rendering and (optionally) AEC reverse.

        If an input device was opened with AEC enabled, the output player will
        automatically feed the APM's reverse stream for echo cancellation.

        Args:
            output_device: Optional output device index (default system device if None).
        """
        return OutputPlayer(
            sample_rate=self._out_sr,
            num_channels=self._channels,
            blocksize=self._blocksize,
            apm_for_reverse=self._apm,
            output_device=output_device,
            delay_estimator=self._delay_estimator,
        )
