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

"""End-to-end audio publish/subscribe tests."""

import asyncio
import ctypes
import math
import os
import uuid
import wave
from pathlib import Path

import numpy as np
import pytest

from livekit import api, rtc
from livekit.rtc.audio_frame import AudioFrame


SAMPLE_RATE = 48000
NUM_CHANNELS = 1
TONE_DURATION_SEC = 1.0
FREQUENCIES_HZ = [100, 300, 500, 700, 1000]
AMPLITUDE = 0.5


def skip_if_no_credentials():
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    return pytest.mark.skipif(
        bool(missing), reason=f"Missing environment variables: {', '.join(missing)}"
    )


def create_token(identity: str, room_name: str) -> str:
    return (
        api.AccessToken()
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        .to_jwt()
    )


def unique_room_name(base: str) -> str:
    return f"{base}-{uuid.uuid4().hex[:8]}"


def _generate_sine_wave(
    frequency: int,
    sample_rate: int,
    num_channels: int,
    duration_sec: float,
    amplitude: float = 0.5,
) -> AudioFrame:
    """Generate an AudioFrame containing a sine wave at the given frequency."""
    samples_per_channel = int(sample_rate * duration_sec)
    t = np.arange(samples_per_channel, dtype=np.float64) / sample_rate
    wave_signal = np.sin(2.0 * math.pi * frequency * t) * amplitude
    pcm = (wave_signal * np.iinfo(np.int16).max).astype(np.int16)

    if num_channels > 1:
        pcm = np.repeat(pcm[:, np.newaxis], num_channels, axis=1).reshape(-1)

    return AudioFrame(
        data=pcm.tobytes(),
        sample_rate=sample_rate,
        num_channels=num_channels,
        samples_per_channel=samples_per_channel,
    )


def _frame_to_mono_float(frame: AudioFrame) -> np.ndarray:
    """Decode an int16 AudioFrame into a normalized float64 mono signal."""
    samples = np.frombuffer(bytes(frame.data.cast("B")), dtype=np.int16).astype(np.float64)
    if frame.num_channels > 1:
        samples = samples.reshape(-1, frame.num_channels).mean(axis=1)
    return samples / float(np.iinfo(np.int16).max)


def _fft_spectrum(frame: AudioFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return (freqs, magnitudes) from a Hann-windowed rfft of `frame`."""
    signal = _frame_to_mono_float(frame)
    window = np.hanning(len(signal))
    # Compensate for the Hann window's coherent gain so magnitudes stay comparable.
    spectrum = np.fft.rfft(signal * window) / (np.sum(window) / 2.0)
    magnitudes = np.abs(spectrum)
    freqs = np.fft.rfftfreq(len(signal), d=1.0 / frame.sample_rate)
    return freqs, magnitudes


def _detect_peak_frequency(frame: AudioFrame) -> float:
    """Return the frequency bin with the largest magnitude in `frame`."""
    freqs, magnitudes = _fft_spectrum(frame)
    return float(freqs[int(np.argmax(magnitudes))])


def _band_energies(
    frame: AudioFrame,
    centers: list[int],
    bandwidth_hz: float = 20.0,
) -> dict[int, float]:
    """Sum squared-magnitude (energy) in narrow bands centered at each frequency."""
    freqs, magnitudes = _fft_spectrum(frame)
    power = magnitudes**2
    return {
        center: float(
            np.sum(power[(freqs >= center - bandwidth_hz) & (freqs <= center + bandwidth_hz)])
        )
        for center in centers
    }


@skip_if_no_credentials()
class TestAudioStreamPublishSubscribe:
    """End-to-end: publish a sine sweep into a room and verify spectrum on the subscriber."""

    async def test_audio_stream_publish_subscribe(self):
        """Publish 5 seconds of 100/300/500/700/1000 Hz tones and FFT-verify received audio."""
        url = os.environ["LIVEKIT_URL"]
        room_name = unique_room_name("test-audio-sweep")

        publisher_room = rtc.Room()
        subscriber_room = rtc.Room()

        publisher_token = create_token("audio-sweep-publisher", room_name)
        subscriber_token = create_token("audio-sweep-subscriber", room_name)

        track_subscribed_event = asyncio.Event()
        subscribed_track: rtc.Track | None = None

        @subscriber_room.on("track_subscribed")
        def on_track_subscribed(
            track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant,
        ):
            nonlocal subscribed_track
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                subscribed_track = track
                track_subscribed_event.set()

        try:
            await subscriber_room.connect(url, subscriber_token)
            await publisher_room.connect(url, publisher_token)

            source = rtc.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
            track = rtc.LocalAudioTrack.create_audio_track("sine-sweep", source)
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_MICROPHONE
            await publisher_room.local_participant.publish_track(track, options)

            await asyncio.wait_for(track_subscribed_event.wait(), timeout=10.0)
            assert subscribed_track is not None

            audio_stream = rtc.AudioStream(
                subscribed_track,
                sample_rate=SAMPLE_RATE,
                num_channels=NUM_CHANNELS,
            )

            total_duration = TONE_DURATION_SEC * len(FREQUENCIES_HZ)
            target_samples = int(SAMPLE_RATE * total_duration)
            # Collect a little extra to tolerate codec startup latency.
            collect_samples_target = target_samples + int(SAMPLE_RATE * 1.0)

            async def publish_tones() -> None:
                await track_subscribed_event.wait()
                for freq in FREQUENCIES_HZ:
                    frame = _generate_sine_wave(
                        freq,
                        SAMPLE_RATE,
                        NUM_CHANNELS,
                        TONE_DURATION_SEC,
                        AMPLITUDE,
                    )
                    await source.capture_frame(frame)
                await source.wait_for_playout()

            async def collect_samples() -> np.ndarray:
                buffers: list[np.ndarray] = []
                total = 0
                async for event in audio_stream:
                    chunk = np.frombuffer(bytes(event.frame.data.cast("B")), dtype=np.int16)
                    buffers.append(chunk)
                    total += len(chunk)
                    if total >= collect_samples_target:
                        break
                return np.concatenate(buffers) if buffers else np.array([], dtype=np.int16)

            publish_task = asyncio.create_task(publish_tones())
            received = await asyncio.wait_for(collect_samples(), timeout=20.0)
            await publish_task
            await audio_stream.aclose()
            await source.aclose()

            assert len(received) >= target_samples, (
                f"Expected at least {target_samples} samples, got {len(received)}"
            )

            recv_wav_path = Path(__file__).parent / "subscriber_recv_freqs.wav"
            with wave.open(str(recv_wav_path), "wb") as wav_out:
                wav_out.setnchannels(NUM_CHANNELS)
                wav_out.setsampwidth(ctypes.sizeof(ctypes.c_int16))
                wav_out.setframerate(SAMPLE_RATE)
                wav_out.writeframes(received.tobytes())

            # Find signal onset to skip codec startup silence.
            envelope = np.abs(received.astype(np.float32))
            threshold = float(envelope.max()) * 0.2
            onset_candidates = np.where(envelope > threshold)[0]
            assert onset_candidates.size > 0, "Received audio contains only silence"
            onset = int(onset_candidates[0])

            samples_per_tone = int(SAMPLE_RATE * TONE_DURATION_SEC)
            # Analyze the middle slice of each tone window to avoid boundary transitions.
            analysis_margin = int(SAMPLE_RATE * 0.2)
            analysis_length = samples_per_tone - 2 * analysis_margin

            per_tone_peaks: list[tuple[int, float]] = []
            for idx, expected_freq in enumerate(FREQUENCIES_HZ):
                start = onset + idx * samples_per_tone + analysis_margin
                end = start + analysis_length
                assert end <= len(received), (
                    f"Not enough samples for tone {idx} (expected {expected_freq} Hz): "
                    f"need {end}, have {len(received)}"
                )
                segment = received[start:end]
                segment_frame = AudioFrame(
                    data=segment.tobytes(),
                    sample_rate=SAMPLE_RATE,
                    num_channels=NUM_CHANNELS,
                    samples_per_channel=len(segment),
                )
                peak_hz = _detect_peak_frequency(segment_frame)
                per_tone_peaks.append((expected_freq, peak_hz))

                # Opus transcoding adds spectral jitter; allow a 15 Hz tolerance.
                assert peak_hz == pytest.approx(expected_freq, abs=15.0), (
                    f"Tone {idx}: expected {expected_freq} Hz, got peak at {peak_hz:.1f} Hz. "
                    f"All peaks: {per_tone_peaks}"
                )

                # The target band should also dominate the other sweep bands.
                energies = _band_energies(segment_frame, FREQUENCIES_HZ, bandwidth_hz=30.0)
                target_energy = energies[expected_freq]
                other_energy = sum(v for k, v in energies.items() if k != expected_freq)
                assert target_energy > 5.0 * max(other_energy, 1e-12), (
                    f"Tone {idx} ({expected_freq} Hz) did not dominate other bands: "
                    f"target={target_energy:.3e}, other={other_energy:.3e}"
                )
        finally:
            await publisher_room.disconnect()
            await subscriber_room.disconnect()
