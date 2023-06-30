import livekit
import logging
import asyncio
from signal import SIGINT, SIGTERM

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'


async def main():
    room = livekit.Room()

    audio_stream = None
    video_stream = None

    logging.info("connecting to %s", URL)
    try:
        await room.connect(URL, TOKEN)
        logging.info("connected to room %s", room.name)
    except livekit.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
        return False

    @room.on("participant_connected")
    def on_participant_connected(participant: livekit.RemoteParticipant):
        logging.info(
            "participant connected: %s %s", participant.sid, participant.identity)

    @room.on("participant_disconnected")
    def on_participant_disconnected(participant: livekit.RemoteParticipant):
        logging.info("participant disconnected: %s %s",
                     participant.sid, participant.identity)

    @room.on("track_published")
    def on_track_published(publication: livekit.LocalTrackPublication, participant: livekit.RemoteParticipant):
        logging.info("track published: %s from participant %s (%s)",
                     publication.sid, participant.sid, participant.identity)

    @room.on("track_unpublished")
    def on_track_unpublished(publication: livekit.LocalTrackPublication, participant: livekit.RemoteParticipant):
        logging.info("track unpublished: %s", publication.sid)

    @room.on("track_subscribed")
    def on_track_subscribed(track: livekit.Track, publication: livekit.RemoteTrackPublication, participant: livekit.RemoteParticipant):
        logging.info("track subscribed: %s", publication.sid)
        if track.kind == livekit.TrackKind.KIND_VIDEO:
            nonlocal video_stream
            video_stream = livekit.VideoStream(track)

            @video_stream.on("frame_received")
            def on_video_frame(frame: livekit.VideoFrame):
                # received a video frame from the track
                pass
        elif track.kind == livekit.TrackKind.KIND_AUDIO:
            print("Subscribed to an Audio Track")
            nonlocal audio_stream
            audio_stream = livekit.AudioStream(track)

            @audio_stream.on('frame_received')
            def on_audio_frame(frame: livekit.AudioFrame):
                # received an audio frame from the track
                pass

    @room.on("track_unsubscribed")
    def on_track_unsubscribed(track: livekit.Track, publication: livekit.RemoteTrackPublication, participant: livekit.RemoteParticipant):
        logging.info("track unsubscribed: %s", publication.sid)

    try:
        await room.run()
    except asyncio.CancelledError:
        logging.info("closing the room")
        await room.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("basic_room.log"), logging.StreamHandler()])

    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main())
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
