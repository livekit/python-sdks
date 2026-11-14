from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Optional

from livekit import rtc
from livekit.rtc.synchronizer import _FPSController


class _FakeVideoSource:
    def __init__(self) -> None:
        self.frames: list[rtc.VideoFrame] = []
        self.on_capture: Optional[Callable[[], None]] = None

    def capture_frame(self, frame: rtc.VideoFrame) -> None:
        self.frames.append(frame)
        if self.on_capture is not None:
            self.on_capture()


class _FakeAudioSource:
    queued_duration = 0.0

    async def wait_for_playout(self) -> None:
        pass


async def test_fps_controller_schedules_from_now_after_a_reset_mid_frame() -> None:
    controller = _FPSController(expected_fps=10)

    await controller.wait_next_process()
    controller.reset()
    before = time.perf_counter()
    controller.after_process()

    assert controller._next_frame_time is not None
    assert before + 0.1 <= controller._next_frame_time <= time.perf_counter() + 0.1


async def test_av_synchronizer_keeps_sending_after_a_reset_mid_frame() -> None:
    video = _FakeVideoSource()
    source: Any = _FakeAudioSource()
    sync = rtc.AVSynchronizer(audio_source=source, video_source=video, video_fps=100)  # type: ignore[arg-type]
    frames = [rtc.VideoFrame(2, 2, rtc.VideoBufferType.RGBA, bytes(16)) for _ in range(3)]

    # reset() from inside the capture lands between wait_next_process() and after_process()
    video.on_capture = sync.reset
    try:
        for frame in frames:
            await sync.push(frame)
        await asyncio.wait_for(sync.wait_for_playout(), timeout=2)
    finally:
        await sync.aclose()

    assert video.frames == frames
