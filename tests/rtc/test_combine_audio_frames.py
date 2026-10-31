from __future__ import annotations

import array
import pytest

from livekit import rtc
import livekit.rtc.utils as utils


def test_combine_audio_frames_allocates_exact_byte_size(monkeypatch: pytest.MonkeyPatch) -> None:
    allocated: list[int] = []
    orig_bytearray = bytearray

    def spy_bytearray(size: int) -> bytearray:
        allocated.append(size)
        return orig_bytearray(size)

    monkeypatch.setattr(utils, "bytearray", spy_bytearray, raising=False)

    f1 = rtc.AudioFrame(array.array("h", [1, 2, 3, 4]).tobytes(), 16000, 1, 4)
    f2 = rtc.AudioFrame(array.array("h", [5, 6, 7, 8]).tobytes(), 16000, 1, 4)
    combined = rtc.combine_audio_frames([f1, f2])

    assert len(allocated) == 1
    assert allocated[0] == combined.data.nbytes


def test_combine_audio_frames_concatenates_samples_correctly() -> None:
    f1 = rtc.AudioFrame(array.array("h", [10, 20, 30]).tobytes(), 16000, 1, 3)
    f2 = rtc.AudioFrame(array.array("h", [40, 50]).tobytes(), 16000, 1, 2)
    combined = rtc.combine_audio_frames([f1, f2])

    assert combined.sample_rate == 16000
    assert combined.num_channels == 1
    assert combined.samples_per_channel == 5
    assert list(combined.data) == [10, 20, 30, 40, 50]


def test_combine_audio_frames_stereo() -> None:
    # 2 channels, 2 samples per channel = 4 samples = 8 bytes
    f1 = rtc.AudioFrame(array.array("h", [1, 2, 3, 4]).tobytes(), 48000, 2, 2)
    f2 = rtc.AudioFrame(array.array("h", [5, 6, 7, 8]).tobytes(), 48000, 2, 2)
    combined = rtc.combine_audio_frames([f1, f2])

    assert combined.sample_rate == 48000
    assert combined.num_channels == 2
    assert combined.samples_per_channel == 4
    assert list(combined.data) == [1, 2, 3, 4, 5, 6, 7, 8]


def test_combine_audio_frames_single_frame() -> None:
    frame = rtc.AudioFrame(array.array("h", [1, 2, 3]).tobytes(), 16000, 1, 3)
    assert rtc.combine_audio_frames(frame) is frame


def test_combine_audio_frames_empty_raises() -> None:
    with pytest.raises(ValueError, match="buffer is empty"):
        rtc.combine_audio_frames([])


def test_combine_audio_frames_mismatched_sample_rate() -> None:
    f1 = rtc.AudioFrame(array.array("h", [1, 2]).tobytes(), 16000, 1, 2)
    f2 = rtc.AudioFrame(array.array("h", [3, 4]).tobytes(), 48000, 1, 2)
    with pytest.raises(ValueError, match="Sample rate mismatch"):
        rtc.combine_audio_frames([f1, f2])


def test_combine_audio_frames_mismatched_channels() -> None:
    f1 = rtc.AudioFrame(array.array("h", [1, 2]).tobytes(), 16000, 1, 2)
    f2 = rtc.AudioFrame(array.array("h", [3, 4, 5, 6]).tobytes(), 16000, 2, 2)
    with pytest.raises(ValueError, match="Channel count mismatch"):
        rtc.combine_audio_frames([f1, f2])


def test_combine_audio_frames_docstring_example() -> None:
    frame1 = rtc.AudioFrame(
        data=b"\x01\x00", sample_rate=48000, num_channels=1, samples_per_channel=1
    )
    frame2 = rtc.AudioFrame(
        data=b"\x02\x00", sample_rate=48000, num_channels=1, samples_per_channel=1
    )
    combined_frame = rtc.combine_audio_frames([frame1, frame2])
    assert combined_frame.data.tobytes() == b"\x01\x00\x02\x00"
    assert combined_frame.sample_rate == 48000
    assert combined_frame.num_channels == 1
    assert combined_frame.samples_per_channel == 2
