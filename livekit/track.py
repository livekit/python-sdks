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

from typing import TYPE_CHECKING

from ._ffi_client import FfiHandle, ffi_client
from ._proto import ffi_pb2 as proto_ffi
from ._proto import track_pb2 as proto_track

if TYPE_CHECKING:
    from .audio_source import AudioSource
    from .video_source import VideoSource


class Track():
    def __init__(self, handle: FfiHandle, info: proto_track.TrackInfo):
        self._info = info
        self._ffi_handle = handle

    @property
    def sid(self) -> str:
        return self._info.sid

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def kind(self) -> proto_track.TrackKind.ValueType:
        return self._info.kind

    @property
    def stream_state(self) -> proto_track.StreamState.ValueType:
        return self._info.stream_state

    @property
    def muted(self) -> bool:
        return self._info.muted

    def update_info(self, info: proto_track.TrackInfo):
        self._info = info


class LocalAudioTrack(Track):
    def __init__(self, handle: FfiHandle, info: proto_track.TrackInfo):
        super().__init__(handle, info)

    @staticmethod
    def create_audio_track(name: str, source: 'AudioSource') -> 'LocalAudioTrack':
        req = proto_ffi.FfiRequest()
        req.create_audio_track.name = name
        req.create_audio_track.source_handle = source._ffi_handle.handle

        resp = ffi_client.request(req)
        track_info = resp.create_audio_track.track
        ffi_handle = FfiHandle(track_info.handle.id)
        return LocalAudioTrack(ffi_handle, track_info)


class LocalVideoTrack(Track):
    def __init__(self, handle: FfiHandle, info: proto_track.TrackInfo):
        super().__init__(handle, info)

    @staticmethod
    def create_video_track(name: str, source: 'VideoSource') -> 'LocalVideoTrack':
        req = proto_ffi.FfiRequest()
        req.create_video_track.name = name
        req.create_video_track.source_handle = source._ffi_handle.handle

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
