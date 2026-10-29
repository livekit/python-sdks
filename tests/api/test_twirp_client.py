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
from typing import List

import pytest

from livekit.api.twirp_client import TwirpClient
from livekit.protocol.room import ListRoomsRequest, ListRoomsResponse


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
    timeout = None

    def __init__(self) -> None:
        self.urls: List[str] = []

    def post(self, url: str, **kwargs) -> _Post:
        self.urls.append(url)
        return _Post()


def _requested_url(host: str) -> str:
    session = _RecordingSession()
    client = TwirpClient(session, host, "livekit")  # type: ignore[arg-type]
    asyncio.run(
        client.request("RoomService", "ListRooms", ListRoomsRequest(), {}, ListRoomsResponse)
    )
    return session.urls[0]


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("wss://example.livekit.cloud", "https://example.livekit.cloud"),
        ("http://localhost:7880/", "http://localhost:7880"),
        ("https://proxy.example.com/livekit", "https://proxy.example.com/livekit"),
        ("wss://proxy.example.com/livekit/", "https://proxy.example.com/livekit"),
    ],
)
def test_request_url_keeps_the_base_path(host: str, expected: str) -> None:
    assert _requested_url(host) == f"{expected}/twirp/livekit.RoomService/ListRooms"
