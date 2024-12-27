import aiohttp
from livekit.protocol.sip import (
    CreateSIPTrunkRequest,
    SIPTrunkInfo,
    CreateSIPInboundTrunkRequest,
    SIPInboundTrunkInfo,
    CreateSIPOutboundTrunkRequest,
    SIPOutboundTrunkInfo,
    ListSIPTrunkRequest,
    ListSIPTrunkResponse,
    ListSIPInboundTrunkRequest,
    ListSIPInboundTrunkResponse,
    ListSIPOutboundTrunkRequest,
    ListSIPOutboundTrunkResponse,
    DeleteSIPTrunkRequest,
    SIPDispatchRuleInfo,
    CreateSIPDispatchRuleRequest,
    ListSIPDispatchRuleRequest,
    ListSIPDispatchRuleResponse,
    DeleteSIPDispatchRuleRequest,
    CreateSIPParticipantRequest,
    TransferSIPParticipantRequest,
    SIPParticipantInfo,
)
from ._service import Service
from .access_token import VideoGrants, SIPGrants

SVC = "SIP"
"""@private"""


class SipService(Service):
    """Client for LiveKit SIP Service API

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    sip_service = lkapi.sip
    ```
    """

    def __init__(
        self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str
    ):
        super().__init__(session, url, api_key, api_secret)

    async def create_sip_trunk(self, create: CreateSIPTrunkRequest) -> SIPTrunkInfo:
        """
        @deprecated Use create_sip_inbound_trunk or create_sip_outbound_trunk instead
        """
        return await self._client.request(
            SVC,
            "CreateSIPTrunk",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            SIPTrunkInfo,
        )

    async def create_sip_inbound_trunk(
        self, create: CreateSIPInboundTrunkRequest
    ) -> SIPInboundTrunkInfo:
        return await self._client.request(
            SVC,
            "CreateSIPInboundTrunk",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            SIPInboundTrunkInfo,
        )

    async def create_sip_outbound_trunk(
        self, create: CreateSIPOutboundTrunkRequest
    ) -> SIPOutboundTrunkInfo:
        return await self._client.request(
            SVC,
            "CreateSIPOutboundTrunk",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            SIPOutboundTrunkInfo,
        )

    async def list_sip_trunk(self, list: ListSIPTrunkRequest) -> ListSIPTrunkResponse:
        return await self._client.request(
            SVC,
            "ListSIPTrunk",
            list,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            ListSIPTrunkResponse,
        )

    async def list_sip_inbound_trunk(
        self, list: ListSIPInboundTrunkRequest
    ) -> ListSIPInboundTrunkResponse:
        return await self._client.request(
            SVC,
            "ListSIPInboundTrunk",
            list,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            ListSIPInboundTrunkResponse,
        )

    async def list_sip_outbound_trunk(
        self, list: ListSIPOutboundTrunkRequest
    ) -> ListSIPOutboundTrunkResponse:
        return await self._client.request(
            SVC,
            "ListSIPOutboundTrunk",
            list,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            ListSIPOutboundTrunkResponse,
        )

    async def delete_sip_trunk(self, delete: DeleteSIPTrunkRequest) -> SIPTrunkInfo:
        return await self._client.request(
            SVC,
            "DeleteSIPTrunk",
            delete,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            SIPTrunkInfo,
        )

    async def create_sip_dispatch_rule(
        self, create: CreateSIPDispatchRuleRequest
    ) -> SIPDispatchRuleInfo:
        return await self._client.request(
            SVC,
            "CreateSIPDispatchRule",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            SIPDispatchRuleInfo,
        )

    async def list_sip_dispatch_rule(
        self, list: ListSIPDispatchRuleRequest
    ) -> ListSIPDispatchRuleResponse:
        return await self._client.request(
            SVC,
            "ListSIPDispatchRule",
            list,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            ListSIPDispatchRuleResponse,
        )

    async def delete_sip_dispatch_rule(
        self, delete: DeleteSIPDispatchRuleRequest
    ) -> SIPDispatchRuleInfo:
        return await self._client.request(
            SVC,
            "DeleteSIPDispatchRule",
            delete,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            SIPDispatchRuleInfo,
        )

    async def create_sip_participant(
        self, create: CreateSIPParticipantRequest
    ) -> SIPParticipantInfo:
        return await self._client.request(
            SVC,
            "CreateSIPParticipant",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(call=True)),
            SIPParticipantInfo,
        )

    async def transfer_sip_participant(
        self, transfer: TransferSIPParticipantRequest
    ) -> SIPParticipantInfo:
        return await self._client.request(
            SVC,
            "TransferSIPParticipant",
            transfer,
            self._auth_header(
                VideoGrants(
                    room_admin=True,
                    room=transfer.room_name,
                ),
                sip=SIPGrants(call=True),
            ),
            SIPParticipantInfo,
        )
