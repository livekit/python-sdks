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

"""Failover tests that need no external mock server: the attempts policy, and
the retry loop against an in-process aiohttp server that has no fallback
regions (``/settings/regions`` is 404, as it is for cloud-api)."""

import asyncio
from typing import Callable, List

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer

from livekit.api import CreateRoomRequest, Room
from livekit.api.twirp_client import TwirpClient

Handler = Callable[[int, web.Request], "web.StreamResponse | None"]


async def _call_single_host(behave: Handler, attempts: List[int]) -> Room:
    """Runs one CreateRoom against a server whose only origin is itself and
    appends each attempt index to ``attempts``. ``behave(attempt, request)``
    returns a response, or None to drop the connection (a transport error with
    no HTTP response)."""

    async def twirp(request: web.Request) -> web.StreamResponse:
        attempt = len(attempts)
        attempts.append(attempt)
        resp = behave(attempt, request)
        if resp is None:
            assert request.transport is not None
            request.transport.close()
            raise web.HTTPServiceUnavailable()
        return resp

    app = web.Application()
    app.router.add_post("/twirp/livekit.RoomService/CreateRoom", twirp)
    async with TestServer(app) as server:
        async with aiohttp.ClientSession() as session:
            client = TwirpClient(
                session,
                str(server.make_url("")),
                "livekit",
                _failover_force=True,
                _failover_backoff=0.001,
            )
            return await client.request("RoomService", "CreateRoom", CreateRoomRequest(), {}, Room)


def _ok(request: web.Request) -> web.Response:
    return web.Response(body=Room(name="r").SerializeToString())


def test_retries_same_host_on_transport_error():
    """Without a fallback origin, a transport error retries the same host."""

    def behave(attempt: int, request: web.Request):
        return None if attempt == 0 else _ok(request)

    attempts: List[int] = []
    room = asyncio.run(_call_single_host(behave, attempts))
    assert room.name == "r"
    assert len(attempts) == 2


def test_retries_same_host_on_5xx():
    """Without a fallback origin, a 5xx retries the same host."""

    def behave(attempt: int, request: web.Request):
        if attempt == 0:
            return web.json_response({"code": "unavailable", "msg": "down"}, status=502)
        return _ok(request)

    attempts: List[int] = []
    room = asyncio.run(_call_single_host(behave, attempts))
    assert room.name == "r"
    assert len(attempts) == 2
