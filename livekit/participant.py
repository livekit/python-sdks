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
import weakref
from typing import TYPE_CHECKING, List, Optional, Union
from weakref import ref

from ._proto.room_pb2 import DataPacketKind, TrackPublishOptions

from ._ffi_client import ffi_client
from ._proto import ffi_pb2 as proto_ffi
from ._proto import participant_pb2 as proto_participant
from ._proto import room_pb2 as proto_room
from .track import LocalAudioTrack, LocalVideoTrack, Track
from .track_publication import (
    LocalTrackPublication,
    RemoteTrackPublication,
    TrackPublication,
)

if TYPE_CHECKING:
    from .room import Room


class PublishTrackError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class PublishDataError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class Participant():
    def __init__(self, info: proto_participant.ParticipantInfo) -> None:
        self._info = info
        self.tracks: dict[str, TrackPublication] = {}

    @property
    def sid(self) -> str:
        return self._info.sid

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def identity(self) -> str:
        return self._info.identity

    @property
    def metadata(self) -> str:
        return self._info.metadata


class LocalParticipant(Participant):
    def __init__(self, info: proto_participant.ParticipantInfo, room: weakref.ref['Room']) -> None:
        super().__init__(info)
        self._room = room
        self.tracks: dict[str, LocalTrackPublication] = {}

    async def publish_data(self,
                           payload: Union[bytes, str],
                           kind: DataPacketKind.ValueType = DataPacketKind.KIND_RELIABLE,
                           destination_sids: Optional[Union[List[str], List['RemoteParticipant']]] = None) -> None:

        room = self._room()
        if room is None:
            raise Exception('room is closed')

        if isinstance(payload, str):
            payload = payload.encode('utf-8')

        data_len = len(payload)

        cdata = (ctypes.c_byte * data_len)(*payload)

        req = proto_ffi.FfiRequest()
        req.publish_data.room_handle.id = room._ffi_handle.handle
        req.publish_data.data_ptr = ctypes.addressof(cdata)
        req.publish_data.data_size = data_len
        req.publish_data.kind = kind

        if destination_sids is not None:
            sids = []
            for p in destination_sids:
                if isinstance(p, RemoteParticipant):
                    sids.append(p.sid)
                else:
                    sids.append(p)

            req.publish_data.destination_sids.extend(sids)

        resp = ffi_client.request(req)
        future: asyncio.Future[proto_room.PublishDataCallback] = asyncio.Future(
        )

        @ffi_client.on('publish_data')
        def on_publish_callback(cb: proto_room.PublishDataCallback):
            if cb.async_id == resp.publish_data.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'publish_data', on_publish_callback)

        cb = await future
        if cb.error:
            raise PublishDataError(cb.error)

    async def publish_track(self, track: Track, options: TrackPublishOptions) -> TrackPublication:
        if not isinstance(track, LocalAudioTrack) and not isinstance(track, LocalVideoTrack):
            raise Exception('cannot publish a remote track')

        room = self._room()
        if room is None:
            raise Exception('room is closed')

        req = proto_ffi.FfiRequest()
        req.publish_track.track_handle.id = track._ffi_handle.handle
        req.publish_track.room_handle.id = room._ffi_handle.handle
        req.publish_track.options.CopyFrom(options)

        resp = ffi_client.request(req)

        future: asyncio.Future[proto_room.PublishTrackCallback] = asyncio.Future(
        )

        @ffi_client.on('publish_track')
        def on_publish_callback(cb: proto_room.PublishTrackCallback):
            if cb.async_id == resp.publish_track.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'publish_track', on_publish_callback)

        cb = await future

        if cb.error:
            raise PublishTrackError(cb.error)

        track_publication = LocalTrackPublication(cb.publication, ref(self))
        track_publication.track = track
        self.tracks[track_publication.sid] = track_publication
        # TODO: Update track info
        return track_publication


class RemoteParticipant(Participant):
    def __init__(self, info: proto_participant.ParticipantInfo) -> None:
        super().__init__(info)
        self.tracks: dict[str, RemoteTrackPublication] = {}
