from pyee.asyncio import AsyncIOEventEmitter
from ._ffi_client import (FfiClient, FfiHandle)
from livekit import Track
from ._proto import ffi_pb2 as proto_ffi
from ._proto import audio_frame_pb2 as proto_audio_frame
from .audio_frame import AudioFrame
import ctypes
import weakref


class AudioStream(AsyncIOEventEmitter):
    _streams: dict[int, weakref.ref['AudioStream']] = {}
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
    def _on_audio_stream_event(cls, event: proto_audio_frame.AudioStreamEvent):
        stream = cls._streams.get(event.handle.id)
        if stream is None:
            return

        stream = stream()
        if stream is None:
            return

        which = event.WhichOneof('message')
        if which == 'frame_received':
            frame_info = event.frame_received.frame
            ffi_handle = FfiHandle(frame_info.handle.id)
            frame = AudioFrame(frame_info, ffi_handle)
            stream._on_frame_received(frame)

    def __init__(self, track: Track):
        super().__init__()
        self.initalize()

        req = proto_ffi.FfiRequest()
        new_audio_stream = req.new_audio_stream
        new_audio_stream.track_handle.id = track._ffi_handle.handle
        new_audio_stream.type = proto_audio_frame.AudioStreamType.AUDIO_STREAM_NATIVE

        ffi_client = FfiClient()
        resp = ffi_client.request(req)
        stream_info = resp.new_audio_stream.stream

        self._streams[stream_info.handle.id] = weakref.ref(self)
        self._ffi_handle = FfiHandle(stream_info.handle.id)
        self._info = stream_info
        self._track = track

    def _on_frame_received(self, frame: AudioFrame):
        self.emit('frame_received', frame)

    def __del__(self):
        self._streams.pop(self._ffi_handle.handle, None)
