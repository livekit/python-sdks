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
import ctypes
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, Literal, Optional, cast, Mapping

from .event_emitter import EventEmitter
from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._proto import participant_pb2 as proto_participant
from ._proto import room_pb2 as proto_room
from ._proto.room_pb2 import ConnectionState
from ._proto.track_pb2 import TrackKind
from ._proto.rpc_pb2 import RpcMethodInvocationEvent
from ._utils import BroadcastQueue
from .e2ee import E2EEManager, E2EEOptions
from .participant import LocalParticipant, Participant, RemoteParticipant
from .track import RemoteAudioTrack, RemoteVideoTrack
from .track_publication import RemoteTrackPublication, TrackPublication
from .transcription import TranscriptionSegment

EventTypes = Literal[
    "participant_connected",
    "participant_disconnected",
    "local_track_published",
    "local_track_unpublished",
    "local_track_subscribed",
    "track_published",
    "track_unpublished",
    "track_subscribed",
    "track_unsubscribed",
    "track_subscription_failed",
    "track_muted",
    "track_unmuted",
    "active_speakers_changed",
    "room_metadata_changed",
    "participant_metadata_changed",
    "participant_name_changed",
    "participant_attributes_changed",
    "connection_quality_changed",
    "data_received",
    "sip_dtmf_received",
    "transcription_received",
    "e2ee_state_changed",
    "connection_state_changed",
    "connected",
    "disconnected",
    "reconnecting",
    "reconnected",
]


@dataclass
class RtcConfiguration:
    ice_transport_type: proto_room.IceTransportType.ValueType = (
        proto_room.IceTransportType.TRANSPORT_ALL
    )
    """Specifies the type of ICE transport to be used (e.g., all, relay, etc.)."""
    continual_gathering_policy: proto_room.ContinualGatheringPolicy.ValueType = (
        proto_room.ContinualGatheringPolicy.GATHER_CONTINUALLY
    )
    """Policy for continual gathering of ICE candidates."""
    ice_servers: list[proto_room.IceServer] = field(default_factory=list)
    """List of ICE servers for STUN/TURN. When empty, it uses the default ICE servers provided by
    the SFU."""


@dataclass
class RoomOptions:
    auto_subscribe: bool = True
    """Automatically subscribe to tracks when participants join."""
    dynacast: bool = False
    e2ee: E2EEOptions | None = None
    """Options for end-to-end encryption."""
    rtc_config: RtcConfiguration | None = None
    """WebRTC-related configuration."""


@dataclass
class DataPacket:
    data: bytes
    """The payload of the data packet."""
    kind: proto_room.DataPacketKind.ValueType
    """Type of the data packet (e.g., RELIABLE, LOSSY)."""
    participant: RemoteParticipant | None
    """Participant who sent the data. None when sent by a server SDK."""
    topic: str | None = None
    """Topic associated with the data packet."""


@dataclass
class SipDTMF:
    code: int
    """DTMF code corresponding to the digit."""
    digit: str
    """DTMF digit sent."""
    participant: RemoteParticipant | None = None
    """Participant who sent the DTMF digit. None when sent by a server SDK."""


class ConnectError(Exception):
    def __init__(self, message: str):
        self.message = message


class Room(EventEmitter[EventTypes]):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """Initializes a new Room instance.

        Parameters:
            loop (Optional[asyncio.AbstractEventLoop]): The event loop to use. If not provided, the default event loop is used.
        """
        super().__init__()

        self._ffi_handle: Optional[FfiHandle] = None
        self._loop = loop or asyncio.get_event_loop()
        self._room_queue = BroadcastQueue[proto_ffi.FfiEvent]()
        self._info = proto_room.RoomInfo()
        self._rpc_invocation_tasks: set[asyncio.Task] = set()

        self._remote_participants: Dict[str, RemoteParticipant] = {}
        self._connection_state = ConnectionState.CONN_DISCONNECTED
        self._first_sid_future = asyncio.Future[str]()
        self._local_participant: LocalParticipant | None = None

    def __del__(self) -> None:
        if self._ffi_handle is not None:
            FfiClient.instance.queue.unsubscribe(self._ffi_queue)

    @property
    async def sid(self) -> str:
        """Asynchronously retrieves the session ID (SID) of the room.

        Returns:
            str: The session ID of the room.
        """
        if self._info.sid:
            return self._info.sid

        return await self._first_sid_future

    @property
    def local_participant(self) -> LocalParticipant:
        """Gets the local participant in the room.

        Returns:
            LocalParticipant: The local participant in the room.
        """
        if self._local_participant is None:
            raise Exception("cannot access local participant before connecting")

        return self._local_participant

    @property
    def connection_state(self) -> ConnectionState.ValueType:
        """Gets the connection state of the room.

        Returns:
            ConnectionState: The connection state of the room.
        """
        return self._connection_state

    @property
    def remote_participants(self) -> Mapping[str, RemoteParticipant]:
        """Gets the remote participants in the room.

        Returns:
            dict[str, RemoteParticipant]: A dictionary of remote participants indexed by their
            identity.
        """
        return self._remote_participants

    @property
    def name(self) -> str:
        """Gets the name of the room.

        Returns:
            str: The name of the room.
        """
        return self._info.name

    @property
    def metadata(self) -> str:
        """Gets the metadata associated with the room.

        Returns:
            str: The metadata of the room.
        """
        return self._info.metadata

    @property
    def e2ee_manager(self) -> E2EEManager:
        """Gets the end-to-end encryption (E2EE) manager for the room.

        Returns:
            E2EEManager: The E2EE manager instance.
        """
        return self._e2ee_manager

    def isconnected(self) -> bool:
        """Checks if the room is currently connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        return (
            self._ffi_handle is not None
            and self._connection_state != ConnectionState.CONN_DISCONNECTED
        )

    def on(self, event: EventTypes, callback: Optional[Callable] = None) -> Callable:
        """Registers an event handler for a specific event type.

        Parameters:
            event (EventTypes): The name of the event to listen for.
            callback (Callable): The function to call when the event occurs.

        Returns:
            Callable: The registered callback function.

        Available events:
            - **"participant_connected"**: Called when a new participant joins the room.
                - Arguments: `participant` (RemoteParticipant)
            - **"participant_disconnected"**: Called when a participant leaves the room.
                - Arguments: `participant` (RemoteParticipant)
            - **"local_track_published"**: Called when a local track is published.
                - Arguments: `publication` (LocalTrackPublication), `track` (Track)
            - **"local_track_unpublished"**: Called when a local track is unpublished.
                - Arguments: `publication` (LocalTrackPublication)
            - **"local_track_subscribed"**: Called when a local track is subscribed.
                - Arguments: `track` (Track)
            - **"track_published"**: Called when a remote participant publishes a track.
                - Arguments: `publication` (RemoteTrackPublication), `participant` (RemoteParticipant)
            - **"track_unpublished"**: Called when a remote participant unpublishes a track.
                - Arguments: `publication` (RemoteTrackPublication), `participant` (RemoteParticipant)
            - **"track_subscribed"**: Called when a track is subscribed.
                - Arguments: `track` (Track), `publication` (RemoteTrackPublication), `participant` (RemoteParticipant)
            - **"track_unsubscribed"**: Called when a track is unsubscribed.
                - Arguments: `track` (Track), `publication` (RemoteTrackPublication), `participant` (RemoteParticipant)
            - **"track_subscription_failed"**: Called when a track subscription fails.
                - Arguments: `participant` (RemoteParticipant), `track_sid` (str), `error` (str)
            - **"track_muted"**: Called when a track is muted.
                - Arguments: `participant` (Participant), `publication` (TrackPublication)
            - **"track_unmuted"**: Called when a track is unmuted.
                - Arguments: `participant` (Participant), `publication` (TrackPublication)
            - **"active_speakers_changed"**: Called when the list of active speakers changes.
                - Arguments: `speakers` (list[Participant])
            - **"room_metadata_changed"**: Called when the room's metadata is updated.
                - Arguments: `old_metadata` (str), `new_metadata` (str)
            - **"participant_metadata_changed"**: Called when a participant's metadata is updated.
                - Arguments: `participant` (Participant), `old_metadata` (str), `new_metadata` (str)
            - **"participant_name_changed"**: Called when a participant's name is changed.
                - Arguments: `participant` (Participant), `old_name` (str), `new_name` (str)
            - **"participant_attributes_changed"**: Called when a participant's attributes change.
                - Arguments: `changed_attributes` (dict), `participant` (Participant)
            - **"connection_quality_changed"**: Called when a participant's connection quality changes.
                - Arguments: `participant` (Participant), `quality` (ConnectionQuality)
            - **"transcription_received"**: Called when a transcription is received.
                - Arguments: `segments` (list[TranscriptionSegment]), `participant` (Participant), `publication` (TrackPublication)
            - **"data_received"**: Called when data is received.
                - Arguments: `data_packet` (DataPacket)
            - **"sip_dtmf_received"**: Called when a SIP DTMF signal is received.
                - Arguments: `sip_dtmf` (SipDTMF)
            - **"e2ee_state_changed"**: Called when a participant's E2EE state changes.
                - Arguments: `participant` (Participant), `state` (EncryptionState)
            - **"connection_state_changed"**: Called when the room's connection state changes.
                - Arguments: `connection_state` (ConnectionState)
            - **"connected"**: Called when the room is successfully connected.
                - Arguments: None
            - **"disconnected"**: Called when the room is disconnected.
                - Arguments: `reason` (DisconnectReason)
            - **"reconnecting"**: Called when the room is attempting to reconnect.
                - Arguments: None
            - **"reconnected"**: Called when the room has successfully reconnected.
                - Arguments: None

        Example:
            ```python
            def on_participant_connected(participant):
                print(f"Participant connected: {participant.identity}")

            room.on("participant_connected", on_participant_connected)
            ```
        """
        return super().on(event, callback)

    async def connect(
        self, url: str, token: str, options: RoomOptions = RoomOptions()
    ) -> None:
        """Connects to a LiveKit room using the specified URL and token.

        Parameters:
            url (str): The WebSocket URL of the LiveKit server to connect to.
            token (str): The access token for authentication and authorization.
            options (RoomOptions, optional): Additional options for the room connection.

        Raises:
            ConnectError: If the connection fails.

        Example:
            ```python
            room = Room()

            # Listen for events before connecting to the room
            @room.on("participant_connected")
            def on_participant_connected(participant):
                print(f"Participant connected: {participant.identity}")

            await room.connect("ws://localhost:7880", "your_token")
            ```
        """
        req = proto_ffi.FfiRequest()
        req.connect.url = url
        req.connect.token = token

        # options
        req.connect.options.auto_subscribe = options.auto_subscribe
        req.connect.options.dynacast = options.dynacast

        if options.e2ee:
            req.connect.options.e2ee.encryption_type = options.e2ee.encryption_type
            req.connect.options.e2ee.key_provider_options.shared_key = (
                options.e2ee.key_provider_options.shared_key  # type: ignore
            )
            req.connect.options.e2ee.key_provider_options.ratchet_salt = (
                options.e2ee.key_provider_options.ratchet_salt
            )
            req.connect.options.e2ee.key_provider_options.failure_tolerance = (
                options.e2ee.key_provider_options.failure_tolerance
            )
            req.connect.options.e2ee.key_provider_options.ratchet_window_size = (
                options.e2ee.key_provider_options.ratchet_window_size
            )

        if options.rtc_config:
            req.connect.options.rtc_config.ice_transport_type = (
                options.rtc_config.ice_transport_type
            )  # type: ignore
            req.connect.options.rtc_config.continual_gathering_policy = (
                options.rtc_config.continual_gathering_policy
            )  # type: ignore
            req.connect.options.rtc_config.ice_servers.extend(
                options.rtc_config.ice_servers
            )

        # subscribe before connecting so we don't miss any events
        self._ffi_queue = FfiClient.instance.queue.subscribe(self._loop)

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.connect.async_id == resp.connect.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.connect.error:
            FfiClient.instance.queue.unsubscribe(self._ffi_queue)
            raise ConnectError(cb.connect.error)

        self._ffi_handle = FfiHandle(cb.connect.result.room.handle.id)

        self._e2ee_manager = E2EEManager(self._ffi_handle.handle, options.e2ee)

        self._info = cb.connect.result.room.info
        self._connection_state = ConnectionState.CONN_CONNECTED

        self._local_participant = LocalParticipant(
            self._room_queue, cb.connect.result.local_participant
        )

        for pt in cb.connect.result.participants:
            rp = self._create_remote_participant(pt.participant)

            # add the initial remote participant tracks
            for owned_publication_info in pt.publications:
                publication = RemoteTrackPublication(owned_publication_info)
                rp._track_publications[publication.sid] = publication

        # start listening to room events
        self._task = self._loop.create_task(self._listen_task())

    async def disconnect(self) -> None:
        """Disconnects from the room."""
        if not self.isconnected():
            return

        await self._drain_rpc_invocation_tasks()

        req = proto_ffi.FfiRequest()
        req.disconnect.room_handle = self._ffi_handle.handle  # type: ignore
        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            await queue.wait_for(
                lambda e: e.disconnect.async_id == resp.disconnect.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)
        await self._task
        FfiClient.instance.queue.unsubscribe(self._ffi_queue)

    async def _listen_task(self) -> None:
        # listen to incoming room events
        while True:
            event = await self._ffi_queue.get()
            if event.WhichOneof("message") == "rpc_method_invocation":
                self._on_rpc_method_invocation(event.rpc_method_invocation)
            elif event.room_event.room_handle == self._ffi_handle.handle:  # type: ignore
                if event.room_event.HasField("eos"):
                    break

                try:
                    self._on_room_event(event.room_event)
                except Exception:
                    logging.exception(
                        "error running user callback for %s: %s",
                        event.room_event.WhichOneof("message"),
                        event.room_event,
                    )

            # wait for the subscribers to process the event
            # before processing the next one
            self._room_queue.put_nowait(event)
            await self._room_queue.join()

        # Clean up any pending RPC invocation tasks
        await self._drain_rpc_invocation_tasks()

    def _on_rpc_method_invocation(self, rpc_invocation: RpcMethodInvocationEvent):
        if self._local_participant is None:
            return

        if (
            rpc_invocation.local_participant_handle
            == self._local_participant._ffi_handle.handle
        ):
            task = self._loop.create_task(
                self._local_participant._handle_rpc_method_invocation(
                    rpc_invocation.invocation_id,
                    rpc_invocation.method,
                    rpc_invocation.request_id,
                    rpc_invocation.caller_identity,
                    rpc_invocation.payload,
                    rpc_invocation.response_timeout_ms / 1000.0,
                )
            )
            self._rpc_invocation_tasks.add(task)
            task.add_done_callback(self._rpc_invocation_tasks.discard)

    def _on_room_event(self, event: proto_room.RoomEvent):
        which = event.WhichOneof("message")
        if which == "participant_connected":
            rparticipant = self._create_remote_participant(
                event.participant_connected.info
            )
            self.emit("participant_connected", rparticipant)
        elif which == "participant_disconnected":
            identity = event.participant_disconnected.participant_identity
            rparticipant = self._remote_participants.pop(identity)
            self.emit("participant_disconnected", rparticipant)
        elif which == "local_track_published":
            sid = event.local_track_published.track_sid
            lpublication = self.local_participant.track_publications[sid]
            track = lpublication.track
            self.emit("local_track_published", lpublication, track)
        elif which == "local_track_unpublished":
            sid = event.local_track_unpublished.publication_sid
            lpublication = self.local_participant.track_publications[sid]
            self.emit("local_track_unpublished", lpublication)
        elif which == "local_track_subscribed":
            sid = event.local_track_subscribed.track_sid
            lpublication = self.local_participant.track_publications[sid]
            lpublication._first_subscription.set_result(None)
            self.emit("local_track_subscribed", lpublication.track)
        elif which == "track_published":
            rparticipant = self._remote_participants[
                event.track_published.participant_identity
            ]
            rpublication = RemoteTrackPublication(event.track_published.publication)
            rparticipant._track_publications[rpublication.sid] = rpublication
            self.emit("track_published", rpublication, rparticipant)
        elif which == "track_unpublished":
            rparticipant = self._remote_participants[
                event.track_unpublished.participant_identity
            ]
            rpublication = rparticipant._track_publications.pop(
                event.track_unpublished.publication_sid
            )
            self.emit("track_unpublished", rpublication, rparticipant)
        elif which == "track_subscribed":
            owned_track_info = event.track_subscribed.track
            track_info = owned_track_info.info
            rparticipant = self._remote_participants[
                event.track_subscribed.participant_identity
            ]
            rpublication = rparticipant.track_publications[track_info.sid]
            rpublication.subscribed = True
            if track_info.kind == TrackKind.KIND_VIDEO:
                remote_video_track = RemoteVideoTrack(owned_track_info)
                rpublication.track = remote_video_track
                self.emit(
                    "track_subscribed", remote_video_track, rpublication, rparticipant
                )
            elif track_info.kind == TrackKind.KIND_AUDIO:
                remote_audio_track = RemoteAudioTrack(owned_track_info)
                rpublication.track = remote_audio_track
                self.emit(
                    "track_subscribed", remote_audio_track, rpublication, rparticipant
                )
        elif which == "track_unsubscribed":
            identity = event.track_unsubscribed.participant_identity
            rparticipant = self._remote_participants[identity]
            rpublication = rparticipant.track_publications[
                event.track_unsubscribed.track_sid
            ]
            track = rpublication.track
            rpublication.track = None
            rpublication.subscribed = False
            self.emit("track_unsubscribed", track, rpublication, rparticipant)
        elif which == "track_subscription_failed":
            identity = event.track_subscription_failed.participant_identity
            rparticipant = self._remote_participants[identity]
            error = event.track_subscription_failed.error
            self.emit(
                "track_subscription_failed",
                rparticipant,
                event.track_subscription_failed.track_sid,
                error,
            )
        elif which == "track_muted":
            identity = event.track_muted.participant_identity
            # TODO: pass participant identity
            participant = self._retrieve_participant(identity)
            assert isinstance(participant, Participant)
            publication = participant.track_publications[event.track_muted.track_sid]
            publication._info.muted = True
            if publication.track:
                publication.track._info.muted = True

            self.emit("track_muted", participant, publication)
        elif which == "track_unmuted":
            identity = event.track_unmuted.participant_identity
            # TODO: pass participant identity
            participant = self._retrieve_participant(identity)
            assert isinstance(participant, Participant)
            publication = participant.track_publications[event.track_unmuted.track_sid]
            publication._info.muted = False
            if publication.track:
                publication.track._info.muted = False

            self.emit("track_unmuted", participant, publication)
        elif which == "active_speakers_changed":
            speakers: list[Participant] = []
            # TODO: pass participant identity
            for identity in event.active_speakers_changed.participant_identities:
                participant = self._retrieve_participant(identity)
                assert isinstance(participant, Participant)
                speakers.append(participant)

            self.emit("active_speakers_changed", speakers)
        elif which == "room_metadata_changed":
            old_metadata = self.metadata
            self._info.metadata = event.room_metadata_changed.metadata
            self.emit("room_metadata_changed", old_metadata, self.metadata)
        elif which == "room_sid_changed":
            if not self._info.sid:
                self._first_sid_future.set_result(event.room_sid_changed.sid)
            self._info.sid = event.room_sid_changed.sid
            # This is an internal event, not exposed to users
        elif which == "participant_metadata_changed":
            identity = event.participant_metadata_changed.participant_identity
            # TODO: pass participant identity
            participant = self._retrieve_participant(identity)
            assert isinstance(participant, Participant)
            old_metadata = participant.metadata
            participant._info.metadata = event.participant_metadata_changed.metadata
            self.emit(
                "participant_metadata_changed",
                participant,
                old_metadata,
                participant.metadata,
            )
        elif which == "participant_name_changed":
            identity = event.participant_name_changed.participant_identity
            participant = self._retrieve_participant(identity)
            assert isinstance(participant, Participant)
            old_name = participant.name
            participant._info.name = event.participant_name_changed.name
            self.emit(
                "participant_name_changed", participant, old_name, participant.name
            )
        elif which == "participant_attributes_changed":
            identity = event.participant_attributes_changed.participant_identity
            attributes = event.participant_attributes_changed.attributes
            changed_attributes = dict(
                (entry.key, entry.value)
                for entry in event.participant_attributes_changed.changed_attributes
            )
            participant = self._retrieve_participant(identity)
            assert isinstance(participant, Participant)
            participant._info.attributes.clear()
            participant._info.attributes.update(
                (entry.key, entry.value) for entry in attributes
            )
            self.emit(
                "participant_attributes_changed",
                changed_attributes,
                participant,
            )
        elif which == "connection_quality_changed":
            identity = event.connection_quality_changed.participant_identity
            # TODO: pass participant identity
            participant = self._retrieve_participant(identity)
            self.emit(
                "connection_quality_changed",
                participant,
                event.connection_quality_changed.quality,
            )
        elif which == "transcription_received":
            transcription = event.transcription_received
            segments = [
                TranscriptionSegment(
                    id=s.id,
                    text=s.text,
                    final=s.final,
                    start_time=s.start_time,
                    end_time=s.end_time,
                    language=s.language,
                )
                for s in transcription.segments
            ]
            part = self._retrieve_participant(transcription.participant_identity)
            pub: TrackPublication | None = None
            if part:
                pub = part.track_publications.get(transcription.track_sid)
            self.emit("transcription_received", segments, part, pub)
        elif which == "data_packet_received":
            packet = event.data_packet_received
            which_val = packet.WhichOneof("value")
            if which_val == "user":
                owned_buffer_info = packet.user.data
                buffer_info = owned_buffer_info.data
                native_data = ctypes.cast(
                    buffer_info.data_ptr,
                    ctypes.POINTER(ctypes.c_byte * buffer_info.data_len),
                ).contents

                data = bytes(native_data)
                FfiHandle(owned_buffer_info.handle.id)
                rparticipant = cast(
                    RemoteParticipant,
                    self._retrieve_remote_participant(packet.participant_identity),
                )
                self.emit(
                    "data_received",
                    DataPacket(
                        data=data,
                        kind=packet.kind,
                        participant=rparticipant,
                        topic=packet.user.topic,
                    ),
                )
            elif which_val == "sip_dtmf":
                rparticipant = cast(
                    RemoteParticipant,
                    self._retrieve_remote_participant(packet.participant_identity),
                )
                self.emit(
                    "sip_dtmf_received",
                    SipDTMF(
                        code=packet.sip_dtmf.code,
                        digit=packet.sip_dtmf.digit,
                        participant=rparticipant,
                    ),
                )
        elif which == "e2ee_state_changed":
            identity = event.e2ee_state_changed.participant_identity
            e2ee_state = event.e2ee_state_changed.state
            # TODO: pass participant identity
            self.emit(
                "e2ee_state_changed", self._retrieve_participant(identity), e2ee_state
            )
        elif which == "connection_state_changed":
            connection_state = event.connection_state_changed.state
            self._connection_state = connection_state
            self.emit("connection_state_changed", connection_state)
        elif which == "connected":
            self.emit("connected")
        elif which == "disconnected":
            self.emit("disconnected", event.disconnected.reason)
        elif which == "reconnecting":
            self.emit("reconnecting")
        elif which == "reconnected":
            self.emit("reconnected")

    async def _drain_rpc_invocation_tasks(self) -> None:
        if self._rpc_invocation_tasks:
            for task in self._rpc_invocation_tasks:
                task.cancel()
            await asyncio.gather(*self._rpc_invocation_tasks, return_exceptions=True)

    def _retrieve_remote_participant(
        self, identity: str
    ) -> Optional[RemoteParticipant]:
        """Retrieve a remote participant by identity"""
        return self._remote_participants.get(identity, None)

    def _retrieve_participant(self, identity: str) -> Optional[Participant]:
        """Retrieve a local or remote participant by identity"""
        if identity and identity == self.local_participant.identity:
            return self.local_participant

        return self._retrieve_remote_participant(identity)

    def _create_remote_participant(
        self, owned_info: proto_participant.OwnedParticipant
    ) -> RemoteParticipant:
        if owned_info.info.identity in self._remote_participants:
            raise Exception("participant already exists")

        participant = RemoteParticipant(owned_info)
        self._remote_participants[participant.identity] = participant
        return participant

    def __repr__(self) -> str:
        sid = "unknown"
        if self._first_sid_future.done():
            sid = self._first_sid_future.result()

        return f"rtc.Room(sid={sid}, name={self.name}, metadata={self.metadata}, connection_state={self._connection_state})"
