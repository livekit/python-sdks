import handle_pb2 as _handle_pb2
import participant_pb2 as _participant_pb2
import track_pb2 as _track_pb2
import video_frame_pb2 as _video_frame_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConnectionQuality(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    QUALITY_POOR: _ClassVar[ConnectionQuality]
    QUALITY_GOOD: _ClassVar[ConnectionQuality]
    QUALITY_EXCELLENT: _ClassVar[ConnectionQuality]

class ConnectionState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CONN_DISCONNECTED: _ClassVar[ConnectionState]
    CONN_CONNECTED: _ClassVar[ConnectionState]
    CONN_RECONNECTING: _ClassVar[ConnectionState]

class DataPacketKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    KIND_LOSSY: _ClassVar[DataPacketKind]
    KIND_RELIABLE: _ClassVar[DataPacketKind]
QUALITY_POOR: ConnectionQuality
QUALITY_GOOD: ConnectionQuality
QUALITY_EXCELLENT: ConnectionQuality
CONN_DISCONNECTED: ConnectionState
CONN_CONNECTED: ConnectionState
CONN_RECONNECTING: ConnectionState
KIND_LOSSY: DataPacketKind
KIND_RELIABLE: DataPacketKind

class ConnectRequest(_message.Message):
    __slots__ = ["url", "token", "options"]
    URL_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    url: str
    token: str
    options: RoomOptions
    def __init__(self, url: _Optional[str] = ..., token: _Optional[str] = ..., options: _Optional[_Union[RoomOptions, _Mapping]] = ...) -> None: ...

class ConnectResponse(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ...) -> None: ...

class ConnectCallback(_message.Message):
    __slots__ = ["async_id", "error", "room"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    error: str
    room: RoomInfo
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ..., error: _Optional[str] = ..., room: _Optional[_Union[RoomInfo, _Mapping]] = ...) -> None: ...

class DisconnectRequest(_message.Message):
    __slots__ = ["room_handle"]
    ROOM_HANDLE_FIELD_NUMBER: _ClassVar[int]
    room_handle: _handle_pb2.FfiHandleId
    def __init__(self, room_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ...) -> None: ...

class DisconnectResponse(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ...) -> None: ...

class DisconnectCallback(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ...) -> None: ...

class PublishTrackRequest(_message.Message):
    __slots__ = ["room_handle", "track_handle", "options"]
    ROOM_HANDLE_FIELD_NUMBER: _ClassVar[int]
    TRACK_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    room_handle: _handle_pb2.FfiHandleId
    track_handle: _handle_pb2.FfiHandleId
    options: TrackPublishOptions
    def __init__(self, room_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., track_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., options: _Optional[_Union[TrackPublishOptions, _Mapping]] = ...) -> None: ...

class PublishTrackResponse(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ...) -> None: ...

class PublishTrackCallback(_message.Message):
    __slots__ = ["async_id", "error", "publication"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    error: str
    publication: _track_pb2.TrackPublicationInfo
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ..., error: _Optional[str] = ..., publication: _Optional[_Union[_track_pb2.TrackPublicationInfo, _Mapping]] = ...) -> None: ...

class UnpublishTrackRequest(_message.Message):
    __slots__ = ["room_handle", "track_sid", "stop_on_unpublish"]
    ROOM_HANDLE_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    STOP_ON_UNPUBLISH_FIELD_NUMBER: _ClassVar[int]
    room_handle: _handle_pb2.FfiHandleId
    track_sid: str
    stop_on_unpublish: bool
    def __init__(self, room_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., track_sid: _Optional[str] = ..., stop_on_unpublish: bool = ...) -> None: ...

class UnpublishTrackResponse(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ...) -> None: ...

class UnpublishTrackCallback(_message.Message):
    __slots__ = ["async_id", "error"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    error: str
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class PublishDataRequest(_message.Message):
    __slots__ = ["room_handle", "data_ptr", "data_size", "kind", "destination_sids"]
    ROOM_HANDLE_FIELD_NUMBER: _ClassVar[int]
    DATA_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_SIZE_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_SIDS_FIELD_NUMBER: _ClassVar[int]
    room_handle: _handle_pb2.FfiHandleId
    data_ptr: int
    data_size: int
    kind: DataPacketKind
    destination_sids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, room_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., data_ptr: _Optional[int] = ..., data_size: _Optional[int] = ..., kind: _Optional[_Union[DataPacketKind, str]] = ..., destination_sids: _Optional[_Iterable[str]] = ...) -> None: ...

class PublishDataResponse(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ...) -> None: ...

class PublishDataCallback(_message.Message):
    __slots__ = ["async_id", "error"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    error: str
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class SetSubscribedRequest(_message.Message):
    __slots__ = ["room_handle", "subscribe", "participant_sid", "track_sid"]
    ROOM_HANDLE_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    room_handle: _handle_pb2.FfiHandleId
    subscribe: bool
    participant_sid: str
    track_sid: str
    def __init__(self, room_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., subscribe: bool = ..., participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ...) -> None: ...

class SetSubscribedResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class VideoEncoding(_message.Message):
    __slots__ = ["max_bitrate", "max_framerate"]
    MAX_BITRATE_FIELD_NUMBER: _ClassVar[int]
    MAX_FRAMERATE_FIELD_NUMBER: _ClassVar[int]
    max_bitrate: int
    max_framerate: float
    def __init__(self, max_bitrate: _Optional[int] = ..., max_framerate: _Optional[float] = ...) -> None: ...

class AudioEncoding(_message.Message):
    __slots__ = ["max_bitrate"]
    MAX_BITRATE_FIELD_NUMBER: _ClassVar[int]
    max_bitrate: int
    def __init__(self, max_bitrate: _Optional[int] = ...) -> None: ...

class TrackPublishOptions(_message.Message):
    __slots__ = ["video_encoding", "audio_encoding", "video_codec", "dtx", "red", "simulcast", "source"]
    VIDEO_ENCODING_FIELD_NUMBER: _ClassVar[int]
    AUDIO_ENCODING_FIELD_NUMBER: _ClassVar[int]
    VIDEO_CODEC_FIELD_NUMBER: _ClassVar[int]
    DTX_FIELD_NUMBER: _ClassVar[int]
    RED_FIELD_NUMBER: _ClassVar[int]
    SIMULCAST_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    video_encoding: VideoEncoding
    audio_encoding: AudioEncoding
    video_codec: _video_frame_pb2.VideoCodec
    dtx: bool
    red: bool
    simulcast: bool
    source: _track_pb2.TrackSource
    def __init__(self, video_encoding: _Optional[_Union[VideoEncoding, _Mapping]] = ..., audio_encoding: _Optional[_Union[AudioEncoding, _Mapping]] = ..., video_codec: _Optional[_Union[_video_frame_pb2.VideoCodec, str]] = ..., dtx: bool = ..., red: bool = ..., simulcast: bool = ..., source: _Optional[_Union[_track_pb2.TrackSource, str]] = ...) -> None: ...

class RoomOptions(_message.Message):
    __slots__ = ["auto_subscribe", "adaptive_stream", "dynacast"]
    AUTO_SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    ADAPTIVE_STREAM_FIELD_NUMBER: _ClassVar[int]
    DYNACAST_FIELD_NUMBER: _ClassVar[int]
    auto_subscribe: bool
    adaptive_stream: bool
    dynacast: bool
    def __init__(self, auto_subscribe: bool = ..., adaptive_stream: bool = ..., dynacast: bool = ...) -> None: ...

class RoomEvent(_message.Message):
    __slots__ = ["room_handle", "participant_connected", "participant_disconnected", "local_track_published", "local_track_unpublished", "track_published", "track_unpublished", "track_subscribed", "track_unsubscribed", "track_subscription_failed", "track_muted", "track_unmuted", "active_speakers_changed", "connection_quality_changed", "data_received", "connection_state_changed", "connected", "disconnected", "reconnecting", "reconnected"]
    ROOM_HANDLE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_CONNECTED_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_DISCONNECTED_FIELD_NUMBER: _ClassVar[int]
    LOCAL_TRACK_PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    LOCAL_TRACK_UNPUBLISHED_FIELD_NUMBER: _ClassVar[int]
    TRACK_PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    TRACK_UNPUBLISHED_FIELD_NUMBER: _ClassVar[int]
    TRACK_SUBSCRIBED_FIELD_NUMBER: _ClassVar[int]
    TRACK_UNSUBSCRIBED_FIELD_NUMBER: _ClassVar[int]
    TRACK_SUBSCRIPTION_FAILED_FIELD_NUMBER: _ClassVar[int]
    TRACK_MUTED_FIELD_NUMBER: _ClassVar[int]
    TRACK_UNMUTED_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SPEAKERS_CHANGED_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_QUALITY_CHANGED_FIELD_NUMBER: _ClassVar[int]
    DATA_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_STATE_CHANGED_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_FIELD_NUMBER: _ClassVar[int]
    DISCONNECTED_FIELD_NUMBER: _ClassVar[int]
    RECONNECTING_FIELD_NUMBER: _ClassVar[int]
    RECONNECTED_FIELD_NUMBER: _ClassVar[int]
    room_handle: _handle_pb2.FfiHandleId
    participant_connected: ParticipantConnected
    participant_disconnected: ParticipantDisconnected
    local_track_published: LocalTrackPublished
    local_track_unpublished: LocalTrackUnpublished
    track_published: TrackPublished
    track_unpublished: TrackUnpublished
    track_subscribed: TrackSubscribed
    track_unsubscribed: TrackUnsubscribed
    track_subscription_failed: TrackSubscriptionFailed
    track_muted: TrackMuted
    track_unmuted: TrackUnmuted
    active_speakers_changed: ActiveSpeakersChanged
    connection_quality_changed: ConnectionQualityChanged
    data_received: DataReceived
    connection_state_changed: ConnectionStateChanged
    connected: Connected
    disconnected: Disconnected
    reconnecting: Reconnecting
    reconnected: Reconnected
    def __init__(self, room_handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., participant_connected: _Optional[_Union[ParticipantConnected, _Mapping]] = ..., participant_disconnected: _Optional[_Union[ParticipantDisconnected, _Mapping]] = ..., local_track_published: _Optional[_Union[LocalTrackPublished, _Mapping]] = ..., local_track_unpublished: _Optional[_Union[LocalTrackUnpublished, _Mapping]] = ..., track_published: _Optional[_Union[TrackPublished, _Mapping]] = ..., track_unpublished: _Optional[_Union[TrackUnpublished, _Mapping]] = ..., track_subscribed: _Optional[_Union[TrackSubscribed, _Mapping]] = ..., track_unsubscribed: _Optional[_Union[TrackUnsubscribed, _Mapping]] = ..., track_subscription_failed: _Optional[_Union[TrackSubscriptionFailed, _Mapping]] = ..., track_muted: _Optional[_Union[TrackMuted, _Mapping]] = ..., track_unmuted: _Optional[_Union[TrackUnmuted, _Mapping]] = ..., active_speakers_changed: _Optional[_Union[ActiveSpeakersChanged, _Mapping]] = ..., connection_quality_changed: _Optional[_Union[ConnectionQualityChanged, _Mapping]] = ..., data_received: _Optional[_Union[DataReceived, _Mapping]] = ..., connection_state_changed: _Optional[_Union[ConnectionStateChanged, _Mapping]] = ..., connected: _Optional[_Union[Connected, _Mapping]] = ..., disconnected: _Optional[_Union[Disconnected, _Mapping]] = ..., reconnecting: _Optional[_Union[Reconnecting, _Mapping]] = ..., reconnected: _Optional[_Union[Reconnected, _Mapping]] = ...) -> None: ...

class RoomInfo(_message.Message):
    __slots__ = ["handle", "sid", "name", "metadata", "local_participant", "participants"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    SID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    sid: str
    name: str
    metadata: str
    local_participant: _participant_pb2.ParticipantInfo
    participants: _containers.RepeatedCompositeFieldContainer[_participant_pb2.ParticipantInfo]
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., sid: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., local_participant: _Optional[_Union[_participant_pb2.ParticipantInfo, _Mapping]] = ..., participants: _Optional[_Iterable[_Union[_participant_pb2.ParticipantInfo, _Mapping]]] = ...) -> None: ...

class ParticipantConnected(_message.Message):
    __slots__ = ["info"]
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: _participant_pb2.ParticipantInfo
    def __init__(self, info: _Optional[_Union[_participant_pb2.ParticipantInfo, _Mapping]] = ...) -> None: ...

class ParticipantDisconnected(_message.Message):
    __slots__ = ["info"]
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: _participant_pb2.ParticipantInfo
    def __init__(self, info: _Optional[_Union[_participant_pb2.ParticipantInfo, _Mapping]] = ...) -> None: ...

class LocalTrackPublished(_message.Message):
    __slots__ = ["publication", "track"]
    PUBLICATION_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    publication: _track_pb2.TrackPublicationInfo
    track: _track_pb2.TrackInfo
    def __init__(self, publication: _Optional[_Union[_track_pb2.TrackPublicationInfo, _Mapping]] = ..., track: _Optional[_Union[_track_pb2.TrackInfo, _Mapping]] = ...) -> None: ...

class LocalTrackUnpublished(_message.Message):
    __slots__ = ["publication_sid"]
    PUBLICATION_SID_FIELD_NUMBER: _ClassVar[int]
    publication_sid: str
    def __init__(self, publication_sid: _Optional[str] = ...) -> None: ...

class TrackPublished(_message.Message):
    __slots__ = ["participant_sid", "publication"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    publication: _track_pb2.TrackPublicationInfo
    def __init__(self, participant_sid: _Optional[str] = ..., publication: _Optional[_Union[_track_pb2.TrackPublicationInfo, _Mapping]] = ...) -> None: ...

class TrackUnpublished(_message.Message):
    __slots__ = ["participant_sid", "publication_sid"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_SID_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    publication_sid: str
    def __init__(self, participant_sid: _Optional[str] = ..., publication_sid: _Optional[str] = ...) -> None: ...

class TrackSubscribed(_message.Message):
    __slots__ = ["participant_sid", "track"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    track: _track_pb2.TrackInfo
    def __init__(self, participant_sid: _Optional[str] = ..., track: _Optional[_Union[_track_pb2.TrackInfo, _Mapping]] = ...) -> None: ...

class TrackUnsubscribed(_message.Message):
    __slots__ = ["participant_sid", "track_sid"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    track_sid: str
    def __init__(self, participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ...) -> None: ...

class TrackSubscriptionFailed(_message.Message):
    __slots__ = ["participant_sid", "track_sid", "error"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    track_sid: str
    error: str
    def __init__(self, participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class TrackMuted(_message.Message):
    __slots__ = ["participant_sid", "track_sid"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    track_sid: str
    def __init__(self, participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ...) -> None: ...

class TrackUnmuted(_message.Message):
    __slots__ = ["participant_sid", "track_sid"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    track_sid: str
    def __init__(self, participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ...) -> None: ...

class ActiveSpeakersChanged(_message.Message):
    __slots__ = ["participant_sids"]
    PARTICIPANT_SIDS_FIELD_NUMBER: _ClassVar[int]
    participant_sids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, participant_sids: _Optional[_Iterable[str]] = ...) -> None: ...

class ConnectionQualityChanged(_message.Message):
    __slots__ = ["participant_sid", "quality"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    quality: ConnectionQuality
    def __init__(self, participant_sid: _Optional[str] = ..., quality: _Optional[_Union[ConnectionQuality, str]] = ...) -> None: ...

class DataReceived(_message.Message):
    __slots__ = ["handle", "participant_sid", "data_ptr", "data_size", "kind"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    DATA_PTR_FIELD_NUMBER: _ClassVar[int]
    DATA_SIZE_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    handle: _handle_pb2.FfiHandleId
    participant_sid: str
    data_ptr: int
    data_size: int
    kind: DataPacketKind
    def __init__(self, handle: _Optional[_Union[_handle_pb2.FfiHandleId, _Mapping]] = ..., participant_sid: _Optional[str] = ..., data_ptr: _Optional[int] = ..., data_size: _Optional[int] = ..., kind: _Optional[_Union[DataPacketKind, str]] = ...) -> None: ...

class ConnectionStateChanged(_message.Message):
    __slots__ = ["state"]
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: ConnectionState
    def __init__(self, state: _Optional[_Union[ConnectionState, str]] = ...) -> None: ...

class Connected(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Disconnected(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Reconnecting(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Reconnected(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
