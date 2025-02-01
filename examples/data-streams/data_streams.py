import os
import logging
import asyncio
from signal import SIGINT, SIGTERM
from livekit import rtc

# Set the following environment variables with your own values
TOKEN = os.environ.get("LIVEKIT_TOKEN")
URL = os.environ.get("LIVEKIT_URL")


async def main(room: rtc.Room):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    async def greetParticipant(identity: str):
        text_writer = await room.local_participant.stream_text(
            destination_identities=[identity], topic="chat"
        )
        for char in "Hi! Just a friendly message":
            await text_writer.write(char)
        await text_writer.aclose()

        await room.local_participant.send_file(
            "./green_tree_python.jpg",
            destination_identities=[identity],
            topic="files",
        )

    async def on_chat_message_received(
        reader: rtc.TextStreamReader, participant_identity: str
    ):
        full_text = await reader.read_all()
        logger.info(
            "Received chat message from %s: '%s'", participant_identity, full_text
        )

    async def on_welcome_image_received(
        reader: rtc.ByteStreamReader, participant_identity: str
    ):
        logger.info(
            "Received image from %s: '%s'", participant_identity, reader.info["name"]
        )
        with open(reader.info["name"], mode="wb") as f:
            async for chunk in reader:
                f.write(chunk)

            f.close()

    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logger.info(
            "participant connected: %s %s", participant.sid, participant.identity
        )
        asyncio.create_task(greetParticipant(participant.identity))

    room.set_text_stream_handler(
        "chat",
        lambda reader, participant_identity: asyncio.create_task(
            on_chat_message_received(reader, participant_identity)
        ),
    )

    room.set_byte_stream_handler(
        "files",
        lambda reader, participant_identity: asyncio.create_task(
            on_welcome_image_received(reader, participant_identity)
        ),
    )

    # By default, autosubscribe is enabled. The participant will be subscribed to
    # all published tracks in the room
    await room.connect(URL, TOKEN)
    logger.info("connected to room %s", room.name)

    for identity, participant in room.remote_participants.items():
        logger.info("Sending a welcome message to %s", identity)
        await greetParticipant(participant.identity)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("data_stream_example.log"),
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
