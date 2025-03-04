import os
import wave
import numpy as np

from livekit.rtc import AudioProcessingModule, AudioFrame


def test_audio_processing():
    sample_rate = 48000
    num_channels = 1
    frames_per_chunk = sample_rate // 100

    current_dir = os.path.dirname(os.path.abspath(__file__))
    capture_wav = os.path.join(current_dir, "test_echo_capture.wav")
    render_wav = os.path.join(current_dir, "test_echo_render.wav")
    output_wav = os.path.join(current_dir, "test_processed.wav")

    # Initialize APM with echo cancellation enabled
    apm = AudioProcessingModule(
        echo_cancellation=True,
        noise_suppression=True,
        high_pass_filter=True,
        auto_gain_control=True,
    )
    print("APM Internal Handle:", apm._ffi_handle)

    with (
        wave.open(capture_wav, "rb") as wf_in_cap,
        wave.open(render_wav, "rb") as wf_in_rend,
        wave.open(output_wav, "wb") as wf_out,
    ):
        assert wf_in_cap.getnchannels() == num_channels, "Capture file must be mono."
        assert wf_in_rend.getnchannels() == num_channels, "Render file must be mono."
        assert wf_in_cap.getframerate() == sample_rate, "Capture file must be 48 kHz."
        assert wf_in_rend.getframerate() == sample_rate, "Render file must be 48 kHz."

        sampwidth = wf_in_cap.getsampwidth()
        wf_out.setnchannels(num_channels)
        wf_out.setsampwidth(sampwidth)
        wf_out.setframerate(sample_rate)

        while True:
            capture_bytes = wf_in_cap.readframes(frames_per_chunk)
            render_bytes = wf_in_rend.readframes(frames_per_chunk)

            if not capture_bytes and not render_bytes:
                break

            # Convert bytes to numpy arrays
            capture_data = np.frombuffer(capture_bytes, dtype=np.int16)
            render_data = np.frombuffer(render_bytes, dtype=np.int16)

            # Pad if necessary
            if len(capture_data) < frames_per_chunk:
                capture_data = np.pad(capture_data, (0, frames_per_chunk - len(capture_data)))
            if len(render_data) < frames_per_chunk:
                render_data = np.pad(render_data, (0, frames_per_chunk - len(render_data)))

            capture_frame = AudioFrame(
                data=capture_data.tobytes(),
                sample_rate=sample_rate,
                num_channels=num_channels,
                samples_per_channel=frames_per_chunk,
            )
            render_frame = AudioFrame(
                data=render_data.tobytes(),
                sample_rate=sample_rate,
                num_channels=num_channels,
                samples_per_channel=frames_per_chunk,
            )

            # Process both streams
            apm.process_reverse_stream(render_frame)
            apm.process_stream(capture_frame)

            wf_out.writeframes(capture_frame.data.tobytes())

    print("Done! Processed audio saved to:", output_wav)
