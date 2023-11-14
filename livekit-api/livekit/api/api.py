import aiohttp
import os
import asyncio


class LiveKitAPI:
    def __init__(
        self,
        url: str = os.getenv("LIVEKIT_URL", "http://localhost:7880"),
        api_key: str = os.getenv("LIVEKIT_API_KEY", ""),
        api_secret: str = os.getenv("LIVEKIT_API_SECRET", ""),
        *,
        loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
        timeout: float = 60,  # 1 minutes by default
    ):
        self._session = aiohttp.ClientSession(timeout=timeout, loop=loop)
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
