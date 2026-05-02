# Wake Word Agent Dispatch Example

This example keeps a local microphone track published from launch, listens for a wake word on
that same microphone stream, dispatches a named LiveKit agent, and sends the pre-connect audio
buffer to the first active agent participant. A companion `agent.py` provides a minimal voice
assistant that ends its session when the user says `bye bye`.

The example also keeps a short local preroll buffer so the pre-connect payload includes the wake
word audio spoken before `LocalAudioTrack.start_preconnect_buffer()` could be called.

## Requirements

- Python 3.11 or newer
- A microphone
- A LiveKit project with an agent registered using `agent_name`
- A wake word ONNX model, such as `hey_livekit.onnx`

Install the example dependencies from this directory:

```bash
cd examples/wakeword_agent_dispatch
uv sync --python 3.11
```

On macOS, `sounddevice` may require PortAudio:

```bash
brew install portaudio
```

On Ubuntu or Debian:

```bash
sudo apt install portaudio19-dev
```

## Configuration

Set your LiveKit credentials and point the example at your wake word model:

```bash
export LIVEKIT_URL="wss://your-project.livekit.cloud"
export LIVEKIT_API_KEY="..."
export LIVEKIT_API_SECRET="..."
export LIVEKIT_ROOM="wakeword-preconnect"
export LIVEKIT_AGENT_NAME="test-agent"
export LIVEKIT_WAKEWORD_MODEL="./models/hey_livekit.onnx"
```

Optional settings:

```bash
export LIVEKIT_WAKEWORD_NAME="hey_livekit"
export LIVEKIT_WAKEWORD_THRESHOLD="0.5"
export LIVEKIT_WAKEWORD_PREROLL_SECONDS="2.0"
export LIVEKIT_PRECONNECT_BUFFER_SECONDS="10.0"
export LIVEKIT_AGENT_METADATA=""
export LIVEKIT_AGENT_WAIT_TIMEOUT="30.0"
export LIVEKIT_AGENT_JOIN_DELAY_SECONDS="2.0"
export LIVEKIT_AGENT_STT_MODEL="deepgram/nova-3"
export LIVEKIT_AGENT_LLM_MODEL="openai/gpt-4o-mini"
export LIVEKIT_AGENT_TTS_MODEL="cartesia/sonic-2"
```

## Run

Start the named agent in one process:

```bash
uv run python agent.py dev
```

Then start the wake word client in another process:

```bash
uv run python wakeword_agent_dispatch.py
```

The script connects to LiveKit, publishes the microphone track immediately, and waits for the
wake word. After detection, it dispatches `LIVEKIT_AGENT_NAME`, waits for an active agent
participant, sends the buffered wake word audio to that participant, and disables wake word
detection while the agent is active. When the agent ends its session, for example after the user
says `bye bye`, the client clears the pre-connect buffer and local audio state before returning
to idle wake word detection.

For testing the pre-connect buffer, `agent.py` waits `LIVEKIT_AGENT_JOIN_DELAY_SECONDS` seconds
before starting the room session. Set it to `0` to remove the artificial delay.
