from __future__ import annotations

import datetime
from typing import Callable, Dict, Optional

import aiohttp
from abc import ABC
from .twirp_client import TwirpClient
from .public_api_client import PublicApiClient
from .access_token import AccessToken, AgentGrants, AgentThreadGrants, VideoGrants, SIPGrants

AUTHORIZATION = "authorization"


class BaseService(ABC):
    """What every service shares: requests are signed with the project's key pair, or carry the
    pre-signed token `LiveKitAPI.with_token` set, verbatim (its grants are the caller's)."""

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self._token: str | None = None

    def _bearer(self, grant: Callable[[AccessToken], AccessToken]) -> Dict[str, str]:
        token = self._token or grant(AccessToken(self.api_key, self.api_secret)).to_jwt()
        return {AUTHORIZATION: f"Bearer {token}"}


class TwirpService(BaseService):
    """A service served over Twirp by the LiveKit server."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        api_key: str,
        api_secret: str,
        failover: bool = True,
    ):
        super().__init__(api_key, api_secret)
        self._client = TwirpClient(session, host, "livekit", failover=failover)

    def _auth_header(
        self, grants: VideoGrants | None, sip: SIPGrants | None = None
    ) -> Dict[str, str]:
        def grant(token: AccessToken) -> AccessToken:
            if grants:
                token.with_grants(grants)
            if sip is not None:
                token.with_sip_grants(sip)
            return token

        return self._bearer(grant)


class PublicApiService(BaseService):
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
        super().__init__(api_key, api_secret)
        self._client = PublicApiClient(session, host, timeout=timeout)

    def _auth_header(self) -> Dict[str, str]:
        return self._bearer(
            lambda token: (
                token.with_ttl(self.TOKEN_TTL)
                .with_agent_grants(AgentGrants(database_admin=True))
                .with_agent_thread_grants(
                    AgentThreadGrants(
                        all=True, list=True, create=True, write=True, read=True, delete=True
                    )
                )
            )
        )
