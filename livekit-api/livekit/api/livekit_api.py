import aiohttp
import os
from .room_service import RoomService
from .egress_service import EgressService
from .ingress_service import IngressService
from .sip_service import SipService
from .agent_dispatch_service import AgentDispatchService
from typing import Optional


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
        timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=60),  # 60 seconds
    ):
        """Create a new LiveKitAPI instance.

        Args:
            url: LiveKit server URL (read from `LIVEKIT_URL` environment variable if not provided)
            api_key: API key (read from `LIVEKIT_API_KEY` environment variable if not provided)
            api_secret: API secret (read from `LIVEKIT_API_SECRET` environment variable if not provided)
            timeout: Request timeout (default: 60 seconds)
        """
        url = url or os.getenv("LIVEKIT_URL")
        api_key = api_key or os.getenv("LIVEKIT_API_KEY")
        api_secret = api_secret or os.getenv("LIVEKIT_API_SECRET")

        if not url:
            raise ValueError("url must be set")

        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must be set")

        self._session = aiohttp.ClientSession(timeout=timeout)
        self._room = RoomService(self._session, url, api_key, api_secret)
        self._ingress = IngressService(self._session, url, api_key, api_secret)
        self._egress = EgressService(self._session, url, api_key, api_secret)
        self._sip = SipService(self._session, url, api_key, api_secret)
        self._agent_dispatch = AgentDispatchService(
            self._session, url, api_key, api_secret
        )

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

    async def aclose(self):
        """Close the API client

        Call this before your application exits or when the API client is no longer needed."""
        await self._session.close()

    async def __aenter__(self):
        """@private

        Support for `async with`"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """@private

        Support for `async with`"""
        await self.aclose()
