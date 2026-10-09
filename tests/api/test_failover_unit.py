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
import socket
from typing import Callable, List, Optional

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from livekit.api import CreateRoomRequest, Room
from livekit.api._failover import FAILOVER_MAX_ATTEMPTS, failover_attempts
from livekit.api.twirp_client import TwirpClient

Handler = Callable[[int, web.Request], "web.StreamResponse | None"]


class _StaticResolver(aiohttp.abc.AbstractResolver):
    """Resolves every hostname to the loopback address so a test server can be
    reached under an arbitrary name."""

    async def resolve(self, host: str, port: int = 0, family: int = socket.AF_INET) -> list:
        return [
            {
                "hostname": host,
                "host": "127.0.0.1",
                "port": port,
                "family": socket.AF_INET,
                "proto": 0,
                "flags": 0,
            }
        ]

    async def close(self) -> None:
        pass


async def _call_single_host(
    behave: Handler,
    attempts: List[int],
    *,
    host: str = "127.0.0.1",
    discovery_hits: Optional[List[None]] = None,
) -> Room:
    """Runs one CreateRoom against a server, reached as ``host``, whose only
    origin is itself; appends each attempt index to ``attempts`` and each
    ``/settings/regions`` hit to ``discovery_hits``. ``behave(attempt, request)``
    returns a response, or None to drop the connection (a transport error with
    no HTTP response)."""

    async def regions(request: web.Request) -> web.StreamResponse:
        if discovery_hits is not None:
            discovery_hits.append(None)
        raise web.HTTPNotFound()

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
    app.router.add_get("/settings/regions", regions)
    async with TestServer(app) as server:
        connector = aiohttp.TCPConnector(resolver=_StaticResolver())
        async with aiohttp.ClientSession(connector=connector) as session:
            client = TwirpClient(
                session,
                f"http://{host}:{server.port}",
                "livekit",
                _failover_force=host == "127.0.0.1",
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


def test_cloud_api_host_never_consults_region_discovery():
    """A Cloud API host retries the same host without any /settings/regions request."""

    def behave(attempt: int, request: web.Request):
        return None if attempt == 0 else _ok(request)

    attempts: List[int] = []
    hits: List[None] = []
    room = asyncio.run(
        _call_single_host(behave, attempts, host="cloud-api.livekit.io", discovery_hits=hits)
    )
    assert room.name == "r"
    assert len(attempts) == 2
    assert hits == []


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


@pytest.mark.parametrize(
    "host, expected",
    [
        ("myproject.livekit.cloud", FAILOVER_MAX_ATTEMPTS),
        ("myproject.region.livekit.cloud", FAILOVER_MAX_ATTEMPTS),
        ("myproject.livekit.io", 1),
        # The LiveKit Cloud API hosts fail over too (same-host retry).
        ("cloud-api.livekit.io", FAILOVER_MAX_ATTEMPTS),
        ("cloud-api.staging.livekit.io", FAILOVER_MAX_ATTEMPTS),
        ("CLOUD-API.LIVEKIT.IO", FAILOVER_MAX_ATTEMPTS),
        ("cloud-api.example.com", 1),
        ("example.com", 1),
        ("127.0.0.1", 1),
        ("notlivekit.cloud", 1),
    ],
)
def test_failover_attempts(host: str, expected: int):
    assert failover_attempts(True, host) == expected
