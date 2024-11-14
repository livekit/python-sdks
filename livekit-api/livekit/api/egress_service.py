import aiohttp
from livekit.protocol.egress import (
    RoomCompositeEgressRequest,
    WebEgressRequest,
    ParticipantEgressRequest,
    TrackCompositeEgressRequest,
    TrackEgressRequest,
    UpdateLayoutRequest,
    UpdateStreamRequest,
    ListEgressRequest,
    StopEgressRequest,
    EgressInfo,
    ListEgressResponse,
)
from ._service import Service
from .access_token import VideoGrants

SVC = "Egress"
"""@private"""


class EgressService(Service):
    """Client for LiveKit Egress Service API

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    egress = lkapi.egress
    ```

    Also see https://docs.livekit.io/home/egress/overview/
    """

    def __init__(
        self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str
    ):
        super().__init__(session, url, api_key, api_secret)

    async def start_room_composite_egress(
        self, start: RoomCompositeEgressRequest
    ) -> EgressInfo:
        return await self._client.request(
            SVC,
            "StartRoomCompositeEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def start_web_egress(self, start: WebEgressRequest) -> EgressInfo:
        return await self._client.request(
            SVC,
            "StartWebEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def start_participant_egress(
        self, start: ParticipantEgressRequest
    ) -> EgressInfo:
        return await self._client.request(
            SVC,
            "StartParticipantEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def start_track_composite_egress(
        self, start: TrackCompositeEgressRequest
    ) -> EgressInfo:
        return await self._client.request(
            SVC,
            "StartTrackCompositeEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def start_track_egress(self, start: TrackEgressRequest) -> EgressInfo:
        return await self._client.request(
            SVC,
            "StartTrackEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def update_layout(self, update: UpdateLayoutRequest) -> EgressInfo:
        return await self._client.request(
            SVC,
            "UpdateLayout",
            update,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def update_stream(self, update: UpdateStreamRequest) -> EgressInfo:
        return await self._client.request(
            SVC,
            "UpdateStream",
            update,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def list_egress(self, list: ListEgressRequest) -> ListEgressResponse:
        return await self._client.request(
            SVC,
            "ListEgress",
            list,
            self._auth_header(VideoGrants(room_record=True)),
            ListEgressResponse,
        )

    async def stop_egress(self, stop: StopEgressRequest) -> EgressInfo:
        return await self._client.request(
            SVC,
            "StopEgress",
            stop,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )
