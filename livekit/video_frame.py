import ctypes
from ._ffi_client import FfiHandle
from ._proto import video_frame_pb2 as proto_video_frame
from ._proto import ffi_pb2 as proto_ffi
from ._ffi_client import FfiClient
from livekit import (VideoRotation, VideoFormatType, VideoFrameBufferType)


class VideoFrame():
    def __init__(self, timestamp_us: int, rotation: VideoRotation.ValueType, buffer: 'VideoFrameBuffer') -> None:
        self.buffer = buffer
        self.timestamp_us = timestamp_us
        self.rotation = rotation


class VideoFrameBuffer():
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        self._info = info
        self._ffi_handle = ffi_handle

    @property
    def width(self) -> int:
        return self._info.width

    @property
    def height(self) -> int:
        return self._info.height

    @property
    def type(self) -> VideoFrameBufferType.ValueType:
        return self._info.buffer_type

    def to_i420(self) -> 'I420Buffer':
        req = proto_ffi.FfiRequest()
        req.to_i420.buffer.id = self._ffi_handle.handle

        ffi_client = FfiClient()
        resp = ffi_client.request(req)

        new_info = resp.to_i420.buffer
        ffi_handle = FfiHandle(new_info.handle.id)
        return I420Buffer(ffi_handle, new_info)

    def to_argb(self, dst: 'ArgbFrame') -> None:
        req = proto_ffi.FfiRequest()
        req.to_argb.buffer.id = self._ffi_handle.handle
        req.to_argb.dst_ptr = ctypes.addressof(dst.data)
        req.to_argb.dst_format = dst.format
        req.to_argb.dst_stride = dst.width * 4
        req.to_argb.dst_width = dst.width
        req.to_argb.dst_height = dst.height

        ffi_client = FfiClient()
        ffi_client.request(req)

    @staticmethod
    def create(ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> 'VideoFrameBuffer':
        """
        Create the right class instance from the VideoFrameBufferInfo
        """

        if info.buffer_type == VideoFrameBufferType.NATIVE:
            return NativeVideoFrameBuffer(ffi_handle, info)
        elif info.buffer_type == VideoFrameBufferType.I420:
            return I420Buffer(ffi_handle, info)
        elif info.buffer_type == VideoFrameBufferType.I420A:
            return I420ABuffer(ffi_handle, info)
        elif info.buffer_type == VideoFrameBufferType.I422:
            return I422Buffer(ffi_handle, info)
        elif info.buffer_type == VideoFrameBufferType.I444:
            return I444Buffer(ffi_handle, info)
        elif info.buffer_type == VideoFrameBufferType.I010:
            return I010Buffer(ffi_handle, info)
        elif info.buffer_type == VideoFrameBufferType.NV12:
            return NV12Buffer(ffi_handle, info)
        else:
            raise Exception('Unsupported VideoFrameBufferType')


class NativeVideoFrameBuffer(VideoFrameBuffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)


class PlanarYuvBuffer(VideoFrameBuffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)

    @property
    def chroma_width(self) -> int:
        return self._info.yuv.chroma_width

    @property
    def chroma_height(self) -> int:
        return self._info.yuv.chroma_height

    @property
    def stride_y(self) -> int:
        return self._info.yuv.stride_y

    @property
    def stride_u(self) -> int:
        return self._info.yuv.stride_u

    @property
    def stride_v(self) -> int:
        return self._info.yuv.stride_v


class PlanarYuv8Buffer(PlanarYuvBuffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)

    @property
    def data_y(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.yuv.data_y_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.yuv.stride_y * self._info.height))).contents
        return arr

    @property
    def data_u(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.yuv.data_u_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.yuv.stride_u * self._info.yuv.chroma_height))).contents
        return arr

    @property
    def data_v(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.yuv.data_v_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.yuv.stride_v * self._info.yuv.chroma_height))).contents
        return arr


class PlanarYuv16Buffer(PlanarYuvBuffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)

    @property
    def data_y(self) -> ctypes.Array[ctypes.c_uint16]:
        arr = ctypes.cast(self._info.yuv.data_y_ptr, ctypes.POINTER(
            ctypes.c_uint16 * (self._info.yuv.stride_y // 2 * self._info.height))).contents
        return arr

    @property
    def data_u(self) -> ctypes.Array[ctypes.c_uint16]:
        arr = ctypes.cast(self._info.yuv.data_u_ptr, ctypes.POINTER(
            ctypes.c_uint16 * (self._info.yuv.stride_u // 2 * self._info.yuv.chroma_height))).contents
        return arr

    @property
    def data_v(self) -> ctypes.Array[ctypes.c_uint16]:
        arr = ctypes.cast(self._info.yuv.data_v_ptr, ctypes.POINTER(
            ctypes.c_uint16 * (self._info.yuv.stride_v // 2 * self._info.yuv.chroma_height))).contents
        return arr


class BiplanaraYuv8Buffer(VideoFrameBuffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)

    @property
    def data_y(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.bi_yuv.data_y_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.bi_yuv.stride_y * self._info.height))).contents
        return arr

    @property
    def data_uv(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.bi_yuv.data_uv_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.bi_yuv.stride_uv * self._info.bi_yuv.chroma_height))).contents
        return arr


class I420Buffer(PlanarYuv8Buffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)


class I420ABuffer(PlanarYuv8Buffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)

    @property
    def data_a(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.yuv.data_a_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.yuv.stride_a * self._info.height))).contents
        return arr


class I422Buffer(PlanarYuv8Buffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)


class I444Buffer(PlanarYuv8Buffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)


class I010Buffer(PlanarYuv16Buffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)


class NV12Buffer(BiplanaraYuv8Buffer):
    def __init__(self, ffi_handle: FfiHandle, info: proto_video_frame.VideoFrameBufferInfo) -> None:
        super().__init__(ffi_handle, info)


class ArgbFrame:
    """
    Mainly used to simplify the usage of to_argb method
    So the users don't need to deal with ctypes
    """

    def __init__(self, format: VideoFormatType.ValueType, width: int, height: int) -> None:
        self._format = format
        self.width = width
        self.height = height
        self.data = (ctypes.c_uint8 * (width * height *
                     ctypes.sizeof(ctypes.c_uint32)))()  # alloc frame

    def to_i420(self) -> I420Buffer:
        # TODO(theomonnom): avoid unnecessary buffer allocation
        req = proto_ffi.FfiRequest()
        req.to_i420.argb.format = self._format
        req.to_i420.argb.width = self.width
        req.to_i420.argb.height = self.height
        req.to_i420.argb.stride = self.width * 4
        req.to_i420.argb.ptr = ctypes.addressof(self.data)

        ffi_client = FfiClient()
        res = ffi_client.request(req)
        buffer_info = res.to_i420.buffer
        ffi_handle = FfiHandle(buffer_info.handle.id)
        return I420Buffer(ffi_handle, buffer_info)

    @property
    def format(self) -> VideoFormatType.ValueType:
        return self._format
