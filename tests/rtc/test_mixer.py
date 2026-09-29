# type: ignore

import asyncio

import numpy as np
import pytest

from livekit.rtc import AudioFrame, AudioMixer
from livekit.rtc.utils import sine_wave_generator

SAMPLE_RATE = 48000
BLOCKSIZE = SAMPLE_RATE // 10


@pytest.mark.asyncio
async def test_mixer_two_sine_waves():
    """
    Test that mixing two sine waves (440Hz and 880Hz) produces an output
    containing both frequency components.
    """
    duration = 1.0
    mixer = AudioMixer(
        sample_rate=SAMPLE_RATE,
        num_channels=1,
        blocksize=BLOCKSIZE,
        stream_timeout_ms=100,
        capacity=100,
    )
    stream1 = sine_wave_generator(440, duration, SAMPLE_RATE)
    stream2 = sine_wave_generator(880, duration, SAMPLE_RATE)
    mixer.add_stream(stream1)
    mixer.add_stream(stream2)
    mixer.end_input()

    mixed_signals = []
    async for frame in mixer:
        data = np.frombuffer(frame.data.tobytes(), dtype=np.int16)
        mixed_signals.append(data)

    await mixer.aclose()

    if not mixed_signals:
        pytest.fail("No frames were produced by the mixer.")

    mixed_signal = np.concatenate(mixed_signals)

    # Use FFT to analyze frequency components.
    fft = np.fft.rfft(mixed_signal)
    freqs = np.fft.rfftfreq(len(mixed_signal), 1 / SAMPLE_RATE)
    magnitude = np.abs(fft)

    # Identify peak frequencies. We'll pick the 5 highest peaks.
    peak_indices = np.argsort(magnitude)[-5:]
    peak_freqs = freqs[peak_indices]

    print("Peak frequencies:", peak_freqs)

    # Assert that the peaks include 440Hz and 880Hz (with a tolerance of ±5 Hz)
    assert any(np.isclose(peak_freqs, 440, atol=5)), f"Expected 440 Hz in peaks, got: {peak_freqs}"
    assert any(np.isclose(peak_freqs, 880, atol=5)), f"Expected 880 Hz in peaks, got: {peak_freqs}"


@pytest.mark.asyncio
async def test_mixer_keeps_generator_stream_that_is_slower_than_the_timeout():
    """
    A stream that misses the timeout once must not be lost: its audio is mixed
    once it arrives.
    """

    async def slow_stream():
        await asyncio.sleep(0.3)  # longer than stream_timeout_ms
        for _ in range(5):
            yield AudioFrame(
                np.ones(BLOCKSIZE, dtype=np.int16).tobytes(), SAMPLE_RATE, 1, BLOCKSIZE
            )

    mixer = AudioMixer(sample_rate=SAMPLE_RATE, num_channels=1, stream_timeout_ms=100)
    mixer.add_stream(slow_stream())
    mixer.end_input()

    async def read_all():
        return [frame async for frame in mixer]

    frames = await asyncio.wait_for(read_all(), timeout=5)
    await mixer.aclose()

    frames_with_audio = [f for f in frames if np.any(np.frombuffer(f.data.tobytes(), np.int16))]
    assert len(frames_with_audio) == 5


@pytest.mark.asyncio
async def test_mixer_aclose_waits_for_pending_stream_cleanup():
    """
    Closing the mixer must finish cancelling an in-flight stream read, so the
    stream's cleanup has completed by the time `aclose` returns.
    """
    cleaned_up = False

    async def stream_with_slow_cleanup():
        nonlocal cleaned_up
        try:
            await asyncio.sleep(10)
            yield AudioFrame(
                np.ones(BLOCKSIZE, dtype=np.int16).tobytes(), SAMPLE_RATE, 1, BLOCKSIZE
            )
        finally:
            await asyncio.sleep(0.1)
            cleaned_up = True

    mixer = AudioMixer(sample_rate=SAMPLE_RATE, num_channels=1, stream_timeout_ms=50)
    mixer.add_stream(stream_with_slow_cleanup())
    await asyncio.sleep(0.2)  # the read is pending and has missed the timeout

    await mixer.aclose()

    assert cleaned_up


@pytest.mark.asyncio
async def test_mixer_aclose_waits_for_cleanup_of_a_removed_stream():
    """A stream removed while its read is pending is also finished by `aclose`."""
    cleaned_up = False

    async def stream_with_slow_cleanup():
        nonlocal cleaned_up
        try:
            await asyncio.sleep(10)
            yield AudioFrame(
                np.ones(BLOCKSIZE, dtype=np.int16).tobytes(), SAMPLE_RATE, 1, BLOCKSIZE
            )
        finally:
            await asyncio.sleep(0.1)
            cleaned_up = True

    stream = stream_with_slow_cleanup()
    mixer = AudioMixer(sample_rate=SAMPLE_RATE, num_channels=1, stream_timeout_ms=50)
    mixer.add_stream(stream)
    await asyncio.sleep(0.2)
    mixer.remove_stream(stream)

    await mixer.aclose()

    assert cleaned_up
