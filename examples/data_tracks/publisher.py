import os
import logging
import asyncio
from signal import SIGINT, SIGTERM
from livekit import rtc

# Set the following environment variables with your own values
TOKEN = os.environ.get("LIVEKIT_TOKEN")
URL = os.environ.get("LIVEKIT_URL")

async def read_sensor() -> bytes:
    # Dynamically read some sensor data...
    return bytes([0xFA] * 256)

async def push_frames(track: rtc.LocalDataTrack):
    while True:
        data = await read_sensor()
        try:
            track.try_push(rtc.DataTrackFrame(payload=data))
        except rtc.PushFrameError as e:
            logging.error("Failed to push frame: %s", e)
        await asyncio.sleep(0.5)

async def main(room: rtc.Room):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    await room.connect(URL, TOKEN)
    logger.info("connected to room %s", room.name)

    track = await room.local_participant.publish_data_track("my_sensor_data")
    await push_frames(track)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("publisher.log"),
            logging.StreamHandler(),
        ],
    )

    loop = asyncio.get_event_loop()
    room = rtc.Room(loop=loop)

    main_task = asyncio.ensure_future(main(room))

    async def cleanup():
        main_task.cancel()
        try:
            await main_task
        except asyncio.CancelledError:
            pass
        await room.disconnect()
        loop.stop()

    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, lambda: asyncio.ensure_future(cleanup()))

    try:
        loop.run_forever()
    finally:
        loop.close()
