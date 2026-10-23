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
from livekit.rtc import ConnectionState
from livekit.rtc._proto import ffi_pb2 as proto_ffi


@pytest.mark.asyncio
async def test_room_sid_disconnected_raises_runtime_error() -> None:
    room = rtc.Room()
    with pytest.raises(RuntimeError, match="cannot get sid of a disconnected room"):
        await room.sid


@pytest.mark.asyncio
async def test_room_sid_resolution() -> None:
    room = rtc.Room()
    room._connection_state = ConnectionState.CONN_CONNECTED

    async def resolve_soon() -> None:
        await asyncio.sleep(0.01)
        room._resolve_first_sid("RM_test123")

    task = asyncio.create_task(resolve_soon())
    sid = await room.sid
    await task
    assert sid == "RM_test123"
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


@pytest.mark.asyncio
async def test_connect_cancellation_fails_sid_future_and_cleans_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    room = rtc.Room()

    # Mock FfiClient request to never answer connect response
    def mock_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        resp = proto_ffi.FfiResponse()
        resp.connect.async_id = 9999
        return resp

    monkeypatch.setattr(rtc._ffi_client.FfiClient.instance, "request", mock_request)

    connect_task = asyncio.create_task(room.connect("ws://dummy", "dummy_token"))
    await asyncio.sleep(0.01)

    assert room._is_connecting

    async def wait_sid() -> None:
        await room.sid

    sid_task = asyncio.create_task(wait_sid())
    await asyncio.sleep(0.01)

    connect_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await connect_task

    assert not room._is_connecting
    with pytest.raises(RuntimeError, match="room connection was cancelled"):
        await sid_task
