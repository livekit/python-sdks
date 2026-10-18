# Copyright 2026 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import asyncio
import threading

import pytest

from livekit import rtc


@pytest.mark.asyncio
async def test_audio_source_aclose_releases_waiter_and_cancels_timer() -> None:
    source = rtc.AudioSource(48000, 1)
    frame = rtc.AudioFrame.create(48000, 1, 48000)
    await asyncio.wait_for(source.capture_frame(frame), timeout=5.0)

    assert source._join_fut is not None
    assert source._join_handle is not None

    await asyncio.wait_for(source.aclose(), timeout=5.0)

    assert source._ffi_handle.disposed
    assert source._join_fut is None
    assert source._join_handle is None

    # After aclose, wait_for_playout should return immediately without hanging
    await asyncio.wait_for(source.wait_for_playout(), timeout=2.0)

    # Repeated calls are idempotent
    await asyncio.wait_for(source.aclose(), timeout=2.0)


def test_audio_source_sync_close() -> None:
    source = rtc.AudioSource(48000, 1)
    assert not source._ffi_handle.disposed

    source.close()
    assert source._ffi_handle.disposed

    # Repeated close is idempotent
    source.close()


def test_audio_source_cross_thread_close() -> None:
    source = rtc.AudioSource(48000, 1)
    assert not source._ffi_handle.disposed

    t = threading.Thread(target=source.close)
    t.start()
    t.join()

    assert source._ffi_handle.disposed


@pytest.mark.asyncio
async def test_audio_source_capture_after_close_is_noop() -> None:
    source = rtc.AudioSource(48000, 1)
    source.close()

    frame = rtc.AudioFrame.create(48000, 1, 480)
    # Should safely return without error
    await asyncio.wait_for(source.capture_frame(frame), timeout=2.0)


def test_video_source_sync_close() -> None:
    source = rtc.VideoSource(640, 480)
    assert not source._ffi_handle.disposed

    source.close()
    assert source._ffi_handle.disposed

    # Repeated close is idempotent
    source.close()


@pytest.mark.asyncio
async def test_video_source_aclose_and_capture_after_close() -> None:
    source = rtc.VideoSource(640, 480)
    assert not source._ffi_handle.disposed

    await asyncio.wait_for(source.aclose(), timeout=5.0)
    assert source._ffi_handle.disposed

    # Capture after close is safely ignored
    frame = rtc.VideoFrame(
        640,
        480,
        rtc.VideoBufferType.RGBA,
        b"\x00" * (640 * 480 * 4),
    )
    source.capture_frame(frame)

    # Repeated aclose is idempotent
    await asyncio.wait_for(source.aclose(), timeout=2.0)


def test_audio_source_init_outside_loop_and_capture_in_asyncio_run() -> None:
    source = rtc.AudioSource(48000, 1)
    assert source._loop is None
    frame = rtc.AudioFrame.create(48000, 1, 480)

    async def _capture() -> None:
        await asyncio.wait_for(source.capture_frame(frame), timeout=5.0)
        assert source._loop is not None
        assert source._loop.is_running()
        await asyncio.wait_for(source.aclose(), timeout=5.0)

    asyncio.run(_capture())


def test_audio_source_cross_thread_clear_queue() -> None:
    source = rtc.AudioSource(48000, 1)
    frame = rtc.AudioFrame.create(48000, 1, 48000)

    async def _run() -> None:
        await source.capture_frame(frame)
        assert source._join_fut is not None

        t = threading.Thread(target=source.clear_queue)
        t.start()
        t.join()

        # Playout waiter should be released by cross-thread clear_queue
        await asyncio.wait_for(source.wait_for_playout(), timeout=2.0)
        await source.aclose()

    asyncio.run(_run())


def test_audio_source_clear_queue_does_not_cancel_subsequent_capture() -> None:
    source = rtc.AudioSource(48000, 1, queue_size_ms=10000)
    frame1 = rtc.AudioFrame.create(48000, 1, 48000)
    frame2 = rtc.AudioFrame.create(48000, 1, 48000)

    async def _run() -> None:
        await source.capture_frame(frame1)
        gen1 = source._capture_gen

        # Simulate clear_queue scheduled from another thread
        loop = asyncio.get_running_loop()
        loop.call_soon(source._release_waiter, gen1)

        # Capture a subsequent frame before yielding
        await source.capture_frame(frame2)
        assert source._capture_gen > gen1
        assert source._join_fut is not None

        # Allow queued clear callback to execute
        await asyncio.sleep(0.01)

        # The subsequent frame's playout future and timer must not be cleared
        assert source._join_fut is not None
        assert not source._join_fut.done()

        await source.aclose()

    asyncio.run(_run())
