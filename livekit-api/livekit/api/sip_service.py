from __future__ import annotations

import aiohttp
from typing import Optional

from livekit.protocol.models import ListUpdate
from livekit.protocol.sip import (
    SIPTrunkInfo,
    CreateSIPInboundTrunkRequest,
    UpdateSIPInboundTrunkRequest,
    SIPInboundTrunkInfo,
    SIPInboundTrunkUpdate,
    CreateSIPOutboundTrunkRequest,
    UpdateSIPOutboundTrunkRequest,
    SIPOutboundTrunkInfo,
    SIPOutboundTrunkUpdate,
    ListSIPInboundTrunkRequest,
    ListSIPInboundTrunkResponse,
    ListSIPOutboundTrunkRequest,
    ListSIPOutboundTrunkResponse,
    DeleteSIPTrunkRequest,
    SIPDispatchRule,
    SIPDispatchRuleInfo,
    SIPDispatchRuleUpdate,
    CreateSIPDispatchRuleRequest,
    UpdateSIPDispatchRuleRequest,
    ListSIPDispatchRuleRequest,
    ListSIPDispatchRuleResponse,
    DeleteSIPDispatchRuleRequest,
    CreateSIPParticipantRequest,
    TransferSIPParticipantRequest,
    SIPParticipantInfo,
    SIPTransport,
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

    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str):
        super().__init__(session, url, api_key, api_secret)

    async def create_sip_inbound_trunk(
        self, create: CreateSIPInboundTrunkRequest
    ) -> SIPInboundTrunkInfo:
        """Create a new SIP inbound trunk.

        Args:
            create: Request containing trunk details

        Returns:
            Created SIP inbound trunk
        """
        return await self._client.request(
            SVC,
            "CreateSIPInboundTrunk",
            create,
            self._admin_headers(),
            SIPInboundTrunkInfo,
        )

    async def update_sip_inbound_trunk(
        self,
        trunk_id: str,
        trunk: SIPInboundTrunkInfo,
    ) -> SIPInboundTrunkInfo:
        """Updates an existing SIP inbound trunk by replacing it entirely.

        Args:
            trunk_id: ID of the SIP inbound trunk to update
            trunk: SIP inbound trunk to update with

        Returns:
            Updated SIP inbound trunk
        """
        return await self._client.request(
            SVC,
            "UpdateSIPInboundTrunk",
            UpdateSIPInboundTrunkRequest(
                sip_trunk_id=trunk_id,
                replace=trunk,
            ),
            self._admin_headers(),
            SIPInboundTrunkInfo,
        )

    async def update_sip_inbound_trunk_fields(
        self,
        trunk_id: str,
        *,
        numbers: Optional[list[str]] = None,
        allowed_addresses: Optional[list[str]] = None,
        allowed_numbers: Optional[list[str]] = None,
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[str] = None,
    ) -> SIPInboundTrunkInfo:
        """Updates specific fields of an existing SIP inbound trunk.

        Only provided fields will be updated.
        """
        update = SIPInboundTrunkUpdate(
            auth_username=auth_username,
            auth_password=auth_password,
            name=name,
            metadata=metadata,
        )
        if numbers is not None:
            update.numbers = ListUpdate(set=numbers)
        if allowed_addresses is not None:
            update.allowed_addresses = ListUpdate(set=allowed_addresses)
        if allowed_numbers is not None:
            update.allowed_numbers = ListUpdate(set=allowed_numbers)

        return await self._client.request(
            SVC,
            "UpdateSIPInboundTrunk",
            UpdateSIPInboundTrunkRequest(
                sip_trunk_id=trunk_id,
                update=update,
            ),
            self._admin_headers(),
            SIPInboundTrunkInfo,
        )

    async def create_sip_outbound_trunk(
        self, create: CreateSIPOutboundTrunkRequest
    ) -> SIPOutboundTrunkInfo:
        """Create a new SIP outbound trunk.

        Args:
            create: Request containing trunk details

        Returns:
            Created SIP outbound trunk
        """
        return await self._client.request(
            SVC,
            "CreateSIPOutboundTrunk",
            create,
            self._admin_headers(),
            SIPOutboundTrunkInfo,
        )

    async def update_sip_outbound_trunk(
        self,
        trunk_id: str,
        trunk: SIPOutboundTrunkInfo,
    ) -> SIPOutboundTrunkInfo:
        """Updates an existing SIP outbound trunk by replacing it entirely.

        Args:
            trunk_id: ID of the SIP outbound trunk to update
            trunk: SIP outbound trunk to update with

        Returns:
            Updated SIP outbound trunk
        """
        return await self._client.request(
            SVC,
            "UpdateSIPOutboundTrunk",
            UpdateSIPOutboundTrunkRequest(
                sip_trunk_id=trunk_id,
                replace=trunk,
            ),
            self._admin_headers(),
            SIPOutboundTrunkInfo,
        )

    async def update_sip_outbound_trunk_fields(
        self,
        trunk_id: str,
        *,
        address: str | None = None,
        transport: SIPTransport | None = None,
        numbers: list[str] | None = None,
        auth_username: str | None = None,
        auth_password: str | None = None,
        name: str | None = None,
        metadata: str | None = None,
    ) -> SIPOutboundTrunkInfo:
        """Updates specific fields of an existing SIP outbound trunk.

        Only provided fields will be updated.
        """
        update = SIPOutboundTrunkUpdate(
            address=address,
            transport=transport,
            auth_username=auth_username,
            auth_password=auth_password,
            name=name,
            metadata=metadata,
        )
        if numbers is not None:
            update.numbers = ListUpdate(set=numbers)
        return await self._client.request(
            SVC,
            "UpdateSIPOutboundTrunk",
            UpdateSIPOutboundTrunkRequest(
                sip_trunk_id=trunk_id,
                update=update,
            ),
            self._admin_headers(),
            SIPOutboundTrunkInfo,
        )

    async def list_sip_inbound_trunk(
        self, list: ListSIPInboundTrunkRequest
    ) -> ListSIPInboundTrunkResponse:
        """List SIP inbound trunks with optional filtering.

        Args:
            list: Request with optional filtering parameters

        Returns:
            Response containing list of SIP inbound trunks
        """
        return await self._client.request(
            SVC,
            "ListSIPInboundTrunk",
            list,
            self._admin_headers(),
            ListSIPInboundTrunkResponse,
        )

    async def list_sip_outbound_trunk(
        self, list: ListSIPOutboundTrunkRequest
    ) -> ListSIPOutboundTrunkResponse:
        """List SIP outbound trunks with optional filtering.

        Args:
            list: Request with optional filtering parameters

        Returns:
            Response containing list of SIP outbound trunks
        """
        return await self._client.request(
            SVC,
            "ListSIPOutboundTrunk",
            list,
            self._admin_headers(),
            ListSIPOutboundTrunkResponse,
        )

    async def delete_sip_trunk(self, delete: DeleteSIPTrunkRequest) -> SIPTrunkInfo:
        """Delete a SIP trunk.

        Args:
            delete: Request containing trunk ID to delete

        Returns:
            Deleted trunk information
        """
        return await self._client.request(
            SVC,
            "DeleteSIPTrunk",
            delete,
            self._admin_headers(),
            SIPTrunkInfo,
        )

    async def create_sip_dispatch_rule(
        self, create: CreateSIPDispatchRuleRequest
    ) -> SIPDispatchRuleInfo:
        """Create a new SIP dispatch rule.

        Args:
            create: Request containing rule details

        Returns:
            Created SIP dispatch rule
        """
        return await self._client.request(
            SVC,
            "CreateSIPDispatchRule",
            create,
            self._admin_headers(),
            SIPDispatchRuleInfo,
        )

    async def update_sip_dispatch_rule(
        self,
        rule_id: str,
        rule: SIPDispatchRuleInfo,
    ) -> SIPDispatchRuleInfo:
        """Updates an existing SIP dispatch rule by replacing it entirely.

        Args:
            rule_id: ID of the SIP dispatch rule to update
            rule: SIP dispatch rule to update with

        Returns:
            Updated SIP dispatch rule
        """
        return await self._client.request(
            SVC,
            "UpdateSIPDispatchRule",
            UpdateSIPDispatchRuleRequest(sip_dispatch_rule_id=rule_id, replace=rule),
            self._admin_headers(),
            SIPDispatchRuleInfo,
        )

    async def update_sip_dispatch_rule_fields(
        self,
        rule_id: str,
        *,
        trunk_ids: Optional[list[str]] = None,
        rule: Optional[SIPDispatchRule] = None,
        name: Optional[str] = None,
        metadata: Optional[str] = None,
        attributes: Optional[dict[str, str]] = None,
    ) -> SIPDispatchRuleInfo:
        """Updates specific fields of an existing SIP dispatch rule.

        Only provided fields will be updated.
        """
        update = SIPDispatchRuleUpdate(
            name=name,
            metadata=metadata,
            rule=rule,
            attributes=attributes,
            trunk_ids=ListUpdate(set=trunk_ids) if trunk_ids else None,
        )
        return await self._client.request(
            SVC,
            "UpdateSIPDispatchRule",
            UpdateSIPDispatchRuleRequest(sip_dispatch_rule_id=rule_id, update=update),
            self._admin_headers(),
            SIPDispatchRuleInfo,
        )

    async def list_sip_dispatch_rule(
        self, list: ListSIPDispatchRuleRequest
    ) -> ListSIPDispatchRuleResponse:
        """List SIP dispatch rules with optional filtering.

        Args:
            list: Request with optional filtering parameters

        Returns:
            Response containing list of SIP dispatch rules
        """
        return await self._client.request(
            SVC,
            "ListSIPDispatchRule",
            list,
            self._admin_headers(),
            ListSIPDispatchRuleResponse,
        )

    async def delete_sip_dispatch_rule(
        self, delete: DeleteSIPDispatchRuleRequest
    ) -> SIPDispatchRuleInfo:
        """Delete a SIP dispatch rule.

        Args:
            delete: Request containing rule ID to delete

        Returns:
            Deleted rule information
        """
        return await self._client.request(
            SVC,
            "DeleteSIPDispatchRule",
            delete,
            self._admin_headers(),
            SIPDispatchRuleInfo,
        )

    async def create_sip_participant(
        self,
        create: CreateSIPParticipantRequest,
        *,
        timeout: Optional[float] = None,
    ) -> SIPParticipantInfo:
        """Create a new SIP participant.

        Args:
            create: Request containing participant details
            timeout: Optional request timeout in seconds

        Returns:
            Created SIP participant

        Raises:
            SIPError: If the SIP operation fails
        """
        client_timeout: Optional[aiohttp.ClientTimeout] = None
        if timeout:
            # obay user specified timeout
            client_timeout = aiohttp.ClientTimeout(total=timeout)
        elif create.wait_until_answered:
            # ensure default timeout isn't too short when using sync mode
            if (
                self._client._session.timeout
                and self._client._session.timeout.total
                and self._client._session.timeout.total < 20
            ):
                client_timeout = aiohttp.ClientTimeout(total=20)

        return await self._client.request(
            SVC,
            "CreateSIPParticipant",
            create,
            self._auth_header(VideoGrants(), sip=SIPGrants(call=True)),
            SIPParticipantInfo,
            timeout=client_timeout,
        )

    async def transfer_sip_participant(
        self, transfer: TransferSIPParticipantRequest
    ) -> SIPParticipantInfo:
        """Transfer a SIP participant to a different room.

        Args:
            transfer: Request containing transfer details

        Returns:
            Updated SIP participant information
        """
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

    def _admin_headers(self) -> dict[str, str]:
        return self._auth_header(VideoGrants(), sip=SIPGrants(admin=True))
