import os
import asyncio
import logging
import threading
import queue
from dotenv import load_dotenv, find_dotenv

from livekit import api, rtc
from db_meter import calculate_db_level, display_single_db_meter


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

    # dB level monitoring (mic only)
    mic_db_queue = queue.Queue()

    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            player.add_track(track)
            logging.info("subscribed to audio from %s", participant.identity)

    room.on("track_subscribed", on_track_subscribed)

    def on_track_unsubscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        asyncio.create_task(player.remove_track(track))
        logging.info("unsubscribed from audio of %s", participant.identity)

    room.on("track_unsubscribed", on_track_unsubscribed)

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
            target=display_single_db_meter,
            args=(mic_db_queue,),
            kwargs={"label": "Mic Level: "},
            daemon=True
        )
        meter_thread.start()

        # Start playing mixed remote audio (tracks added via event handlers)
        await player.start()

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
        await player.aclose()
        try:
            await room.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
