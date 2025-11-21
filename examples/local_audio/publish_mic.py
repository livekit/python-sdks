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
        raise RuntimeError(
            "LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in env"
        )

    room = rtc.Room()

    # Create media devices helper and open default microphone with AEC enabled
    devices = rtc.MediaDevices()
    mic = devices.open_input(enable_aec=True)

    # dB level monitoring
    mic_db_queue = queue.Queue()

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

        track = rtc.LocalAudioTrack.create_audio_track("mic", mic.source)
        pub_opts = rtc.TrackPublishOptions()
        pub_opts.source = rtc.TrackSource.SOURCE_MICROPHONE
        await room.local_participant.publish_track(track, pub_opts)
        logging.info("published local microphone")

        # Start dB meter display in a separate thread
        meter_thread = threading.Thread(
            target=display_single_db_meter, args=(mic_db_queue, "Mic: "), daemon=True
        )
        meter_thread.start()

        # Monitor microphone dB levels
        async def monitor_mic_db():
            mic_stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
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
        try:
            await room.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
