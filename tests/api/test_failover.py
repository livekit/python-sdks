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

"""Region failover tests against the shared mock LiveKit API server
(livekit/livekit cmd/test-server). Point them at a running instance with
LK_TEST_SERVER_URL (default http://127.0.0.1:9999); they skip when no server is
reachable. The mock returns Cache-Control: max-age=0, so the region cache never
stores entries and scenarios don't interfere.

See cmd/test-server/README.md for the X-Lk-Mock-* control protocol. These tests
drive TwirpClient.request() directly because the public service methods do not
expose per-call headers.
"""

import asyncio
import os
import urllib.request

import aiohttp
import pytest

from livekit.api import CreateRoomRequest, Room, TwirpError
from livekit.api.twirp_client import TwirpClient

BASE = os.getenv("LK_TEST_SERVER_URL", "http://127.0.0.1:9999")


def _server_up() -> bool:
    try:
        with urllib.request.urlopen(f"{BASE}/settings/regions", timeout=1) as r:
            return r.status == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _server_up(), reason=f"mock test server not reachable at {BASE}"
)


# _failover_force bypasses the cloud-host check (the mock is on 127.0.0.1) and a
# tiny backoff keeps the tests fast — both are internal, test-only knobs.
async def _call(directives: dict, *, failover: bool = True, force: bool = True) -> Room:
    async with aiohttp.ClientSession() as session:
        client = TwirpClient(
            session,
            BASE,
            "livekit",
            failover=failover,
            _failover_force=force,
            _failover_backoff=0.001,
        )
        headers = {
            "authorization": "Bearer test-token",
            "x-lk-mock-skip-auth": "true",
            **directives,
        }
        return await client.request("RoomService", "CreateRoom", CreateRoomRequest(), headers, Room)


def test_healthy():
    asyncio.run(_call({}))


def test_primary_unavailable():
    asyncio.run(_call({"x-lk-mock-fail-regions": "0"}))


def test_two_regions_unavailable():
    asyncio.run(_call({"x-lk-mock-fail-regions": "0,1"}))


def test_all_unavailable():
    with pytest.raises(TwirpError):
        asyncio.run(_call({"x-lk-mock-fail-regions": "0,1,2,3"}))


def test_client_error_not_retried():
    with pytest.raises(TwirpError) as exc:
        asyncio.run(_call({"x-lk-mock-fail-regions": "0", "x-lk-mock-fail-status": "400"}))
    assert exc.value.code == "invalid_argument"


def test_transport_error_failover():
    asyncio.run(_call({"x-lk-mock-fail-regions": "0", "x-lk-mock-fail-mode": "drop"}))


def test_region_discovery_unreachable():
    with pytest.raises(TwirpError):
        asyncio.run(_call({"x-lk-mock-fail-regions": "0", "x-lk-mock-regions-status": "500"}))


def test_not_cloud_host():
    # Enabled but not forced; 127.0.0.1 is not a cloud host, so no failover.
    with pytest.raises(TwirpError):
        asyncio.run(_call({"x-lk-mock-fail-regions": "0"}, force=False))


def test_disabled():
    # failover=False disables failover entirely.
    with pytest.raises(TwirpError):
        asyncio.run(_call({"x-lk-mock-fail-regions": "0"}, failover=False))
