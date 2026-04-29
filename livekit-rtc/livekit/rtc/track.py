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

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, List, Union

from ._ffi_client import FfiHandle, FfiClient
from ._proto import ffi_pb2 as proto_ffi
from ._proto import track_pb2 as proto_track
from ._proto import stats_pb2 as proto_stats

if TYPE_CHECKING:
    from .audio_ring_buffer import AudioRingBuffer
    from .audio_source import AudioSource
    from .participant import LocalParticipant
    from .video_source import VideoSource

PRE_CONNECT_AUDIO_BUFFER_TOPIC = "lk.agent.pre-connect-audio-buffer"


class Track:
    def __init__(self, owned_info: proto_track.OwnedTrack):
        self._info = owned_info.info
        self._ffi_handle = FfiHandle(owned_info.handle.id)

    @property
    def sid(self) -> str:
        return self._info.sid

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def kind(self) -> proto_track.TrackKind.ValueType:
        return self._info.kind

    @property
    def stream_state(self) -> proto_track.StreamState.ValueType:
        return self._info.stream_state

    @property
    def muted(self) -> bool:
        return self._info.muted

    async def get_stats(self) -> List[proto_stats.RtcStats]:
        req = proto_ffi.FfiRequest()
        req.get_stats.track_handle = self._ffi_handle.handle

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.get_stats.async_id == resp.get_stats.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.get_stats.error:
            raise Exception(cb.get_stats.error)

        return list(cb.get_stats.stats)


class LocalAudioTrack(Track):
    def __init__(self, info: proto_track.OwnedTrack, source: AudioSource | None = None):
        super().__init__(info)
        self._source = source
        self._preconnect_buffer: AudioRingBuffer | None = None
        self._participant: LocalParticipant | None = None
        self._publication_sid: str | None = None
        self._send_lock = asyncio.Lock()

    @staticmethod
    def create_audio_track(name: str, source: AudioSource) -> LocalAudioTrack:
        req = proto_ffi.FfiRequest()
        req.create_audio_track.name = name
        req.create_audio_track.source_handle = source._ffi_handle.handle

        resp = FfiClient.instance.request(req)
        return LocalAudioTrack(resp.create_audio_track.track, source=source)

    @property
    def has_preconnect_buffer(self) -> bool:
        return self._preconnect_buffer is not None

    def start_preconnect_buffer(self, *, max_duration: float = 10.0) -> None:
        if self._source is None:
            raise RuntimeError("track has no audio source")

        from .audio_ring_buffer import AudioRingBuffer

        self._preconnect_buffer = AudioRingBuffer(
            max_duration=max_duration,
            sample_rate=self._source.sample_rate,
            num_channels=self._source.num_channels,
        )
        self._source._set_preconnect_buffer(self._preconnect_buffer)

    def stop_preconnect_buffer(self) -> None:
        if self._source is not None:
            self._source._set_preconnect_buffer(None)
        self._preconnect_buffer = None

    async def send_preconnect_buffer(self, *, destination_identity: str) -> None:
        if self._participant is None:
            raise RuntimeError("track is not published")
        if self._preconnect_buffer is None:
            raise RuntimeError("preconnect buffer is not active")

        async with self._send_lock:
            data = self._preconnect_buffer.capture()
            if not data:
                return

            assert self._source is not None
            writer = await self._participant.stream_bytes(
                "preconnect-buffer",
                topic=PRE_CONNECT_AUDIO_BUFFER_TOPIC,
                mime_type="application/octet-stream",
                destination_identities=[destination_identity],
                attributes={
                    "trackId": self._publication_sid or self.sid,
                    "sampleRate": str(self._source.sample_rate),
                    "channels": str(self._source.num_channels),
                },
            )

            await writer.write(data)
            await writer.aclose()

    def mute(self) -> None:
        req = proto_ffi.FfiRequest()
        req.local_track_mute.track_handle = self._ffi_handle.handle
        req.local_track_mute.mute = True
        FfiClient.instance.request(req)
        self._info.muted = True

    def unmute(self) -> None:
        req = proto_ffi.FfiRequest()
        req.local_track_mute.track_handle = self._ffi_handle.handle
        req.local_track_mute.mute = False
        FfiClient.instance.request(req)
        self._info.muted = False

    def __repr__(self) -> str:
        return f"rtc.LocalAudioTrack(sid={self.sid}, name={self.name})"


class LocalVideoTrack(Track):
    def __init__(self, info: proto_track.OwnedTrack):
        super().__init__(info)

    @staticmethod
    def create_video_track(name: str, source: "VideoSource") -> "LocalVideoTrack":
        req = proto_ffi.FfiRequest()
        req.create_video_track.name = name
        req.create_video_track.source_handle = source._ffi_handle.handle

        resp = FfiClient.instance.request(req)
        return LocalVideoTrack(resp.create_video_track.track)

    def mute(self):
        req = proto_ffi.FfiRequest()
        req.local_track_mute.track_handle = self._ffi_handle.handle
        req.local_track_mute.mute = True
        FfiClient.instance.request(req)
        self._info.muted = True

    def unmute(self):
        req = proto_ffi.FfiRequest()
        req.local_track_mute.track_handle = self._ffi_handle.handle
        req.local_track_mute.mute = False
        FfiClient.instance.request(req)
        self._info.muted = False

    def __repr__(self) -> str:
        return f"rtc.LocalVideoTrack(sid={self.sid}, name={self.name})"


class RemoteAudioTrack(Track):
    def __init__(self, info: proto_track.OwnedTrack):
        super().__init__(info)

    def __repr__(self) -> str:
        return f"rtc.RemoteAudioTrack(sid={self.sid}, name={self.name})"


class RemoteVideoTrack(Track):
    def __init__(self, info: proto_track.OwnedTrack):
        super().__init__(info)

    def __repr__(self) -> str:
        return f"rtc.RemoteVideoTrack(sid={self.sid}, name={self.name})"


LocalTrack = Union[LocalVideoTrack, LocalAudioTrack]
RemoteTrack = Union[RemoteVideoTrack, RemoteAudioTrack]
AudioTrack = Union[LocalAudioTrack, RemoteAudioTrack]
VideoTrack = Union[LocalVideoTrack, RemoteVideoTrack]
