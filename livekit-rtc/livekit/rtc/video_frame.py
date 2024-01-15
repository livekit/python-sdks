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

from ._ffi_client import FfiHandle, FfiClient
from ._proto import ffi_pb2 as proto_ffi
from ._utils import get_address
from ._proto import video_frame_pb2 as proto_video_frame
from ._proto.video_frame_pb2 import VideoFormatType, VideoFrameBufferType, VideoRotation
from abc import ABC, abstractmethod


class VideoFrame:
    def __init__(
        self,
        buffer: "VideoFrameBuffer",
        *,
        timestamp_us: int = 0,
        rotation: VideoRotation.ValueType = VideoRotation.VIDEO_ROTATION_0,
    ) -> None:
        """Creates a new VideoFrame.

        Args:
            buffer: The VideoFrameBuffer to use
            timestamp_us: The timestamp of the frame in microseconds. When it's 0, the framework will use current time
            rotation: Degrees of rotation for the frame, defaults to 0
        """
        self.buffer = buffer
        self.timestamp_us = timestamp_us
        self.rotation = rotation


class VideoFrameBuffer(ABC):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        buffer_type: VideoFrameBufferType.ValueType,
    ) -> None:
        view = memoryview(data)
        if not view.c_contiguous:
            raise ValueError("data must be contiguous")

        self._data = bytearray(data)
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
    def data(self) -> bytearray:
        return self._data

    @property
    def type(self) -> VideoFrameBufferType.ValueType:
        return self._buffer_type

    @abstractmethod
    def _proto_info(self) -> proto_video_frame.VideoFrameBufferInfo:
        pass

    def to_i420(self) -> "I420Buffer":
        req = proto_ffi.FfiRequest()
        req.to_i420.buffer.CopyFrom(self._proto_info())
        resp = FfiClient.instance.request(req)
        return I420Buffer._from_owned_info(resp.to_i420.buffer)

    def to_argb(self, dst: "ArgbFrame") -> None:
        """Convert and copy frame buffer to an RGBA frame at `dst`"""
        req = proto_ffi.FfiRequest()
        req.to_argb.buffer.CopyFrom(self._proto_info())
        req.to_argb.dst_ptr = get_address(memoryview(dst.data))
        req.to_argb.dst_format = dst.format
        req.to_argb.dst_stride = dst.stride
        req.to_argb.dst_width = dst.width
        req.to_argb.dst_height = dst.height
        FfiClient.instance.request(req)

    @staticmethod
    def _from_owned_info(
        owned_info: proto_video_frame.OwnedVideoFrameBuffer,
    ) -> "VideoFrameBuffer":
        """
        Create the right class instance from the VideoFrameBufferInfo
        """

        info = owned_info.info
        if info.buffer_type == VideoFrameBufferType.NATIVE:
            return NativeVideoBuffer._from_owned_info(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I420:
            return I420Buffer._from_owned_info(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I420A:
            return I420ABuffer._from_owned_info(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I422:
            return I422Buffer._from_owned_info(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I444:
            return I444Buffer._from_owned_info(owned_info)
        elif info.buffer_type == VideoFrameBufferType.I010:
            return I010Buffer._from_owned_info(owned_info)
        elif info.buffer_type == VideoFrameBufferType.NV12:
            return NV12Buffer._from_owned_info(owned_info)
        else:
            raise Exception("Unsupported VideoFrameBufferType")


# TODO(theomonnom): Ability to get GPU texture directly
class NativeVideoBuffer(VideoFrameBuffer):
    def __init__(self, owned_info: proto_video_frame.OwnedVideoFrameBuffer) -> None:
        self._info = owned_info.info
        self._ffi_handle = FfiHandle(owned_info.handle.id)
        super().__init__(
            bytearray(),
            self._info.width,
            self._info.height,
            VideoFrameBufferType.NATIVE,
        )

    def _proto_info(self) -> proto_video_frame.VideoFrameBufferInfo:
        return self._info

    @staticmethod
    def _from_owned_info(
        owned_info: proto_video_frame.OwnedVideoFrameBuffer,
    ) -> "NativeVideoBuffer":
        return NativeVideoBuffer(owned_info)

    def to_i420(self) -> "I420Buffer":
        req = proto_ffi.FfiRequest()
        req.to_i420.handle = self._ffi_handle.handle
        resp = FfiClient.instance.request(req)
        return I420Buffer._from_owned_info(resp.to_i420.buffer)

    def to_argb(self, dst: "ArgbFrame") -> None:
        self.to_i420().to_argb(dst)


class PlanarYuvBuffer(VideoFrameBuffer, ABC):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        buffer_type: VideoFrameBufferType.ValueType,
        stride_y: int,
        stride_u: int,
        stride_v: int,
        chroma_width: int,
        chroma_height: int,
    ) -> None:
        super().__init__(data, width, height, buffer_type)
        self._stride_y = stride_y
        self._stride_u = stride_u
        self._stride_v = stride_v
        self._chroma_width = chroma_width
        self._chroma_height = chroma_height

    def _proto_info(self) -> proto_video_frame.VideoFrameBufferInfo:
        info = proto_video_frame.VideoFrameBufferInfo()
        info.width = self.width
        info.height = self.height
        info.yuv.chroma_width = self.chroma_width
        info.yuv.chroma_height = self.chroma_height
        info.buffer_type = self.type
        info.yuv.stride_y = self.stride_y
        info.yuv.stride_u = self.stride_u
        info.yuv.stride_v = self.stride_v
        return info

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
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        buffer_type: VideoFrameBufferType.ValueType,
        stride_y: int,
        stride_u: int,
        stride_v: int,
        chroma_width: int,
        chroma_height: int,
    ) -> None:
        super().__init__(
            data,
            width,
            height,
            buffer_type,
            stride_y,
            stride_u,
            stride_v,
            chroma_width,
            chroma_height,
        )

    def _proto_info(self) -> proto_video_frame.VideoFrameBufferInfo:
        info = super()._proto_info()
        info.yuv.data_y_ptr = get_address(self.data_y)
        info.yuv.data_u_ptr = get_address(self.data_u)
        info.yuv.data_v_ptr = get_address(self.data_v)
        return info

    @property
    def data_y(self) -> memoryview:
        return memoryview(self._data)[0 : self._stride_y * self._height]

    @property
    def data_u(self) -> memoryview:
        return memoryview(self._data)[
            self._stride_y * self._height : self._stride_y * self._height
            + self._stride_u * self._chroma_height
        ]

    @property
    def data_v(self) -> memoryview:
        return memoryview(self._data)[
            self._stride_y * self._height
            + self._stride_u * self._chroma_height : self._stride_y * self._height
            + self._stride_u * self._chroma_height
            + self._stride_v * self._chroma_height
        ]


class PlanarYuv16Buffer(PlanarYuvBuffer, ABC):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        buffer_type: VideoFrameBufferType.ValueType,
        stride_y: int,
        stride_u: int,
        stride_v: int,
        chroma_width: int,
        chroma_height: int,
    ) -> None:
        super().__init__(
            data,
            width,
            height,
            buffer_type,
            stride_y,
            stride_u,
            stride_v,
            chroma_width,
            chroma_height,
        )

    def _proto_info(self) -> proto_video_frame.VideoFrameBufferInfo:
        info = super()._proto_info()
        info.yuv.data_y_ptr = get_address(self.data_y)
        info.yuv.data_u_ptr = get_address(self.data_u)
        info.yuv.data_v_ptr = get_address(self.data_v)
        return info

    @property
    def data_y(self) -> memoryview:
        return memoryview(self._data)[0 : self._stride_y * self._height].cast("H")

    @property
    def data_u(self) -> memoryview:
        return memoryview(self._data)[
            self._stride_y * self._height : self._stride_y * self._height
            + self._stride_u * self._chroma_height
        ].cast("H")

    @property
    def data_v(self) -> memoryview:
        return memoryview(self._data)[
            self._stride_y * self._height
            + self._stride_u * self._chroma_height : self._stride_y * self._height
            + self._stride_u * self._chroma_height
            + self._stride_v * self._chroma_height
        ].cast("H")


class BiplanaraYuv8Buffer(VideoFrameBuffer, ABC):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        buffer_type: VideoFrameBufferType.ValueType,
        stride_y: int,
        stride_uv: int,
        chroma_width: int,
        chroma_height: int,
    ) -> None:
        super().__init__(data, width, height, buffer_type)
        self._stride_y = stride_y
        self._stride_uv = stride_uv
        self._chroma_width = chroma_width
        self._chroma_height = chroma_height

    def _proto_info(self) -> proto_video_frame.VideoFrameBufferInfo:
        info = proto_video_frame.VideoFrameBufferInfo()
        info.width = self._width
        info.height = self._height
        info.bi_yuv.chroma_width = self.chroma_width
        info.bi_yuv.chroma_height = self.chroma_height
        info.buffer_type = self._buffer_type
        info.bi_yuv.stride_y = self._stride_y
        info.bi_yuv.stride_uv = self._stride_uv
        info.bi_yuv.data_y_ptr = get_address(self.data_y)
        info.bi_yuv.data_uv_ptr = get_address(self.data_uv)
        return info

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

    @property
    def data_y(self) -> memoryview:
        return memoryview(self._data)[0 : self._stride_y * self._height]

    @property
    def data_uv(self) -> memoryview:
        return memoryview(self._data)[
            self._stride_y * self._height : self._stride_y * self._height
            + self._stride_uv * self._chroma_height
        ]


class I420Buffer(PlanarYuv8Buffer):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        stride_y: int,
        stride_u: int,
        stride_v: int,
    ) -> None:
        if len(data) < I420Buffer.calc_data_size(height, stride_y, stride_u, stride_v):
            raise ValueError(
                "buffer too small for I420 data. Expected {} bytes, got {}.".format(
                    I420Buffer.calc_data_size(height, stride_y, stride_u, stride_v),
                    len(data),
                )
            )

        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        super().__init__(
            data,
            width,
            height,
            VideoFrameBufferType.I420,
            stride_y,
            stride_u,
            stride_v,
            chroma_width,
            chroma_height,
        )

    @staticmethod
    def _from_owned_info(
        owned_info: proto_video_frame.OwnedVideoFrameBuffer,
    ) -> "I420Buffer":
        info = owned_info.info
        stride_y = info.yuv.stride_y
        stride_u = info.yuv.stride_u
        stride_v = info.yuv.stride_v
        nbytes = I420Buffer.calc_data_size(info.height, stride_y, stride_u, stride_v)
        cdata = (ctypes.c_uint8 * nbytes).from_address(info.yuv.data_y_ptr)
        data = bytearray(cdata)
        FfiHandle(owned_info.handle.id)
        return I420Buffer(data, info.width, info.height, stride_y, stride_u, stride_v)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int) -> int:
        return stride_y * height + (stride_u + stride_v) * ((height + 1) // 2)

    @staticmethod
    def create(width: int, height: int) -> "I420Buffer":
        stride_y = width
        stride_u = (width + 1) // 2
        stride_v = (width + 1) // 2
        data_size = I420Buffer.calc_data_size(height, stride_y, stride_u, stride_v)
        data = bytearray(data_size)
        return I420Buffer(data, width, height, stride_y, stride_u, stride_v)


class I420ABuffer(PlanarYuv8Buffer):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        stride_y: int,
        stride_u: int,
        stride_v: int,
        stride_a: int,
    ) -> None:
        if len(data) < I420ABuffer.calc_data_size(
            height, stride_y, stride_u, stride_v, stride_a
        ):
            raise ValueError(
                "buffer too small for I420A data. Expected {} bytes, got {}.".format(
                    I420ABuffer.calc_data_size(
                        height, stride_y, stride_u, stride_v, stride_a
                    ),
                    len(data),
                )
            )

        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        super().__init__(
            data,
            width,
            height,
            VideoFrameBufferType.I420A,
            stride_y,
            stride_u,
            stride_v,
            chroma_width,
            chroma_height,
        )
        self._stride_a = stride_a

    @staticmethod
    def _from_owned_info(
        owned_info: proto_video_frame.OwnedVideoFrameBuffer,
    ) -> "I420ABuffer":
        info = owned_info.info
        stride_y = info.yuv.stride_y
        stride_u = info.yuv.stride_u
        stride_v = info.yuv.stride_v
        stride_a = info.yuv.stride_a
        cdata = (
            ctypes.c_uint8
            * I420ABuffer.calc_data_size(
                info.height, stride_y, stride_u, stride_v, stride_a
            )
        ).from_address(info.yuv.data_y_ptr)
        data = bytearray(cdata)
        FfiHandle(owned_info.handle.id)
        return I420ABuffer(
            data, info.width, info.height, stride_y, stride_u, stride_v, stride_a
        )

    @staticmethod
    def calc_data_size(
        height: int, stride_y: int, stride_u: int, stride_v: int, stride_a: int
    ) -> int:
        return (stride_y + stride_a) * height + (stride_u + stride_v) * (
            (height + 1) // 2
        )

    @property
    def stride_a(self) -> int:
        return self._stride_a

    @property
    def data_a(self) -> memoryview:
        return memoryview(self._data)[
            self._stride_y * self._height
            + self._stride_u * self._chroma_height
            + self._stride_v * self._chroma_height : self._stride_y * self._height
            + self._stride_u * self._chroma_height
            + self._stride_v * self._chroma_height
            + self._stride_a * self._height
        ]


class I422Buffer(PlanarYuv8Buffer):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        stride_y: int,
        stride_u: int,
        stride_v: int,
    ) -> None:
        if len(data) < I422Buffer.calc_data_size(height, stride_y, stride_u, stride_v):
            raise ValueError(
                "buffer too small for I422 data. Expected {} bytes, got {}.".format(
                    I422Buffer.calc_data_size(height, stride_y, stride_u, stride_v),
                    len(data),
                )
            )

        view = memoryview(data)
        if not view.c_contiguous:
            raise ValueError("data must be contiguous")

        chroma_width = (width + 1) // 2
        chroma_height = height
        super().__init__(
            data,
            width,
            height,
            VideoFrameBufferType.I422,
            stride_y,
            stride_u,
            stride_v,
            chroma_width,
            chroma_height,
        )

    @staticmethod
    def _from_owned_info(
        owned_info: proto_video_frame.OwnedVideoFrameBuffer,
    ) -> "I422Buffer":
        info = owned_info.info
        stride_y = info.yuv.stride_y
        stride_u = info.yuv.stride_u
        stride_v = info.yuv.stride_v
        cdata = (
            ctypes.c_uint8
            * I422Buffer.calc_data_size(info.height, stride_y, stride_u, stride_v)
        ).from_address(info.yuv.data_y_ptr)
        data = bytearray(cdata)
        FfiHandle(owned_info.handle.id)
        return I422Buffer(data, info.width, info.height, stride_y, stride_u, stride_v)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int) -> int:
        return stride_y * height + stride_u * height + stride_v * height


class I444Buffer(PlanarYuv8Buffer):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        stride_y: int,
        stride_u: int,
        stride_v: int,
    ) -> None:
        if len(data) < I444Buffer.calc_data_size(height, stride_y, stride_u, stride_v):
            raise ValueError(
                "buffer too small for I444 data. Expected {} bytes, got {}.".format(
                    I444Buffer.calc_data_size(height, stride_y, stride_u, stride_v),
                    len(data),
                )
            )

        chroma_width = width
        chroma_height = height
        super().__init__(
            data,
            width,
            height,
            VideoFrameBufferType.I444,
            stride_y,
            stride_u,
            stride_v,
            chroma_width,
            chroma_height,
        )

    @staticmethod
    def _from_owned_info(
        owned_info: proto_video_frame.OwnedVideoFrameBuffer,
    ) -> "I444Buffer":
        info = owned_info.info
        stride_y = info.yuv.stride_y
        stride_u = info.yuv.stride_u
        stride_v = info.yuv.stride_v
        cdata = (
            ctypes.c_uint8
            * I444Buffer.calc_data_size(info.height, stride_y, stride_u, stride_v)
        ).from_address(info.yuv.data_y_ptr)
        data = bytearray(cdata)
        FfiHandle(owned_info.handle.id)
        return I444Buffer(data, info.width, info.height, stride_y, stride_u, stride_v)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int) -> int:
        return stride_y * height + stride_u * height + stride_v * height


class I010Buffer(PlanarYuv16Buffer):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        stride_y: int,
        stride_u: int,
        stride_v: int,
    ) -> None:
        if len(data) < I010Buffer.calc_data_size(height, stride_y, stride_u, stride_v):
            raise ValueError(
                "buffer too small for I010 data. Expected {} bytes, got {}.".format(
                    I010Buffer.calc_data_size(height, stride_y, stride_u, stride_v),
                    len(data),
                )
            )

        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        super().__init__(
            data,
            width,
            height,
            VideoFrameBufferType.I010,
            stride_y,
            stride_u,
            stride_v,
            chroma_width,
            chroma_height,
        )

    @staticmethod
    def _from_owned_info(
        owned_info: proto_video_frame.OwnedVideoFrameBuffer,
    ) -> "I010Buffer":
        info = owned_info.info
        stride_y = info.yuv.stride_y
        stride_u = info.yuv.stride_u
        stride_v = info.yuv.stride_v
        cdata = (
            ctypes.c_uint8
            * I010Buffer.calc_data_size(info.height, stride_y, stride_u, stride_v)
        ).from_address(info.yuv.data_y_ptr)
        data = bytearray(cdata)
        FfiHandle(owned_info.handle.id)
        return I010Buffer(data, info.width, info.height, stride_y, stride_u, stride_v)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_u: int, stride_v: int) -> int:
        return (
            stride_y * height * 2
            + stride_u * ((height + 1) // 2) * 2
            + stride_v * ((height + 1) // 2) * 2
        )


class NV12Buffer(BiplanaraYuv8Buffer):
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        width: int,
        height: int,
        stride_y: int,
        stride_uv: int,
    ) -> None:
        if len(data) < NV12Buffer.calc_data_size(height, stride_y, stride_uv):
            raise ValueError(
                "buffer too small for NV12 data. Expected {} bytes, got {}.".format(
                    NV12Buffer.calc_data_size(height, stride_y, stride_uv), len(data)
                )
            )

        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        super().__init__(
            data,
            width,
            height,
            VideoFrameBufferType.NV12,
            stride_y,
            stride_uv,
            chroma_width,
            chroma_height,
        )

    @staticmethod
    def _from_owned_info(
        owned_info: proto_video_frame.OwnedVideoFrameBuffer,
    ) -> "NV12Buffer":
        info = owned_info.info
        stride_y = info.bi_yuv.stride_y
        stride_uv = info.bi_yuv.stride_uv
        cdata = (
            ctypes.c_uint8 * NV12Buffer.calc_data_size(info.height, stride_y, stride_uv)
        ).from_address(info.yuv.data_y_ptr)
        data = bytearray(cdata)
        FfiHandle(owned_info.handle.id)
        return NV12Buffer(data, info.width, info.height, stride_y, stride_uv)

    @staticmethod
    def calc_data_size(height: int, stride_y: int, stride_uv: int) -> int:
        return stride_y * height + stride_uv * ((height + 1) // 2)


class ArgbFrame:
    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        format: VideoFormatType.ValueType,
        width: int,
        height: int,
        stride: int = 0,
    ) -> None:
        """
        Create a new ArgbFrame.

        Args:
            data: The data for the frame. Must be at least width * height * sizeof(uint32) bytes.
            format: The format of the data.
            width: The width of the frame.
            height: The height of the frame.
            stride: The stride of the frame. If 0, the stride will be set to width * sizeof(uint32).
        """

        if stride == 0:
            stride = width * ctypes.sizeof(ctypes.c_uint32)

        if len(data) < stride * height:
            raise ValueError("data size does not match stride and height")

        self._data = bytearray(data)
        self._format = format
        self._width = width
        self._height = height
        self._stride = stride

    @staticmethod
    def create(
        format: VideoFormatType.ValueType, width: int, height: int
    ) -> "ArgbFrame":
        data = bytearray(width * height * ctypes.sizeof(ctypes.c_uint32))
        return ArgbFrame(data, format, width, height)

    def to_i420(self) -> I420Buffer:
        """Converts the frame to an I420 VideoFrameBuffer for use with VideoFrame"""
        req = proto_ffi.FfiRequest()
        req.to_i420.argb.format = self.format
        req.to_i420.argb.width = self.width
        req.to_i420.argb.height = self.height
        req.to_i420.argb.stride = self.stride
        req.to_i420.argb.ptr = get_address(memoryview(self._data))
        res = FfiClient.instance.request(req)
        return I420Buffer._from_owned_info(res.to_i420.buffer)

    @property
    def data(self) -> memoryview:
        return memoryview(self._data)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def stride(self) -> int:
        return self._stride

    @property
    def format(self) -> VideoFormatType.ValueType:
        return self._format
