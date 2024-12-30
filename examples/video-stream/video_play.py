import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterable, Union
import sys

import numpy as np
import os
import signal
from livekit import api
from livekit import rtc

try:
    import av
except ImportError:
    raise RuntimeError(
        "av is required to run this example, install with `pip install av`"
    )

# ensure LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET are set

logger = logging.getLogger(__name__)


@dataclass
class MediaInfo:
    video_width: int
    video_height: int
    video_fps: float
    audio_sample_rate: int
    audio_channels: int


class MediaFileStreamer:
    """Streams video and audio frames from a media file in an endless loop."""

    def __init__(self, media_file: Union[str, Path]) -> None:
        self._media_file = str(media_file)
        # Create separate containers for each stream
        self._video_container = av.open(self._media_file)
        self._audio_container = av.open(self._media_file)

        # Cache media info
        video_stream = self._video_container.streams.video[0]
        audio_stream = self._audio_container.streams.audio[0]
        self._info = MediaInfo(
            video_width=video_stream.width,
            video_height=video_stream.height,
            video_fps=float(video_stream.average_rate),  # type: ignore
            audio_sample_rate=audio_stream.sample_rate,
            audio_channels=audio_stream.channels,
        )

    @property
    def info(self) -> MediaInfo:
        return self._info

    async def stream_video(self) -> AsyncIterable[tuple[rtc.VideoFrame, float]]:
        """Streams video frames from the media file in an endless loop."""
        for i, av_frame in enumerate(self._video_container.decode(video=0)):
            # Convert video frame to RGBA
            frame = av_frame.to_rgb().to_ndarray()
            frame_rgba = np.ones((frame.shape[0], frame.shape[1], 4), dtype=np.uint8)
            frame_rgba[:, :, :3] = frame
            yield (
                rtc.VideoFrame(
                    width=frame.shape[1],
                    height=frame.shape[0],
                    type=rtc.VideoBufferType.RGBA,
                    data=frame_rgba.tobytes(),
                ),
                av_frame.time,
            )

    async def stream_audio(self) -> AsyncIterable[tuple[rtc.AudioFrame, float]]:
        """Streams audio frames from the media file in an endless loop."""
        for i, av_frame in enumerate(self._audio_container.decode(audio=0)):
            # Convert audio frame to raw int16 samples
            frame = av_frame.to_ndarray().T  # Transpose to (samples, channels)
            frame = (frame * 32768).astype(np.int16)
            duration = len(frame) / self.info.audio_sample_rate
            yield (
                rtc.AudioFrame(
                    data=frame.tobytes(),
                    sample_rate=self.info.audio_sample_rate,
                    num_channels=frame.shape[1],
                    samples_per_channel=frame.shape[0],
                ),
                av_frame.time + duration,
            )

    def reset(self):
        self._video_container.seek(0)
        self._audio_container.seek(0)

    async def aclose(self) -> None:
        """Closes the media container and stops streaming."""
        self._video_container.close()
        self._audio_container.close()


async def main(room: rtc.Room, room_name: str, media_path: str):
    token = (
        api.AccessToken()
        .with_identity("python-publisher")
        .with_name("Python Publisher")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                agent=True,
            )
        )
        .to_jwt()
    )
    url = os.getenv("LIVEKIT_URL")
    logging.info("connecting to %s", url)

    try:
        await room.connect(url, token)
        logging.info("connected to room %s", room.name)
    except rtc.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
        return

    # Create media streamer
    streamer = MediaFileStreamer(media_path)
    media_info = streamer.info

    # Create video and audio sources/tracks
    queue_size_ms = 1000  # TODO: testing with different sizes
    video_source = rtc.VideoSource(
        width=media_info.video_width,
        height=media_info.video_height,
    )
    logger.info(media_info)
    audio_source = rtc.AudioSource(
        sample_rate=media_info.audio_sample_rate,
        num_channels=media_info.audio_channels,
        queue_size_ms=queue_size_ms,
    )

    video_track = rtc.LocalVideoTrack.create_video_track("video", video_source)
    audio_track = rtc.LocalAudioTrack.create_audio_track("audio", audio_source)

    # Publish tracks
    video_options = rtc.TrackPublishOptions(
        source=rtc.TrackSource.SOURCE_CAMERA,
        video_encoding=rtc.VideoEncoding(
            max_framerate=30,
            max_bitrate=5_000_000,
        ),
    )
    audio_options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)

    await room.local_participant.publish_track(video_track, video_options)
    await room.local_participant.publish_track(audio_track, audio_options)

    av_sync = rtc.AVSynchronizer(
        audio_source=audio_source,
        video_source=video_source,
        video_fps=media_info.video_fps,
        video_queue_size_ms=queue_size_ms,
    )

    async def _push_frames(
        stream: AsyncIterable[tuple[rtc.VideoFrame | rtc.AudioFrame, float]],
        av_sync: rtc.AVSynchronizer,
    ):
        async for frame, timestamp in stream:
            await av_sync.push(frame, timestamp)
            await asyncio.sleep(0)

    try:
        while True:
            streamer.reset()
            video_task = asyncio.create_task(
                _push_frames(streamer.stream_video(), av_sync)
            )
            audio_task = asyncio.create_task(
                _push_frames(streamer.stream_audio(), av_sync)
            )

            # wait for both tasks to complete
            await asyncio.gather(video_task, audio_task)
            await av_sync.wait_for_playout()
            logger.info("playout finished")
    finally:
        await streamer.aclose()
        await av_sync.aclose()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.FileHandler("video_play.log"), logging.StreamHandler()],
    )

    if len(sys.argv) != 3:
        print("Usage: python video_play.py <room-name> </path/to/video>")
        sys.exit(1)

    room_name = sys.argv[1]
    media_path = sys.argv[2]

    loop = asyncio.get_event_loop()
    room = rtc.Room(loop=loop)

    async def cleanup():
        await room.disconnect()
        loop.stop()

    asyncio.ensure_future(main(room, room_name, media_path))
    for signal in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(signal, lambda: asyncio.ensure_future(cleanup()))

    try:
        loop.run_forever()
    finally:
        loop.close()
