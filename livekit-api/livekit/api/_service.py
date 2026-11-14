from __future__ import annotations

import aiohttp
from abc import ABC
from typing import Awaitable, Callable
from .twirp_client import TwirpClient
from .access_token import AccessToken, Claims, VideoGrants, SIPGrants

AUTHORIZATION = "authorization"

TokenSource = Callable[[Claims], Awaitable[str]]
"""Returns a token that carries the given claims.

`LiveKitAPI` calls it before each request, in place of signing a token with an API
key and secret, with the claims that request needs. It may cache tokens.
"""


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
        # Set by LiveKitAPI to get a token per call in place of signing one.
        self._token_source: TokenSource | None = None

    async def _auth_header(
        self, grants: VideoGrants | None, sip: SIPGrants | None = None
    ) -> dict[str, str]:
        # A pre-signed token is sent verbatim; the caller is responsible for its grants.
        if self._token:
            return {AUTHORIZATION: "Bearer {}".format(self._token)}

        if self._token_source is not None:
            token = await self._token_source(Claims(video=grants, sip=sip))
            return {AUTHORIZATION: "Bearer {}".format(token)}

        tok = AccessToken(self.api_key, self.api_secret)
        if grants:
            tok.with_grants(grants)
        if sip is not None:
            tok.with_sip_grants(sip)

        token = tok.to_jwt()
        return {AUTHORIZATION: "Bearer {}".format(token)}
