from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
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
        "Run it with `uv run --project examples/local_video python examples/local_video/subscriber.py`."
    ) from exc


WINDOW_NAME = "livekit_video"


@dataclass(frozen=True)
class SubscribedVideoTrack:
    track: rtc.Track
    publication: rtc.RemoteTrackPublication
    participant: rtc.RemoteParticipant


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Subscribe to a LiveKit video track and optionally display packet metadata.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--room-name", default="video-room", help="LiveKit room name")
    parser.add_argument(
        "--identity", default="python-video-subscriber", help="Participant identity"
    )
    parser.add_argument(
        "--participant",
        help="Only subscribe to video from this participant identity",
    )
    parser.add_argument("--url", help="LiveKit server URL; falls back to LIVEKIT_URL")
    parser.add_argument("--api-key", help="LiveKit API key; falls back to LIVEKIT_API_KEY")
    parser.add_argument(
        "--api-secret",
        help="LiveKit API secret; falls back to LIVEKIT_API_SECRET",
    )
    parser.add_argument(
        "--display-timestamp",
        action="store_true",
        help="Overlay frame ID, publisher timestamp, receive timestamp, and latency",
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
                can_publish=False,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )


def _unix_time_us() -> int:
    return time.time_ns() // 1_000


def _install_signal_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except (NotImplementedError, RuntimeError):
            pass


def _metadata_field(metadata: rtc.FrameMetadata | None, field: str) -> int | None:
    if metadata is None:
        return None
    if not metadata.HasField(field):
        return None
    return getattr(metadata, field)


def _format_timestamp_us(timestamp_us: int | None) -> str:
    if timestamp_us is None:
        return "N/A"
    try:
        timestamp = datetime.fromtimestamp(timestamp_us / 1_000_000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return f"<invalid {timestamp_us}>"
    return f"{timestamp:%Y-%m-%d %H:%M:%S}.{timestamp.microsecond // 1_000:03d}Z"


def _format_latency_us(receive_us: int, publish_us: int | None) -> str:
    if publish_us is None:
        return "N/A"
    return f"{max(receive_us - publish_us, 0) / 1_000:.1f}ms"


def _draw_timestamp_overlay(
    image: np.ndarray,
    *,
    metadata: rtc.FrameMetadata | None,
    receive_us: int,
) -> None:
    publish_us = _metadata_field(metadata, "user_timestamp")
    frame_id = _metadata_field(metadata, "frame_id")
    lines = [
        f"Frame ID:    {frame_id if frame_id is not None else 'N/A'}",
        f"Sensor:      {_format_timestamp_us(publish_us)}",
        f"Receive:     {_format_timestamp_us(receive_us)}",
        f"E2E Latency: {_format_latency_us(receive_us, publish_us)}",
    ]

    font_face = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 1
    line_height = 22
    padding = 8
    text_sizes = [cv2.getTextSize(line, font_face, font_scale, thickness)[0] for line in lines]
    box_width = max(width for width, _ in text_sizes) + (padding * 2)
    box_height = (line_height * len(lines)) + (padding * 2)
    cv2.rectangle(image, (8, 8), (8 + box_width, 8 + box_height), (0, 0, 0), -1)

    y = 8 + padding + 16
    for line in lines:
        cv2.putText(
            image,
            line,
            (8 + padding, y),
            font_face,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )
        y += line_height


def _feature_names(features: list[int]) -> str:
    names = []
    for feature in features:
        try:
            names.append(rtc.PacketTrailerFeature.Name(feature))
        except ValueError:
            names.append(str(feature))
    return ", ".join(names) or "none"


def _window_is_open() -> bool:
    try:
        return cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) >= 1
    except cv2.error:
        return False


async def _next_video_track(
    track_queue: asyncio.Queue[SubscribedVideoTrack],
    stop_event: asyncio.Event,
) -> SubscribedVideoTrack | None:
    while not stop_event.is_set():
        try:
            return await asyncio.wait_for(track_queue.get(), timeout=0.5)
        except asyncio.TimeoutError:
            continue
    return None


async def _render_video(
    video_stream: rtc.VideoStream,
    args: argparse.Namespace,
    stop_event: asyncio.Event,
    active_track_gone: asyncio.Event,
) -> None:
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

    try:
        while not stop_event.is_set() and not active_track_gone.is_set():
            try:
                frame_event = await asyncio.wait_for(video_stream.__anext__(), timeout=0.5)
            except asyncio.TimeoutError:
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    stop_event.set()
                continue
            except StopAsyncIteration:
                break

            receive_us = _unix_time_us()
            frame = frame_event.frame
            rgb = np.frombuffer(frame.data, dtype=np.uint8).reshape((frame.height, frame.width, 3))
            image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            if args.display_timestamp:
                _draw_timestamp_overlay(
                    image,
                    metadata=frame_event.metadata,
                    receive_us=receive_us,
                )

            cv2.imshow(WINDOW_NAME, image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                stop_event.set()
            if not _window_is_open():
                stop_event.set()
    finally:
        cv2.destroyAllWindows()


async def run(args: argparse.Namespace, stop_event: asyncio.Event) -> None:
    url, api_key, api_secret = _require_connection(args)
    room = rtc.Room()
    track_queue: asyncio.Queue[SubscribedVideoTrack] = asyncio.Queue()
    active_publication_sid: str | None = None
    active_track_gone = asyncio.Event()
    video_stream: rtc.VideoStream | None = None

    @room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        if track.kind != rtc.TrackKind.KIND_VIDEO:
            return
        if args.participant and participant.identity != args.participant:
            logging.info(
                "skipping video track from %s; waiting for %s",
                participant.identity,
                args.participant,
            )
            return

        track_queue.put_nowait(
            SubscribedVideoTrack(
                track=track,
                publication=publication,
                participant=participant,
            )
        )

    @room.on("track_unsubscribed")
    def on_track_unsubscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        nonlocal active_publication_sid
        if publication.sid == active_publication_sid:
            logging.info("active video track unsubscribed: %s", publication.sid)
            active_track_gone.set()

    @room.on("track_unpublished")
    def on_track_unpublished(
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        nonlocal active_publication_sid
        if publication.sid == active_publication_sid:
            logging.info("active video track unpublished: %s", publication.sid)
            active_track_gone.set()

    try:
        token = _create_token(args, api_key, api_secret)
        logging.info("connecting to room %s as %s", args.room_name, args.identity)
        await room.connect(url, token)
        logging.info("connected to room %s", room.name)

        while not stop_event.is_set():
            logging.info("waiting for a video track")
            subscribed = await _next_video_track(track_queue, stop_event)
            if subscribed is None:
                break

            active_publication_sid = subscribed.publication.sid
            active_track_gone = asyncio.Event()
            logging.info(
                "subscribed to %s from %s with packet trailer features: %s",
                subscribed.publication.sid,
                subscribed.participant.identity,
                _feature_names(list(subscribed.publication.packet_trailer_features)),
            )

            video_stream = rtc.VideoStream.from_track(
                track=subscribed.track,
                format=rtc.VideoBufferType.RGB24,
                capacity=1,
            )
            try:
                await _render_video(video_stream, args, stop_event, active_track_gone)
            finally:
                await video_stream.aclose()
                video_stream = None
                active_publication_sid = None
    finally:
        if video_stream is not None:
            await video_stream.aclose()
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
