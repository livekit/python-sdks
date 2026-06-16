# LiveKit Python SDK Examples

This directory contains examples demonstrating various features of the LiveKit Python SDK.

## Prerequisites

Set the following environment variables:

```bash
export LIVEKIT_URL=ws://localhost:7880
export LIVEKIT_API_KEY=devkey
export LIVEKIT_API_SECRET=secret
```

## Examples Overview

| Example | Description |
|---------|-------------|
| [basic_room.py](#basic_roompy) | Room connection with PlatformAudio and synthetic audio modes |
| [room_example.py](#room_examplepy) | Basic room connection and event handling |
| [api.py](#apipy) | Room management via LiveKit API |
| [e2ee.py](#e2eepy) | End-to-end encryption demo |
| [rpc.py](#rpcpy) | Remote Procedure Call between participants |
| [multiple_connections.py](#multiple_connectionspy) | Sequential connections for sync frameworks |
| [participant_attributes.py](#participant_attributespy) | Dynamic participant attributes |
| [publish_wave.py](#publish_wavepy) | Publish sine wave audio |
| [publish_hue.py](#publish_huepy) | Publish color-cycling video |
| [play_audio_stream.py](#play_audio_streampy) | Play received audio with sounddevice |
| [webhook.py](#webhookpy) | Webhook event handling |
| [agent_dispatch.py](#agent_dispatchpy) | Manual agent dispatch |

### Subdirectories

| Directory | Description |
|-----------|-------------|
| [face_landmark/](face_landmark/) | Facial landmark detection using MediaPipe |
| [video-stream/](video-stream/) | Video/audio sync with AVSynchronizer |
| [data_tracks/](data_tracks/) | Data channel examples |
| [data-streams/](data-streams/) | Data streaming examples |
| [local_audio/](local_audio/) | Local audio capture with dB metering |

---

## basic_room.py

The most comprehensive example, demonstrating room connection with audio capabilities. It showcases two audio capture modes that can be used independently or combined.

### Quick Start

```bash
# List available audio devices
python basic_room.py --list-devices

# Connect with PlatformAudio (recommended)
python basic_room.py --platform-audio --room my-room

# Connect with specific devices
python basic_room.py --platform-audio --mic-id "device-guid" --speaker-id "device-guid"

# Publish a WAV file
python basic_room.py --file audio.wav --room my-room

# Mix microphone + WAV file (both modes together)
python basic_room.py --platform-audio --file background.wav --room my-room
```

### Audio Modes

#### PlatformAudio Mode (`--platform-audio`)

Uses WebRTC's Audio Device Module (ADM) for microphone capture. **Recommended for most applications.**

**Features:**
- Built-in voice processing:
  - **Echo Cancellation (AEC)** - removes echo from speaker playback
  - **Noise Suppression (NS)** - reduces background noise
  - **Auto Gain Control (AGC)** - normalizes audio levels
- Hardware-accelerated processing on supported platforms (e.g., iOS VPIO)
- Automatic speaker playout for received audio
- Device enumeration and selection
- No external audio libraries required

**Limitations:**
- No direct access to raw audio frames (ADM sends directly to WebRTC)
- Cannot apply custom audio processing before publishing

```python
platform_audio = rtc.PlatformAudio()
source = platform_audio.create_audio_source(
    rtc.PlatformAudioOptions(
        echo_cancellation=True,
        noise_suppression=True,
        auto_gain_control=True,
    )
)
track = rtc.LocalAudioTrack.create_audio_track("microphone", source)
```

#### Synthetic Mode (Default)

Manual control over audio frames via `AudioSource.capture_frame()`. Use this for custom audio processing or programmatic audio generation.

**Features:**
- Full control over audio data
- Access to raw audio frames for custom processing
- Generate synthetic audio (files, TTS, audio synthesis)
- Apply custom filters, effects, or ML models

**Limitations:**
- No built-in AEC/NS/AGC - implement yourself or use `AudioProcessingModule`
- Must handle speaker playout manually via `AudioStream`
- Requires external audio libraries for mic capture (sounddevice, pyaudio)

```python
source = rtc.AudioSource(sample_rate=48000, num_channels=1)
track = rtc.LocalAudioTrack.create_audio_track("audio", source)

frame = rtc.AudioFrame(data=audio_bytes, sample_rate=48000, ...)
await source.capture_frame(frame)
```

#### Mixing Both Modes

PlatformAudio and Synthetic modes can run simultaneously. The `--file` option demonstrates this by publishing a WAV file (synthetic) alongside microphone capture (PlatformAudio).

```bash
python basic_room.py --platform-audio --file music.wav --room my-room
```

This creates two audio tracks:
1. **Microphone** - via PlatformAudio with voice processing
2. **File** - via synthetic mode from WAV

Use cases: background music while speaking, sound effects, mixing pre-recorded audio with live input.

### Command Line Options

| Option | Description |
|--------|-------------|
| `--list-devices` | List available audio devices and exit |
| `--platform-audio` | Use PlatformAudio for microphone (recommended) |
| `--file WAV_PATH` | Publish audio from WAV file (synthetic mode) |
| `--room NAME` | Room name (default: my-room) |
| `--mic-id ID` | Select microphone by device ID |
| `--speaker-id ID` | Select speaker by device ID |

### When to Use Each Mode

| Use Case | Mode |
|----------|------|
| Voice/video calls | PlatformAudio |
| Conferencing apps | PlatformAudio |
| Playing audio files | Synthetic |
| Text-to-speech | Synthetic |
| Custom audio processing | Synthetic |
| ML audio effects | Synthetic |
| Background music + voice | Both |

---

## local_audio/

Examples for local audio capture with microphone and speaker management.

### full_duplex.py

Full-duplex audio with microphone capture and speaker playout.

```bash
cd local_audio
python full_duplex.py
```

Features:
- Microphone capture via MediaDevices
- Speaker playout for received audio
- Real-time dB level metering

### publish_mic.py

Publish microphone audio with dB level monitoring.

```bash
cd local_audio
python publish_mic.py
```

Features:
- Microphone capture with AEC enabled
- Real-time dB level visualization

---

## room_example.py

Basic room connection demonstrating event handling and participant tracking.

```bash
python room_example.py
```

---

## api.py

Room management using the LiveKit API (create rooms, list rooms).

```bash
python api.py
```

---

## e2ee.py

End-to-end encryption with a rotating 3D cube visualization.

```bash
python e2ee.py
```

---

## rpc.py

Remote Procedure Call (RPC) between participants - greetings, math operations, timeout handling.

```bash
python rpc.py
```

---

## multiple_connections.py

Sequential room connections in a single thread. Useful for Django/Flask integration.

```bash
python multiple_connections.py
```

---

## participant_attributes.py

Set, update, and delete participant attributes dynamically.

```bash
python participant_attributes.py
```

---

## publish_wave.py

Publish a sine wave audio track at a specified frequency.

```bash
python publish_wave.py
```

---

## publish_hue.py

Publish a color-cycling animated video track.

```bash
python publish_hue.py
```

---

## play_audio_stream.py

Play incoming audio from remote participants using sounddevice.

```bash
pip install sounddevice
python play_audio_stream.py
```

---

## webhook.py

Handle LiveKit webhook events using aiohttp.

```bash
python webhook.py
```

---

## agent_dispatch.py

Manually dispatch agents to rooms (instead of automatic dispatch).

```bash
python agent_dispatch.py
```
