from __future__ import annotations

import ctypes
from dataclasses import replace
from typing import Any

import pytest

from livekit import rtc
from livekit.rtc import encoded_video
from livekit.rtc._proto import ffi_pb2 as proto_ffi


# A 16x16 red VP9 keyframe generated with libvpx-vp9, yuv420p, realtime.
VP9_KEYFRAME = bytes.fromhex(
    "824983420000f000f60038241c184a00003060000010bffff4a3dffffff9c97fffffffbd840000"
)


def frame(**kwargs: Any) -> rtc.EncodedVideoFrame:
    return replace(
        rtc.EncodedVideoFrame(
            data=VP9_KEYFRAME,
            width=16,
            height=16,
            codec=rtc.VideoCodec.VP9,
            frame_type=rtc.EncodedFrameType.ENCODED_FRAME_KEY,
            timestamp_us=123456,
        ),
        **kwargs,
    )


@pytest.mark.parametrize("width,height", [(0, 16), (16, 0), (-1, 16)])
def test_invalid_dimensions(width: int, height: int) -> None:
    with pytest.raises(ValueError, match="dimensions"):
        frame(width=width, height=height)
    with pytest.raises(ValueError, match="dimensions"):
        rtc.EncodedVideoSource(width, height)


def test_empty_or_mutable_payload() -> None:
    with pytest.raises(ValueError, match="empty"):
        frame(data=b"")
    with pytest.raises(TypeError, match="bytes"):
        frame(data=bytearray(VP9_KEYFRAME))


@pytest.mark.parametrize("accepted", [True, False])
@pytest.mark.parametrize("metadata", [None, rtc.FrameMetadata(frame_id=7, user_timestamp=99)])
async def test_capture_ffi_contract(
    monkeypatch: pytest.MonkeyPatch, accepted: bool, metadata: rtc.FrameMetadata | None
) -> None:
    requests = []

    def request(self: Any, req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        requests.append(req)
        response = proto_ffi.FfiResponse()
        if req.HasField("new_video_source"):
            assert req.new_video_source.type == encoded_video.proto_video.VIDEO_SOURCE_ENCODED
            assert req.new_video_source.resolution.width == 16
            assert req.new_video_source.resolution.height == 16
            response.new_video_source.source.handle.id = 0
        else:
            capture = req.capture_encoded_video_frame
            # Read foreign memory during the synchronous call, while it must be valid.
            assert (
                ctypes.string_at(capture.buffer.data_ptr, capture.buffer.data_len) == VP9_KEYFRAME
            )
            assert capture.codec == rtc.VideoCodec.VP9
            assert capture.frame_type == rtc.EncodedFrameType.ENCODED_FRAME_KEY
            assert (capture.width, capture.height, capture.timestamp_us) == (16, 16, 123456)
            assert capture.HasField("metadata") == (metadata is not None)
            if metadata is not None:
                assert capture.metadata == metadata
            response.capture_encoded_video_frame.accepted = accepted
        return response

    monkeypatch.setattr(encoded_video.FfiClient, "request", request)
    source = rtc.EncodedVideoSource(16, 16)
    try:
        assert source.capture_frame(frame(metadata=metadata)) is accepted
        assert len(requests) == 2
    finally:
        await source.aclose()


@pytest.mark.parametrize("has_rate_control", [False, True])
async def test_feedback(monkeypatch: pytest.MonkeyPatch, has_rate_control: bool) -> None:
    source = rtc.EncodedVideoSource(16, 16)
    calls = 0

    def request(self: Any, req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        nonlocal calls
        assert req.take_encoded_video_source_feedback.source_handle == source._ffi_handle.handle
        result = proto_ffi.FfiResponse()
        feedback = result.take_encoded_video_source_feedback
        feedback.keyframe_requested = calls == 0
        if has_rate_control and calls == 0:
            feedback.rate_control.target_bitrate_bps = 123000
            feedback.rate_control.framerate_fps = 29.97
        calls += 1
        return result

    monkeypatch.setattr(encoded_video.FfiClient, "request", request)
    try:
        feedback = source.take_feedback()
        assert feedback.keyframe_requested
        assert feedback.rate_control == (
            rtc.EncodedRateControl(123000, 29.97) if has_rate_control else None
        )
        assert source.take_feedback() == rtc.EncodedVideoSourceFeedback(False, None)
    finally:
        await source.aclose()


async def test_native_source_lifecycle() -> None:
    # Exercise the shipped native FFI, not just serialization mocks.
    for _ in range(10):
        source = rtc.EncodedVideoSource(16, 16)
        try:
            track = rtc.LocalVideoTrack.create_video_track("encoded", source)
            assert track.kind == rtc.TrackKind.KIND_VIDEO
            assert isinstance(source.capture_frame(frame()), bool)
            assert source.take_feedback() == rtc.EncodedVideoSourceFeedback(False, None)
        finally:
            await source.aclose()
            await source.aclose()  # Closing is idempotent.
        assert source._ffi_handle.disposed
        del track


async def test_publish_preencoded_video() -> None:
    """A receiver decodes the access unit published through the real native FFI."""
    import asyncio
    import contextlib
    import os
    import time
    import uuid

    from livekit import api

    if not all(os.getenv(key) for key in ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")):
        pytest.skip("LiveKit server credentials are required")

    room_name = f"encoded-video-{uuid.uuid4().hex}"
    publisher, subscriber = rtc.Room(), rtc.Room()
    source = rtc.EncodedVideoSource(16, 16)
    subscribed: asyncio.Future[rtc.Track] = asyncio.get_running_loop().create_future()
    video_stream = None
    producer = None

    @subscriber.on("track_subscribed")
    def on_track(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        if not subscribed.done():
            subscribed.set_result(track)

    def token(identity: str) -> str:
        return (
            api.AccessToken()
            .with_identity(identity)
            .with_grants(api.VideoGrants(room_join=True, room=room_name))
            .to_jwt()
        )

    try:
        await subscriber.connect(os.environ["LIVEKIT_URL"], token("subscriber"))
        await publisher.connect(os.environ["LIVEKIT_URL"], token("publisher"))
        track = rtc.LocalVideoTrack.create_video_track("preencoded", source)
        await publisher.local_participant.publish_track(
            track,
            rtc.TrackPublishOptions(
                video_codec=rtc.VideoCodec.VP9,
                video_encoder=rtc.VideoEncoderBackend.ENCODER_BACKEND_PRE_ENCODED,
                simulcast=False,
            ),
        )
        remote = await asyncio.wait_for(subscribed, 10)
        video_stream = rtc.VideoStream(remote, format=rtc.VideoBufferType.RGBA)

        async def send() -> None:
            while True:
                source.capture_frame(frame(timestamp_us=time.monotonic_ns() // 1000))
                await asyncio.sleep(0.04)

        producer = asyncio.create_task(send())
        received = await asyncio.wait_for(video_stream.__anext__(), 10)
        assert (received.frame.width, received.frame.height) == (16, 16)
        red, green, blue, alpha = received.frame.data[:4]
        assert red > 200 and green < 50 and blue < 50 and alpha == 255
    finally:
        if producer is not None:
            producer.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await producer
        if video_stream is not None:
            await video_stream.aclose()
        await publisher.disconnect()
        await subscriber.disconnect()
        await source.aclose()
