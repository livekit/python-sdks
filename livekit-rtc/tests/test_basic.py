"""End-to-end translation of the Flutter `BasicsTest` scenario.

The test exercises connect/disconnect lifecycle, participant
visibility, reconnection, and track publish/subscribe between four rooms.

Requires the following environment variables to run:
    LIVEKIT_URL
    LIVEKIT_API_KEY
    LIVEKIT_API_SECRET
"""

from __future__ import annotations

import asyncio
import os
import uuid
from typing import Callable, Optional

import pytest

from livekit import api, rtc


WAIT_TIMEOUT = 20.0
WAIT_INTERVAL = 0.1


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


async def _connect(room: rtc.Room, identity: str, room_name: str) -> str:
    """Mints a token, connects `room`, and returns the token (for reconnect)."""
    token = create_token(identity, room_name)
    url = os.environ["LIVEKIT_URL"]
    await room.connect(url, token)
    return token


async def _ensure_all_connected(rooms: list[rtc.Room]) -> None:
    await _wait_until(
        lambda: all(
            r.connection_state == rtc.ConnectionState.CONN_CONNECTED for r in rooms
        ),
        message="not all rooms reached CONN_CONNECTED",
    )


async def _ensure_track_subscribed(room: rtc.Room, track_sid: str) -> None:
    def _has_subscribed() -> bool:
        for participant in room.remote_participants.values():
            pub = participant.track_publications.get(track_sid)
            if pub is not None and pub.subscribed:
                return True
        return False

    await _wait_until(
        _has_subscribed,
        message=f"room did not subscribe to track {track_sid}",
    )


def _expect_event(
    room: rtc.Room, event: str, predicate: Optional[Callable[..., bool]] = None
) -> asyncio.Future:
    """Returns a future that resolves when `event` (optionally matching
    `predicate`) is fired on `room`."""
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


async def _publish_video(
    room: rtc.Room, track_name: str
) -> rtc.LocalTrackPublication:
    source = rtc.VideoSource(320, 240)
    track = rtc.LocalVideoTrack.create_video_track(track_name, source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_CAMERA)
    return await room.local_participant.publish_track(track, options)


async def _publish_audio(room: rtc.Room, track_name: str) -> rtc.LocalTrackPublication:
    source = rtc.AudioSource(48000, 1)
    track = rtc.LocalAudioTrack.create_audio_track(track_name, source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    return await room.local_participant.publish_track(track, options)


@skip_if_no_credentials()
@pytest.mark.asyncio
async def test_connection_basics() -> None:
    room_name = unique_room_name("py-basics")

    p1, p2 = rtc.Room(), rtc.Room()
    await _connect(p1, "p1", room_name)
    await _connect(p2, "p2", room_name)
    await _ensure_all_connected([p1, p2])

    # p2 should observe p1 leaving
    p2_saw_p1_left = _expect_event(
        p2,
        "participant_disconnected",
        predicate=lambda p: p.identity == "p1",
    )
    await p1.disconnect()
    await _await_event(p2_saw_p1_left)

    await _wait_until(
        lambda: p1.connection_state == rtc.ConnectionState.CONN_DISCONNECTED,
        message="p1 did not reach CONN_DISCONNECTED",
    )

    await p2.disconnect()
    await _wait_until(
        lambda: p2.connection_state == rtc.ConnectionState.CONN_DISCONNECTED,
        message="p2 did not reach CONN_DISCONNECTED",
    )

    # p3: connect, disconnect, reconnect, disconnect cycle
    p3 = rtc.Room()
    p3_token = await _connect(p3, "p3", room_name)
    p3_url = os.environ["LIVEKIT_URL"]

    await p3.disconnect()
    assert p3.connection_state == rtc.ConnectionState.CONN_DISCONNECTED, (
        f"expected p3 disconnected, got {p3.connection_state}"
    )

    await p3.connect(p3_url, p3_token)
    assert p3.connection_state == rtc.ConnectionState.CONN_CONNECTED, (
        f"expected p3 connected, got {p3.connection_state}"
    )

    await p3.disconnect()
    assert p3.connection_state == rtc.ConnectionState.CONN_DISCONNECTED, (
        f"expected p3 disconnected, got {p3.connection_state}"
    )

    # p4 joins, then p3 reconnects to publish to p4
    p4 = rtc.Room()
    await _connect(p4, "p4", room_name)

    await p3.connect(p3_url, p3_token)
    assert p3.connection_state == rtc.ConnectionState.CONN_CONNECTED, (
        f"expected p3 reconnected, got {p3.connection_state}"
    )

    # publish camera from p3, expect p4 to see track_published
    video_published = _expect_event(p4, "track_published")
    video_pub = await _publish_video(p3, "p3-camera")
    await _await_event(video_published)
    await _ensure_track_subscribed(p4, video_pub.sid)

    # publish microphone from p3, expect p4 to see another track_published
    audio_published = _expect_event(
        p4,
        "track_published",
        predicate=lambda pub, _p: pub.sid != video_pub.sid,
    )
    audio_pub = await _publish_audio(p3, "p3-mic")
    await _await_event(audio_published)
    await _ensure_track_subscribed(p4, audio_pub.sid)

    await p3.disconnect()
    await p4.disconnect()

    assert p3.connection_state == rtc.ConnectionState.CONN_DISCONNECTED
    assert p4.connection_state == rtc.ConnectionState.CONN_DISCONNECTED
