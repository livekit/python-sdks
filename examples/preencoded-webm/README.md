# Pre-encoded WebM streaming

Publish VP8/VP9 WebM from a file or streaming HTTP(S) response using the Python
pre-encoded video source. PyAV only demuxes packets: there is no `decode`, raw
pixel conversion, or encoder in the publishing path. Audio is outside this example.

The WebM example requires Python 3.10+ and PyAV 16.1+ for packet side-data access.
The underlying pre-encoded SDK API also supports Python 3.9.

From the repository root (with the bundled FFI installed):

```sh
uv sync --dev
uv pip install -r examples/preencoded-webm/requirements.txt
export LIVEKIT_URL=ws://localhost:7880
export LIVEKIT_API_KEY=devkey
export LIVEKIT_API_SECRET=secret
.venv/bin/python examples/preencoded-webm/publish.py input.webm --room demo
# The input can also be an HTTP(S) URL producing a live WebM response.
```

Use WebM with a keyframe at the start, increasing timestamps, fixed dimensions,
and no B-frame reordering. The example supports VP8 and VP9; receiver codec/profile
support still matters. Reads run off the asyncio loop, one packet at a time, with
network timeouts and bounded probing so the first frame does not wait for EOF.
Presentation timestamps drive pacing, including variable frame-rate input. The
publisher waits up to 30 seconds for a subscriber and briefly repeats the initial
keyframe until the native encoder reports its first rate target (at most five
seconds). This avoids consuming the only keyframe of a short clip before encoder
initialization; it is not a general keyframe-recovery mechanism. At EOF the track
stays published until Ctrl-C, since capture acceptance is not a delivery or drain
acknowledgement.

The demuxer cannot satisfy a request for a new keyframe or lower bitrate; feedback
is logged and must be connected to an upstream encoder in a production integration.
Use short GOPs and an appropriate bitrate for a file demonstration. Late joiners
and packet loss may require waiting until the next keyframe. This example does not
provide adaptive encoding or a loss-recovery policy.

## Transparency and container-preserving transport

This example publishes opaque video as a standard VP8/VP9 media track. It removes
WebM container framing, so it rejects alpha and BlockAdditional side data instead
of silently losing them. It does not define a custom alpha payload or transport.

To preserve transparent WebM, carry its original bytes, including the WebM header,
track metadata, Clusters, and BlockAdditional elements. LiveKit's existing
[byte-stream API](https://docs.livekit.io/transport/data/byte-streams/) can carry
such bytes incrementally, but is a data stream rather than a video media track.
An ordinary VP9 RTP media track does not accept a WebM container as its payload.

A future client adapter could feed an intact WebM byte stream into native media
playback without application-side decoding or re-encoding. Streaming playback,
alpha support, and latency still need validation on each target browser/mobile
platform. The adjacent [WebM byte-stream example](../webm-byte-stream/) forwards the
container intact. No client playback adapter is included.

## Validation

```sh
uv run --with 'av>=16.1' pytest tests/rtc/test_encoded_video.py tests/rtc/test_webm_example.py
```

Tests generate synthetic WebM, verify unchanged compressed video bytes and
key/delta timestamps, reject alpha, read the first frame before a pipe or HTTP
response reaches EOF, and check startup and cancellation cleanup. The base API's
server-backed test publishes VP9 and verifies subscriber pixels.
