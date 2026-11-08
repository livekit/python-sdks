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

"""The thread and database services against an in-process Public API server:
the requests they send (path, query, body, bearer token) and the protocol
messages they map the responses onto."""

import asyncio
import json
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

import aiohttp
import jwt
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from google.protobuf.duration_pb2 import Duration

from livekit.api import LiveKitAPI, ServerError, TokenVerifier
from livekit.api.public_api_client import public_api_url
from livekit.protocol.agent_pb.agent_session import ChatRole
from livekit.protocol.agent_pb.agent_thread import AgentTask, AgentThread
from livekit.protocol.agentdb import AgentDB

KEY, SECRET = "key", "a-secret-long-enough-for-hmac-sha256"

Reply = Tuple[int, Any]


class Recorded:
    def __init__(self, request: web.Request, body: bytes) -> None:
        self.method = request.method
        self.path = request.path
        self.query = dict(request.query)
        self.headers = request.headers
        self.json = json.loads(body) if body else None

    @property
    def bearer(self) -> str:
        auth = self.headers["Authorization"]
        assert auth.startswith("Bearer ")
        return auth[len("Bearer ") :]


def run(
    call: Callable[[LiveKitAPI], Awaitable[Any]],
    reply: Reply = (200, {}),
    *,
    token: Optional[str] = None,
) -> Tuple[Any, Recorded]:
    """Runs `call` against a server answering every request with `reply`, and
    returns its result with the one request the server received."""
    requests: List[Recorded] = []

    async def handle(request: web.Request) -> web.Response:
        requests.append(Recorded(request, await request.read()))
        status, body = reply
        if isinstance(body, str):
            return web.Response(status=status, text=body)
        return web.json_response(body, status=status)

    async def main() -> Any:
        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", handle)
        async with TestServer(app) as server:
            url = f"http://127.0.0.1:{server.port}"
            if token:
                lkapi = LiveKitAPI.with_token(token, url)
            else:
                lkapi = LiveKitAPI(url, KEY, SECRET)
            async with lkapi:
                return await call(lkapi)

    result = asyncio.run(main())
    assert len(requests) == 1
    return result, requests[0]


def test_public_api_url_from_project_url():
    staging = "https://beta-api.staging.livekit.cloud"
    assert public_api_url("wss://my-app-abc.staging.livekit.cloud") == staging
    assert public_api_url("https://my-app-abc.staging.livekit.cloud/") == staging
    assert public_api_url("wss://my-app-abc.livekit.cloud") == "https://beta-api.livekit.cloud"
    assert public_api_url("ws://localhost:7880") == "http://localhost:7880"
    assert public_api_url("http://127.0.0.1:8080/") == "http://127.0.0.1:8080"
    assert public_api_url("https://livekit.example.com") == "https://livekit.example.com"


def test_get_thread_signs_a_short_lived_token_with_thread_and_database_grants():
    thread_json = {
        "threadId": "AT_1",
        "scope": "user-1",
        "attributes": {"plan": "pro"},
        "createdAt": "2026-01-02T03:04:05.123456789Z",
        "idleTtl": "86400s",
        "databaseId": "DB_1",
    }
    thread, req = run(lambda lk: lk.threads.get_thread("AT_1"), (200, {"thread": thread_json}))

    assert req.method == "GET"
    assert req.path == "/v0/projects/p_/threads/AT_1"
    assert req.headers["User-Agent"].startswith("livekit-server-sdk-python/")
    claims = TokenVerifier(KEY, SECRET).verify(req.bearer)
    assert claims.agent is not None and claims.agent.database_admin
    thread_grants = claims.agent_thread
    assert thread_grants is not None
    assert thread_grants.all and thread_grants.list and thread_grants.create
    assert thread_grants.write and thread_grants.read and thread_grants.delete

    assert thread.thread_id == "AT_1"
    assert thread.scope == "user-1"
    assert dict(thread.attributes) == {"plan": "pro"}
    assert thread.created_at.nanos == 123456789
    assert thread.idle_ttl.seconds == 86400
    assert thread.database_id == "DB_1"


def test_token_ttl_is_60_seconds():
    _, req = run(lambda lk: lk.threads.get_thread("AT_1"))
    raw = jwt.decode(req.bearer, options={"verify_signature": False})
    assert raw["iss"] == KEY
    assert raw["exp"] - raw["nbf"] == 60


def test_pre_signed_token_is_sent_verbatim():
    _, req = run(lambda lk: lk.databases.get_database("DB_1"), token="pre-signed")
    assert req.bearer == "pre-signed"


def test_create_thread_body():
    req = AgentThread.CreateRequest(
        scope="user-1", attributes={"plan": "pro"}, idle_ttl=Duration(seconds=60)
    )
    thread, rec = run(
        lambda lk: lk.threads.create_thread(req), (200, {"thread": {"threadId": "AT_2"}})
    )
    assert (rec.method, rec.path) == ("POST", "/v0/projects/p_/threads")
    assert rec.json == {"scope": "user-1", "attributes": {"plan": "pro"}, "idleTtl": "60s"}
    assert thread.thread_id == "AT_2"


def test_create_thread_leaves_unset_fields_out():
    _, rec = run(lambda lk: lk.threads.create_thread(AgentThread.CreateRequest()))
    assert rec.json == {}


def test_update_thread_keeps_the_id_in_the_path():
    req = AgentThread.UpdateRequest(thread_id="AT_1", attributes={"plan": "", "seat": "3"})
    _, rec = run(lambda lk: lk.threads.update_thread(req), (200, {"thread": {"threadId": "AT_1"}}))
    assert (rec.method, rec.path) == ("PATCH", "/v0/projects/p_/threads/AT_1")
    # An empty value deletes the attribute, so it must reach the server.
    assert rec.json == {"attributes": {"plan": "", "seat": "3"}}


def test_delete_thread():
    result, rec = run(lambda lk: lk.threads.delete_thread("AT_1"))
    assert (rec.method, rec.path) == ("DELETE", "/v0/projects/p_/threads/AT_1")
    assert result is None


def test_list_threads_pages():
    reply = {
        "items": [{"threadId": "AT_1"}, {"threadId": "AT_2"}],
        "pageInfo": {"nextCursor": "c2", "hasMore": True},
    }
    req = AgentThread.ListRequest(scope="user-1", page_token="c1", limit=2)
    res, rec = run(lambda lk: lk.threads.list_threads(req), (200, reply))
    assert rec.query == {"scope": "user-1", "page.cursor": "c1", "page.pageSize": "2"}
    assert [t.thread_id for t in res.threads] == ["AT_1", "AT_2"]
    assert res.next_page_token == "c2"


def test_list_threads_sends_no_unset_filter():
    res, rec = run(
        lambda lk: lk.threads.list_threads(AgentThread.ListRequest()), (200, {"items": []})
    )
    assert rec.query == {}
    assert len(res.threads) == 0 and res.next_page_token == ""


def test_thread_items():
    reply = {
        "items": [
            {
                "agent": "frontdesk",
                "seq": "7",
                "messageId": "m1",
                "item": {
                    "message": {"id": "i1", "role": "ASSISTANT", "content": [{"text": "hello"}]}
                },
                "addedLater": True,
            }
        ],
        "pageInfo": {"nextCursor": "", "hasMore": False},
    }
    req = AgentThread.GetItemsRequest(
        thread_id="AT_1", agent="frontdesk", limit=10, sort_order=AgentThread.SORT_ORDER_DESC
    )
    res, rec = run(lambda lk: lk.threads.get_thread_items(req), (200, reply))
    assert rec.path == "/v0/projects/p_/threads/AT_1/items"
    assert rec.query == {
        "agent": "frontdesk",
        "page.pageSize": "10",
        "sortOrder": "SORT_ORDER_DESC",
    }
    (item,) = res.items
    assert (item.agent, item.seq, item.message_id) == ("frontdesk", 7, "m1")
    assert item.item.message.role == ChatRole.ASSISTANT
    assert item.item.message.content[0].text == "hello"
    assert res.next_page_token == ""


def test_thread_tasks_status_filter():
    reply = {"items": [{"taskId": "t1", "threadId": "AT_1", "name": "book", "status": "RUNNING"}]}
    req = AgentTask.GetTasksRequest(thread_id="AT_1", status=AgentTask.RUNNING)
    res, rec = run(lambda lk: lk.threads.get_thread_tasks(req), (200, reply))
    assert rec.path == "/v0/projects/p_/threads/AT_1/tasks"
    assert rec.query == {"status": "RUNNING"}
    assert res.tasks[0].status == AgentTask.RUNNING

    _, rec = run(
        lambda lk: lk.threads.get_thread_tasks(AgentTask.GetTasksRequest(thread_id="AT_1"))
    )
    assert rec.query == {}


def test_database_operations():
    created, rec = run(
        lambda lk: lk.databases.create_database(AgentDB.CreateRequest(ttl=Duration(seconds=3600))),
        (200, {"databaseId": "DB_1", "expiresAt": "2026-01-02T03:04:05Z"}),
    )
    assert (rec.method, rec.path, rec.json) == (
        "POST",
        "/v0/projects/p_/databases",
        {"ttl": "3600s"},
    )
    assert created.database_id == "DB_1" and created.expires_at.seconds > 0

    db, rec = run(
        lambda lk: lk.databases.get_database("DB_1"),
        (200, {"database": {"databaseId": "DB_1", "region": "us", "tip": "12"}}),
    )
    assert (rec.method, rec.path) == ("GET", "/v0/projects/p_/databases/DB_1")
    assert (db.database_id, db.region, db.tip) == ("DB_1", "us", 12)

    listed, rec = run(
        lambda lk: lk.databases.list_databases(AgentDB.ListRequest(page_size=5, page_token="c1")),
        (200, {"items": [{"databaseId": "DB_1"}], "pageInfo": {"nextCursor": "c2"}}),
    )
    assert rec.query == {"page.cursor": "c1", "page.pageSize": "5"}
    assert [d.database_id for d in listed.databases] == ["DB_1"]
    assert listed.next_page_token == "c2"

    _, rec = run(lambda lk: lk.databases.delete_database("DB_1"))
    assert (rec.method, rec.path) == ("DELETE", "/v0/projects/p_/databases/DB_1")

    exported, rec = run(
        lambda lk: lk.databases.export_database("DB_1"),
        (200, {"downloadUrl": "https://s3/db", "expiresAt": "2026-01-02T03:04:05Z", "tip": "42"}),
    )
    assert (rec.method, rec.path) == ("POST", "/v0/projects/p_/databases/DB_1:export")
    assert (exported.download_url, exported.tip) == ("https://s3/db", 42)


@pytest.mark.parametrize(
    "reply, code, message",
    [
        ((404, {"code": 5, "message": "thread not found"}), "not_found", "thread not found"),
        ((409, {"code": "aborted", "message": "busy"}), "aborted", "busy"),
        ((503, "upstream down"), "unavailable", "upstream down"),
        ((502, {}), "internal", "{}"),
        ((418, {}), "unknown", "{}"),
    ],
)
def test_errors_map_to_server_error(reply: Reply, code: str, message: str):
    async def call(lk: LiveKitAPI) -> ServerError:
        with pytest.raises(ServerError) as err:
            await lk.threads.get_thread("AT_1")
        return err.value

    err, _ = run(call, reply)
    assert (err.code, err.message, err.status) == (code, message, reply[0])


def test_services_share_the_session_and_timeout():
    async def main() -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            default = LiveKitAPI("wss://x.livekit.cloud", KEY, SECRET, session=session)
            custom = LiveKitAPI(
                "wss://x.livekit.cloud", KEY, SECRET, timeout=aiohttp.ClientTimeout(total=3)
            )
            try:
                return {
                    "pool": default.threads._client.threads.api_client.rest_client.pool_manager,
                    "session": session,
                    "host": default.databases._client.host,
                    "default": default.threads._client.timeout,
                    "custom": custom.databases._client.timeout,
                }
            finally:
                await custom.aclose()

    r = asyncio.run(main())
    assert r["pool"] is r["session"]
    assert r["host"] == "https://beta-api.livekit.cloud"
    assert (r["default"], r["custom"]) == (10.0, 3)
