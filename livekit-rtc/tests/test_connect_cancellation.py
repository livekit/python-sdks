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
from livekit.rtc import room as room_mod
from livekit.rtc._ffi_client import FfiClient
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from utils import wait_until  # type: ignore[import-not-found]

CONNECT_ASYNC_ID = 101
DISCONNECT_ASYNC_ID = 202
ROOM_HANDLE = 7


class _FakeHandle:
    """Stand-in for FfiHandle so a made-up handle id is never dropped natively."""

    def __init__(self, handle: int) -> None:
        self.handle = handle


def _install_fake_ffi(monkeypatch: pytest.MonkeyPatch) -> list[proto_ffi.FfiRequest]:
    """Record every FfiRequest and answer the ones the cancel path waits on."""
    requests: list[proto_ffi.FfiRequest] = []

    def fake_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        requests.append(req)
        resp = proto_ffi.FfiResponse()
        which = req.WhichOneof("message")
        if which == "connect":
            # the connect callback is delivered by the test, not here
            resp.connect.async_id = CONNECT_ASYNC_ID
        elif which == "disconnect":
            resp.disconnect.async_id = DISCONNECT_ASYNC_ID
            event = proto_ffi.FfiEvent()
            event.disconnect.async_id = DISCONNECT_ASYNC_ID
            FfiClient.instance.queue.put(event)
        return resp

    monkeypatch.setattr(FfiClient.instance, "request", fake_request)
    monkeypatch.setattr(room_mod, "FfiHandle", _FakeHandle)
    return requests


def _deliver_connect_callback() -> None:
    event = proto_ffi.FfiEvent()
    event.connect.async_id = CONNECT_ASYNC_ID
    event.connect.result.room.handle.id = ROOM_HANDLE
    FfiClient.instance.queue.put(event)


async def test_cancelled_connect_answers_ready_and_closes_the_room(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests = _install_fake_ffi(monkeypatch)
    subscribers_before = len(FfiClient.instance.queue._subscribers)

    room = rtc.Room()
    task = asyncio.create_task(room.connect("ws://localhost:7880", "token"))
    await wait_until(lambda: bool(requests), message="connect request never issued")

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    # the FFI server does not cancel an in-flight connect: it answers, then waits for
    # ReadyForRoomEvent. an unanswered wait panics it and the panic kills the process.
    _deliver_connect_callback()
    await room.disconnect()

    assert [req.WhichOneof("message") for req in requests] == [
        "connect",
        "ready_for_room_event",
        "disconnect",
    ]
    assert requests[1].ready_for_room_event.room_handle == ROOM_HANDLE
    assert requests[2].disconnect.room_handle == ROOM_HANDLE
    assert len(FfiClient.instance.queue._subscribers) == subscribers_before


async def test_cancelled_connect_leaves_no_pending_work_when_the_server_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests = _install_fake_ffi(monkeypatch)
    subscribers_before = len(FfiClient.instance.queue._subscribers)

    room = rtc.Room()
    task = asyncio.create_task(room.connect("ws://localhost:7880", "token"))
    await wait_until(lambda: bool(requests), message="connect request never issued")

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    event = proto_ffi.FfiEvent()
    event.connect.async_id = CONNECT_ASYNC_ID
    event.connect.error = "could not connect"
    FfiClient.instance.queue.put(event)
    await room.disconnect()

    # there is no room to close, so nothing follows the connect
    assert [req.WhichOneof("message") for req in requests] == ["connect"]
    assert len(FfiClient.instance.queue._subscribers) == subscribers_before
