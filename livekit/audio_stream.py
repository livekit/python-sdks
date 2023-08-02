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
from ._proto import audio_frame_pb2 as proto_audio_frame
from ._proto import ffi_pb2 as proto_ffi
from .audio_frame import AudioFrame
from .track import Track


class AudioStream(EventEmitter):
    _streams: WeakValueDictionary[int, 'AudioStream'] = WeakValueDictionary()
    _initialized = False

    @classmethod
    def initalize(cls) -> None:
        if cls._initialized:
            return

        cls._initialized = True
        # See VideoStream for the reason we don't use the instance method for the listener
        ffi_client.add_listener('audio_stream_event',
                                cls._on_audio_stream_event)

    @classmethod
    def _on_audio_stream_event(cls, event: proto_audio_frame.AudioStreamEvent) -> None:
        stream = cls._streams.get(event.source_handle)
        if stream is None:
            return

        which = event.WhichOneof('message')
        if which == 'frame_received':
            frame_info = event.frame_received.frame
            ffi_handle = FfiHandle(frame_info.handle.id)
            frame = AudioFrame(frame_info, ffi_handle)
            stream._on_frame_received(frame)

    def __init__(self, track: Track) -> None:
        super().__init__()
        self.__class__.initalize()

        req = proto_ffi.FfiRequest()
        new_audio_stream = req.new_audio_stream
        new_audio_stream.track_handle = track._ffi_handle.handle
        new_audio_stream.type = proto_audio_frame.AudioStreamType.AUDIO_STREAM_NATIVE

        resp = ffi_client.request(req)
        stream_info = resp.new_audio_stream.stream

        self._streams[stream_info.handle.id] = self
        self._ffi_handle = FfiHandle(stream_info.handle.id)
        self._info = stream_info
        self._track = track

    def _on_frame_received(self, frame: AudioFrame) -> None:
        self.emit('frame_received', frame)

    def __del__(self):
        self._streams.pop(self._ffi_handle.handle, None)
