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

"""Exercise Room.connect's real subscription without a native FFI or server."""

import asyncio
from collections.abc import AsyncIterator
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from livekit import rtc
from livekit.rtc._ffi_client import FfiClient, FfiQueue
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._proto import track_pb2 as proto_track


@pytest.fixture
async def connected_room(
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[tuple[rtc.Room, FfiQueue[proto_ffi.FfiEvent]]]:
    queue = FfiQueue[proto_ffi.FfiEvent]()

    def request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        response = proto_ffi.FfiResponse()
        event = proto_ffi.FfiEvent()
        which = req.WhichOneof("message")
        if which == "connect":
            response.connect.async_id = event.connect.async_id = 1
            event.connect.result.room.handle.id = 1
            event.connect.result.room.info.sid = "RM_test"
        elif which == "ready_for_room_event":
            return response
        elif which == "publish_track":
            response.publish_track.async_id = event.publish_track.async_id = 2
            event.publish_track.publication.info.sid = "TR_test"
        elif which == "unpublish_track":
            response.unpublish_track.async_id = event.unpublish_track.async_id = 3
        elif which == "disconnect":
            response.disconnect.async_id = event.disconnect.async_id = 4
            eos = proto_ffi.FfiEvent()
            eos.room_event.room_handle = req.disconnect.room_handle
            eos.room_event.eos.SetInParent()
            queue.put(eos)
        else:
            raise AssertionError(f"unexpected FFI request: {which}")
        queue.put(event)
        return response

    # A different PID prevents synthetic handles from being dropped natively.
    monkeypatch.setattr(
        FfiClient, "_instance", SimpleNamespace(queue=queue, request=request, _pid=-1)
    )
    room = rtc.Room()
    await asyncio.wait_for(room.connect("wss://example.invalid", "test-token"), 1)
    assert room._ffi_handle is not None
    room._ffi_handle.mark_consumed()
    try:
        yield room, queue
    finally:
        try:
            await asyncio.wait_for(room.disconnect(), 1)
        finally:
            # Do not access the restored FFI singleton from Room.__del__ later.
            room._ffi_handle = None
        assert not queue._subscribers


@pytest.mark.parametrize("event_type", ["audio_stream_event", "video_stream_event"])
async def test_media_events_do_not_schedule_room_callbacks(
    connected_room: tuple[rtc.Room, FfiQueue[proto_ffi.FfiEvent]], event_type: str
) -> None:
    room, queue = connected_room
    loop = asyncio.get_running_loop()
    media_queue = queue.subscribe(loop, filter_fn=lambda e: e.WhichOneof("message") == event_type)
    event = proto_ffi.FfiEvent()
    getattr(event, event_type).SetInParent()
    try:
        with patch.object(
            loop, "call_soon_threadsafe", wraps=loop.call_soon_threadsafe
        ) as schedule:
            for _ in range(100):
                queue.put(event)

        # Only the independent media subscriber should incur an event-loop wakeup.
        assert schedule.call_count == 100
        assert all(call.args[0] == media_queue.put_nowait for call in schedule.call_args_list)
        await asyncio.sleep(0)
        assert media_queue.qsize() == 100
        assert room._ffi_queue.empty()
    finally:
        queue.unsubscribe(media_queue)


@pytest.mark.parametrize(
    "event_type",
    [
        "room_event",
        "rpc_method_invocation",
        "publish_track",
        "unpublish_track",
        "capture_audio_frame",
    ],
)
async def test_room_keeps_control_events_and_request_callbacks(
    connected_room: tuple[rtc.Room, FfiQueue[proto_ffi.FfiEvent]],
    monkeypatch: pytest.MonkeyPatch,
    event_type: str,
) -> None:
    room, queue = connected_room
    room_handler = Mock()
    rpc_handler = Mock()
    monkeypatch.setattr(room, "_on_room_event", room_handler)
    monkeypatch.setattr(room, "_on_rpc_method_invocation", rpc_handler)
    subscriber = room._room_queue.subscribe()
    event = proto_ffi.FfiEvent()
    getattr(event, event_type).SetInParent()
    if event_type == "room_event":
        event.room_event.room_handle = 1
    try:
        queue.put(event)
        received = await asyncio.wait_for(subscriber.get(), 1)
        subscriber.task_done()
        assert received is event
        if event_type == "room_event":
            room_handler.assert_called_once_with(event.room_event)
        elif event_type == "rpc_method_invocation":
            rpc_handler.assert_called_once_with(event.rpc_method_invocation)
    finally:
        room._room_queue.unsubscribe(subscriber)


async def test_publish_and_unpublish_complete_through_room_subscription(
    connected_room: tuple[rtc.Room, FfiQueue[proto_ffi.FfiEvent]],
) -> None:
    room, _ = connected_room
    track = rtc.LocalAudioTrack(proto_track.OwnedTrack())
    participant = room.local_participant

    publication = await asyncio.wait_for(participant.publish_track(track), 1)
    assert participant.track_publications["TR_test"] is publication
    assert publication.track is track

    await asyncio.wait_for(participant.unpublish_track(publication.sid), 1)
    assert not participant.track_publications
    assert publication.track is None
