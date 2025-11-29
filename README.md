<!--BEGIN_BANNER_IMAGE-->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="/.github/banner_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="/.github/banner_light.png">
  <img style="width:100%;" alt="The LiveKit icon, the name of the repository and some sample code in the background." src="https://raw.githubusercontent.com/livekit/python-sdks/main/.github/banner_light.png">
</picture>

<!--END_BANNER_IMAGE-->

[![pypi-v](https://img.shields.io/pypi/v/livekit.svg?label=livekit)](https://pypi.org/project/livekit/)
[![pypi-v](https://img.shields.io/pypi/v/livekit-api.svg?label=livekit-api)](https://pypi.org/project/livekit-api/)

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
token = api.AccessToken() \
    .with_identity("python-bot") \
    .with_name("Python Bot") \
    .with_grants(api.VideoGrants(
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
    lkapi = api.LiveKitAPI("https://my-project.livekit.cloud")
    room_info = await lkapi.room.create_room(
        api.CreateRoomRequest(name="my-room"),
    )
    print(room_info)
    results = await lkapi.room.list_rooms(api.ListRoomsRequest())
    print(results)
    await lkapi.aclose()

asyncio.run(main())
```

### Using other APIs

Services can be accessed via the LiveKitAPI object.

```python
lkapi = api.LiveKitAPI("https://my-project.livekit.cloud")

# Room Service
room_svc = lkapi.room

# Egress Service
egress_svc = lkapi.egress

# Ingress Service
ingress_svc = lkapi.ingress

# Sip Service
sip_svc = lkapi.sip

# Agent Dispatch
dispatch_svc = lkapi.agent_dispatch

# Connector Service
connector_svc = lkapi.connector
```

## Using Real-time SDK

```shell
$ pip install livekit
```

### Connecting to a room

see [room_example](examples/room_example.py) for full example

```python
from livekit import rtc

async def main():
    room = rtc.Room()

    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logging.info(
            "participant connected: %s %s", participant.sid, participant.identity)

    async def receive_frames(stream: rtc.VideoStream):
        async for frame in stream:
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
    for identity, participant in room.remote_participants.items():
        print(f"identity: {identity}")
        print(f"participant: {participant}")
        for tid, publication in participant.track_publications.items():
            print(f"\ttrack id: {publication}")
```

### RPC

Perform your own predefined method calls from one participant to another.

This feature is especially powerful when used with [Agents](https://docs.livekit.io/agents), for instance to forward LLM function calls to your client application.

#### Registering an RPC method

The participant who implements the method and will receive its calls must first register support:

```python
@room.local_participant.register_rpc_method("greet")
async def handle_greet(data: RpcInvocationData):
    print(f"Received greeting from {data.caller_identity}: {data.payload}")
    return f"Hello, {data.caller_identity}!"
```

In addition to the payload, your handler will also receive `response_timeout`, which informs you the maximum time available to return a response. If you are unable to respond in time, the call will result in an error on the caller's side.

#### Performing an RPC request

The caller may then initiate an RPC call like so:

```python
try:
  response = await room.local_participant.perform_rpc(
    destination_identity='recipient-identity',
    method='greet',
    payload='Hello from RPC!'
  )
  print(f"RPC response: {response}")
except Exception as e:
  print(f"RPC call failed: {e}")
```

You may find it useful to adjust the `response_timeout` parameter, which indicates the amount of time you will wait for a response. We recommend keeping this value as low as possible while still satisfying the constraints of your application.

## Using local media devices

The `MediaDevices` class provides a high-level interface for working with local audio input (microphone) and output (speakers) devices. It's built on top of the `sounddevice` library and integrates seamlessly with LiveKit's audio processing features.  In order to use `MediaDevices`, you must have the `sounddevice` library installed in your local Python environment, if it's not available, `MediaDevices` will not work.

### Capturing microphone input

```python
from livekit import rtc

# Create a MediaDevices instance
devices = rtc.MediaDevices()

# Open the default microphone with audio processing enabled
mic = devices.open_input(
    enable_aec=True,          # Acoustic Echo Cancellation
    noise_suppression=True,   # Noise suppression
    high_pass_filter=True,    # High-pass filter
    auto_gain_control=True    # Automatic gain control
)

# Use the audio source to create a track and publish it
track = rtc.LocalAudioTrack.create_audio_track("microphone", mic.source)
await room.local_participant.publish_track(track)

# Clean up when done
await mic.aclose()
```

### Playing audio to speakers

```python
# Open the default output device
player = devices.open_output()

# Add remote audio tracks to the player (typically in a track_subscribed handler)
@room.on("track_subscribed")
def on_track_subscribed(track: rtc.Track, publication, participant):
    if track.kind == rtc.TrackKind.KIND_AUDIO:
        player.add_track(track)

# Start playback (mixes all added tracks)
await player.start()

# Clean up when done
await player.aclose()
```

### Full duplex audio (microphone + speakers)

For full duplex audio with echo cancellation, open the input device first (with AEC enabled), then open the output device. The output player will automatically feed the APM's reverse stream for effective echo cancellation:

```python
devices = rtc.MediaDevices()

# Open microphone with AEC
mic = devices.open_input(enable_aec=True)

# Open speakers - automatically uses the mic's APM for echo cancellation
player = devices.open_output()

# Publish microphone
track = rtc.LocalAudioTrack.create_audio_track("mic", mic.source)
await room.local_participant.publish_track(track)

# Add remote tracks and start playback
player.add_track(remote_audio_track)
await player.start()
```

### Listing available devices

```python
devices = rtc.MediaDevices()

# List input devices
input_devices = devices.list_input_devices()
for device in input_devices:
    print(f"{device['index']}: {device['name']}")

# List output devices  
output_devices = devices.list_output_devices()
for device in output_devices:
    print(f"{device['index']}: {device['name']}")

# Get default device indices
default_input = devices.default_input_device()
default_output = devices.default_output_device()
```

See [publish_mic.py](examples/local_audio/publish_mic.py) and [full_duplex.py](examples/local_audio/full_duplex.py) for complete examples.


#### Errors

LiveKit is a dynamic realtime environment and calls can fail for various reasons.

You may throw errors of the type `RpcError` with a string `message` in an RPC method handler and they will be received on the caller's side with the message intact. Other errors will not be transmitted and will instead arrive to the caller as `1500` ("Application Error"). Other built-in errors are detailed in `RpcError`.

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
<tr><td>LiveKit SDKs</td><td><a href="https://github.com/livekit/client-sdk-js">Browser</a> · <a href="https://github.com/livekit/client-sdk-swift">iOS/macOS/visionOS</a> · <a href="https://github.com/livekit/client-sdk-android">Android</a> · <a href="https://github.com/livekit/client-sdk-flutter">Flutter</a> · <a href="https://github.com/livekit/client-sdk-react-native">React Native</a> · <a href="https://github.com/livekit/rust-sdks">Rust</a> · <a href="https://github.com/livekit/node-sdks">Node.js</a> · <b>Python</b> · <a href="https://github.com/livekit/client-sdk-unity">Unity</a> · <a href="https://github.com/livekit/client-sdk-unity-web">Unity (WebGL)</a> · <a href="https://github.com/livekit/client-sdk-esp32">ESP32</a></td></tr><tr></tr>
<tr><td>Server APIs</td><td><a href="https://github.com/livekit/node-sdks">Node.js</a> · <a href="https://github.com/livekit/server-sdk-go">Golang</a> · <a href="https://github.com/livekit/server-sdk-ruby">Ruby</a> · <a href="https://github.com/livekit/server-sdk-kotlin">Java/Kotlin</a> · <b>Python</b> · <a href="https://github.com/livekit/rust-sdks">Rust</a> · <a href="https://github.com/agence104/livekit-server-sdk-php">PHP (community)</a> · <a href="https://github.com/pabloFuente/livekit-server-sdk-dotnet">.NET (community)</a></td></tr><tr></tr>
<tr><td>UI Components</td><td><a href="https://github.com/livekit/components-js">React</a> · <a href="https://github.com/livekit/components-android">Android Compose</a> · <a href="https://github.com/livekit/components-swift">SwiftUI</a> · <a href="https://github.com/livekit/components-flutter">Flutter</a></td></tr><tr></tr>
<tr><td>Agents Frameworks</td><td><a href="https://github.com/livekit/agents">Python</a> · <a href="https://github.com/livekit/agents-js">Node.js</a> · <a href="https://github.com/livekit/agent-playground">Playground</a></td></tr><tr></tr>
<tr><td>Services</td><td><a href="https://github.com/livekit/livekit">LiveKit server</a> · <a href="https://github.com/livekit/egress">Egress</a> · <a href="https://github.com/livekit/ingress">Ingress</a> · <a href="https://github.com/livekit/sip">SIP</a></td></tr><tr></tr>
<tr><td>Resources</td><td><a href="https://docs.livekit.io">Docs</a> · <a href="https://github.com/livekit-examples">Example apps</a> · <a href="https://livekit.io/cloud">Cloud</a> · <a href="https://docs.livekit.io/home/self-hosting/deployment">Self-hosting</a> · <a href="https://github.com/livekit/livekit-cli">CLI</a></td></tr>
</tbody>
</table>
<!--END_REPO_NAV-->
