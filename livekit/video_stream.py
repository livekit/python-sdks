from pyee.asyncio import AsyncIOEventEmitter
from ._ffi_client import (FfiClient, FfiHandle)
from livekit import (Track, Room, Participant)
from ._proto import track_pb2 as proto_track
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from .video_frame import (VideoFrame, VideoFrameBuffer)
import weakref


class VideoStream(AsyncIOEventEmitter):
    _streams: dict[int, weakref.ref['VideoStream']] = {}
    _initialized = False

    @classmethod
    def initalize(cls):
        if cls._initialized:
            return

        cls._initialized = True
        ffi_client = FfiClient()
        # Not using the instance method the listener because it keeps a strong reference to the instance
        # And we rely on __del__ to determine when the instance isn't used
        ffi_client.add_listener('video_stream_event',
                                cls._on_video_stream_event)

    @classmethod
    def _on_video_stream_event(cls, event: proto_video_frame.VideoStreamEvent):
        stream = cls._streams.get(event.handle.id)
        if stream is None:
            return

        stream = stream()
        if stream is None:
            return

        which = event.WhichOneof('message')
        if which == 'frame_received':
            frame_info = event.frame_received.frame
            buffer_info = event.frame_received.buffer
            ffi_handle = FfiHandle(buffer_info.handle.id)

            frame = VideoFrame(frame_info.timestamp_us, frame_info.rotation,
                               VideoFrameBuffer.create(ffi_handle, buffer_info))
            stream._on_frame_received(frame)

    def __init__(self, track: Track):
        super().__init__()
        self.initalize()

        req = proto_ffi.FfiRequest()
        new_video_stream = req.new_video_stream
        new_video_stream.track_handle.id = track._ffi_handle.handle
        new_video_stream.type = proto_video_frame.VideoStreamType.VIDEO_STREAM_NATIVE

        ffi_client = FfiClient()
        resp = ffi_client.request(req)
        stream_info = resp.new_video_stream.stream

        self._streams[stream_info.handle.id] = weakref.ref(self)
        self._ffi_handle = FfiHandle(stream_info.handle.id)
        self._info = stream_info
        self._track = track

    def _on_frame_received(self, frame: VideoFrame):
        self.emit('frame_received', frame)

    def __del__(self):
        self._streams.pop(self._ffi_handle.handle, None)
