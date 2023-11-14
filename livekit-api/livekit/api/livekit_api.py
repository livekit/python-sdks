import aiohttp
import os
from .room_service import RoomService
from .egress_service import EgressService
from .ingress_service import IngressService


class LiveKitAPI:
    def __init__(
        self,
        url: str = os.getenv("LIVEKIT_URL", "http://localhost:7880"),
        api_key: str = os.getenv("LIVEKIT_API_KEY", ""),
        api_secret: str = os.getenv("LIVEKIT_API_SECRET", ""),
        *,
        timeout: float = 60,  # 1 minutes by default
    ):
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
