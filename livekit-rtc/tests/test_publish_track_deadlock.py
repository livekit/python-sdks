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

"""Regression tests for publish_track and unpublish_track room queue lifecycle.

When the FFI reports a publish or unpublish error, publish_track/unpublish_track raises.
The event returned by queue.wait_for() must be marked done immediately so that
Room._listen_task's join() does not remain blocked on the unconsumed event.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from livekit import rtc
from livekit.rtc._ffi_client import FfiClient
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._utils import BroadcastQueue, Queue
from livekit.rtc.participant import PublishTrackError, UnpublishTrackError

_ASYNC_ID = 54321


@pytest.mark.asyncio
async def test_publish_track_marks_event_done_before_raising_error() -> None:
    """Verify that publish_track marks the event done immediately upon receipt,

    even when the FFI event reports an error. It must not rely solely on
    unsubscription release to account for the event.
    """
    room_queue: BroadcastQueue[proto_ffi.FfiEvent] = BroadcastQueue()

    participant = rtc.LocalParticipant.__new__(rtc.LocalParticipant)
    participant._room_queue = room_queue
    participant._ffi_handle = MagicMock(handle=1)
    participant._track_publications = {}

    track = MagicMock()
    track._ffi_handle = MagicMock(handle=2)

    resp = proto_ffi.FfiResponse()
    resp.publish_track.async_id = _ASYNC_ID

    error_event = proto_ffi.FfiEvent()
    error_event.publish_track.async_id = _ASYNC_ID
    error_event.publish_track.error = "publish track failed"

    called_while_subscribed = False

    orig_subscribe = room_queue.subscribe

    def spy_subscribe() -> Queue[proto_ffi.FfiEvent]:
        q = orig_subscribe()
        orig_task_done = q.task_done

        def spy_task_done() -> None:
            nonlocal called_while_subscribed
            if q in room_queue._subscribers:
                called_while_subscribed = True
            orig_task_done()

        q.task_done = spy_task_done  # type: ignore[method-assign]
        return q

    room_queue.subscribe = spy_subscribe  # type: ignore[method-assign]

    with patch.object(FfiClient.instance, "request", return_value=resp):
        pub_task = asyncio.create_task(participant.publish_track(track))
        await asyncio.sleep(0)  # let publish_track subscribe

        room_queue.put_nowait(error_event)

        with pytest.raises(PublishTrackError, match="publish track failed"):
            await pub_task

    assert called_while_subscribed, (
        "queue.task_done() was not called for the event while the subscriber was active"
    )


@pytest.mark.asyncio
async def test_publish_track_error_releases_room_queue_join() -> None:
    """Verify that Room._listen_task's join() finishes cleanly when publish_track fails."""
    room_queue: BroadcastQueue[proto_ffi.FfiEvent] = BroadcastQueue()

    participant = rtc.LocalParticipant.__new__(rtc.LocalParticipant)
    participant._room_queue = room_queue
    participant._ffi_handle = MagicMock(handle=1)
    participant._track_publications = {}

    track = MagicMock()
    track._ffi_handle = MagicMock(handle=2)

    resp = proto_ffi.FfiResponse()
    resp.publish_track.async_id = _ASYNC_ID

    error_event = proto_ffi.FfiEvent()
    error_event.publish_track.async_id = _ASYNC_ID
    error_event.publish_track.error = "publish track failed"

    async def deliver_event_like_listen_task() -> None:
        room_queue.put_nowait(error_event)
        await room_queue.join()

    with patch.object(FfiClient.instance, "request", return_value=resp):
        pub_task = asyncio.create_task(participant.publish_track(track))
        await asyncio.sleep(0)
        listen_task = asyncio.create_task(deliver_event_like_listen_task())

        try:
            with pytest.raises(PublishTrackError):
                await pub_task

            try:
                await asyncio.wait_for(listen_task, timeout=2.0)
            except asyncio.TimeoutError:
                pytest.fail("room queue join() deadlocked after publish_track error")
        finally:
            if not listen_task.done():
                listen_task.cancel()


@pytest.mark.asyncio
async def test_unpublish_track_marks_event_done_before_raising_error() -> None:
    """Verify that unpublish_track marks the event done immediately upon receipt,

    even when the FFI event reports an error. It must not rely solely on
    unsubscription release to account for the event.
    """
    room_queue: BroadcastQueue[proto_ffi.FfiEvent] = BroadcastQueue()

    participant = rtc.LocalParticipant.__new__(rtc.LocalParticipant)
    participant._room_queue = room_queue
    participant._ffi_handle = MagicMock(handle=1)
    participant._track_publications = {}

    resp = proto_ffi.FfiResponse()
    resp.unpublish_track.async_id = _ASYNC_ID

    error_event = proto_ffi.FfiEvent()
    error_event.unpublish_track.async_id = _ASYNC_ID
    error_event.unpublish_track.error = "unpublish track failed"

    called_while_subscribed = False

    orig_subscribe = room_queue.subscribe

    def spy_subscribe() -> Queue[proto_ffi.FfiEvent]:
        q = orig_subscribe()
        orig_task_done = q.task_done

        def spy_task_done() -> None:
            nonlocal called_while_subscribed
            if q in room_queue._subscribers:
                called_while_subscribed = True
            orig_task_done()

        q.task_done = spy_task_done  # type: ignore[method-assign]
        return q

    room_queue.subscribe = spy_subscribe  # type: ignore[method-assign]

    with patch.object(FfiClient.instance, "request", return_value=resp):
        unpub_task = asyncio.create_task(participant.unpublish_track("TR_test"))
        await asyncio.sleep(0)

        room_queue.put_nowait(error_event)

        with pytest.raises(UnpublishTrackError, match="unpublish track failed"):
            await unpub_task

    assert called_while_subscribed, (
        "queue.task_done() was not called for the event while the subscriber was active"
    )


@pytest.mark.asyncio
async def test_unpublish_track_error_releases_room_queue_join() -> None:
    """Verify that Room._listen_task's join() finishes cleanly when unpublish_track fails."""
    room_queue: BroadcastQueue[proto_ffi.FfiEvent] = BroadcastQueue()

    participant = rtc.LocalParticipant.__new__(rtc.LocalParticipant)
    participant._room_queue = room_queue
    participant._ffi_handle = MagicMock(handle=1)
    participant._track_publications = {}

    resp = proto_ffi.FfiResponse()
    resp.unpublish_track.async_id = _ASYNC_ID

    error_event = proto_ffi.FfiEvent()
    error_event.unpublish_track.async_id = _ASYNC_ID
    error_event.unpublish_track.error = "unpublish track failed"

    async def deliver_event_like_listen_task() -> None:
        room_queue.put_nowait(error_event)
        await room_queue.join()

    with patch.object(FfiClient.instance, "request", return_value=resp):
        unpub_task = asyncio.create_task(participant.unpublish_track("TR_test"))
        await asyncio.sleep(0)
        listen_task = asyncio.create_task(deliver_event_like_listen_task())

        try:
            with pytest.raises(UnpublishTrackError):
                await unpub_task

            try:
                await asyncio.wait_for(listen_task, timeout=2.0)
            except asyncio.TimeoutError:
                pytest.fail("room queue join() deadlocked after unpublish_track error")
        finally:
            if not listen_task.done():
                listen_task.cancel()
