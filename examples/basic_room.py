import asyncio
import logging
from signal import SIGINT, SIGTERM
from typing import Union

import livekit

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'


async def main() -> None:
    room = livekit.Room()

    @room.listens_to("participant_connected")
    def on_participant_connected(participant: livekit.RemoteParticipant) -> None:
        logging.info(
            "participant connected: %s %s", participant.sid, participant.identity)

    @room.listens_to("participant_disconnected")
    def on_participant_disconnected(participant: livekit.RemoteParticipant):
        logging.info("participant disconnected: %s %s",
                     participant.sid, participant.identity)

    @room.listens_to("local_track_published")
    def on_local_track_published(publication: livekit.LocalTrackPublication,
                                 track: Union[livekit.LocalAudioTrack,
                                              livekit.LocalVideoTrack]):
        logging.info("local track published: %s", publication.sid)

    @room.listens_to("active_speakers_changed")
    def on_active_speakers_changed(speakers: list[livekit.Participant]):
        logging.info("active speakers changed: %s", speakers)

    @room.listens_to("local_track_unpublished")
    def on_local_track_unpublished(publication: livekit.LocalTrackPublication):
        logging.info("local track unpublished: %s", publication.sid)

    @room.listens_to("track_published")
    def on_track_published(publication: livekit.RemoteTrackPublication,
                           participant: livekit.RemoteParticipant):
        logging.info("track published: %s from participant %s (%s)",
                     publication.sid, participant.sid, participant.identity)

    @room.listens_to("track_unpublished")
    def on_track_unpublished(publication: livekit.RemoteTrackPublication,
                             participant: livekit.RemoteParticipant):
        logging.info("track unpublished: %s", publication.sid)

    @room.listens_to("track_subscribed")
    def on_track_subscribed(track: livekit.Track,
                            publication: livekit.RemoteTrackPublication,
                            participant: livekit.RemoteParticipant):
        logging.info("track subscribed: %s", publication.sid)
        if track.kind == livekit.TrackKind.KIND_VIDEO:
            video_stream = livekit.VideoStream(track)
            # video_stream is an async iterator that yields VideoFrame
        elif track.kind == livekit.TrackKind.KIND_AUDIO:
            print("Subscribed to an Audio Track")
            audio_stream = livekit.AudioStream(track)
            # audio_stream is an async iterator that yields AudioFrame

    @room.listens_to("track_unsubscribed")
    def on_track_unsubscribed(track: livekit.Track,
                              publication: livekit.RemoteTrackPublication,
                              participant: livekit.RemoteParticipant):
        logging.info("track unsubscribed: %s", publication.sid)

    @room.listens_to("track_muted")
    def on_track_muted(publication: livekit.RemoteTrackPublication,
                       participant: livekit.RemoteParticipant):
        logging.info("track muted: %s", publication.sid)

    @room.listens_to("track_unmuted")
    def on_track_unmuted(publication: livekit.RemoteTrackPublication,
                         participant: livekit.RemoteParticipant):
        logging.info("track unmuted: %s", publication.sid)

    @room.listens_to("data_received")
    def on_data_received(data: bytes,
                         kind: livekit.DataPacketKind,
                         participant: livekit.Participant):
        logging.info("received data from %s: %s", participant.identity, data)

    @room.listens_to("connection_quality_changed")
    def on_connection_quality_changed(participant: livekit.Participant,
                                      quality: livekit.ConnectionQuality):
        logging.info("connection quality changed for %s", participant.identity)

    @room.listens_to("track_subscription_failed")
    def on_track_subscription_failed(participant: livekit.RemoteParticipant,
                                     track_sid: str,
                                     error: str):
        logging.info("track subscription failed: %s %s",
                     participant.identity, error)

    @room.listens_to("connection_state_changed")
    def on_connection_state_changed(state: livekit.ConnectionState):
        logging.info("connection state changed: %s", state)

    @room.listens_to("connected")
    def on_connected() -> None:
        logging.info("connected")

    @room.listens_to("disconnected")
    def on_disconnected() -> None:
        logging.info("disconnected")

    @room.listens_to("reconnecting")
    def on_reconnecting() -> None:
        logging.info("reconnecting")

    @room.listens_to("reconnected")
    def on_reconnected() -> None:
        logging.info("reconnected")

    try:
        logging.info("connecting to %s", URL)
        await room.connect(URL, TOKEN)
        logging.info("connected to room %s", room.name)

        await room.local_participant.publish_data("hello world")

        logging.info("participants: %s", room.participants)

        await room.run()
    except livekit.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
    except asyncio.CancelledError:
        logging.info("closing the room")
        await room.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("basic_room.log"), logging.StreamHandler()])

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, loop.stop)
    try:
        loop.run_forever()
    finally:
        loop.close()
