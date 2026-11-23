# LiveKit SDK for Python

Python SDK to integrate LiveKit's real-time video, audio, and data capabilities into your Python applications using WebRTC. Designed for use with [LiveKit Agents](https://github.com/livekit/agents) to build powerful voice AI apps.

See https://docs.livekit.io/ for more information.

## Publishing prepared tracks during connection

Create a track backed by an empty source and supply its complete publication options
when connecting. Audio generation can run concurrently; no PCM or capture device is
needed to prepare the publication.

```python
from livekit import rtc

source = rtc.AudioSource(sample_rate=24000, num_channels=1)
track = rtc.LocalAudioTrack.create_audio_track("agent_audio", source)
options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
await room.connect(url, token, rtc.RoomOptions(publish_tracks=[(track, options)]))
publication = next(p for p in room.local_participant.track_publications.values()
                   if p.track is track)
# Push generated audio later with await source.capture_frame(frame).
# At shutdown:
await room.local_participant.unpublish_track(publication.sid)
await source.aclose()
```

Single-PC connections can bundle these publications into JOIN on supporting servers;
other configurations use ordinary publication. Do not publish the supplied tracks
again after connect. This requires the matching native FFI build. Cancellation waits
for the native connection attempt to finish and cleans up any unclaimed room.

## Publishing pre-encoded video

Use `EncodedVideoSource` when an upstream encoder already provides compressed
frames. The source uses the same native passthrough encoder as the Rust SDK;
Python does not decode or re-encode the video.

```python
from livekit import rtc

source = rtc.EncodedVideoSource(width=640, height=360)
track = rtc.LocalVideoTrack.create_video_track("camera", source)
await room.local_participant.publish_track(
    track,
    rtc.TrackPublishOptions(
        video_codec=rtc.VideoCodec.VP9,
        video_encoder=rtc.VideoEncoderBackend.ENCODER_BACKEND_PRE_ENCODED,
        simulcast=False,
    ),
)
# Supply each complete encoded frame at its playback time.
source.capture_frame(rtc.EncodedVideoFrame(
    data=encoded_vp9_frame,
    width=640,
    height=360,
    codec=rtc.VideoCodec.VP9,
    frame_type=rtc.EncodedFrameType.ENCODED_FRAME_KEY,
    timestamp_us=capture_timestamp_us,
))
feedback = source.take_feedback()
# Forward feedback.keyframe_requested and feedback.rate_control to your encoder.
# At shutdown, unpublish the track and release the source:
await room.local_participant.unpublish_track(track.sid)
await source.aclose()
```

Supported codecs are H.264, H.265, VP8, VP9 and AV1, subject to receiver support.
Submit complete access units (Annex B for H.264/H.265), not WebM/MP4 container
bytes or RTP packets. A container must first be demuxed; demuxing extracts
compressed frames and does not reconstruct pixels. The codec must match the
publication and stay fixed, and simulcast must be disabled.

The caller controls pacing and handles keyframe and bitrate feedback. In
particular, a prerecorded file cannot generate a new keyframe on demand for a
late subscriber or after packet loss. WebM's auxiliary alpha data is not part of
the VP9 color access unit and is not transported by this API.
