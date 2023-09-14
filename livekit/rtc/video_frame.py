# Copyright 2023 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ctypes

from ._ffi_client import FfiHandle, ffi_client
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from ._proto.video_frame_pb2 import VideoFormatType, VideoFrameBufferType, VideoRotation


class VideoFrame:
    def __init__(self, timestamp_us: int,
                 rotation: VideoRotation.ValueType,
                 buffer: 'VideoFrameBuffer') -> None:
        self.buffer = buffer
        self.timestamp_us = timestamp_us
        self.rotation = rotation


class VideoFrameBuffer:
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        self._info = owned_info.info
        self._ffi_handle = FfiHandle(owned_info.handle.id)

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
        req.to_i420.yuv_handle = self._ffi_handle.handle

        resp = ffi_client.request(req)
        return I420Buffer(resp.to_i420.buffer)

    def to_argb(self, dst: 'ArgbFrame') -> None:
        req = proto_ffi.FfiRequest()
        req.to_argb.buffer_handle = self._ffi_handle.handle
        req.to_argb.dst_ptr = ctypes.addressof(dst.data)
        req.to_argb.dst_format = dst.format
        req.to_argb.dst_stride = dst.width * 4
        req.to_argb.dst_width = dst.width
        req.to_argb.dst_height = dst.height

        ffi_client.request(req)

    @staticmethod
    def create(owned_info: proto_video_frame.OwnedVideoFrameBuffer) \
            -> 'VideoFrameBuffer':
        """
        Create the right class instance from the VideoFrameBufferInfo
        """

        info = owned_info.info
        if info.buffer_type == VideoFrameBufferType.NATIVE:
            return NativeVideoFrameBuffer(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I420:
            return I420Buffer(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I420A:
            return I420ABuffer(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I422:
            return I422Buffer(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I444:
            return I444Buffer(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I010:
            return I010Buffer(owned_info)
        elif info.buffer_type == VideoFrameBufferType.NV12:
            return NV12Buffer(owned_info)
        else:
            raise Exception('Unsupported VideoFrameBufferType')


class NativeVideoFrameBuffer(VideoFrameBuffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)


class PlanarYuvBuffer(VideoFrameBuffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)

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
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)

    @property
    def data_y(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.yuv.data_y_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.yuv.stride_y * self._info.height))).contents
        return arr

    @property
    def data_u(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.yuv.data_u_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.yuv.stride_u *
                              self._info.yuv.chroma_height))).contents
        return arr

    @property
    def data_v(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.yuv.data_v_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.yuv.stride_v *
                              self._info.yuv.chroma_height))).contents
        return arr


class PlanarYuv16Buffer(PlanarYuvBuffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)

    @property
    def data_y(self) -> ctypes.Array[ctypes.c_uint16]:
        arr = ctypes.cast(self._info.yuv.data_y_ptr, ctypes.POINTER(
            ctypes.c_uint16 * (self._info.yuv.stride_y // 2 *
                               self._info.height))).contents
        return arr

    @property
    def data_u(self) -> ctypes.Array[ctypes.c_uint16]:
        arr = ctypes.cast(self._info.yuv.data_u_ptr, ctypes.POINTER(
            ctypes.c_uint16 * (self._info.yuv.stride_u // 2 *
                               self._info.yuv.chroma_height))).contents
        return arr

    @property
    def data_v(self) -> ctypes.Array[ctypes.c_uint16]:
        arr = ctypes.cast(self._info.yuv.data_v_ptr, ctypes.POINTER(
            ctypes.c_uint16 * (self._info.yuv.stride_v // 2 *
                               self._info.yuv.chroma_height))).contents
        return arr


class BiplanaraYuv8Buffer(VideoFrameBuffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)

    @property
    def data_y(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.bi_yuv.data_y_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.bi_yuv.stride_y * self._info.height))).contents
        return arr

    @property
    def data_uv(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.bi_yuv.data_uv_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.bi_yuv.stride_uv *
                              self._info.bi_yuv.chroma_height))).contents
        return arr


class I420Buffer(PlanarYuv8Buffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)


class I420ABuffer(PlanarYuv8Buffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)

    @property
    def data_a(self) -> ctypes.Array[ctypes.c_uint8]:
        arr = ctypes.cast(self._info.yuv.data_a_ptr, ctypes.POINTER(
            ctypes.c_uint8 * (self._info.yuv.stride_a * self._info.height))).contents
        return arr


class I422Buffer(PlanarYuv8Buffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)


class I444Buffer(PlanarYuv8Buffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)


class I010Buffer(PlanarYuv16Buffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)


class NV12Buffer(BiplanaraYuv8Buffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        super().__init__(owned_info)


class ArgbFrame:
    """
    Mainly used to simplify the usage of to_argb method
    So the users don't need to deal with ctypes
    """

    def __init__(self,
                 format: VideoFormatType.ValueType,
                 width: int,
                 height: int) -> None:
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

        res = ffi_client.request(req)
        return I420Buffer(res.to_i420.buffer)

    @property
    def format(self) -> VideoFormatType.ValueType:
        return self._format
