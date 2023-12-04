import aiohttp
import os
from .room_service import RoomService
from .egress_service import EgressService
from .ingress_service import IngressService
from typing import Optional


class LiveKitAPI:
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        *,
        timeout: float = 60,  # 1 minutes by default
    ):
        if not url:
            url = os.getenv("LIVEKIT_URL", "")

        if not api_key:
            api_key = os.getenv("LIVEKIT_API_KEY", "")

        if not api_secret:
            api_secret = os.getenv("LIVEKIT_API_SECRET", "")

        if not url:
            raise ValueError("url must be set")

        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must be set")

        self._session = aiohttp.ClientSession(timeout=timeout)
        self._room = RoomService(url, api_key, api_secret, self._session)
        self._ingress = IngressService(url, api_key, api_secret, self._session)
        self._egress = EgressService(url, api_key, api_secret, self._session)

    @property
    def room(self):
        return self._room

    @property
    def ingress(self):
        return self._ingress

    @property
    def egress(self):
        return self._egress

    async def aclose(self):
        await self._session.close()
