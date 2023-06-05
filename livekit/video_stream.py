from pyee.asyncio import AsyncIOEventEmitter
from ._ffi_client import (FfiClient, FfiHandle)
from livekit import (Track, Room, Participant)
from ._proto import track_pb2 as proto_track
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from .video_frame import (VideoFrame, VideoFrameBuffer)


class VideoStream(AsyncIOEventEmitter):
    _streams: dict[int, 'VideoStream'] = {}
    _initialized = False

    @classmethod
    def initalize(cls):
        if cls._initialized:
            return

        cls._initialized = True
        ffi_client = FfiClient()
        ffi_client.add_listener('video_stream_event',
                                cls._on_video_stream_event)

    @classmethod
    def _on_video_stream_event(cls, event: proto_video_frame.VideoStreamEvent):
        stream = cls._streams.get(event.handle.id)
        if stream is None:
            return

        which = event.WhichOneof('message')
        if which == 'frame_received':
            frame_info = event.frame_received.frame
            buffer_info = event.frame_received.buffer
            ffi_handle = FfiHandle(buffer_info.handle.id)

            frame = VideoFrame(frame_info)
            buffer = VideoFrameBuffer.create(ffi_handle, buffer_info)
            stream._on_frame_received(frame, buffer)

    def __init__(self, track: Track):
        super().__init__()
        self.initalize()

        room = track._room()
        if room is None:
            raise ValueError("track's room is not valid anymore")

        participant = track._participant()
        if participant is None:
            raise ValueError("track's participant is not valid anymore")

        req = proto_ffi.FfiRequest()
        new_video_stream = req.new_video_stream
        new_video_stream.room_handle.id = room._ffi_handle.handle
        new_video_stream.track_sid = track.sid
        new_video_stream.participant_sid = participant.sid
        new_video_stream.type = proto_video_frame.VideoStreamType.VIDEO_STREAM_NATIVE

        ffi_client = FfiClient()
        resp = ffi_client.request(req)
        stream_info = resp.new_video_stream.stream

        self._streams[stream_info.handle.id] = self
        self._ffi_handle = FfiHandle(stream_info.handle.id)
        self._info = stream_info
        self._track = track

    def _on_frame_received(self, frame: VideoFrame, buffer: VideoFrameBuffer):
        self.emit('frame_received', frame, buffer)

    def __del__(self):
        self._streams.pop(self._ffi_handle.handle, None)
