from __future__ import annotations

import ctypes

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


@pytest.mark.parametrize(
    "name",
    ["RGBA", "ABGR", "ARGB", "BGRA", "RGB24", "I420", "I420A", "I422", "I444", "I010", "NV12"],
)
def test_frame_rejects_data_shorter_than_the_format_needs(name: str) -> None:
    t, w, h = getattr(T, name), 5, 3
    length = video_frame._get_plane_length(t, w, h)

    rtc.VideoFrame(w, h, t, bytearray(length))
    with pytest.raises(ValueError):
        rtc.VideoFrame(w, h, t, bytearray(length - 1))


def test_frame_measures_a_memoryview_in_bytes() -> None:
    w, h = 4, 3
    pixels = memoryview(bytearray(w * h * 4))

    rtc.VideoFrame(w, h, T.RGBA, pixels.cast("B", shape=[h, w, 4]))
    rtc.VideoFrame(w, h, T.RGBA, pixels.cast("I"))
    with pytest.raises(ValueError):
        rtc.VideoFrame(w, h, T.RGBA, pixels[:-4].cast("I"))
