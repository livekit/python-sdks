# Copyright 2023 LiveKit, Inc.
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
from typing import Dict, List, Optional, Type, TypeVar

import aiohttp
from google.protobuf.message import Message
from urllib.parse import urlparse

from ._failover import (
    FailoverConfig,
    RegionCache,
    failover_attempts,
    failover_backoff_base,
    host_key,
    origin_of,
    pick_next,
)

DEFAULT_PREFIX = "twirp"

# Shared across all clients in the process so the region list is fetched once.
_REGION_CACHE = RegionCache()


class TwirpError(Exception):
    def __init__(
        self,
        code: str,
        msg: str,
        *,
        status: int,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        self._code = code
        self._msg = msg
        self._status = status
        self._metadata = metadata or {}

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._msg

    @property
    def status(self) -> int:
        """HTTP status code"""
        return self._status

    @property
    def metadata(self) -> Dict[str, str]:
        """Twirp metadata"""
        return self._metadata

    def __str__(self) -> str:
        result = f"TwirpError(code={self.code}, message={self.message}, status={self.status}"
        if self.metadata:
            result += f", metadata={self.metadata}"
        result += ")"
        return result


class TwirpErrorCode:
    CANCELED = "canceled"
    UNKNOWN = "unknown"
    INVALID_ARGUMENT = "invalid_argument"
    MALFORMED = "malformed"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    NOT_FOUND = "not_found"
    BAD_ROUTE = "bad_route"
    ALREADY_EXISTS = "already_exists"
    PERMISSION_DENIED = "permission_denied"
    UNAUTHENTICATED = "unauthenticated"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    FAILED_PRECONDITION = "failed_precondition"
    ABORTED = "aborted"
    OUT_OF_RANGE = "out_of_range"
    UNIMPLEMENTED = "unimplemented"
    INTERNAL = "internal"
    UNAVAILABLE = "unavailable"
    DATA_LOSS = "dataloss"


T = TypeVar("T", bound=Message)


class TwirpClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        pkg: str,
        prefix: str = DEFAULT_PREFIX,
        failover: Optional[FailoverConfig] = None,
    ) -> None:
        parse_res = urlparse(host)
        scheme = parse_res.scheme
        if scheme.startswith("ws"):
            scheme = scheme.replace("ws", "http")

        host = f"{scheme}://{parse_res.netloc}/{parse_res.path}"
        self.host = host.rstrip("/")
        self.pkg = pkg
        self.prefix = prefix
        self._session = session
        self._failover: Optional[FailoverConfig] = failover
        self._origin = origin_of(self.host)

    async def request(
        self,
        service: str,
        method: str,
        data: Message,
        headers: Dict[str, str],
        response_class: Type[T],
        *,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ) -> T:
        """Issues a Twirp request, failing over to alternative regions on
        retryable errors. On any transport error or HTTP 5xx it discovers
        regions via ``/settings/regions`` and replays the request — body and
        headers intact — against the next untried region, with exponential
        backoff. A 4xx is returned immediately."""
        path = f"{self.prefix}/{self.pkg}.{service}/{method}"
        forward_headers = dict(headers)  # for the discovery fetch (no content-type yet)
        headers = dict(headers)
        headers["Content-Type"] = "application/protobuf"
        serialized_data = data.SerializeToString()

        host = urlparse(self._origin).hostname
        max_attempts = failover_attempts(self._failover, host)
        attempted = {host_key(self._origin)}
        region_origins: Optional[List[str]] = None
        current_origin = self._origin

        for attempt in range(max_attempts):
            is_last = attempt + 1 >= max_attempts
            url = f"{current_origin}/{path}"

            transport_exc: Optional[BaseException] = None
            retryable_status: Optional[int] = None
            error_data: Dict = {}
            try:
                async with self._session.post(
                    url, headers=headers, data=serialized_data, timeout=timeout
                ) as resp:
                    if resp.status == 200:
                        return response_class.FromString(await resp.read())
                    # Twirp encodes errors as JSON regardless of content type.
                    try:
                        error_data = await resp.json()
                    except Exception:
                        error_data = {}
                    if resp.status < 500:
                        # 4xx is terminal.
                        raise self._twirp_error(error_data, resp.status)
                    retryable_status = resp.status
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                transport_exc = e

            # Only retryable failures (5xx or transport error) reach this point.
            next_origin = None
            if not is_last:
                if region_origins is None:
                    region_origins = await _REGION_CACHE.region_origins(
                        self._session, self._origin, forward_headers
                    )
                next_origin = pick_next(region_origins, attempted)

            if next_origin is None:
                if transport_exc is not None:
                    raise transport_exc
                raise self._twirp_error(error_data, retryable_status or 500)

            await asyncio.sleep(failover_backoff_base(self._failover) * (2**attempt))
            attempted.add(host_key(next_origin))
            current_origin = next_origin

        raise RuntimeError("failover loop exited without returning")  # unreachable

    @staticmethod
    def _twirp_error(error_data: Dict, status: int) -> "TwirpError":
        return TwirpError(
            error_data.get("code", "unknown"),
            error_data.get("msg", ""),
            status=status,
            metadata=error_data.get("meta"),
        )
