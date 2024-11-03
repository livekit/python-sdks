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

import ctypes
from typing import List, Union, Callable, Dict, Awaitable, Optional, Mapping, cast
from abc import abstractmethod, ABC

from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._proto import participant_pb2 as proto_participant
from ._proto.room_pb2 import (
    TrackPublishOptions,
)
from ._proto.room_pb2 import (
    TranscriptionSegment as ProtoTranscriptionSegment,
)
from ._utils import BroadcastQueue
from .track import LocalTrack
from .track_publication import (
    LocalTrackPublication,
    RemoteTrackPublication,
    TrackPublication,
)
from .transcription import Transcription
from .rpc import RpcError
from ._proto.rpc_pb2 import RpcMethodInvocationResponseRequest
from .log import logger
import asyncio

from .rpc import RpcInvocationData


class PublishTrackError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class UnpublishTrackError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class PublishDataError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class PublishDTMFError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class PublishTranscriptionError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class Participant(ABC):
    def __init__(self, owned_info: proto_participant.OwnedParticipant) -> None:
        self._info = owned_info.info
        self._ffi_handle = FfiHandle(owned_info.handle.id)

    @property
    @abstractmethod
    def track_publications(self) -> Mapping[str, TrackPublication]:
        """
        A dictionary of track publications associated with the participant.
        """
        ...

    @property
    def sid(self) -> str:
        return self._info.sid

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def identity(self) -> str:
        return self._info.identity

    @property
    def metadata(self) -> str:
        return self._info.metadata

    @property
    def attributes(self) -> dict[str, str]:
        """Custom attributes associated with the participant."""
        return dict(self._info.attributes)

    @property
    def kind(self) -> proto_participant.ParticipantKind.ValueType:
        """Participant's kind (e.g., regular participant, ingress, egress, sip, agent)."""
        return self._info.kind


class LocalParticipant(Participant):
    """Represents the local participant in a room."""

    def __init__(
        self,
        room_queue: BroadcastQueue[proto_ffi.FfiEvent],
        owned_info: proto_participant.OwnedParticipant,
    ) -> None:
        super().__init__(owned_info)
        self._room_queue = room_queue
        self._track_publications: dict[str, LocalTrackPublication] = {}  # type: ignore
        self._rpc_handlers: Dict[
            str, Callable[[RpcInvocationData], Union[Awaitable[str], str]]
        ] = {}

    @property
    def track_publications(self) -> Mapping[str, LocalTrackPublication]:
        """
        A dictionary of track publications associated with the participant.
        """
        return self._track_publications

    async def publish_data(
        self,
        payload: Union[bytes, str],
        *,
        reliable: bool = True,
        destination_identities: List[str] = [],
        topic: str = "",
    ) -> None:
        """
        Publish arbitrary data to the room.

        Args:
            payload (Union[bytes, str]): The data to publish.
            reliable (bool, optional): Whether to send reliably or not. Defaults to True.
            destination_identities (List[str], optional): List of participant identities to send to. Defaults to [].
            topic (str, optional): The topic under which to publish the data. Defaults to "".

        Raises:
            PublishDataError: If there is an error in publishing data.
        """
        if isinstance(payload, str):
            payload = payload.encode("utf-8")

        data_len = len(payload)
        cdata = (ctypes.c_byte * data_len)(*payload)

        req = proto_ffi.FfiRequest()
        req.publish_data.local_participant_handle = self._ffi_handle.handle
        req.publish_data.data_ptr = ctypes.addressof(cdata)
        req.publish_data.data_len = data_len
        req.publish_data.reliable = reliable
        req.publish_data.topic = topic
        req.publish_data.destination_identities.extend(destination_identities)

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.publish_data.async_id == resp.publish_data.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.publish_data.error:
            raise PublishDataError(cb.publish_data.error)

    async def publish_dtmf(self, *, code: int, digit: str) -> None:
        """
        Publish SIP DTMF message.

        Args:
            code (int): DTMF code.
            digit (str): DTMF digit.

        Raises:
            PublishDTMFError: If there is an error in publishing SIP DTMF message.
        """
        req = proto_ffi.FfiRequest()
        req.publish_sip_dtmf.local_participant_handle = self._ffi_handle.handle
        req.publish_sip_dtmf.code = code
        req.publish_sip_dtmf.digit = digit

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.publish_sip_dtmf.async_id == resp.publish_sip_dtmf.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.publish_sip_dtmf.error:
            raise PublishDTMFError(cb.publish_sip_dtmf.error)

    async def publish_transcription(self, transcription: Transcription) -> None:
        """
        Publish transcription data to the room.

        Args:
            transcription (Transcription): The transcription data to publish.

        Raises:
            PublishTranscriptionError: If there is an error in publishing transcription.
        """
        req = proto_ffi.FfiRequest()
        proto_segments = [
            ProtoTranscriptionSegment(
                id=s.id,
                text=s.text,
                start_time=s.start_time,
                end_time=s.end_time,
                final=s.final,
                language=s.language,
            )
            for s in transcription.segments
        ]
        # fmt: off
        req.publish_transcription.local_participant_handle = self._ffi_handle.handle
        req.publish_transcription.participant_identity = transcription.participant_identity
        req.publish_transcription.segments.extend(proto_segments)
        req.publish_transcription.track_id = transcription.track_sid
        # fmt: on
        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.publish_transcription.async_id
                == resp.publish_transcription.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.publish_transcription.error:
            raise PublishTranscriptionError(cb.publish_transcription.error)

    async def perform_rpc(
        self,
        *,
        destination_identity: str,
        method: str,
        payload: str,
        response_timeout: Optional[float] = None,
    ) -> str:
        """
        Initiate an RPC call to a remote participant.

        Args:
            destination_identity (str): The `identity` of the destination participant
            method (str): The method name to call
            payload (str): The method payload
            response_timeout (Optional[float]): Timeout for receiving a response after initial connection

        Returns:
            str: The response payload

        Raises:
            RpcError: On failure. Details in `message`.
        """
        req = proto_ffi.FfiRequest()
        req.perform_rpc.local_participant_handle = self._ffi_handle.handle
        req.perform_rpc.destination_identity = destination_identity
        req.perform_rpc.method = method
        req.perform_rpc.payload = payload
        if response_timeout is not None:
            req.perform_rpc.response_timeout_ms = int(response_timeout * 1000)

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb = await queue.wait_for(
                lambda e: (e.perform_rpc.async_id == resp.perform_rpc.async_id)
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.perform_rpc.HasField("error"):
            raise RpcError._from_proto(cb.perform_rpc.error)

        return cb.perform_rpc.payload

    def register_rpc_method(
        self,
        method_name: str,
        handler: Optional[
            Callable[[RpcInvocationData], Union[Awaitable[str], str]]
        ] = None,
    ) -> Union[None, Callable]:
        """
        Establishes the participant as a receiver for calls of the specified RPC method.
        Can be used either as a decorator or a regular method.

        The handler will receive one argument of type `RpcInvocationData` and should return a string response which will be forwarded back to the caller.

        The handler may be synchronous or asynchronous.

        If unable to respond within `response_timeout`, the caller will hang up and receive an error on their side.

        You may raise errors of type `RpcError` in the handler, and they will be forwarded to the caller.

        Other errors raised in your handler will be caught and forwarded to the caller as "1500 Application Error".

        Args:
            method_name (str): The name of the indicated RPC method.
            handler (Optional[Callable]): Handler to be invoked whenever an RPC request for this method is received.  Omit this argument to use the decorator syntax.

        Returns:
            None (when used as a decorator it returns the decorator function)

        Example:
            # As a decorator:
            @room.local_participant.register_rpc_method("greet")
            async def greet_handler(data: RpcInvocationData) -> str:
                print(f"Received greeting from {data.caller_identity}: {data.payload}")
                return f"Hello, {data.caller_identity}!"

            # As a regular method:
            async def greet_handler(data: RpcInvocationData) -> str:
                print(f"Received greeting from {data.caller_identity}: {data.payload}")
                return f"Hello, {data.caller_identity}!"

            room.local_participant.register_rpc_method('greet', greet_handler)
        """

        def register(handler_func):
            self._rpc_handlers[method_name] = handler_func
            req = proto_ffi.FfiRequest()
            req.register_rpc_method.local_participant_handle = self._ffi_handle.handle
            req.register_rpc_method.method = method_name
            FfiClient.instance.request(req)

        if handler is not None:
            register(handler)
            return None
        else:
            # Called as a decorator
            return register

    def unregister_rpc_method(self, method: str) -> None:
        """
        Unregisters a previously registered RPC method.

        Args:
            method (str): The name of the RPC method to unregister
        """
        self._rpc_handlers.pop(method, None)

        req = proto_ffi.FfiRequest()
        req.unregister_rpc_method.local_participant_handle = self._ffi_handle.handle
        req.unregister_rpc_method.method = method

        FfiClient.instance.request(req)

    async def _handle_rpc_method_invocation(
        self,
        invocation_id: int,
        method: str,
        request_id: str,
        caller_identity: str,
        payload: str,
        response_timeout: float,
    ) -> None:
        response_error: Optional[RpcError] = None
        response_payload: Optional[str] = None

        params = RpcInvocationData(
            request_id, caller_identity, payload, response_timeout
        )

        handler = self._rpc_handlers.get(method)

        if not handler:
            response_error = RpcError._built_in(RpcError.ErrorCode.UNSUPPORTED_METHOD)
        else:
            try:
                if asyncio.iscoroutinefunction(handler):
                    async_handler = cast(
                        Callable[[RpcInvocationData], Awaitable[str]], handler
                    )

                    async def run_handler():
                        try:
                            return await async_handler(params)
                        except asyncio.CancelledError:
                            # This will be caught by the outer try-except if it's due to timeout
                            raise

                    try:
                        response_payload = await asyncio.wait_for(
                            run_handler(), timeout=response_timeout
                        )
                    except asyncio.TimeoutError:
                        raise RpcError._built_in(RpcError.ErrorCode.RESPONSE_TIMEOUT)
                    except asyncio.CancelledError:
                        raise RpcError._built_in(
                            RpcError.ErrorCode.RECIPIENT_DISCONNECTED
                        )
                else:
                    sync_handler = cast(Callable[[RpcInvocationData], str], handler)
                    response_payload = sync_handler(params)
            except RpcError as error:
                response_error = error
            except Exception as error:
                logger.exception(
                    f"Uncaught error returned by RPC handler for {method}. Returning APPLICATION_ERROR instead.  Original error: {error}",
                )
                response_error = RpcError._built_in(
                    RpcError.ErrorCode.APPLICATION_ERROR
                )

        req = proto_ffi.FfiRequest(
            rpc_method_invocation_response=RpcMethodInvocationResponseRequest(
                local_participant_handle=self._ffi_handle.handle,
                invocation_id=invocation_id,
                error=response_error._to_proto() if response_error else None,
                payload=response_payload,
            )
        )

        res = FfiClient.instance.request(req)

        if res.rpc_method_invocation_response.error:
            logger.exception(
                f"error sending rpc method invocation response: {res.rpc_method_invocation_response.error}"
            )

    async def set_metadata(self, metadata: str) -> None:
        """
        Set the metadata for the local participant.

        Note: this requires `canUpdateOwnMetadata` permission.

        Args:
            metadata (str): The new metadata.
        """
        req = proto_ffi.FfiRequest()
        req.set_local_metadata.local_participant_handle = self._ffi_handle.handle
        req.set_local_metadata.metadata = metadata

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            await queue.wait_for(
                lambda e: e.set_local_metadata.async_id
                == resp.set_local_metadata.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

    async def set_name(self, name: str) -> None:
        """
        Set the name for the local participant.

        Note: this requires `canUpdateOwnMetadata` permission.

        Args:
            name (str): The new name.
        """
        req = proto_ffi.FfiRequest()
        req.set_local_name.local_participant_handle = self._ffi_handle.handle
        req.set_local_name.name = name

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            await queue.wait_for(
                lambda e: e.set_local_name.async_id == resp.set_local_name.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

    async def set_attributes(self, attributes: dict[str, str]) -> None:
        """
        Set custom attributes for the local participant.

        Note: this requires `canUpdateOwnMetadata` permission.

        Args:
            attributes (dict[str, str]): A dictionary of attributes to set.
        """
        req = proto_ffi.FfiRequest()
        req.set_local_attributes.local_participant_handle = self._ffi_handle.handle
        existing_attributes = {
            entry.key: entry.value for entry in req.set_local_attributes.attributes
        }
        existing_attributes.update(attributes)

        for key, value in existing_attributes.items():
            entry = req.set_local_attributes.attributes.add()
            entry.key = key
            entry.value = value

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            await queue.wait_for(
                lambda e: e.set_local_attributes.async_id
                == resp.set_local_attributes.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

    async def publish_track(
        self, track: LocalTrack, options: TrackPublishOptions = TrackPublishOptions()
    ) -> LocalTrackPublication:
        """
        Publish a local track to the room.

        Args:
            track (LocalTrack): The track to publish.
            options (TrackPublishOptions, optional): Options for publishing the track.

        Returns:
            LocalTrackPublication: The publication of the published track.

        Raises:
            PublishTrackError: If there is an error in publishing the track.
        """
        req = proto_ffi.FfiRequest()
        req.publish_track.track_handle = track._ffi_handle.handle
        req.publish_track.local_participant_handle = self._ffi_handle.handle
        req.publish_track.options.CopyFrom(options)

        queue = self._room_queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.publish_track.async_id == resp.publish_track.async_id
            )

            if cb.publish_track.error:
                raise PublishTrackError(cb.publish_track.error)

            track_publication = LocalTrackPublication(cb.publish_track.publication)
            track_publication.track = track
            track._info.sid = track_publication.sid
            self._track_publications[track_publication.sid] = track_publication

            queue.task_done()
            return track_publication
        finally:
            self._room_queue.unsubscribe(queue)

    async def unpublish_track(self, track_sid: str) -> None:
        """
        Unpublish a track from the room.

        Args:
            track_sid (str): The SID of the track to unpublish.

        Raises:
            UnpublishTrackError: If there is an error in unpublishing the track.
        """
        req = proto_ffi.FfiRequest()
        req.unpublish_track.local_participant_handle = self._ffi_handle.handle
        req.unpublish_track.track_sid = track_sid

        queue = self._room_queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.unpublish_track.async_id == resp.unpublish_track.async_id
            )

            if cb.unpublish_track.error:
                raise UnpublishTrackError(cb.unpublish_track.error)

            publication = self._track_publications.pop(track_sid)
            publication.track = None
            queue.task_done()
        finally:
            self._room_queue.unsubscribe(queue)

    def __repr__(self) -> str:
        return f"rtc.LocalParticipant(sid={self.sid}, identity={self.identity}, name={self.name})"


class RemoteParticipant(Participant):
    def __init__(self, owned_info: proto_participant.OwnedParticipant) -> None:
        super().__init__(owned_info)
        self._track_publications: dict[str, RemoteTrackPublication] = {}  # type: ignore

    @property
    def track_publications(self) -> Mapping[str, RemoteTrackPublication]:
        """
        A dictionary of track publications associated with the participant.
        """
        return self._track_publications

    def __repr__(self) -> str:
        return f"rtc.RemoteParticipant(sid={self.sid}, identity={self.identity}, name={self.name})"
