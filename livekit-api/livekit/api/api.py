import aiohttp
import os


class LivekitAPI:
    def __init__(
        self,
        url: str = os.getenv("LIVEKIT_URL", "http://localhost:7880"),
        api_key: str = os.getenv("LIVEKIT_API_KEY", ""),
        api_secret: str = os.getenv("LIVEKIT_API_SECRET", ""),
    ):
        self._session = aiohttp.ClientSession()
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
