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

"""E2E tests for E2EE shared key ."""

from __future__ import annotations

import asyncio
import os
import uuid
from typing import Callable, TypeVar

import pytest

from livekit import api, rtc


SHARED_KEY = b"12345678"
WRONG_KEY = b"wrongkey"
WIDTH, HEIGHT = 320, 180
FRAME_RATE = 15

T = TypeVar("T")


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


async def assert_eventually(
    condition: Callable[[], T],
    timeout: float = 10.0,
    interval: float = 0.1,
    message: str = "Condition not met within timeout",
) -> T:
    deadline = asyncio.get_event_loop().time() + timeout
    last_result = None
    while asyncio.get_event_loop().time() < deadline:
        last_result = condition()
        if last_result:
            return last_result
        await asyncio.sleep(interval)
    raise AssertionError(f"{message} (last result: {last_result})")


def make_e2ee_options() -> rtc.E2EEOptions:
    options = rtc.E2EEOptions()
    options.key_provider_options.shared_key = SHARED_KEY
    options.key_provider_options.ratchet_window_size = 16
    # failure_tolerance must be >= 0 for the cryptor to surface DECRYPTION_FAILED;
    # the default -1 means "infinite retries via auto-ratchet" and never emits.
    options.key_provider_options.failure_tolerance = 3
    return options


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
async def test_e2ee_shared_key():
    """E2E test for shared-key E2EE.

    E2EE shared key E2E test:
      1. Publisher and two receivers connect with the same shared key.
      2. Publisher publishes a video track; receivers must observe
         track_published and an OK e2ee_state.
      3. All participants must use GCM encryption.
      4. Publisher ratchets the shared key; receivers must observe
         KEY_RATCHETED state.
      5. Publisher swaps its shared key for a wrong one; receivers must observe
         DECRYPTION_FAILED.
      6. After exhausting failure_tolerance, the receiver cryptor stops
         retrying; restoring the correct key on the publisher and re-installing
         it on the receivers must bring them back to OK.
    """
    room_name = unique_room_name("test-e2ee-shared-key")
    url = os.getenv("LIVEKIT_URL")

    publisher_room = rtc.Room()
    receiver1_room = rtc.Room()
    receiver2_room = rtc.Room()

    publisher_token = create_token("e2eePublisher", room_name)
    receiver1_token = create_token("receiver1", room_name)
    receiver2_token = create_token("receiver2", room_name)

    # State tracked from event callbacks
    track_published_on: dict[str, asyncio.Event] = {
        "receiver1": asyncio.Event(),
        "receiver2": asyncio.Event(),
    }
    track_subscribed_on: dict[str, asyncio.Event] = {
        "receiver1": asyncio.Event(),
        "receiver2": asyncio.Event(),
    }
    # all e2ee states seen for the publisher's identity (per receiver), since the
    # last reset. KEY_RATCHETED in particular can be transient.
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
            # only track state from the publisher's frames
            if participant is not None and participant.identity == "e2eePublisher":
                seen_e2ee_states[label].add(state)
                e2ee_state_log[label].append(state)

    wire_receiver(receiver1_room, "receiver1")
    wire_receiver(receiver2_room, "receiver2")

    publish_stop = asyncio.Event()
    publish_task: asyncio.Task | None = None

    try:
        connect_options = rtc.RoomOptions(auto_subscribe=True, encryption=make_e2ee_options())

        await publisher_room.connect(url, publisher_token, options=connect_options)
        await receiver1_room.connect(
            url,
            receiver1_token,
            options=rtc.RoomOptions(auto_subscribe=True, encryption=make_e2ee_options()),
        )
        await receiver2_room.connect(
            url,
            receiver2_token,
            options=rtc.RoomOptions(auto_subscribe=True, encryption=make_e2ee_options()),
        )

        # 1) all connected
        for room in (publisher_room, receiver1_room, receiver2_room):
            assert room.connection_state == rtc.ConnectionState.CONN_CONNECTED

        # 2) publish a video track from the publisher
        source = rtc.VideoSource(WIDTH, HEIGHT)
        track = rtc.LocalVideoTrack.create_video_track("e2ee-cam", source)
        publish_options = rtc.TrackPublishOptions()
        publish_options.source = rtc.TrackSource.SOURCE_CAMERA
        publish_options.video_codec = rtc.VideoCodec.VP8
        publish_options.simulcast = True
        publication = await publisher_room.local_participant.publish_track(track, publish_options)
        assert publication is not None and publication.sid

        publish_task = asyncio.create_task(publish_dummy_video(source, publish_stop))

        # 3) receivers must observe track_published
        await asyncio.wait_for(track_published_on["receiver1"].wait(), timeout=15.0)
        await asyncio.wait_for(track_published_on["receiver2"].wait(), timeout=15.0)

        # 4) receivers must subscribe to the track
        await asyncio.wait_for(track_subscribed_on["receiver1"].wait(), timeout=15.0)
        await asyncio.wait_for(track_subscribed_on["receiver2"].wait(), timeout=15.0)

        # 5) wait for receivers to see an OK encryption state from the publisher
        await assert_eventually(
            lambda: rtc.EncryptionState.OK in seen_e2ee_states["receiver1"],
            timeout=15.0,
            message="receiver1 did not reach EncryptionState.OK",
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.OK in seen_e2ee_states["receiver2"],
            timeout=15.0,
            message="receiver2 did not reach EncryptionState.OK",
        )

        # 6) verify all participants are using GCM on the published video track
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

        # 7) ratchet the shared key on the publisher; receivers should ratchet too
        seen_e2ee_states["receiver1"].clear()
        seen_e2ee_states["receiver2"].clear()
        e2ee_state_log["receiver1"].clear()
        e2ee_state_log["receiver2"].clear()
        await asyncio.sleep(1.0)

        key_provider = publisher_room.e2ee_manager.key_provider
        assert key_provider is not None
        key_provider.ratchet_shared_key(key_index=0)

        await assert_eventually(
            lambda: rtc.EncryptionState.KEY_RATCHETED in seen_e2ee_states["receiver1"],
            timeout=15.0,
            message=(
                "receiver1 did not observe KEY_RATCHETED after publisher ratchet "
                f"(saw {e2ee_state_log['receiver1']})"
            ),
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.KEY_RATCHETED in seen_e2ee_states["receiver2"],
            timeout=15.0,
            message=(
                "receiver2 did not observe KEY_RATCHETED after publisher ratchet "
                f"(saw {e2ee_state_log['receiver2']})"
            ),
        )

        # 8) swap the publisher's shared key for a wrong one; receivers should
        # fail to decrypt and surface DECRYPTION_FAILED once failure_tolerance
        # is exhausted.
        seen_e2ee_states["receiver1"].clear()
        seen_e2ee_states["receiver2"].clear()
        e2ee_state_log["receiver1"].clear()
        e2ee_state_log["receiver2"].clear()
        await asyncio.sleep(1.0)

        key_provider.set_shared_key(WRONG_KEY, key_index=0)

        await assert_eventually(
            lambda: rtc.EncryptionState.DECRYPTION_FAILED in seen_e2ee_states["receiver1"],
            timeout=15.0,
            message=(
                "receiver1 did not observe DECRYPTION_FAILED after publisher swapped key "
                f"(saw {e2ee_state_log['receiver1']})"
            ),
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.DECRYPTION_FAILED in seen_e2ee_states["receiver2"],
            timeout=15.0,
            message=(
                "receiver2 did not observe DECRYPTION_FAILED after publisher swapped key "
                f"(saw {e2ee_state_log['receiver2']})"
            ),
        )

        # 9) restore the correct shared key on the publisher, and re-install it
        # on the receivers too: once failure_tolerance is exhausted the
        # receiver cryptor stops retrying, so a fresh key event is required to
        # bring it back to OK.
        seen_e2ee_states["receiver1"].clear()
        seen_e2ee_states["receiver2"].clear()
        e2ee_state_log["receiver1"].clear()
        e2ee_state_log["receiver2"].clear()
        await asyncio.sleep(1.0)

        key_provider.set_shared_key(SHARED_KEY, key_index=0)
        receiver1_room.e2ee_manager.key_provider.set_shared_key(SHARED_KEY, key_index=0)
        receiver2_room.e2ee_manager.key_provider.set_shared_key(SHARED_KEY, key_index=0)

        await assert_eventually(
            lambda: rtc.EncryptionState.OK in seen_e2ee_states["receiver1"],
            timeout=15.0,
            message=(
                "receiver1 did not return to EncryptionState.OK after key restore "
                f"(saw {e2ee_state_log['receiver1']})"
            ),
        )
        await assert_eventually(
            lambda: rtc.EncryptionState.OK in seen_e2ee_states["receiver2"],
            timeout=15.0,
            message=(
                "receiver2 did not return to EncryptionState.OK after key restore "
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
