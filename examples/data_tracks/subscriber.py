import os
import logging
import asyncio
from signal import SIGINT, SIGTERM
from livekit import rtc

# Set the following environment variables with your own values
TOKEN = os.environ.get("LIVEKIT_TOKEN")
URL = os.environ.get("LIVEKIT_URL")


async def subscribe(track: rtc.RemoteDataTrack):
    logging.info(
        "Subscribing to '%s' published by '%s'",
        track.info.name,
        track.publisher_identity,
    )
    subscription = await track.subscribe()
    async for frame in subscription:
        logging.info("Received frame (%d bytes)", len(frame.payload))

        latency = frame.duration_since_timestamp()
        if latency is not None:
            logging.info("Latency: %.3f s", latency)


async def main(room: rtc.Room):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    active_tasks = []

    @room.on("data_track_published")
    def on_data_track_published(track: rtc.RemoteDataTrack):
        task = asyncio.create_task(subscribe(track))
        active_tasks.append(task)
        task.add_done_callback(lambda _: active_tasks.remove(task))

    await room.connect(URL, TOKEN)
    logger.info("connected to room %s", room.name)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("subscriber.log"),
            logging.StreamHandler(),
        ],
    )

    loop = asyncio.get_event_loop()
    room = rtc.Room(loop=loop)

    async def cleanup():
        await room.disconnect()
        loop.stop()

    asyncio.ensure_future(main(room))
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, lambda: asyncio.ensure_future(cleanup()))

    try:
        loop.run_forever()
    finally:
        loop.close()
