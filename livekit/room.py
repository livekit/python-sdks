from ctypes import *
import asyncio
from pyee.asyncio import AsyncIOEventEmitter
from ._ffi_client import (FfiClient, FfiHandle)
from .participant import (Participant, LocalParticipant, RemoteParticipant)
from .track_publication import (RemoteTrackPublication, LocalTrackPublication)
from ._proto import ffi_pb2 as proto_ffi
from ._proto import room_pb2 as proto_room
from ._proto import participant_pb2 as proto_participant


class ConnectError(Exception):
    def __init__(self, message: str):
        self.message = message


class Room(AsyncIOEventEmitter):
    def __init__(self):
        super().__init__()
        self._ffi_handle: FfiHandle = None
        self._room_info: proto_room.RoomInfo = None
        self._participants: dict[str, RemoteParticipant] = {}

    async def connect(self, url: str, token: str):
        # TODO(theomonnom): We should be more flexible about the event loop
        ffi_client = FfiClient()
        ffi_client.set_event_loop(asyncio.get_running_loop())

        req = proto_ffi.FfiRequest()
        req.connect.url = url
        req.connect.token = token

        resp = ffi_client.request(req)
        async_id = resp.connect.async_id

        future = asyncio.Future()

        def on_connect_callback(cb: proto_room.ConnectCallback):
            if cb.async_id == async_id:
                future.set_result(cb)
                ffi_client.remove_listener('connect', on_connect_callback)

        ffi_client.add_listener('connect', on_connect_callback)
        resp = await future

        if resp.error:
            raise ConnectError(resp.error)
        else:
            self._ffi_handle = FfiHandle(resp.room.handle.id)
            self._room_info = resp.room
            self._close_future = asyncio.Future()
            ffi_client.add_listener('room', self._on_room_event)

    async def close(self):
        self._ffi_handle = None
        # TODO(theomonnom): wait for ffi resp
        self._close_future.set_result(None)

    async def run(self):
        await self._close_future

    def _on_room_event(self, event: proto_room.RoomEvent):
        which = event.WhichOneof('message')
        if which == 'participant_connected':
            remote_participant = self._create_remote_participant(
                event.participant_connected.info)
            self.emit('participant_connected', remote_participant)
        elif which == 'participant_disconnected':
            sid = event.participant_disconnected.info.sid
            participant = self._participants.pop(sid)
            self.emit('participant_disconnected', participant)
        elif which == 'track_published':
            participant = self._participants[event.track_published.participant_sid]
            publication = RemoteTrackPublication(
                event.track_published.publication)
            participant._tracks[publication.sid] = publication
            self.emit('track_published', publication)
        elif which == 'track_unpublished':
            participant = self._participants[event.track_unpublished.participant_sid]

    def _create_remote_participant(self, info: proto_participant.ParticipantInfo) -> RemoteParticipant:
        participant = RemoteParticipant(info)
        self._participants[participant.sid] = participant

        # TODO(publications)

        return participant

    @property
    def sid(self) -> str:
        return self._room_info.sid

    @property
    def name(self) -> str:
        return self._room_info.name

    @property
    def metadata(self) -> str:
        return self._room_info.metadata
