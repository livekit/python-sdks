# Local Video Packet-Trailer Examples

These desktop examples show how to publish a local camera track and attach packet-trailer frame metadata from Python.

## Setup

```bash
export LIVEKIT_URL=https://your-livekit-host
export LIVEKIT_API_KEY=your-api-key
export LIVEKIT_API_SECRET=your-api-secret
```

Run these examples from the repository root with `uv run --project examples/local_video`.
LiveKit connection settings can also be passed with `--url`, `--api-key`, and `--api-secret`.

## Publisher

Publish a camera track:

```bash
uv run --project examples/local_video python examples/local_video/publisher.py \
  --room-name demo \
  --identity py-cam \
  --camera-index 0
```

Attach packet-trailer metadata:

```bash
uv run --project examples/local_video python examples/local_video/publisher.py \
  --room-name demo \
  --identity py-cam \
  --attach-timestamp \
  --attach-frame-id
```

Useful flags:

- `--camera-index <n>`: OpenCV camera index to publish.
- `--width <px>` / `--height <px>`: requested camera resolution.
- `--fps <n>`: requested publish frame rate.
- `--attach-timestamp`: attach wall-clock microseconds since Unix epoch as `FrameMetadata.user_timestamp`.
- `--attach-frame-id`: attach a monotonically increasing `FrameMetadata.frame_id`.

## Subscriber

Render the first video track in the room:

```bash
uv run --project examples/local_video python examples/local_video/subscriber.py \
  --room-name demo \
  --identity py-viewer
```

Display packet-trailer metadata over the video:

```bash
uv run --project examples/local_video python examples/local_video/subscriber.py \
  --room-name demo \
  --identity py-viewer \
  --display-timestamp
```

Use `--participant py-cam` to only subscribe to video from a specific participant identity.

Press `q` in the video window or `Ctrl+C` in the terminal to exit.
