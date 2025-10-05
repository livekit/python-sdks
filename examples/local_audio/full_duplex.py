import os
import asyncio
import logging
import threading
import queue
from dotenv import load_dotenv, find_dotenv

from livekit import api, rtc
from db_meter import calculate_db_level, display_dual_db_meters


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # Load environment variables from a .env file if present
    load_dotenv(find_dotenv())

    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    if not url or not api_key or not api_secret:
        raise RuntimeError("LIVEKIT_URL and LIVEKIT_TOKEN must be set in env")

    room = rtc.Room()

    devices = rtc.MediaDevices()

    # Open microphone & speaker
    mic = devices.open_input()
    player = devices.open_output()

    # Mixer for all remote audio streams
    mixer = rtc.AudioMixer(sample_rate=48000, num_channels=1)

    # dB level monitoring
    mic_db_queue = queue.Queue()
    room_db_queue = queue.Queue()

    # Track stream bookkeeping for cleanup
    streams_by_pub: dict[str, rtc.AudioStream] = {}
    streams_by_participant: dict[str, set[rtc.AudioStream]] = {}
    
    # remove stream from mixer and close it
    async def _remove_stream(
        stream: rtc.AudioStream, participant_sid: str | None = None, pub_sid: str | None = None
    ) -> None:
        try:
            mixer.remove_stream(stream)
        except Exception:
            pass
        try:
            await stream.aclose()
        except Exception:
            pass
        if participant_sid and participant_sid in streams_by_participant:
            streams_by_participant.get(participant_sid, set()).discard(stream)
            if not streams_by_participant.get(participant_sid):
                streams_by_participant.pop(participant_sid, None)
        if pub_sid is not None:
            streams_by_pub.pop(pub_sid, None)

    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
            streams_by_pub[publication.sid] = stream
            streams_by_participant.setdefault(participant.sid, set()).add(stream)
            mixer.add_stream(stream)
            logging.info("subscribed to audio from %s", participant.identity)

    room.on("track_subscribed", on_track_subscribed)

    def on_track_unsubscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        stream = streams_by_pub.get(publication.sid)
        if stream is not None:
            asyncio.create_task(_remove_stream(stream, participant.sid, publication.sid))
            logging.info("unsubscribed from audio of %s", participant.identity)

    room.on("track_unsubscribed", on_track_unsubscribed)

    def on_track_unpublished(
        publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant
    ):
        stream = streams_by_pub.get(publication.sid)
        if stream is not None:
            asyncio.create_task(_remove_stream(stream, participant.sid, publication.sid))
            logging.info("track unpublished: %s from %s", publication.sid, participant.identity)

    room.on("track_unpublished", on_track_unpublished)

    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        streams = list(streams_by_participant.pop(participant.sid, set()))
        for stream in streams:
            # Best-effort discover publication sid
            pub_sid = None
            for k, v in list(streams_by_pub.items()):
                if v is stream:
                    pub_sid = k
                    break
            asyncio.create_task(_remove_stream(stream, participant.sid, pub_sid))
        logging.info("participant disconnected: %s", participant.identity)

    room.on("participant_disconnected", on_participant_disconnected)

    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity("local-audio")
        .with_name("Local Audio")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room="local-audio",
            )
        )
        .to_jwt()
    )

    try:
        await room.connect(url, token)
        logging.info("connected to room %s", room.name)

        # Publish microphone
        track = rtc.LocalAudioTrack.create_audio_track("mic", mic.source)
        pub_opts = rtc.TrackPublishOptions()
        pub_opts.source = rtc.TrackSource.SOURCE_MICROPHONE
        await room.local_participant.publish_track(track, pub_opts)
        logging.info("published local microphone")

        # Start dB meter display in a separate thread
        meter_thread = threading.Thread(
            target=display_dual_db_meters,
            args=(mic_db_queue, room_db_queue),
            daemon=True
        )
        meter_thread.start()

        # Create a monitoring wrapper for the mixer that calculates dB levels
        # while passing frames through to the player
        async def monitored_mixer():
            try:
                async for frame in mixer:
                    # Calculate dB level for room audio
                    samples = list(frame.data)
                    db_level = calculate_db_level(samples)
                    try:
                        room_db_queue.put_nowait(db_level)
                    except queue.Full:
                        pass  # Drop if queue is full
                    # Yield the frame for playback
                    yield frame
            except Exception:
                pass

        # Start playing mixed remote audio with monitoring
        asyncio.create_task(player.play(monitored_mixer()))

        # Monitor microphone dB levels
        async def monitor_mic_db():
            mic_stream = rtc.AudioStream(
                track, sample_rate=48000, num_channels=1
            )
            try:
                async for frame_event in mic_stream:
                    frame = frame_event.frame
                    # Convert frame data to list of samples
                    samples = list(frame.data)
                    db_level = calculate_db_level(samples)
                    # Update queue with latest value (non-blocking)
                    try:
                        mic_db_queue.put_nowait(db_level)
                    except queue.Full:
                        pass  # Drop if queue is full
            except Exception:
                pass
            finally:
                await mic_stream.aclose()

        asyncio.create_task(monitor_mic_db())

        # Run until Ctrl+C
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await mic.aclose()
        await mixer.aclose()
        await player.aclose()
        try:
            await room.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
