from __future__ import annotations

import aiohttp

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

    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str):
        super().__init__(session, url, api_key, api_secret)

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
        self, request: AcceptWhatsAppCallRequest
    ) -> AcceptWhatsAppCallResponse:
        """
        Accept an inbound WhatsApp call

        Args:
            request: AcceptWhatsAppCallRequest containing call parameters and SDP

        Returns:
            AcceptWhatsAppCallResponse with the room name
        """
        return await self._client.request(
            SVC,
            "AcceptWhatsAppCall",
            request,
            self._auth_header(VideoGrants(room_create=True)),
            AcceptWhatsAppCallResponse,
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
