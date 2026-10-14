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
async def test_mixer_keeps_async_generator_after_a_timeout():
    """
    A stream that misses the timeout once must not be closed: cancelling the
    pending read of an async generator ends it, which dropped the rest of its audio.
    """
    frames, block = 10, 480

    async def late_once():
        for i in range(frames):
            if i == 3:
                await asyncio.sleep(0.25)
            yield AudioFrame(np.full(block, 1000, dtype=np.int16).tobytes(), SAMPLE_RATE, 1, block)

    mixer = AudioMixer(
        sample_rate=SAMPLE_RATE, num_channels=1, blocksize=block, stream_timeout_ms=100
    )
    mixer.add_stream(late_once())
    mixer.end_input()

    with_audio = 0
    async for frame in mixer:
        if np.frombuffer(frame.data.tobytes(), dtype=np.int16).any():
            with_audio += 1
    await mixer.aclose()

    assert with_audio == frames


@pytest.mark.asyncio
async def test_mixer_drops_a_stalled_stream_after_end_input():
    async def one_frame_then_stall():
        yield AudioFrame(np.full(480, 1000, dtype=np.int16).tobytes(), SAMPLE_RATE, 1, 480)
        await asyncio.Event().wait()

    mixer = AudioMixer(sample_rate=SAMPLE_RATE, num_channels=1, blocksize=480, stream_timeout_ms=50)
    mixer.add_stream(one_frame_then_stall())
    mixer.end_input()

    async def drain():
        return [frame async for frame in mixer]

    draining = asyncio.ensure_future(drain())
    done, _ = await asyncio.wait({draining}, timeout=1)
    await mixer.aclose()
    assert done
    assert len(draining.result()) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("how", ["remove_stream", "aclose"])
async def test_mixer_cancels_a_pending_read_when_the_stream_goes_away(how):
    closed = asyncio.Event()

    async def never_yields():
        try:
            await asyncio.Event().wait()
            yield  # pragma: no cover
        finally:
            closed.set()

    mixer = AudioMixer(sample_rate=SAMPLE_RATE, num_channels=1, blocksize=480, stream_timeout_ms=50)
    stream = never_yields()
    mixer.add_stream(stream)
    await asyncio.sleep(0.12)  # at least one round has timed out on the stream

    if how == "remove_stream":
        mixer.remove_stream(stream)
    else:
        await mixer.aclose()

    await asyncio.wait_for(closed.wait(), timeout=1)
    assert not mixer._pending_reads
    await mixer.aclose()


@pytest.mark.asyncio
async def test_mixer_starts_no_read_on_a_removed_stream():
    # a round can be scheduled before remove_stream() and run after it
    async def never_yields():
        await asyncio.Event().wait()
        yield  # pragma: no cover

    mixer = AudioMixer(sample_rate=SAMPLE_RATE, num_channels=1, blocksize=480, stream_timeout_ms=10)
    stream = never_yields()
    mixer.add_stream(stream)
    mixer.remove_stream(stream)

    await mixer._get_contribution(stream, np.empty((0, 1), dtype=np.int16))
    assert not mixer._pending_reads
    await mixer.aclose()


@pytest.mark.asyncio
async def test_mixer_keeps_buffered_audio_when_a_stream_raises_timeout_error():
    async def partial_then_timeout():
        yield AudioFrame(np.full(240, 1000, dtype=np.int16).tobytes(), SAMPLE_RATE, 1, 240)
        raise asyncio.TimeoutError

    mixer = AudioMixer(sample_rate=SAMPLE_RATE, num_channels=1, blocksize=480)
    mixer.add_stream(partial_then_timeout())
    mixer.end_input()

    with_audio = 0
    async for frame in mixer:
        if np.frombuffer(frame.data.tobytes(), dtype=np.int16).any():
            with_audio += 1
    await mixer.aclose()

    assert with_audio == 1


@pytest.mark.asyncio
async def test_mixer_aclose_waits_for_a_cancelled_read_to_clean_up():
    cleaned_up = False

    async def slow_cleanup():
        nonlocal cleaned_up
        try:
            await asyncio.Event().wait()
            yield  # pragma: no cover
        finally:
            await asyncio.sleep(0.1)
            cleaned_up = True

    mixer = AudioMixer(sample_rate=SAMPLE_RATE, num_channels=1, blocksize=480, stream_timeout_ms=50)
    mixer.add_stream(slow_cleanup())
    await asyncio.sleep(0.12)

    await mixer.aclose()
    assert cleaned_up
