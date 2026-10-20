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

from __future__ import annotations

import asyncio
from typing import Any
import pytest

from livekit.rtc import Room
from livekit.rtc._ffi_client import FfiClient, FfiHandle
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._proto.participant_pb2 import DisconnectReason


async def _wait_until_dropped(
    dropped_handles: list[int], expected_handle: int, timeout: float = 2.0
) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if dropped_handles == [expected_handle]:
            return
        await asyncio.sleep(0.01)
    assert dropped_handles == [expected_handle]


@pytest.mark.asyncio
async def test_room_connect_cancelled_during_handshake_cleans_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    room = Room()
    dropped_handles: list[int] = []
    ready_requests: list[int] = []
    disconnect_requests: list[tuple[int, int]] = []

    connect_async_id = 101
    disconnect_async_id = 202
    fake_room_handle_id = 9999

    def fake_dispose(self: FfiHandle) -> None:
        if self.handle != 0 and not self._disposed:
            self._disposed = True
            dropped_handles.append(self.handle)

    monkeypatch.setattr(FfiHandle, "dispose", fake_dispose)

    def fake_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        which = req.WhichOneof("message")
        if which == "connect":
            resp = proto_ffi.FfiResponse()
            resp.connect.async_id = connect_async_id
            return resp
        elif which == "ready_for_room_event":
            ready_requests.append(req.ready_for_room_event.room_handle)
            return proto_ffi.FfiResponse()
        elif which == "disconnect":
            disconnect_requests.append((req.disconnect.room_handle, req.disconnect.reason))
            resp = proto_ffi.FfiResponse()
            resp.disconnect.async_id = disconnect_async_id

            # Simulate the disconnect callback from native FFI
            disc_cb = proto_ffi.FfiEvent()
            disc_cb.disconnect.async_id = disconnect_async_id
            FfiClient.instance.queue.put(disc_cb)
            return resp
        raise AssertionError(f"unexpected request: {which}")

    monkeypatch.setattr(FfiClient.instance, "request", fake_request)

    connect_task = asyncio.create_task(room.connect("ws://127.0.0.1:7880", "fake-token"))

    # Yield to let connect() dispatch ConnectRequest and park waiting on queue
    await asyncio.sleep(0)
    assert not connect_task.done()

    # Cancel the connect task
    connect_task.cancel()

    # Yield to deliver cancellation
    await asyncio.sleep(0)

    # Now deliver the ConnectCallback from native FFI
    connect_cb = proto_ffi.FfiEvent()
    connect_cb.connect.async_id = connect_async_id
    connect_cb.connect.result.room.handle.id = fake_room_handle_id
    FfiClient.instance.queue.put(connect_cb)

    # Wait for the task to finish cancellation
    with pytest.raises(asyncio.CancelledError):
        await connect_task

    # Allow background cleanup task to process the connect callback
    await _wait_until_dropped(dropped_handles, fake_room_handle_id)

    # Verify:
    # 1. ready_for_room_event was dispatched to satisfy 15s timer (Fixes #784)
    assert ready_requests == [fake_room_handle_id]

    # 2. disconnect was dispatched to prevent ghost session / duplicate identity (Fixes #804)
    assert len(disconnect_requests) == 1
    assert disconnect_requests[0][0] == fake_room_handle_id
    assert disconnect_requests[0][1] == DisconnectReason.CLIENT_INITIATED

    # 3. Handle was properly dropped in native FFI
    assert dropped_handles == [fake_room_handle_id]

    # 4. Room state remains disconnected
    assert not room.isconnected()


@pytest.mark.asyncio
async def test_room_connect_cancelled_when_connect_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    room = Room()
    ready_requests: list[int] = []
    disconnect_requests: list[int] = []
    connect_async_id = 303

    def fake_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        which = req.WhichOneof("message")
        if which == "connect":
            resp = proto_ffi.FfiResponse()
            resp.connect.async_id = connect_async_id
            return resp
        elif which == "ready_for_room_event":
            ready_requests.append(req.ready_for_room_event.room_handle)
            return proto_ffi.FfiResponse()
        elif which == "disconnect":
            disconnect_requests.append(req.disconnect.room_handle)
            return proto_ffi.FfiResponse()
        raise AssertionError(f"unexpected request: {which}")

    monkeypatch.setattr(FfiClient.instance, "request", fake_request)

    connect_task = asyncio.create_task(room.connect("ws://127.0.0.1:7880", "fake-token"))

    await asyncio.sleep(0)
    connect_task.cancel()
    await asyncio.sleep(0)

    # Deliver a connection error callback
    connect_cb = proto_ffi.FfiEvent()
    connect_cb.connect.async_id = connect_async_id
    connect_cb.connect.error = "Connection refused"
    FfiClient.instance.queue.put(connect_cb)

    with pytest.raises(asyncio.CancelledError):
        await connect_task

    # No ready or disconnect request should be sent if connect failed
    assert ready_requests == []
    assert disconnect_requests == []
    assert not room.isconnected()


@pytest.mark.asyncio
async def test_room_connect_wait_for_timeout_cancellation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    room = Room()
    dropped_handles: list[int] = []
    ready_requests: list[int] = []
    disconnect_requests: list[int] = []

    connect_async_id = 404
    disconnect_async_id = 505
    fake_room_handle_id = 8888

    def fake_dispose(self: FfiHandle) -> None:
        if self.handle != 0 and not self._disposed:
            self._disposed = True
            dropped_handles.append(self.handle)

    monkeypatch.setattr(FfiHandle, "dispose", fake_dispose)

    def fake_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        which = req.WhichOneof("message")
        if which == "connect":
            resp = proto_ffi.FfiResponse()
            resp.connect.async_id = connect_async_id
            return resp
        elif which == "ready_for_room_event":
            ready_requests.append(req.ready_for_room_event.room_handle)
            return proto_ffi.FfiResponse()
        elif which == "disconnect":
            disconnect_requests.append(req.disconnect.room_handle)
            resp = proto_ffi.FfiResponse()
            resp.disconnect.async_id = disconnect_async_id

            disc_cb = proto_ffi.FfiEvent()
            disc_cb.disconnect.async_id = disconnect_async_id
            FfiClient.instance.queue.put(disc_cb)
            return resp
        raise AssertionError(f"unexpected request: {which}")

    monkeypatch.setattr(FfiClient.instance, "request", fake_request)

    async def _delayed_connect_cb() -> None:
        await asyncio.sleep(0.05)
        connect_cb = proto_ffi.FfiEvent()
        connect_cb.connect.async_id = connect_async_id
        connect_cb.connect.result.room.handle.id = fake_room_handle_id
        FfiClient.instance.queue.put(connect_cb)

    asyncio.create_task(_delayed_connect_cb())

    # Wait with a short timeout that triggers cancellation
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(room.connect("ws://127.0.0.1:7880", "fake-token"), timeout=0.01)

    # Allow delayed callback and background cleanup task to run
    await _wait_until_dropped(dropped_handles, fake_room_handle_id)

    # Handshake cleanup was satisfied
    assert ready_requests == [fake_room_handle_id]
    assert disconnect_requests == [fake_room_handle_id]
    assert dropped_handles == [fake_room_handle_id]
    assert not room.isconnected()


@pytest.mark.asyncio
async def test_room_connect_setup_failure_cleans_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    room = Room()
    dropped_handles: list[int] = []
    ready_requests: list[int] = []
    disconnect_requests: list[int] = []

    connect_async_id = 606
    disconnect_async_id = 707
    fake_room_handle_id = 7777

    def fake_dispose(self: FfiHandle) -> None:
        if self.handle != 0 and not self._disposed:
            self._disposed = True
            dropped_handles.append(self.handle)

    monkeypatch.setattr(FfiHandle, "dispose", fake_dispose)

    def fake_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        which = req.WhichOneof("message")
        if which == "connect":
            resp = proto_ffi.FfiResponse()
            resp.connect.async_id = connect_async_id
            return resp
        elif which == "ready_for_room_event":
            ready_requests.append(req.ready_for_room_event.room_handle)
            return proto_ffi.FfiResponse()
        elif which == "disconnect":
            disconnect_requests.append(req.disconnect.room_handle)
            resp = proto_ffi.FfiResponse()
            resp.disconnect.async_id = disconnect_async_id

            disc_cb = proto_ffi.FfiEvent()
            disc_cb.disconnect.async_id = disconnect_async_id
            FfiClient.instance.queue.put(disc_cb)
            return resp
        raise AssertionError(f"unexpected request: {which}")

    monkeypatch.setattr(FfiClient.instance, "request", fake_request)

    # Force an exception during room setup before ready_for_room_event
    def faulty_create_remote_participant(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("simulated setup explosion")

    monkeypatch.setattr(room, "_create_remote_participant", faulty_create_remote_participant)

    async def _deliver_cb() -> None:
        await asyncio.sleep(0.01)
        connect_cb = proto_ffi.FfiEvent()
        connect_cb.connect.async_id = connect_async_id
        connect_cb.connect.result.room.handle.id = fake_room_handle_id
        # Add a participant to trigger faulty_create_remote_participant
        p = connect_cb.connect.result.participants.add()
        p.participant.info.identity = "remote_1"
        FfiClient.instance.queue.put(connect_cb)

    asyncio.create_task(_deliver_cb())

    with pytest.raises(RuntimeError, match="simulated setup explosion"):
        await room.connect("ws://127.0.0.1:7880", "fake-token")

    # Handshake cleanup was satisfied even on exception during setup
    assert ready_requests == [fake_room_handle_id]
    assert disconnect_requests == [fake_room_handle_id]
    assert dropped_handles == [fake_room_handle_id]
    assert not room.isconnected()
    # Ensure failed setup does not leave stale participants or unreset state
    assert len(room.remote_participants) == 0
    assert room._local_participant is None


@pytest.mark.asyncio
async def test_room_connect_repeated_cancellation_during_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    room = Room()
    dropped_handles: list[int] = []
    ready_requests: list[int] = []
    disconnect_requests: list[int] = []

    connect_async_id = 808
    disconnect_async_id = 909
    fake_room_handle_id = 5555

    def fake_dispose(self: FfiHandle) -> None:
        if self.handle != 0 and not self._disposed:
            self._disposed = True
            dropped_handles.append(self.handle)

    monkeypatch.setattr(FfiHandle, "dispose", fake_dispose)

    def fake_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        which = req.WhichOneof("message")
        if which == "connect":
            resp = proto_ffi.FfiResponse()
            resp.connect.async_id = connect_async_id
            return resp
        elif which == "ready_for_room_event":
            ready_requests.append(req.ready_for_room_event.room_handle)
            return proto_ffi.FfiResponse()
        elif which == "disconnect":
            disconnect_requests.append(req.disconnect.room_handle)
            resp = proto_ffi.FfiResponse()
            resp.disconnect.async_id = disconnect_async_id

            disc_cb = proto_ffi.FfiEvent()
            disc_cb.disconnect.async_id = disconnect_async_id
            FfiClient.instance.queue.put(disc_cb)
            return resp
        raise AssertionError(f"unexpected request: {which}")

    monkeypatch.setattr(FfiClient.instance, "request", fake_request)

    connect_task = asyncio.create_task(room.connect("ws://127.0.0.1:7880", "fake-token"))

    await asyncio.sleep(0)
    # Repeated cancellation before callback arrives
    connect_task.cancel()
    connect_task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await connect_task

    # Deliver connect callback; background cleanup task handles it
    connect_cb = proto_ffi.FfiEvent()
    connect_cb.connect.async_id = connect_async_id
    connect_cb.connect.result.room.handle.id = fake_room_handle_id
    FfiClient.instance.queue.put(connect_cb)

    await _wait_until_dropped(dropped_handles, fake_room_handle_id)

    assert ready_requests == [fake_room_handle_id]
    assert disconnect_requests == [fake_room_handle_id]
    assert dropped_handles == [fake_room_handle_id]
    assert not room.isconnected()


@pytest.mark.asyncio
async def test_room_connect_subsequent_connect_waits_for_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    room = Room()
    dropped_handles: list[int] = []
    ready_requests: list[int] = []
    disconnect_requests: list[int] = []
    connect_requests: list[str] = []

    fake_room_handle_id = 42
    connect_async_id_1 = 101
    connect_async_id_2 = 102
    disconnect_async_id = 202

    def fake_dispose(self: FfiHandle) -> None:
        if not self._disposed:
            self._disposed = True
            dropped_handles.append(self.handle)

    monkeypatch.setattr(FfiHandle, "dispose", fake_dispose)

    call_count = 0

    def fake_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        nonlocal call_count
        which = req.WhichOneof("message")
        if which == "connect":
            call_count += 1
            connect_requests.append(req.connect.token)
            resp = proto_ffi.FfiResponse()
            resp.connect.async_id = connect_async_id_1 if call_count == 1 else connect_async_id_2
            return resp
        elif which == "ready_for_room_event":
            ready_requests.append(req.ready_for_room_event.room_handle)
            return proto_ffi.FfiResponse()
        elif which == "disconnect":
            disconnect_requests.append(req.disconnect.room_handle)
            resp = proto_ffi.FfiResponse()
            resp.disconnect.async_id = disconnect_async_id
            disc_cb = proto_ffi.FfiEvent()
            disc_cb.disconnect.async_id = disconnect_async_id
            FfiClient.instance.queue.put(disc_cb)
            return resp
        raise AssertionError(f"unexpected request: {which}")

    monkeypatch.setattr(FfiClient.instance, "request", fake_request)

    # First attempt cancelled while connect is in flight
    connect_task1 = asyncio.create_task(room.connect("ws://127.0.0.1:7880", "token-1"))
    await asyncio.sleep(0)
    connect_task1.cancel()

    with pytest.raises(asyncio.CancelledError):
        await connect_task1

    assert room.cleanup_task is not None
    assert not room.cleanup_task.done()

    # Second connect attempt started immediately
    connect_task2 = asyncio.create_task(room.connect("ws://127.0.0.1:7880", "token-2"))
    await asyncio.sleep(0)

    # The second attempt must NOT have dispatched req.connect yet because cleanup is pending
    assert len(connect_requests) == 1

    # Now deliver connect callback for attempt 1
    connect_cb1 = proto_ffi.FfiEvent()
    connect_cb1.connect.async_id = connect_async_id_1
    connect_cb1.connect.result.room.handle.id = fake_room_handle_id
    FfiClient.instance.queue.put(connect_cb1)

    # Cleanup finishes and second connect proceeds to send request
    await _wait_until_dropped(dropped_handles, fake_room_handle_id)
    assert len(connect_requests) == 2
    assert connect_requests == ["token-1", "token-2"]

    # Cancel task 2 to finish cleanly
    connect_task2.cancel()
    with pytest.raises(asyncio.CancelledError):
        await connect_task2
