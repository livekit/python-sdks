import os
import sys
import asyncio
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "livekit-rtc")))

from livekit import rtc
from livekit.rtc import MediaDevices

async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    url = os.getenv("LIVEKIT_URL")
    token = os.getenv("LIVEKIT_TOKEN")
    if not url or not token:
        raise RuntimeError("LIVEKIT_URL and LIVEKIT_TOKEN must be set in env")

    room = rtc.Room()

    # Create media devices helper and open default microphone with AEC enabled
    devices = MediaDevices()
    mic = devices.open_microphone(enable_aec=True)

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


