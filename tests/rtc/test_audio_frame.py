from __future__ import annotations

import ctypes

import pytest

from livekit import rtc


def test_frame_from_a_read_only_numpy_buffer_can_be_captured() -> None:
    # np.frombuffer returns a read-only array, so its memoryview is read-only too.
    np = pytest.importorskip("numpy")
    samples = bytes(range(8))
    frame = rtc.AudioFrame(memoryview(np.frombuffer(samples, dtype=np.uint8)), 48000, 1, 4)

    info = frame._proto_info()

    assert ctypes.string_at(info.data_ptr, len(samples)) == samples
