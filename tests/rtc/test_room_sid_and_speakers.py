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

import asyncio

import pytest

from livekit import rtc
from livekit.rtc import ConnectionState, Participant, RemoteParticipant
from livekit.rtc._proto import participant_pb2 as proto_participant
from livekit.rtc._proto import room_pb2 as proto_room


@pytest.mark.asyncio
async def test_room_sid_disconnected_raises_runtime_error() -> None:
    room = rtc.Room()
    with pytest.raises(RuntimeError, match="cannot get sid of a disconnected room"):
        await room.sid


@pytest.mark.asyncio
async def test_room_get_sid_timeout() -> None:
    room = rtc.Room()
    room._connection_state = ConnectionState.CONN_CONNECTED
    with pytest.raises(asyncio.TimeoutError):
        await room.get_sid(timeout=0.05)


@pytest.mark.asyncio
async def test_room_sid_resolution_and_get_sid() -> None:
    room = rtc.Room()
    room._connection_state = ConnectionState.CONN_CONNECTED

    async def resolve_soon() -> None:
        await asyncio.sleep(0.01)
        room._resolve_first_sid("RM_test123")

    task = asyncio.create_task(resolve_soon())
    sid = await room.get_sid(timeout=1.0)
    await task
    assert sid == "RM_test123"
    assert await room.sid == "RM_test123"
    assert "RM_test123" in repr(room)


@pytest.mark.asyncio
async def test_room_sid_failed_on_disconnect() -> None:
    room = rtc.Room()
    room._connection_state = ConnectionState.CONN_CONNECTED

    async def wait_sid() -> None:
        await room.sid

    wait_task = asyncio.create_task(wait_sid())
    await asyncio.sleep(0.01)

    # Room disconnects before receiving SID
    room._fail_first_sid(RuntimeError("room disconnected before receiving sid"))

    with pytest.raises(RuntimeError, match="room disconnected before receiving sid"):
        await wait_task


def _create_mock_remote_participant(identity: str, sid: str) -> RemoteParticipant:
    owned_info = proto_participant.OwnedParticipant()
    owned_info.handle.id = 0
    owned_info.info.sid = sid
    owned_info.info.identity = identity
    p = RemoteParticipant(owned_info)
    p._ffi_handle.mark_consumed()
    return p


@pytest.mark.asyncio
async def test_active_speakers_deduplication() -> None:
    room = rtc.Room()
    p1 = _create_mock_remote_participant("user-1", "PA_1")
    p2 = _create_mock_remote_participant("user-2", "PA_2")
    room._remote_participants["user-1"] = p1
    room._remote_participants["user-2"] = p2

    emitted_speaker_identities: list[list[str]] = []

    def on_speakers_changed(speakers: list[Participant]) -> None:
        emitted_speaker_identities.append([p.identity for p in speakers])

    room.on("active_speakers_changed", on_speakers_changed)

    # 1. First event: user-1 is speaking
    ev1 = proto_room.RoomEvent()
    ev1.active_speakers_changed.participant_identities.append("user-1")
    room._on_room_event(ev1)

    assert len(emitted_speaker_identities) == 1
    assert emitted_speaker_identities[-1] == ["user-1"]
    assert [p.identity for p in room.active_speakers] == ["user-1"]

    # 2. Duplicate event: user-1 still speaking (no change) -> should NOT emit
    ev2 = proto_room.RoomEvent()
    ev2.active_speakers_changed.participant_identities.append("user-1")
    room._on_room_event(ev2)

    assert len(emitted_speaker_identities) == 1

    # 3. New event: user-1 and user-2 speaking -> should emit
    ev3 = proto_room.RoomEvent()
    ev3.active_speakers_changed.participant_identities.extend(["user-1", "user-2"])
    room._on_room_event(ev3)

    assert len(emitted_speaker_identities) == 2
    assert emitted_speaker_identities[-1] == ["user-1", "user-2"]
    assert [p.identity for p in room.active_speakers] == ["user-1", "user-2"]

    # 4. Speakers stop: blank event -> should emit empty list
    ev4 = proto_room.RoomEvent()
    ev4.active_speakers_changed.SetInParent()
    room._on_room_event(ev4)

    assert len(emitted_speaker_identities) == 3
    assert emitted_speaker_identities[-1] == []
    assert room.active_speakers == []

    # 5. Subsequent blank event -> should NOT emit again
    ev5 = proto_room.RoomEvent()
    ev5.active_speakers_changed.SetInParent()
    room._on_room_event(ev5)

    assert len(emitted_speaker_identities) == 3


@pytest.mark.asyncio
async def test_participant_disconnected_updates_active_speakers() -> None:
    room = rtc.Room()
    p1 = _create_mock_remote_participant("user-1", "PA_1")
    p2 = _create_mock_remote_participant("user-2", "PA_2")
    room._remote_participants["user-1"] = p1
    room._remote_participants["user-2"] = p2

    emitted_speaker_identities: list[list[str]] = []

    def on_speakers_changed(speakers: list[Participant]) -> None:
        emitted_speaker_identities.append([p.identity for p in speakers])

    room.on("active_speakers_changed", on_speakers_changed)

    # Both users speaking
    ev = proto_room.RoomEvent()
    ev.active_speakers_changed.participant_identities.extend(["user-1", "user-2"])
    room._on_room_event(ev)
    assert len(emitted_speaker_identities) == 1

    # user-1 disconnects
    disc_ev = proto_room.RoomEvent()
    disc_ev.participant_disconnected.participant_identity = "user-1"
    room._on_room_event(disc_ev)

    assert len(emitted_speaker_identities) == 2
    assert emitted_speaker_identities[-1] == ["user-2"]
    assert [p.identity for p in room.active_speakers] == ["user-2"]


@pytest.mark.asyncio
async def test_room_disconnect_clears_active_speakers() -> None:
    room = rtc.Room()
    p1 = _create_mock_remote_participant("user-1", "PA_1")
    room._remote_participants["user-1"] = p1

    emitted_speaker_identities: list[list[str]] = []

    def on_speakers_changed(speakers: list[Participant]) -> None:
        emitted_speaker_identities.append([p.identity for p in speakers])

    room.on("active_speakers_changed", on_speakers_changed)

    # user-1 speaking
    ev = proto_room.RoomEvent()
    ev.active_speakers_changed.participant_identities.append("user-1")
    room._on_room_event(ev)
    assert len(emitted_speaker_identities) == 1
    assert [p.identity for p in room.active_speakers] == ["user-1"]

    # Disconnect event arrives
    disc_ev = proto_room.RoomEvent()
    disc_ev.disconnected.reason = proto_participant.DisconnectReason.UNKNOWN_REASON
    room._on_room_event(disc_ev)

    assert len(emitted_speaker_identities) == 2
    assert emitted_speaker_identities[-1] == []
    assert room.active_speakers == []
