
[![crates.io](https://img.shields.io/pypi/v/livekit.svg)](https://pypi.org/project/livekit/)

# client-sdk-python
The Livekit Python Client provides a convenient interface for integrating Livekit's real-time video and audio capabilities into your Python applications. With this library, developers can easily leverage Livekit's WebRTC functionalities, allowing them to focus on building their AI models or other application logic without worrying about the complexities of WebRTC.

### Connecting to a room
```python
async def main():
    room = livekit.Room()
    await room.connect(URL, TOKEN)
    logging.info("connected to room %s", room.name)

    @room.on("participant_connected")
    def on_participant_connected(participant: livekit.RemoteParticipant):
        logging.info(
            "participant connected: %s %s", participant.sid, participant.identity)

    video_stream = None
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
```
