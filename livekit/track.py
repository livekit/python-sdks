from ._proto import track_pb2 as proto_track
from typing import Optional
from ._ffi_client import FfiHandle


class Track():
    def __init__(self, info: proto_track.TrackInfo, handle: Optional[FfiHandle]):
        self._info = info
        self._ffi_handle = handle

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
    def __init__(self, info: proto_track.TrackInfo, handle: FfiHandle):
        super().__init__(info, handle)


class LocalVideoTrack(Track):
    def __init__(self, info: proto_track.TrackInfo, handle: FfiHandle):
        super().__init__(info, handle)


class RemoteAudioTrack(Track):
    def __init__(self, info: proto_track.TrackInfo):
        super().__init__(info, None)


class RemoteVideoTrack(Track):
    def __init__(self, info: proto_track.TrackInfo):
        super().__init__(info, None)
