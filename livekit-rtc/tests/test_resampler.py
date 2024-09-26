from livekit.rtc import AudioResampler, AudioResamplerQuality
import time
import wave
import os


def test_audio_resampler():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    wav_file_path = os.path.join(current_dir, "test_audio.wav")

    # Open the wave file
    with wave.open(wav_file_path, "rb") as wf_in:
        n_channels = wf_in.getnchannels()
        sampwidth = wf_in.getsampwidth()
        n_frames = wf_in.getnframes()
        audio_data = bytearray(wf_in.readframes(n_frames))

    if sampwidth != 2:
        raise ValueError(f"Expected 16-bit PCM data, but got {sampwidth * 8}-bit.")

    qualities = [
        AudioResamplerQuality.QUICK,
        AudioResamplerQuality.LOW,
        AudioResamplerQuality.MEDIUM,
        AudioResamplerQuality.HIGH,
        AudioResamplerQuality.VERY_HIGH,
    ]

    for quality in qualities:
        total_time = 0
        nb_runs = 20
        output_frames = []
        for i in range(nb_runs):
            output_frames = []
            resampler = AudioResampler(44100, 8000, quality=quality)

            start_time = time.perf_counter()

            chunk_size = 1024 * n_channels * sampwidth
            output_frames = []
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i : i + chunk_size]
                frames = resampler.push(bytearray(chunk))
                output_frames.extend(frames)

            frames = resampler.flush()
            output_frames.extend(frames)

            end_time = time.perf_counter()
            total_time += end_time - start_time

        total_time = total_time * 1000
        print(f"Quality: {quality}, Average time: {total_time / nb_runs:.2f}ms")

        output_data = b""

        for frame in output_frames:
            output_data += frame.data

        with wave.open(f"audio_resampled_{quality.name}.wav", "wb") as wf_out:
            wf_out.setnchannels(n_channels)
            wf_out.setsampwidth(sampwidth)
            wf_out.setframerate(8000)
            wf_out.writeframes(output_data)
