<!--BEGIN_BANNER_IMAGE-->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="/.github/banner_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="/.github/banner_light.png">
  <img style="width:100%;" alt="The LiveKit icon, the name of the repository and some sample code in the background." src="https://raw.githubusercontent.com/livekit/python-sdks/main/.github/banner_light.png">
</picture>

<!--END_BANNER_IMAGE-->

[![pypi-v](https://img.shields.io/pypi/v/livekit.svg)](https://pypi.org/project/livekit/)

# 📹🎙️🐍 Python SDK for LiveKit

<!--BEGIN_DESCRIPTION-->
Use this SDK to add realtime video, audio and data features to your Python app. By connecting to <a href="https://livekit.io/">LiveKit</a> Cloud or a self-hosted server, you can quickly build applications such as multi-modal AI, live streaming, or video calls with just a few lines of code.
<!--END_DESCRIPTION-->

This repo contains two packages

- [livekit](https://pypi.org/project/livekit/): Real-time SDK for connecting to LiveKit as a participant
- [livekit-api](https://pypi.org/project/livekit-api/): Access token generation and server APIs

## Using Server API

```shell
$ pip install livekit-api
```

### Generating an access token

```python
from livekit import api
import os

# will automatically use the LIVEKIT_API_KEY and LIVEKIT_API_SECRET env vars
token = api.access_token.AccessToken() \
    .with_identity("python-bot") \
    .with_name("Python Bot") \
    .with_grants(api.access_token.VideoGrants(
        room_join=True,
        room="my-room",
    )).to_jwt()
```

### Creating a room

RoomService uses asyncio and aiohttp to make API calls. It needs to be used with an event loop.

```python
from livekit import api
import asyncio

async def main():
    lkapi = api.livekit_api.LiveKitAPI(
        'http://localhost:7880',
    )
    room_info = await lkapi.room.create_room(
        api.CreateRoomRequest(name="my-room"),
    )
    print(room_info)
    results = await lkapi.room.list_rooms(api.ListRoomsRequest())
    print(results)
    await lkapi.aclose()

asyncio.run(main())
```

## Using Real-time SDK

```shell
$ pip install livekit
```

### Connecting to a room

```python
from livekit import rtc

async def main():
    room = rtc.Room()

    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logging.info(
            "participant connected: %s %s", participant.sid, participant.identity)

    async def receive_frames(stream: rtc.VideoStream):
        async for frame in video_stream:
            # received a video frame from the track, process it here
            pass

    # track_subscribed is emitted whenever the local participant is subscribed to a new track
    @room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        logging.info("track subscribed: %s", publication.sid)
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            video_stream = rtc.VideoStream(track)
            asyncio.ensure_future(receive_frames(video_stream))

    # By default, autosubscribe is enabled. The participant will be subscribed to
    # all published tracks in the room
    await room.connect(URL, TOKEN)
    logging.info("connected to room %s", room.name)

    # participants and tracks that are already available in the room
    # participant_connected and track_published events will *not* be emitted for them
    for participant in room.participants.items():
        for publication in participant.track_publications.items():
            print("track publication: %s", publication.sid)
```

### Sending and receiving chat

```python

room = rtc.Room()
...

chat = rtc.ChatManager(room)

# receiving chat
@chat.on("message_received")
def on_message_received(msg: rtc.ChatMessage):
    print(f"message received: {msg.participant.identity}: {msg.message}")

# sending chat
await chat.send_message("hello world")
```

## Examples

- [Facelandmark](https://github.com/livekit/python-sdks/tree/main/examples/face_landmark): Use mediapipe to detect face landmarks (eyes, nose ...)
- [Basic room](https://github.com/livekit/python-sdks/blob/main/examples/basic_room.py): Connect to a room
- [Publish hue](https://github.com/livekit/python-sdks/blob/main/examples/publish_hue.py): Publish a rainbow video track
- [Publish wave](https://github.com/livekit/python-sdks/blob/main/examples/publish_wave.py): Publish a sine wave

## Getting help / Contributing

Please join us on [Slack](https://livekit.io/join-slack) to get help from our devs / community members. We welcome your contributions(PRs) and details can be discussed there.

<!--BEGIN_REPO_NAV-->
<br/><table>
<thead><tr><th colspan="2">LiveKit Ecosystem</th></tr></thead>
<tbody>
<tr><td>Realtime SDKs</td><td><a href="https://github.com/livekit/components-js">React Components</a> · <a href="https://github.com/livekit/client-sdk-js">Browser</a> · <a href="https://github.com/livekit/components-swift">Swift Components</a> · <a href="https://github.com/livekit/client-sdk-swift">iOS/macOS/visionOS</a> · <a href="https://github.com/livekit/client-sdk-android">Android</a> · <a href="https://github.com/livekit/client-sdk-flutter">Flutter</a> · <a href="https://github.com/livekit/client-sdk-react-native">React Native</a> · <a href="https://github.com/livekit/rust-sdks">Rust</a> · <a href="https://github.com/livekit/node-sdks">Node.js</a> · <b>Python</b> · <a href="https://github.com/livekit/client-sdk-unity-web">Unity (web)</a> · <a href="https://github.com/livekit/client-sdk-unity">Unity (beta)</a></td></tr><tr></tr>
<tr><td>Server APIs</td><td><a href="https://github.com/livekit/node-sdks">Node.js</a> · <a href="https://github.com/livekit/server-sdk-go">Golang</a> · <a href="https://github.com/livekit/server-sdk-ruby">Ruby</a> · <a href="https://github.com/livekit/server-sdk-kotlin">Java/Kotlin</a> · <b>Python</b> · <a href="https://github.com/livekit/rust-sdks">Rust</a> · <a href="https://github.com/agence104/livekit-server-sdk-php">PHP (community)</a></td></tr><tr></tr>
<tr><td>Agents Frameworks</td><td><a href="https://github.com/livekit/agents">Python</a> · <a href="https://github.com/livekit/agent-playground">Playground</a></td></tr><tr></tr>
<tr><td>Services</td><td><a href="https://github.com/livekit/livekit">LiveKit server</a> · <a href="https://github.com/livekit/egress">Egress</a> · <a href="https://github.com/livekit/ingress">Ingress</a> · <a href="https://github.com/livekit/sip">SIP</a></td></tr><tr></tr>
<tr><td>Resources</td><td><a href="https://docs.livekit.io">Docs</a> · <a href="https://github.com/livekit-examples">Example apps</a> · <a href="https://livekit.io/cloud">Cloud</a> · <a href="https://docs.livekit.io/home/self-hosting/deployment">Self-hosting</a> · <a href="https://github.com/livekit/livekit-cli">CLI</a></td></tr>
</tbody>
</table>
<!--END_REPO_NAV-->
