from __future__ import annotations

import aiohttp
from abc import ABC
from .twirp_client import TwirpClient
from .access_token import AccessToken, VideoGrants, SIPGrants

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
