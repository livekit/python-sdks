"""Publish compressed WebM video from a file or a streaming HTTP response."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time
from dataclasses import replace
from typing import Iterator, TypeVar

import av
from livekit import api, rtc

from webm import demux

T = TypeVar("T")
logger = logging.getLogger(__name__)


async def read_next(frames: Iterator[T]) -> T | None:
    """Keep blocking HTTP/demux reads off the loop and join them on cancellation."""
    pending = asyncio.create_task(asyncio.to_thread(next, frames, None))
    try:
        return await asyncio.shield(pending)
    except asyncio.CancelledError:
        # av.open's read timeout bounds this wait. The container must not be
        # closed while a worker is using it.
        try:
            await pending
        finally:
            raise


async def publish(room: rtc.Room, frames: Iterator[rtc.EncodedVideoFrame], *, name: str) -> None:
    """Pace and publish one compressed video stream; always release its source."""
    frame = await read_next(frames)
    if frame is None:
        raise ValueError("WebM contains no video frames")
    if frame.frame_type != rtc.EncodedFrameType.ENCODED_FRAME_KEY:
        raise ValueError("WebM must start at a keyframe")
    source = rtc.EncodedVideoSource(frame.width, frame.height)
    publication = None
    try:
        track = rtc.LocalVideoTrack.create_video_track(name, source)
        publication = await room.local_participant.publish_track(
            track,
            rtc.TrackPublishOptions(
                video_codec=frame.codec,
                video_encoder=rtc.VideoEncoderBackend.ENCODER_BACKEND_PRE_ENCODED,
                simulcast=False,
            ),
        )
        # Do not consume a short file before the first subscriber is ready.
        await asyncio.wait_for(publication.wait_for_subscription(), timeout=30)
        origin_pts = frame.timestamp_us
        origin_clock = time.monotonic_ns() // 1000
        warned_feedback = False
        started = False
        startup_deadline = time.monotonic() + 5
        while frame is not None:
            timestamp = origin_clock + frame.timestamp_us - origin_pts
            await asyncio.sleep(max(0, (timestamp - time.monotonic_ns() // 1000) / 1_000_000))
            if not source.capture_frame(replace(frame, timestamp_us=timestamp)):
                raise RuntimeError("native source rejected the encoded frame")
            feedback = source.take_feedback()
            if not started:
                # Track subscription can precede native encoder initialization.
                # Keep the initial keyframe until it has processed a frame and
                # reported its rate target; otherwise a short file can lose its
                # only keyframe before the encoder is ready.
                if feedback.rate_control is None:
                    if time.monotonic() >= startup_deadline:
                        raise TimeoutError("pre-encoded encoder did not start")
                    await asyncio.sleep(0.04)
                    origin_clock = time.monotonic_ns() // 1000
                    continue
                started = True
            if not warned_feedback and (feedback.keyframe_requested or feedback.rate_control):
                logger.warning(
                    "Encoder feedback received: %s; this demux-only example cannot "
                    "change the upstream encoder. Use short GOPs and a suitable bitrate.",
                    feedback,
                )
                warned_feedback = True
            frame = await read_next(frames)
        # There is no encoded-video drain acknowledgement. Keep the track alive
        # until cancellation rather than guessing when the final frame arrived.
        logger.info("WebM ended; press Ctrl-C to unpublish and disconnect")
        await asyncio.Event().wait()
    finally:
        try:
            if publication is not None:
                await room.local_participant.unpublish_track(publication.sid)
        finally:
            await source.aclose()


async def main(args: argparse.Namespace) -> None:
    # Open before connecting; URL open/read timeouts prevent an abandoned network
    # source from indefinitely holding a worker during shutdown.
    with av.open(
        args.input,
        format="webm",
        timeout=(5.0, 5.0),
        buffer_size=4096,
        options={"probesize": "4096", "analyzeduration": "0"},
    ) as container:
        frames = demux(container, experimental_alpha=args.experimental_alpha)
        room = rtc.Room()
        token = (
            api.AccessToken()
            .with_identity("webm-publisher")
            .with_grants(api.VideoGrants(room_join=True, room=args.room))
            .to_jwt()
        )
        try:
            await room.connect(os.environ["LIVEKIT_URL"], token)
            await publish(
                room,
                frames,
                name="experimental-webm-alpha-v1" if args.experimental_alpha else "webm",
            )
        finally:
            await room.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="WebM file or streaming HTTP(S) URL")
    parser.add_argument("--room", default="preencoded-webm")
    parser.add_argument(
        "--experimental-alpha",
        action="store_true",
        help="use the unnegotiated alpha prototype; matching test receivers only",
    )
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(parser.parse_args()))
