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
import google.protobuf.descriptor
import google.protobuf.internal.containers
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

class _VideoCodec:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _VideoCodecEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_VideoCodec.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    VP8: _VideoCodec.ValueType  # 0
    H264: _VideoCodec.ValueType  # 1
    AV1: _VideoCodec.ValueType  # 2
    VP9: _VideoCodec.ValueType  # 3

class VideoCodec(_VideoCodec, metaclass=_VideoCodecEnumTypeWrapper): ...

VP8: VideoCodec.ValueType  # 0
H264: VideoCodec.ValueType  # 1
AV1: VideoCodec.ValueType  # 2
VP9: VideoCodec.ValueType  # 3
global___VideoCodec = VideoCodec

class _VideoRotation:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _VideoRotationEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_VideoRotation.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    VIDEO_ROTATION_0: _VideoRotation.ValueType  # 0
    VIDEO_ROTATION_90: _VideoRotation.ValueType  # 1
    VIDEO_ROTATION_180: _VideoRotation.ValueType  # 2
    VIDEO_ROTATION_270: _VideoRotation.ValueType  # 3

class VideoRotation(_VideoRotation, metaclass=_VideoRotationEnumTypeWrapper): ...

VIDEO_ROTATION_0: VideoRotation.ValueType  # 0
VIDEO_ROTATION_90: VideoRotation.ValueType  # 1
VIDEO_ROTATION_180: VideoRotation.ValueType  # 2
VIDEO_ROTATION_270: VideoRotation.ValueType  # 3
global___VideoRotation = VideoRotation

class _VideoBufferType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _VideoBufferTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_VideoBufferType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    RGBA: _VideoBufferType.ValueType  # 0
    ABGR: _VideoBufferType.ValueType  # 1
    ARGB: _VideoBufferType.ValueType  # 2
    BGRA: _VideoBufferType.ValueType  # 3
    RGB24: _VideoBufferType.ValueType  # 4
    I420: _VideoBufferType.ValueType  # 5
    I420A: _VideoBufferType.ValueType  # 6
    I422: _VideoBufferType.ValueType  # 7
    I444: _VideoBufferType.ValueType  # 8
    I010: _VideoBufferType.ValueType  # 9
    NV12: _VideoBufferType.ValueType  # 10

class VideoBufferType(_VideoBufferType, metaclass=_VideoBufferTypeEnumTypeWrapper): ...

RGBA: VideoBufferType.ValueType  # 0
ABGR: VideoBufferType.ValueType  # 1
ARGB: VideoBufferType.ValueType  # 2
BGRA: VideoBufferType.ValueType  # 3
RGB24: VideoBufferType.ValueType  # 4
I420: VideoBufferType.ValueType  # 5
I420A: VideoBufferType.ValueType  # 6
I422: VideoBufferType.ValueType  # 7
I444: VideoBufferType.ValueType  # 8
I010: VideoBufferType.ValueType  # 9
NV12: VideoBufferType.ValueType  # 10
global___VideoBufferType = VideoBufferType

class _VideoStreamType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _VideoStreamTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_VideoStreamType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    VIDEO_STREAM_NATIVE: _VideoStreamType.ValueType  # 0
    VIDEO_STREAM_WEBGL: _VideoStreamType.ValueType  # 1
    VIDEO_STREAM_HTML: _VideoStreamType.ValueType  # 2

class VideoStreamType(_VideoStreamType, metaclass=_VideoStreamTypeEnumTypeWrapper):
    """
    VideoStream
    """

VIDEO_STREAM_NATIVE: VideoStreamType.ValueType  # 0
VIDEO_STREAM_WEBGL: VideoStreamType.ValueType  # 1
VIDEO_STREAM_HTML: VideoStreamType.ValueType  # 2
global___VideoStreamType = VideoStreamType

class _VideoSourceType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _VideoSourceTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_VideoSourceType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    VIDEO_SOURCE_NATIVE: _VideoSourceType.ValueType  # 0

class VideoSourceType(_VideoSourceType, metaclass=_VideoSourceTypeEnumTypeWrapper): ...

VIDEO_SOURCE_NATIVE: VideoSourceType.ValueType  # 0
global___VideoSourceType = VideoSourceType

@typing_extensions.final
class NewVideoStreamRequest(google.protobuf.message.Message):
    """Create a new VideoStream
    VideoStream is used to receive video frames from a track
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRACK_HANDLE_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    FORMAT_FIELD_NUMBER: builtins.int
    NORMALIZE_STRIDE_FIELD_NUMBER: builtins.int
    track_handle: builtins.int
    type: global___VideoStreamType.ValueType
    format: global___VideoBufferType.ValueType
    """Get the frame on a specific format"""
    normalize_stride: builtins.bool
    """if true, stride will be set to width/chroma_width"""
    def __init__(
        self,
        *,
        track_handle: builtins.int = ...,
        type: global___VideoStreamType.ValueType = ...,
        format: global___VideoBufferType.ValueType | None = ...,
        normalize_stride: builtins.bool = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_format", b"_format", "format", b"format"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_format", b"_format", "format", b"format", "normalize_stride", b"normalize_stride", "track_handle", b"track_handle", "type", b"type"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_format", b"_format"]) -> typing_extensions.Literal["format"] | None: ...

global___NewVideoStreamRequest = NewVideoStreamRequest

@typing_extensions.final
class NewVideoStreamResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    STREAM_FIELD_NUMBER: builtins.int
    @property
    def stream(self) -> global___OwnedVideoStream: ...
    def __init__(
        self,
        *,
        stream: global___OwnedVideoStream | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["stream", b"stream"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["stream", b"stream"]) -> None: ...

global___NewVideoStreamResponse = NewVideoStreamResponse

@typing_extensions.final
class NewVideoSourceRequest(google.protobuf.message.Message):
    """Create a new VideoSource
    VideoSource is used to send video frame to a track
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TYPE_FIELD_NUMBER: builtins.int
    RESOLUTION_FIELD_NUMBER: builtins.int
    type: global___VideoSourceType.ValueType
    @property
    def resolution(self) -> global___VideoSourceResolution:
        """Used to determine which encodings to use + simulcast layers
        Most of the time it corresponds to the source resolution
        """
    def __init__(
        self,
        *,
        type: global___VideoSourceType.ValueType = ...,
        resolution: global___VideoSourceResolution | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["resolution", b"resolution"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["resolution", b"resolution", "type", b"type"]) -> None: ...

global___NewVideoSourceRequest = NewVideoSourceRequest

@typing_extensions.final
class NewVideoSourceResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SOURCE_FIELD_NUMBER: builtins.int
    @property
    def source(self) -> global___OwnedVideoSource: ...
    def __init__(
        self,
        *,
        source: global___OwnedVideoSource | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["source", b"source"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["source", b"source"]) -> None: ...

global___NewVideoSourceResponse = NewVideoSourceResponse

@typing_extensions.final
class CaptureVideoFrameRequest(google.protobuf.message.Message):
    """Push a frame to a VideoSource"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SOURCE_HANDLE_FIELD_NUMBER: builtins.int
    BUFFER_FIELD_NUMBER: builtins.int
    TIMESTAMP_US_FIELD_NUMBER: builtins.int
    ROTATION_FIELD_NUMBER: builtins.int
    source_handle: builtins.int
    @property
    def buffer(self) -> global___VideoBufferInfo: ...
    timestamp_us: builtins.int
    """In microseconds"""
    rotation: global___VideoRotation.ValueType
    def __init__(
        self,
        *,
        source_handle: builtins.int = ...,
        buffer: global___VideoBufferInfo | None = ...,
        timestamp_us: builtins.int = ...,
        rotation: global___VideoRotation.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["buffer", b"buffer"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["buffer", b"buffer", "rotation", b"rotation", "source_handle", b"source_handle", "timestamp_us", b"timestamp_us"]) -> None: ...

global___CaptureVideoFrameRequest = CaptureVideoFrameRequest

@typing_extensions.final
class CaptureVideoFrameResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___CaptureVideoFrameResponse = CaptureVideoFrameResponse

@typing_extensions.final
class VideoConvertRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    FLIP_Y_FIELD_NUMBER: builtins.int
    BUFFER_FIELD_NUMBER: builtins.int
    DST_TYPE_FIELD_NUMBER: builtins.int
    flip_y: builtins.bool
    @property
    def buffer(self) -> global___VideoBufferInfo: ...
    dst_type: global___VideoBufferType.ValueType
    def __init__(
        self,
        *,
        flip_y: builtins.bool = ...,
        buffer: global___VideoBufferInfo | None = ...,
        dst_type: global___VideoBufferType.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["buffer", b"buffer"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["buffer", b"buffer", "dst_type", b"dst_type", "flip_y", b"flip_y"]) -> None: ...

global___VideoConvertRequest = VideoConvertRequest

@typing_extensions.final
class VideoConvertResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ERROR_FIELD_NUMBER: builtins.int
    BUFFER_FIELD_NUMBER: builtins.int
    error: builtins.str
    @property
    def buffer(self) -> global___OwnedVideoBuffer: ...
    def __init__(
        self,
        *,
        error: builtins.str | None = ...,
        buffer: global___OwnedVideoBuffer | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_error", b"_error", "buffer", b"buffer", "error", b"error"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_error", b"_error", "buffer", b"buffer", "error", b"error"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_error", b"_error"]) -> typing_extensions.Literal["error"] | None: ...

global___VideoConvertResponse = VideoConvertResponse

@typing_extensions.final
class VideoResolution(google.protobuf.message.Message):
    """
    VideoFrame buffers
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    WIDTH_FIELD_NUMBER: builtins.int
    HEIGHT_FIELD_NUMBER: builtins.int
    FRAME_RATE_FIELD_NUMBER: builtins.int
    width: builtins.int
    height: builtins.int
    frame_rate: builtins.float
    def __init__(
        self,
        *,
        width: builtins.int = ...,
        height: builtins.int = ...,
        frame_rate: builtins.float = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["frame_rate", b"frame_rate", "height", b"height", "width", b"width"]) -> None: ...

global___VideoResolution = VideoResolution

@typing_extensions.final
class VideoBufferInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class ComponentInfo(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        DATA_PTR_FIELD_NUMBER: builtins.int
        STRIDE_FIELD_NUMBER: builtins.int
        SIZE_FIELD_NUMBER: builtins.int
        data_ptr: builtins.int
        stride: builtins.int
        size: builtins.int
        def __init__(
            self,
            *,
            data_ptr: builtins.int = ...,
            stride: builtins.int = ...,
            size: builtins.int = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["data_ptr", b"data_ptr", "size", b"size", "stride", b"stride"]) -> None: ...

    TYPE_FIELD_NUMBER: builtins.int
    WIDTH_FIELD_NUMBER: builtins.int
    HEIGHT_FIELD_NUMBER: builtins.int
    DATA_PTR_FIELD_NUMBER: builtins.int
    STRIDE_FIELD_NUMBER: builtins.int
    COMPONENTS_FIELD_NUMBER: builtins.int
    type: global___VideoBufferType.ValueType
    width: builtins.int
    height: builtins.int
    data_ptr: builtins.int
    stride: builtins.int
    """only for packed formats"""
    @property
    def components(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___VideoBufferInfo.ComponentInfo]: ...
    def __init__(
        self,
        *,
        type: global___VideoBufferType.ValueType = ...,
        width: builtins.int = ...,
        height: builtins.int = ...,
        data_ptr: builtins.int = ...,
        stride: builtins.int = ...,
        components: collections.abc.Iterable[global___VideoBufferInfo.ComponentInfo] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["components", b"components", "data_ptr", b"data_ptr", "height", b"height", "stride", b"stride", "type", b"type", "width", b"width"]) -> None: ...

global___VideoBufferInfo = VideoBufferInfo

@typing_extensions.final
class OwnedVideoBuffer(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___VideoBufferInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___VideoBufferInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedVideoBuffer = OwnedVideoBuffer

@typing_extensions.final
class VideoStreamInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TYPE_FIELD_NUMBER: builtins.int
    type: global___VideoStreamType.ValueType
    def __init__(
        self,
        *,
        type: global___VideoStreamType.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["type", b"type"]) -> None: ...

global___VideoStreamInfo = VideoStreamInfo

@typing_extensions.final
class OwnedVideoStream(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___VideoStreamInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___VideoStreamInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedVideoStream = OwnedVideoStream

@typing_extensions.final
class VideoStreamEvent(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    STREAM_HANDLE_FIELD_NUMBER: builtins.int
    FRAME_RECEIVED_FIELD_NUMBER: builtins.int
    EOS_FIELD_NUMBER: builtins.int
    stream_handle: builtins.int
    @property
    def frame_received(self) -> global___VideoFrameReceived: ...
    @property
    def eos(self) -> global___VideoStreamEOS: ...
    def __init__(
        self,
        *,
        stream_handle: builtins.int = ...,
        frame_received: global___VideoFrameReceived | None = ...,
        eos: global___VideoStreamEOS | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["eos", b"eos", "frame_received", b"frame_received", "message", b"message"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["eos", b"eos", "frame_received", b"frame_received", "message", b"message", "stream_handle", b"stream_handle"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["message", b"message"]) -> typing_extensions.Literal["frame_received", "eos"] | None: ...

global___VideoStreamEvent = VideoStreamEvent

@typing_extensions.final
class VideoFrameReceived(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    BUFFER_FIELD_NUMBER: builtins.int
    TIMESTAMP_US_FIELD_NUMBER: builtins.int
    ROTATION_FIELD_NUMBER: builtins.int
    @property
    def buffer(self) -> global___OwnedVideoBuffer: ...
    timestamp_us: builtins.int
    """In microseconds"""
    rotation: global___VideoRotation.ValueType
    def __init__(
        self,
        *,
        buffer: global___OwnedVideoBuffer | None = ...,
        timestamp_us: builtins.int = ...,
        rotation: global___VideoRotation.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["buffer", b"buffer"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["buffer", b"buffer", "rotation", b"rotation", "timestamp_us", b"timestamp_us"]) -> None: ...

global___VideoFrameReceived = VideoFrameReceived

@typing_extensions.final
class VideoStreamEOS(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___VideoStreamEOS = VideoStreamEOS

@typing_extensions.final
class VideoSourceResolution(google.protobuf.message.Message):
    """
    VideoSource
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    WIDTH_FIELD_NUMBER: builtins.int
    HEIGHT_FIELD_NUMBER: builtins.int
    width: builtins.int
    height: builtins.int
    def __init__(
        self,
        *,
        width: builtins.int = ...,
        height: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["height", b"height", "width", b"width"]) -> None: ...

global___VideoSourceResolution = VideoSourceResolution

@typing_extensions.final
class VideoSourceInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TYPE_FIELD_NUMBER: builtins.int
    type: global___VideoSourceType.ValueType
    def __init__(
        self,
        *,
        type: global___VideoSourceType.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["type", b"type"]) -> None: ...

global___VideoSourceInfo = VideoSourceInfo

@typing_extensions.final
class OwnedVideoSource(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HANDLE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int
    @property
    def handle(self) -> handle_pb2.FfiOwnedHandle: ...
    @property
    def info(self) -> global___VideoSourceInfo: ...
    def __init__(
        self,
        *,
        handle: handle_pb2.FfiOwnedHandle | None = ...,
        info: global___VideoSourceInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["handle", b"handle", "info", b"info"]) -> None: ...

global___OwnedVideoSource = OwnedVideoSource
