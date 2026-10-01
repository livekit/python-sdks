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
from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from livekit.api import CreateRoomRequest, LiveKitAPI, Room
from livekit.api import twirp_client
from livekit.api.twirp_client import REQUEST_ID_HEADER, TwirpClient


@pytest.mark.parametrize("base_path", ["", "/", "/livekit", "/proxy/livekit/"])
@pytest.mark.parametrize("scheme", ["http", "ws"])
def test_api_request_preserves_base_path(base_path: str, scheme: str) -> None:
    async def run() -> None:
        async def create_room(request: web.Request) -> web.Response:
            message = CreateRoomRequest.FromString(await request.read())
            assert message.name == "test-room"
            assert request.headers["Authorization"] == "Bearer test-token"
            return web.Response(body=Room(name=message.name).SerializeToString())

        app = web.Application()
        app.router.add_post(
            f"{base_path.rstrip('/')}/twirp/livekit.RoomService/CreateRoom", create_room
        )
        async with TestServer(app) as server:
            url = str(server.make_url(base_path)).replace("http://", f"{scheme}://", 1)
            async with LiveKitAPI.with_token("test-token", url, failover=False) as api:
                room = await api.room.create_room(CreateRoomRequest(name="test-room"))
            assert room.name == "test-room"

    asyncio.run(run())


@pytest.mark.parametrize("prefix", ["twirp", "custom/twirp"])
def test_failover_preserves_base_path(monkeypatch: pytest.MonkeyPatch, prefix: str) -> None:
    async def run() -> None:
        requests = []

        async def record_request(request: web.Request) -> None:
            requests.append(
                (request.path, request.headers[REQUEST_ID_HEADER], await request.read())
            )

        async def primary(request: web.Request) -> web.Response:
            await record_request(request)
            return web.json_response({"code": "unavailable", "msg": "retry"}, status=503)

        async def fallback(request: web.Request) -> web.Response:
            await record_request(request)
            return web.Response(body=Room(name="test-room").SerializeToString())

        route = f"/proxy/livekit/{prefix}/livekit.RoomService/CreateRoom"
        primary_app = web.Application()
        primary_app.router.add_post(route, primary)
        fallback_app = web.Application()
        fallback_app.router.add_post(route, fallback)
        async with TestServer(primary_app) as first, TestServer(fallback_app) as second:
            discover = AsyncMock(return_value=[str(second.make_url("")).rstrip("/")])
            monkeypatch.setattr(twirp_client._REGION_CACHE, "region_origins", discover)
            async with aiohttp.ClientSession() as session:
                client = TwirpClient(
                    session,
                    str(first.make_url("/proxy/livekit/")),
                    "livekit",
                    prefix=prefix,
                    _failover_force=True,
                    _failover_backoff=0,
                )
                room = await client.request(
                    "RoomService", "CreateRoom", CreateRoomRequest(name="test-room"), {}, Room
                )
            assert room.name == "test-room"
            assert len(requests) == 2
            assert requests[0] == requests[1]
            assert requests[0][0] == route
            assert requests[0][1]
            discover.assert_awaited_once()

    asyncio.run(run())
