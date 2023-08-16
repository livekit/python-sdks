<!--BEGIN_BANNER_IMAGE-->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="/.github/banner_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="/.github/banner_light.png">
  <img style="width:100%;" alt="The LiveKit icon, the name of the repository and some sample code in the background." src="https://raw.githubusercontent.com/livekit/client-sdk-python/main/.github/banner_light.png">
</picture>
<!--END_BANNER_IMAGE-->

[![pypi-v](https://img.shields.io/pypi/v/livekit.svg)](https://pypi.org/project/livekit/)

# 📹🎙️🐍 Python Client SDK for LiveKit

The Livekit Python Client provides a convenient interface for integrating Livekit's real-time video and audio capabilities into your Python applications. With this library, developers can easily leverage Livekit's WebRTC functionalities, allowing them to focus on building their AI models or other application logic without worrying about the complexities of WebRTC.

Official LiveKit documentation: https://docs.livekit.io/

## Installation
```shell
$ pip install livekit
```

## Connecting to a room

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

    await room.run()
```

## Examples
 - [Facelandmark](https://github.com/livekit/client-sdk-python/tree/main/examples/face_landmark): Use mediapipe to detect face landmarks (eyes, nose ...)
 - [Whisper](https://github.com/livekit/client-sdk-python/tree/main/examples/whisper): Transcribe an audio track using OpenAI whisper
 - [Basic room](https://github.com/livekit/client-sdk-python/blob/main/examples/basic_room.py): Connect to a room
 - [Publish hue](https://github.com/livekit/client-sdk-python/blob/main/examples/publish_hue.py): Publish a rainbow video track
 - [Publish wave](https://github.com/livekit/client-sdk-python/blob/main/examples/publish_hue.py): Publish a sine wave 

## Getting help / Contributing

Please join us on [Slack](https://join.slack.com/t/livekit-users/shared_invite/zt-rrdy5abr-5pZ1wW8pXEkiQxBzFiXPUg) to get help from our [devs](https://github.com/orgs/livekit/teams/devs/members) / community members. We welcome your contributions(PRs) and details can be discussed there.

<!--BEGIN_REPO_NAV-->
<br/><table>
<thead><tr><th colspan="2">LiveKit Ecosystem</th></tr></thead>
<tbody>
<tr><td>Client SDKs</td><td><a href="https://github.com/livekit/components-js">Components</a> · <a href="https://github.com/livekit/client-sdk-js">JavaScript</a> · <a href="https://github.com/livekit/client-sdk-swift">iOS/macOS</a> · <a href="https://github.com/livekit/client-sdk-android">Android</a> · <a href="https://github.com/livekit/client-sdk-flutter">Flutter</a> · <a href="https://github.com/livekit/client-sdk-react-native">React Native</a> · <a href="https://github.com/livekit/client-sdk-rust">Rust</a> · <b>Python</b> · <a href="https://github.com/livekit/client-sdk-unity-web">Unity (web)</a> · <a href="https://github.com/livekit/client-sdk-unity">Unity (beta)</a></td></tr><tr></tr>
<tr><td>Server SDKs</td><td><a href="https://github.com/livekit/server-sdk-js">Node.js</a> · <a href="https://github.com/livekit/server-sdk-go">Golang</a> · <a href="https://github.com/livekit/server-sdk-ruby">Ruby</a> · <a href="https://github.com/livekit/server-sdk-kotlin">Java/Kotlin</a> · <a href="https://github.com/agence104/livekit-server-sdk-php">PHP (community)</a> · <a href="https://github.com/tradablebits/livekit-server-sdk-python">Python (community)</a></td></tr><tr></tr>
<tr><td>Services</td><td><a href="https://github.com/livekit/livekit">Livekit server</a> · <a href="https://github.com/livekit/egress">Egress</a> · <a href="https://github.com/livekit/ingress">Ingress</a></td></tr><tr></tr>
<tr><td>Resources</td><td><a href="https://docs.livekit.io">Docs</a> · <a href="https://github.com/livekit-examples">Example apps</a> · <a href="https://livekit.io/cloud">Cloud</a> · <a href="https://docs.livekit.io/oss/deployment">Self-hosting</a> · <a href="https://github.com/livekit/livekit-cli">CLI</a></td></tr>
</tbody>
</table>
<!--END_REPO_NAV-->
