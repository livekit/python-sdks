from __future__ import annotations

import aiohttp
from typing import Optional

from livekit.protocol.connector_whatsapp import (
    DialWhatsAppCallRequest,
    DialWhatsAppCallResponse,
    DisconnectWhatsAppCallRequest,
    DisconnectWhatsAppCallResponse,
    ConnectWhatsAppCallRequest,
    ConnectWhatsAppCallResponse,
    AcceptWhatsAppCallRequest,
    AcceptWhatsAppCallResponse,
)
from livekit.protocol.connector_twilio import (
    ConnectTwilioCallRequest,
    ConnectTwilioCallResponse,
)
from ._service import Service
from ._dial_timeout import dial_timeout
from .access_token import VideoGrants

SVC = "Connector"
"""@private"""


class ConnectorService(Service):
    """Client for LiveKit Connector Service API

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    connector_service = lkapi.connector
    ```
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        api_key: str,
        api_secret: str,
        failover: bool = True,
    ):
        super().__init__(session, url, api_key, api_secret, failover=failover)

    async def dial_whatsapp_call(
        self, request: DialWhatsAppCallRequest
    ) -> DialWhatsAppCallResponse:
        """
        Initiate an outbound WhatsApp call

        Args:
            request: DialWhatsAppCallRequest containing call parameters

        Returns:
            DialWhatsAppCallResponse with the WhatsApp call ID and room name
        """
        return await self._client.request(
            SVC,
            "DialWhatsAppCall",
            request,
            self._auth_header(VideoGrants(room_create=True)),
            DialWhatsAppCallResponse,
        )

    async def disconnect_whatsapp_call(
        self, request: DisconnectWhatsAppCallRequest
    ) -> DisconnectWhatsAppCallResponse:
        """
        Disconnect an active WhatsApp call

        Args:
            request: DisconnectWhatsAppCallRequest containing the call ID to disconnect

        Returns:
            DisconnectWhatsAppCallResponse (empty response)
        """
        return await self._client.request(
            SVC,
            "DisconnectWhatsAppCall",
            request,
            self._auth_header(VideoGrants(room_create=True)),
            DisconnectWhatsAppCallResponse,
        )

    async def connect_whatsapp_call(
        self, request: ConnectWhatsAppCallRequest
    ) -> ConnectWhatsAppCallResponse:
        """
        Connect a WhatsApp call with SDP information

        Args:
            request: ConnectWhatsAppCallRequest containing call ID and SDP

        Returns:
            ConnectWhatsAppCallResponse (empty response)
        """
        return await self._client.request(
            SVC,
            "ConnectWhatsAppCall",
            request,
            self._auth_header(VideoGrants(room_create=True)),
            ConnectWhatsAppCallResponse,
        )

    async def accept_whatsapp_call(
        self,
        request: AcceptWhatsAppCallRequest,
        *,
        timeout: Optional[float] = None,
    ) -> AcceptWhatsAppCallResponse:
        """
        Accept an inbound WhatsApp call

        Args:
            request: AcceptWhatsAppCallRequest containing call parameters and SDP
            timeout: Optional request timeout in seconds. When the request waits
                for an answer (wait_until_answered), it defaults to a longer value
                (dialing takes time) and is raised, if needed, to stay above the
                request's ringing_timeout.

        Returns:
            AcceptWhatsAppCallResponse with the room name
        """
        client_timeout: Optional[aiohttp.ClientTimeout] = None
        if request.wait_until_answered:
            # Waiting for the call to be answered dials a phone, which takes
            # longer than a normal request and must outlast ringing.
            client_timeout = aiohttp.ClientTimeout(total=dial_timeout(timeout, request))
        elif timeout:
            client_timeout = aiohttp.ClientTimeout(total=timeout)

        return await self._client.request(
            SVC,
            "AcceptWhatsAppCall",
            request,
            self._auth_header(VideoGrants(room_create=True)),
            AcceptWhatsAppCallResponse,
            timeout=client_timeout,
        )

    async def connect_twilio_call(
        self, request: ConnectTwilioCallRequest
    ) -> ConnectTwilioCallResponse:
        """
        Connect a Twilio call to a LiveKit room

        Args:
            request: ConnectTwilioCallRequest containing call parameters

        Returns:
            ConnectTwilioCallResponse with the websocket URL for Twilio media stream
        """
        return await self._client.request(
            SVC,
            "ConnectTwilioCall",
            request,
            self._auth_header(VideoGrants(room_create=True)),
            ConnectTwilioCallResponse,
        )
