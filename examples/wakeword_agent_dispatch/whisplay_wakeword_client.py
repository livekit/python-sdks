from __future__ import annotations

import asyncio
import contextlib
import datetime
import logging
import os
import signal
import subprocess
import wave
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Deque, Optional

import numpy as np
from dotenv import find_dotenv, load_dotenv
from livekit import api, rtc

SAMPLE_RATE = 48_000
NUM_CHANNELS = 1
WAKEWORD_SAMPLE_RATE = 16_000
WAKEWORD_WINDOW_SAMPLES = 2 * WAKEWORD_SAMPLE_RATE
OUTPUT_FRAME_SAMPLES = 480  # 10 ms at 48 kHz
PRE_CONNECT_AUDIO_BUFFER_TOPIC = "lk.agent.pre-connect-audio-buffer"
DEFAULT_WM8960_DEVICE_NAME = "wm8960"

logger = logging.getLogger("whisplay-wakeword-client")


@dataclass(frozen=True)
class Config:
    url: str
    api_key: str
    api_secret: str
    room_name: str
    identity: str
    name: str
    agent_name: str
    wakeword_model: Path
    wakeword_name: Optional[str]
    wakeword_threshold: float
    wakeword_preroll_seconds: float
    preconnect_buffer_seconds: float
    preconnect_debug_wav: Path | None
    agent_metadata: str
    agent_wait_timeout: float
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
            identity=os.getenv("LIVEKIT_IDENTITY", "whisplay-wakeword-client"),
            name=os.getenv("LIVEKIT_NAME", "Whisplay Wake Word Client"),
            agent_name=os.getenv("LIVEKIT_AGENT_NAME", "test-agent"),
            wakeword_model=Path(
                os.getenv("LIVEKIT_WAKEWORD_MODEL", "./models/hey_livekit.onnx")
            ),
            wakeword_name=os.getenv("LIVEKIT_WAKEWORD_NAME"),
            wakeword_threshold=float(os.getenv("LIVEKIT_WAKEWORD_THRESHOLD", "0.5")),
            wakeword_preroll_seconds=float(
                os.getenv("LIVEKIT_WAKEWORD_PREROLL_SECONDS", "2.0")
            ),
            preconnect_buffer_seconds=float(
                os.getenv("LIVEKIT_PRECONNECT_BUFFER_SECONDS", "10.0")
            ),
            preconnect_debug_wav=(
                Path(debug_wav).expanduser()
                if (debug_wav := os.getenv("LIVEKIT_PRECONNECT_DEBUG_WAV"))
                else None
            ),
            agent_metadata=os.getenv("LIVEKIT_AGENT_METADATA", ""),
            agent_wait_timeout=float(os.getenv("LIVEKIT_AGENT_WAIT_TIMEOUT", "30.0")),
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
        ["amixer", "-c", str(card_index), "sset", "Speaker", "127"],
        ["amixer", "-c", str(card_index), "sset", "Speaker DC", "5"],
        ["amixer", "-c", str(card_index), "sset", "Speaker AC", "5"],
        ["amixer", "-c", str(card_index), "sset", "Playback", "255"],
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
        logger.warning(
            "%s device index %s not found; trying WM8960 or system default",
            kind,
            requested_index,
        )

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


@dataclass(frozen=True)
class MicChunk:
    data: bytes
    samples_per_channel: int


class PreconnectAudioBuffer:
    def __init__(self, max_duration: float) -> None:
        self._max_samples = self._duration_to_samples(max_duration)
        self._chunks: Deque[MicChunk] = deque()
        self._samples = 0

    @staticmethod
    def _duration_to_samples(duration: float) -> int:
        return max(1, int(duration * SAMPLE_RATE))

    def set_max_duration(self, max_duration: float) -> None:
        self._max_samples = self._duration_to_samples(max_duration)
        self._trim()

    def append(self, chunk: MicChunk) -> None:
        self._chunks.append(chunk)
        self._samples += chunk.samples_per_channel
        self._trim()

    def _trim(self) -> None:
        while self._samples > self._max_samples and len(self._chunks) > 1:
            dropped = self._chunks.popleft()
            self._samples -= dropped.samples_per_channel

    def capture(self) -> bytes:
        data = b"".join(chunk.data for chunk in self._chunks)
        self.clear()
        return data

    def clear(self) -> None:
        self._chunks.clear()
        self._samples = 0


class WakeWordAudioWindow:
    def __init__(self, max_samples: int) -> None:
        self._max_samples = max_samples
        self._chunks: Deque[np.ndarray] = deque()
        self._samples = 0

    def append(self, samples: np.ndarray) -> None:
        if samples.size == 0:
            return

        samples = samples.reshape(-1)
        self._chunks.append(samples)
        self._samples += samples.size

        while self._samples > self._max_samples:
            excess = self._samples - self._max_samples
            oldest = self._chunks[0]
            if oldest.size <= excess:
                self._chunks.popleft()
                self._samples -= oldest.size
            else:
                self._chunks[0] = oldest[excess:]
                self._samples -= excess

    @property
    def is_full(self) -> bool:
        return self._samples == self._max_samples

    def samples(self) -> np.ndarray:
        if len(self._chunks) == 1:
            return self._chunks[0].copy()

        return np.concatenate(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()
        self._samples = 0


class ClientMode(Enum):
    IDLE = "idle"
    DISPATCHING = "dispatching"
    IN_SESSION = "in_session"


@dataclass
class ClientState:
    mode: ClientMode = ClientMode.IDLE
    agent_identity: str | None = None
    dispatch_task: asyncio.Task[str] | None = None


def _chunk_to_audio_frame(chunk: MicChunk) -> rtc.AudioFrame:
    return rtc.AudioFrame(
        data=chunk.data,
        sample_rate=SAMPLE_RATE,
        num_channels=NUM_CHANNELS,
        samples_per_channel=chunk.samples_per_channel,
    )


def _put_chunk(queue: asyncio.Queue[MicChunk], chunk: MicChunk) -> None:
    if queue.full():
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            pass

    try:
        queue.put_nowait(chunk)
    except asyncio.QueueFull:
        pass


def _is_active_agent(participant: rtc.RemoteParticipant) -> bool:
    return (
        participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_AGENT
        and participant.state == rtc.ParticipantState.PARTICIPANT_STATE_ACTIVE
    )


async def _wait_for_active_agent(room: rtc.Room, timeout: float) -> rtc.RemoteParticipant:
    for participant in room.remote_participants.values():
        if _is_active_agent(participant):
            return participant

    loop = asyncio.get_running_loop()
    future: asyncio.Future[rtc.RemoteParticipant] = loop.create_future()

    def _on_participant_active(participant: rtc.RemoteParticipant) -> None:
        if _is_active_agent(participant) and not future.done():
            future.set_result(participant)

    room.on("participant_active", _on_participant_active)
    try:
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        room.off("participant_active", _on_participant_active)


def _preconnect_debug_wav_path(path: Path) -> Path:
    if path.suffix.lower() == ".wav":
        return path

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return path / f"preconnect-buffer-{timestamp}.wav"


def _write_preconnect_debug_wav(
    path: Path,
    pcm_data: bytes,
    *,
    sample_rate: int,
    num_channels: int,
) -> Path:
    output_path = _preconnect_debug_wav_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    return output_path


async def _send_preconnect_buffer(
    track: rtc.LocalAudioTrack,
    audio_queue: asyncio.Queue[MicChunk],
    preconnect_buffer: PreconnectAudioBuffer,
    *,
    destination_identity: str,
    debug_wav: Path | None,
) -> None:
    participant = getattr(track, "_participant", None)
    if participant is None:
        raise RuntimeError("track is not published")

    source = getattr(track, "_source", None)
    if source is None:
        raise RuntimeError("track has no audio source")

    async with track._send_lock:
        drained = _drain_audio_queue_to_buffer(audio_queue, preconnect_buffer)
        if drained:
            logger.info("included %d queued audio chunks in pre-connect buffer", drained)

        data = preconnect_buffer.capture()
        if not data:
            return

        if debug_wav is not None:
            output_path = _write_preconnect_debug_wav(
                debug_wav,
                data,
                sample_rate=source.sample_rate,
                num_channels=source.num_channels,
            )
            duration = len(data) / (source.sample_rate * source.num_channels * 2)
            logger.info(
                "wrote pre-connect buffer debug WAV %s (%.2fs, %d bytes)",
                output_path,
                duration,
                len(data),
            )

        writer = await participant.stream_bytes(
            "preconnect-buffer",
            topic=PRE_CONNECT_AUDIO_BUFFER_TOPIC,
            mime_type="application/octet-stream",
            destination_identities=[destination_identity],
            attributes={
                "trackId": track._publication_sid or track.sid,
                "sampleRate": str(source.sample_rate),
                "channels": str(source.num_channels),
            },
        )

        await writer.write(data)
        await writer.aclose()


async def _dispatch_agent_and_send_buffer(
    lkapi: api.LiveKitAPI,
    room: rtc.Room,
    track: rtc.LocalAudioTrack,
    audio_queue: asyncio.Queue[MicChunk],
    preconnect_buffer: PreconnectAudioBuffer,
    config: Config,
) -> str:
    dispatch = await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name=config.agent_name,
            room=config.room_name,
            metadata=config.agent_metadata,
        )
    )
    logger.info("created dispatch %s for agent %s", dispatch.id, config.agent_name)

    agent = await _wait_for_active_agent(room, timeout=config.agent_wait_timeout)
    logger.info("agent participant %s is active; sending buffered audio", agent.identity)
    await _send_preconnect_buffer(
        track,
        audio_queue,
        preconnect_buffer,
        destination_identity=agent.identity,
        debug_wav=config.preconnect_debug_wav,
    )
    logger.info("sent pre-connect buffer to %s", agent.identity)
    return agent.identity


def _drain_audio_queue(audio_queue: asyncio.Queue[MicChunk]) -> int:
    drained = 0
    while True:
        try:
            audio_queue.get_nowait()
            drained += 1
        except asyncio.QueueEmpty:
            return drained


def _drain_audio_queue_to_buffer(
    audio_queue: asyncio.Queue[MicChunk],
    preconnect_buffer: PreconnectAudioBuffer,
) -> int:
    drained = 0
    while True:
        try:
            chunk = audio_queue.get_nowait()
        except asyncio.QueueEmpty:
            return drained
        preconnect_buffer.append(chunk)
        drained += 1


async def _wait_mic_chunk_or_shutdown(
    audio_queue: asyncio.Queue[MicChunk],
    shutdown: asyncio.Event,
) -> MicChunk | None:
    """Return the next mic chunk, or None when shutdown was requested."""
    if shutdown.is_set():
        return None
    get_chunk = asyncio.create_task(audio_queue.get())
    wait_shutdown = asyncio.create_task(shutdown.wait())
    done, pending = await asyncio.wait(
        {get_chunk, wait_shutdown},
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    if wait_shutdown in done:
        return None
    return get_chunk.result()


def _reset_wakeword_model(model: Any) -> None:
    reset = getattr(model, "reset", None)
    if callable(reset):
        reset()


async def _monitor_mic_track(
    track: rtc.LocalAudioTrack,
    audio_queue: asyncio.Queue[MicChunk],
) -> None:
    audio_stream = rtc.AudioStream(
        track=track,
        sample_rate=SAMPLE_RATE,
        num_channels=NUM_CHANNELS,
        frame_size_ms=10,
    )
    try:
        async for event in audio_stream:
            frame = event.frame
            _put_chunk(
                audio_queue,
                MicChunk(
                    data=frame.data.tobytes(),
                    samples_per_channel=frame.samples_per_channel,
                ),
            )
    finally:
        await audio_stream.aclose()


async def _run_audio_loop(
    audio_queue: asyncio.Queue[MicChunk],
    model: Any,
    source: rtc.AudioSource,
    track: rtc.LocalAudioTrack,
    room: rtc.Room,
    lkapi: api.LiveKitAPI,
    config: Config,
    shutdown: asyncio.Event,
) -> None:
    preconnect_buffer = PreconnectAudioBuffer(config.wakeword_preroll_seconds)
    wakeword_window = WakeWordAudioWindow(WAKEWORD_WINDOW_SAMPLES)
    wakeword_resampler = rtc.AudioResampler(SAMPLE_RATE, WAKEWORD_SAMPLE_RATE)
    state = ClientState()

    def _reset_to_idle(reason: str, *, cancel_dispatch: bool = True) -> None:
        nonlocal wakeword_resampler

        if cancel_dispatch and state.dispatch_task and not state.dispatch_task.done():
            state.dispatch_task.cancel()

        state.dispatch_task = None
        state.agent_identity = None
        state.mode = ClientMode.IDLE
        source.clear_queue()
        preconnect_buffer.set_max_duration(config.wakeword_preroll_seconds)
        preconnect_buffer.clear()
        wakeword_window.clear()
        wakeword_resampler = rtc.AudioResampler(SAMPLE_RATE, WAKEWORD_SAMPLE_RATE)
        drained = _drain_audio_queue(audio_queue)
        _reset_wakeword_model(model)
        logger.info(
            "reset to idle mode after %s; dropped %d queued audio chunks",
            reason,
            drained,
        )

    def _on_participant_active(participant: rtc.RemoteParticipant) -> None:
        if not _is_active_agent(participant):
            return

        if state.mode == ClientMode.IDLE:
            state.mode = ClientMode.IN_SESSION
            state.agent_identity = participant.identity
            logger.info(
                "agent participant %s is active; wake word detection disabled",
                participant.identity,
            )

    def _on_participant_disconnected(participant: rtc.RemoteParticipant) -> None:
        if participant.kind != rtc.ParticipantKind.PARTICIPANT_KIND_AGENT:
            return

        if (
            state.mode == ClientMode.IN_SESSION
            and state.agent_identity == participant.identity
        ):
            logger.info("agent participant %s disconnected", participant.identity)
            _reset_to_idle("agent session ended")

    def _on_dispatch_done(task: asyncio.Task[str]) -> None:
        if state.dispatch_task is task:
            state.dispatch_task = None

        if task.cancelled():
            return

        try:
            agent_identity = task.result()
        except Exception:
            logger.exception("agent dispatch or pre-connect buffer send failed")
            _reset_to_idle("dispatch failed", cancel_dispatch=False)
            return

        agent = room.remote_participants.get(agent_identity)
        if agent is None:
            _reset_to_idle("agent left before session could start", cancel_dispatch=False)
            return

        state.mode = ClientMode.IN_SESSION
        state.agent_identity = agent_identity
        logger.info(
            "agent session is active for %s; wake word detection remains disabled",
            agent_identity,
        )

    logger.info("listening for wake word using %s", config.wakeword_model)

    room.on("participant_active", _on_participant_active)
    room.on("participant_disconnected", _on_participant_disconnected)
    for participant in room.remote_participants.values():
        _on_participant_active(participant)

    try:
        while True:
            chunk = await _wait_mic_chunk_or_shutdown(audio_queue, shutdown)
            if chunk is None:
                logger.info("audio loop stopping (shutdown requested)")
                break

            if state.mode in (ClientMode.IDLE, ClientMode.DISPATCHING):
                preconnect_buffer.append(chunk)

            if state.mode == ClientMode.IDLE:
                for wakeword_frame in wakeword_resampler.push(_chunk_to_audio_frame(chunk)):
                    samples = np.frombuffer(wakeword_frame.data, dtype=np.int16)
                    wakeword_window.append(samples)
                if not wakeword_window.is_full:
                    continue

                scores = model.predict(wakeword_window.samples())
                if not scores:
                    continue

                wakeword_name = config.wakeword_name or next(iter(scores))
                confidence = float(scores.get(wakeword_name, 0.0))

                if confidence >= config.wakeword_threshold:
                    state.mode = ClientMode.DISPATCHING
                    logger.info(
                        "detected %s with confidence %.2f; wake word detection disabled",
                        wakeword_name,
                        confidence,
                    )

                    # Keep one ordered buffer from the monitor stream so the wakeword
                    # preroll and dispatch audio do not cross timing domains.
                    preconnect_buffer.set_max_duration(config.preconnect_buffer_seconds)

                    state.dispatch_task = asyncio.create_task(
                        _dispatch_agent_and_send_buffer(
                            lkapi,
                            room,
                            track,
                            audio_queue,
                            preconnect_buffer,
                            config,
                        )
                    )
                    state.dispatch_task.add_done_callback(_on_dispatch_done)
    finally:
        room.off("participant_active", _on_participant_active)
        room.off("participant_disconnected", _on_participant_disconnected)
        _reset_to_idle("audio loop stopped")


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s",
        datefmt="%H:%M:%S",
    )
    load_dotenv(find_dotenv())

    config = Config.from_env()
    if not config.wakeword_model.exists():
        raise RuntimeError(f"wake word model not found: {config.wakeword_model}")

    from livekit.wakeword import WakeWordModel

    shutdown_event = asyncio.Event()
    background_tasks: set[asyncio.Task[None]] = set()

    def _create_background_task(coro: Awaitable[None]) -> None:
        task = asyncio.create_task(coro)
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    def _request_shutdown() -> None:
        if not shutdown_event.is_set():
            logger.info("shutdown requested; stopping Whisplay wake word client")
        shutdown_event.set()

    model = WakeWordModel(models=[str(config.wakeword_model)])
    audio_queue: asyncio.Queue[MicChunk] = asyncio.Queue(maxsize=100)
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
    lkapi = api.LiveKitAPI(config.url, config.api_key, config.api_secret)
    signal_handlers_registered = False
    loop = asyncio.get_running_loop()

    async def _log_transcription_stream(
        reader: rtc.TextStreamReader,
        participant_identity: str,
    ) -> None:
        chunks: list[str] = []
        try:
            async for chunk in reader:
                chunks.append(chunk)
                logger.info(
                    "transcription chunk from %s: %s",
                    participant_identity,
                    chunk,
                )

            transcript = "".join(chunks).strip()
            logger.info(
                "transcription stream from %s complete: %s attributes=%s",
                participant_identity,
                transcript or "<empty>",
                reader.info.attributes,
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception(
                "failed to read transcription stream from %s",
                participant_identity,
            )

    def _on_transcription_stream(
        reader: rtc.TextStreamReader,
        participant_identity: str,
    ) -> None:
        _create_background_task(
            _log_transcription_stream(reader, participant_identity)
        )

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
    room.register_text_stream_handler("lk.transcription", _on_transcription_stream)

    try:
        try:
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, _request_shutdown)
            signal_handlers_registered = True
        except (NotImplementedError, RuntimeError):
            pass

        await room.connect(config.url, _create_token(config))
        logger.info("connected to room %s", room.name)

        track = rtc.LocalAudioTrack.create_audio_track("whisplay-wakeword-mic", mic.source)
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        options.preconnect_buffer = True
        publication = await room.local_participant.publish_track(track, options)
        logger.info("published Whisplay microphone track %s", publication.sid)

        await player.start()
        logger.info("speaker playback started; waiting for room audio")
        _create_background_task(_monitor_mic_track(track, audio_queue))

        await _run_audio_loop(
            audio_queue,
            model,
            mic.source,
            track,
            room,
            lkapi,
            config,
            shutdown_event,
        )
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

        room.unregister_text_stream_handler("lk.transcription")
        with contextlib.suppress(Exception):
            await lkapi.aclose()
        with contextlib.suppress(Exception):
            await room.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
