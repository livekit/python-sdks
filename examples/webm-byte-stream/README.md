# Stream intact WebM through LiveKit

Forward the original bytes of a WebM file or streaming HTTP response through
LiveKit's existing byte-stream API, with MIME type `video/webm`. WebM headers,
timestamps, compressed color, and alpha `BlockAdditional` data remain unchanged.
There is no demuxing, decoding, re-encoding, remuxing, or custom media format.
The publisher does not parse or validate the input; supply valid streaming WebM.

From the repository root (Python 3.10+, with the bundled FFI installed):

```sh
uv sync --dev
export LIVEKIT_URL=ws://localhost:7880
export LIVEKIT_API_KEY=devkey
export LIVEKIT_API_SECRET=secret
uv run python examples/webm-byte-stream/stream_webm.py input.webm \
  --room demo --recipient viewer
# input.webm can also be a streaming HTTP(S) URL.
```

The receiver must already be connected and have a `webm` byte-stream handler
registered before sending. The example checks participant presence, which does
not prove that its handler is ready. Applications need their own readiness flow.
Streams do not replay their beginning to participants who join midway; restart
from a suitable WebM initialization segment and keyframe for a new viewer.

Reads and awaited writes are incremental, using chunks of at most 15 KB. Chunk
boundaries need not align with WebM elements: concatenating the received chunks
reconstructs the original byte stream. HTTP reads have a five-second inactivity
timeout; a failed or cancelled transfer closes the writer with an error reason.
A file is sent as quickly as the transport allows; this is not a frame scheduler.
The receiver/player uses WebM timestamps for playout.

## Why a byte stream

LiveKit's pre-encoded media source takes codec access units. The standard
[VP9 RTP payload format](https://www.rfc-editor.org/rfc/rfc9628.html#section-4)
describes VP9 frame transport, not WebM container or alpha `BlockAdditional`
transport. Sending WebM as if it were a VP9 access unit would require a custom
receiver and transport convention. Changing the MIME type alone cannot add that
support to an ordinary WebRTC video track.

LiveKit's [byte streams](https://docs.livekit.io/transport/data/byte-streams/)
already support incremental arbitrary bytes. This example uses that existing
transport rather than inventing an RTP payload. It is a data stream, not a
published video media track: ordinary track attachment, media congestion feedback,
and automatic video subscription do not apply. Byte streams use reliable delivery;
loss recovery can delay later bytes and increase latency. LiveKit's lossy data
tracks are not interchangeable: dropping arbitrary WebM chunks corrupts the stream.

## Future playback

A client handler must feed incoming bytes into a streaming media player. On the
web, the intended path is Media Source Extensions with a compatible WebM byte
stream; see the [WebM byte-stream specification](https://www.w3.org/TR/mse-byte-stream-format-webm/).
This preserves the possibility of native alpha composition without an
application-side decode/re-encode step. An arbitrary WebM file is not necessarily
MSE-compatible, and file playback support does not prove streaming alpha support.
Browser/mobile playback, alpha support, buffering, and latency need platform tests.
No client playback adapter is implemented in this example.
