import os
import wave
import numpy as np

from livekit.rtc import AudioProcessingModule, AudioFrame

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def test_agc_modifies_audio() -> None:
    num_channels = 1

    input_wav = os.path.join(FIXTURES_DIR, "test_audio.wav")
    output_wav = os.path.join(FIXTURES_DIR, "test_processed.wav")

    apm = AudioProcessingModule(auto_gain_control=True)

    any_frame_modified = False

    with wave.open(input_wav, "rb") as wf_in:
        assert wf_in.getnchannels() == num_channels, "Input file must be mono."
        sample_rate = wf_in.getframerate()
        sampwidth = wf_in.getsampwidth()
        frames_per_chunk = sample_rate // 100

        with wave.open(output_wav, "wb") as wf_out:
            wf_out.setnchannels(num_channels)
            wf_out.setsampwidth(sampwidth)
            wf_out.setframerate(sample_rate)

            while True:
                raw_bytes = wf_in.readframes(frames_per_chunk)
                if not raw_bytes:
                    break

                data = np.frombuffer(raw_bytes, dtype=np.int16)
                if len(data) < frames_per_chunk:
                    data = np.pad(data, (0, frames_per_chunk - len(data)))

                original = data.copy()

                frame = AudioFrame(
                    data=data.tobytes(),
                    sample_rate=sample_rate,
                    num_channels=num_channels,
                    samples_per_channel=frames_per_chunk,
                )

                apm.process_stream(frame)

                processed = np.frombuffer(frame.data, dtype=np.int16)
                if not np.array_equal(original, processed):
                    any_frame_modified = True

                wf_out.writeframes(frame.data.tobytes())

    assert any_frame_modified, (
        "APM did not modify any audio frames — processing may be a no-op. "
        "With AGC enabled, output should differ from input."
    )


def test_agc_initial_gain() -> None:
    input_wav = os.path.join(FIXTURES_DIR, "test_audio.wav")

    with wave.open(input_wav, "rb") as wf_in:
        sample_rate = wf_in.getframerate()
        data = np.frombuffer(wf_in.readframes(sample_rate), dtype=np.int16)

    frames_per_chunk = sample_rate // 100

    def output_rms(apm: AudioProcessingModule) -> float:
        processed = []
        for start in range(0, len(data) - frames_per_chunk + 1, frames_per_chunk):
            frame = AudioFrame(
                data=data[start : start + frames_per_chunk].tobytes(),
                sample_rate=sample_rate,
                num_channels=1,
                samples_per_channel=frames_per_chunk,
            )
            apm.process_stream(frame)
            processed.append(np.frombuffer(frame.data, dtype=np.int16))
        return float(np.sqrt(np.mean(np.concatenate(processed).astype(np.float64) ** 2)))

    default_rms = output_rms(AudioProcessingModule(auto_gain_control=True))
    zero_rms = output_rms(
        AudioProcessingModule(auto_gain_control=True, auto_gain_control_initial_gain_db=0.0)
    )

    assert zero_rms < default_rms, (
        "AGC with a 0 dB initial gain should apply less gain at the start than the default."
    )
