import asyncio
from pyee.asyncio import AsyncIOEventEmitter
from ._ffi_client import (FfiClient, FfiHandle)
from ._proto import ffi_pb2 as proto_ffi
from ._proto import room_pb2 as proto_room
from ._proto import participant_pb2 as proto_participant
from .participant import (Participant, LocalParticipant, RemoteParticipant)
from .track_publication import (RemoteTrackPublication, LocalTrackPublication)
from .track import (RemoteAudioTrack, RemoteVideoTrack)
from livekit import TrackKind
import weakref


class ConnectError(Exception):
    def __init__(self, message: str):
        self.message = message


class Room(AsyncIOEventEmitter):
    def __init__(self):
        super().__init__()
        self._ffi_handle: FfiHandle = None
        self._room_info: proto_room.RoomInfo = None
        self._participants: dict[str, RemoteParticipant] = {}

    def __del__(self):
        ffi_client = FfiClient()
        ffi_client.remove_listener('room_event', self._on_room_event)

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
                # add existing participants
                for participant_info in cb.room.participants:
                    self._create_remote_participant(participant_info)

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
            ffi_client.add_listener('room_event', self._on_room_event)

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
            self.emit('track_published', publication, participant)
        elif which == 'track_unpublished':
            participant = self._participants[event.track_unpublished.participant_sid]
            publication = participant._tracks.pop(
                event.track_unpublished.publication_sid)
            self.emit('track_unpublished', publication, participant)
        elif which == 'track_subscribed':
            track_info = event.track_subscribed.track
            participant = self._participants[event.track_subscribed.participant_sid]
            publication = participant._tracks[track_info.sid]

            if track_info.kind == TrackKind.KIND_VIDEO:
                video_track = RemoteVideoTrack(
                    track_info, weakref.ref(self), weakref.ref(participant))
                publication._track = video_track
                self.emit('track_subscribed', video_track,
                          publication, participant)
            elif track_info.kind == TrackKind.KIND_AUDIO:
                audio_track = RemoteAudioTrack(
                    track_info, weakref.ref(self), weakref.ref(participant))
                publication._track = audio_track
                self.emit('track_subscribed', audio_track,
                          publication, participant)
        elif which == 'track_unsubscribed':
            participant = self._participants[event.track_unsubscribed.participant_sid]
            publication = participant._tracks[event.track_unsubscribed.track_sid]
            track = publication._track
            publication._track = None
            self.emit('track_unsubscribed', track, publication, participant)

    def _create_remote_participant(self, info: proto_participant.ParticipantInfo) -> RemoteParticipant:
        if info.sid in self._participants:
            raise Exception('participant already exists')

        participant = RemoteParticipant(info)
        self._participants[participant.sid] = participant

        #  add existing track publications
        for publication_info in info.publications:
            publication = RemoteTrackPublication(publication_info)
            participant._tracks[publication.sid] = publication

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
