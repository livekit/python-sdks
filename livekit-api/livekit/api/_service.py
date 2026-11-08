from __future__ import annotations

import datetime
from typing import Dict, Optional

import aiohttp
from abc import ABC
from .twirp_client import TwirpClient
from .public_api_client import PublicApiClient
from .access_token import AccessToken, AgentGrants, AgentThreadGrants, VideoGrants, SIPGrants

AUTHORIZATION = "authorization"


class Service(ABC):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        api_key: str,
        api_secret: str,
        failover: bool = True,
    ):
        self._client = TwirpClient(session, host, "livekit", failover=failover)
        self.api_key = api_key
        self.api_secret = api_secret
        # A pre-signed token set by LiveKitAPI for token auth; sent verbatim,
        # skipping per-call signing. Per-service constructors stay key/secret-only.
        self._token: str | None = None

    def _auth_header(
        self, grants: VideoGrants | None, sip: SIPGrants | None = None
    ) -> dict[str, str]:
        # A pre-signed token is sent verbatim; the caller is responsible for its grants.
        if self._token:
            return {AUTHORIZATION: "Bearer {}".format(self._token)}

        tok = AccessToken(self.api_key, self.api_secret)
        if grants:
            tok.with_grants(grants)
        if sip is not None:
            tok.with_sip_grants(sip)

        token = tok.to_jwt()
        return {AUTHORIZATION: "Bearer {}".format(token)}


class PublicApiService(ABC):
    """A service served by the LiveKit Cloud Public API."""

    # Each request signs its own token, so a short lifetime is enough.
    TOKEN_TTL = datetime.timedelta(seconds=60)

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        api_key: str,
        api_secret: str,
        *,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ):
        self._client = PublicApiClient(session, host, timeout=timeout)
        self.api_key = api_key
        self.api_secret = api_secret
        # Set by LiveKitAPI.with_token: sent verbatim, its grants are the caller's.
        self._token: str | None = None

    def _auth_header(self) -> Dict[str, str]:
        token = self._token or (
            AccessToken(self.api_key, self.api_secret)
            .with_ttl(self.TOKEN_TTL)
            .with_agent_grants(AgentGrants(database_admin=True))
            .with_agent_thread_grants(
                AgentThreadGrants(
                    all=True, list=True, create=True, write=True, read=True, delete=True
                )
            )
            .to_jwt()
        )
        return {AUTHORIZATION: f"Bearer {token}"}
