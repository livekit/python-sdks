from ._proto import participant_pb2 as proto_participant
from ._proto import ffi_pb2 as proto_ffi
from ._proto import room_pb2 as proto_room
from .track_publication import TrackPublication
from .track import (Track, LocalAudioTrack, LocalVideoTrack)
from ._ffi_client import (FfiClient, FfiHandle)
from typing import TYPE_CHECKING
import weakref
import asyncio
from livekit import TrackPublishOptions

if TYPE_CHECKING:
    from livekit import (Room, Participant)


class PublishTrackError(Exception):
    def __init__(self, message: str):
        self.message = message


class Participant():
    def __init__(self, info: proto_participant.ParticipantInfo):
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
    def __init__(self, info: proto_participant.ParticipantInfo, room: weakref.ref['Room']):
        super().__init__(info)
        self._room = room

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

        ffi_client = FfiClient()
        resp = ffi_client.request(req)
        future = asyncio.Future()

        @ffi_client.on('publish_track')
        def on_publish_callback(cb: proto_room.PublishTrackCallback):
            if cb.async_id == resp.publish_track.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'publish_track', on_publish_callback)

        resp: proto_room.PublishTrackCallback = await future

        if resp.error:
            raise PublishTrackError(resp.error)

        track_publication = TrackPublication(resp.publication)
        track_publication.track = track
        self.tracks[track_publication.sid] = track_publication
        # TODO: Update track info
        return track_publication


class RemoteParticipant(Participant):
    def __init__(self, info: proto_participant.ParticipantInfo):
        super().__init__(info)
