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

import weakref
from typing import TYPE_CHECKING, List, Optional, Union
from ._ffi_client import FfiHandle, FfiClient
from ._proto import ffi_pb2 as proto_ffi
from ._proto import track_pb2 as proto_track
from ._proto import stats_pb2 as proto_stats

if TYPE_CHECKING:
    from .audio_source import AudioSource
    from .audio_stream import AudioStream
    from .room import Room
    from .video_source import VideoSource
    from .platform_audio import PlatformAudioSource


class Track:
    def __init__(self, owned_info: proto_track.OwnedTrack):
        self._info = owned_info.info
        self._ffi_handle = FfiHandle(owned_info.handle.id)
        self._room_ref: Optional[weakref.ref[Room]] = None
        self._audio_streams: weakref.WeakSet[AudioStream] = weakref.WeakSet()

    def _resolve_room(self) -> Optional[Room]:
        return self._room_ref() if self._room_ref is not None else None

    def _set_room(self, room: Optional[Room]) -> None:
        old_room = self._resolve_room()
        if old_room is None and room is None:
            # Already roomless — nothing to detach and nothing to re-clear.
            # Without this guard a second _set_room(None) (e.g. the unpublish /
            # local_track_unpublished race calling it from both paths) would
            # re-fire _on_*_cleared on every registered processor.
            return
        if old_room is not room:
            if old_room is not None:
                old_room.off("token_refreshed", self._on_room_token_refreshed)
            if room is not None:
                room.on("token_refreshed", self._on_room_token_refreshed)

        self._room_ref = weakref.ref(room) if room is not None else None

        for stream in self._audio_streams:
            self._push_processor_metadata_to_stream(stream, room)

    def _on_room_token_refreshed(self) -> None:
        room = self._resolve_room()
        if room is None or room._token is None or room._server_url is None:
            return
        for stream in self._audio_streams:
            if not stream._processor:
                continue
            stream._processor._on_credentials_updated(token=room._token, url=room._server_url)

    def _push_processor_metadata_to_stream(self, stream: AudioStream, room: Optional[Room]) -> None:
        if not stream._processor:
            return

        if room is None:
            # track left a room - clear processor's room context
            stream._processor._on_stream_info_cleared()
            stream._processor._on_credentials_cleared()
            return

        identity = ""
        pub_sid = ""
        track_sid = self.sid
        if track_sid:
            for participant in room.remote_participants.values():
                publication = participant.track_publications.get(track_sid)
                if publication is not None:
                    identity, pub_sid = participant.identity, publication.sid
                    break
            else:
                local = room._local_participant
                if local is not None:
                    for local_publication in local.track_publications.values():
                        if local_publication.sid == track_sid:
                            identity, pub_sid = local.identity, local_publication.sid
                            break

        stream._processor._on_stream_info_updated(
            room_name=room.name,
            participant_identity=identity,
            publication_sid=pub_sid,
        )
        if room._token is not None and room._server_url is not None:
            stream._processor._on_credentials_updated(token=room._token, url=room._server_url)

    def _register_audio_stream(self, stream: AudioStream) -> None:
        self._audio_streams.add(stream)
        room = self._resolve_room()
        if room is not None:
            self._push_processor_metadata_to_stream(stream, room)

    def _unregister_audio_stream(self, stream: AudioStream) -> None:
        self._audio_streams.discard(stream)

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
    def __init__(self, info: proto_track.OwnedTrack):
        super().__init__(info)

    @staticmethod
    def create_audio_track(
        name: str, source: Union["AudioSource", "PlatformAudioSource"]
    ) -> "LocalAudioTrack":
        """Create a local audio track from an audio source.

        Args:
            name: The name of the track (e.g., "microphone", "audio-file").
            source: Either an AudioSource (synthetic mode for manual frame capture)
                or a PlatformAudioSource (from PlatformAudio, uses WebRTC ADM).

        Returns:
            A LocalAudioTrack that can be published to a room.

        Example with PlatformAudio (recommended for most use cases):
            ```python
            platform_audio = rtc.PlatformAudio()
            source = platform_audio.create_audio_source()
            track = rtc.LocalAudioTrack.create_audio_track("microphone", source)
            ```

        Example with AudioSource (synthetic mode for custom processing):
            ```python
            # Synthetic mode: You must manually capture frames
            source = rtc.AudioSource(sample_rate=48000, num_channels=1)
            track = rtc.LocalAudioTrack.create_audio_track("audio", source)
            # Then in a loop: await source.capture_frame(frame)
            ```
        """
        req = proto_ffi.FfiRequest()
        req.create_audio_track.name = name
        req.create_audio_track.source_handle = source._ffi_handle.handle

        resp = FfiClient.instance.request(req)
        return LocalAudioTrack(resp.create_audio_track.track)

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
