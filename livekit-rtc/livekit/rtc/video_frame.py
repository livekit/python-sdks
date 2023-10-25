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
from typing import Union

from ._ffi_client import FfiHandle, ffi_client
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from ._proto.video_frame_pb2 import VideoFormatType, VideoFrameBufferType, VideoFrameReceived, VideoRotation
from abc import ABC


class VideoFrame:
    def __init__(self, timestamp_us: int,
                 rotation: VideoRotation.ValueType,
                 buffer: 'VideoFrameBuffer') -> None:
        self.buffer = buffer
        self.timestamp_us = timestamp_us
        self.rotation = rotation


class VideoFrameBuffer(ABC):

    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 buffer_type: VideoFrameBufferType.ValueType) -> None:
        self._data = data
        self._width = width
        self._height = height
        self._buffer_type = buffer_type

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def type(self) -> VideoFrameBufferType.ValueType:
        return self._buffer_type

    # TODO(theomonnom): Need Rust modification
    def to_i420(self) -> 'I420Buffer':
        req = proto_ffi.FfiRequest()
        req.to_i420.yuv_handle = self._ffi_handle.handle
        resp = ffi_client.request(req)
        return I420Buffer(resp.to_i420.buffer)

    # TODO(theomonnom): Need Rust modification
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
    def _from_owned_info(owned_info: proto_video_frame.OwnedVideoFrameBuffer) \
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


# TODO(theomonnom): Ability to get GPU texture directly
class NativeVideoFrameBuffer(VideoFrameBuffer):
    def __init__(self, width: int, height: int) -> None:
        super().__init__(bytearray(), width, height, VideoFrameBufferType.NATIVE)


class PlanarYuvBuffer(VideoFrameBuffer, ABC):
    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 buffer_type: VideoFrameBufferType.ValueType,
                 stride_y: int,
                 stride_u: int,
                 stride_v: int,
                 chroma_width: int,
                 chroma_height: int) -> None:
        super().__init__(data, width, height, buffer_type)
        self._stride_y = stride_y
        self._stride_u = stride_u
        self._stride_v = stride_v
        self._chroma_width = chroma_width
        self._chroma_height = chroma_height

    @property
    def chroma_width(self) -> int:
        return self._chroma_width

    @property
    def chroma_height(self) -> int:
        return self._chroma_height

    @property
    def stride_y(self) -> int:
        return self._stride_y

    @property
    def stride_u(self) -> int:
        return self._stride_u

    @property
    def stride_v(self) -> int:
        return self._stride_v


class PlanarYuv8Buffer(PlanarYuvBuffer, ABC):
    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 buffer_type: VideoFrameBufferType.ValueType,
                 stride_y: int,
                 stride_u: int,
                 stride_v: int,
                 chroma_width: int,
                 chroma_height: int) -> None:
        super().__init__(data, width, height, buffer_type, stride_u,
                         stride_y, stride_v, chroma_width, chroma_height)

    @property
    def data_y(self) -> memoryview:
        return memoryview(self._data)[0:self._stride_y * self._height]

    @property
    def data_u(self) -> memoryview:
        return memoryview(self._data)[self._stride_y * self._height:
                                      self._stride_y * self._height +
                                      self._stride_u * self._chroma_height]

    @property
    def data_v(self) -> memoryview:
        return memoryview(self._data)[self._stride_y * self._height +
                                      self._stride_u * self._chroma_height:
                                      self._stride_y * self._height +
                                      self._stride_u * self._chroma_height +
                                      self._stride_v * self._chroma_height]


class PlanarYuv16Buffer(PlanarYuvBuffer, ABC):
    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 buffer_type: VideoFrameBufferType.ValueType,
                 stride_y: int,
                 stride_u: int,
                 stride_v: int,
                 chroma_width: int,
                 chroma_height: int) -> None:
        super().__init__(data, width, height, buffer_type, stride_y,
                         stride_u, stride_v, chroma_width, chroma_height)

    @property
    def data_y(self) -> memoryview:
        return memoryview(self._data)[0:self._stride_y * self._height].cast('H')

    @property
    def data_u(self) -> memoryview:
        return memoryview(self._data)[self._stride_y * self._height:
                                      self._stride_y * self._height +
                                      self._stride_u * self._chroma_height].cast('H')

    @property
    def data_v(self) -> memoryview:
        return memoryview(self._data)[self._stride_y * self._height +
                                      self._stride_u * self._chroma_height:
                                      self._stride_y * self._height +
                                      self._stride_u * self._chroma_height +
                                      self._stride_v * self._chroma_height].cast('H')


class BiplanaraYuv8Buffer(VideoFrameBuffer, ABC):
    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 buffer_type: VideoFrameBufferType.ValueType,
                 stride_y: int,
                 stride_uv: int,
                 chroma_width: int,
                 chroma_height: int) -> None:
        super().__init__(data, width, height, buffer_type)
        self._stride_y = stride_y
        self._stride_uv = stride_uv
        self._chroma_width = chroma_width
        self._chroma_height = chroma_height

    @property
    def chroma_width(self) -> int:
        return self._chroma_width

    @property
    def chroma_height(self) -> int:
        return self._chroma_height

    @property
    def stride_y(self) -> int:
        return self._stride_y

    @property
    def stride_uv(self) -> int:
        return self._stride_uv

    @ property
    def data_y(self) -> memoryview:
        return memoryview(self._data)[0:self._stride_y * self._height]

    @ property
    def data_uv(self) -> memoryview:
        return memoryview(self._data)[self._stride_y * self._height:
                                      self._stride_y * self._height +
                                      self._stride_uv * self._chroma_height]


class I420Buffer(PlanarYuv8Buffer):
    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 stride_y: int,
                 stride_u: int,
                 stride_v: int) -> None:

        if len(data) < I420Buffer.calc_data_size(height, stride_y, stride_u, stride_v):
            raise ValueError(
                'buffer too small for I420 data. Expected {} bytes, got {}.'.format(
                    I420Buffer.calc_data_size(height, stride_y, stride_u, stride_v), len(data)))

        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        super().__init__(data, width, height,
                         VideoFrameBufferType.I420, stride_y, stride_u, stride_v, chroma_width, chroma_height)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int) -> int:
        return stride_y * height + (stride_u + stride_v) * ((height + 1) // 2)

    @staticmethod
    def create(width: int, height: int) -> 'I420Buffer':
        stride_y = width
        stride_u = (width + 1) // 2
        stride_v = (width + 1) // 2
        data_size = I420Buffer.calc_data_size(
            height, stride_y, stride_u, stride_v)
        data = bytearray(data_size)
        return I420Buffer(data, width, height, stride_y, stride_u, stride_v)


class I420ABuffer(PlanarYuv8Buffer):
    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 stride_y: int,
                 stride_u: int,
                 stride_v: int,
                 stride_a: int) -> None:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        super().__init__(data, width, height, VideoFrameBufferType.I420A,
                         stride_y, stride_u, stride_v, chroma_width, chroma_height)
        self._stride_a = stride_a

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int, stride_a: int) -> int:
        return (stride_y + stride_a) * height + (stride_u + stride_v) * ((height + 1) // 2)

    @property
    def stride_a(self) -> int:
        return self._stride_a

    @property
    def data_a(self) -> memoryview:
        return memoryview(self._data)[self._stride_y * self._height +
                                      self._stride_u * self._chroma_height +
                                      self._stride_v * self._chroma_height:
                                      self._stride_y * self._height +
                                      self._stride_u * self._chroma_height +
                                      self._stride_v * self._chroma_height +
                                      self._stride_a * self._height]


class I422Buffer(PlanarYuv8Buffer):
    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 stride_y: int,
                 stride_u: int,
                 stride_v: int) -> None:
        chroma_width = (width + 1) // 2
        chroma_height = height
        super().__init__(data, width, height, VideoFrameBufferType.I422,
                         stride_y, stride_u, stride_v, chroma_width, chroma_height)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int) -> int:
        return stride_y * height + stride_u * height + stride_v * height



class I444Buffer(PlanarYuv8Buffer):
    def __init__(self,
                 data: bytearray,
                 width: int,
                 height: int,
                 stride_y: int,
                 stride_u: int,
                 stride_v: int) -> None:
        chroma_width = width
        chroma_height = height
        super().__init__(data, width, height, VideoFrameBufferType.I444,
                         stride_y, stride_u, stride_v, chroma_width, chroma_height)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int) -> int:
        return stride_y * height + stride_u * height + stride_v * height


class I010Buffer(PlanarYuv16Buffer):
    def __init__(self, data: bytearray,
                 width: int,
                 height: int,
                 stride_y: int,
                 stride_u: int,
                 stride_v: int) -> None:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        super().__init__(data, width, height, VideoFrameBufferType.I010,
                         stride_y, stride_u, stride_v, chroma_width, chroma_height)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int) -> int:
        return stride_y * height * 2 + stride_u * ((height + 1) // 2) * 2 + stride_v * ((height + 1) // 2) * 2



class NV12Buffer(BiplanaraYuv8Buffer):
    def __init__(self, data: bytearray,
                 width: int,
                 height: int,
                 stride_y: int,
                 stride_uv: int) -> None:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        super().__init__(data, width, height, VideoFrameBufferType.NV12,
                         stride_y, stride_uv, chroma_width, chroma_height)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_uv: int) -> int:
        return stride_y * height + stride_uv * ((height + 1) // 2)



class ArgbFrame:
    def __init__(self,
                 data: Union[bytes, bytearray, memoryview],
                 format: VideoFormatType.ValueType,
                 width: int,
                 height: int,
                 stride: int = 0) -> None:

        if stride == 0:
            stride = width * ctypes.sizeof(ctypes.c_uint32)

        if len(data) < stride * height:
            raise ValueError("data size does not match stride and height")

        self._data = bytearray(data)
        self._format = format
        self._width = width
        self._height = height
        self._stride = stride

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

    @ property
    def format(self) -> VideoFormatType.ValueType:
        return self._format
