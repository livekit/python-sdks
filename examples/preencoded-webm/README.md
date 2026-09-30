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

## Experimental single-track alpha transport

**This is a backend wire-format prototype, not interoperable transparent WebRTC.**
Opaque publishing works with existing VP8/VP9 receivers. Alpha mode must only be
used with matching test receivers in an isolated room; an ordinary browser/mobile
LiveKit video track does not recognize the additional data. No browser or mobile
playback adapter is implemented here.

By default, the demuxer rejects alpha WebM instead of silently dropping its alpha.
To opt into the experimental VP9 envelope:

```sh
.venv/bin/python examples/preencoded-webm/publish.py transparent.webm \
  --room alpha-experiment --experimental-alpha
```

The prototype extracts the VP9 color access unit and the separately compressed
alpha access unit from WebM `BlockAdditional` with `BlockAddID=1`. It publishes both
inside **one encoded-frame payload on one media track**, sharing one frame type,
timestamp, and RTP frame boundary. There is no second track or data channel.
The native passthrough encoder forwards the bytes, and normal RTP packetization
can split them across multiple packets.

The provisional payload is:

```text
[color access unit][alpha access unit]
[color length: u32 big endian][alpha length: u32 big endian]["LKWA"][version: u8 = 1]
```

`LKWA` and version 1 are local proposal values, not an assigned LiveKit format.
Lengths exclude the 13-byte footer. Both components must be nonempty and the
entire payload must be at most 16 MiB in this example. A receiver validates the
footer and sizes after RTP reassembly, then extracts the original compressed
components **before** handing anything to an ordinary VP9 decoder. The included
`unpack_alpha` function specifies that byte contract; it is not a video renderer.
Sparse/reused alpha blocks and dimension changes are not supported. A WebM
keyframe must contain independently decodable color and alpha components.

This deliberately does not overload LiveKit's `FrameMetadata.user_data`: the
native LKTS trailer has a one-byte length and a maximum total size of 255 bytes,
while alpha access units can be many kilobytes. The media envelope precedes any
native metadata trailer. Combining it with frame metadata or E2EE needs separate
interoperability testing; this example does not enable either.

### Required before this could become a supported feature

- Agree on a versioned transport profile with LiveKit maintainers. The example's
  track name identifies a prototype; it does **not** negotiate receiver support.
- Add capability signaling and enforce it for every subscriber, including late
  joins. Unsupported receivers must be rejected or explicitly offered an opaque
  fallback. Today's server does not strip this custom alpha envelope for them.
- Implement a receiver path for each target platform. A browser adapter could
  investigate remuxing compressed color and alpha into WebM for native playback;
  browser/MSE alpha support and latency must be tested. Native mobile SDKs need
  their own supported decode/playback path. No cross-platform guarantee follows
  from successful byte transport.
- Validate loss/reordering/retransmission, congestion feedback, keyframe recovery,
  codec profiles, resource limits, metadata, encryption, and reconnection.

These are interoperability requirements, not additional Python encoder settings.
Keep the alpha mode experimental until they are resolved.

## Validation

```sh
uv run --with 'av>=16.1' pytest tests/rtc/test_encoded_video.py tests/rtc/test_webm_example.py
```

Tests generate synthetic alpha WebM, verify unchanged compressed payloads and
key/delta timestamps, read the first frame before a pipe reaches EOF, reject
malformed/oversized envelopes, and check cancellation joins the active demux read.
The base API's server-backed test publishes VP9 and verifies subscriber pixels.

A separate local transport probe used Python FFI 0.12.80, LiveKit server 1.13.7,
and a Go SDK 2.18.1 subscriber to reassemble RTP without decoding. A 37,630-byte
compound frame (27,578 color bytes, 10,039 alpha bytes, 13-byte footer) crossed the
server in 33 RTP packets with identical SHA-256 before and after. This demonstrates
transport through the tested stack; it does not validate an alpha player or
compatibility with every LiveKit deployment.
