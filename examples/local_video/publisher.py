from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import time

import numpy as np
from livekit import api, rtc

try:
    import cv2
except ImportError as exc:
    raise SystemExit(
        "opencv-python is required to run this example. "
        "Run it with `uv run --project examples/local_video python examples/local_video/publisher.py`."
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish a local camera track with optional frame metadata.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--camera-index", type=int, default=0, help="OpenCV camera index to use")
    parser.add_argument("--width", type=int, default=1280, help="Requested capture width")
    parser.add_argument("--height", type=int, default=720, help="Requested capture height")
    parser.add_argument("--fps", type=float, default=30.0, help="Requested publish frame rate")
    parser.add_argument("--room-name", default="video-room", help="LiveKit room name")
    parser.add_argument("--identity", default="python-camera-pub", help="Participant identity")
    parser.add_argument("--url", help="LiveKit server URL; falls back to LIVEKIT_URL")
    parser.add_argument("--api-key", help="LiveKit API key; falls back to LIVEKIT_API_KEY")
    parser.add_argument(
        "--api-secret",
        help="LiveKit API secret; falls back to LIVEKIT_API_SECRET",
    )
    parser.add_argument(
        "--attach-timestamp",
        action="store_true",
        help="Attach wall-clock microseconds in FrameMetadata.user_timestamp",
    )
    parser.add_argument(
        "--attach-frame-id",
        action="store_true",
        help="Attach a monotonically increasing FrameMetadata.frame_id",
    )
    return parser.parse_args()


def _require_connection(args: argparse.Namespace) -> tuple[str, str, str]:
    url = args.url or os.getenv("LIVEKIT_URL")
    api_key = args.api_key or os.getenv("LIVEKIT_API_KEY")
    api_secret = args.api_secret or os.getenv("LIVEKIT_API_SECRET")

    missing = [
        name
        for name, value in (
            ("LIVEKIT_URL or --url", url),
            ("LIVEKIT_API_KEY or --api-key", api_key),
            ("LIVEKIT_API_SECRET or --api-secret", api_secret),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing LiveKit connection settings: {', '.join(missing)}")

    return url, api_key, api_secret


def _create_token(args: argparse.Namespace, api_key: str, api_secret: str) -> str:
    return (
        api.AccessToken(api_key, api_secret)
        .with_identity(args.identity)
        .with_name(args.identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=args.room_name,
                can_publish=True,
                can_subscribe=False,
            )
        )
        .to_jwt()
    )


def _open_camera(args: argparse.Namespace) -> tuple[cv2.VideoCapture, int, int]:
    if args.fps <= 0:
        raise RuntimeError("--fps must be greater than zero")

    capture = cv2.VideoCapture(args.camera_index)
    if not capture.isOpened():
        raise RuntimeError(f"Could not open camera index {args.camera_index}")

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    capture.set(cv2.CAP_PROP_FPS, args.fps)

    ok, frame = capture.read()
    if not ok or frame is None:
        capture.release()
        raise RuntimeError(f"Could not read from camera index {args.camera_index}")

    height, width = frame.shape[:2]
    logging.info("camera opened at %sx%s", width, height)
    return capture, width, height


def _frame_metadata_features(args: argparse.Namespace) -> list[int]:
    features = []
    if args.attach_timestamp:
        features.append(rtc.FrameMetadataFeature.FMF_USER_TIMESTAMP)
    if args.attach_frame_id:
        features.append(rtc.FrameMetadataFeature.FMF_FRAME_ID)
    return features


def _metadata_for_frame(
    args: argparse.Namespace,
    *,
    user_timestamp: int,
    frame_id: int,
) -> rtc.FrameMetadata | None:
    if not args.attach_timestamp and not args.attach_frame_id:
        return None

    metadata = rtc.FrameMetadata()
    if args.attach_timestamp:
        metadata.user_timestamp = user_timestamp
    if args.attach_frame_id:
        metadata.frame_id = frame_id
    return metadata


def _unix_time_us() -> int:
    return time.time_ns() // 1_000


def _install_signal_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except (NotImplementedError, RuntimeError):
            pass


async def _capture_loop(
    args: argparse.Namespace,
    capture: cv2.VideoCapture,
    source: rtc.VideoSource,
    width: int,
    height: int,
    stop_event: asyncio.Event,
) -> None:
    interval = 1.0 / args.fps
    next_frame_at = time.perf_counter()
    started_at_ns = time.perf_counter_ns()
    frame_id = 1
    submitted = 0
    last_log_at = time.perf_counter()

    while not stop_event.is_set():
        ok, bgr = await asyncio.to_thread(capture.read)
        if not ok or bgr is None:
            logging.warning("camera frame read failed")
            await asyncio.sleep(0.1)
            continue

        if bgr.shape[1] != width or bgr.shape[0] != height:
            bgr = cv2.resize(bgr, (width, height), interpolation=cv2.INTER_AREA)

        user_timestamp = _unix_time_us()
        timestamp_us = (time.perf_counter_ns() - started_at_ns) // 1_000
        rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA)
        rgba = np.ascontiguousarray(rgba)
        frame = rtc.VideoFrame(width, height, rtc.VideoBufferType.RGBA, rgba.tobytes())
        metadata = _metadata_for_frame(
            args,
            user_timestamp=user_timestamp,
            frame_id=frame_id,
        )
        source.capture_frame(frame, timestamp_us=timestamp_us, metadata=metadata)

        submitted += 1
        if args.attach_frame_id:
            frame_id = (frame_id + 1) & 0xFFFFFFFF

        now = time.perf_counter()
        if now - last_log_at >= 2.0:
            logging.info(
                "published %s frames at ~%.1f fps", submitted, submitted / (now - last_log_at)
            )
            submitted = 0
            last_log_at = now

        next_frame_at += interval
        sleep_for = next_frame_at - time.perf_counter()
        if sleep_for > 0:
            await asyncio.sleep(sleep_for)
        else:
            next_frame_at = time.perf_counter()


async def run(args: argparse.Namespace, stop_event: asyncio.Event) -> None:
    url, api_key, api_secret = _require_connection(args)
    capture, width, height = _open_camera(args)
    room = rtc.Room()
    source: rtc.VideoSource | None = None

    try:
        token = _create_token(args, api_key, api_secret)
        logging.info("connecting to room %s as %s", args.room_name, args.identity)
        await room.connect(url, token)
        logging.info("connected to room %s", room.name)

        source = rtc.VideoSource(width, height)
        track = rtc.LocalVideoTrack.create_video_track("camera", source)
        options = rtc.TrackPublishOptions(
            source=rtc.TrackSource.SOURCE_CAMERA,
            video_encoding=rtc.VideoEncoding(
                max_framerate=args.fps,
                max_bitrate=3_000_000,
            ),
            frame_metadata_features=_frame_metadata_features(args),
        )
        publication = await room.local_participant.publish_track(track, options)
        logging.info(
            "published camera track %s with frame metadata features %s",
            publication.sid,
            list(publication.frame_metadata_features),
        )

        await _capture_loop(args, capture, source, width, height, stop_event)
    finally:
        capture.release()
        if source is not None:
            await source.aclose()
        await room.disconnect()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    stop_event = asyncio.Event()
    _install_signal_handlers(stop_event)
    await run(args, stop_event)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
