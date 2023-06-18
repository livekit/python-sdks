import handle_pb2 as _handle_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VideoCodec(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VP8: _ClassVar[VideoCodec]
    H264: _ClassVar[VideoCodec]
    AV1: _ClassVar[VideoCodec]

class VideoRotation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VIDEO_ROTATION_0: _ClassVar[VideoRotation]
    VIDEO_ROTATION_90: _ClassVar[VideoRotation]
    VIDEO_ROTATION_180: _ClassVar[VideoRotation]
    VIDEO_ROTATION_270: _ClassVar[VideoRotation]

class VideoFormatType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    FORMAT_ARGB: _ClassVar[VideoFormatType]
    FORMAT_BGRA: _ClassVar[VideoFormatType]
    FORMAT_ABGR: _ClassVar[VideoFormatType]
    FORMAT_RGBA: _ClassVar[VideoFormatType]

class VideoFrameBufferType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    NATIVE: _ClassVar[VideoFrameBufferType]
    I420: _ClassVar[VideoFrameBufferType]
    I420A: _ClassVar[VideoFrameBufferType]
    I422: _ClassVar[VideoFrameBufferType]
    I444: _ClassVar[VideoFrameBufferType]
    I010: _ClassVar[VideoFrameBufferType]
    NV12: _ClassVar[VideoFrameBufferType]
    WEBGL: _ClassVar[VideoFrameBufferType]

class VideoStreamType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VIDEO_STREAM_NATIVE: _ClassVar[VideoStreamType]
    VIDEO_STREAM_WEBGL: _ClassVar[VideoStreamType]
    VIDEO_STREAM_HTML: _ClassVar[VideoStreamType]

class VideoSourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VIDEO_SOURCE_NATIVE: _ClassVar[VideoSourceType]
VP8: VideoCodec
H264: VideoCodec
AV1: VideoCodec
VIDEO_ROTATION_0: VideoRotation
VIDEO_ROTATION_90: VideoRotation
VIDEO_ROTATION_180: VideoRotation
VIDEO_ROTATION_270: VideoRotation
FORMAT_ARGB: VideoFormatType
FORMAT_BGRA: VideoFormatType
FORMAT_ABGR: VideoFormatType
FORMAT_RGBA: VideoFormatType
NATIVE: VideoFrameBufferType
I420: VideoFrameBufferType
I420A: VideoFrameBufferType
I422: VideoFrameBufferType
I444: VideoFrameBufferType
I010: VideoFrameBufferType
NV12: VideoFrameBufferType
WEBGL: VideoFrameBufferType
VIDEO_STREAM_NATIVE: VideoStreamType
VIDEO_STREAM_WEBGL: VideoStreamType
VIDEO_STREAM_HTML: VideoStreamType
VIDEO_SOURCE_NATIVE: VideoSourceType

class AllocVideoBufferRequest(_message.Message):
    __slots__ = ["type", "width", "height"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    type: VideoFrameBufferType
    width: int
    height: int
    def __init__(self, type: _Optional[_Union[VideoFrameBufferType, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class AllocVideoBufferResponse(_message.Message):
    __slots__ = ["buffer"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: VideoFrameBufferInfo
    def __init__(self, buffer: _Optional[_Union[VideoFrameBufferInfo, _Mapping]] = ...) -> None: ...

class NewVideoStreamRequest(_message.Message):
    __slots__ = ["track_handle", "type"]
    TRACK_HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    track_handle: _handle_pb2.FfiHandleId
    type: VideoStreamType
    def __init__(self, track_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., type: _Optional[_Union[VideoStreamType, str]] = ...) -> None: ...

class NewVideoStreamResponse(_message.Message):
    __slots__ = ["stream"]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    stream: VideoStreamInfo
    def __init__(self, stream: _Optional[_Union[VideoStreamInfo, _Mapping]] = ...) -> None: ...

class NewVideoSourceRequest(_message.Message):
    __slots__ = ["type", "resolution"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    type: VideoSourceType
    resolution: VideoSourceResolution
    def __init__(self, type: _Optional[_Union[VideoSourceType, str]] = ..., resolution: _Optional[_Union[VideoSourceResolution, _Mapping]] = ...) -> None: ...

class NewVideoSourceResponse(_message.Message):
    __slots__ = ["source"]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    source: VideoSourceInfo
    def __init__(self, source: _Optional[_Union[VideoSourceInfo, _Mapping]] = ...) -> None: ...

class CaptureVideoFrameRequest(_message.Message):
    __slots__ = ["source_handle", "frame", "buffer_handle"]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    BUFFER_HANDLE_FIELD_NUMBER: _ClassVar[int]
    source_handle: _handle_pb2.FfiHandleId
    frame: VideoFrameInfo
    buffer_handle: _handle_pb2.FfiHandleId
    def __init__(self, source_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., frame: _Optional[_Union[VideoFrameInfo, _Mapping]] = ..., buffer_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ...) -> None: ...

class CaptureVideoFrameResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ToI420Request(_message.Message):
    __slots__ = ["flip_y", "argb", "buffer"]
    FLIP_Y_FIELD_NUMBER: _ClassVar[int]
    ARGB_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    flip_y: bool
    argb: ARGBBufferInfo
    buffer: _handle_pb2.FfiHandleId
    def __init__(self, flip_y: bool = ..., argb: _Optional[_Union[ARGBBufferInfo, _Mapping]] = ..., buffer: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ...) -> None: ...

class ToI420Response(_message.Message):
    __slots__ = ["buffer"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: VideoFrameBufferInfo
    def __init__(self, buffer: _Optional[_Union[VideoFrameBufferInfo, _Mapping]] = ...) -> None: ...

class ToArgbRequest(_message.Message):
    __slots__ = ["buffer", "dst_ptr", "dst_format", "dst_stride", "dst_width", "dst_height", "flip_y"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    DST_PTR_FIELD_NUMBER: _ClassVar[int]
    DST_FORMAT_FIELD_NUMBER: _ClassVar[int]
    DST_STRIDE_FIELD_NUMBER: _ClassVar[int]
    DST_WIDTH_FIELD_NUMBER: _ClassVar[int]
    DST_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FLIP_Y_FIELD_NUMBER: _ClassVar[int]
    buffer: _handle_pb2.FfiHandleId
    dst_ptr: int
    dst_format: VideoFormatType
    dst_stride: int
    dst_width: int
    dst_height: int
    flip_y: bool
    def __init__(self, buffer: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., dst_ptr: _Optional[int] = ..., dst_format: _Optional[_Union[VideoFormatType, str]] = ..., dst_stride: _Optional[int] = ..., dst_width: _Optional[int] = ..., dst_height: _Optional[int] = ..., flip_y: bool = ...) -> None: ...

class ToArgbResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class VideoResolution(_message.Message):
    __slots__ = ["width", "height", "frame_rate"]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FRAME_RATE_FIELD_NUMBER: _ClassVar[int]
    width: int
    height: int
    frame_rate: float
    def __init__(self, width: _Optional[int] = ..., height: _Optional[int] = ..., frame_rate: _Optional[float] = ...) -> None: ...

class ARGBBufferInfo(_message.Message):
    __slots__ = ["ptr", "format", "stride", "width", "height"]
    PTR_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    STRIDE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ptr: int
    format: VideoFormatType
    stride: int
    width: int
    height: int
    def __init__(self, ptr: _Optional[int] = ..., format: _Optional[_Union[VideoFormatType, str]] = ..., stride: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class VideoFrameInfo(_message.Message):
    __slots__ = ["timestamp_us", "rotation"]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    timestamp_us: int
    rotation: VideoRotation
    def __init__(self, timestamp_us: _Optional[int] = ..., rotation: _Optional[_Union[VideoRotation, str]] = ...) -> None: ...

class VideoFrameBufferInfo(_message.Message):
    __slots__ = ["handle", "buffer_type", "width", "height", "yuv", "bi_yuv", "native"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    BUFFER_TYPE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    YUV_FIELD_NUMBER: _ClassVar[int]
    BI_YUV_FIELD_NUMBER: _ClassVar[int]
    NATIVE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    buffer_type: VideoFrameBufferType
    width: int
    height: int
    yuv: PlanarYuvBufferInfo
    bi_yuv: BiplanarYuvBufferInfo
    native: NativeBufferInfo
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., buffer_type: _Optional[_Union[VideoFrameBufferType, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., yuv: _Optional[_Union[PlanarYuvBufferInfo, _Mapping]] = ..., bi_yuv: _Optional[_Union[BiplanarYuvBufferInfo, _Mapping]] = ..., native: _Optional[_Union[NativeBufferInfo, _Mapping]] = ...) -> None: ...

class PlanarYuvBufferInfo(_message.Message):
    __slots__ = ["chroma_width", "chroma_height", "stride_y", "stride_u", "stride_v", "stride_a", "data_y_ptr", "data_u_ptr", "data_v_ptr", "data_a_ptr"]
    CHROMA_WIDTH_FIELD_NUMBER: _ClassVar[int]
    CHROMA_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    STRIDE_Y_FIELD_NUMBER: _ClassVar[int]
    STRIDE_U_FIELD_NUMBER: _ClassVar[int]
    STRIDE_V_FIELD_NUMBER: _ClassVar[int]
    STRIDE_A_FIELD_NUMBER: _ClassVar[int]
    DATA_Y_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_U_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_V_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_A_PTR_FIELD_NUMBER: _ClassVar[int]
    chroma_width: int
    chroma_height: int
    stride_y: int
    stride_u: int
    stride_v: int
    stride_a: int
    data_y_ptr: int
    data_u_ptr: int
    data_v_ptr: int
    data_a_ptr: int
    def __init__(self, chroma_width: _Optional[int] = ..., chroma_height: _Optional[int] = ..., stride_y: _Optional[int] = ..., stride_u: _Optional[int] = ..., stride_v: _Optional[int] = ..., stride_a: _Optional[int] = ..., data_y_ptr: _Optional[int] = ..., data_u_ptr: _Optional[int] = ..., data_v_ptr: _Optional[int] = ..., data_a_ptr: _Optional[int] = ...) -> None: ...

class BiplanarYuvBufferInfo(_message.Message):
    __slots__ = ["chroma_width", "chroma_height", "stride_y", "stride_uv", "data_y_ptr", "data_uv_ptr"]
    CHROMA_WIDTH_FIELD_NUMBER: _ClassVar[int]
    CHROMA_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    STRIDE_Y_FIELD_NUMBER: _ClassVar[int]
    STRIDE_UV_FIELD_NUMBER: _ClassVar[int]
    DATA_Y_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_UV_PTR_FIELD_NUMBER: _ClassVar[int]
    chroma_width: int
    chroma_height: int
    stride_y: int
    stride_uv: int
    data_y_ptr: int
    data_uv_ptr: int
    def __init__(self, chroma_width: _Optional[int] = ..., chroma_height: _Optional[int] = ..., stride_y: _Optional[int] = ..., stride_uv: _Optional[int] = ..., data_y_ptr: _Optional[int] = ..., data_uv_ptr: _Optional[int] = ...) -> None: ...

class NativeBufferInfo(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class VideoStreamInfo(_message.Message):
    __slots__ = ["handle", "type"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    type: VideoStreamType
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., type: _Optional[_Union[VideoStreamType, str]] = ...) -> None: ...

class VideoStreamEvent(_message.Message):
    __slots__ = ["handle", "frame_received"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    FRAME_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    frame_received: VideoFrameReceived
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., frame_received: _Optional[_Union[VideoFrameReceived, _Mapping]] = ...) -> None: ...

class VideoFrameReceived(_message.Message):
    __slots__ = ["frame", "buffer"]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    frame: VideoFrameInfo
    buffer: VideoFrameBufferInfo
    def __init__(self, frame: _Optional[_Union[VideoFrameInfo, _Mapping]] = ..., buffer: _Optional[_Union[VideoFrameBufferInfo, _Mapping]] = ...) -> None: ...

class VideoSourceResolution(_message.Message):
    __slots__ = ["width", "height"]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    width: int
    height: int
    def __init__(self, width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class VideoSourceInfo(_message.Message):
    __slots__ = ["handle", "type"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    type: VideoSourceType
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., type: _Optional[_Union[VideoSourceType, str]] = ...) -> None: ...
