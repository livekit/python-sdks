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
import time
from typing import List, Optional

import aiohttp
import pytest
from aiohttp import web

from livekit.api import LiveKitAPI
from livekit.api.twirp_client import TwirpClient
from livekit.protocol.room import ListRoomsRequest, ListRoomsResponse

API_KEY = "devkey"
API_SECRET = "secret-that-is-long-enough-000000"

_MISSING = object()


class _Response:
    status = 200

    async def read(self) -> bytes:
        return ListRoomsResponse().SerializeToString()


class _Post:
    async def __aenter__(self) -> _Response:
        return _Response()

    async def __aexit__(self, *exc) -> None:
        return None


class _RecordingSession:
    """Captures the timeout actually handed to aiohttp for each request."""

    def __init__(self, timeout: aiohttp.ClientTimeout) -> None:
        self.timeout = timeout
        self.timeouts: List[object] = []

    def post(self, url: str, **kwargs) -> _Post:
        self.timeouts.append(kwargs.get("timeout", _MISSING))
        return _Post()


def _record_timeout(
    session_timeout: aiohttp.ClientTimeout,
    client_timeout: Optional[aiohttp.ClientTimeout] = None,
    call_timeout: Optional[aiohttp.ClientTimeout] = None,
) -> object:
    """Returns the timeout the client hands to aiohttp for one request."""
    session = _RecordingSession(session_timeout)
    client = TwirpClient(
        session,  # type: ignore[arg-type]
        "http://localhost:7880",
        "livekit",
        timeout=client_timeout,
    )
    kwargs = {} if call_timeout is None else {"timeout": call_timeout}
    asyncio.run(
        client.request(
            "RoomService", "ListRooms", ListRoomsRequest(), {}, ListRoomsResponse, **kwargs
        )
    )
    assert len(session.timeouts) == 1
    return session.timeouts[0]


def test_session_timeout_is_forwarded_when_no_override() -> None:
    """Regression: the session timeout must reach aiohttp.

    Passing ``timeout=None`` explicitly means "no timeout at all" to aiohttp,
    not "use the session default" — only a missing argument selects the
    session timeout. Forwarding None left every call unbounded, so a host that
    accepted the connection and never answered was waited on forever.
    """
    assert _record_timeout(aiohttp.ClientTimeout(total=10)) == aiohttp.ClientTimeout(total=10)


def test_client_default_timeout_applies() -> None:
    timeout = _record_timeout(
        aiohttp.ClientTimeout(total=300),
        client_timeout=aiohttp.ClientTimeout(total=10),
    )
    assert timeout == aiohttp.ClientTimeout(total=10)


def test_per_call_timeout_wins_over_client_and_session() -> None:
    timeout = _record_timeout(
        aiohttp.ClientTimeout(total=300),
        client_timeout=aiohttp.ClientTimeout(total=10),
        call_timeout=aiohttp.ClientTimeout(total=30),
    )
    assert timeout == aiohttp.ClientTimeout(total=30)


def test_timeout_applies_to_a_caller_supplied_session() -> None:
    """``timeout`` used to be ignored unless the SDK created the session."""

    async def check() -> None:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
            lk = LiveKitAPI(
                "http://localhost:7880",
                API_KEY,
                API_SECRET,
                session=session,
                timeout=aiohttp.ClientTimeout(total=10),
            )
            assert lk._room._client._timeout == aiohttp.ClientTimeout(total=10)
            # The shared session is left alone; only API calls get the deadline.
            assert session.timeout == aiohttp.ClientTimeout(total=300)

    asyncio.run(check())


def test_caller_supplied_session_without_timeout_is_unchanged() -> None:
    """Back-compat: no ``timeout`` means the session's own timeout still governs."""

    async def check() -> None:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
            lk = LiveKitAPI("http://localhost:7880", API_KEY, API_SECRET, session=session)
            assert lk._room._client._timeout is None

    asyncio.run(check())


def test_sdk_created_session_keeps_its_ten_second_default() -> None:
    async def check() -> None:
        lk = LiveKitAPI("http://localhost:7880", API_KEY, API_SECRET)
        try:
            assert lk._session.timeout == aiohttp.ClientTimeout(total=10)
            assert lk._room._client._timeout == aiohttp.ClientTimeout(total=10)
        finally:
            await lk.aclose()

    asyncio.run(check())


@pytest.mark.parametrize("use_custom_session", [False, True])
def test_request_fails_instead_of_hanging(use_custom_session: bool) -> None:
    """End to end against a host that accepts the connection and never answers."""

    async def check() -> None:
        async def hang(request: web.Request) -> web.Response:
            await asyncio.sleep(3600)
            return web.Response()

        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", hang)
        # The handler never returns, so don't let teardown wait out its
        # default 60s grace period.
        runner = web.AppRunner(app, shutdown_timeout=0.1)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = runner.addresses[0][1]

        timeout = aiohttp.ClientTimeout(total=1)
        session = aiohttp.ClientSession(timeout=timeout) if use_custom_session else None
        lk = LiveKitAPI(
            f"http://127.0.0.1:{port}", API_KEY, API_SECRET, session=session, timeout=timeout
        )

        start = time.monotonic()
        try:
            with pytest.raises(asyncio.TimeoutError):
                # Generous ceiling: the point is that it terminates at all, and
                # without the fix it would run until the wait_for cancelled it.
                await asyncio.wait_for(lk.room.list_rooms(ListRoomsRequest()), 20)
            assert time.monotonic() - start < 15
        finally:
            await lk.aclose()
            if session is not None:
                await session.close()
            await runner.shutdown()
            await runner.cleanup()

    asyncio.run(check())
