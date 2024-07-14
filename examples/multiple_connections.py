import os
import asyncio
from livekit import api, rtc

# This example demonstrates running multiple connections sequentially in the same thread.
# This is useful when interoperating with a synchronous framework like Django or Flask
# where you would connect to a LiveKit room as part of a request handler.

# LIVEKIT_URL needs to be set
# also, set either LIVEKIT_TOKEN, or API_KEY and API_SECRET


async def main():
    url = os.environ["LIVEKIT_URL"]
    token = os.getenv("LIVEKIT_TOKEN")
    room = rtc.Room()
    if not token:
        token = (
            api.AccessToken()
            .with_identity("python-bot")
            .with_name("Python Bot")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room="my-room",
                )
            )
            .to_jwt()
        )

    track_sub = asyncio.Event()

    @room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            stream = rtc.AudioStream(track)  # the error comes from this line
            track_sub.set()
            # any created streams would need to be closed explicitly to avoid leaks
            asyncio.get_event_loop().create_task(stream.aclose())
            print("subscribed to audio track")

    await room.connect(url, token)
    print(f"connected to room: {room.name}")
    await track_sub.wait()
    await room.disconnect()
    print("disconnected from room")


def ensure_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        # Create a new event loop if none exists (this can happen in some contexts like certain threads)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main())
    print("successfully ran multiple connections")
