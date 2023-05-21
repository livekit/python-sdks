import handle_pb2 as _handle_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

AV1: VideoCodec
DESCRIPTOR: _descriptor.FileDescriptor
FORMAT_ABGR: VideoFormatType
FORMAT_ARGB: VideoFormatType
FORMAT_BGRA: VideoFormatType
FORMAT_RGBA: VideoFormatType
H264: VideoCodec
I010: VideoFrameBufferType
I420: VideoFrameBufferType
I420A: VideoFrameBufferType
I422: VideoFrameBufferType
I444: VideoFrameBufferType
NATIVE: VideoFrameBufferType
NV12: VideoFrameBufferType
VIDEO_ROTATION_0: VideoRotation
VIDEO_ROTATION_180: VideoRotation
VIDEO_ROTATION_270: VideoRotation
VIDEO_ROTATION_90: VideoRotation
VIDEO_SOURCE_NATIVE: VideoSourceType
VIDEO_STREAM_HTML: VideoStreamType
VIDEO_STREAM_NATIVE: VideoStreamType
VIDEO_STREAM_WEBGL: VideoStreamType
VP8: VideoCodec
WEBGL: VideoFrameBufferType

class ARGBBufferInfo(_message.Message):
    __slots__ = ["format", "height", "ptr", "stride", "width"]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    PTR_FIELD_NUMBER: _ClassVar[int]
    STRIDE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    format: VideoFormatType
    height: int
    ptr: int
    stride: int
    width: int
    def __init__(self, ptr: _Optional[int] = ..., format: _Optional[_Union[VideoFormatType, str]] = ..., stride: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class AllocVideoBufferRequest(_message.Message):
    __slots__ = ["height", "type", "width"]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    height: int
    type: VideoFrameBufferType
    width: int
    def __init__(self, type: _Optional[_Union[VideoFrameBufferType, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class AllocVideoBufferResponse(_message.Message):
    __slots__ = ["buffer"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: VideoFrameBufferInfo
    def __init__(self, buffer: _Optional[_Union[VideoFrameBufferInfo, _Mapping]] = ...) -> None: ...

class BiplanarYuvBufferInfo(_message.Message):
    __slots__ = ["chroma_height", "chroma_width", "data_uv_ptr", "data_y_ptr", "stride_uv", "stride_y"]
    CHROMA_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CHROMA_WIDTH_FIELD_NUMBER: _ClassVar[int]
    DATA_UV_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_Y_PTR_FIELD_NUMBER: _ClassVar[int]
    STRIDE_UV_FIELD_NUMBER: _ClassVar[int]
    STRIDE_Y_FIELD_NUMBER: _ClassVar[int]
    chroma_height: int
    chroma_width: int
    data_uv_ptr: int
    data_y_ptr: int
    stride_uv: int
    stride_y: int
    def __init__(self, chroma_width: _Optional[int] = ..., chroma_height: _Optional[int] = ..., stride_y: _Optional[int] = ..., stride_uv: _Optional[int] = ..., data_y_ptr: _Optional[int] = ..., data_uv_ptr: _Optional[int] = ...) -> None: ...

class CaptureVideoFrameRequest(_message.Message):
    __slots__ = ["buffer_handle", "frame", "source_handle"]
    BUFFER_HANDLE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    buffer_handle: _handle_pb2.FFIHandleId
    frame: VideoFrameInfo
    source_handle: _handle_pb2.FFIHandleId
    def __init__(self, source_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., frame: _Optional[_Union[VideoFrameInfo, _Mapping]] = ..., buffer_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ...) -> None: ...

class CaptureVideoFrameResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class NativeBufferInfo(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class NewVideoSourceRequest(_message.Message):
    __slots__ = ["type"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: VideoSourceType
    def __init__(self, type: _Optional[_Union[VideoSourceType, str]] = ...) -> None: ...

class NewVideoSourceResponse(_message.Message):
    __slots__ = ["source"]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    source: VideoSourceInfo
    def __init__(self, source: _Optional[_Union[VideoSourceInfo, _Mapping]] = ...) -> None: ...

class NewVideoStreamRequest(_message.Message):
    __slots__ = ["participant_sid", "room_handle", "track_sid", "type"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    ROOM_HANDLE_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    room_handle: _handle_pb2.FFIHandleId
    track_sid: str
    type: VideoStreamType
    def __init__(self, room_handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ..., type: _Optional[_Union[VideoStreamType, str]] = ...) -> None: ...

class NewVideoStreamResponse(_message.Message):
    __slots__ = ["stream"]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    stream: VideoStreamInfo
    def __init__(self, stream: _Optional[_Union[VideoStreamInfo, _Mapping]] = ...) -> None: ...

class PlanarYuvBufferInfo(_message.Message):
    __slots__ = ["chroma_height", "chroma_width", "data_a_ptr", "data_u_ptr", "data_v_ptr", "data_y_ptr", "stride_a", "stride_u", "stride_v", "stride_y"]
    CHROMA_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CHROMA_WIDTH_FIELD_NUMBER: _ClassVar[int]
    DATA_A_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_U_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_V_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_Y_PTR_FIELD_NUMBER: _ClassVar[int]
    STRIDE_A_FIELD_NUMBER: _ClassVar[int]
    STRIDE_U_FIELD_NUMBER: _ClassVar[int]
    STRIDE_V_FIELD_NUMBER: _ClassVar[int]
    STRIDE_Y_FIELD_NUMBER: _ClassVar[int]
    chroma_height: int
    chroma_width: int
    data_a_ptr: int
    data_u_ptr: int
    data_v_ptr: int
    data_y_ptr: int
    stride_a: int
    stride_u: int
    stride_v: int
    stride_y: int
    def __init__(self, chroma_width: _Optional[int] = ..., chroma_height: _Optional[int] = ..., stride_y: _Optional[int] = ..., stride_u: _Optional[int] = ..., stride_v: _Optional[int] = ..., stride_a: _Optional[int] = ..., data_y_ptr: _Optional[int] = ..., data_u_ptr: _Optional[int] = ..., data_v_ptr: _Optional[int] = ..., data_a_ptr: _Optional[int] = ...) -> None: ...

class ToARGBRequest(_message.Message):
    __slots__ = ["buffer", "dst_format", "dst_height", "dst_ptr", "dst_stride", "dst_width", "flip_y"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    DST_FORMAT_FIELD_NUMBER: _ClassVar[int]
    DST_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DST_PTR_FIELD_NUMBER: _ClassVar[int]
    DST_STRIDE_FIELD_NUMBER: _ClassVar[int]
    DST_WIDTH_FIELD_NUMBER: _ClassVar[int]
    FLIP_Y_FIELD_NUMBER: _ClassVar[int]
    buffer: _handle_pb2.FFIHandleId
    dst_format: VideoFormatType
    dst_height: int
    dst_ptr: int
    dst_stride: int
    dst_width: int
    flip_y: bool
    def __init__(self, buffer: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., dst_ptr: _Optional[int] = ..., dst_format: _Optional[_Union[VideoFormatType, str]] = ..., dst_stride: _Optional[int] = ..., dst_width: _Optional[int] = ..., dst_height: _Optional[int] = ..., flip_y: bool = ...) -> None: ...

class ToARGBResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ToI420Request(_message.Message):
    __slots__ = ["argb", "buffer", "flip_y"]
    ARGB_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    FLIP_Y_FIELD_NUMBER: _ClassVar[int]
    argb: ARGBBufferInfo
    buffer: _handle_pb2.FFIHandleId
    flip_y: bool
    def __init__(self, flip_y: bool = ..., argb: _Optional[_Union[ARGBBufferInfo, _Mapping]] = ..., buffer: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ...) -> None: ...

class ToI420Response(_message.Message):
    __slots__ = ["buffer"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: VideoFrameBufferInfo
    def __init__(self, buffer: _Optional[_Union[VideoFrameBufferInfo, _Mapping]] = ...) -> None: ...

class VideoFrameBufferInfo(_message.Message):
    __slots__ = ["bi_yuv", "buffer_type", "handle", "height", "native", "width", "yuv"]
    BI_YUV_FIELD_NUMBER: _ClassVar[int]
    BUFFER_TYPE_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    NATIVE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    YUV_FIELD_NUMBER: _ClassVar[int]
    bi_yuv: BiplanarYuvBufferInfo
    buffer_type: VideoFrameBufferType
    handle: _handle_pb2.FFIHandleId
    height: int
    native: NativeBufferInfo
    width: int
    yuv: PlanarYuvBufferInfo
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., buffer_type: _Optional[_Union[VideoFrameBufferType, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., yuv: _Optional[_Union[PlanarYuvBufferInfo, _Mapping]] = ..., bi_yuv: _Optional[_Union[BiplanarYuvBufferInfo, _Mapping]] = ..., native: _Optional[_Union[NativeBufferInfo, _Mapping]] = ...) -> None: ...

class VideoFrameInfo(_message.Message):
    __slots__ = ["rotation", "timestamp"]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    rotation: VideoRotation
    timestamp: int
    def __init__(self, timestamp: _Optional[int] = ..., rotation: _Optional[_Union[VideoRotation, str]] = ...) -> None: ...

class VideoFrameReceived(_message.Message):
    __slots__ = ["buffer", "frame"]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    buffer: VideoFrameBufferInfo
    frame: VideoFrameInfo
    def __init__(self, frame: _Optional[_Union[VideoFrameInfo, _Mapping]] = ..., buffer: _Optional[_Union[VideoFrameBufferInfo, _Mapping]] = ...) -> None: ...

class VideoResolution(_message.Message):
    __slots__ = ["frame_rate", "height", "width"]
    FRAME_RATE_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    frame_rate: float
    height: int
    width: int
    def __init__(self, width: _Optional[int] = ..., height: _Optional[int] = ..., frame_rate: _Optional[float] = ...) -> None: ...

class VideoSourceInfo(_message.Message):
    __slots__ = ["handle", "type"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FFIHandleId
    type: VideoSourceType
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., type: _Optional[_Union[VideoSourceType, str]] = ...) -> None: ...

class VideoStreamEvent(_message.Message):
    __slots__ = ["frame_received", "handle"]
    FRAME_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    frame_received: VideoFrameReceived
    handle: _handle_pb2.FFIHandleId
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., frame_received: _Optional[_Union[VideoFrameReceived, _Mapping]] = ...) -> None: ...

class VideoStreamInfo(_message.Message):
    __slots__ = ["handle", "track_sid", "type"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FFIHandleId
    track_sid: str
    type: VideoStreamType
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FFIHandleId, _Mapping]] = ..., type: _Optional[_Union[VideoStreamType, str]] = ..., track_sid: _Optional[str] = ...) -> None: ...

class VideoCodec(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class VideoRotation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class VideoFormatType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class VideoFrameBufferType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class VideoStreamType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class VideoSourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
