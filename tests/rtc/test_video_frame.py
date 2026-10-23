from __future__ import annotations

import array
import ctypes
import gc
import weakref

import pytest

from livekit import rtc
from livekit.rtc import video_frame
from livekit.rtc._proto import video_frame_pb2 as proto_video

T = proto_video.VideoBufferType


def _chroma(n: int) -> int:
    return (n + 1) // 2


# Plane sizes in bytes, in memory order, for a tightly packed frame of each format.
def _expected_planes(t: int, w: int, h: int) -> list[int]:
    cw, ch = _chroma(w), _chroma(h)
    return {
        T.I420: [w * h, cw * ch, cw * ch],
        T.I420A: [w * h, cw * ch, cw * ch, w * h],
        T.I422: [w * h, cw * h, cw * h],
        T.I444: [w * h, w * h, w * h],
        T.I010: [w * h * 2, cw * ch * 2, cw * ch * 2],
        T.NV12: [w * h, cw * ch * 2],
    }[t]


@pytest.mark.parametrize("name", ["I420", "I420A", "I422", "I444", "I010", "NV12"])
@pytest.mark.parametrize(("w", "h"), [(640, 480), (480, 640), (5, 3)])
def test_planes_are_packed_and_match_the_frame_length(name: str, w: int, h: int) -> None:
    t = getattr(T, name)
    planes = video_frame._get_plane_infos(0, t, w, h)

    assert [p.size for p in planes] == _expected_planes(t, w, h)
    offset = 0
    for plane in planes:
        assert plane.data_ptr == offset
        offset += plane.size
    assert video_frame._get_plane_length(t, w, h) == offset


@pytest.mark.parametrize("name", ["I420A", "NV12"])
def test_frame_from_the_ffi_copies_exactly_the_frame(name: str) -> None:
    # Frames received from a VideoStream are copied out of FFI memory with this length.
    t, w, h = getattr(T, name), 640, 480
    expected = sum(_expected_planes(t, w, h))
    buf = (ctypes.c_uint8 * (expected * 2))()  # room past the frame, so main over-reads safely
    owned = proto_video.OwnedVideoBuffer()
    owned.info.type, owned.info.width, owned.info.height = t, w, h
    owned.info.data_ptr = ctypes.addressof(buf)

    frame = rtc.VideoFrame._from_owned_info(owned)

    assert len(frame.data) == expected


def test_get_plane_returns_each_i422_plane() -> None:
    w, h = 4, 2
    y, u, v = b"\x01" * (w * h), b"\x02" * (_chroma(w) * h), b"\x03" * (_chroma(w) * h)
    frame = rtc.VideoFrame(w, h, T.I422, y + u + v)

    assert [bytes(frame.get_plane(i)) for i in range(3)] == [y, u, v]


@pytest.mark.parametrize("plane_nth", [-1, -3, -4, 3])
def test_get_plane_returns_none_outside_the_planes(plane_nth: int) -> None:
    frame = rtc.VideoFrame(4, 2, T.I420, bytes(8 + 2 + 2))

    assert frame.get_plane(plane_nth) is None


def test_a_plane_keeps_the_frame_buffer_alive() -> None:
    buffer = array.array("B", [1] * 8 + [2] * 2 + [3] * 2)
    buffer_ref = weakref.ref(buffer)

    plane = rtc.VideoFrame(4, 2, T.I420, memoryview(buffer)).get_plane(2)
    del buffer
    gc.collect()

    # the frame is gone; the plane is the only thing left pointing at the buffer
    assert buffer_ref() is not None
    assert plane is not None and bytes(plane) == b"\x03\x03"


def test_a_plane_of_a_bytes_frame_is_read_only() -> None:
    plane = rtc.VideoFrame(4, 2, T.I420, bytes(8 + 2 + 2)).get_plane(0)

    assert plane is not None and plane.readonly
