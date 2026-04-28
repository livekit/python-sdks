import argparse
import asyncio
import logging
import signal

from livekit import rtc


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="LiveKit server URL")
    parser.add_argument("--token", required=True, help="LiveKit access token")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("debug-participant")

    room = rtc.Room()
    stop_event = asyncio.Event()

    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant) -> None:
        logger.info(
            "participant connected: sid=%s identity=%s",
            participant.sid,
            participant.identity,
        )

    @room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant) -> None:
        logger.info(
            "participant disconnected: sid=%s identity=%s",
            participant.sid,
            participant.identity,
        )

    @room.on("data_track_published")
    def on_data_track_published(track: rtc.RemoteDataTrack) -> None:
        logger.info(
            "data track published: sid=%s name=%s publisher=%s",
            track.info.sid,
            track.info.name,
            track.publisher_identity,
        )

    @room.on("data_track_unpublished")
    def on_data_track_unpublished(track_sid: str) -> None:
        logger.info("data track unpublished: sid=%s", track_sid)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await room.connect(args.url, args.token)
    logger.info("connected to room: %s", room.name)

    for participant in room.remote_participants.values():
        logger.info(
            "participant already in room: sid=%s identity=%s",
            participant.sid,
            participant.identity,
        )

    try:
        await stop_event.wait()
    finally:
        await room.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
