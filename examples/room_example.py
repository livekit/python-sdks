import os
import logging
import asyncio
from livekit import rtc

# Set the following environment variables with your own values
TOKEN = os.environ.get("LIVEKIT_TOKEN")
URL = os.environ.get("LIVEKIT_URL")


async def main():
    logging.basicConfig(level=logging.INFO)
    room = rtc.Room()

    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logging.info(
            "participant connected: %s %s", participant.sid, participant.identity
        )

    async def receive_frames(stream: rtc.VideoStream):
        async for frame in stream:
            # received a video frame from the track, process it here
            pass

    # track_subscribed is emitted whenever the local participant is subscribed to a new track
    @room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        logging.info("track subscribed: %s", publication.sid)
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            video_stream = rtc.VideoStream(track)
            asyncio.ensure_future(receive_frames(video_stream))

    # By default, autosubscribe is enabled. The participant will be subscribed to
    # all published tracks in the room
    await room.connect(URL, TOKEN)
    logging.info("connected to room %s", room.name)

    for identity, participant in room.remote_participants.items():
        print(f"identity: {identity}")
        print(f"participant: {participant}")
        # Now participant is the RemoteParticipant object, not a tuple
        print(f"participant sid: {participant.sid}")
        print(f"participant identity: {participant.identity}")
        print(f"participant name: {participant.name}")
        print(f"participant kind: {participant.kind}")
        print(f"participant track publications: {
              participant.track_publications}")
        for tid, publication in participant.track_publications.items():
            print(f"\ttrack id: {tid}")
            print(f"\t\ttrack publication: {publication}")
            print(f"\t\ttrack kind: {publication.kind}")
            print(f"\t\ttrack name: {publication.name}")
            print(f"\t\ttrack source: {publication.source}")

        print(f"participant metadata: {participant.metadata}")


if __name__ == "__main__":
    # exit if token and url are not set
    if not TOKEN or not URL:
        print("TOKEN and URL are required environment variables")
        exit(1)

    asyncio.run(main())
