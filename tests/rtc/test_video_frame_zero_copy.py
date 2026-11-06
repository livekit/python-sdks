"""Borrowed video frames: the ones that read the SDK's buffer instead of a copy.

These exercise `VideoFrame._borrow_owned_info` and the lifetime rules around
it without a live room, by building the `OwnedVideoBuffer` the FFI would send
over a buffer this process owns.
"""

from __future__ import annotations

import asyncio
import ctypes
import itertools
from types import SimpleNamespace
from typing import Any, Callable

import pytest

from livekit.rtc._proto import video_frame_pb2 as proto_video
from livekit.rtc._utils import RingQueue
from livekit.rtc.video_frame import VideoFrame
from livekit.rtc.video_stream import (
    VideoFrameEvent,
    VideoStream,
    _close_discarded,
    _dropped_frames,
)

WIDTH = 64
HEIGHT = 32
I420_LEN = WIDTH * HEIGHT + ((WIDTH + 1) // 2) * ((HEIGHT + 1) // 2) * 2


class FakeNativeBuffer:
    """Stands in for the buffer the FFI hands over, and records its release.

    The real handle is an id into the Rust handle map. Here it is a ctypes
    array this process keeps alive, so the pointer stays valid for the whole
    test no matter when the frame releases it. Each instance gets its own
    handle id, so a test holding several can tell which one was released.
    """

    def __init__(self, handle_id: int, disposed_ids: set[int], fill: int = 0x7F) -> None:
        self.handle_id = handle_id
        self._disposed_ids = disposed_ids
        self.storage = (ctypes.c_uint8 * I420_LEN)(*([fill] * I420_LEN))

    @property
    def address(self) -> int:
        return ctypes.addressof(self.storage)

    @property
    def disposed(self) -> bool:
        return self.handle_id in self._disposed_ids

    def owned_info(self) -> proto_video.OwnedVideoBuffer:
        owned = proto_video.OwnedVideoBuffer()
        owned.handle.id = self.handle_id
        owned.info.type = proto_video.VideoBufferType.I420
        owned.info.width = WIDTH
        owned.info.height = HEIGHT
        owned.info.data_ptr = self.address
        return owned


@pytest.fixture
def new_native(monkeypatch: pytest.MonkeyPatch) -> Callable[[], FakeNativeBuffer]:
    """Mints fake FFI buffers whose releases are tracked per handle id.

    VideoFrame builds a real FfiHandle; this stops it from calling into the
    native library for handle ids that do not exist there.
    """
    disposed_ids: set[int] = set()
    ids = itertools.count(1000)

    def fake_dispose(self: Any) -> None:
        disposed_ids.add(self.handle)

    monkeypatch.setattr("livekit.rtc._ffi_client.FfiHandle.dispose", fake_dispose)
    return lambda: FakeNativeBuffer(next(ids), disposed_ids)


@pytest.fixture
def native(new_native: Callable[[], FakeNativeBuffer]) -> FakeNativeBuffer:
    return new_native()


def borrow(native: FakeNativeBuffer) -> VideoFrame:
    return VideoFrame._borrow_owned_info(native.owned_info())


def test_a_borrowed_frame_reads_the_native_buffer_without_copying(
    native: FakeNativeBuffer,
) -> None:
    frame = borrow(native)

    assert frame.is_borrowed
    assert frame.width == WIDTH and frame.height == HEIGHT
    assert len(frame.data) == I420_LEN
    assert bytes(frame.data[:4]) == b"\x7f\x7f\x7f\x7f"

    # The giveaway that nothing was copied: a write through the native buffer
    # shows up in the frame.
    native.storage[0] = 0x01
    assert frame.data[0] == 0x01

    frame.close()


def test_an_owned_frame_copies_and_releases_the_handle_immediately(
    native: FakeNativeBuffer,
) -> None:
    frame = VideoFrame._from_owned_info(native.owned_info())

    assert not frame.is_borrowed
    assert native.disposed, "the copying path is done with the buffer right away"

    native.storage[0] = 0x01
    assert frame.data[0] == 0x7F, "the copy is independent of the native buffer"


def test_closing_releases_the_handle_and_invalidates_the_data(
    native: FakeNativeBuffer,
) -> None:
    frame = borrow(native)
    assert not native.disposed, "the buffer stays out while the frame is open"

    frame.close()

    assert native.disposed
    assert not frame.is_borrowed
    with pytest.raises(RuntimeError, match="closed"):
        frame.data


def test_closing_twice_is_harmless(native: FakeNativeBuffer) -> None:
    frame = borrow(native)
    frame.close()
    frame.close()

    assert native.disposed


def test_closing_an_owned_frame_does_nothing(native: FakeNativeBuffer) -> None:
    frame = VideoFrame._from_owned_info(native.owned_info())

    frame.close()

    assert frame.data[0] == 0x7F, "an owned frame stays usable after close()"


def test_the_frame_works_as_a_context_manager(native: FakeNativeBuffer) -> None:
    with borrow(native) as frame:
        assert frame.data[0] == 0x7F

    assert native.disposed


def test_close_does_not_pretend_to_guard_outstanding_views(
    native: FakeNativeBuffer,
) -> None:
    """The documented hazard, pinned so nobody mistakes close() for a guard.

    A view built from `frame.data` re-exports the underlying array rather than
    the frame's memoryview, so CPython reports no outstanding export. close()
    releases the buffer regardless; this is the contract, not a bug.
    """
    frame = borrow(native)
    derived = frame.data

    frame.close()

    assert native.disposed, "close() releases the buffer unconditionally"
    assert derived.obj is not None, "the caller is left holding a dangling view"


def test_ring_queue_reports_evicted_items() -> None:
    discarded: list[int] = []
    queue: RingQueue[int] = RingQueue(capacity=2, on_discard=discarded.append)

    queue.put(1)
    queue.put(2)
    queue.put(3)

    assert discarded == [1], "the oldest item is handed back before it is dropped"


def test_ring_queue_get_nowait_drains_then_returns_none() -> None:
    queue: RingQueue[int] = RingQueue()
    queue.put(1)
    queue.put(2)

    assert [queue.get_nowait(), queue.get_nowait(), queue.get_nowait()] == [1, 2, None]


def test_plane_info_is_unused_by_the_borrowed_path_but_still_resolves(
    native: FakeNativeBuffer,
) -> None:
    # get_plane() derives plane offsets from the frame's own buffer address, so
    # it has to keep working for a frame backed by native memory.
    frame = borrow(native)

    y = frame.get_plane(0)

    assert y is not None
    assert len(y) == WIDTH * HEIGHT
    frame.close()


def test_handle_is_released_when_a_borrowed_frame_is_garbage_collected(
    native: FakeNativeBuffer,
) -> None:
    borrow(native)  # dropped immediately; __del__ is the backstop

    import gc

    gc.collect()

    assert native.disposed


# --- VideoStream's side of the borrow ----------------------------------------
#
# These drive the stream object directly rather than through a room: __init__
# talks to the FFI, so the tests build an instance without running it and then
# exercise the frame hand-off, which is what bounds a borrowed buffer's life.


def make_stream(zero_copy: bool, capacity: int = 0) -> VideoStream:
    stream = object.__new__(VideoStream)
    stream._zero_copy = zero_copy
    stream._borrowed = None
    stream._queue = RingQueue(capacity, on_discard=_close_discarded if zero_copy else None)
    # __anext__ checks this before reading the queue.
    stream._task = asyncio.get_event_loop().create_future()
    return stream


def frame_event(frame: VideoFrame) -> VideoFrameEvent:
    return VideoFrameEvent(frame=frame, timestamp_us=0, rotation=0, metadata=None)


@pytest.mark.asyncio
async def test_requesting_the_next_frame_closes_the_previous_borrow(
    native: FakeNativeBuffer, new_native: Callable[[], FakeNativeBuffer]
) -> None:
    second = new_native()
    stream = make_stream(zero_copy=True)
    stream._queue.put(frame_event(borrow(native)))
    stream._queue.put(frame_event(VideoFrame._borrow_owned_info(second.owned_info())))

    first_event = await stream.__anext__()
    assert not native.disposed, "the frame just handed out is still open"

    await stream.__anext__()

    assert native.disposed, "asking for the next frame ended the previous borrow"
    assert first_event.frame._closed


@pytest.mark.asyncio
async def test_an_owning_stream_never_closes_frames_behind_the_caller(
    native: FakeNativeBuffer,
) -> None:
    stream = make_stream(zero_copy=False)
    stream._queue.put(frame_event(VideoFrame._from_owned_info(native.owned_info())))
    stream._queue.put(frame_event(VideoFrame._from_owned_info(native.owned_info())))

    first_event = await stream.__anext__()
    await stream.__anext__()

    assert not first_event.frame._closed, "an owned frame stays valid indefinitely"
    assert first_event.frame.data[0] == 0x7F


@pytest.mark.asyncio
async def test_a_frame_evicted_by_a_full_queue_is_closed(
    native: FakeNativeBuffer, new_native: Callable[[], FakeNativeBuffer]
) -> None:
    stream = make_stream(zero_copy=True, capacity=1)
    evicted = borrow(native)
    stream._queue.put(frame_event(evicted))

    stream._queue.put(frame_event(borrow(new_native())))

    assert evicted._closed, "the dropped frame released its buffer immediately"
    assert native.disposed


@pytest.mark.asyncio
async def test_closing_the_stream_releases_the_outstanding_and_queued_frames(
    native: FakeNativeBuffer, new_native: Callable[[], FakeNativeBuffer]
) -> None:
    queued_buffer = new_native()
    stream = make_stream(zero_copy=True)
    stream._queue.put(frame_event(borrow(native)))
    stream._queue.put(frame_event(VideoFrame._borrow_owned_info(queued_buffer.owned_info())))

    await stream.__anext__()  # hands out the first, leaves the second queued
    stream._task.set_result(None)
    stream._ffi_handle = _NoopHandle()
    await stream.aclose()

    assert native.disposed, "the frame the caller was holding"
    assert queued_buffer.disposed, "the frame still sitting in the queue"


class _NoopHandle:
    def dispose(self) -> None:
        pass


# --- the dropped-frame counter ----------------------------------------------


def test_dropped_frames_reads_zero_when_the_ffi_predates_the_field() -> None:
    # The generated protos only gained `dropped_frames` alongside the native
    # counter. Against an older livekit_ffi the field is absent, and zero is
    # the honest answer: nothing was reported either way.
    frame_received = proto_video.VideoFrameReceived()

    assert _dropped_frames(frame_received) == 0


def test_dropped_frames_reads_the_field_when_the_ffi_provides_it() -> None:
    # Stands in for the regenerated message, so this keeps passing before and
    # after the rust-sdks bump.
    assert _dropped_frames(SimpleNamespace(dropped_frames=7)) == 7


def test_a_frame_event_defaults_to_no_dropped_frames() -> None:
    assert (
        frame_event(VideoFrame(1, 1, proto_video.VideoBufferType.RGBA, b"\0\0\0\0")).dropped_frames
        == 0
    )
