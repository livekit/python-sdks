from ._ffi_client import (FfiClient, FfiHandle)
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from livekit import (VideoFrame)


class VideoSource:
    def __init__(self):
        req = proto_ffi.FfiRequest()
        req.new_video_source.type = proto_video_frame.VideoSourceType.VIDEO_SOURCE_NATIVE

        ffi_client = FfiClient()
        resp = ffi_client.request(req)
        self._info = resp.new_video_source.source
        self._ffi_handle = FfiHandle(self._info.handle.id)

    def capture_frame(self, frame: VideoFrame):
        req = proto_ffi.FfiRequest()
        req.capture_video_frame.source_handle.id = self._ffi_handle.handle
        req.capture_video_frame.buffer_handle.id = frame.buffer._ffi_handle.handle
        req.capture_video_frame.frame.rotation = frame.rotation
        req.capture_video_frame.frame.timestamp_us = frame.timestamp_us

        ffi_client = FfiClient()
        ffi_client.request(req)
