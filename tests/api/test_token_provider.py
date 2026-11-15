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

"""How LiveKitAPI authenticates each call: with a token provider, an API key and
secret, or a static token. A recording session stands in for the server."""

from typing import Dict, List

import jwt
import pytest

from livekit import api
from livekit.api.access_token import Claims
from livekit.protocol.room import ListParticipantsRequest, ListParticipantsResponse

URL = "http://localhost:7880"
KEY, SECRET = "devkey", "thiskeyistotallyunsafe-but-32-bytes-long"


class _Response:
    status = 200

    async def read(self) -> bytes:
        return ListParticipantsResponse().SerializeToString()


class _Post:
    async def __aenter__(self) -> _Response:
        return _Response()

    async def __aexit__(self, *exc) -> None:
        return None


class _RecordingSession:
    timeout = None

    def __init__(self) -> None:
        self.headers: List[Dict[str, str]] = []

    def post(self, url: str, *, headers: Dict[str, str], **kwargs) -> _Post:
        self.headers.append(headers)
        return _Post()


def _bearer(session: _RecordingSession) -> str:
    return session.headers[-1]["authorization"].removeprefix("Bearer ")


async def _list_participants(lk: api.LiveKitAPI) -> None:
    await lk.room.list_participants(ListParticipantsRequest(room="test-room"))


async def test_token_provider_gets_the_grants_of_each_call() -> None:
    requested: List[api.TokenGrants] = []

    async def token_provider(grants: api.TokenGrants) -> str:
        requested.append(grants)
        return f"provider-token-{len(requested)}"

    session = _RecordingSession()
    lk = api.LiveKitAPI(URL, token_provider=token_provider, session=session)  # type: ignore[arg-type]

    await _list_participants(lk)
    assert requested == [Claims(video=api.VideoGrants(room_admin=True, room="test-room"))]
    assert _bearer(session) == "provider-token-1"

    await lk.sip.list_inbound_trunk(api.ListSIPInboundTrunkRequest())
    assert requested[-1] == Claims(video=api.VideoGrants(), sip=api.SIPGrants(admin=True))
    assert _bearer(session) == "provider-token-2"


async def test_token_provider_takes_precedence_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIVEKIT_TOKEN", "env-token")
    monkeypatch.setenv("LIVEKIT_API_KEY", KEY)
    monkeypatch.setenv("LIVEKIT_API_SECRET", SECRET)

    async def token_provider(grants: api.TokenGrants) -> str:
        return "provider-token"

    session = _RecordingSession()
    lk = api.LiveKitAPI(URL, token_provider=token_provider, session=session)  # type: ignore[arg-type]
    await _list_participants(lk)
    assert _bearer(session) == "provider-token"


def test_token_and_token_provider_are_exclusive() -> None:
    async def token_provider(grants: api.TokenGrants) -> str:
        return "provider-token"

    with pytest.raises(ValueError, match="cannot both be set"):
        api.LiveKitAPI(URL, token="static", token_provider=token_provider)


async def test_key_and_secret_sign_each_call() -> None:
    session = _RecordingSession()
    lk = api.LiveKitAPI(URL, KEY, SECRET, session=session)  # type: ignore[arg-type]
    await _list_participants(lk)

    claims = api.TokenVerifier(KEY, SECRET).verify(_bearer(session))
    assert claims.video == api.VideoGrants(room_admin=True, room="test-room")
    assert jwt.decode(_bearer(session), options={"verify_signature": False})["iss"] == KEY


async def test_static_token_is_sent_verbatim() -> None:
    session = _RecordingSession()
    lk = api.LiveKitAPI.with_token("static-token", URL, session=session)  # type: ignore[arg-type]
    await _list_participants(lk)
    assert _bearer(session) == "static-token"
