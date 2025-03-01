import asyncio
import logging
import time
from collections import deque
from typing import Optional, Union

from .video_frame import VideoFrame
from .audio_frame import AudioFrame
from .audio_source import AudioSource
from .video_source import VideoSource


logger = logging.getLogger(__name__)


class AVSynchronizer:
    """Synchronize audio and video capture.

    Usage:
        av_sync = AVSynchronizer(
            audio_source=audio_source,
            video_source=video_source,
            video_fps=video_fps,
        )

        async for video_frame, audio_frame in video_generator:
            await av_sync.push(video_frame)
            await av_sync.push(audio_frame)
    """

    def __init__(
        self,
        *,
        audio_source: AudioSource,
        video_source: VideoSource,
        video_fps: float,
        video_queue_size_ms: float = 100,
        _max_delay_tolerance_ms: float = 300,
    ):
        self._audio_source = audio_source
        self._video_source = video_source
        self._video_fps = video_fps
        self._video_queue_size_ms = video_queue_size_ms
        self._max_delay_tolerance_ms = _max_delay_tolerance_ms

        self._stopped = False
        # the time of the last video/audio frame captured
        self._last_video_time: float = 0
        self._last_audio_time: float = 0

        self._video_queue_max_size = int(self._video_fps * self._video_queue_size_ms / 1000)
        if self._video_queue_size_ms > 0:
            # ensure queue is bounded if queue size is specified
            self._video_queue_max_size = max(1, self._video_queue_max_size)

        self._video_queue = asyncio.Queue[tuple[VideoFrame, Optional[float]]](
            maxsize=self._video_queue_max_size
        )
        self._fps_controller = _FPSController(
            expected_fps=self._video_fps,
            max_delay_tolerance_ms=self._max_delay_tolerance_ms,
        )
        self._capture_video_task = asyncio.create_task(self._capture_video())

    async def push(
        self, frame: Union[VideoFrame, AudioFrame], timestamp: Optional[float] = None
    ) -> None:
        """Push a frame to the synchronizer

        Args:
            frame: The video or audio frame to push.
            timestamp: (optional) The timestamp of the frame, for logging purposes for now.
                For AudioFrame, it should be the end time of the frame.
        """
        if isinstance(frame, AudioFrame):
            await self._audio_source.capture_frame(frame)
            if timestamp is not None:
                self._last_audio_time = timestamp
            return

        await self._video_queue.put((frame, timestamp))

    async def clear_queue(self) -> None:
        self._audio_source.clear_queue()
        while not self._video_queue.empty():
            await self._video_queue.get()
            self._video_queue.task_done()

    async def wait_for_playout(self) -> None:
        """Wait until all video and audio frames are played out."""
        await asyncio.gather(
            self._audio_source.wait_for_playout(),
            self._video_queue.join(),
        )

    def reset(self) -> None:
        self._fps_controller.reset()

    async def _capture_video(self) -> None:
        while not self._stopped:
            frame, timestamp = await self._video_queue.get()
            async with self._fps_controller:
                self._video_source.capture_frame(frame)
                if timestamp is not None:
                    self._last_video_time = timestamp
            self._video_queue.task_done()

    async def aclose(self) -> None:
        self._stopped = True
        if self._capture_video_task:
            self._capture_video_task.cancel()

    @property
    def actual_fps(self) -> float:
        return self._fps_controller.actual_fps

    @property
    def last_video_time(self) -> float:
        """The time of the last video frame captured"""
        return self._last_video_time

    @property
    def last_audio_time(self) -> float:
        """The time of the last audio frame played out"""
        return self._last_audio_time - self._audio_source.queued_duration


class _FPSController:
    def __init__(self, *, expected_fps: float, max_delay_tolerance_ms: float = 300) -> None:
        """Controls frame rate by adjusting sleep time based on actual FPS.

        Usage:
            async with _FPSController(expected_fps=30):
                # process frame
                pass

        Args:
            expected_fps: Target frames per second
            max_delay_tolerance_ms: Maximum delay tolerance in milliseconds
        """
        self._expected_fps = expected_fps
        self._frame_interval = 1.0 / expected_fps
        self._max_delay_tolerance_secs = max_delay_tolerance_ms / 1000

        self._next_frame_time: Optional[float] = None
        self._fps_calc_winsize = max(2, int(1.0 * expected_fps))
        self._send_timestamps: deque[float] = deque(maxlen=self._fps_calc_winsize)

    async def __aenter__(self) -> None:
        await self.wait_next_process()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.after_process()

    def reset(self) -> None:
        self._next_frame_time = None
        self._send_timestamps.clear()

    async def wait_next_process(self) -> None:
        """Wait until it's time for the next frame.

        Adjusts sleep time based on actual FPS to maintain target rate.
        """
        current_time = time.perf_counter()

        # initialize the next frame time
        if self._next_frame_time is None:
            self._next_frame_time = current_time

        # calculate sleep time
        sleep_time = self._next_frame_time - current_time
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
        else:
            # check if significantly behind schedule
            if -sleep_time > self._max_delay_tolerance_secs:
                logger.warning(f"Frame capture was behind schedule for {-sleep_time * 1000:.2f} ms")
                self._next_frame_time = time.perf_counter()

    def after_process(self) -> None:
        """Update timing information after processing a frame."""
        assert self._next_frame_time is not None, "wait_next_process must be called first"

        # update timing information
        self._send_timestamps.append(time.perf_counter())

        # calculate next frame time
        self._next_frame_time += self._frame_interval

    @property
    def expected_fps(self) -> float:
        return self._expected_fps

    @property
    def actual_fps(self) -> float:
        """Get current average FPS."""
        if len(self._send_timestamps) < 2:
            return 0

        return (len(self._send_timestamps) - 1) / (
            self._send_timestamps[-1] - self._send_timestamps[0]
        )
