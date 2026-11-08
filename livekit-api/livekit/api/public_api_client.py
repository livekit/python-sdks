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

from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar
from urllib.parse import urlparse

import aiohttp
from google.protobuf import json_format
from google.protobuf.message import Message

from ._generated.public_api import ApiClient, Configuration, DatabaseServiceApi, ThreadServiceApi
from .errors import ServerError, ServerErrorCode
from .version import USER_AGENT

# The project id that names the project of the request's token.
PROJECT = "p_"

DEFAULT_TIMEOUT = 10.0
STAGING_URL = "https://beta-api.staging.livekit.cloud"
PRODUCTION_URL = "https://beta-api.livekit.cloud"

_STATUS_CODES = {
    400: ServerErrorCode.INVALID_ARGUMENT,
    401: ServerErrorCode.UNAUTHENTICATED,
    403: ServerErrorCode.PERMISSION_DENIED,
    404: ServerErrorCode.NOT_FOUND,
    409: ServerErrorCode.ALREADY_EXISTS,
    429: ServerErrorCode.RESOURCE_EXHAUSTED,
    499: ServerErrorCode.CANCELED,
    501: ServerErrorCode.UNIMPLEMENTED,
    502: ServerErrorCode.UNAVAILABLE,
    503: ServerErrorCode.UNAVAILABLE,
    504: ServerErrorCode.DEADLINE_EXCEEDED,
}

M = TypeVar("M", bound=Message)


def public_api_url(project_url: str) -> str:
    """The Public API base URL of a project URL (`LIVEKIT_URL`).

    LiveKit Cloud projects use the Cloud Public API; any other host (self-hosted)
    serves it itself.
    """
    if project_url.startswith("wss://"):
        http = "https://" + project_url[len("wss://") :]
    elif project_url.startswith("ws://"):
        http = "http://" + project_url[len("ws://") :]
    else:
        http = project_url
    hostname = urlparse(http).hostname or ""
    if hostname.endswith(".staging.livekit.cloud"):
        return STAGING_URL
    if hostname.endswith(".livekit.cloud"):
        return PRODUCTION_URL
    return http.rstrip("/")


class PublicApiClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        *,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ) -> None:
        self.host = public_api_url(host)
        self.timeout = timeout.total if timeout and timeout.total else DEFAULT_TIMEOUT
        api = ApiClient(Configuration(host=self.host))
        api.user_agent = USER_AGENT
        # Requests go through the caller's session, which this client never closes.
        api.rest_client.pool_manager = session
        self.threads = ThreadServiceApi(api)
        self.databases = DatabaseServiceApi(api)

    async def request(
        self,
        *,
        operation: Callable[..., Awaitable[aiohttp.ClientResponse]],
        headers: Dict[str, str],
        response_class: Type[M],
        field: Optional[str] = None,
        **params: Any,
    ) -> M:
        """Calls a generated operation and parses its JSON (or its `field`) into `response_class`.
        A parameter at its protobuf default (`""`, `0`) is left unset."""
        data, status = await self._call(operation=operation, headers=headers, params=params)
        return _parse(data.get(field) if field else data, response_class, status)

    async def list(
        self,
        *,
        operation: Callable[..., Awaitable[aiohttp.ClientResponse]],
        headers: Dict[str, str],
        response_class: Type[M],
        items: str,
        page_token: str,
        limit: int,
        **params: Any,
    ) -> M:
        """Calls a generated list operation for one page: its `items` and `pageInfo` become the
        protocol response's `items` field and `next_page_token`."""
        data, status = await self._call(
            operation=operation,
            headers=headers,
            # A limit of zero or below leaves the page size to the server.
            params={"page_cursor": page_token, "page_page_size": max(limit, 0), **params},
        )
        next_page = (data.get("pageInfo") or {}).get("nextCursor", "")
        page = {items: data.get("items"), "nextPageToken": next_page}
        return _parse(page, response_class, status)

    async def _call(
        self,
        *,
        operation: Callable[..., Awaitable[aiohttp.ClientResponse]],
        headers: Dict[str, str],
        params: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], int]:
        """The JSON object of a successful response and its status. Required parameters (the
        operation's own, without a default) must be set; optional ones at their protobuf
        default are left unset."""
        required = {
            name
            for name, p in inspect.signature(operation).parameters.items()
            if p.default is p.empty and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
        }
        for name in required & params.keys():
            if params[name] in (None, ""):
                raise ValueError(f"{name} must not be empty")
        set_params = {k: v for k, v in params.items() if k in required or v not in (None, "", 0)}
        resp = await operation(
            project_id=PROJECT, _headers=headers, _request_timeout=self.timeout, **set_params
        )
        try:
            body = await resp.read()
        finally:
            resp.release()
        if not 200 <= resp.status < 300:
            raise _server_error(body, resp.status)
        try:
            data = json.loads(body) if body else {}
        except ValueError:
            data = None
        if not isinstance(data, dict):
            raise _malformed("response is not a JSON object", body, resp.status)
        return data, resp.status


def _parse(data: Any, response_class: Type[M], status: int) -> M:
    # Fields this SDK doesn't know yet are ignored.
    try:
        return json_format.ParseDict(data or {}, response_class(), ignore_unknown_fields=True)
    except json_format.ParseError as e:
        raise ServerError(ServerErrorCode.MALFORMED, f"malformed response: {e}", status=status)


def _malformed(reason: str, body: bytes, status: int) -> ServerError:
    snippet = body[:200].decode("utf-8", errors="replace")
    return ServerError(ServerErrorCode.MALFORMED, f"{reason}: {snippet}", status=status)


def _server_error(body: bytes, status: int) -> ServerError:
    # Errors carry a google.rpc.Status, whose numeric code says no more than the
    # HTTP status; a string code is the server's own name for it.
    text = body.decode("utf-8", errors="replace")
    code: Optional[str] = None
    msg = ""
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    if isinstance(data, dict):
        code = data["code"] if isinstance(data.get("code"), str) else None
        msg = str(data.get("message") or "")
    if code is None:
        code = _STATUS_CODES.get(status) or (
            ServerErrorCode.INTERNAL if status >= 500 else ServerErrorCode.UNKNOWN
        )
    return ServerError(code, msg or text or f"HTTP {status}", status=status)


def to_json(msg: Message) -> Dict[str, Any]:
    """The protobuf JSON of a request message, leaving unset fields out."""
    return json_format.MessageToDict(msg)
