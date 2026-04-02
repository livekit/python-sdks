import argparse
import asyncio
import logging
import os
import signal
import time
from dataclasses import dataclass, field
from typing import Optional

from livekit import api, rtc

try:
    import cv2
except ImportError as exc:  # pragma: no cover - example dependency
    raise RuntimeError(
        "opencv-python is required to run this example, install with `pip install opencv-python`"
    ) from exc


logger = logging.getLogger(__name__)


def unix_time_us_now() -> int:
    return time.time_ns() // 1_000


def monotonic_time_us_now() -> int:
    return time.perf_counter_ns() // 1_000


@dataclass
class RollingMs:
    total_ms: float = 0.0
    samples: int = 0

    def record(self, value_ms: float) -> None:
        self.total_ms += value_ms
        self.samples += 1

    def average(self) -> float:
        if self.samples == 0:
            return 0.0
        return self.total_ms / self.samples

    def reset(self) -> None:
        self.total_ms = 0.0
        self.samples = 0


@dataclass
class PublisherTimingSummary:
    paced_wait_ms: RollingMs = field(default_factory=RollingMs)
    camera_frame_read_ms: RollingMs = field(default_factory=RollingMs)
    frame_draw_ms: RollingMs = field(default_factory=RollingMs)
    frame_convert_ms: RollingMs = field(default_factory=RollingMs)
    submit_to_webrtc_ms: RollingMs = field(default_factory=RollingMs)
    capture_to_webrtc_total_ms: RollingMs = field(default_factory=RollingMs)

    def reset(self) -> None:
        self.paced_wait_ms.reset()
        self.camera_frame_read_ms.reset()
        self.frame_draw_ms.reset()
        self.frame_convert_ms.reset()
        self.submit_to_webrtc_ms.reset()
        self.capture_to_webrtc_total_ms.reset()


def format_timing_line(timings: PublisherTimingSummary) -> str:
    return (
        "Timing ms: "
        f"paced_wait {timings.paced_wait_ms.average():.2f} | "
        f"camera_frame_read {timings.camera_frame_read_ms.average():.2f} | "
        f"frame_draw {timings.frame_draw_ms.average():.2f} | "
        f"convert_to_rgba {timings.frame_convert_ms.average():.2f} | "
        f"submit_to_webrtc {timings.submit_to_webrtc_ms.average():.2f} | "
        f"capture_to_webrtc_total {timings.capture_to_webrtc_total_ms.average():.2f}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish local camera video to LiveKit")
    parser.add_argument("--list-cameras", action="store_true", help="List available cameras and exit")
    parser.add_argument("--camera-index", type=int, default=0, help="Camera index to use")
    parser.add_argument("--width", type=int, default=1280, help="Desired capture width")
    parser.add_argument("--height", type=int, default=720, help="Desired capture height")
    parser.add_argument("--fps", type=int, default=30, help="Desired capture frame rate")
    parser.add_argument(
        "--max-bitrate",
        type=int,
        default=None,
        help="Max main-layer bitrate in bps",
    )
    parser.add_argument("--simulcast", action="store_true", help="Enable simulcast publishing")
    parser.add_argument(
        "--identity",
        default="python-camera-pub",
        help="LiveKit participant identity",
    )
    parser.add_argument("--room-name", default="video-room", help="LiveKit room name")
    parser.add_argument("--url", default=None, help="LiveKit server URL")
    parser.add_argument("--api-key", default=None, help="LiveKit API key")
    parser.add_argument("--api-secret", default=None, help="LiveKit API secret")
    parser.add_argument(
        "--h265",
        action="store_true",
        help="Attempt H.265 publishing and fall back to H.264 if it fails",
    )
    parser.add_argument(
        "--attach-timestamp",
        action="store_true",
        help="Attach system time as frame metadata user_timestamp_us",
    )
    parser.add_argument(
        "--burn-timestamp",
        action="store_true",
        help="Burn the attached timestamp into the video frame",
    )
    parser.add_argument(
        "--attach-frame-id",
        action="store_true",
        help="Attach a monotonically increasing frame_id to each frame",
    )
    parser.add_argument(
        "--e2ee-key",
        default=None,
        help="Shared encryption key for AES-GCM end-to-end encryption",
    )
    parser.add_argument(
        "--max-camera-index",
        type=int,
        default=10,
        help="Highest camera index to probe when listing cameras",
    )
    return parser


def list_cameras(max_camera_index: int) -> None:
    print("Available cameras:")
    found_any = False
    for index in range(max_camera_index + 1):
        cap = cv2.VideoCapture(index)
        try:
            if not cap.isOpened():
                continue

            found_any = True
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            backend = ""
            if hasattr(cap, "getBackendName"):
                try:
                    backend = cap.getBackendName()
                except Exception:
                    backend = ""

            suffix = f" ({backend})" if backend else ""
            print(f"{index}: {width}x{height} @ {fps:.1f} fps{suffix}")
        finally:
            cap.release()

    if not found_any:
        print("No cameras detected.")


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
                can_publish=True,
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


def build_publish_options(args: argparse.Namespace, codec: rtc.VideoCodec.ValueType) -> rtc.TrackPublishOptions:
    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_CAMERA
    options.simulcast = args.simulcast
    options.video_codec = codec
    options.video_encoding.max_framerate = float(args.fps)
    if args.max_bitrate is not None:
        options.video_encoding.max_bitrate = args.max_bitrate

    if args.attach_timestamp:
        options.packet_trailer_features.append(rtc.PTF_USER_TIMESTAMP)
    if args.attach_frame_id:
        options.packet_trailer_features.append(rtc.PTF_FRAME_ID)

    return options


def install_signal_handlers(shutdown: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()

    def request_shutdown() -> None:
        if not shutdown.is_set():
            logger.info("Shutdown requested, stopping publisher...")
            shutdown.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_shutdown)
        except NotImplementedError:  # pragma: no cover - platform-specific fallback
            signal.signal(sig, lambda *_: request_shutdown())


def open_camera(args: argparse.Namespace) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(args.camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open camera index {args.camera_index}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(args.width))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(args.height))
    cap.set(cv2.CAP_PROP_FPS, float(args.fps))
    return cap


async def publish_track_with_fallback(
    room: rtc.Room,
    track: rtc.LocalVideoTrack,
    args: argparse.Namespace,
) -> rtc.LocalTrackPublication:
    requested_codec = rtc.VideoCodec.H265 if args.h265 else rtc.VideoCodec.H264
    requested_name = rtc.VideoCodec.Name(requested_codec)
    logger.info("Attempting publish with codec %s", requested_name)

    try:
        publication = await room.local_participant.publish_track(
            track,
            build_publish_options(args, requested_codec),
        )
        logger.info("Published camera track with %s", requested_name)
        return publication
    except Exception as exc:
        if requested_codec != rtc.VideoCodec.H265:
            raise

        logger.warning("H.265 publish failed (%s). Falling back to H.264...", exc)
        publication = await room.local_participant.publish_track(
            track,
            build_publish_options(args, rtc.VideoCodec.H264),
        )
        logger.info("Published camera track with H.264 fallback")
        return publication


def burn_timestamp(frame_bgr, timestamp_us: int) -> None:
    text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_us / 1_000_000))
    text = f"{text}.{(timestamp_us // 1_000) % 1000:03d}"
    (_, text_height), baseline = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        2,
    )
    cv2.putText(
        frame_bgr,
        text,
        (20, frame_bgr.shape[0] - baseline - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


async def capture_loop(
    args: argparse.Namespace,
    cap: cv2.VideoCapture,
    source: rtc.VideoSource,
    shutdown: asyncio.Event,
) -> None:
    target_interval = 1.0 / max(args.fps, 1)
    next_deadline = time.perf_counter()
    started_us = monotonic_time_us_now()
    frame_counter = 1
    frames = 0
    last_log_at = time.perf_counter()
    timings = PublisherTimingSummary()

    while not shutdown.is_set():
        paced_wait_started_at = time.perf_counter()
        delay = next_deadline - paced_wait_started_at
        if delay > 0:
            await asyncio.sleep(delay)
        paced_wait_finished_at = time.perf_counter()
        next_deadline += target_interval

        camera_capture_started_at = time.perf_counter()
        ok, frame_bgr = await asyncio.to_thread(cap.read)
        camera_frame_acquired_at = time.perf_counter()
        if not ok or frame_bgr is None:
            logger.warning("Camera read failed, retrying...")
            await asyncio.sleep(0.05)
            continue

        capture_wall_time_us = unix_time_us_now()

        frame_draw_started_at = time.perf_counter()
        if args.attach_timestamp and args.burn_timestamp:
            burn_timestamp(frame_bgr, capture_wall_time_us)
        frame_draw_finished_at = time.perf_counter()

        frame_convert_started_at = time.perf_counter()
        frame_rgba = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGBA)
        frame_convert_finished_at = time.perf_counter()

        video_frame = rtc.VideoFrame(
            width=frame_rgba.shape[1],
            height=frame_rgba.shape[0],
            type=rtc.VideoBufferType.RGBA,
            data=frame_rgba.tobytes(),
        )

        user_timestamp_us = capture_wall_time_us if args.attach_timestamp else None
        frame_id = frame_counter if args.attach_frame_id else None
        if args.attach_frame_id:
            frame_counter = (frame_counter + 1) & 0xFFFFFFFF

        frame_metadata = None
        if user_timestamp_us is not None or frame_id is not None:
            frame_metadata = rtc.FrameMetadata(
                user_timestamp_us=user_timestamp_us,
                frame_id=frame_id,
            )

        submit_to_webrtc_started_at = time.perf_counter()
        source.capture_frame(
            video_frame,
            timestamp_us=monotonic_time_us_now() - started_us,
            frame_metadata=frame_metadata,
        )
        webrtc_capture_finished_at = time.perf_counter()

        frames += 1
        timings.paced_wait_ms.record((paced_wait_finished_at - paced_wait_started_at) * 1000.0)
        timings.camera_frame_read_ms.record(
            (camera_frame_acquired_at - camera_capture_started_at) * 1000.0
        )
        timings.frame_draw_ms.record((frame_draw_finished_at - frame_draw_started_at) * 1000.0)
        timings.frame_convert_ms.record(
            (frame_convert_finished_at - frame_convert_started_at) * 1000.0
        )
        timings.submit_to_webrtc_ms.record(
            (webrtc_capture_finished_at - submit_to_webrtc_started_at) * 1000.0
        )
        timings.capture_to_webrtc_total_ms.record(
            (webrtc_capture_finished_at - camera_capture_started_at) * 1000.0
        )

        if time.perf_counter() - last_log_at >= 2.0:
            elapsed = time.perf_counter() - last_log_at
            logger.info(
                "Video status: %dx%d | ~%.1f fps | target %.2f ms",
                frame_rgba.shape[1],
                frame_rgba.shape[0],
                frames / elapsed,
                target_interval * 1000.0,
            )
            logger.info("%s", format_timing_line(timings))
            frames = 0
            timings.reset()
            last_log_at = time.perf_counter()


async def run(args: argparse.Namespace) -> None:
    if args.list_cameras:
        list_cameras(args.max_camera_index)
        return

    url = env_or_arg(args.url, "LIVEKIT_URL")
    token = build_token(args)
    shutdown = asyncio.Event()
    install_signal_handlers(shutdown)

    room = rtc.Room(loop=asyncio.get_running_loop())
    room_options = build_room_options(args.e2ee_key)

    logger.info("Connecting to room '%s' as '%s'...", args.room_name, args.identity)
    await room.connect(url, token, options=room_options)
    logger.info("Connected to room %s", room.name)

    if args.e2ee_key:
        room.e2ee_manager.set_enabled(True)
        logger.info("End-to-end encryption activated")

    cap = open_camera(args)
    publication = None
    source = None

    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or args.width
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or args.height
        fps = cap.get(cv2.CAP_PROP_FPS) or float(args.fps)
        logger.info(
            "Camera opened: %dx%d @ %.1f fps (index %d)",
            width,
            height,
            fps,
            args.camera_index,
        )

        source = rtc.VideoSource(width=width, height=height)
        track = rtc.LocalVideoTrack.create_video_track("camera", source)
        publication = await publish_track_with_fallback(room, track, args)
        logger.info("Published track sid=%s", publication.sid)

        while not shutdown.is_set():
            await capture_loop(args, cap, source, shutdown)
    finally:
        shutdown.set()
        cap.release()
        if publication is not None:
            try:
                await room.local_participant.unpublish_track(publication.sid)
            except Exception:
                logger.debug("Track was already unpublished", exc_info=True)
        if source is not None:
            await source.aclose()
        await room.disconnect()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
