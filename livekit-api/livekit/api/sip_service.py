import aiohttp
from livekit.protocol import sip as proto_sip
from ._service import Service
from .access_token import VideoGrants, SIPGrants

SVC = "SIP"


class SipService(Service):
    def __init__(
        self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str
    ):
        super().__init__(session, url, api_key, api_secret)

    async def create_sip_trunk(
        self, create: proto_sip.CreateSIPTrunkRequest
    ) -> proto_sip.SIPTrunkInfo:
        return await self._client.request(
            SVC,
            "CreateSIPTrunk",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.SIPTrunkInfo,
        )

    async def create_sip_inbound_trunk(
        self, create: proto_sip.CreateSIPInboundTrunkRequest
    ) -> proto_sip.SIPInboundTrunkInfo:
        return await self._client.request(
            SVC,
            "CreateSIPInboundTrunk",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.SIPInboundTrunkInfo,
        )

    async def create_sip_outbound_trunk(
        self, create: proto_sip.CreateSIPOutboundTrunkRequest
    ) -> proto_sip.SIPOutboundTrunkInfo:
        return await self._client.request(
            SVC,
            "CreateSIPOutboundTrunk",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.SIPOutboundTrunkInfo,
        )

    async def list_sip_trunk(
        self, list: proto_sip.ListSIPTrunkRequest
    ) -> proto_sip.ListSIPTrunkResponse:
        return await self._client.request(
            SVC,
            "ListSIPTrunk",
            list,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.ListSIPTrunkResponse,
        )

    async def list_sip_inbound_trunk(
        self, list: proto_sip.ListSIPInboundTrunkRequest
    ) -> proto_sip.ListSIPInboundTrunkResponse:
        return await self._client.request(
            SVC,
            "ListSIPInboundTrunk",
            list,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.ListSIPInboundTrunkResponse,
        )

    async def list_sip_outbound_trunk(
        self, list: proto_sip.ListSIPOutboundTrunkRequest
    ) -> proto_sip.ListSIPOutboundTrunkResponse:
        return await self._client.request(
            SVC,
            "ListSIPOutboundTrunk",
            list,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.ListSIPOutboundTrunkResponse,
        )

    async def delete_sip_trunk(
        self, delete: proto_sip.DeleteSIPTrunkRequest
    ) -> proto_sip.SIPTrunkInfo:
        return await self._client.request(
            SVC,
            "DeleteSIPTrunk",
            delete,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.SIPTrunkInfo,
        )

    async def create_sip_dispatch_rule(
        self, create: proto_sip.CreateSIPDispatchRuleRequest
    ) -> proto_sip.SIPDispatchRuleInfo:
        return await self._client.request(
            SVC,
            "CreateSIPDispatchRule",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.SIPDispatchRuleInfo,
        )

    async def list_sip_dispatch_rule(
        self, list: proto_sip.ListSIPDispatchRuleRequest
    ) -> proto_sip.ListSIPDispatchRuleResponse:
        return await self._client.request(
            SVC,
            "ListSIPDispatchRule",
            list,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.ListSIPDispatchRuleResponse,
        )

    async def delete_sip_dispatch_rule(
        self, delete: proto_sip.DeleteSIPDispatchRuleRequest
    ) -> proto_sip.SIPDispatchRuleInfo:
        return await self._client.request(
            SVC,
            "DeleteSIPDispatchRule",
            delete,
            self._auth_header(VideoGrants(), sip=SIPGrants(admin=True)),
            proto_sip.SIPDispatchRuleInfo,
        )

    async def create_sip_participant(
        self, create: proto_sip.CreateSIPParticipantRequest
    ) -> proto_sip.SIPParticipantInfo:
        return await self._client.request(
            SVC,
            "CreateSIPParticipant",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(call=True)),
            proto_sip.SIPParticipantInfo,
        )

    async def transfer_sip_participant(
        self, transfer: proto_sip.TransferSIPParticipantRequest
    ) -> proto_sip.SIPParticipantInfo:
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
            proto_sip.SIPParticipantInfo,
        )
