import handle_pb2 as _handle_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AudioStreamType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    AUDIO_STREAM_NATIVE: _ClassVar[AudioStreamType]
    AUDIO_STREAM_HTML: _ClassVar[AudioStreamType]

class AudioSourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    AUDIO_SOURCE_NATIVE: _ClassVar[AudioSourceType]
AUDIO_STREAM_NATIVE: AudioStreamType
AUDIO_STREAM_HTML: AudioStreamType
AUDIO_SOURCE_NATIVE: AudioSourceType

class AllocAudioBufferRequest(_message.Message):
    __slots__ = ["sample_rate", "num_channels", "samples_per_channel"]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    NUM_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_PER_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    sample_rate: int
    num_channels: int
    samples_per_channel: int
    def __init__(self, sample_rate: _Optional[int] = ..., num_channels: _Optional[int] = ..., samples_per_channel: _Optional[int] = ...) -> None: ...

class AllocAudioBufferResponse(_message.Message):
    __slots__ = ["buffer"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: AudioFrameBufferInfo
    def __init__(self, buffer: _Optional[_Union[AudioFrameBufferInfo, _Mapping]] = ...) -> None: ...

class NewAudioStreamRequest(_message.Message):
    __slots__ = ["track_handle", "type"]
    TRACK_HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    track_handle: _handle_pb2.FfiHandleId
    type: AudioStreamType
    def __init__(self, track_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., type: _Optional[_Union[AudioStreamType, str]] = ...) -> None: ...

class NewAudioStreamResponse(_message.Message):
    __slots__ = ["stream"]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    stream: AudioStreamInfo
    def __init__(self, stream: _Optional[_Union[AudioStreamInfo, _Mapping]] = ...) -> None: ...

class NewAudioSourceRequest(_message.Message):
    __slots__ = ["type", "options"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    type: AudioSourceType
    options: AudioSourceOptions
    def __init__(self, type: _Optional[_Union[AudioSourceType, str]] = ..., options: _Optional[_Union[AudioSourceOptions, _Mapping]] = ...) -> None: ...

class NewAudioSourceResponse(_message.Message):
    __slots__ = ["source"]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    source: AudioSourceInfo
    def __init__(self, source: _Optional[_Union[AudioSourceInfo, _Mapping]] = ...) -> None: ...

class CaptureAudioFrameRequest(_message.Message):
    __slots__ = ["source_handle", "buffer_handle"]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    BUFFER_HANDLE_FIELD_NUMBER: _ClassVar[int]
    source_handle: _handle_pb2.FfiHandleId
    buffer_handle: _handle_pb2.FfiHandleId
    def __init__(self, source_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., buffer_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ...) -> None: ...

class CaptureAudioFrameResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class NewAudioResamplerRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class NewAudioResamplerResponse(_message.Message):
    __slots__ = ["handle"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ...) -> None: ...

class RemixAndResampleRequest(_message.Message):
    __slots__ = ["resampler_handle", "buffer_handle", "num_channels", "sample_rate"]
    RESAMPLER_HANDLE_FIELD_NUMBER: _ClassVar[int]
    BUFFER_HANDLE_FIELD_NUMBER: _ClassVar[int]
    NUM_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    resampler_handle: _handle_pb2.FfiHandleId
    buffer_handle: _handle_pb2.FfiHandleId
    num_channels: int
    sample_rate: int
    def __init__(self, resampler_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., buffer_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., num_channels: _Optional[int] = ..., sample_rate: _Optional[int] = ...) -> None: ...

class RemixAndResampleResponse(_message.Message):
    __slots__ = ["buffer"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: AudioFrameBufferInfo
    def __init__(self, buffer: _Optional[_Union[AudioFrameBufferInfo, _Mapping]] = ...) -> None: ...

class AudioFrameBufferInfo(_message.Message):
    __slots__ = ["handle", "data_ptr", "num_channels", "sample_rate", "samples_per_channel"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    DATA_PTR_FIELD_NUMBER: _ClassVar[int]
    NUM_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_PER_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    data_ptr: int
    num_channels: int
    sample_rate: int
    samples_per_channel: int
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., data_ptr: _Optional[int] = ..., num_channels: _Optional[int] = ..., sample_rate: _Optional[int] = ..., samples_per_channel: _Optional[int] = ...) -> None: ...

class AudioStreamInfo(_message.Message):
    __slots__ = ["handle", "type"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    type: AudioStreamType
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., type: _Optional[_Union[AudioStreamType, str]] = ...) -> None: ...

class AudioStreamEvent(_message.Message):
    __slots__ = ["handle", "frame_received"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    FRAME_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    frame_received: AudioFrameReceived
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., frame_received: _Optional[_Union[AudioFrameReceived, _Mapping]] = ...) -> None: ...

class AudioFrameReceived(_message.Message):
    __slots__ = ["frame"]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    frame: AudioFrameBufferInfo
    def __init__(self, frame: _Optional[_Union[AudioFrameBufferInfo, _Mapping]] = ...) -> None: ...

class AudioSourceOptions(_message.Message):
    __slots__ = ["echo_cancellation", "noise_suppression", "auto_gain_control"]
    ECHO_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    NOISE_SUPPRESSION_FIELD_NUMBER: _ClassVar[int]
    AUTO_GAIN_CONTROL_FIELD_NUMBER: _ClassVar[int]
    echo_cancellation: bool
    noise_suppression: bool
    auto_gain_control: bool
    def __init__(self, echo_cancellation: bool = ..., noise_suppression: bool = ..., auto_gain_control: bool = ...) -> None: ...

class AudioSourceInfo(_message.Message):
    __slots__ = ["handle", "type"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    type: AudioSourceType
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., type: _Optional[_Union[AudioSourceType, str]] = ...) -> None: ...
