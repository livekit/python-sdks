import os
import wave


from livekit.rtc import Aec


def test_cancel_echo():
    sample_rate = 48000
    num_channels = 1
    frames_per_chunk = sample_rate // 100

    current_dir = os.path.dirname(os.path.abspath(__file__))
    capture_wav = os.path.join(current_dir, "test_echo_capture.wav")
    render_wav = os.path.join(current_dir, "test_echo_render.wav")
    output_wav = os.path.join(current_dir, "test_echo_cancelled.wav")

    aec = Aec(sample_rate, num_channels)
    print("AEC Internal Handle:", aec._ffi_handle)

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

        bytes_per_sample = sampwidth

        while True:
            capture_bytes = wf_in_cap.readframes(frames_per_chunk)
            render_bytes = wf_in_rend.readframes(frames_per_chunk)

            if not capture_bytes and not render_bytes:
                break

            capture_chunk = bytearray(capture_bytes)
            render_chunk = bytearray(render_bytes)

            needed_capture_len = frames_per_chunk * bytes_per_sample * num_channels
            needed_render_len = frames_per_chunk * bytes_per_sample * num_channels

            if len(capture_chunk) < needed_capture_len:
                capture_chunk += b"\x00" * (needed_capture_len - len(capture_chunk))

            if len(render_chunk) < needed_render_len:
                render_chunk += b"\x00" * (needed_render_len - len(render_chunk))

            aec.cancel_echo(capture_chunk, render_chunk)
            wf_out.writeframes(capture_chunk)

    print("Done! Echo-cancelled audio saved to:", output_wav)
