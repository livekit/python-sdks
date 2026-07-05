import aiohttp
import os
from .room_service import RoomService
from .egress_service import EgressService
from .ingress_service import IngressService
from .sip_service import SipService
from .agent_dispatch_service import AgentDispatchService
from .connector_service import ConnectorService
from typing import Any, Optional


class LiveKitAPI:
    """LiveKit Server API Client

    This class is the main entrypoint, which exposes all services.

    Usage:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    rooms = await lkapi.room.list_rooms(api.proto_room.ListRoomsRequest(names=['test-room']))
    ```
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        *,
        token: Optional[str] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
        session: Optional[aiohttp.ClientSession] = None,
        failover: bool = True,
    ):
        """Create a new LiveKitAPI instance.

        Authenticate with an API key and secret (recommended for backend use).
        For token auth (client-side use, where the API secret must not be
        exposed), prefer the :meth:`with_token` constructor.

        Args:
            url: LiveKit server URL (read from `LIVEKIT_URL` environment variable if not provided)
            api_key: API key (read from `LIVEKIT_API_KEY` environment variable if not provided)
            api_secret: API secret (read from `LIVEKIT_API_SECRET` environment variable if not provided)
            token: Pre-signed access token (read from `LIVEKIT_TOKEN` environment variable if not provided)
            timeout: Request timeout (default: 10 seconds)
            session: aiohttp.ClientSession instance to use for requests, if not provided, a new one will be created
        """
        url = url or os.getenv("LIVEKIT_URL")
        token = token or os.getenv("LIVEKIT_TOKEN")
        api_key = api_key or os.getenv("LIVEKIT_API_KEY")
        api_secret = api_secret or os.getenv("LIVEKIT_API_SECRET")

        if not url:
            raise ValueError("url must be set")

        if not token and (not api_key or not api_secret):
            raise ValueError("either token, or api_key and api_secret, must be set")

        self._custom_session = True
        self._session = session
        if not self._session:
            self._custom_session = False
            if not timeout:
                timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(timeout=timeout)

        # In token mode there is no key/secret; pass empty strings and rely on
        # the token, injected into each service below.
        key = api_key or ""
        secret = api_secret or ""
        self._room = RoomService(self._session, url, key, secret, failover)
        self._ingress = IngressService(self._session, url, key, secret, failover)
        self._egress = EgressService(self._session, url, key, secret, failover)
        self._sip = SipService(self._session, url, key, secret, failover)
        self._agent_dispatch = AgentDispatchService(self._session, url, key, secret, failover)
        self._connector = ConnectorService(self._session, url, key, secret, failover)

        if token:
            for svc in (
                self._room,
                self._ingress,
                self._egress,
                self._sip,
                self._agent_dispatch,
                self._connector,
            ):
                svc._token = token

    @classmethod
    def with_token(
        cls,
        token: str,
        url: Optional[str] = None,
        *,
        timeout: Optional[aiohttp.ClientTimeout] = None,
        session: Optional[aiohttp.ClientSession] = None,
        failover: bool = True,
    ) -> "LiveKitAPI":
        """Create a LiveKitAPI authenticated with a pre-signed token.

        The token is sent verbatim and must already carry the grants for the calls
        it's used with. Since it needs no secret, this is suitable for client-side
        use. `url` falls back to the `LIVEKIT_URL` environment variable.

        Args:
            token: Pre-signed access token
            url: LiveKit server URL (read from `LIVEKIT_URL` if not provided)
            timeout: Request timeout (default: 10 seconds)
            session: aiohttp.ClientSession to use; a new one is created if omitted
        """
        return cls(url, token=token, timeout=timeout, session=session, failover=failover)

    @property
    def agent_dispatch(self) -> AgentDispatchService:
        """Instance of the AgentDispatchService"""
        return self._agent_dispatch

    @property
    def room(self) -> RoomService:
        """Instance of the RoomService"""
        return self._room

    @property
    def ingress(self) -> IngressService:
        """Instance of the IngressService"""
        return self._ingress

    @property
    def egress(self) -> EgressService:
        """Instance of the EgressService"""
        return self._egress

    @property
    def sip(self) -> SipService:
        """Instance of the SipService"""
        return self._sip

    @property
    def connector(self) -> ConnectorService:
        """Instance of the ConnectorService"""
        return self._connector

    async def aclose(self) -> None:
        """Close the API client

        Call this before your application exits or when the API client is no longer needed."""
        # we do not close custom sessions, that's up to the caller
        if not self._custom_session and self._session is not None:
            await self._session.close()

    async def __aenter__(self) -> "LiveKitAPI":
        """@private

        Support for `async with`"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """@private

        Support for `async with`"""
        await self.aclose()
