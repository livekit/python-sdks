"""End-to-end Test for basic scenarios.

The test exercises connect/disconnect lifecycle, participant
visibility, reconnection, and track publish/subscribe between four rooms.

Requires the following environment variables to run:
    LIVEKIT_URL
    LIVEKIT_API_KEY
    LIVEKIT_API_SECRET
"""

from __future__ import annotations

import os

import pytest

from livekit import rtc

from utils import (  # type: ignore[import-not-found]
    await_event,
    connect_room,
    create_token,
    ensure_rooms_all_connected,
    ensure_track_subscribed,
    expect_room_event,
    skip_if_no_credentials,
    unique_room_name,
    wait_until,
)


async def _publish_video(room: rtc.Room, track_name: str) -> rtc.LocalTrackPublication:
    source = rtc.VideoSource(320, 240)
    track = rtc.LocalVideoTrack.create_video_track(track_name, source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_CAMERA)
    return await room.local_participant.publish_track(track, options)


async def _publish_audio(room: rtc.Room, track_name: str) -> rtc.LocalTrackPublication:
    source = rtc.AudioSource(48000, 1)
    track = rtc.LocalAudioTrack.create_audio_track(track_name, source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    return await room.local_participant.publish_track(track, options)


@skip_if_no_credentials()  # type: ignore[untyped-decorator]
@pytest.mark.asyncio
async def test_connection_basics() -> None:
    room_name = unique_room_name("py-basics")

    p1 = await connect_room("p1", room_name)
    p2 = await connect_room("p2", room_name)
    await ensure_rooms_all_connected([p1, p2])

    # p2 should observe p1 leaving
    p2_saw_p1_left = expect_room_event(
        p2,
        "participant_disconnected",
        predicate=lambda p: p.identity == "p1",
    )
    await p1.disconnect()
    await await_event(p2_saw_p1_left)

    await wait_until(
        lambda: p1.connection_state == rtc.ConnectionState.CONN_DISCONNECTED,
        message="p1 did not reach CONN_DISCONNECTED",
    )

    await p2.disconnect()
    await wait_until(
        lambda: p2.connection_state == rtc.ConnectionState.CONN_DISCONNECTED,
        message="p2 did not reach CONN_DISCONNECTED",
    )

    # p3: connect, disconnect, reconnect, disconnect cycle
    p3 = await connect_room("p3", room_name)
    p3_url = os.environ["LIVEKIT_URL"]
    p3_token = create_token("p3", room_name)

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
    p4 = await connect_room("p4", room_name)

    await p3.connect(p3_url, p3_token)
    assert p3.connection_state == rtc.ConnectionState.CONN_CONNECTED, (
        f"expected p3 reconnected, got {p3.connection_state}"
    )

    # publish camera from p3, expect p4 to see track_published
    video_published = expect_room_event(p4, "track_published")
    video_pub = await _publish_video(p3, "p3-camera")
    await await_event(video_published)
    await ensure_track_subscribed(p4, video_pub.sid)

    # publish microphone from p3, expect p4 to see another track_published
    audio_published = expect_room_event(
        p4,
        "track_published",
        predicate=lambda pub, _p: pub.sid != video_pub.sid,
    )
    audio_pub = await _publish_audio(p3, "p3-mic")
    await await_event(audio_published)
    await ensure_track_subscribed(p4, audio_pub.sid)

    await p3.disconnect()
    await p4.disconnect()

    assert p3.connection_state == rtc.ConnectionState.CONN_DISCONNECTED
    assert p4.connection_state == rtc.ConnectionState.CONN_DISCONNECTED
