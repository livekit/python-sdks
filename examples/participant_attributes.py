import asyncio
import logging
from signal import SIGINT, SIGTERM
import os

from livekit import api, rtc

# ensure LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET are set


async def main(room: rtc.Room) -> None:
    token = (
        api.AccessToken()
        .with_identity("python-bot")
        .with_name("Python Bot")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room="my-room",
                can_update_own_metadata=True,
            )
        )
        .to_jwt()
    )

    @room.on("participant_attributes_changed")
    def on_participant_attributes_changed(
        participant: rtc.Participant, changed_attributes: dict[str, str]
    ):
        logging.info(
            "participant attributes changed: %s %s",
            participant.attributes,
            changed_attributes,
        )

    await room.connect(os.getenv("LIVEKIT_URL"), token)
    logging.info("connected to room %s", room.name)

    # Create an attribute
    await room.local_participant.set_attributes({"foo": "bar"})
    # Delete an attribute
    await room.local_participant.set_attributes({"foo": ""})

    # Create another attribute
    await room.local_participant.set_attributes({"baz": "qux"})

    # Update an attribute
    await room.local_participant.set_attributes({"baz": "biz"})


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.FileHandler("basic_room.log"), logging.StreamHandler()],
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
