from ._proto import track_pb2 as proto_track
from ._proto import ffi_pb2 as proto_ffi
from ._ffi_client import (FfiHandle, FfiClient)
from typing import (Optional, TYPE_CHECKING)

if TYPE_CHECKING:
    from livekit import (VideoSource, AudioSource)


class Track():
    def __init__(self, handle: Optional[FfiHandle], info: proto_track.TrackInfo):
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
    def __init__(self, ffi_handle: FfiHandle, info: proto_track.TrackInfo):
        super().__init__(ffi_handle, info)

    def create_audio_track(name: str, source: 'AudioSource') -> 'LocalAudioTrack':
        req = proto_ffi.FfiRequest()
        req.create_audio_track.name = name
        req.create_audio_track.source_handle.id = source._ffi_handle.handle

        ffi_client = FfiClient()
        resp = ffi_client.request(req)
        track_info = resp.create_audio_track.track
        ffi_handle = FfiHandle(track_info.handle.id)
        return LocalAudioTrack(ffi_handle, track_info)


class LocalVideoTrack(Track):
    def __init__(self, ffi_handle: FfiHandle, info: proto_track.TrackInfo):
        super().__init__(ffi_handle, info)

    def create_video_track(name: str, source: 'VideoSource') -> 'LocalVideoTrack':
        req = proto_ffi.FfiRequest()
        req.create_video_track.name = name
        req.create_video_track.source_handle.id = source._ffi_handle.handle

        ffi_client = FfiClient()
        resp = ffi_client.request(req)
        track_info = resp.create_video_track.track
        ffi_handle = FfiHandle(track_info.handle.id)
        return LocalVideoTrack(ffi_handle, track_info)


class RemoteAudioTrack(Track):
    def __init__(self, ffi_handle: FfiHandle, info: proto_track.TrackInfo):
        super().__init__(ffi_handle, info)


class RemoteVideoTrack(Track):
    def __init__(self, ffi_handle: FfiHandle, info: proto_track.TrackInfo):
        super().__init__(ffi_handle, info)
