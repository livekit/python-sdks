from ._proto import track_pb2 as proto_track
from ._ffi_client import FfiHandle
from typing import (Optional, TYPE_CHECKING)
from weakref import ref

if TYPE_CHECKING:
    from livekit import (Room, Participant)


class Track():
    def __init__(self, handle: Optional[FfiHandle], info: proto_track.TrackInfo, room: ref['Room'], participant: ref['Participant']):
        self._info = info
        self._ffi_handle = handle

        # TODO(theomonnom): Simplify that and use a FfiHandleId?
        # the weak references are needed because when we need to communicate with the
        # ffi_server which track we are referring to, we also need to provide the room
        # and the participant.
        self._room = room
        self._participant = participant

    @property
    def sid(self) -> str:
        return self._info.sid

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def kind(self) -> proto_track.TrackKind:
        return self._info.kind

    @property
    def stream_state(self) -> proto_track.StreamState:
        return self._info.stream_state

    @property
    def muted(self) -> bool:
        return self._info.muted

    def update_info(self, info: proto_track.TrackInfo):
        self._info = info


class LocalAudioTrack(Track):
    def __init__(self, ffi_handle: FfiHandle, info: proto_track.TrackInfo, room: ref['Room'], participant: ref['Participant']):
        super().__init__(ffi_handle, info, room, participant)


class LocalVideoTrack(Track):
    def __init__(self, ffi_handle: FfiHandle, info: proto_track.TrackInfo, room: ref['Room'], participant: ref['Participant']):
        super().__init__(ffi_handle, info, room, participant)


class RemoteAudioTrack(Track):
    def __init__(self, info: proto_track.TrackInfo, room: ref['Room'], participant: ref['Participant']):
        super().__init__(None, info, room, participant)


class RemoteVideoTrack(Track):
    def __init__(self, info: proto_track.TrackInfo, room: ref['Room'], participant: ref['Participant']):
        super().__init__(None, info, room, participant)
