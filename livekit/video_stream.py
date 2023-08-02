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

from weakref import WeakValueDictionary

from pyee.asyncio import EventEmitter

from ._ffi_client import FfiHandle, ffi_client
from ._proto import ffi_pb2 as proto_ffi
from ._proto import video_frame_pb2 as proto_video_frame
from .track import Track
from .video_frame import VideoFrame, VideoFrameBuffer


class VideoStream(EventEmitter):
    _streams: WeakValueDictionary[int, 'VideoStream'] = WeakValueDictionary()
    _initialized = False

    @classmethod
    def initalize(cls) -> None:
        if cls._initialized:
            return

        cls._initialized = True

        # Not using the instance method the listener because it keeps a strong reference
        # to the instance.
        # And we rely on __del__ to determine when the instance isn't used
        ffi_client.add_listener('video_stream_event',
                                cls._on_video_stream_event)

    @classmethod
    def _on_video_stream_event(cls, event: proto_video_frame.VideoStreamEvent) -> None:
        stream = cls._streams.get(event.stream_handle)
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

    def __init__(self, track: Track) -> None:
        super().__init__()
        self.__class__.initalize()

        req = proto_ffi.FfiRequest()
        new_video_stream = req.new_video_stream
        new_video_stream.track_handle = track._ffi_handle.handle
        new_video_stream.type = proto_video_frame.VideoStreamType.VIDEO_STREAM_NATIVE

        resp = ffi_client.request(req)
        stream_info = resp.new_video_stream.stream

        self._streams[stream_info.handle.id] = self
        self._ffi_handle = FfiHandle(stream_info.handle.id)
        self._info = stream_info
        self._track = track

    def _on_frame_received(self, frame: VideoFrame) -> None:
        self.emit('frame_received', frame)

    def __del__(self) -> None:
        self._streams.pop(self._ffi_handle.handle, None)
