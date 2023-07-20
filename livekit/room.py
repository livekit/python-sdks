import asyncio
from pyee.asyncio import AsyncIOEventEmitter
from ._ffi_client import (FfiClient, FfiHandle)
from ._proto import ffi_pb2 as proto_ffi
from ._proto import room_pb2 as proto_room
from ._proto import participant_pb2 as proto_participant
from .participant import (Participant, LocalParticipant, RemoteParticipant)
from .track_publication import (RemoteTrackPublication, LocalTrackPublication)
from .track import (RemoteAudioTrack, RemoteVideoTrack,
                    LocalVideoTrack, LocalAudioTrack)
from livekit import (TrackKind, ConnectionState)
import weakref
import ctypes


class ConnectError(Exception):
    def __init__(self, message: str):
        self.message = message


class Room(AsyncIOEventEmitter):
    def __init__(self) -> None:
        super().__init__()
        self.participants: dict[str, RemoteParticipant] = {}
        self.connection_state = ConnectionState.CONN_DISCONNECTED

        ffi_client = FfiClient()
        ffi_client.add_listener('room_event', self._on_room_event)

    def __del__(self):
        ffi_client = FfiClient()
        ffi_client.remove_listener('room_event', self._on_room_event)

    @property
    def sid(self) -> str:
        return self._info.sid

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def metadata(self) -> str:
        return self._info.metadata

    def isconnected(self) -> bool:
        return self._ffi_handle is not None and self.connection_state == ConnectionState.CONN_CONNECTED

    async def connect(self, url: str, token: str) -> None:
        # TODO(theomonnom): We should be more flexible about the event loop
        ffi_client = FfiClient()
        ffi_client.set_event_loop(asyncio.get_running_loop())

        req = proto_ffi.FfiRequest()
        req.connect.url = url
        req.connect.token = token

        resp = ffi_client.request(req)
        future: asyncio.Future[proto_room.ConnectCallback] = asyncio.Future()

        @ffi_client.listens_to('connect')
        def on_connect_callback(cb: proto_room.ConnectCallback):
            if cb.async_id == resp.connect.async_id:
                future.set_result(cb)
                ffi_client.remove_listener('connect', on_connect_callback)

        cb = await future
        if cb.error:
            raise ConnectError(cb.error)

        self._ffi_handle = FfiHandle(cb.room.handle.id)
        self._info = cb.room
        self._close_future: asyncio.Future[None] = asyncio.Future()

        self.local_participant = LocalParticipant(
            cb.room.local_participant, weakref.ref(self))

        for participant_info in cb.room.participants:
            self._create_remote_participant(participant_info)

    async def disconnect(self) -> None:
        if not self.isconnected():
            return

        ffi_client = FfiClient()

        req = proto_ffi.FfiRequest()
        req.disconnect.room_handle.id = self._ffi_handle.handle

        resp = ffi_client.request(req)
        future: asyncio.Future[proto_room.DisconnectCallback] = asyncio.Future(
        )

        @ffi_client.on('disconnect')
        def on_disconnect_callback(cb: proto_room.DisconnectCallback):
            if cb.async_id == resp.disconnect.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'disconnect', on_disconnect_callback)

        await future
        if not self._close_future.cancelled():
            self._close_future.set_result(None)

    async def run(self) -> None:
        # wait for disconnect
        await self._close_future

    def _on_room_event(self, event: proto_room.RoomEvent):
        if event.room_handle.id != self._ffi_handle.handle:
            return

        which = event.WhichOneof('message')
        if which == 'participant_connected':
            remote_participant = self._create_remote_participant(
                event.participant_connected.info)
            self.emit('participant_connected', remote_participant)
        elif which == 'participant_disconnected':
            sid = event.participant_disconnected.info.sid
            participant = self.participants.pop(sid)
            self.emit('participant_disconnected', participant)
        elif which == 'local_track_published':
            publication = LocalTrackPublication(
                event.local_track_published.publication, weakref.ref(self.local_participant))
            track_info = event.local_track_published.track
            ffi_handle = FfiHandle(track_info.handle.id)

            self.local_participant.tracks[publication.sid] = publication

            if track_info.kind == TrackKind.KIND_VIDEO:
                track = LocalVideoTrack(ffi_handle, track_info)
                publication.track = track
                self.emit('local_track_published', publication, track)
            elif track_info.kind == TrackKind.KIND_AUDIO:
                track = LocalAudioTrack(ffi_handle, track_info)
                publication.track = track
                self.emit('local_track_published', publication, track)
        elif which == 'local_track_unpublished':
            publication = self.local_participant.tracks.pop(
                event.local_track_unpublished.publication_sid)
            publication.track = None
            self.emit('local_track_unpublished', publication)
        elif which == 'track_published':
            participant = self.participants[event.track_published.participant_sid]
            publication = RemoteTrackPublication(
                event.track_published.publication, weakref.ref(participant))
            participant.tracks[publication.sid] = publication
            self.emit('track_published', publication, participant)
        elif which == 'track_unpublished':
            participant = self.participants[event.track_unpublished.participant_sid]
            publication = participant.tracks.pop(
                event.track_unpublished.publication_sid)
            self.emit('track_unpublished', publication, participant)
        elif which == 'track_subscribed':
            track_info = event.track_subscribed.track
            participant = self.participants[event.track_subscribed.participant_sid]
            publication = participant.tracks[track_info.sid]
            ffi_handle = FfiHandle(track_info.handle.id)
            publication.subscribed = True
            if track_info.kind == TrackKind.KIND_VIDEO:
                video_track = RemoteVideoTrack(ffi_handle, track_info)
                publication.track = video_track
                self.emit('track_subscribed', video_track,
                          publication, participant)
            elif track_info.kind == TrackKind.KIND_AUDIO:
                audio_track = RemoteAudioTrack(ffi_handle, track_info)
                publication.track = audio_track
                self.emit('track_subscribed', audio_track,
                          publication, participant)
        elif which == 'track_unsubscribed':
            participant = self.participants[event.track_unsubscribed.participant_sid]
            publication = participant.tracks[event.track_unsubscribed.track_sid]
            track = publication.track
            publication.track = None
            publication.subscribed = False
            self.emit('track_unsubscribed', track, publication, participant)
        elif which == 'track_subscription_failed':
            participant = self.participants[event.track_subscription_failed.participant_sid]
            error = event.track_subscription_failed.error
            self.emit('track_subscription_failed', participant,
                      event.track_subscription_failed.track_sid, error)
        elif which == 'track_muted':
            sid = event.track_muted.participant_sid
            if sid == self.local_participant.sid:
                participant = self.local_participant
            else:
                participant = self.participants[sid]

            publication = participant.tracks[event.track_muted.track_sid]
            publication._info.muted = True
            if publication.track:
                publication.track._info.muted = True

            self.emit('track_muted', participant, publication)
        elif which == 'track_unmuted':
            sid = event.track_unmuted.participant_sid
            if sid == self.local_participant.sid:
                participant = self.local_participant
            else:
                participant = self.participants[sid]

            publication = participant.tracks[event.track_unmuted.track_sid]
            publication._info.muted = False
            if publication.track:
                publication.track._info.muted = False

            self.emit('track_unmuted', participant, publication)
        elif which == 'active_speakers_changed':
            speakers = []
            for sid in event.active_speakers_changed.participant_sids:
                if sid == self.local_participant.sid:
                    speakers.append(self.local_participant)
                else:
                    speakers.append(self.participants[sid])

            self.emit('active_speakers_changed', speakers)
        elif which == 'connection_quality_changed':
            sid = event.connection_quality_changed.participant_sid
            if sid == self.local_participant.sid:
                participant = self.local_participant
            else:
                participant = self.participants[sid]

            self.emit('connection_quality_changed',
                      participant, event.connection_quality_changed.quality)
        elif which == 'data_received':
            participant = self.participants[event.data_received.participant_sid]
            data = ctypes.cast(event.data_received.data_ptr,
                               ctypes.POINTER(ctypes.c_byte * event.data_received.data_size)).contents
            data = bytes(data)
            FfiHandle(event.data_received.handle.id)
            self.emit('data_received', data,
                      event.data_received.kind, participant)
        elif which == 'connection_state_changed':
            state = event.connection_state_changed.state
            self.connection_state = state
            self.emit('connection_state_changed', state)
        elif which == 'connected':
            self.emit('connected')
        elif which == 'disconnected':
            self.emit('disconnected')
        elif which == 'reconnecting':
            self.emit('reconnecting')
        elif which == 'reconnected':
            self.emit('reconnected')

    def _create_remote_participant(self, info: proto_participant.ParticipantInfo) -> RemoteParticipant:
        if info.sid in self.participants:
            raise Exception('participant already exists')

        participant = RemoteParticipant(info)
        self.participants[participant.sid] = participant

        for publication_info in info.publications:
            publication = RemoteTrackPublication(
                publication_info, weakref.ref(participant))
            participant.tracks[publication.sid] = publication

        return participant
