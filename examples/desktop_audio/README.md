# Publish desktop audio with PocketStation

Publish one running application, the complete desktop output mix, or a
microphone as a LiveKit audio track. PocketStation captures the local source;
LiveKit publishes it to the room.

## Install

Use Python 3.11 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set the credentials for a LiveKit Cloud project or self-hosted server:

```bash
export LIVEKIT_URL="wss://your-project.livekit.cloud"
export LIVEKIT_API_KEY="your-api-key"
export LIVEKIT_API_SECRET="your-api-secret"
```

## Publish one application

Start the application and make sure it is producing audio. Replace `Zoom`
with its display name or application identifier:

```bash
python publish.py --application Zoom
```

Join the `desktop-audio` room from another participant to receive the
`application-audio` track. PocketStation fails before capture begins if the
selection matches no application or more than one application.

## Other inputs

Capture every sound playing through the desktop:

```bash
python publish.py --system-audio
```

Capture the default microphone:

```bash
python publish.py --microphone
```

Microphone capture is never enabled automatically. This example publishes raw
microphone audio without echo cancellation, noise suppression, or automatic
gain control. Use LiveKit `PlatformAudio` when an interactive call needs those
voice-processing features.

Pass `--room NAME` to use another room. Pass `--duration 30` for a finite run;
otherwise press Control-C to stop. PocketStation stops capture and drains
accepted frames before LiveKit disconnects.

## How it works

PocketStation captures 48 kHz audio in 10 ms frames. A PocketStation Connector
downmixes each source frame to mono PCM16 and publishes it through a LiveKit
`AudioSource` with a 100 ms queue. Provider delivery runs outside the
operating-system audio callback, so a slow room connection does not block
native capture.

Application and system-audio tracks use LiveKit's
`SOURCE_SCREENSHARE_AUDIO` classification. The explicit microphone option uses
`SOURCE_MICROPHONE`.

The example uses PocketStation `0.1.4`, LiveKit `1.1.17`, and LiveKit API
`1.2.1` from PyPI. Platform permissions and native prerequisites are
documented in the [PocketStation platform guide](https://github.com/pocketstation-io/sdk-python/blob/main/docs/operations/platform-support.md).

Run the conversion test without connecting to a room:

```bash
python -m unittest discover tests
```
