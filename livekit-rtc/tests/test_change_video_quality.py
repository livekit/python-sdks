"""End-to-end Test for simulcast video quality layers.

The test publishes a 1280x720 simulcast video track (rolling colored bars) using
both VP8 and H264 codecs, and on the receiver side verifies that subscribing to
each simulcast quality layer (HIGH=f, MEDIUM=h, LOW=q) yields frames of the
expected resolution.

Requires the following environment variables to run:
    LIVEKIT_URL
    LIVEKIT_API_KEY
    LIVEKIT_API_SECRET
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid
from typing import Callable, Optional, Tuple

import numpy as np
import pytest

from livekit import api, rtc
from livekit.rtc._proto.track_publication_pb2 import VideoQuality
from livekit.rtc.room import EventTypes


WAIT_TIMEOUT = 30.0
WAIT_INTERVAL = 0.1
PUBLISH_WIDTH = 1280
PUBLISH_HEIGHT = 720
PUBLISH_FPS = 15

# Default simulcast layer dimensions for a 720p source publication.
LAYER_DIMENSIONS = {
    "f": (1280, 720),
    "h": (640, 360),
    "q": (320, 180),
}

QUALITY_SEQUENCE = [
    (VideoQuality.VIDEO_QUALITY_HIGH, "f"),
    (VideoQuality.VIDEO_QUALITY_MEDIUM, "h"),
    (VideoQuality.VIDEO_QUALITY_LOW, "q"),
]


def skip_if_no_credentials():
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    return pytest.mark.skipif(
        bool(missing), reason=f"Missing environment variables: {', '.join(missing)}"
    )


def create_token(identity: str, room_name: str) -> str:
    return (
        api.AccessToken()
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        .to_jwt()
    )


def unique_room_name(base: str) -> str:
    return f"{base}-{uuid.uuid4().hex[:8]}"


async def _wait_until(
    predicate: Callable[[], bool],
    *,
    timeout: float = WAIT_TIMEOUT,
    interval: float = WAIT_INTERVAL,
    message: str = "condition not met",
) -> None:
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return
        await asyncio.sleep(interval)
    raise AssertionError(f"timeout waiting: {message}")


async def _ensure_all_connected(rooms: list[rtc.Room]) -> None:
    await _wait_until(
        lambda: all(r.connection_state == rtc.ConnectionState.CONN_CONNECTED for r in rooms),
        message="not all rooms reached CONN_CONNECTED",
    )


async def _ensure_track_subscribed(room: rtc.Room, track_sid: str) -> rtc.RemoteTrackPublication:
    holder: dict[str, rtc.RemoteTrackPublication] = {}

    def _has_subscribed() -> bool:
        for participant in room.remote_participants.values():
            pub = participant.track_publications.get(track_sid)
            if pub is not None and pub.subscribed and pub.track is not None:
                holder["pub"] = pub
                return True
        return False

    await _wait_until(
        _has_subscribed,
        message=f"room did not subscribe to track {track_sid}",
    )
    return holder["pub"]


def _expect_event(
    room: rtc.Room,
    event: EventTypes,
    predicate: Optional[Callable[..., bool]] = None,
) -> asyncio.Future:
    loop = asyncio.get_event_loop()
    fut: asyncio.Future = loop.create_future()

    def _on_event(*args, **kwargs) -> None:
        if fut.done():
            return
        if predicate is None or predicate(*args, **kwargs):
            fut.set_result(args)

    room.on(event, _on_event)
    return fut


async def _await_event(fut: asyncio.Future, timeout: float = WAIT_TIMEOUT) -> None:
    try:
        await asyncio.wait_for(fut, timeout=timeout)
    except asyncio.TimeoutError as e:
        raise AssertionError("timed out waiting for event") from e


def _make_rolling_i420(width: int, height: int, t: float) -> rtc.VideoFrame:
    """Build a 1280x720 I420 frame containing 8 vertical color bars that scroll
    horizontally over time, so the encoder always sees motion."""
    bar_w = max(width // 8, 1)
    offset = int(t * 240) % bar_w

    cols_y = np.arange(width, dtype=np.int32)
    bar_idx_y = ((cols_y + offset) // bar_w) % 8
    y_row = (bar_idx_y * 28 + 32).astype(np.uint8)

    cw = width // 2
    cols_c = np.arange(cw, dtype=np.int32)
    bar_idx_c = (((cols_c * 2) + offset) // bar_w) % 8
    u_row = (bar_idx_c * 18 + 80).astype(np.uint8)
    v_row = (220 - bar_idx_c * 18).astype(np.uint8)

    y_plane = np.tile(y_row, (height, 1))
    u_plane = np.tile(u_row, (height // 2, 1))
    v_plane = np.tile(v_row, (height // 2, 1))

    data = np.concatenate([y_plane.ravel(), u_plane.ravel(), v_plane.ravel()])
    return rtc.VideoFrame(width, height, rtc.VideoBufferType.I420, data.tobytes())


async def _publish_loop(source: rtc.VideoSource, stop: asyncio.Event) -> None:
    interval = 1.0 / PUBLISH_FPS
    start = time.monotonic()
    while not stop.is_set():
        t = time.monotonic() - start
        frame = _make_rolling_i420(PUBLISH_WIDTH, PUBLISH_HEIGHT, t)
        source.capture_frame(frame)
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass


async def _wait_for_layer(
    stream: rtc.VideoStream,
    expected_w: int,
    expected_h: int,
    *,
    timeout: float = 20.0,
    samples: int = 5,
    tolerance: float = 0.20,
) -> Tuple[int, int]:
    """Drain frames until we observe `samples` consecutive frames whose
    dimensions match the expected layer (within `tolerance`)."""
    deadline = asyncio.get_event_loop().time() + timeout
    matches = 0
    last: Optional[Tuple[int, int]] = None
    iterator = stream.__aiter__()
    while asyncio.get_event_loop().time() < deadline:
        try:
            ev = await asyncio.wait_for(iterator.__anext__(), timeout=2.0)
        except asyncio.TimeoutError:
            continue
        except StopAsyncIteration:
            break
        w, h = ev.frame.width, ev.frame.height
        last = (w, h)
        if (
            abs(w - expected_w) / expected_w <= tolerance
            and abs(h - expected_h) / expected_h <= tolerance
        ):
            matches += 1
            if matches >= samples:
                return last
        else:
            matches = 0
    raise AssertionError(
        f"timed out waiting for ~{expected_w}x{expected_h}, last seen={last}"
    )


@skip_if_no_credentials()
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "video_codec, codec_name",
    [
        (rtc.VideoCodec.VP8, "vp8"),
        (rtc.VideoCodec.H264, "h264"),
    ],
)
async def test_simulcast_quality_layers(
    video_codec: rtc.VideoCodec.ValueType, codec_name: str
) -> None:
    room_name = unique_room_name(f"py-simulcast-{codec_name}")
    url = os.environ["LIVEKIT_URL"]

    sender, receiver = rtc.Room(), rtc.Room()
    await sender.connect(url, create_token("sender", room_name))
    await receiver.connect(url, create_token("receiver", room_name))
    await _ensure_all_connected([sender, receiver])

    source = rtc.VideoSource(PUBLISH_WIDTH, PUBLISH_HEIGHT)
    track = rtc.LocalVideoTrack.create_video_track(f"simulcast-{codec_name}", source)
    options = rtc.TrackPublishOptions(
        source=rtc.TrackSource.SOURCE_CAMERA,
        simulcast=True,
        video_codec=video_codec,
        video_encoding=rtc.VideoEncoding(max_bitrate=3_000_000, max_framerate=PUBLISH_FPS),
    )

    stop = asyncio.Event()
    pub_task = asyncio.create_task(_publish_loop(source, stop))

    stream: Optional[rtc.VideoStream] = None
    try:
        track_published = _expect_event(
            receiver,
            "track_published",
            predicate=lambda pub, _p: pub.kind == rtc.TrackKind.KIND_VIDEO,
        )
        local_pub = await sender.local_participant.publish_track(track, options)
        await _await_event(track_published)

        print(
            f"[{codec_name}] local_pub: sid={local_pub.sid} "
            f"simulcasted={local_pub.simulcasted} "
            f"mime_type={local_pub.mime_type} "
            f"{local_pub.width}x{local_pub.height}"
        )
        remote_pub = await _ensure_track_subscribed(receiver, local_pub.sid)
        assert remote_pub.track is not None

        # Give the SFU a moment to propagate simulcast layer metadata and
        # let the encoder/bandwidth estimator ramp up to all layers before
        # we start switching qualities.
        await asyncio.sleep(5.0)
        print(
            f"[{codec_name}] remote_pub: sid={remote_pub.sid} "
            f"simulcasted={remote_pub.simulcasted} "
            f"mime_type={remote_pub.mime_type} "
            f"{remote_pub.width}x{remote_pub.height}"
        )

        stream = rtc.VideoStream.from_track(track=remote_pub.track)

        for quality, layer in QUALITY_SEQUENCE:
            remote_pub.set_video_quality(quality)
            ew, eh = LAYER_DIMENSIONS[layer]
            actual = await _wait_for_layer(stream, ew, eh, timeout=20.0)
            print(
                f"[{codec_name}] layer={layer} expected~{ew}x{eh} got={actual[0]}x{actual[1]}"
            )
    finally:
        stop.set()
        try:
            await pub_task
        except Exception:
            pass
        if stream is not None:
            await stream.aclose()
        await sender.disconnect()
        await receiver.disconnect()
