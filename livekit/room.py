# Copyright 2023 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import ctypes
from dataclasses import dataclass
from typing import Optional

from pyee.asyncio import EventEmitter

from ._ffi_client import FfiHandle, ffi_client
from ._proto import ffi_pb2 as proto_ffi
from ._proto import participant_pb2 as proto_participant
from ._proto import room_pb2 as proto_room
from ._proto.room_pb2 import ConnectionState
from ._proto.track_pb2 import TrackKind
from .participant import LocalParticipant, Participant, RemoteParticipant
from .track import RemoteAudioTrack, RemoteVideoTrack
from .track_publication import RemoteTrackPublication


@dataclass
class RoomOptions:
    auto_subscribe: bool = True
    dynacast: bool = True


class ConnectError(Exception):
    def __init__(self, message: str):
        self.message = message


class Room(EventEmitter):
    def __init__(self) -> None:
        super().__init__()
        self.participants: dict[str, RemoteParticipant] = {}
        self.connection_state = ConnectionState.CONN_DISCONNECTED
        self._ffi_handle: Optional[FfiHandle] = None
        ffi_client.add_listener('room_event', self._on_room_event)

    def __del__(self):
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
        return self._ffi_handle is not None and \
            self.connection_state != ConnectionState.CONN_DISCONNECTED

    async def connect(self,
                      url: str,
                      token: str,
                      options: RoomOptions = RoomOptions()) -> None:
        req = proto_ffi.FfiRequest()
        req.connect.url = url
        req.connect.token = token

        # options
        req.connect.options.auto_subscribe = options.auto_subscribe
        req.connect.options.dynacast = options.dynacast

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

        self._close_future: asyncio.Future[None] = asyncio.Future()
        self._ffi_handle = FfiHandle(cb.room.handle.id)
        self._info = cb.room
        self.connection_state = ConnectionState.CONN_CONNECTED

        lp_handle = FfiHandle(cb.local_participant.handle.id)
        self.local_participant = LocalParticipant(
            lp_handle, cb.local_participant)

        for pt in cb.participants:
            rp_handle = FfiHandle(pt.participant.handle.id)
            rp = self._create_remote_participant(rp_handle, pt.participant)

            # add the initial remote participant tracks
            for publication_info in pt.publications:
                pub_handle = FfiHandle(publication_info.handle.id)
                publication = RemoteTrackPublication(
                    pub_handle, publication_info)
                rp.tracks[publication.sid] = publication

    async def disconnect(self) -> None:
        if not self.isconnected():
            return

        req = proto_ffi.FfiRequest()
        req.disconnect.room_handle = self._ffi_handle.handle  # type: ignore

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
        await self._close_future

    def _on_room_event(self, event: proto_room.RoomEvent):
        if self._ffi_handle is None:
            return

        if event.room_handle != self._ffi_handle.handle:
            return

        which = event.WhichOneof('message')
        if which == 'participant_connected':
            rp_info = event.participant_connected.info
            ffi_handle = FfiHandle(rp_info.handle.id)
            rparticipant = self._create_remote_participant(
                ffi_handle, rp_info)
            self.emit('participant_connected', rparticipant)
        elif which == 'participant_disconnected':
            sid = event.participant_disconnected.participant_sid
            rparticipant = self.participants.pop(sid)
            self.emit('participant_disconnected', rparticipant)
        elif which == 'local_track_published':
            sid = event.local_track_published.track_sid
            # publication is created inside LocalParticipant.publish_track
            # (This event is called after that)
            lpublication = self.local_participant.tracks[sid]
            track = lpublication.track
            self.emit('local_track_published', lpublication, track)
        elif which == 'local_track_unpublished':
            sid = event.local_track_unpublished.publication_sid
            lpublication = self.local_participant.tracks[sid]
            self.emit('local_track_unpublished', lpublication)
        elif which == 'track_published':
            rparticipant = self.participants[event.track_published.participant_sid]
            ffi_handle = FfiHandle(event.track_published.publication.handle.id)
            rpublication = RemoteTrackPublication(ffi_handle,
                                                  event.track_published.publication)
            rparticipant.tracks[rpublication.sid] = rpublication
            self.emit('track_published', rpublication, rparticipant)
        elif which == 'track_unpublished':
            rparticipant = self.participants[event.track_unpublished.participant_sid]
            rpublication = rparticipant.tracks.pop(
                event.track_unpublished.publication_sid)
            self.emit('track_unpublished', rpublication, rparticipant)
        elif which == 'track_subscribed':
            track_info = event.track_subscribed.track
            rparticipant = self.participants[event.track_subscribed.participant_sid]
            rpublication = rparticipant.tracks[track_info.sid]
            ffi_handle = FfiHandle(track_info.handle.id)
            rpublication.subscribed = True
            if track_info.kind == TrackKind.KIND_VIDEO:
                remote_video_track = RemoteVideoTrack(ffi_handle, track_info)
                rpublication.track = remote_video_track
                self.emit('track_subscribed',
                          remote_video_track, rpublication, rparticipant)
            elif track_info.kind == TrackKind.KIND_AUDIO:
                remote_audio_track = RemoteAudioTrack(ffi_handle, track_info)
                rpublication.track = remote_audio_track
                self.emit('track_subscribed', remote_audio_track,
                          rpublication, rparticipant)
        elif which == 'track_unsubscribed':
            sid = event.track_unsubscribed.participant_sid
            rparticipant = self.participants[sid]
            rpublication = rparticipant.tracks[event.track_unsubscribed.track_sid]
            track = rpublication.track
            rpublication.track = None
            rpublication.subscribed = False
            self.emit('track_unsubscribed', track, rpublication, rparticipant)
        elif which == 'track_subscription_failed':
            sid = event.track_subscription_failed.participant_sid
            rparticipant = self.participants[sid]
            error = event.track_subscription_failed.error
            self.emit('track_subscription_failed', rparticipant,
                      event.track_subscription_failed.track_sid, error)
        elif which == 'track_muted':
            sid = event.track_muted.participant_sid
            participant = self._retrieve_participant(sid)
            publication = participant.tracks[event.track_muted.track_sid]
            publication._info.muted = True
            if publication.track:
                publication.track._info.muted = True

            self.emit('track_muted', participant, publication)
        elif which == 'track_unmuted':
            sid = event.track_unmuted.participant_sid
            participant = self._retrieve_participant(sid)
            publication = participant.tracks[event.track_unmuted.track_sid]
            publication._info.muted = False
            if publication.track:
                publication.track._info.muted = False

            self.emit('track_unmuted', participant, publication)
        elif which == 'active_speakers_changed':
            speakers: list[Participant] = []
            for sid in event.active_speakers_changed.participant_sids:
                speakers.append(self._retrieve_participant(sid))

            self.emit('active_speakers_changed', speakers)
        elif which == 'connection_quality_changed':
            sid = event.connection_quality_changed.participant_sid
            p = self._retrieve_participant(sid)

            self.emit('connection_quality_changed',
                      p, event.connection_quality_changed.quality)
        elif which == 'data_received':
            rparticipant = self.participants[event.data_received.participant_sid]
            buffer_info = event.data_received.data
            native_data = ctypes.cast(buffer_info.data_ptr,
                                      ctypes.POINTER(ctypes.c_byte
                                                     * buffer_info.data_len)).contents
            data = bytearray(native_data)
            FfiHandle(buffer_info.handle.id)
            self.emit('data_received', data,
                      event.data_received.kind, rparticipant)
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

    def _retrieve_participant(self, sid: str) -> Participant:
        """ Retrieve a participant by sid, returns the LocalParticipant
          if sid matches """
        if sid == self.local_participant.sid:
            return self.local_participant
        else:
            return self.participants[sid]

    def _create_remote_participant(self, handle: FfiHandle,
                                   info: proto_participant.ParticipantInfo) \
            -> RemoteParticipant:
        if info.sid in self.participants:
            raise Exception('participant already exists')

        participant = RemoteParticipant(handle, info)
        self.participants[participant.sid] = participant
        return participant
