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

import weakref
from typing import TYPE_CHECKING, Optional

from livekit._proto import track_pb2 as proto_track

from ._ffi_client import ffi_client
from ._proto import ffi_pb2 as proto_ffi
from .track import Track

if TYPE_CHECKING:
    from .participant import LocalParticipant, RemoteParticipant


class TrackPublication():
    def __init__(self, info: proto_track.TrackPublicationInfo):
        self._info = info
        self.track: Optional[Track] = None

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
    def source(self) -> proto_track.TrackSource.ValueType:
        return self._info.source

    @property
    def simulcasted(self) -> bool:
        return self._info.simulcasted

    @property
    def width(self) -> int:
        return self._info.width

    @property
    def height(self) -> int:
        return self._info.height

    @property
    def mime_type(self) -> str:
        return self._info.mime_type

    @property
    def muted(self) -> bool:
        return self._info.muted


class LocalTrackPublication(TrackPublication):
    def __init__(self, info: proto_track.TrackPublicationInfo, participant: weakref.ref['LocalParticipant']):
        super().__init__(info)
        self.participant = participant


class RemoteTrackPublication(TrackPublication):
    def __init__(self, info: proto_track.TrackPublicationInfo, participant: weakref.ref['RemoteParticipant']):
        super().__init__(info)
        self.subscribed = False
        self.participant = participant

    def set_subscribed(self, subscribed: bool):
        participant = self.participant()
        if participant is None:
            return

        req = proto_ffi.FfiRequest()
        req.set_subscribed.track_sid = self.sid
        req.set_subscribed.participant_sid = participant.sid
        req.set_subscribed.subscribe = subscribed

        ffi_client.request(req)
