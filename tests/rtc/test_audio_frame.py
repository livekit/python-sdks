from __future__ import annotations

import array
import io
import types
import wave

import pytest

from livekit import rtc


def _frame(samples: list[int], samples_per_channel: int, num_channels: int = 1) -> rtc.AudioFrame:
    return rtc.AudioFrame(
        array.array("h", samples).tobytes(), 16000, num_channels, samples_per_channel
    )


def test_data_holds_only_the_frame_samples() -> None:
    # the buffer may be larger than the frame; the samples past it are not part of the frame
    frame = _frame([1, 2, 3, 4, 99, 99], samples_per_channel=2, num_channels=2)

    assert list(frame.data) == [1, 2, 3, 4]


def test_combine_audio_frames_keeps_every_frame_sample() -> None:
    combined = rtc.combine_audio_frames([_frame([1, 2, 99, 99], 2), _frame([3, 4], 2)])

    assert combined.samples_per_channel == 4
    assert list(combined.data) == [1, 2, 3, 4]


def test_to_wav_bytes_writes_only_the_frame_samples() -> None:
    frame = _frame([1, 2, 99, 99], samples_per_channel=2)

    with wave.open(io.BytesIO(frame.to_wav_bytes())) as wav:
        assert wav.getnframes() == 2
        assert array.array("h", wav.readframes(wav.getnframes())).tolist() == [1, 2]


def test_frame_over_a_larger_bytearray_shares_its_memory() -> None:
    # AudioProcessingModule processes frames in place, so the frame must not copy the buffer
    buffer = bytearray(array.array("h", [1, 2, 99, 99]).tobytes())
    frame = rtc.AudioFrame(buffer, 16000, 1, 2)

    frame.data[0] = 7
    assert array.array("h", bytes(buffer[:2])).tolist() == [7]


@pytest.mark.parametrize("method", ["process_stream", "process_reverse_stream"])
def test_apm_sends_only_the_frame_bytes(monkeypatch: pytest.MonkeyPatch, method: str) -> None:
    from livekit.rtc import apm as apm_module

    requests = []

    class _FakeClient:
        def request(self, req):  # type: ignore[no-untyped-def]
            requests.append(req)
            return apm_module.proto_ffi.FfiResponse()

    monkeypatch.setattr(apm_module, "FfiClient", types.SimpleNamespace(instance=_FakeClient()))
    module = object.__new__(apm_module.AudioProcessingModule)
    module._ffi_handle = types.SimpleNamespace(handle=1)  # type: ignore[assignment]

    # a 10 ms mono frame at 16 kHz over a buffer with 40 extra samples
    getattr(module, method)(rtc.AudioFrame(bytearray(400), 16000, 1, 160))

    sent = getattr(requests[0], "apm_" + method)
    assert sent.size == 320


def test_serialized_frame_holds_only_the_frame_samples() -> None:
    pydantic = pytest.importorskip("pydantic")
    adapter = pydantic.TypeAdapter(rtc.AudioFrame)

    data = adapter.dump_python(_frame([1, 2, 99, 99], samples_per_channel=2))

    assert list(adapter.validate_python(data).data) == [1, 2]
