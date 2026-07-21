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

"""Regression test for unpublish_track deadlocking the room event loop.

When the FFI reports an unpublish error, unpublish_track raises. If it raises
before marking its room-queue event done, Room._listen_task's join() blocks on
that unconsumed event forever and the room stops processing events.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from livekit import rtc
from livekit.rtc._ffi_client import FfiClient
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._utils import BroadcastQueue
from livekit.rtc.participant import UnpublishTrackError

_ASYNC_ID = 4242


async def test_unpublish_track_error_does_not_deadlock_room_queue() -> None:
    room_queue: BroadcastQueue[proto_ffi.FfiEvent] = BroadcastQueue()

    participant = rtc.LocalParticipant.__new__(rtc.LocalParticipant)
    participant._room_queue = room_queue
    participant._ffi_handle = MagicMock(handle=1)
    participant._track_publications = {}

    resp = proto_ffi.FfiResponse()
    resp.unpublish_track.async_id = _ASYNC_ID

    error_event = proto_ffi.FfiEvent()
    error_event.unpublish_track.async_id = _ASYNC_ID
    error_event.unpublish_track.error = "unpublish failed"

    async def deliver_event_like_listen_task() -> None:
        # Mirror Room._listen_task: hand the event to subscribers, then wait for
        # them to finish before moving on to the next event.
        room_queue.put_nowait(error_event)
        await room_queue.join()

    with patch.object(FfiClient.instance, "request", return_value=resp):
        unpublish = asyncio.ensure_future(participant.unpublish_track("TR_test"))
        await asyncio.sleep(0)  # let unpublish subscribe before the event is delivered
        listen = asyncio.ensure_future(deliver_event_like_listen_task())

        with pytest.raises(UnpublishTrackError):
            await unpublish

        try:
            await asyncio.wait_for(listen, timeout=5)
        except asyncio.TimeoutError:
            listen.cancel()
            pytest.fail("room queue join() deadlocked after unpublish_track error")
