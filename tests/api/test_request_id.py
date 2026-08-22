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

"""Tests for the per-request idempotency key the client stamps on every API
request. These drive TwirpClient.request() against a fake aiohttp session so no
server is needed, and use the internal test-only failover knobs
(_failover_force/_failover_backoff) to exercise the retry path.
"""

from __future__ import annotations

import pytest

from livekit.api import CreateRoomRequest, Room
from livekit.api.twirp_client import REQUEST_ID_HEADER, TwirpClient

HOST = "https://primary.example.livekit.cloud"


class _FakeResponse:
    def __init__(
        self,
        status: int,
        *,
        body: bytes = b"",
        json_data: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self._body = body
        self._json = json_data if json_data is not None else {}
        self.headers = headers or {}

    async def read(self) -> bytes:
        return self._body

    async def json(self) -> dict:
        return self._json

    async def __aenter__(self) -> _FakeResponse:
        return self

    async def __aexit__(self, *exc) -> None:
        return None


class _FakeSession:
    """Records the headers of every request; replays ``statuses`` in order for
    the Twirp POSTs and serves ``regions`` from /settings/regions."""

    timeout = None

    def __init__(self, statuses: list[int], regions: list[str] | None = None) -> None:
        self.post_headers: list[dict[str, str]] = []
        self._statuses = list(statuses)
        self._regions = regions or []

    def post(self, url, headers=None, data=None, timeout=None) -> _FakeResponse:
        self.post_headers.append(dict(headers or {}))
        status = self._statuses.pop(0) if self._statuses else 200
        return _FakeResponse(status)

    def get(self, url, headers=None, timeout=None) -> _FakeResponse:
        return _FakeResponse(
            200,
            json_data={"regions": [{"url": u} for u in self._regions]},
            # Never cache, so each test discovers its own region list.
            headers={"Cache-Control": "max-age=0"},
        )


async def _call(client: TwirpClient, headers: dict[str, str]) -> Room:
    return await client.request("RoomService", "CreateRoom", CreateRoomRequest(), headers, Room)


def _request_ids(session: _FakeSession) -> list[str | None]:
    return [h.get(REQUEST_ID_HEADER) for h in session.post_headers]


# The header lets the server dedup a request that the SDK replayed.
async def test_stamps_a_request_id():
    session = _FakeSession([200, 200])
    client = TwirpClient(session, HOST, "livekit", failover=False)  # type: ignore[arg-type]

    await _call(client, {})
    await _call(client, {})

    ids = _request_ids(session)
    assert all(ids)
    # A new logical call is a new request, so it gets its own id.
    assert ids[0] != ids[1]


async def test_preserves_caller_request_id():
    session = _FakeSession([200])
    client = TwirpClient(session, HOST, "livekit", failover=False)  # type: ignore[arg-type]

    # Matched case-insensitively, as HTTP header names are.
    await _call(client, {"x-livekit-request-id": "caller-123"})

    assert session.post_headers[0]["x-livekit-request-id"] == "caller-123"
    assert REQUEST_ID_HEADER not in session.post_headers[0]


# The id is generated once per logical call, so every failover attempt must
# carry the same value.
async def test_same_request_id_across_failover_attempts():
    session = _FakeSession(
        [503, 503, 200],
        regions=["wss://r1.example.livekit.cloud", "wss://r2.example.livekit.cloud"],
    )
    # _failover_force bypasses the cloud-host check; a zero backoff keeps it fast.
    client = TwirpClient(
        session,  # type: ignore[arg-type]
        HOST,
        "livekit",
        _failover_force=True,
        _failover_backoff=0,
    )

    await _call(client, {})

    ids = _request_ids(session)
    assert len(ids) == 3
    assert ids[0]
    assert len(set(ids)) == 1


if __name__ == "__main__":
    pytest.main([__file__])
