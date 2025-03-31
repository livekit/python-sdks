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

    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str):
        super().__init__(session, url, api_key, api_secret)

    async def start_room_composite_egress(self, start: RoomCompositeEgressRequest) -> EgressInfo:
        """Starts a composite recording of a room."""
        return await self._client.request(
            SVC,
            "StartRoomCompositeEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def start_web_egress(self, start: WebEgressRequest) -> EgressInfo:
        """Starts a recording of a web page."""
        return await self._client.request(
            SVC,
            "StartWebEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def start_participant_egress(self, start: ParticipantEgressRequest) -> EgressInfo:
        """Starts a recording of a participant."""
        return await self._client.request(
            SVC,
            "StartParticipantEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def start_track_composite_egress(self, start: TrackCompositeEgressRequest) -> EgressInfo:
        """Starts a composite recording with audio and video tracks."""
        return await self._client.request(
            SVC,
            "StartTrackCompositeEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def start_track_egress(self, start: TrackEgressRequest) -> EgressInfo:
        """Starts a recording of a single track."""
        return await self._client.request(
            SVC,
            "StartTrackEgress",
            start,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def update_layout(self, update: UpdateLayoutRequest) -> EgressInfo:
        """Updates the layout of a composite recording."""
        return await self._client.request(
            SVC,
            "UpdateLayout",
            update,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def update_stream(self, update: UpdateStreamRequest) -> EgressInfo:
        """Updates the stream of a RoomComposite, Web, or Participant recording."""
        return await self._client.request(
            SVC,
            "UpdateStream",
            update,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )

    async def list_egress(self, list: ListEgressRequest) -> ListEgressResponse:
        """Lists all active egress and recently completed recordings.

        Args:
            list (ListEgressRequest): arg contains optional filters:
                - room_name: str - List all egresses for a specific room
                - egress_id: str - Only list egress with matching ID
                - active: bool - Only list active egresses
        """
        return await self._client.request(
            SVC,
            "ListEgress",
            list,
            self._auth_header(VideoGrants(room_record=True)),
            ListEgressResponse,
        )

    async def stop_egress(self, stop: StopEgressRequest) -> EgressInfo:
        """Stops an active egress recording."""
        return await self._client.request(
            SVC,
            "StopEgress",
            stop,
            self._auth_header(VideoGrants(room_record=True)),
            EgressInfo,
        )
