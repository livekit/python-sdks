from __future__ import annotations

import asyncio
import contextlib
import logging
import os
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Deque, Iterable, Optional

import numpy as np
from dotenv import find_dotenv, load_dotenv
from livekit import api, rtc

SAMPLE_RATE = 48_000
NUM_CHANNELS = 1
WAKEWORD_SAMPLE_RATE = 16_000
WAKEWORD_WINDOW_SAMPLES = 2 * WAKEWORD_SAMPLE_RATE
OUTPUT_SAMPLE_RATE = 48_000
OUTPUT_FRAME_SAMPLES = 480  # 10 ms at 48 kHz

logger = logging.getLogger("wakeword-agent-dispatch")


@dataclass(frozen=True)
class Config:
    url: str
    api_key: str
    api_secret: str
    room_name: str
    agent_name: str
    wakeword_model: Path
    wakeword_name: Optional[str]
    wakeword_threshold: float
    wakeword_preroll_seconds: float
    preconnect_buffer_seconds: float
    agent_metadata: str
    agent_wait_timeout: float

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
            agent_metadata=os.getenv("LIVEKIT_AGENT_METADATA", ""),
            agent_wait_timeout=float(os.getenv("LIVEKIT_AGENT_WAIT_TIMEOUT", "30.0")),
        )


@dataclass(frozen=True)
class MicChunk:
    data: bytes
    samples_per_channel: int


class PrerollBuffer:
    def __init__(self, max_duration: float) -> None:
        self._max_samples = max(1, int(max_duration * SAMPLE_RATE))
        self._chunks: Deque[MicChunk] = deque()
        self._samples = 0

    def append(self, chunk: MicChunk) -> None:
        self._chunks.append(chunk)
        self._samples += chunk.samples_per_channel

        while self._samples > self._max_samples and len(self._chunks) > 1:
            dropped = self._chunks.popleft()
            self._samples -= dropped.samples_per_channel

    def snapshot(self) -> list[MicChunk]:
        return list(self._chunks)

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


def _push_preroll_to_preconnect_buffer(
    track: rtc.LocalAudioTrack,
    chunks: Iterable[MicChunk],
) -> None:
    preconnect_buffer = getattr(track, "_preconnect_buffer", None)
    if preconnect_buffer is None:
        raise RuntimeError("pre-connect buffer was not started")

    for chunk in chunks:
        preconnect_buffer.push(_chunk_to_audio_frame(chunk))


async def _dispatch_agent_and_send_buffer(
    lkapi: api.LiveKitAPI,
    room: rtc.Room,
    track: rtc.LocalAudioTrack,
    config: Config,
) -> str:
    try:
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
        await track.send_preconnect_buffer(destination_identity=agent.identity)
        logger.info("sent pre-connect buffer to %s", agent.identity)
        return agent.identity
    finally:
        track.stop_preconnect_buffer()


def _drain_audio_queue(audio_queue: asyncio.Queue[MicChunk]) -> int:
    drained = 0
    while True:
        try:
            audio_queue.get_nowait()
            drained += 1
        except asyncio.QueueEmpty:
            return drained


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
) -> None:
    preroll = PrerollBuffer(config.wakeword_preroll_seconds)
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
        track.stop_preconnect_buffer()
        source.clear_queue()
        preroll.clear()
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
            chunk = await audio_queue.get()

            if state.mode == ClientMode.IDLE:
                preroll.append(chunk)

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

                    track.start_preconnect_buffer(
                        max_duration=config.preconnect_buffer_seconds
                    )

                    # The SDK buffer only captures after it starts. Because this loop
                    # observes the already-published mic track, include the full preroll.
                    preroll_chunks = preroll.snapshot()
                    _push_preroll_to_preconnect_buffer(track, preroll_chunks)

                    state.dispatch_task = asyncio.create_task(
                        _dispatch_agent_and_send_buffer(lkapi, room, track, config)
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

    model = WakeWordModel(models=[str(config.wakeword_model)])
    room = rtc.Room()
    lkapi = api.LiveKitAPI(config.url, config.api_key, config.api_secret)
    audio_queue: asyncio.Queue[MicChunk] = asyncio.Queue(maxsize=100)
    devices = rtc.MediaDevices(
        input_sample_rate=SAMPLE_RATE,
        output_sample_rate=OUTPUT_SAMPLE_RATE,
        num_channels=NUM_CHANNELS,
        blocksize=OUTPUT_FRAME_SAMPLES,
    )
    mic = devices.open_input(enable_aec=True)
    player = devices.open_output()
    background_tasks: set[asyncio.Task[None]] = set()

    def _create_background_task(coro) -> None:
        task = asyncio.create_task(coro)
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

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

    def _maybe_play_agent_track(
        track: rtc.Track,
        participant: rtc.RemoteParticipant,
    ) -> None:
        if (
            track.kind != rtc.TrackKind.KIND_AUDIO
            or participant.kind != rtc.ParticipantKind.PARTICIPANT_KIND_AGENT
        ):
            return

        _create_background_task(player.add_track(track))
        logger.info(
            "playing agent audio track %s from %s",
            track.sid,
            participant.identity,
        )

    def _on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        _maybe_play_agent_track(track, participant)

    def _on_track_unsubscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        _create_background_task(player.remove_track(track))
        logger.info(
            "stopped playing audio track %s from %s",
            track.sid,
            participant.identity,
        )

    room.on("track_subscribed", _on_track_subscribed)
    room.on("track_unsubscribed", _on_track_unsubscribed)
    room.register_text_stream_handler("lk.transcription", _on_transcription_stream)

    token = (
        api.AccessToken(config.api_key, config.api_secret)
        .with_identity("wakeword-client")
        .with_name("Wake Word Client")
        .with_grants(api.VideoGrants(room_join=True, room=config.room_name))
        .to_jwt()
    )

    try:
        await room.connect(config.url, token)
        logger.info("connected to room %s", room.name)

        track = rtc.LocalAudioTrack.create_audio_track("wakeword-mic", mic.source)

        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        options.preconnect_buffer = True
        publication = await room.local_participant.publish_track(track, options)
        logger.info("published microphone track %s", publication.sid)

        await player.start()
        _create_background_task(_monitor_mic_track(track, audio_queue))

        await _run_audio_loop(
            audio_queue,
            model,
            mic.source,
            track,
            room,
            lkapi,
            config,
        )
    finally:
        for task in list(background_tasks):
            task.cancel()
        for task in list(background_tasks):
            with contextlib.suppress(asyncio.CancelledError):
                await task
        await mic.aclose()
        await player.aclose()
        room.unregister_text_stream_handler("lk.transcription")
        await lkapi.aclose()
        await room.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
