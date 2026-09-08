"""Publish desktop or microphone audio from PocketStation to LiveKit."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from typing import Protocol

import numpy as np
import pocketstation as pks
import pocketstation.aio as pks_aio
from livekit import api, rtc

SAMPLE_RATE_HZ = 48_000
CHANNEL_COUNT = 1
FRAME_DURATION_MS = 10
LIVEKIT_QUEUE_MS = 100
LOGGER = logging.getLogger(__name__)


class SessionState(Protocol):
    @property
    def is_stopped(self) -> bool: ...


class LiveKitConnector(pks_aio.Connector):
    """Publish PocketStation frames through one LiveKit AudioSource."""

    def __init__(self, source: rtc.AudioSource) -> None:
        self.source = source
        self.frames_sent = 0
        self.closed = False

    async def send(self, frame: pks.AudioFrame) -> None:
        try:
            await self.source.capture_frame(to_livekit_frame(frame))
        except Exception:
            LOGGER.exception(
                "LiveKit rejected a %d Hz, %d-channel audio frame",
                frame.sample_rate_hz,
                frame.channel_count,
            )
            raise
        self.frames_sent += 1

    async def stop(self) -> None:
        if self.closed:
            return
        await self.source.wait_for_playout()
        await self.source.aclose()
        self.closed = True


def to_livekit_frame(frame: pks.AudioFrame) -> rtc.AudioFrame:
    """Downmix one PocketStation float32 frame to mono PCM16."""
    channels = np.asarray(frame.samples, dtype=np.float32).reshape((-1, frame.channel_count))
    mono = np.mean(channels, axis=1, dtype=np.float32)
    pcm = np.rint(np.clip(mono, -1.0, 1.0) * 32_767).astype("<i2")
    return rtc.AudioFrame(
        data=pcm.tobytes(),
        sample_rate=frame.sample_rate_hz,
        num_channels=CHANNEL_COUNT,
        samples_per_channel=frame.sample_count // frame.channel_count,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish one local audio source to a LiveKit room")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--application", help="Running application name or identifier")
    source.add_argument(
        "--system-audio",
        action="store_true",
        help="Capture the complete desktop output mix",
    )
    source.add_argument(
        "--microphone",
        action="store_true",
        help="Capture the default microphone without voice processing",
    )
    parser.add_argument("--room", default="desktop-audio", help="LiveKit room name")
    parser.add_argument(
        "--duration",
        type=float,
        default=0.0,
        help="Stop after this many seconds; zero runs until interrupted",
    )
    args = parser.parse_args()
    if args.duration < 0:
        parser.error("--duration must be zero or greater")
    return args


def selected_source(
    args: argparse.Namespace,
) -> tuple[pks.Source, str, rtc.TrackSource.ValueType]:
    if args.application is not None:
        selected = (
            pks.Source.application_process_id(int(args.application))
            if args.application.isdecimal()
            else pks.Source.application(args.application)
        )
        return (
            selected,
            "application-audio",
            rtc.TrackSource.SOURCE_SCREENSHARE_AUDIO,
        )
    if args.system_audio:
        return (
            pks.Source.system_audio(),
            "system-audio",
            rtc.TrackSource.SOURCE_SCREENSHARE_AUDIO,
        )
    return (
        pks.Source.microphone_default(),
        "microphone",
        rtc.TrackSource.SOURCE_MICROPHONE,
    )


def livekit_credentials() -> tuple[str, str, str]:
    names = ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")
    values = tuple(os.getenv(name) for name in names)
    missing = [name for name, value in zip(names, values, strict=True) if not value]
    if missing:
        raise RuntimeError(f"Set {', '.join(missing)} before running this example")
    return (
        os.environ["LIVEKIT_URL"],
        os.environ["LIVEKIT_API_KEY"],
        os.environ["LIVEKIT_API_SECRET"],
    )


async def wait_until_done(
    disconnected: asyncio.Event,
    running: SessionState,
    *,
    duration: float,
) -> None:
    """Return when the room disconnects, capture stops, or time expires."""

    async def wait_for_session() -> None:
        while not running.is_stopped:
            await asyncio.sleep(0.05)

    room_wait = asyncio.create_task(disconnected.wait())
    session_wait = asyncio.create_task(wait_for_session())
    try:
        await asyncio.wait(
            {room_wait, session_wait},
            timeout=duration or None,
            return_when=asyncio.FIRST_COMPLETED,
        )
    finally:
        for task in (room_wait, session_wait):
            if not task.done():
                task.cancel()
        await asyncio.gather(room_wait, session_wait, return_exceptions=True)


async def run(args: argparse.Namespace) -> None:
    url, api_key, api_secret = livekit_credentials()
    source, track_name, track_source = selected_source(args)

    room = rtc.Room()
    livekit_source = rtc.AudioSource(
        SAMPLE_RATE_HZ,
        CHANNEL_COUNT,
        queue_size_ms=LIVEKIT_QUEUE_MS,
    )
    connector = LiveKitConnector(livekit_source)
    disconnected = asyncio.Event()

    @room.on("disconnected")
    def on_disconnected(*_: object) -> None:
        disconnected.set()

    session = pks_aio.Session(
        sample_rate_hz=SAMPLE_RATE_HZ,
        channels=CHANNEL_COUNT,
        frame_duration_ms=FRAME_DURATION_MS,
    )
    session.capture(source).send_to(connector)

    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity("pocketstation-publisher")
        .with_name("PocketStation Publisher")
        .with_grants(api.VideoGrants(room_join=True, room=args.room))
        .to_jwt()
    )

    try:
        await room.connect(url, token)
        track = rtc.LocalAudioTrack.create_audio_track(track_name, livekit_source)
        options = rtc.TrackPublishOptions()
        options.source = track_source
        publication = await room.local_participant.publish_track(track, options)
        LOGGER.info("published %s as track %s", track_name, publication.sid)

        running = await session.start()
        async with running:
            await wait_until_done(disconnected, running, duration=args.duration)
        result = running.stop_result
        if result is None or not result.success:
            raise RuntimeError("PocketStation stopped after a capture or delivery failure")
    finally:
        if not connector.closed:
            await connector.stop()
        await room.disconnect()
        LOGGER.info("published %d audio frames", connector.frames_sent)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
