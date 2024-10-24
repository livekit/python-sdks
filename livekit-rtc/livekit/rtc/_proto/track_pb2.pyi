"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
Copyright 2023 LiveKit, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import builtins
import collections.abc
from . import e2ee_pb2
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
from . import handle_pb2
from . import stats_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _TrackKind:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _TrackKindEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_TrackKind.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    KIND_UNKNOWN: _TrackKind.ValueType  # 0
    KIND_AUDIO: _TrackKind.ValueType  # 1
    KIND_VIDEO: _TrackKind.ValueType  # 2

class TrackKind(_TrackKind, metaclass=_TrackKindEnumTypeWrapper): ...

KIND_UNKNOWN: TrackKind.ValueType  # 0
KIND_AUDIO: TrackKind.ValueType  # 1
KIND_VIDEO: TrackKind.ValueType  # 2
global___TrackKind = TrackKind

class _TrackSource:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _TrackSourceEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_TrackSource.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    SOURCE_UNKNOWN: _TrackSource.ValueType  # 0
    SOURCE_CAMERA: _TrackSource.ValueType  # 1
    SOURCE_MICROPHONE: _TrackSource.ValueType  # 2
    SOURCE_SCREENSHARE: _TrackSource.ValueType  # 3
    SOURCE_SCREENSHARE_AUDIO: _TrackSource.ValueType  # 4

class TrackSource(_TrackSource, metaclass=_TrackSourceEnumTypeWrapper): ...

SOURCE_UNKNOWN: TrackSource.ValueType  # 0
SOURCE_CAMERA: TrackSource.ValueType  # 1
SOURCE_MICROPHONE: TrackSource.ValueType  # 2
SOURCE_SCREENSHARE: TrackSource.ValueType  # 3
SOURCE_SCREENSHARE_AUDIO: TrackSource.ValueType  # 4
global___TrackSource = TrackSource

class _StreamState:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _StreamStateEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_StreamState.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    STATE_UNKNOWN: _StreamState.ValueType  # 0
    STATE_ACTIVE: _StreamState.ValueType  # 1
    STATE_PAUSED: _StreamState.ValueType  # 2

class StreamState(_StreamState, metaclass=_StreamStateEnumTypeWrapper): ...

STATE_UNKNOWN: StreamState.ValueType  # 0
STATE_ACTIVE: StreamState.ValueType  # 1
STATE_PAUSED: StreamState.ValueType  # 2
global___StreamState = StreamState

@typing.final
class CreateVideoTrackRequest(google.protobuf.message.Message):
    """Create a new VideoTrack from a VideoSource"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    NAME_FIELD_NUMBER: builtins.int
    SOURCE_HANDLE_FIELD_NUMBER: builtins.int
    name: builtins.str
    source_handle: builtins.int
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        source_handle: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["name", b"name", "source_handle", b"source_handle"]) -> None: ...

global___CreateVideoTrackRequest = CreateVideoTrackRequest

@typing.final
class CreateVideoTrackResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRACK_FIELD_NUMBER: builtins.int
    @property
    def track(self) -> global___OwnedTrack: ...
    def __init__(
        self,
        *,
        track: global___OwnedTrack | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["track", b"track"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["track", b"track"]) -> None: ...

global___CreateVideoTrackResponse = CreateVideoTrackResponse

@typing.final
class CreateAudioTrackRequest(google.protobuf.message.Message):
    """Create a new AudioTrack from a AudioSource"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    NAME_FIELD_NUMBER: builtins.int
    SOURCE_HANDLE_FIELD_NUMBER: builtins.int
    name: builtins.str
    source_handle: builtins.int
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        source_handle: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["name", b"name", "source_handle", b"source_handle"]) -> None: ...

global___CreateAudioTrackRequest = CreateAudioTrackRequest

@typing.final
class CreateAudioTrackResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRACK_FIELD_NUMBER: builtins.int
    @property
    def track(self) -> global___OwnedTrack: ...
    def __init__(
        self,
        *,
        track: global___OwnedTrack | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["track", b"track"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["track", b"track"]) -> None: ...

global___CreateAudioTrackResponse = CreateAudioTrackResponse

@typing.final
class GetStatsRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRACK_HANDLE_FIELD_NUMBER: builtins.int
    track_handle: builtins.int
    def __init__(
        self,
        *,
        track_handle: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["track_handle", b"track_handle"]) -> None: ...

global___GetStatsRequest = GetStatsRequest

@typing.final
class GetStatsResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ASYNC_ID_FIELD_NUMBER: builtins.int
    async_id: builtins.int
    def __init__(
        self,
        *,
        async_id: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["async_id", b"async_id"]) -> None: ...

global___GetStatsResponse = GetStatsResponse

@typing.final
class GetStatsCallback(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ASYNC_ID_FIELD_NUMBER: builtins.int
    ERROR_FIELD_NUMBER: builtins.int
    STATS_FIELD_NUMBER: builtins.int
    async_id: builtins.int
    error: builtins.str
    @property
    def stats(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[stats_pb2.RtcStats]: ...
    def __init__(
        self,
        *,
        async_id: builtins.int = ...,
        error: builtins.str | None = ...,
        stats: collections.abc.Iterable[stats_pb2.RtcStats] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["_error", b"_error", "error", b"error"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["_error", b"_error", "async_id", b"async_id", "error", b"error", "stats", b"stats"]) -> None: ...
    def WhichOneof(self, oneof_group: typing.Literal["_error", b"_error"]) -> typing.Literal["error"] | None: ...

global___GetStatsCallback = GetStatsCallback

@typing.final
class TrackEvent(google.protobuf.message.Message):
    """
    Track
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___TrackEvent = TrackEvent

@typing.final
class TrackPublicationInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SID_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    KIND_FIELD_NUMBER: builtins.int
    SOURCE_FIELD_NUMBER: builtins.int
    SIMULCASTED_FIELD_NUMBER: builtins.int
    WIDTH_FIELD_NUMBER: builtins.int
    HEIGHT_FIELD_NUMBER: builtins.int
    MIME_TYPE_FIELD_NUMBER: builtins.int
    MUTED_FIELD_NUMBER: builtins.int
    REMOTE_FIELD_NUMBER: builtins.int
    ENCRYPTION_TYPE_FIELD_NUMBER: builtins.int
    sid: builtins.str
    name: builtins.str
    kind: global___TrackKind.ValueType
    source: global___TrackSource.ValueType
    simulcasted: builtins.bool
    width: builtins.int
    height: builtins.int
    mime_type: builtins.str
    muted: builtins.bool
    remote: builtins.bool
    encryption_type: e2ee_pb2.EncryptionType.ValueType
    def __init__(
        self,
        *,
        sid: builtins.str = ...,
        name: builtins.str = ...,
        kind: global___TrackKind.ValueType = ...,
        source: global___TrackSource.ValueType = ...,
        simulcasted: builtins.bool = ...,
        width: builtins.int = ...,
        height: builtins.int = ...,
        mime_type: builtins.str = ...,
        muted: builtins.bool = ...,
        remote: builtins.bool = ...,
        encryption_type: e2ee_pb2.EncryptionType.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["encryption_type", b"encryption_type", "height", b"height", "kind", b"kind", "mime_type", b"mime_type", "muted", b"muted", "name", b"name", "remote", b"remote", "sid", b"sid", "simulcasted", b"simulcasted", "source", b"source", "width", b"width"]) -> None: ...

global___TrackPublicationInfo = TrackPublicationInfo

@typing.final
class OwnedTrackPublication(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___TrackPublicationInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___TrackPublicationInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedTrackPublication = OwnedTrackPublication

@typing.final
class TrackInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SID_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    KIND_FIELD_NUMBER: builtins.int
    STREAM_STATE_FIELD_NUMBER: builtins.int
    MUTED_FIELD_NUMBER: builtins.int
    REMOTE_FIELD_NUMBER: builtins.int
    sid: builtins.str
    name: builtins.str
    kind: global___TrackKind.ValueType
    stream_state: global___StreamState.ValueType
    muted: builtins.bool
    remote: builtins.bool
    def __init__(
        self,
        *,
        sid: builtins.str = ...,
        name: builtins.str = ...,
        kind: global___TrackKind.ValueType = ...,
        stream_state: global___StreamState.ValueType = ...,
        muted: builtins.bool = ...,
        remote: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["kind", b"kind", "muted", b"muted", "name", b"name", "remote", b"remote", "sid", b"sid", "stream_state", b"stream_state"]) -> None: ...

global___TrackInfo = TrackInfo

@typing.final
class OwnedTrack(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___TrackInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___TrackInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedTrack = OwnedTrack

@typing.final
class LocalTrackMuteRequest(google.protobuf.message.Message):
    """Mute/UnMute a track"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRACK_HANDLE_FIELD_NUMBER: builtins.int
    MUTE_FIELD_NUMBER: builtins.int
    track_handle: builtins.int
    mute: builtins.bool
    def __init__(
        self,
        *,
        track_handle: builtins.int = ...,
        mute: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["mute", b"mute", "track_handle", b"track_handle"]) -> None: ...

global___LocalTrackMuteRequest = LocalTrackMuteRequest

@typing.final
class LocalTrackMuteResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MUTED_FIELD_NUMBER: builtins.int
    muted: builtins.bool
    def __init__(
        self,
        *,
        muted: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["muted", b"muted"]) -> None: ...

global___LocalTrackMuteResponse = LocalTrackMuteResponse

@typing.final
class EnableRemoteTrackRequest(google.protobuf.message.Message):
    """Enable/Disable a remote track"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRACK_HANDLE_FIELD_NUMBER: builtins.int
    ENABLED_FIELD_NUMBER: builtins.int
    track_handle: builtins.int
    enabled: builtins.bool
    def __init__(
        self,
        *,
        track_handle: builtins.int = ...,
        enabled: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["enabled", b"enabled", "track_handle", b"track_handle"]) -> None: ...

global___EnableRemoteTrackRequest = EnableRemoteTrackRequest

@typing.final
class EnableRemoteTrackResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ENABLED_FIELD_NUMBER: builtins.int
    enabled: builtins.bool
    def __init__(
        self,
        *,
        enabled: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["enabled", b"enabled"]) -> None: ...

global___EnableRemoteTrackResponse = EnableRemoteTrackResponse
