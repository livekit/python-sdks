from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import signal
import subprocess
from dataclasses import dataclass
from typing import Awaitable

from dotenv import find_dotenv, load_dotenv
from livekit import api, rtc

SAMPLE_RATE = 48_000
NUM_CHANNELS = 1
OUTPUT_FRAME_SAMPLES = 480  # 10 ms at 48 kHz
DEFAULT_WM8960_DEVICE_NAME = "wm8960"

logger = logging.getLogger("whisplay-client")


@dataclass(frozen=True)
class Config:
    url: str
    api_key: str
    api_secret: str
    room_name: str
    identity: str
    name: str
    audio_input_device: int | None
    audio_output_device: int | None

    @staticmethod
    def from_env() -> "Config":
        url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        if not url or not api_key or not api_secret:
            raise RuntimeError(
                "LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set"
            )

        return Config(
            url=url,
            api_key=api_key,
            api_secret=api_secret,
            room_name=os.getenv("LIVEKIT_ROOM", "wakeword-preconnect"),
            identity=os.getenv("LIVEKIT_IDENTITY", "whisplay-client"),
            name=os.getenv("LIVEKIT_NAME", "Whisplay Client"),
            audio_input_device=Config._optional_int_from_env(
                "LIVEKIT_AUDIO_INPUT_DEVICE"
            ),
            audio_output_device=Config._optional_int_from_env(
                "LIVEKIT_AUDIO_OUTPUT_DEVICE"
            ),
        )

    @staticmethod
    def _optional_int_from_env(name: str) -> int | None:
        raw = os.getenv(name)
        if raw is None or not raw.strip():
            return None

        try:
            return int(raw)
        except ValueError:
            raise RuntimeError(f"{name} must be an integer device index") from None


def _find_wm8960_card() -> int | None:
    try:
        with open("/proc/asound/cards") as cards:
            for line in cards:
                if DEFAULT_WM8960_DEVICE_NAME in line.lower():
                    return int(line.strip().split()[0])
    except Exception:
        return None

    return None


def _setup_wm8960_mixer() -> None:
    """Configure the WM8960 codec for simultaneous mic capture and speaker output."""
    card_index = _find_wm8960_card()
    if card_index is None:
        logger.info("WM8960 ALSA card not found; skipping mixer setup")
        return

    logger.info("configuring WM8960 mixer on ALSA card %s", card_index)
    commands = [
        ["amixer", "-c", str(card_index), "sset", "Left Output Mixer PCM", "on"],
        ["amixer", "-c", str(card_index), "sset", "Right Output Mixer PCM", "on"],
        ["amixer", "-c", str(card_index), "sset", "Speaker", "121"],
        ["amixer", "-c", str(card_index), "sset", "Playback", "230"],
        ["amixer", "-c", str(card_index), "sset", "Left Input Mixer Boost", "on"],
        ["amixer", "-c", str(card_index), "sset", "Right Input Mixer Boost", "on"],
        ["amixer", "-c", str(card_index), "sset", "Capture", "45"],
        ["amixer", "-c", str(card_index), "sset", "ADC PCM", "195"],
        ["amixer", "-c", str(card_index), "sset", "Left Input Boost Mixer LINPUT1", "2"],
        ["amixer", "-c", str(card_index), "sset", "Right Input Boost Mixer RINPUT1", "2"],
    ]

    for command in commands:
        try:
            subprocess.run(command, capture_output=True, timeout=5, check=False)
        except FileNotFoundError:
            logger.warning("amixer not found; skipping WM8960 mixer setup")
            return
        except Exception:
            logger.exception("failed to run WM8960 mixer command: %s", command)


def _device_name_for_index(devices: rtc.MediaDevices, kind: str, index: int | None) -> str:
    listing = (
        devices.list_input_devices()
        if kind == "input"
        else devices.list_output_devices()
    )
    for device in listing:
        if device["index"] == index:
            return device["name"]

    return "system default" if index is None else f"device {index}"


def _select_audio_device(
    devices: rtc.MediaDevices,
    kind: str,
    requested_index: int | None,
) -> tuple[int | None, str]:
    listing = (
        devices.list_input_devices()
        if kind == "input"
        else devices.list_output_devices()
    )
    default_index = (
        devices.default_input_device()
        if kind == "input"
        else devices.default_output_device()
    )

    if requested_index is not None:
        for device in listing:
            if device["index"] == requested_index:
                return requested_index, device["name"]
        raise RuntimeError(f"{kind} device index {requested_index} not found")

    for device in listing:
        if DEFAULT_WM8960_DEVICE_NAME in device["name"].lower():
            return device["index"], device["name"]

    logger.warning("WM8960 %s device not found; using system default", kind)
    return default_index, _device_name_for_index(devices, kind, default_index)


def _create_token(config: Config) -> str:
    return (
        api.AccessToken(config.api_key, config.api_secret)
        .with_identity(config.identity)
        .with_name(config.name)
        .with_grants(api.VideoGrants(room_join=True, room=config.room_name))
        .to_jwt()
    )


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s",
        datefmt="%H:%M:%S",
    )
    load_dotenv(find_dotenv())

    config = Config.from_env()
    shutdown_event = asyncio.Event()
    background_tasks: set[asyncio.Task[None]] = set()

    def _create_background_task(coro: Awaitable[None]) -> None:
        task = asyncio.create_task(coro)
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    def _request_shutdown() -> None:
        if not shutdown_event.is_set():
            logger.info("shutdown requested; stopping Whisplay client")
        shutdown_event.set()

    _setup_wm8960_mixer()
    devices = rtc.MediaDevices(
        input_sample_rate=SAMPLE_RATE,
        output_sample_rate=SAMPLE_RATE,
        num_channels=NUM_CHANNELS,
        blocksize=OUTPUT_FRAME_SAMPLES,
    )
    input_device, input_device_name = _select_audio_device(
        devices,
        "input",
        config.audio_input_device,
    )
    output_device, output_device_name = _select_audio_device(
        devices,
        "output",
        config.audio_output_device,
    )
    logger.info(
        "using audio devices input=[%s] %s output=[%s] %s",
        input_device,
        input_device_name,
        output_device,
        output_device_name,
    )

    mic = devices.open_input(enable_aec=True, input_device=input_device)
    player = devices.open_output(output_device=output_device)
    room = rtc.Room()
    signal_handlers_registered = False
    loop = asyncio.get_running_loop()

    def _on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        if track.kind != rtc.TrackKind.KIND_AUDIO:
            return

        _create_background_task(player.add_track(track))
        logger.info("playing audio track %s from %s", track.sid, participant.identity)

    def _on_track_unsubscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        if track.kind != rtc.TrackKind.KIND_AUDIO:
            return

        _create_background_task(player.remove_track(track))
        logger.info(
            "stopped playing audio track %s from %s",
            track.sid,
            participant.identity,
        )

    room.on("track_subscribed", _on_track_subscribed)
    room.on("track_unsubscribed", _on_track_unsubscribed)

    try:
        try:
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, _request_shutdown)
            signal_handlers_registered = True
        except (NotImplementedError, RuntimeError):
            pass

        await room.connect(config.url, _create_token(config))
        logger.info("connected to room %s", room.name)

        track = rtc.LocalAudioTrack.create_audio_track("whisplay-mic", mic.source)
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        publication = await room.local_participant.publish_track(track, options)
        logger.info("published Whisplay microphone track %s", publication.sid)

        await player.start()
        logger.info("speaker playback started; waiting for remote audio")

        await shutdown_event.wait()
    finally:
        if signal_handlers_registered:
            for sig in (signal.SIGINT, signal.SIGTERM):
                with contextlib.suppress(Exception):
                    loop.remove_signal_handler(sig)

        room.off("track_subscribed", _on_track_subscribed)
        room.off("track_unsubscribed", _on_track_unsubscribed)

        for task in list(background_tasks):
            task.cancel()
        for task in list(background_tasks):
            with contextlib.suppress(asyncio.CancelledError):
                await task

        # Close playback before capture so PortAudio + AEC tear down cleanly.
        with contextlib.suppress(Exception):
            await player.aclose()
        with contextlib.suppress(Exception):
            await mic.aclose()
        with contextlib.suppress(Exception):
            await room.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
