import aiohttp
from livekit.protocol.ingress import (
    CreateIngressRequest,
    IngressInfo,
    UpdateIngressRequest,
    ListIngressRequest,
    DeleteIngressRequest,
    ListIngressResponse,
)
from ._service import Service
from .access_token import VideoGrants

SVC = "Ingress"
"""@private"""


class IngressService(Service):
    """Client for LiveKit Ingress Service API

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    ingress = lkapi.ingress
    ```

    Also see https://docs.livekit.io/home/ingress/overview/
    """

    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str):
        super().__init__(session, url, api_key, api_secret)

    async def create_ingress(self, create: CreateIngressRequest) -> IngressInfo:
        return await self._client.request(
            SVC,
            "CreateIngress",
            create,
            self._auth_header(VideoGrants(ingress_admin=True)),
            IngressInfo,
        )

    async def update_ingress(self, update: UpdateIngressRequest) -> IngressInfo:
        return await self._client.request(
            SVC,
            "UpdateIngress",
            update,
            self._auth_header(VideoGrants(ingress_admin=True)),
            IngressInfo,
        )

    async def list_ingress(self, list: ListIngressRequest) -> ListIngressResponse:
        return await self._client.request(
            SVC,
            "ListIngress",
            list,
            self._auth_header(VideoGrants(ingress_admin=True)),
            ListIngressResponse,
        )

    async def delete_ingress(self, delete: DeleteIngressRequest) -> IngressInfo:
        return await self._client.request(
            SVC,
            "DeleteIngress",
            delete,
            self._auth_header(VideoGrants(ingress_admin=True)),
            IngressInfo,
        )
