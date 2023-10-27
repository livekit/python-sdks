from ._proto import livekit_models_pb2 as proto_models
from ._proto import livekit_room_pb2 as proto_room
from ._service import Service
from .access_token import VideoGrants

SVC = "RoomService"


class RoomService(Service):
    def __init__(self, host: str, api_key: str, api_secret: str):
        super().__init__(host, api_key, api_secret)

    async def create_room(
        self, create: proto_room.CreateRoomRequest
    ) -> proto_models.Room:
        return await self._client.request(
            SVC,
            "CreateRoom",
            create,
            self._auth_header(VideoGrants(room_create=True)),
            proto_models.Room,
        )

    async def list_rooms(
        self, list: proto_room.ListRoomsRequest
    ) -> proto_room.ListRoomsResponse:
        return await self._client.request(
            SVC,
            "ListRooms",
            list,
            self._auth_header(VideoGrants(room_list=True)),
            proto_room.ListRoomsResponse,
        )

    async def delete_room(
        self, delete: proto_room.DeleteRoomRequest
    ) -> proto_room.DeleteRoomResponse:
        return await self._client.request(
            SVC,
            "DeleteRoom",
            delete,
            self._auth_header(VideoGrants(room_create=True)),
            proto_room.DeleteRoomResponse,
        )

    async def update_room_metadata(
        self, update: proto_room.UpdateRoomMetadataRequest
    ) -> proto_models.Room:
        return await self._client.request(
            SVC,
            "UpdateRoomMetadata",
            update,
            self._auth_header(VideoGrants(room_admin=True, room=update.room)),
            proto_models.Room,
        )

    async def list_participants(
        self, list: proto_room.ListParticipantsRequest
    ) -> proto_room.ListParticipantsResponse:
        return await self._client.request(
            SVC,
            "ListParticipants",
            list,
            self._auth_header(VideoGrants(room_admin=True, room=list.room)),
            proto_room.ListParticipantsResponse,
        )

    async def get_participant(
        self, get: proto_room.RoomParticipantIdentity
    ) -> proto_models.ParticipantInfo:
        return await self._client.request(
            SVC,
            "GetParticipant",
            get,
            self._auth_header(VideoGrants(room_admin=True, room=get.room)),
            proto_models.ParticipantInfo,
        )

    async def remove_participant(
        self, remove: proto_room.RoomParticipantIdentity
    ) -> proto_room.RemoveParticipantResponse:
        return await self._client.request(
            SVC,
            "remove_participant",
            remove,
            self._auth_header(VideoGrants(room_admin=True, room=remove.room)),
            proto_room.RemoveParticipantResponse,
        )
