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

"""The transport of the services served by the LiveKit Cloud Public API.

The HTTP layer is generated from the Public API OpenAPI spec into `_public_api`
(see `livekit-api/public-api/generate.sh`). `PublicApiClient` sends its requests
through the caller's aiohttp session and turns responses into JSON or a
`ServerError`, the way `TwirpClient` does for the Twirp services.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable
from typing import Any, Callable, Dict, Optional, TypeVar
from urllib.parse import urlparse

import aiohttp
from google.protobuf import json_format
from google.protobuf.message import Message

from ._public_api import ApiClient, Configuration, DatabaseServiceApi, ThreadServiceApi
from .twirp_client import _USER_AGENT, ServerError, ServerErrorCode

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
    501: ServerErrorCode.UNIMPLEMENTED,
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
        api.user_agent = _USER_AGENT
        # Requests go through the caller's session, which this client never closes.
        api.rest_client.pool_manager = session
        self.threads = ThreadServiceApi(api)
        self.databases = DatabaseServiceApi(api)

    async def request(
        self,
        operation: Callable[..., Awaitable[aiohttp.ClientResponse]],
        *,
        headers: Dict[str, str],
        **params: Any,
    ) -> Dict[str, Any]:
        """Issues a generated `*_without_preload_content` operation in the project
        of the request's token, returning the JSON of a success. An error status
        raises a `ServerError`.

        `params` are the operation's parameters by name: the generated signatures
        don't promise a positional order."""
        resp = await operation(
            project_id=PROJECT, _headers=headers, _request_timeout=self.timeout, **params
        )
        body = await resp.read()
        if 200 <= resp.status < 300:
            data = json.loads(body) if body else {}
            return data if isinstance(data, dict) else {}
        raise _server_error(body, resp.status)


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
    return ServerError(code, msg or text, status=status)


def to_json(msg: Message) -> Dict[str, Any]:
    """The protobuf JSON of a request message, leaving unset fields out."""
    return json_format.MessageToDict(msg)


def from_json(data: Any, msg: M) -> M:
    """Parses protobuf JSON into `msg`, ignoring fields this SDK doesn't know."""
    json_format.ParseDict(data or {}, msg, ignore_unknown_fields=True)
    return msg


def next_cursor(data: Dict[str, Any]) -> str:
    """The cursor of the page after a list response; empty when exhausted."""
    page = data.get("pageInfo") or {}
    return str(page.get("nextCursor") or "")


def opt(s: str) -> Optional[str]:
    """An empty string is unset."""
    return s or None


def page_size(limit: int) -> Optional[int]:
    """A zero limit is unset."""
    return limit if limit > 0 else None
