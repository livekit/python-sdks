import handle_pb2 as _handle_pb2
import video_frame_pb2 as _video_frame_pb2
import audio_frame_pb2 as _audio_frame_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
KIND_AUDIO: TrackKind
KIND_UNKNOWN: TrackKind
KIND_VIDEO: TrackKind
SOURCE_CAMERA: TrackSource
SOURCE_MICROPHONE: TrackSource
SOURCE_SCREENSHARE: TrackSource
SOURCE_SCREENSHARE_AUDIO: TrackSource
SOURCE_UNKNOWN: TrackSource
STATE_ACTIVE: StreamState
STATE_PAUSED: StreamState
STATE_UNKNOWN: StreamState

class AudioCaptureOptions(_message.Message):
    __slots__ = ["auto_gain_control", "echo_cancellation", "noise_suppression"]
    AUTO_GAIN_CONTROL_FIELD_NUMBER: _ClassVar[int]
    ECHO_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    NOISE_SUPPRESSION_FIELD_NUMBER: _ClassVar[int]
    auto_gain_control: bool
    echo_cancellation: bool
    noise_suppression: bool
    def __init__(self, echo_cancellation: bool = ..., noise_suppression: bool = ..., auto_gain_control: bool = ...) -> None: ...

class CreateAudioTrackRequest(_message.Message):
    __slots__ = ["name", "options", "source_handle"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    options: AudioCaptureOptions
    source_handle: _handle_pb2.FFIHandleId
    def __init__(self, name: _Optional[str] = ..., options: _Optional[_Union[AudioCaptureOptions, _Mapping]] = ..., source_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ...) -> None: ...

class CreateAudioTrackResponse(_message.Message):
    __slots__ = ["track"]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    track: TrackInfo
    def __init__(self, track: _Optional[_Union[TrackInfo, _Mapping]] = ...) -> None: ...

class CreateVideoTrackRequest(_message.Message):
    __slots__ = ["name", "options", "source_handle"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    options: VideoCaptureOptions
    source_handle: _handle_pb2.FFIHandleId
    def __init__(self, name: _Optional[str] = ..., options: _Optional[_Union[VideoCaptureOptions, _Mapping]] = ..., source_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ...) -> None: ...

class CreateVideoTrackResponse(_message.Message):
    __slots__ = ["track"]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    track: TrackInfo
    def __init__(self, track: _Optional[_Union[TrackInfo, _Mapping]] = ...) -> None: ...

class TrackEvent(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class TrackInfo(_message.Message):
    __slots__ = ["kind", "muted", "name", "opt_handle", "remote", "sid", "stream_state"]
    KIND_FIELD_NUMBER: _ClassVar[int]
    MUTED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPT_HANDLE_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    SID_FIELD_NUMBER: _ClassVar[int]
    STREAM_STATE_FIELD_NUMBER: _ClassVar[int]
    kind: TrackKind
    muted: bool
    name: str
    opt_handle: _handle_pb2.FFIHandleId
    remote: bool
    sid: str
    stream_state: StreamState
    def __init__(self, opt_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., sid: _Optional[str] = ..., name: _Optional[str] = ..., kind: _Optional[_Union[TrackKind, str]] = ..., stream_state: _Optional[_Union[StreamState, str]] = ..., muted: bool = ..., remote: bool = ...) -> None: ...

class TrackPublicationInfo(_message.Message):
    __slots__ = ["height", "kind", "mime_type", "muted", "name", "remote", "sid", "simulcasted", "source", "width"]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    MUTED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    SID_FIELD_NUMBER: _ClassVar[int]
    SIMULCASTED_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    height: int
    kind: TrackKind
    mime_type: str
    muted: bool
    name: str
    remote: bool
    sid: str
    simulcasted: bool
    source: TrackSource
    width: int
    def __init__(self, sid: _Optional[str] = ..., name: _Optional[str] = ..., kind: _Optional[_Union[TrackKind, str]] = ..., source: _Optional[_Union[TrackSource, str]] = ..., simulcasted: bool = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., mime_type: _Optional[str] = ..., muted: bool = ..., remote: bool = ...) -> None: ...

class VideoCaptureOptions(_message.Message):
    __slots__ = ["resolution"]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    resolution: _video_frame_pb2.VideoResolution
    def __init__(self, resolution: _Optional[_Union[_video_frame_pb2.VideoResolution, _Mapping]] = ...) -> None: ...

class TrackKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class TrackSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class StreamState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
