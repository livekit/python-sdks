import aiohttp
from livekit.protocol.room import CreateRoomRequest, ListRoomsRequest, DeleteRoomRequest, ListRoomsResponse, DeleteRoomResponse, ListParticipantsRequest, ListParticipantsResponse, RoomParticipantIdentity, MuteRoomTrackRequest, MuteRoomTrackResponse, UpdateParticipantRequest, UpdateSubscriptionsRequest, SendDataRequest, SendDataResponse, UpdateRoomMetadataRequest, RemoveParticipantResponse, UpdateSubscriptionsResponse
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

    async def create_room(self, create: CreateRoomRequest) -> Room:
        return await self._client.request(
            SVC,
            "CreateRoom",
            create,
            self._auth_header(VideoGrants(room_create=True)),
            Room,
        )

    async def list_rooms(self, list: ListRoomsRequest) -> ListRoomsResponse:
        return await self._client.request(
            SVC,
            "ListRooms",
            list,
            self._auth_header(VideoGrants(room_list=True)),
            ListRoomsResponse,
        )

    async def delete_room(self, delete: DeleteRoomRequest) -> DeleteRoomResponse:
        return await self._client.request(
            SVC,
            "DeleteRoom",
            delete,
            self._auth_header(VideoGrants(room_create=True)),
            DeleteRoomResponse,
        )

    async def update_room_metadata(self, update: UpdateRoomMetadataRequest) -> Room:
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
        return await self._client.request(
            SVC,
            "ListParticipants",
            list,
            self._auth_header(VideoGrants(room_admin=True, room=list.room)),
            ListParticipantsResponse,
        )

    async def get_participant(self, get: RoomParticipantIdentity) -> ParticipantInfo:
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
        return await self._client.request(
            SVC,
            "UpdateSubscriptions",
            update,
            self._auth_header(VideoGrants(room_admin=True, room=update.room)),
            UpdateSubscriptionsResponse,
        )

    async def send_data(self, send: SendDataRequest) -> SendDataResponse:
        return await self._client.request(
            SVC,
            "SendData",
            send,
            self._auth_header(VideoGrants(room_admin=True, room=send.room)),
            SendDataResponse,
        )
