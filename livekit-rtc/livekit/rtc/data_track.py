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
    def __init__(self, message: str) -> None:
        self.message = message


class PushFrameError(Exception):
    """Frame could not be pushed to a data track."""

    def __init__(self, message: str) -> None:
        self.message = message


@dataclass
class DataTrackInfo:
    """Metadata about a data track."""

    sid: str
    name: str
    uses_e2ee: bool


@dataclass
class DataTrackOptions:
    """Options for publishing a data track."""

    name: str
    """Track name used to identify the track to other participants.

    Must not be empty and must be unique per publisher.
    """


@dataclass
class DataTrackFrame:
    """A frame published on a data track, consisting of a payload and optional metadata."""

    payload: bytes
    user_timestamp: Optional[int] = None


class LocalDataTrack:
    """A locally published data track that can push frames to subscribers."""

    def __init__(self, owned_info: proto_data_track.OwnedLocalDataTrack) -> None:
        self._info = DataTrackInfo(
            sid=owned_info.info.sid,
            name=owned_info.info.name,
            uses_e2ee=owned_info.info.uses_e2ee,
        )
        self._ffi_handle = FfiHandle(owned_info.handle.id)

    @property
    def info(self) -> DataTrackInfo:
        return self._info

    def try_push(self, frame: DataTrackFrame) -> None:
        """Push a frame to subscribers of this track.

        Args:
            frame: The data track frame to send.

        Raises:
            PushFrameError: If the push fails (e.g. track not published).
        """
        proto_frame = proto_data_track.DataTrackFrame(payload=bytes(frame.payload))
        if frame.user_timestamp is not None:
            proto_frame.user_timestamp = frame.user_timestamp

        req = proto_ffi.FfiRequest()
        req.local_data_track_try_push.track_handle = self._ffi_handle.handle
        req.local_data_track_try_push.frame.CopyFrom(proto_frame)

        resp = FfiClient.instance.request(req)
        if resp.local_data_track_try_push.HasField("error"):
            raise PushFrameError(resp.local_data_track_try_push.error)

    def is_published(self) -> bool:
        """Check whether this track is still published."""
        req = proto_ffi.FfiRequest()
        req.local_data_track_is_published.track_handle = self._ffi_handle.handle

        resp = FfiClient.instance.request(req)
        return resp.local_data_track_is_published.is_published

    def unpublish(self) -> None:
        """Unpublish this track."""
        req = proto_ffi.FfiRequest()
        req.local_data_track_unpublish.track_handle = self._ffi_handle.handle
        FfiClient.instance.request(req)

    def __repr__(self) -> str:
        return f"rtc.LocalDataTrack(sid={self._info.sid}, name={self._info.name})"


class RemoteDataTrack:
    """A data track published by a remote participant."""

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
        return self._info

    @property
    def publisher_identity(self) -> str:
        return self._publisher_identity

    async def subscribe(self) -> DataTrackSubscription:
        """Subscribe to this data track and receive frames.

        Returns:
            A DataTrackSubscription that can be used as an async iterator.

        Raises:
            SubscribeDataTrackError: If subscription fails.
        """
        req = proto_ffi.FfiRequest()
        req.subscribe_data_track.track_handle = self._ffi_handle.handle
        req.subscribe_data_track.options.CopyFrom(
            proto_data_track.DataTrackSubscribeOptions()
        )

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.subscribe_data_track.async_id
                == resp.subscribe_data_track.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.subscribe_data_track.HasField("error"):
            raise SubscribeDataTrackError(cb.subscribe_data_track.error)

        return DataTrackSubscription(cb.subscribe_data_track.subscription)

    def is_published(self) -> bool:
        """Check whether this remote track is still published."""
        req = proto_ffi.FfiRequest()
        req.remote_data_track_is_published.track_handle = self._ffi_handle.handle

        resp = FfiClient.instance.request(req)
        return resp.remote_data_track_is_published.is_published

    def __repr__(self) -> str:
        return (
            f"rtc.RemoteDataTrack(sid={self._info.sid}, name={self._info.name}, "
            f"publisher_identity={self._publisher_identity})"
        )


class DataTrackSubscription:
    """An active subscription to a remote data track.

    Use as an async iterator to receive frames::

        subscription = await remote_track.subscribe()
        async for frame in subscription:
            process(frame.payload)

    Dropping or closing the subscription unsubscribes from the track.
    """

    def __init__(
        self, owned_info: proto_data_track.OwnedDataTrackSubscription
    ) -> None:
        self._ffi_handle = FfiHandle(owned_info.handle.id)
        handle_id = owned_info.handle.id

        self._queue = FfiClient.instance.queue.subscribe(
            filter_fn=lambda e: (
                e.WhichOneof("message") == "data_track_subscription_event"
                and e.data_track_subscription_event.subscription_handle == handle_id
            ),
        )
        self._closed = False

    def __aiter__(self) -> AsyncIterator[DataTrackFrame]:
        return self

    async def __anext__(self) -> DataTrackFrame:
        if self._closed:
            raise StopAsyncIteration

        event: proto_ffi.FfiEvent = await self._queue.get()
        sub_event = event.data_track_subscription_event
        detail = sub_event.WhichOneof("detail")

        if detail == "frame_received":
            proto_frame = sub_event.frame_received.frame
            user_ts: Optional[int] = None
            if proto_frame.HasField("user_timestamp"):
                user_ts = proto_frame.user_timestamp
            return DataTrackFrame(
                payload=proto_frame.payload,
                user_timestamp=user_ts,
            )
        elif detail == "eos":
            self._close()
            raise StopAsyncIteration
        else:
            self._close()
            raise StopAsyncIteration

    def _close(self) -> None:
        if not self._closed:
            self._closed = True
            FfiClient.instance.queue.unsubscribe(self._queue)

    def close(self) -> None:
        """Explicitly close the subscription and unsubscribe."""
        self._close()
        self._ffi_handle.dispose()

    def __del__(self) -> None:
        self._close()
