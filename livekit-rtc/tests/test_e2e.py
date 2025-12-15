"""
End-to-end tests for LiveKit RTC library.

These tests verify core functionality of the LiveKit RTC library including:
- Publishing and subscribing to audio tracks
- Audio stream consumption and energy verification
- Room lifecycle events (connect, disconnect, track publish/unpublish)
- Connection state transitions

Requirements:
- LIVEKIT_URL: LiveKit server URL
- LIVEKIT_API_KEY: API key for authentication
- LIVEKIT_API_SECRET: API secret for authentication

Tests will be skipped if these environment variables are not set.

Usage:
    pytest test_e2e.py -v
"""

import asyncio
import os
import uuid
from typing import Callable, TypeVar
import numpy as np
import pytest

from livekit import rtc, api
from livekit.rtc.utils import sine_wave_generator


SAMPLE_RATE = 48000
T = TypeVar("T")


async def assert_eventually(
    condition: Callable[[], T],
    timeout: float = 5.0,
    interval: float = 0.1,
    message: str = "Condition not met within timeout",
) -> T:
    """
    Poll a condition until it becomes truthy or timeout is reached.
    Returns immediately once condition is satisfied.
    """
    deadline = asyncio.get_event_loop().time() + timeout
    last_result = None

    while asyncio.get_event_loop().time() < deadline:
        last_result = condition()
        if last_result:
            return last_result
        await asyncio.sleep(interval)

    raise AssertionError(f"{message} (last result: {last_result})")


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


@pytest.mark.asyncio
@skip_if_no_credentials()
async def test_publish_track():
    """Test that a published track can be subscribed by another participant"""
    room_name = unique_room_name("test-publish-track")
    url = os.getenv("LIVEKIT_URL")

    publisher_room = rtc.Room()
    subscriber_room = rtc.Room()

    publisher_token = create_token("publisher", room_name)
    subscriber_token = create_token("subscriber", room_name)

    track_published_event = asyncio.Event()
    track_subscribed_event = asyncio.Event()
    subscribed_track = None

    @subscriber_room.on("track_published")
    def on_track_published(
        publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant
    ):
        track_published_event.set()

    @subscriber_room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        nonlocal subscribed_track
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            subscribed_track = track
            track_subscribed_event.set()

    try:
        await subscriber_room.connect(url, subscriber_token)
        await publisher_room.connect(url, publisher_token)

        source = rtc.AudioSource(SAMPLE_RATE, 1)
        track = rtc.LocalAudioTrack.create_audio_track("test-audio", source)
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        publication = await publisher_room.local_participant.publish_track(track, options)

        assert publication is not None
        assert publication.sid is not None

        await asyncio.wait_for(track_published_event.wait(), timeout=5.0)
        await asyncio.wait_for(track_subscribed_event.wait(), timeout=5.0)

        assert subscribed_track is not None
        assert isinstance(subscribed_track, rtc.RemoteAudioTrack)

    finally:
        await publisher_room.disconnect()
        await subscriber_room.disconnect()


@pytest.mark.asyncio
@skip_if_no_credentials()
async def test_audio_stream_subscribe():
    """Test that published audio can be consumed and has similar energy levels"""
    room_name = unique_room_name("test-audio-stream")
    url = os.getenv("LIVEKIT_URL")

    publisher_room = rtc.Room()
    subscriber_room = rtc.Room()

    publisher_token = create_token("audio-publisher", room_name)
    subscriber_token = create_token("audio-subscriber", room_name)

    track_subscribed_event = asyncio.Event()
    subscribed_track = None

    @subscriber_room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        nonlocal subscribed_track
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            subscribed_track = track
            track_subscribed_event.set()

    try:
        await subscriber_room.connect(url, subscriber_token)
        await publisher_room.connect(url, publisher_token)

        source = rtc.AudioSource(SAMPLE_RATE, 1)
        track = rtc.LocalAudioTrack.create_audio_track("sine-wave", source)
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        await publisher_room.local_participant.publish_track(track, options)
        target_duration = 5.0

        published_energy = []

        async def publish_audio():
            async for frame in sine_wave_generator(440, target_duration, SAMPLE_RATE):
                data = np.frombuffer(frame.data.tobytes(), dtype=np.int16)
                energy = np.mean(np.abs(data.astype(np.float32)))
                published_energy.append(energy)
                await source.capture_frame(frame)

        publish_task = asyncio.create_task(publish_audio())

        await asyncio.wait_for(track_subscribed_event.wait(), timeout=5.0)
        assert subscribed_track is not None

        audio_stream = rtc.AudioStream(
            subscribed_track,
            sample_rate=SAMPLE_RATE,
            num_channels=1,
        )

        received_frames = []
        target_frames = int(target_duration * SAMPLE_RATE / 480)

        frame_count = 0
        async for event in audio_stream:
            frame = event.frame
            data = np.frombuffer(frame.data, dtype=np.int16)
            received_frames.append(data)
            frame_count += 1
            if frame_count >= target_frames:
                break

        await audio_stream.aclose()
        await publish_task

        assert len(received_frames) > 0, "No audio frames were received"

        received_energy = []
        for data in received_frames:
            energy = np.mean(np.abs(data.astype(np.float32)))
            received_energy.append(energy)

        avg_received_energy = np.mean(received_energy)
        avg_published_energy = np.mean(published_energy)

        assert avg_received_energy > 0, "Received audio has no energy"
        assert avg_published_energy > 0, "Published audio has no energy"
        assert (
            avg_received_energy > avg_published_energy * 0.9
            and avg_received_energy < avg_published_energy * 1.1
        ), "Received audio energy is not within range"

    finally:
        await publisher_room.disconnect()
        await subscriber_room.disconnect()


@pytest.mark.asyncio
@skip_if_no_credentials()
async def test_room_lifecycle_events():
    """Test that room lifecycle and track events are fired properly"""
    room_name = unique_room_name("test-lifecycle-events")
    url = os.getenv("LIVEKIT_URL")

    room1 = rtc.Room()
    room2 = rtc.Room()

    token1 = create_token("participant-1", room_name)
    token2 = create_token("participant-2", room_name)

    events = {
        "disconnected": [],
        "participant_connected": [],
        "participant_disconnected": [],
        "local_track_published": [],
        "local_track_unpublished": [],
        "track_published": [],
        "track_unpublished": [],
        "track_subscribed": [],
        "track_unsubscribed": [],
        "room_updated": [],
        "connection_state_changed": [],
    }

    @room1.on("disconnected")
    def on_room1_disconnected(reason):
        events["disconnected"].append("room1")

    @room1.on("participant_connected")
    def on_room1_participant_connected(participant: rtc.RemoteParticipant):
        events["participant_connected"].append(f"room1-{participant.identity}")

    @room1.on("participant_disconnected")
    def on_room1_participant_disconnected(participant: rtc.RemoteParticipant):
        events["participant_disconnected"].append(f"room1-{participant.identity}")

    @room1.on("local_track_published")
    def on_room1_local_track_published(publication: rtc.LocalTrackPublication, track):
        events["local_track_published"].append(f"room1-{publication.sid}")

    @room1.on("local_track_unpublished")
    def on_room1_local_track_unpublished(publication: rtc.LocalTrackPublication):
        events["local_track_unpublished"].append(f"room1-{publication.sid}")

    @room1.on("room_updated")
    def on_room1_room_updated():
        events["room_updated"].append("room1")

    @room1.on("connection_state_changed")
    def on_room1_connection_state_changed(state: rtc.ConnectionState):
        events["connection_state_changed"].append(f"room1-{state}")

    @room2.on("track_published")
    def on_room2_track_published(
        publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant
    ):
        events["track_published"].append(f"room2-{publication.sid}")

    @room2.on("track_subscribed")
    def on_room2_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        events["track_subscribed"].append(f"room2-{publication.sid}")

    @room2.on("track_unpublished")
    def on_room2_track_unpublished(
        publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant
    ):
        events["track_unpublished"].append(f"room2-{publication.sid}")

    try:
        await room1.connect(url, token1)

        await assert_eventually(
            lambda: len(events["connection_state_changed"]) > 0
            and events["connection_state_changed"][-1]
            == f"room1-{rtc.ConnectionState.CONN_CONNECTED}",
            message="room1 connection_state_changed event not fired or did not reach CONN_CONNECTED state",
        )

        await room2.connect(url, token2)

        await assert_eventually(
            lambda: "room1-participant-2" in events["participant_connected"],
            message="room1 did not receive participant_connected for participant-2",
        )
        await assert_eventually(
            lambda: room2.remote_participants.get("participant-1") is not None,
            message="room2 did not see participant-1",
        )

        source = rtc.AudioSource(SAMPLE_RATE, 1)
        track = rtc.LocalAudioTrack.create_audio_track("test-track", source)
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        publication = await room1.local_participant.publish_track(track, options)

        await assert_eventually(
            lambda: len(events["local_track_published"]) > 0,
            message="local_track_published event not fired",
        )
        await assert_eventually(
            lambda: any("room2" in e for e in events["track_published"]),
            message="room2 did not receive track_published",
        )
        await assert_eventually(
            lambda: len(events["track_subscribed"]) > 0, message="track_subscribed event not fired"
        )

        await room1.local_participant.unpublish_track(publication.sid)

        await assert_eventually(
            lambda: len(events["local_track_unpublished"]) > 0,
            message="local_track_unpublished event not fired",
        )
        await assert_eventually(
            lambda: len(events["track_unpublished"]) > 0,
            message="track_unpublished event not fired",
        )

        await room2.disconnect()

        await assert_eventually(
            lambda: "room1-participant-2" in events["participant_disconnected"],
            message="participant_disconnected not fired for participant-2",
        )

        await room1.disconnect()

        await assert_eventually(
            lambda: lambda: len(events["connection_state_changed"]) > 0
            and events["connection_state_changed"][-1]
            == f"room1-{rtc.ConnectionState.CONN_DISCONNECTED}",
            message="room1 disconnected event not fired",
        )

        print("\nEvent Summary:")
        for event_type, event_list in events.items():
            if event_list:
                print(f"  {event_type}: {len(event_list)} events")

    finally:
        if room1.isconnected():
            await room1.disconnect()
        if room2.isconnected():
            await room2.disconnect()


@pytest.mark.asyncio
@skip_if_no_credentials()
async def test_connection_state_transitions():
    """Test that connection state transitions work correctly"""
    room_name = unique_room_name("test-connection-state")
    url = os.getenv("LIVEKIT_URL")

    room = rtc.Room()
    token = create_token("state-test", room_name)

    states = []

    @room.on("connection_state_changed")
    def on_state_changed(state: rtc.ConnectionState):
        states.append(state)

    try:
        assert room.connection_state == rtc.ConnectionState.CONN_DISCONNECTED

        await room.connect(url, token)

        await assert_eventually(
            lambda: room.connection_state == rtc.ConnectionState.CONN_CONNECTED,
            message="Room did not reach CONN_CONNECTED state",
        )
        await assert_eventually(
            lambda: rtc.ConnectionState.CONN_CONNECTED in states,
            message="CONN_CONNECTED state not in state change events",
        )

        await room.disconnect()

        await assert_eventually(
            lambda: room.connection_state == rtc.ConnectionState.CONN_DISCONNECTED,
            message="Room did not reach CONN_DISCONNECTED state after disconnect",
        )

    finally:
        if room.isconnected():
            await room.disconnect()
