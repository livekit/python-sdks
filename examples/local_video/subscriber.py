import argparse
import asyncio
import logging
import os
import signal
import time
from datetime import datetime, timezone
from typing import Optional

import numpy as np
from livekit import api, rtc

try:
    import cv2
except ImportError as exc:  # pragma: no cover - example dependency
    raise RuntimeError(
        "opencv-python is required to run this example, install with `pip install opencv-python`"
    ) from exc


logger = logging.getLogger(__name__)
WINDOW_NAME = "livekit_local_video"


def unix_time_us_now() -> int:
    return time.time_ns() // 1_000


def format_timestamp_us(timestamp_us: int) -> str:
    dt = datetime.fromtimestamp(timestamp_us / 1_000_000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"


def packet_trailer_feature_names(features: list[int]) -> str:
    if not features:
        return "none"
    names: list[str] = []
    for feature in features:
        try:
            names.append(rtc.PacketTrailerFeature.Name(feature))
        except ValueError:
            names.append(str(feature))
    return ", ".join(names)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Subscribe to local camera video from LiveKit")
    parser.add_argument(
        "--identity",
        default="python-video-subscriber",
        help="LiveKit participant identity",
    )
    parser.add_argument("--room-name", default="video-room", help="LiveKit room name")
    parser.add_argument("--url", default=None, help="LiveKit server URL")
    parser.add_argument("--api-key", default=None, help="LiveKit API key")
    parser.add_argument("--api-secret", default=None, help="LiveKit API secret")
    parser.add_argument(
        "--participant",
        default=None,
        help="Only subscribe to video from this participant identity",
    )
    parser.add_argument(
        "--display-timestamp",
        action="store_true",
        help="Overlay user timestamp, receive timestamp, frame ID, and latency",
    )
    parser.add_argument(
        "--e2ee-key",
        default=None,
        help="Shared encryption key for AES-GCM end-to-end encryption",
    )
    return parser


def env_or_arg(value: Optional[str], env_name: str) -> str:
    resolved = value or os.getenv(env_name)
    if not resolved:
        raise RuntimeError(f"{env_name} must be provided via --{env_name.lower().replace('_', '-')} or env")
    return resolved


def build_token(args: argparse.Namespace) -> str:
    api_key = env_or_arg(args.api_key, "LIVEKIT_API_KEY")
    api_secret = env_or_arg(args.api_secret, "LIVEKIT_API_SECRET")
    return (
        api.AccessToken(api_key, api_secret)
        .with_identity(args.identity)
        .with_name(args.identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=args.room_name,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )


def build_room_options(e2ee_key: Optional[str]) -> rtc.RoomOptions:
    encryption = None
    if e2ee_key:
        encryption = rtc.E2EEOptions()
        encryption.key_provider_options.shared_key = e2ee_key.encode("utf-8")

    return rtc.RoomOptions(
        auto_subscribe=True,
        dynacast=True,
        encryption=encryption,
    )


def install_signal_handlers(shutdown: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()

    def request_shutdown() -> None:
        if not shutdown.is_set():
            logger.info("Shutdown requested, stopping subscriber...")
            shutdown.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_shutdown)
        except NotImplementedError:  # pragma: no cover - platform-specific fallback
            signal.signal(sig, lambda *_: request_shutdown())


def draw_overlay(frame_bgr: np.ndarray, lines: list[str]) -> None:
    if not lines:
        return

    x = 16
    y = 28
    line_height = 24
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    thickness = 2

    for line in lines:
        cv2.putText(frame_bgr, line, (x, y), font, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(frame_bgr, line, (x, y), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)
        y += line_height


class LocalVideoSubscriber:
    def __init__(self, args: argparse.Namespace, room: rtc.Room, shutdown: asyncio.Event) -> None:
        self.args = args
        self.room = room
        self.shutdown = shutdown
        self.active_sid: Optional[str] = None
        self.active_task: Optional[asyncio.Task[None]] = None

    def matches_participant(self, participant: rtc.RemoteParticipant) -> bool:
        if self.args.participant is None:
            return True
        return participant.identity == self.args.participant

    def attach_handlers(self) -> None:
        @self.room.on("track_published")
        def on_track_published(
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant,
        ) -> None:
            if publication.kind != rtc.TrackKind.KIND_VIDEO:
                return

            logger.info(
                "Track published: sid=%s participant=%s codec=%s simulcast=%s size=%dx%d packet_trailer_features=%s",
                publication.sid,
                participant.identity,
                publication.mime_type,
                publication.simulcasted,
                publication.width,
                publication.height,
                packet_trailer_feature_names(publication.packet_trailer_features),
            )

            if not self.matches_participant(participant):
                publication.set_subscribed(False)

        @self.room.on("track_subscribed")
        def on_track_subscribed(
            track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant,
        ) -> None:
            if track.kind != rtc.TrackKind.KIND_VIDEO:
                return

            if not self.matches_participant(participant):
                publication.set_subscribed(False)
                return

            if self.active_task is not None and not self.active_task.done():
                logger.info(
                    "Ignoring subscribed video track %s from %s because track %s is already active",
                    publication.sid,
                    participant.identity,
                    self.active_sid,
                )
                publication.set_subscribed(False)
                return

            self.active_sid = publication.sid
            self.active_task = asyncio.create_task(
                self.consume_video_track(track, publication, participant)
            )

        @self.room.on("track_unsubscribed")
        def on_track_unsubscribed(
            _track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            _participant: rtc.RemoteParticipant,
        ) -> None:
            self.stop_active_track(publication.sid, "Track unsubscribed")

        @self.room.on("track_unpublished")
        def on_track_unpublished(
            publication: rtc.RemoteTrackPublication,
            _participant: rtc.RemoteParticipant,
        ) -> None:
            self.stop_active_track(publication.sid, "Track unpublished")

    def stop_active_track(self, sid: str, reason: str) -> None:
        if self.active_sid != sid:
            return
        logger.info("%s: %s", reason, sid)
        if self.active_task is not None and not self.active_task.done():
            self.active_task.cancel()

    def clear_active_track(self, sid: str) -> None:
        if self.active_sid == sid:
            self.active_sid = None
            self.active_task = None

    async def aclose(self) -> None:
        if self.active_task is not None and not self.active_task.done():
            self.active_task.cancel()
            try:
                await self.active_task
            except asyncio.CancelledError:
                pass

    async def consume_video_track(
        self,
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        logger.info(
            "Subscribed to video track: sid=%s participant=%s codec=%s simulcast=%s size=%dx%d packet_trailer_features=%s",
            publication.sid,
            participant.identity,
            publication.mime_type,
            publication.simulcasted,
            publication.width,
            publication.height,
            packet_trailer_feature_names(publication.packet_trailer_features),
        )

        stream = rtc.VideoStream(track, format=rtc.VideoBufferType.RGB24)
        fps = 0.0
        fps_frames = 0
        fps_window_started_at = time.perf_counter()

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
        cv2.startWindowThread()

        try:
            async for frame_event in stream:
                if self.shutdown.is_set():
                    break

                buffer = frame_event.frame
                image_rgb = np.frombuffer(buffer.data, dtype=np.uint8).reshape(
                    (buffer.height, buffer.width, 3)
                )
                image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                fps_frames += 1
                elapsed = time.perf_counter() - fps_window_started_at
                if elapsed >= 0.5:
                    fps = fps_frames / elapsed
                    fps_frames = 0
                    fps_window_started_at = time.perf_counter()

                overlay_lines = [
                    f"{publication.mime_type} {buffer.width}x{buffer.height} {fps:.1f}fps",
                    f"Participant: {participant.identity}",
                    f"Packet trailer: {packet_trailer_feature_names(publication.packet_trailer_features)}",
                ]

                if self.args.display_timestamp:
                    publish_us = frame_event.user_timestamp_us
                    frame_id = frame_event.frame_id
                    receive_us = unix_time_us_now()
                    if frame_id is not None or publish_us is not None:
                        overlay_lines.append(
                            f"Frame ID: {frame_id if frame_id is not None else 'N/A'}"
                        )
                    if publish_us is not None:
                        overlay_lines.append(f"Publish: {format_timestamp_us(publish_us)}")
                        overlay_lines.append(f"Receive: {format_timestamp_us(receive_us)}")
                        overlay_lines.append(
                            f"Latency: {(receive_us - publish_us) / 1000.0:.1f}ms"
                        )

                draw_overlay(image_bgr, overlay_lines)
                cv2.imshow(WINDOW_NAME, image_bgr)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Quit requested from subscriber window")
                    self.shutdown.set()
                    break
        except asyncio.CancelledError:
            logger.debug("Video consumer cancelled for sid=%s", publication.sid)
        finally:
            await stream.aclose()
            try:
                cv2.destroyWindow(WINDOW_NAME)
            except cv2.error:
                pass
            self.clear_active_track(publication.sid)


async def run(args: argparse.Namespace) -> None:
    url = env_or_arg(args.url, "LIVEKIT_URL")
    token = build_token(args)
    shutdown = asyncio.Event()
    install_signal_handlers(shutdown)

    room = rtc.Room(loop=asyncio.get_running_loop())
    subscriber = LocalVideoSubscriber(args, room, shutdown)
    subscriber.attach_handlers()

    logger.info("Connecting to room '%s' as '%s'...", args.room_name, args.identity)
    await room.connect(url, token, options=build_room_options(args.e2ee_key))
    logger.info("Connected to room %s", room.name)

    if args.e2ee_key:
        room.e2ee_manager.set_enabled(True)
        logger.info("End-to-end encryption activated")

    try:
        await shutdown.wait()
    finally:
        await subscriber.aclose()
        await room.disconnect()
        cv2.destroyAllWindows()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
