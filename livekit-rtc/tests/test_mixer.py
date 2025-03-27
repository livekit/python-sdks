# type: ignore

from typing import AsyncIterator
import numpy as np
import pytest
import matplotlib.pyplot as plt

from livekit.rtc import AudioMixer
from livekit.rtc.audio_frame import AudioFrame

SAMPLE_RATE = 48000
# Use 100ms blocks (i.e. 1600 samples per frame)
BLOCKSIZE = SAMPLE_RATE // 10


async def sine_wave_generator(freq: float, duration: float) -> AsyncIterator[AudioFrame]:
    total_frames = int((duration * SAMPLE_RATE) // BLOCKSIZE)
    t_frame = np.arange(BLOCKSIZE) / SAMPLE_RATE
    for i in range(total_frames):
        # Shift the time for each frame so that the sine wave is continuous
        t = t_frame + i * BLOCKSIZE / SAMPLE_RATE
        # Create a sine wave with amplitude 0.3 (to avoid clipping when summing)
        signal = 0.3 * np.sin(2 * np.pi * freq * t)
        # Convert from float [-0.5, 0.5] to int16 values
        signal_int16 = np.int16(signal * 32767)
        frame = AudioFrame(
            signal_int16.tobytes(),
            SAMPLE_RATE,
            1,
            BLOCKSIZE,
        )
        yield frame


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
    stream1 = sine_wave_generator(440, duration)
    stream2 = sine_wave_generator(880, duration)
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

    plt.figure(figsize=(10, 4))
    plt.plot(mixed_signal[:1000])  # plot 1000
    plt.title("Mixed Signal")
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.show()

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
