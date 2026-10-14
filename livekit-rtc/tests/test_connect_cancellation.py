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


class _FakeFfi:
    """Records every FfiRequest and dropped handle, and answers the requests the
    cancel path waits on the way the FFI server does."""

    def __init__(self) -> None:
        self.requests: list[proto_ffi.FfiRequest] = []
        self.disposed: list[int] = []
        # room events the server emits once the SDK says it is ready, by room handle
        self.events_after_ready: dict[int, list[proto_ffi.FfiEvent]] = {}
        self._next_connect_id = CONNECT_ASYNC_ID
        self._next_disconnect_id = DISCONNECT_ASYNC_ID

    def kinds(self) -> list[str]:
        return [req.WhichOneof("message") for req in self.requests]

    def request(self, req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        self.requests.append(req)
        resp = proto_ffi.FfiResponse()
        which = req.WhichOneof("message")
        if which == "connect":
            # the connect callback is delivered by the test, not here
            resp.connect.async_id = self._next_connect_id
            self._next_connect_id += 1
        elif which == "ready_for_room_event":
            for event in self.events_after_ready.pop(req.ready_for_room_event.room_handle, []):
                FfiClient.instance.queue.put(event)
        elif which == "disconnect":
            resp.disconnect.async_id = self._next_disconnect_id
            self._next_disconnect_id += 1
            event = proto_ffi.FfiEvent()
            event.disconnect.async_id = resp.disconnect.async_id
            FfiClient.instance.queue.put(event)
            eos = proto_ffi.FfiEvent()
            eos.room_event.room_handle = req.disconnect.room_handle
            eos.room_event.eos.SetInParent()
            FfiClient.instance.queue.put(eos)
        return resp


def _install_fake_ffi(monkeypatch: pytest.MonkeyPatch) -> _FakeFfi:
    fake = _FakeFfi()

    class _FakeHandle:
        """Stand-in for FfiHandle so a made-up handle id is never dropped natively."""

        def __init__(self, handle: int) -> None:
            self.handle = handle

        def dispose(self) -> None:
            fake.disposed.append(self.handle)

    monkeypatch.setattr(FfiClient.instance, "request", fake.request)
    monkeypatch.setattr(room_mod, "FfiHandle", _FakeHandle)
    return fake


def _deliver_connect_callback(
    async_id: int = CONNECT_ASYNC_ID, room_handle: int = ROOM_HANDLE
) -> proto_ffi.FfiEvent:
    event = proto_ffi.FfiEvent()
    event.connect.async_id = async_id
    event.connect.result.room.handle.id = room_handle
    FfiClient.instance.queue.put(event)
    return event


async def _cancelled_connect(room: rtc.Room, fake: _FakeFfi) -> None:
    sent = len(fake.requests)
    task = asyncio.create_task(room.connect("ws://localhost:7880", "token"))
    await wait_until(lambda: len(fake.requests) > sent, message="connect request never issued")
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_cancelled_connect_answers_ready_and_closes_the_room(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _install_fake_ffi(monkeypatch)
    requests = fake.requests
    subscribers_before = len(FfiClient.instance.queue._subscribers)

    room = rtc.Room()
    await _cancelled_connect(room, fake)

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
    assert fake.disposed == [ROOM_HANDLE]
    assert len(FfiClient.instance.queue._subscribers) == subscribers_before


async def test_cancelled_connect_leaves_no_pending_work_when_the_server_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _install_fake_ffi(monkeypatch)
    subscribers_before = len(FfiClient.instance.queue._subscribers)

    room = rtc.Room()
    await _cancelled_connect(room, fake)

    event = proto_ffi.FfiEvent()
    event.connect.async_id = CONNECT_ASYNC_ID
    event.connect.error = "could not connect"
    FfiClient.instance.queue.put(event)
    await room.disconnect()

    # there is no room to close, so nothing follows the connect
    assert fake.kinds() == ["connect"]
    assert fake.disposed == []
    assert len(FfiClient.instance.queue._subscribers) == subscribers_before


async def test_a_cancelled_disconnect_still_lets_the_cleanup_finish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Giving up on disconnect() must not cancel the cleanup it is waiting on.

    gather() cancels its children when it is cancelled, so a caller who bounds
    disconnect() with a timeout, or abandons it on shutdown, would cancel the
    task that answers the FFI's wait for ReadyForRoomEvent. The wait then times
    out, the FFI panics, and the panic handler kills the process: the exact
    failure the rest of this file is about, reintroduced one layer up.
    """
    fake = _install_fake_ffi(monkeypatch)
    subscribers_before = len(FfiClient.instance.queue._subscribers)

    room = rtc.Room()
    await _cancelled_connect(room, fake)

    # the cleanup is now parked on the connect callback, which has not arrived
    closing = asyncio.create_task(room.disconnect())
    await asyncio.sleep(0)
    closing.cancel()
    with pytest.raises(asyncio.CancelledError):
        await closing

    _deliver_connect_callback()
    await asyncio.gather(*room._aborted_connect_tasks)

    assert fake.kinds() == ["connect", "ready_for_room_event", "disconnect"]
    assert fake.requests[1].ready_for_room_event.room_handle == ROOM_HANDLE
    assert fake.requests[2].disconnect.room_handle == ROOM_HANDLE
    assert len(FfiClient.instance.queue._subscribers) == subscribers_before


async def test_a_retry_on_the_same_room_waits_for_the_cancelled_attempt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A retry loop like `wait_for(room.connect(...), 0.2)` with no disconnect().

    If the retry joined while the cancelled attempt was still in flight, the
    server would evict whichever session came second as DUPLICATE_IDENTITY and
    the cleanup would then close the other, leaving the caller a dead room.
    """
    fake = _install_fake_ffi(monkeypatch)
    subscribers_before = len(FfiClient.instance.queue._subscribers)

    room = rtc.Room()
    await _cancelled_connect(room, fake)

    retry = asyncio.create_task(room.connect("ws://localhost:7880", "token"))
    for _ in range(5):
        await asyncio.sleep(0)
    assert fake.kinds() == ["connect"], "the retry joined before the first attempt left"

    # the first attempt's join completes, and its cleanup closes it
    _deliver_connect_callback(CONNECT_ASYNC_ID, ROOM_HANDLE)
    await wait_until(lambda: len(fake.requests) == 4, message="the retry never connected")
    _deliver_connect_callback(CONNECT_ASYNC_ID + 1, ROOM_HANDLE + 1)
    await retry

    assert fake.kinds() == [
        "connect",
        "ready_for_room_event",
        "disconnect",
        "connect",
        "ready_for_room_event",
    ]
    assert fake.requests[2].disconnect.room_handle == ROOM_HANDLE
    assert fake.requests[4].ready_for_room_event.room_handle == ROOM_HANDLE + 1
    assert room.isconnected()

    await room.disconnect()
    assert fake.requests[-1].disconnect.room_handle == ROOM_HANDLE + 1
    assert len(FfiClient.instance.queue._subscribers) == subscribers_before


async def test_a_cancelled_connect_into_a_populated_room_drops_every_handle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Nothing owns the participants and publications a cancelled connect gets back,
    nor the ones in room events sent before the disconnect, so the cleanup has to
    drop their handles or a worker that keeps timing out connects leaks them."""
    fake = _install_fake_ffi(monkeypatch)

    room = rtc.Room()
    await _cancelled_connect(room, fake)

    joined = proto_ffi.FfiEvent()
    joined.room_event.room_handle = ROOM_HANDLE
    joined.room_event.participant_connected.info.handle.id = 14
    fake.events_after_ready[ROOM_HANDLE] = [joined]

    event = proto_ffi.FfiEvent()
    event.connect.async_id = CONNECT_ASYNC_ID
    result = event.connect.result
    result.room.handle.id = ROOM_HANDLE
    result.local_participant.handle.id = 11
    remote = result.participants.add()
    remote.participant.handle.id = 12
    remote.publications.add().handle.id = 13
    FfiClient.instance.queue.put(event)
    await room.disconnect()

    assert fake.kinds() == ["connect", "ready_for_room_event", "disconnect"]
    assert sorted(fake.disposed) == [ROOM_HANDLE, 11, 12, 13, 14]
    # the room goes last, after everything it owned
    assert fake.disposed[-1] == ROOM_HANDLE


async def test_an_exit_other_than_cancellation_still_closes_the_room(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GeneratorExit (a coroutine closed during shutdown) or KeyboardInterrupt at the
    connect await must hand the room off too, or the FFI is left waiting."""
    fake = _install_fake_ffi(monkeypatch)
    subscribers_before = len(FfiClient.instance.queue._subscribers)

    room = rtc.Room()
    coro = room.connect("ws://localhost:7880", "token")
    coro.send(None)  # runs up to the await on the connect callback
    assert fake.kinds() == ["connect"]
    coro.close()  # raises GeneratorExit at that await

    _deliver_connect_callback()
    await room.disconnect()

    assert fake.kinds() == ["connect", "ready_for_room_event", "disconnect"]
    assert len(FfiClient.instance.queue._subscribers) == subscribers_before
