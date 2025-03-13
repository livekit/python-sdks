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
from ._proto import video_frame_pb2 as proto_video
from ._proto import ffi_pb2 as proto
from typing import List, Optional
from ._ffi_client import FfiClient, FfiHandle
from ._utils import get_address

from typing import Any


class VideoFrame:
    """
    Represents a video frame with associated metadata and pixel data.

    This class provides methods to access video frame properties such as width, height,
    and pixel format, as well as methods for manipulating and converting video frames.
    """

    def __init__(
        self,
        width: int,
        height: int,
        type: proto_video.VideoBufferType.ValueType,
        data: Union[bytes, bytearray, memoryview],
    ) -> None:
        """
        Initializes a new VideoFrame instance.

        Args:
            width (int): The width of the video frame in pixels.
            height (int): The height of the video frame in pixels.
            type (proto_video.VideoBufferType.ValueType): The format type of the video frame data
                (e.g., RGBA, BGRA, RGB24, etc.).
            data (Union[bytes, bytearray, memoryview]): The raw pixel data for the video frame.
        """
        self._width = width
        self._height = height
        self._type = type
        self._data = bytearray(data)

    @property
    def width(self) -> int:
        """
        Returns the width of the video frame in pixels.

        Returns:
            int: The width of the video frame.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        Returns the height of the video frame in pixels.

        Returns:
            int: The height of the video frame.
        """
        return self._height

    @property
    def type(self) -> proto_video.VideoBufferType.ValueType:
        """
        Returns the height of the video frame in pixels.

        Returns:
            int: The height of the video frame.
        """
        return self._type

    @property
    def data(self) -> memoryview:
        """
        Returns a memoryview of the raw pixel data for the video frame.

        Returns:
            memoryview: The raw pixel data of the video frame as a memoryview object.
        """
        return memoryview(self._data)

    @staticmethod
    def _from_owned_info(owned_info: proto_video.OwnedVideoBuffer) -> "VideoFrame":
        info = owned_info.info
        data_len = _get_plane_length(info.type, info.width, info.height)
        cdata = (ctypes.c_uint8 * data_len).from_address(info.data_ptr)
        data = bytearray(cdata)
        frame = VideoFrame(
            width=info.width,
            height=info.height,
            type=info.type,
            data=data,
        )
        FfiHandle(owned_info.handle.id)
        return frame

    def _proto_info(self) -> proto_video.VideoBufferInfo:
        info = proto_video.VideoBufferInfo()
        addr = get_address(self.data)
        info.components.extend(_get_plane_infos(addr, self.type, self.width, self.height))
        info.width = self.width
        info.height = self.height
        info.type = self.type
        info.data_ptr = addr
        info.stride = 0

        if self.type in [
            proto_video.VideoBufferType.ARGB,
            proto_video.VideoBufferType.ABGR,
            proto_video.VideoBufferType.RGBA,
            proto_video.VideoBufferType.BGRA,
        ]:
            info.stride = self.width * 4
        elif self.type == proto_video.VideoBufferType.RGB24:
            info.stride = self.width * 3

        return info

    def get_plane(self, plane_nth: int) -> Optional[memoryview]:
        """
        Returns the memoryview of a specific plane in the video frame, based on its index.

        Some video formats (e.g., I420, NV12) contain multiple planes (Y, U, V channels).
        This method allows access to individual planes by index.

        Args:
            plane_nth (int): The index of the plane to retrieve (starting from 0).

        Returns:
            Optional[memoryview]: A memoryview of the specified plane's data, or None if
            the index is out of bounds for the format.
        """
        plane_infos = _get_plane_infos(get_address(self.data), self.type, self.width, self.height)
        if plane_nth >= len(plane_infos):
            return None

        plane_info = plane_infos[plane_nth]
        cdata = (ctypes.c_uint8 * plane_info.size).from_address(plane_info.data_ptr)
        return memoryview(cdata)

    def convert(
        self, type: proto_video.VideoBufferType.ValueType, *, flip_y: bool = False
    ) -> "VideoFrame":
        """
        Converts the current video frame to a different format type, optionally flipping
        the frame vertically.

        Args:
            type (proto_video.VideoBufferType.ValueType): The target format type to convert to
                (e.g., RGBA, I420).
            flip_y (bool, optional): If True, the frame will be flipped vertically. Defaults to False.

        Returns:
            VideoFrame: A new VideoFrame object in the specified format.

        Raises:
            Exception: If the conversion isn't supported.

        Example:
            Convert a frame from RGBA to I420 format:

            >>> frame = VideoFrame(width=1920, height=1080, type=proto_video.VideoBufferType.RGBA, data=raw_data)
            >>> converted_frame = frame.convert(proto_video.VideoBufferType.I420)
            >>> print(converted_frame.type)
            VideoBufferType.I420

        Example:
            Convert a frame from BGRA to RGB24 format and flip it vertically:

            >>> frame = VideoFrame(width=1280, height=720, type=proto_video.VideoBufferType.BGRA, data=raw_data)
            >>> converted_frame = frame.convert(proto_video.VideoBufferType.RGB24, flip_y=True)
            >>> print(converted_frame.type)
            VideoBufferType.RGB24
            >>> print(converted_frame.width, converted_frame.height)
            1280 720
        """
        req = proto.FfiRequest()
        req.video_convert.flip_y = flip_y
        req.video_convert.dst_type = type
        req.video_convert.buffer.CopyFrom(self._proto_info())
        resp = FfiClient.instance.request(req)
        if resp.video_convert.error:
            raise Exception(resp.video_convert.error)

        return VideoFrame._from_owned_info(resp.video_convert.buffer)

    def __repr__(self) -> str:
        return f"rtc.VideoFrame(width={self.width}, height={self.height}, type={proto_video.VideoBufferType.Name(self.type)})"

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any):
        from pydantic_core import core_schema
        import base64

        def validate_video_frame(value: Any) -> "VideoFrame":
            if isinstance(value, VideoFrame):
                return value

            if isinstance(value, tuple):
                value = value[0]

            if isinstance(value, dict):
                return VideoFrame(
                    width=value["width"],
                    height=value["height"],
                    type=proto_video.VideoBufferType.Value(value["type"]),
                    data=base64.b64decode(value["data"]),
                )

            raise TypeError("Invalid type for VideoFrame")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.model_fields_schema(
                        {
                            "width": core_schema.model_field(core_schema.int_schema()),
                            "height": core_schema.model_field(core_schema.int_schema()),
                            "type": core_schema.model_field(core_schema.str_schema()),
                            "data": core_schema.model_field(core_schema.str_schema()),
                        },
                    ),
                    core_schema.no_info_plain_validator_function(validate_video_frame),
                ]
            ),
            python_schema=core_schema.no_info_plain_validator_function(validate_video_frame),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: {
                    "width": instance.width,
                    "height": instance.height,
                    "type": proto_video.VideoBufferType.Name(instance.type),
                    "data": base64.b64encode(instance.data).decode("utf-8"),
                }
            ),
        )


def _component_info(
    data_ptr: int, stride: int, size: int
) -> proto_video.VideoBufferInfo.ComponentInfo:
    cmpt = proto_video.VideoBufferInfo.ComponentInfo()
    cmpt.data_ptr = data_ptr
    cmpt.stride = stride
    cmpt.size = size
    return cmpt


def _get_plane_length(type: proto_video.VideoBufferType.ValueType, width: int, height: int) -> int:
    """
    Return the size in bytes of a participant video buffer type based on its size (This ignores the strides)
    """
    if type in [
        proto_video.VideoBufferType.ARGB,
        proto_video.VideoBufferType.ABGR,
        proto_video.VideoBufferType.RGBA,
        proto_video.VideoBufferType.BGRA,
    ]:
        return width * height * 4
    elif type == proto_video.VideoBufferType.RGB24:
        return width * height * 3
    elif type == proto_video.VideoBufferType.I420:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        return width * height + chroma_width * chroma_height * 2
    elif type == proto_video.VideoBufferType.I420A:
        chroma_width = (width + 1) // 2
        return width * height * 2 + chroma_width * chroma_width * 2
    elif type == proto_video.VideoBufferType.I422:
        chroma_width = (width + 1) // 2
        return width * height + chroma_width * height * 2
    elif type == proto_video.VideoBufferType.I444:
        return width * height * 3
    elif type == proto_video.VideoBufferType.I010:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        return width * height * 2 + chroma_width * chroma_height * 4
    elif type == proto_video.VideoBufferType.NV12:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        return width * height + chroma_width * chroma_width * 2

    raise Exception(f"unsupported video buffer type: {type}")


def _get_plane_infos(
    addr: int, type: proto_video.VideoBufferType.ValueType, width: int, height: int
) -> List[proto_video.VideoBufferInfo.ComponentInfo]:
    if type == proto_video.VideoBufferType.I420:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        y = _component_info(addr, width, width * height)
        u = _component_info(y.data_ptr + y.size, chroma_width, chroma_width * chroma_height)
        v = _component_info(u.data_ptr + u.size, chroma_width, chroma_width * chroma_height)
        return [y, u, v]
    elif type == proto_video.VideoBufferType.I420A:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        y = _component_info(addr, width, width * height)
        u = _component_info(y.data_ptr + y.size, chroma_width, chroma_width * chroma_height)
        v = _component_info(u.data_ptr + u.size, chroma_width, chroma_width * chroma_height)
        a = _component_info(v.data_ptr + v.size, width, width * height)
        return [y, u, v, a]
    elif type == proto_video.VideoBufferType.I422:
        chroma_width = (width + 1) // 2
        y = _component_info(addr, width, width * height)
        u = _component_info(y.data_ptr + y.size, chroma_width, chroma_width * height)
        v = _component_info(u.data_ptr + u.size + u.size, chroma_width, chroma_width * height)
        return [y, u, v]
    elif type == proto_video.VideoBufferType.I444:
        y = _component_info(addr, width, width * height)
        u = _component_info(y.data_ptr + y.size, width, width * height)
        v = _component_info(u.data_ptr + u.size, width, width * height)
        return [y, u, v]
    elif type == proto_video.VideoBufferType.I010:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        y = _component_info(addr, width * 2, width * height * 2)
        u = _component_info(y.data_ptr + y.size, chroma_width * 2, chroma_width * chroma_height * 2)
        v = _component_info(u.data_ptr + u.size, chroma_width * 2, chroma_width * chroma_height * 2)
        return [y, u, v]
    elif type == proto_video.VideoBufferType.NV12:
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
        y = _component_info(addr, width, width * height)
        uv = _component_info(
            y.data_ptr + y.size, chroma_width * 2, chroma_width * chroma_height * 2
        )
        return [y, uv]

    return []
