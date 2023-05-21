import handle_pb2 as _handle_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

AUDIO_SOURCE_NATIVE: AudioSourceType
AUDIO_STREAM_HTML: AudioStreamType
AUDIO_STREAM_NATIVE: AudioStreamType
DESCRIPTOR: _descriptor.FileDescriptor

class AllocAudioBufferRequest(_message.Message):
    __slots__ = ["num_channels", "sample_rate", "samples_per_channel"]
    NUM_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_PER_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    num_channels: int
    sample_rate: int
    samples_per_channel: int
    def __init__(self, sample_rate: _Optional[int] = ..., num_channels: _Optional[int] = ..., samples_per_channel: _Optional[int] = ...) -> None: ...

class AllocAudioBufferResponse(_message.Message):
    __slots__ = ["buffer"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: AudioFrameBufferInfo
    def __init__(self, buffer: _Optional[_Union[AudioFrameBufferInfo, _Mapping]] = ...) -> None: ...

class AudioFrameBufferInfo(_message.Message):
    __slots__ = ["data_ptr", "handle", "num_channels", "sample_rate", "samples_per_channel"]
    DATA_PTR_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    NUM_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_PER_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    data_ptr: int
    handle: _handle_pb2.FFIHandleId
    num_channels: int
    sample_rate: int
    samples_per_channel: int
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., data_ptr: _Optional[int] = ..., num_channels: _Optional[int] = ..., sample_rate: _Optional[int] = ..., samples_per_channel: _Optional[int] = ...) -> None: ...

class AudioFrameReceived(_message.Message):
    __slots__ = ["frame"]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    frame: AudioFrameBufferInfo
    def __init__(self, frame: _Optional[_Union[AudioFrameBufferInfo, _Mapping]] = ...) -> None: ...

class AudioSourceInfo(_message.Message):
    __slots__ = ["handle", "type"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FFIHandleId
    type: AudioSourceType
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., type: _Optional[_Union[AudioSourceType, str]] = ...) -> None: ...

class AudioStreamEvent(_message.Message):
    __slots__ = ["frame_received", "handle"]
    FRAME_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    frame_received: AudioFrameReceived
    handle: _handle_pb2.FFIHandleId
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., frame_received: _Optional[_Union[AudioFrameReceived, _Mapping]] = ...) -> None: ...

class AudioStreamInfo(_message.Message):
    __slots__ = ["handle", "track_sid", "type"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FFIHandleId
    track_sid: str
    type: AudioStreamType
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., type: _Optional[_Union[AudioStreamType, str]] = ..., track_sid: _Optional[str] = ...) -> None: ...

class CaptureAudioFrameRequest(_message.Message):
    __slots__ = ["buffer_handle", "source_handle"]
    BUFFER_HANDLE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    buffer_handle: _handle_pb2.FFIHandleId
    source_handle: _handle_pb2.FFIHandleId
    def __init__(self, source_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., buffer_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ...) -> None: ...

class CaptureAudioFrameResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class NewAudioResamplerRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class NewAudioResamplerResponse(_message.Message):
    __slots__ = ["handle"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FFIHandleId
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ...) -> None: ...

class NewAudioSourceRequest(_message.Message):
    __slots__ = ["type"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: AudioSourceType
    def __init__(self, type: _Optional[_Union[AudioSourceType, str]] = ...) -> None: ...

class NewAudioSourceResponse(_message.Message):
    __slots__ = ["source"]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    source: AudioSourceInfo
    def __init__(self, source: _Optional[_Union[AudioSourceInfo, _Mapping]] = ...) -> None: ...

class NewAudioStreamRequest(_message.Message):
    __slots__ = ["participant_sid", "room_handle", "track_sid", "type"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    ROOM_HANDLE_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    room_handle: _handle_pb2.FFIHandleId
    track_sid: str
    type: AudioStreamType
    def __init__(self, room_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ..., type: _Optional[_Union[AudioStreamType, str]] = ...) -> None: ...

class NewAudioStreamResponse(_message.Message):
    __slots__ = ["stream"]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    stream: AudioStreamInfo
    def __init__(self, stream: _Optional[_Union[AudioStreamInfo, _Mapping]] = ...) -> None: ...

class RemixAndResampleRequest(_message.Message):
    __slots__ = ["buffer_handle", "num_channels", "resampler_handle", "sample_rate"]
    BUFFER_HANDLE_FIELD_NUMBER: _ClassVar[int]
    NUM_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    RESAMPLER_HANDLE_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    buffer_handle: _handle_pb2.FFIHandleId
    num_channels: int
    resampler_handle: _handle_pb2.FFIHandleId
    sample_rate: int
    def __init__(self, resampler_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., buffer_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., num_channels: _Optional[int] = ..., sample_rate: _Optional[int] = ...) -> None: ...

class RemixAndResampleResponse(_message.Message):
    __slots__ = ["buffer"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: AudioFrameBufferInfo
    def __init__(self, buffer: _Optional[_Union[AudioFrameBufferInfo, _Mapping]] = ...) -> None: ...

class AudioStreamType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class AudioSourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
