# Copyright 2026 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""E2E tests for E2EE key per-partcipant."""

from __future__ import annotations

import asyncio
import os

import pytest

from livekit import rtc

from utils import (
    assert_eventually,
    create_token,
    skip_if_no_credentials,
    unique_room_name,
)


# Per-participant keys (publisher identity → list of (key_bytes, key_index))
PUBLISHER_IDENTITY = "e2eePublisher"
PUBLISHER_KEYS: list[tuple[bytes, int]] = [
    (b"12345678", 0),
    (b"abcdefgh", 1),
    (b"ijklmnop", 2),
]

WIDTH, HEIGHT = 320, 180
FRAME_RATE = 15


def make_per_participant_e2ee_options() -> rtc.E2EEOptions:
    options = rtc.E2EEOptions()
    # No shared key — keys are installed per participant after connect.
    options.key_provider_options.shared_key = None
    options.key_provider_options.ratchet_window_size = 16
    # failure_tolerance must be >= 0 for the cryptor to surface DECRYPTION_FAILED;
    # the default -1 means "infinite retries via auto-ratchet" and never emits.
    options.key_provider_options.failure_tolerance = 3
    return options


def install_publisher_keys(room: rtc.Room) -> None:
    """Install the publisher's per-participant keys on `room`'s key provider."""
    key_provider = room.e2ee_manager.key_provider
    assert key_provider is not None, "room is missing a key provider"
    for key, key_index in PUBLISHER_KEYS:
        key_provider.set_key(PUBLISHER_IDENTITY, key, key_index)


def set_key_index_on_all_cryptors(room: rtc.Room, key_index: int) -> None:
    """Equivalent of dart's e2eeManager.setKeyIndex(idx): apply to every cryptor."""
    for cryptor in room.e2ee_manager.frame_cryptors():
        cryptor.set_key_index(key_index)


async def publish_dummy_video(source: rtc.VideoSource, stop_event: asyncio.Event) -> None:
    """Continuously publish frames until stop_event is set."""
    pixel_count = WIDTH * HEIGHT
    frame_idx = 0
    while not stop_event.is_set():
        fill = frame_idx % 256
        pixel = bytes((255, fill, (fill + 85) % 256, (fill + 170) % 256))
        buf = pixel * pixel_count
        frame = rtc.VideoFrame(WIDTH, HEIGHT, rtc.VideoBufferType.ARGB, buf)
        source.capture_frame(frame)
        frame_idx += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=1.0 / FRAME_RATE)
        except asyncio.TimeoutError:
            pass


@pytest.mark.asyncio
@skip_if_no_credentials()
async def test_e2ee_per_participant() -> None:
    """E2E test for per-participant E2EE keys.

    E2EE per-participant E2E test:
      1. Each room has its own KeyProvider; the publisher's three keys
         (indexes 0/1/2) are installed on every room.
      2. Publisher publishes a video track. Receivers must observe
         track_published and an OK e2ee_state.
      3. All participants must use GCM encryption.
      4. Publisher ratchets key index 2 → receivers observe KEY_RATCHETED.
      5. Publisher overwrites key index 0 with a wrong key → receivers
         observe DECRYPTION_FAILED.
      6. Publisher switches to key index 1 → receivers observe OK
         (since they already have key index 1).
      7. Publisher switches to key index 2 and ratchets it; receivers
         switch to key index 2 → receivers observe KEY_RATCHETED.
    """
    room_name = unique_room_name("test-e2ee-per-participant")
    url = os.getenv("LIVEKIT_URL")
    assert url is not None

    publisher_room = rtc.Room()
    receiver1_room = rtc.Room()
    receiver2_room = rtc.Room()

    publisher_token = create_token(PUBLISHER_IDENTITY, room_name)
    receiver1_token = create_token("receiver1", room_name)
    receiver2_token = create_token("receiver2", room_name)

    track_published_on: dict[str, asyncio.Event] = {
        "receiver1": asyncio.Event(),
        "receiver2": asyncio.Event(),
    }
    track_subscribed_on: dict[str, asyncio.Event] = {
        "receiver1": asyncio.Event(),
        "receiver2": asyncio.Event(),
    }
    seen_e2ee_states: dict[str, set[int]] = {
        "receiver1": set(),
        "receiver2": set(),
    }
    e2ee_state_log: dict[str, list[int]] = {
        "receiver1": [],
        "receiver2": [],
    }

    def wire_receiver(room: rtc.Room, label: str) -> None:
        @room.on("track_published")
        def _on_pub(
            publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant
        ) -> None:
            track_published_on[label].set()

        @room.on("track_subscribed")
        def _on_sub(
            track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant,
        ) -> None:
            track_subscribed_on[label].set()

        @room.on("e2ee_state_changed")
        def _on_state(participant: rtc.Participant, state: int) -> None:
            if participant is not None and participant.identity == PUBLISHER_IDENTITY:
                seen_e2ee_states[label].add(state)
                e2ee_state_log[label].append(state)

    wire_receiver(receiver1_room, "receiver1")
    wire_receiver(receiver2_room, "receiver2")

    publish_stop = asyncio.Event()
    publish_task: asyncio.Task[None] | None = None

    try:
        # 1) connect all three rooms with per-participant E2EE options
        await publisher_room.connect(
            url,
            publisher_token,
            options=rtc.RoomOptions(
                auto_subscribe=True, encryption=make_per_participant_e2ee_options()
            ),
        )
        await receiver1_room.connect(
            url,
            receiver1_token,
            options=rtc.RoomOptions(
                auto_subscribe=True, encryption=make_per_participant_e2ee_options()
            ),
        )
        await receiver2_room.connect(
            url,
            receiver2_token,
            options=rtc.RoomOptions(
                auto_subscribe=True, encryption=make_per_participant_e2ee_options()
            ),
        )

        for room in (publisher_room, receiver1_room, receiver2_room):
            assert room.connection_state == rtc.ConnectionState.CONN_CONNECTED
            install_publisher_keys(room)

        # 2) publish a video track
        source = rtc.VideoSource(WIDTH, HEIGHT)
        track = rtc.LocalVideoTrack.create_video_track("e2ee-cam", source)
        publish_options = rtc.TrackPublishOptions()
        publish_options.source = rtc.TrackSource.SOURCE_CAMERA
        publish_options.video_codec = rtc.VideoCodec.VP8
        publish_options.simulcast = True
        publication = await publisher_room.local_participant.publish_track(track, publish_options)
        assert publication is not None and publication.sid

        publish_task = asyncio.create_task(publish_dummy_video(source, publish_stop))

        # 3) receivers see track_published / track_subscribed
        await asyncio.wait_for(track_published_on["receiver1"].wait(), timeout=15.0)
        await asyncio.wait_for(track_published_on["receiver2"].wait(), timeout=15.0)
        await asyncio.wait_for(track_subscribed_on["receiver1"].wait(), timeout=15.0)
        await asyncio.wait_for(track_subscribed_on["receiver2"].wait(), timeout=15.0)

        # 4) receivers reach EncryptionState.OK
        await assert_eventually(
            lambda: rtc.EncryptionState.OK in seen_e2ee_states["receiver1"],
            message=(
                f"receiver1 did not reach EncryptionState.OK (saw {e2ee_state_log['receiver1']})"
            ),
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.OK in seen_e2ee_states["receiver2"],
            message=(
                f"receiver2 did not reach EncryptionState.OK (saw {e2ee_state_log['receiver2']})"
            ),
        )

        # 5) verify GCM on both receiver rooms
        def all_remote_video_pubs_gcm(room: rtc.Room) -> bool:
            for rp in room.remote_participants.values():
                for pub in rp.track_publications.values():
                    if pub.kind != rtc.TrackKind.KIND_VIDEO:
                        continue
                    if pub.encryption_type != rtc.EncryptionType.GCM:
                        return False
            return True

        await assert_eventually(
            lambda: all_remote_video_pubs_gcm(receiver1_room),
            message="receiver1 sees a non-GCM video publication",
        )
        await assert_eventually(
            lambda: all_remote_video_pubs_gcm(receiver2_room),
            message="receiver2 sees a non-GCM video publication",
        )

        # 6) ratchet publisher's key at index 0 (the default cryptor key index);
        #    receivers should auto-ratchet to match.
        seen_e2ee_states["receiver1"].clear()
        seen_e2ee_states["receiver2"].clear()
        e2ee_state_log["receiver1"].clear()
        e2ee_state_log["receiver2"].clear()
        await asyncio.sleep(1.0)

        publisher_key_provider = publisher_room.e2ee_manager.key_provider
        assert publisher_key_provider is not None
        publisher_key_provider.ratchet_key(PUBLISHER_IDENTITY, key_index=0)

        await assert_eventually(
            lambda: rtc.EncryptionState.KEY_RATCHETED in seen_e2ee_states["receiver1"],
            message=(
                "receiver1 did not observe KEY_RATCHETED after publisher ratchet "
                f"(saw {e2ee_state_log['receiver1']})"
            ),
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.KEY_RATCHETED in seen_e2ee_states["receiver2"],
            message=(
                "receiver2 did not observe KEY_RATCHETED after publisher ratchet "
                f"(saw {e2ee_state_log['receiver2']})"
            ),
        )

        # 7) publisher overwrites key index 0 with a wrong key (receivers
        #    still hold the original key 0) → receivers observe DECRYPTION_FAILED
        seen_e2ee_states["receiver1"].clear()
        seen_e2ee_states["receiver2"].clear()
        e2ee_state_log["receiver1"].clear()
        e2ee_state_log["receiver2"].clear()
        await asyncio.sleep(1.0)

        publisher_key_provider.set_key(PUBLISHER_IDENTITY, b"wrongkey", 0)

        await assert_eventually(
            lambda: rtc.EncryptionState.DECRYPTION_FAILED in seen_e2ee_states["receiver1"],
            message=(
                f"receiver1 did not observe DECRYPTION_FAILED (saw {e2ee_state_log['receiver1']})"
            ),
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.DECRYPTION_FAILED in seen_e2ee_states["receiver2"],
            message=(
                f"receiver2 did not observe DECRYPTION_FAILED (saw {e2ee_state_log['receiver2']})"
            ),
        )

        # 8) publisher switches to key index 1 (still correct on both sides).
        #    Once failure_tolerance is exhausted the receiver cryptor stops
        #    retrying, so we also re-install key index 1 on the receivers to
        #    deliver a fresh key event that wakes the cryptor back up.
        seen_e2ee_states["receiver1"].clear()
        seen_e2ee_states["receiver2"].clear()
        e2ee_state_log["receiver1"].clear()
        e2ee_state_log["receiver2"].clear()
        await asyncio.sleep(1.0)

        set_key_index_on_all_cryptors(publisher_room, 1)
        key1_bytes, _ = PUBLISHER_KEYS[1]
        receiver1_key_provider = receiver1_room.e2ee_manager.key_provider
        receiver2_key_provider = receiver2_room.e2ee_manager.key_provider
        assert receiver1_key_provider is not None
        assert receiver2_key_provider is not None
        receiver1_key_provider.set_key(PUBLISHER_IDENTITY, key1_bytes, 1)
        receiver2_key_provider.set_key(PUBLISHER_IDENTITY, key1_bytes, 1)

        await assert_eventually(
            lambda: rtc.EncryptionState.OK in seen_e2ee_states["receiver1"],
            message=(
                "receiver1 did not return to EncryptionState.OK with key index 1 "
                f"(saw {e2ee_state_log['receiver1']})"
            ),
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.OK in seen_e2ee_states["receiver2"],
            message=(
                "receiver2 did not return to EncryptionState.OK with key index 1 "
                f"(saw {e2ee_state_log['receiver2']})"
            ),
        )

        # 9) publisher switches to key index 2 and ratchets it; receivers
        #    switch to key index 2 → should observe KEY_RATCHETED
        seen_e2ee_states["receiver1"].clear()
        seen_e2ee_states["receiver2"].clear()
        e2ee_state_log["receiver1"].clear()
        e2ee_state_log["receiver2"].clear()
        await asyncio.sleep(1.0)

        set_key_index_on_all_cryptors(publisher_room, 2)
        publisher_key_provider.ratchet_key(PUBLISHER_IDENTITY, key_index=2)
        set_key_index_on_all_cryptors(receiver1_room, 2)
        set_key_index_on_all_cryptors(receiver2_room, 2)

        await assert_eventually(
            lambda: rtc.EncryptionState.KEY_RATCHETED in seen_e2ee_states["receiver1"],
            message=(
                "receiver1 did not observe KEY_RATCHETED after key-index switch "
                f"(saw {e2ee_state_log['receiver1']})"
            ),
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.KEY_RATCHETED in seen_e2ee_states["receiver2"],
            message=(
                "receiver2 did not observe KEY_RATCHETED after key-index switch "
                f"(saw {e2ee_state_log['receiver2']})"
            ),
        )

    finally:
        publish_stop.set()
        if publish_task is not None:
            try:
                await asyncio.wait_for(publish_task, timeout=2.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                publish_task.cancel()

        for room in (publisher_room, receiver1_room, receiver2_room):
            if room.isconnected():
                await room.disconnect()
