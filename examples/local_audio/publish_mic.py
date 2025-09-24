import os
import asyncio
import logging
from dotenv import load_dotenv, find_dotenv

from livekit import api, rtc


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # Load environment variables from a .env file if present
    load_dotenv(find_dotenv())

    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    if not url or not api_key or not api_secret:
        raise RuntimeError("LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in env")

    room = rtc.Room()

    # Create media devices helper and open default microphone with AEC enabled
    devices = rtc.MediaDevices()
    mic = devices.open_input(enable_aec=True)
    
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
