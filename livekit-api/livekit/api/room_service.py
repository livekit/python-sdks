import aiohttp
from livekit.protocol.room import (
    CreateRoomRequest,
    ListRoomsRequest,
    DeleteRoomRequest,
    ListRoomsResponse,
    DeleteRoomResponse,
    ListParticipantsRequest,
    ListParticipantsResponse,
    RoomParticipantIdentity,
    MuteRoomTrackRequest,
    MuteRoomTrackResponse,
    UpdateParticipantRequest,
    UpdateSubscriptionsRequest,
    SendDataRequest,
    SendDataResponse,
    UpdateRoomMetadataRequest,
    RemoveParticipantResponse,
    UpdateSubscriptionsResponse,
)
from livekit.protocol.models import Room, ParticipantInfo
from ._service import Service
from .access_token import VideoGrants

SVC = "RoomService"
"""@private"""


class RoomService(Service):
    """Client for LiveKit RoomService API

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    room_service = lkapi.room
    ```

    Also see https://docs.livekit.io/home/server/managing-rooms/ and https://docs.livekit.io/home/server/managing-participants/
    """

    def __init__(
        self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str
    ):
        super().__init__(session, url, api_key, api_secret)

    async def create_room(
        self,
        create: CreateRoomRequest,
    ) -> Room:
        """Creates a new room with specified configuration.

        Args:
            create (CreateRoomRequest): arg containing:
                - name: str - Unique room name
                - empty_timeout: int - Seconds to keep room open if empty
                - max_participants: int - Max allowed participants
                - metadata: str - Custom room metadata
                - egress: RoomEgress - Egress configuration
                - min_playout_delay: int - Minimum playout delay in ms
                - max_playout_delay: int - Maximum playout delay in ms
                - sync_streams: bool - Enable A/V sync for playout delays >200ms

        Returns:
            Room: The created room object
        """
        return await self._client.request(
            SVC,
            "CreateRoom",
            create,
            self._auth_header(VideoGrants(room_create=True)),
            Room,
        )

    async def list_rooms(self, list: ListRoomsRequest) -> ListRoomsResponse:
        """Lists active rooms.

        Args:
            list (ListRoomsRequest): arg containing:
                - names: list[str] - Optional list of room names to filter by

        Returns:
            ListRoomsResponse:
                - rooms: list[Room] - List of active Room objects
        """
        return await self._client.request(
            SVC,
            "ListRooms",
            list,
            self._auth_header(VideoGrants(room_list=True)),
            ListRoomsResponse,
        )

    async def delete_room(self, delete: DeleteRoomRequest) -> DeleteRoomResponse:
        """Deletes a room and disconnects all participants.

        Args:
            delete (DeleteRoomRequest): arg containing:
                - room: str - Name of room to delete

        Returns:
            DeleteRoomResponse: Empty response object
        """
        return await self._client.request(
            SVC,
            "DeleteRoom",
            delete,
            self._auth_header(VideoGrants(room_create=True)),
            DeleteRoomResponse,
        )

    async def update_room_metadata(self, update: UpdateRoomMetadataRequest) -> Room:
        """Updates a room's [metadata](https://docs.livekit.io/home/client/data/room-metadata/).

        Args:
            update (UpdateRoomMetadataRequest): arg containing:
                - room: str - Name of room to update
                - metadata: str - New metadata to set

        Returns:
            Room: Updated Room object
        """
        return await self._client.request(
            SVC,
            "UpdateRoomMetadata",
            update,
            self._auth_header(VideoGrants(room_admin=True, room=update.room)),
            Room,
        )

    async def list_participants(
        self, list: ListParticipantsRequest
    ) -> ListParticipantsResponse:
        """Lists all participants in a room.

        Args:
            list (ListParticipantsRequest): arg containing:
                - room: str - Name of room to list participants from

        Returns:
            ListParticipantsResponse:
                - participants: list[ParticipantInfo] - List of participant details
        """
        return await self._client.request(
            SVC,
            "ListParticipants",
            list,
            self._auth_header(VideoGrants(room_admin=True, room=list.room)),
            ListParticipantsResponse,
        )

    async def get_participant(self, get: RoomParticipantIdentity) -> ParticipantInfo:
        """Gets details about a specific participant.

        Args:
            get (RoomParticipantIdentity): arg containing:
                - room: str - Room name
                - identity: str - Participant identity to look up

        Returns:
            ParticipantInfo:
                - sid: str - Participant session ID
                - identity: str - Participant identity
                - state: int - Connection state
                - tracks: list[TrackInfo] - Published tracks
                - metadata: str - Participant metadata
                - joined_at: int - Join timestamp
                - name: str - Display name
                - version: int - Protocol version
                - permission: ParticipantPermission - Granted permissions
                - region: str - Connected region
        """
        return await self._client.request(
            SVC,
            "GetParticipant",
            get,
            self._auth_header(VideoGrants(room_admin=True, room=get.room)),
            ParticipantInfo,
        )

    async def remove_participant(
        self, remove: RoomParticipantIdentity
    ) -> RemoveParticipantResponse:
        """Removes a participant from a room.

        Args:
            remove (RoomParticipantIdentity): arg containing:
                - room: str - Room name
                - identity: str - Identity of participant to remove

        Returns:
            RemoveParticipantResponse: Empty response object
        """
        return await self._client.request(
            SVC,
            "RemoveParticipant",
            remove,
            self._auth_header(VideoGrants(room_admin=True, room=remove.room)),
            RemoveParticipantResponse,
        )

    async def mute_published_track(
        self,
        update: MuteRoomTrackRequest,
    ) -> MuteRoomTrackResponse:
        """Mutes or unmutes a participant's published track.

        Args:
            update (MuteRoomTrackRequest): arg containing:
                - room: str - Room name
                - identity: str - Participant identity
                - track_sid: str - Track session ID to mute
                - muted: bool - True to mute, False to unmute

        Returns:
            MuteRoomTrackResponse containing:
                - track: TrackInfo - Updated track information
        """
        return await self._client.request(
            SVC,
            "MutePublishedTrack",
            update,
            self._auth_header(VideoGrants(room_admin=True, room=update.room)),
            MuteRoomTrackResponse,
        )

    async def update_participant(
        self, update: UpdateParticipantRequest
    ) -> ParticipantInfo:
        """Updates a participant's metadata or permissions.

        Args:
            update (UpdateParticipantRequest): arg containing:
                - room: str - Room name
                - identity: str - Participant identity
                - metadata: str - New metadata
                - permission: ParticipantPermission - New permissions
                - name: str - New display name
                - attributes: dict[str, str] - Key-value attributes

        Returns:
            ParticipantInfo: Updated participant information
        """
        return await self._client.request(
            SVC,
            "UpdateParticipant",
            update,
            self._auth_header(VideoGrants(room_admin=True, room=update.room)),
            ParticipantInfo,
        )

    async def update_subscriptions(
        self, update: UpdateSubscriptionsRequest
    ) -> UpdateSubscriptionsResponse:
        """Updates a participant's track subscriptions.

        Args:
            update (UpdateSubscriptionsRequest): arg containing:
                - room: str - Room name
                - identity: str - Participant identity
                - track_sids: list[str] - Track session IDs
                - subscribe: bool - True to subscribe, False to unsubscribe
                - participant_tracks: list[ParticipantTracks] - Participant track mappings

        Returns:
            UpdateSubscriptionsResponse: Empty response object
        """
        return await self._client.request(
            SVC,
            "UpdateSubscriptions",
            update,
            self._auth_header(VideoGrants(room_admin=True, room=update.room)),
            UpdateSubscriptionsResponse,
        )

    async def send_data(self, send: SendDataRequest) -> SendDataResponse:
        """Sends data to participants in a room.

        Args:
            send (SendDataRequest): arg containing:
                - room: str - Room name
                - data: bytes - Data payload to send
                - kind: DataPacket.Kind - RELIABLE or LOSSY delivery
                - destination_identities: list[str] - Target participant identities
                - topic: str - Optional topic for the message

        Returns:
            SendDataResponse: Empty response object
        """
        return await self._client.request(
            SVC,
            "SendData",
            send,
            self._auth_header(VideoGrants(room_admin=True, room=send.room)),
            SendDataResponse,
        )
