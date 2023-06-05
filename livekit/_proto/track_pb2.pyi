import handle_pb2 as _handle_pb2
import video_frame_pb2 as _video_frame_pb2
import audio_frame_pb2 as _audio_frame_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TrackKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    KIND_UNKNOWN: _ClassVar[TrackKind]
    KIND_AUDIO: _ClassVar[TrackKind]
    KIND_VIDEO: _ClassVar[TrackKind]

class TrackSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SOURCE_UNKNOWN: _ClassVar[TrackSource]
    SOURCE_CAMERA: _ClassVar[TrackSource]
    SOURCE_MICROPHONE: _ClassVar[TrackSource]
    SOURCE_SCREENSHARE: _ClassVar[TrackSource]
    SOURCE_SCREENSHARE_AUDIO: _ClassVar[TrackSource]

class StreamState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    STATE_UNKNOWN: _ClassVar[StreamState]
    STATE_ACTIVE: _ClassVar[StreamState]
    STATE_PAUSED: _ClassVar[StreamState]
KIND_UNKNOWN: TrackKind
KIND_AUDIO: TrackKind
KIND_VIDEO: TrackKind
SOURCE_UNKNOWN: TrackSource
SOURCE_CAMERA: TrackSource
SOURCE_MICROPHONE: TrackSource
SOURCE_SCREENSHARE: TrackSource
SOURCE_SCREENSHARE_AUDIO: TrackSource
STATE_UNKNOWN: StreamState
STATE_ACTIVE: StreamState
STATE_PAUSED: StreamState

class VideoCaptureOptions(_message.Message):
    __slots__ = ["resolution"]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    resolution: _video_frame_pb2.VideoResolution
    def __init__(self, resolution: _Optional[_Union[_video_frame_pb2.VideoResolution, _Mapping]] = ...) -> None: ...

class AudioCaptureOptions(_message.Message):
    __slots__ = ["echo_cancellation", "noise_suppression", "auto_gain_control"]
    ECHO_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    NOISE_SUPPRESSION_FIELD_NUMBER: _ClassVar[int]
    AUTO_GAIN_CONTROL_FIELD_NUMBER: _ClassVar[int]
    echo_cancellation: bool
    noise_suppression: bool
    auto_gain_control: bool
    def __init__(self, echo_cancellation: bool = ..., noise_suppression: bool = ..., auto_gain_control: bool = ...) -> None: ...

class CreateVideoTrackRequest(_message.Message):
    __slots__ = ["name", "options", "source_handle"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    options: VideoCaptureOptions
    source_handle: _handle_pb2.FfiHandleId
    def __init__(self, name: _Optional[str] = ..., options: _Optional[_Union[VideoCaptureOptions, _Mapping]] = ..., source_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ...) -> None: ...

class CreateVideoTrackResponse(_message.Message):
    __slots__ = ["track"]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    track: TrackInfo
    def __init__(self, track: _Optional[_Union[TrackInfo, _Mapping]] = ...) -> None: ...

class CreateAudioTrackRequest(_message.Message):
    __slots__ = ["name", "options", "source_handle"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    options: AudioCaptureOptions
    source_handle: _handle_pb2.FfiHandleId
    def __init__(self, name: _Optional[str] = ..., options: _Optional[_Union[AudioCaptureOptions, _Mapping]] = ..., source_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ...) -> None: ...

class CreateAudioTrackResponse(_message.Message):
    __slots__ = ["track"]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    track: TrackInfo
    def __init__(self, track: _Optional[_Union[TrackInfo, _Mapping]] = ...) -> None: ...

class TrackEvent(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class TrackPublicationInfo(_message.Message):
    __slots__ = ["sid", "name", "kind", "source", "simulcasted", "width", "height", "mime_type", "muted", "remote"]
    SID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SIMULCASTED_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    MUTED_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    sid: str
    name: str
    kind: TrackKind
    source: TrackSource
    simulcasted: bool
    width: int
    height: int
    mime_type: str
    muted: bool
    remote: bool
    def __init__(self, sid: _Optional[str] = ..., name: _Optional[str] = ..., kind: _Optional[_Union[TrackKind, str]] = ..., source: _Optional[_Union[TrackSource, str]] = ..., simulcasted: bool = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., mime_type: _Optional[str] = ..., muted: bool = ..., remote: bool = ...) -> None: ...

class TrackInfo(_message.Message):
    __slots__ = ["opt_handle", "sid", "name", "kind", "stream_state", "muted", "remote"]
    OPT_HANDLE_FIELD_NUMBER: _ClassVar[int]
    SID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    STREAM_STATE_FIELD_NUMBER: _ClassVar[int]
    MUTED_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    opt_handle: _handle_pb2.FfiHandleId
    sid: str
    name: str
    kind: TrackKind
    stream_state: StreamState
    muted: bool
    remote: bool
    def __init__(self, opt_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., sid: _Optional[str] = ..., name: _Optional[str] = ..., kind: _Optional[_Union[TrackKind, str]] = ..., stream_state: _Optional[_Union[StreamState, str]] = ..., muted: bool = ..., remote: bool = ...) -> None: ...
