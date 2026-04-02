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

from dataclasses import dataclass
from typing import AsyncIterator, Optional

from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._proto import data_track_pb2 as proto_data_track


class SubscribeDataTrackError(Exception):
    """An error that can occur when subscribing to a data track."""

    def __init__(self, message: str) -> None:
        self.message = message


class PushFrameError(Exception):
    """Frame could not be pushed to a data track.

    Pushing a frame can fail for several reasons:

    - The track has been unpublished by the local participant or SFU
    - The room is no longer connected
    - Frames are being pushed too fast
    """

    def __init__(self, message: str) -> None:
        self.message = message


@dataclass
class DataTrackInfo:
    """Information about a published data track."""

    sid: str
    """Unique track identifier assigned by the SFU.

    This identifier may change if a reconnect occurs. Use ``name`` if a
    stable identifier is needed.
    """

    name: str
    """Name of the track assigned by the publisher."""

    uses_e2ee: bool
    """Whether or not frames sent on the track use end-to-end encryption."""


@dataclass
class DataTrackFrame:
    """A frame published on a data track, consisting of a payload and optional metadata."""

    payload: bytes
    """The frame's payload."""

    user_timestamp: Optional[int] = None
    """The frame's user timestamp, if one is associated."""


class LocalDataTrack:
    """Data track published by the local participant."""

    def __init__(self, owned_info: proto_data_track.OwnedLocalDataTrack) -> None:
        self._info = DataTrackInfo(
            sid=owned_info.info.sid,
            name=owned_info.info.name,
            uses_e2ee=owned_info.info.uses_e2ee,
        )
        self._ffi_handle = FfiHandle(owned_info.handle.id)

    @property
    def info(self) -> DataTrackInfo:
        """Information about the data track."""
        return self._info

    def try_push(self, frame: DataTrackFrame) -> None:
        """Try pushing a frame to subscribers of the track.

        See :class:`DataTrackFrame` for how to construct a frame and attach metadata.

        Args:
            frame: The data track frame to send.

        Raises:
            PushFrameError: If the push fails.
        """
        proto_frame = proto_data_track.DataTrackFrame(payload=bytes(frame.payload))
        if frame.user_timestamp is not None:
            proto_frame.user_timestamp = frame.user_timestamp

        req = proto_ffi.FfiRequest()
        req.local_data_track_try_push.track_handle = self._ffi_handle.handle
        req.local_data_track_try_push.frame.CopyFrom(proto_frame)

        resp = FfiClient.instance.request(req)
        if resp.local_data_track_try_push.HasField("error"):
            raise PushFrameError(resp.local_data_track_try_push.error.message)

    def is_published(self) -> bool:
        """Whether or not the track is still published."""
        req = proto_ffi.FfiRequest()
        req.local_data_track_is_published.track_handle = self._ffi_handle.handle

        resp = FfiClient.instance.request(req)
        return resp.local_data_track_is_published.is_published

    async def unpublish(self) -> None:
        """Unpublishes the track."""
        req = proto_ffi.FfiRequest()
        req.local_data_track_unpublish.track_handle = self._ffi_handle.handle
        FfiClient.instance.request(req)

    def __repr__(self) -> str:
        return f"rtc.LocalDataTrack(sid={self._info.sid}, name={self._info.name})"


class RemoteDataTrack:
    """Data track published by a remote participant."""

    def __init__(self, owned_info: proto_data_track.OwnedRemoteDataTrack) -> None:
        self._info = DataTrackInfo(
            sid=owned_info.info.sid,
            name=owned_info.info.name,
            uses_e2ee=owned_info.info.uses_e2ee,
        )
        self._ffi_handle = FfiHandle(owned_info.handle.id)
        self._publisher_identity = owned_info.publisher_identity

    @property
    def info(self) -> DataTrackInfo:
        """Information about the data track."""
        return self._info

    @property
    def publisher_identity(self) -> str:
        """Identity of the participant who published the track."""
        return self._publisher_identity

    def subscribe(self, *, buffer_size: Optional[int] = None) -> DataTrackStream:
        """Subscribes to the data track to receive frames.

        Args:
            buffer_size: Maximum number of received frames to buffer internally.
                When ``None``, the default buffer size is used.
                Zero is not a valid buffer size; if a value of zero is provided, it will be clamped to one.

        Returns a :class:`DataTrackStream` that yields
        :class:`DataTrackFrame` instances as they arrive. If the
        subscription encounters an error, it is raised as
        :class:`SubscribeDataTrackError` when iteration ends.
        """
        opts = proto_data_track.DataTrackSubscribeOptions()
        if buffer_size is not None:
            opts.buffer_size = buffer_size

        req = proto_ffi.FfiRequest()
        req.subscribe_data_track.track_handle = self._ffi_handle.handle
        req.subscribe_data_track.options.CopyFrom(opts)

        resp = FfiClient.instance.request(req)
        return DataTrackStream(resp.subscribe_data_track.stream)

    def is_published(self) -> bool:
        """Whether or not the track is still published."""
        req = proto_ffi.FfiRequest()
        req.remote_data_track_is_published.track_handle = self._ffi_handle.handle

        resp = FfiClient.instance.request(req)
        return resp.remote_data_track_is_published.is_published

    def __repr__(self) -> str:
        return (
            f"rtc.RemoteDataTrack(sid={self._info.sid}, name={self._info.name}, "
            f"publisher_identity={self._publisher_identity})"
        )


class DataTrackStream:
    """An active subscription to a remote data track.

    Use as an async iterator to receive frames::

        stream = remote_track.subscribe()
        async for frame in stream:
            process(frame.payload)

    Dropping or closing the stream unsubscribes from the track.

    If subscribing to the track fails, :class:`SubscribeDataTrackError`
    is raised when iteration ends instead of a normal ``StopAsyncIteration``.
    """

    def __init__(self, owned_info: proto_data_track.OwnedDataTrackStream) -> None:
        self._ffi_handle = FfiHandle(owned_info.handle.id)
        handle_id = owned_info.handle.id

        self._queue = FfiClient.instance.queue.subscribe(
            filter_fn=lambda e: (
                e.WhichOneof("message") == "data_track_stream_event"
                and e.data_track_stream_event.stream_handle == handle_id
            ),
        )
        self._closed = False

    async def read(self) -> Optional[DataTrackFrame]:
        """Read a single frame, or ``None`` if the stream has ended."""
        try:
            return await self.__anext__()
        except StopAsyncIteration:
            return None

    def __aiter__(self) -> AsyncIterator[DataTrackFrame]:
        return self

    async def __anext__(self) -> DataTrackFrame:
        if self._closed:
            raise StopAsyncIteration

        self._send_read_request()
        event: proto_ffi.FfiEvent = await self._queue.get()
        stream_event = event.data_track_stream_event
        detail = stream_event.WhichOneof("detail")

        if detail == "frame_received":
            proto_frame = stream_event.frame_received.frame
            user_ts: Optional[int] = None
            if proto_frame.HasField("user_timestamp"):
                user_ts = proto_frame.user_timestamp
            return DataTrackFrame(
                payload=proto_frame.payload,
                user_timestamp=user_ts,
            )
        elif detail == "eos":
            self._close()
            if stream_event.eos.HasField("error"):
                raise SubscribeDataTrackError(stream_event.eos.error)
            raise StopAsyncIteration
        else:
            self._close()
            raise StopAsyncIteration

    def _send_read_request(self) -> None:
        req = proto_ffi.FfiRequest()
        req.data_track_stream_read.stream_handle = self._ffi_handle.handle
        FfiClient.instance.request(req)

    def _close(self) -> None:
        if not self._closed:
            self._closed = True
            FfiClient.instance.queue.unsubscribe(self._queue)

    def close(self) -> None:
        """Explicitly close the subscription and unsubscribe."""
        self._close()
        self._ffi_handle.dispose()

    async def aclose(self) -> None:
        self.close()
