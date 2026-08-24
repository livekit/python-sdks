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

See cmd/test-server/README.md for the X-Lk-Mock JSON control protocol. These
tests drive TwirpClient.request() directly because failover relies on internal
test-only knobs (_failover_force/_failover_backoff) the public methods don't
expose.
"""

import asyncio
import json
import os
import urllib.request
from typing import List, Optional

import aiohttp
import pytest

from livekit.api import CreateRoomRequest, Room, ServerError
from livekit.api.twirp_client import REQUEST_ID_HEADER, TwirpClient

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
async def _call(
    mock: dict,
    *,
    failover: bool = True,
    force: bool = True,
    extra_headers: Optional[dict] = None,
    trace_configs: Optional[List[aiohttp.TraceConfig]] = None,
) -> Room:
    async with aiohttp.ClientSession(trace_configs=trace_configs) as session:
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
            # These tests exercise failover, not authz; skip the mock's permission check.
            "X-Lk-Mock": json.dumps({"skipAuth": True, **mock}),
            **(extra_headers or {}),
        }
        return await client.request("RoomService", "CreateRoom", CreateRoomRequest(), headers, Room)


def test_healthy():
    asyncio.run(_call({}))


def test_primary_unavailable():
    asyncio.run(_call({"failRegions": [0]}))


def test_two_regions_unavailable():
    asyncio.run(_call({"failRegions": [0, 1]}))


def test_all_unavailable():
    with pytest.raises(ServerError):
        asyncio.run(_call({"failRegions": [0, 1, 2, 3]}))


def test_client_error_not_retried():
    with pytest.raises(ServerError) as exc:
        asyncio.run(_call({"failRegions": [0], "failStatus": 400}))
    assert exc.value.code == "invalid_argument"


def test_transport_error_failover():
    asyncio.run(_call({"failRegions": [0], "failMode": "drop"}))


def test_region_discovery_unreachable():
    with pytest.raises(ServerError):
        asyncio.run(_call({"failRegions": [0], "regionsStatus": 500}))


def test_not_cloud_host():
    # Enabled but not forced; 127.0.0.1 is not a cloud host, so no failover.
    with pytest.raises(ServerError):
        asyncio.run(_call({"failRegions": [0]}, force=False))


def test_disabled():
    # failover=False disables failover entirely.
    with pytest.raises(ServerError):
        asyncio.run(_call({"failRegions": [0]}, failover=False))


# Records the request id header(s) the SDK put on the wire for each Twirp
# attempt. Region discovery is a separate request, so it is not recorded.
def _request_id_recorder(seen: List[List[str]]) -> aiohttp.TraceConfig:
    trace = aiohttp.TraceConfig()

    async def on_request_start(_session, _ctx, params) -> None:
        if not params.url.path.endswith("/settings/regions"):
            seen.append(list(params.headers.getall(REQUEST_ID_HEADER, [])))

    trace.on_request_start.append(on_request_start)
    return trace


def test_request_id_stable_across_attempts():
    # The id is generated once per logical call, so a replayed request carries
    # the same idempotency key on every attempt and the server can dedup it.
    seen: List[List[str]] = []
    asyncio.run(_call({"failRegions": [0, 1]}, trace_configs=[_request_id_recorder(seen)]))
    assert len(seen) == 3  # primary + two fallbacks
    assert all(len(ids) == 1 for ids in seen)  # never duplicated
    assert seen[0][0]
    assert len({ids[0] for ids in seen}) == 1


def test_request_id_unique_per_call():
    # A new logical call is a new request, so it gets its own id.
    seen: List[List[str]] = []
    recorder = _request_id_recorder(seen)
    asyncio.run(_call({}, trace_configs=[recorder]))
    asyncio.run(_call({}, trace_configs=[recorder]))
    assert len(seen) == 2
    assert seen[0][0] and seen[1][0]
    assert seen[0][0] != seen[1][0]
