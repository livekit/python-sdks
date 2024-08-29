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
import google.protobuf.descriptor
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
from . import handle_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _AudioStreamType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _AudioStreamTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_AudioStreamType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    AUDIO_STREAM_NATIVE: _AudioStreamType.ValueType  # 0
    AUDIO_STREAM_HTML: _AudioStreamType.ValueType  # 1

class AudioStreamType(_AudioStreamType, metaclass=_AudioStreamTypeEnumTypeWrapper):
    """
    AudioStream
    """

AUDIO_STREAM_NATIVE: AudioStreamType.ValueType  # 0
AUDIO_STREAM_HTML: AudioStreamType.ValueType  # 1
global___AudioStreamType = AudioStreamType

class _AudioSourceType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _AudioSourceTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_AudioSourceType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    AUDIO_SOURCE_NATIVE: _AudioSourceType.ValueType  # 0

class AudioSourceType(_AudioSourceType, metaclass=_AudioSourceTypeEnumTypeWrapper): ...

AUDIO_SOURCE_NATIVE: AudioSourceType.ValueType  # 0
global___AudioSourceType = AudioSourceType

@typing_extensions.final
class NewAudioStreamRequest(google.protobuf.message.Message):
    """Create a new AudioStream
    AudioStream is used to receive audio frames from a track
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRACK_HANDLE_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    track_handle: builtins.int
    type: global___AudioStreamType.ValueType
    def __init__(
        self,
        *,
        track_handle: builtins.int = ...,
        type: global___AudioStreamType.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["track_handle", b"track_handle", "type", b"type"]) -> None: ...

global___NewAudioStreamRequest = NewAudioStreamRequest

@typing_extensions.final
class NewAudioStreamResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    STREAM_FIELD_NUMBER: builtins.int
    @property
    def stream(self) -> global___OwnedAudioStream: ...
    def __init__(
        self,
        *,
        stream: global___OwnedAudioStream | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["stream", b"stream"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["stream", b"stream"]) -> None: ...

global___NewAudioStreamResponse = NewAudioStreamResponse

@typing_extensions.final
class NewAudioSourceRequest(google.protobuf.message.Message):
    """Create a new AudioSource"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TYPE_FIELD_NUMBER: builtins.int
    OPTIONS_FIELD_NUMBER: builtins.int
    SAMPLE_RATE_FIELD_NUMBER: builtins.int
    NUM_CHANNELS_FIELD_NUMBER: builtins.int
    ENABLE_QUEUE_FIELD_NUMBER: builtins.int
    type: global___AudioSourceType.ValueType
    @property
    def options(self) -> global___AudioSourceOptions: ...
    sample_rate: builtins.int
    num_channels: builtins.int
    enable_queue: builtins.bool
    def __init__(
        self,
        *,
        type: global___AudioSourceType.ValueType = ...,
        options: global___AudioSourceOptions | None = ...,
        sample_rate: builtins.int = ...,
        num_channels: builtins.int = ...,
        enable_queue: builtins.bool | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_enable_queue", b"_enable_queue", "_options", b"_options", "enable_queue", b"enable_queue", "options", b"options"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_enable_queue", b"_enable_queue", "_options", b"_options", "enable_queue", b"enable_queue", "num_channels", b"num_channels", "options", b"options", "sample_rate", b"sample_rate", "type", b"type"]) -> None: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_enable_queue", b"_enable_queue"]) -> typing_extensions.Literal["enable_queue"] | None: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_options", b"_options"]) -> typing_extensions.Literal["options"] | None: ...

global___NewAudioSourceRequest = NewAudioSourceRequest

@typing_extensions.final
class NewAudioSourceResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SOURCE_FIELD_NUMBER: builtins.int
    @property
    def source(self) -> global___OwnedAudioSource: ...
    def __init__(
        self,
        *,
        source: global___OwnedAudioSource | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["source", b"source"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["source", b"source"]) -> None: ...

global___NewAudioSourceResponse = NewAudioSourceResponse

@typing_extensions.final
class CaptureAudioFrameRequest(google.protobuf.message.Message):
    """Push a frame to an AudioSource 
    The data provided must be available as long as the client receive the callback.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SOURCE_HANDLE_FIELD_NUMBER: builtins.int
    BUFFER_FIELD_NUMBER: builtins.int
    source_handle: builtins.int
    @property
    def buffer(self) -> global___AudioFrameBufferInfo: ...
    def __init__(
        self,
        *,
        source_handle: builtins.int = ...,
        buffer: global___AudioFrameBufferInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["buffer", b"buffer"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["buffer", b"buffer", "source_handle", b"source_handle"]) -> None: ...

global___CaptureAudioFrameRequest = CaptureAudioFrameRequest

@typing_extensions.final
class CaptureAudioFrameResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ASYNC_ID_FIELD_NUMBER: builtins.int
    async_id: builtins.int
    def __init__(
        self,
        *,
        async_id: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["async_id", b"async_id"]) -> None: ...

global___CaptureAudioFrameResponse = CaptureAudioFrameResponse

@typing_extensions.final
class CaptureAudioFrameCallback(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ASYNC_ID_FIELD_NUMBER: builtins.int
    ERROR_FIELD_NUMBER: builtins.int
    async_id: builtins.int
    error: builtins.str
    def __init__(
        self,
        *,
        async_id: builtins.int = ...,
        error: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_error", b"_error", "error", b"error"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_error", b"_error", "async_id", b"async_id", "error", b"error"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_error", b"_error"]) -> typing_extensions.Literal["error"] | None: ...

global___CaptureAudioFrameCallback = CaptureAudioFrameCallback

@typing_extensions.final
class NewAudioResamplerRequest(google.protobuf.message.Message):
    """Create a new AudioResampler"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___NewAudioResamplerRequest = NewAudioResamplerRequest

@typing_extensions.final
class NewAudioResamplerResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    RESAMPLER_FIELD_NUMBER: builtins.int
    @property
    def resampler(self) -> global___OwnedAudioResampler: ...
    def __init__(
        self,
        *,
        resampler: global___OwnedAudioResampler | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["resampler", b"resampler"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["resampler", b"resampler"]) -> None: ...

global___NewAudioResamplerResponse = NewAudioResamplerResponse

@typing_extensions.final
class RemixAndResampleRequest(google.protobuf.message.Message):
    """Remix and resample an audio frame"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    RESAMPLER_HANDLE_FIELD_NUMBER: builtins.int
    BUFFER_FIELD_NUMBER: builtins.int
    NUM_CHANNELS_FIELD_NUMBER: builtins.int
    SAMPLE_RATE_FIELD_NUMBER: builtins.int
    resampler_handle: builtins.int
    @property
    def buffer(self) -> global___AudioFrameBufferInfo: ...
    num_channels: builtins.int
    sample_rate: builtins.int
    def __init__(
        self,
        *,
        resampler_handle: builtins.int = ...,
        buffer: global___AudioFrameBufferInfo | None = ...,
        num_channels: builtins.int = ...,
        sample_rate: builtins.int = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["buffer", b"buffer"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["buffer", b"buffer", "num_channels", b"num_channels", "resampler_handle", b"resampler_handle", "sample_rate", b"sample_rate"]) -> None: ...

global___RemixAndResampleRequest = RemixAndResampleRequest

@typing_extensions.final
class RemixAndResampleResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    BUFFER_FIELD_NUMBER: builtins.int
    @property
    def buffer(self) -> global___OwnedAudioFrameBuffer: ...
    def __init__(
        self,
        *,
        buffer: global___OwnedAudioFrameBuffer | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["buffer", b"buffer"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["buffer", b"buffer"]) -> None: ...

global___RemixAndResampleResponse = RemixAndResampleResponse

@typing_extensions.final
class AudioFrameBufferInfo(google.protobuf.message.Message):
    """
    AudioFrame buffer
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DATA_PTR_FIELD_NUMBER: builtins.int
    NUM_CHANNELS_FIELD_NUMBER: builtins.int
    SAMPLE_RATE_FIELD_NUMBER: builtins.int
    SAMPLES_PER_CHANNEL_FIELD_NUMBER: builtins.int
    data_ptr: builtins.int
    """*const i16"""
    num_channels: builtins.int
    sample_rate: builtins.int
    samples_per_channel: builtins.int
    def __init__(
        self,
        *,
        data_ptr: builtins.int = ...,
        num_channels: builtins.int = ...,
        sample_rate: builtins.int = ...,
        samples_per_channel: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["data_ptr", b"data_ptr", "num_channels", b"num_channels", "sample_rate", b"sample_rate", "samples_per_channel", b"samples_per_channel"]) -> None: ...

global___AudioFrameBufferInfo = AudioFrameBufferInfo

@typing_extensions.final
class OwnedAudioFrameBuffer(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___AudioFrameBufferInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___AudioFrameBufferInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedAudioFrameBuffer = OwnedAudioFrameBuffer

@typing_extensions.final
class AudioStreamInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TYPE_FIELD_NUMBER: builtins.int
    type: global___AudioStreamType.ValueType
    def __init__(
        self,
        *,
        type: global___AudioStreamType.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["type", b"type"]) -> None: ...

global___AudioStreamInfo = AudioStreamInfo

@typing_extensions.final
class OwnedAudioStream(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___AudioStreamInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___AudioStreamInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedAudioStream = OwnedAudioStream

@typing_extensions.final
class AudioStreamEvent(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    STREAM_HANDLE_FIELD_NUMBER: builtins.int
    FRAME_RECEIVED_FIELD_NUMBER: builtins.int
    EOS_FIELD_NUMBER: builtins.int
    stream_handle: builtins.int
    @property
    def frame_received(self) -> global___AudioFrameReceived: ...
    @property
    def eos(self) -> global___AudioStreamEOS: ...
    def __init__(
        self,
        *,
        stream_handle: builtins.int = ...,
        frame_received: global___AudioFrameReceived | None = ...,
        eos: global___AudioStreamEOS | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["eos", b"eos", "frame_received", b"frame_received", "message", b"message"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["eos", b"eos", "frame_received", b"frame_received", "message", b"message", "stream_handle", b"stream_handle"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["message", b"message"]) -> typing_extensions.Literal["frame_received", "eos"] | None: ...

global___AudioStreamEvent = AudioStreamEvent

@typing_extensions.final
class AudioFrameReceived(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    FRAME_FIELD_NUMBER: builtins.int
    @property
    def frame(self) -> global___OwnedAudioFrameBuffer: ...
    def __init__(
        self,
        *,
        frame: global___OwnedAudioFrameBuffer | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["frame", b"frame"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["frame", b"frame"]) -> None: ...

global___AudioFrameReceived = AudioFrameReceived

@typing_extensions.final
class AudioStreamEOS(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___AudioStreamEOS = AudioStreamEOS

@typing_extensions.final
class AudioSourceOptions(google.protobuf.message.Message):
    """
    AudioSource
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ECHO_CANCELLATION_FIELD_NUMBER: builtins.int
    NOISE_SUPPRESSION_FIELD_NUMBER: builtins.int
    AUTO_GAIN_CONTROL_FIELD_NUMBER: builtins.int
    echo_cancellation: builtins.bool
    noise_suppression: builtins.bool
    auto_gain_control: builtins.bool
    def __init__(
        self,
        *,
        echo_cancellation: builtins.bool = ...,
        noise_suppression: builtins.bool = ...,
        auto_gain_control: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["auto_gain_control", b"auto_gain_control", "echo_cancellation", b"echo_cancellation", "noise_suppression", b"noise_suppression"]) -> None: ...

global___AudioSourceOptions = AudioSourceOptions

@typing_extensions.final
class AudioSourceInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TYPE_FIELD_NUMBER: builtins.int
    type: global___AudioSourceType.ValueType
    def __init__(
        self,
        *,
        type: global___AudioSourceType.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["type", b"type"]) -> None: ...

global___AudioSourceInfo = AudioSourceInfo

@typing_extensions.final
class OwnedAudioSource(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___AudioSourceInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___AudioSourceInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedAudioSource = OwnedAudioSource

@typing_extensions.final
class AudioResamplerInfo(google.protobuf.message.Message):
    """
    AudioResampler
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___AudioResamplerInfo = AudioResamplerInfo

@typing_extensions.final
class OwnedAudioResampler(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___AudioResamplerInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___AudioResamplerInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedAudioResampler = OwnedAudioResampler
