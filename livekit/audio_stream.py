from pyee.asyncio import AsyncIOEventEmitter
from ._ffi_client import (FfiClient, FfiHandle)
from livekit import (Track, Room, Participant)
from ._proto import track_pb2 as proto_track
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from .video_frame import (VideoFrame, VideoFrameBuffer)


class AudioStream(AsyncIOEventEmitter):
    _streams: dict[int, 'AudioStream'] = {}
    _initialized = False

    @classmethod
    def initalize(cls):
        if cls._initialized:
            return

        cls._initialized = True
        ffi_client = FfiClient()
        # See VideoStream for the reason we don't use the instance method for the listener
        ffi_client.add_listener('audio_stream_event',
                                cls._on_audio_stream_event)

    @classmethod
    def _on_audio_stream_event(cls, event: proto_video_frame.AudioStreamEvent):
        pass

    def __init__(self, track: Track):
        super().__init__()
        self.initalize()
