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

"""Region failover for the Twirp API clients.

On a retryable failure (any transport error or HTTP 5xx) the client discovers
alternative LiveKit Cloud regions via ``/settings/regions`` and replays the
request against the next region, with exponential backoff. 4xx responses are
returned immediately.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict
from urllib.parse import urlparse

import aiohttp

_DEFAULT_MAX_ATTEMPTS = 3
_DEFAULT_BACKOFF_BASE = 0.2


class FailoverOptions(TypedDict, total=False):
    """Region-failover tuning, passed as the ``failover`` argument. Use it as a
    plain dict, e.g. ``failover={"max_attempts": 5}``. All keys are optional.

    Keys:
        max_attempts: total number of attempts including the initial request —
            the original host plus up to ``max_attempts - 1`` fallback regions.
            Defaults to 3. Set to 1 to disable failover (a single attempt).
        backoff_base: seconds before the first retry; each subsequent retry
            doubles it. Defaults to 0.2.
    """

    max_attempts: int
    backoff_base: float


def failover_attempts(failover: Optional[FailoverOptions], host: Optional[str]) -> int:
    """Total request attempts including the initial one; 1 means no failover.

    With no config (``None``) failover is enabled only for LiveKit Cloud hosts.
    An explicit config enables it for any host; ``max_attempts=1`` disables it.
    """
    if failover is None:
        return _DEFAULT_MAX_ATTEMPTS if (bool(host) and is_cloud(host)) else 1  # type: ignore[arg-type]
    return max(1, failover.get("max_attempts", _DEFAULT_MAX_ATTEMPTS))


def failover_backoff_base(failover: Optional[FailoverOptions]) -> float:
    return (failover or {}).get("backoff_base", _DEFAULT_BACKOFF_BASE)


def is_cloud(host: str) -> bool:
    # Auto mode only enables failover for LiveKit Cloud project domains.
    return host.endswith(".livekit.cloud")


def to_http(url: str) -> str:
    """Normalizes a region URL to an http(s) scheme (ws -> http, wss -> https)."""
    if url.startswith("ws"):
        return "http" + url[2:]
    return url


def origin_of(url: str) -> str:
    """Returns the scheme://host[:port] origin of a URL, dropping any path."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def host_key(url: str) -> str:
    """A stable key identifying a host (including port) for dedup across attempts."""
    return urlparse(url).netloc.lower()


def pick_next(region_origins: List[str], attempted: set[str]) -> Optional[str]:
    """Returns the first region origin whose host has not yet been attempted."""
    for origin in region_origins:
        if host_key(origin) not in attempted:
            return origin
    return None


@dataclass
class _CacheEntry:
    origins: List[str]
    fetched_at: float
    ttl: float


class RegionCache:
    """Process-wide cache of the LiveKit Cloud region list, keyed by host."""

    def __init__(self) -> None:
        self._entries: Dict[str, _CacheEntry] = {}

    async def region_origins(
        self,
        session: aiohttp.ClientSession,
        origin: str,
        headers: Dict[str, str],
    ) -> List[str]:
        """Returns alternative region origins for ``origin``, fetching
        ``/settings/regions`` if the cache is stale. Best-effort: on a fetch
        failure it serves a stale cached list when available, otherwise an empty
        list. Forwards ``headers`` so a valid token — and any test directives —
        reach the discovery endpoint."""
        key = host_key(origin)
        entry = self._entries.get(key)
        if entry is not None and (time.monotonic() - entry.fetched_at) < entry.ttl:
            return entry.origins

        try:
            origins, ttl = await self._fetch(session, origin, headers)
        except Exception:
            return entry.origins if entry is not None else []

        # A zero TTL (e.g. Cache-Control: max-age=0) means "do not cache".
        if ttl > 0:
            self._entries[key] = _CacheEntry(origins, time.monotonic(), ttl)
        return origins

    async def _fetch(
        self,
        session: aiohttp.ClientSession,
        origin: str,
        headers: Dict[str, str],
    ) -> tuple[List[str], float]:
        fetch_headers = {
            k: v for k, v in headers.items() if k.lower() not in ("content-type", "content-length")
        }
        # Short timeout so a slow/unreachable discovery endpoint doesn't stall
        # the failover path.
        async with session.get(
            f"{origin}/settings/regions",
            headers=fetch_headers,
            timeout=aiohttp.ClientTimeout(total=2),
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"region discovery failed: {resp.status}")
            ttl = _parse_max_age(resp.headers.get("Cache-Control"))
            body = await resp.json()
        origins = [origin_of(to_http(r["url"])) for r in body.get("regions", []) if r.get("url")]
        return origins, ttl


def _parse_max_age(cache_control: Optional[str]) -> float:
    if not cache_control:
        return 0.0
    for directive in cache_control.split(","):
        directive = directive.strip().lower()
        if directive.startswith("max-age="):
            try:
                return float(int(directive[len("max-age=") :]))
            except ValueError:
                return 0.0
    return 0.0
