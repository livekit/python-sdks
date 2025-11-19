from . import models as _models
from .logger_pb import options as _options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SignalTarget(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PUBLISHER: _ClassVar[SignalTarget]
    SUBSCRIBER: _ClassVar[SignalTarget]

class StreamState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVE: _ClassVar[StreamState]
    PAUSED: _ClassVar[StreamState]

class CandidateProtocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UDP: _ClassVar[CandidateProtocol]
    TCP: _ClassVar[CandidateProtocol]
    TLS: _ClassVar[CandidateProtocol]
PUBLISHER: SignalTarget
SUBSCRIBER: SignalTarget
ACTIVE: StreamState
PAUSED: StreamState
UDP: CandidateProtocol
TCP: CandidateProtocol
TLS: CandidateProtocol

class SignalRequest(_message.Message):
    __slots__ = ("offer", "answer", "trickle", "add_track", "mute", "subscription", "track_setting", "leave", "update_layers", "subscription_permission", "sync_state", "simulate", "ping", "update_metadata", "ping_req", "update_audio_track", "update_video_track")
    OFFER_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    TRICKLE_FIELD_NUMBER: _ClassVar[int]
    ADD_TRACK_FIELD_NUMBER: _ClassVar[int]
    MUTE_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TRACK_SETTING_FIELD_NUMBER: _ClassVar[int]
    LEAVE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_LAYERS_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    SYNC_STATE_FIELD_NUMBER: _ClassVar[int]
    SIMULATE_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    UPDATE_METADATA_FIELD_NUMBER: _ClassVar[int]
    PING_REQ_FIELD_NUMBER: _ClassVar[int]
    UPDATE_AUDIO_TRACK_FIELD_NUMBER: _ClassVar[int]
    UPDATE_VIDEO_TRACK_FIELD_NUMBER: _ClassVar[int]
    offer: SessionDescription
    answer: SessionDescription
    trickle: TrickleRequest
    add_track: AddTrackRequest
    mute: MuteTrackRequest
    subscription: UpdateSubscription
    track_setting: UpdateTrackSettings
    leave: LeaveRequest
    update_layers: UpdateVideoLayers
    subscription_permission: SubscriptionPermission
    sync_state: SyncState
    simulate: SimulateScenario
    ping: int
    update_metadata: UpdateParticipantMetadata
    ping_req: Ping
    update_audio_track: UpdateLocalAudioTrack
    update_video_track: UpdateLocalVideoTrack
    def __init__(self, offer: _Optional[_Union[SessionDescription, _Mapping]] = ..., answer: _Optional[_Union[SessionDescription, _Mapping]] = ..., trickle: _Optional[_Union[TrickleRequest, _Mapping]] = ..., add_track: _Optional[_Union[AddTrackRequest, _Mapping]] = ..., mute: _Optional[_Union[MuteTrackRequest, _Mapping]] = ..., subscription: _Optional[_Union[UpdateSubscription, _Mapping]] = ..., track_setting: _Optional[_Union[UpdateTrackSettings, _Mapping]] = ..., leave: _Optional[_Union[LeaveRequest, _Mapping]] = ..., update_layers: _Optional[_Union[UpdateVideoLayers, _Mapping]] = ..., subscription_permission: _Optional[_Union[SubscriptionPermission, _Mapping]] = ..., sync_state: _Optional[_Union[SyncState, _Mapping]] = ..., simulate: _Optional[_Union[SimulateScenario, _Mapping]] = ..., ping: _Optional[int] = ..., update_metadata: _Optional[_Union[UpdateParticipantMetadata, _Mapping]] = ..., ping_req: _Optional[_Union[Ping, _Mapping]] = ..., update_audio_track: _Optional[_Union[UpdateLocalAudioTrack, _Mapping]] = ..., update_video_track: _Optional[_Union[UpdateLocalVideoTrack, _Mapping]] = ...) -> None: ...

class SignalResponse(_message.Message):
    __slots__ = ("join", "answer", "offer", "trickle", "update", "track_published", "leave", "mute", "speakers_changed", "room_update", "connection_quality", "stream_state_update", "subscribed_quality_update", "subscription_permission_update", "refresh_token", "track_unpublished", "pong", "reconnect", "pong_resp", "subscription_response", "request_response", "track_subscribed", "room_moved", "media_sections_requirement", "subscribed_audio_codec_update")
    JOIN_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    OFFER_FIELD_NUMBER: _ClassVar[int]
    TRICKLE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    TRACK_PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    LEAVE_FIELD_NUMBER: _ClassVar[int]
    MUTE_FIELD_NUMBER: _ClassVar[int]
    SPEAKERS_CHANGED_FIELD_NUMBER: _ClassVar[int]
    ROOM_UPDATE_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_QUALITY_FIELD_NUMBER: _ClassVar[int]
    STREAM_STATE_UPDATE_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_QUALITY_UPDATE_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_PERMISSION_UPDATE_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TRACK_UNPUBLISHED_FIELD_NUMBER: _ClassVar[int]
    PONG_FIELD_NUMBER: _ClassVar[int]
    RECONNECT_FIELD_NUMBER: _ClassVar[int]
    PONG_RESP_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    TRACK_SUBSCRIBED_FIELD_NUMBER: _ClassVar[int]
    ROOM_MOVED_FIELD_NUMBER: _ClassVar[int]
    MEDIA_SECTIONS_REQUIREMENT_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_AUDIO_CODEC_UPDATE_FIELD_NUMBER: _ClassVar[int]
    join: JoinResponse
    answer: SessionDescription
    offer: SessionDescription
    trickle: TrickleRequest
    update: ParticipantUpdate
    track_published: TrackPublishedResponse
    leave: LeaveRequest
    mute: MuteTrackRequest
    speakers_changed: SpeakersChanged
    room_update: RoomUpdate
    connection_quality: ConnectionQualityUpdate
    stream_state_update: StreamStateUpdate
    subscribed_quality_update: SubscribedQualityUpdate
    subscription_permission_update: SubscriptionPermissionUpdate
    refresh_token: str
    track_unpublished: TrackUnpublishedResponse
    pong: int
    reconnect: ReconnectResponse
    pong_resp: Pong
    subscription_response: SubscriptionResponse
    request_response: RequestResponse
    track_subscribed: TrackSubscribed
    room_moved: RoomMovedResponse
    media_sections_requirement: MediaSectionsRequirement
    subscribed_audio_codec_update: SubscribedAudioCodecUpdate
    def __init__(self, join: _Optional[_Union[JoinResponse, _Mapping]] = ..., answer: _Optional[_Union[SessionDescription, _Mapping]] = ..., offer: _Optional[_Union[SessionDescription, _Mapping]] = ..., trickle: _Optional[_Union[TrickleRequest, _Mapping]] = ..., update: _Optional[_Union[ParticipantUpdate, _Mapping]] = ..., track_published: _Optional[_Union[TrackPublishedResponse, _Mapping]] = ..., leave: _Optional[_Union[LeaveRequest, _Mapping]] = ..., mute: _Optional[_Union[MuteTrackRequest, _Mapping]] = ..., speakers_changed: _Optional[_Union[SpeakersChanged, _Mapping]] = ..., room_update: _Optional[_Union[RoomUpdate, _Mapping]] = ..., connection_quality: _Optional[_Union[ConnectionQualityUpdate, _Mapping]] = ..., stream_state_update: _Optional[_Union[StreamStateUpdate, _Mapping]] = ..., subscribed_quality_update: _Optional[_Union[SubscribedQualityUpdate, _Mapping]] = ..., subscription_permission_update: _Optional[_Union[SubscriptionPermissionUpdate, _Mapping]] = ..., refresh_token: _Optional[str] = ..., track_unpublished: _Optional[_Union[TrackUnpublishedResponse, _Mapping]] = ..., pong: _Optional[int] = ..., reconnect: _Optional[_Union[ReconnectResponse, _Mapping]] = ..., pong_resp: _Optional[_Union[Pong, _Mapping]] = ..., subscription_response: _Optional[_Union[SubscriptionResponse, _Mapping]] = ..., request_response: _Optional[_Union[RequestResponse, _Mapping]] = ..., track_subscribed: _Optional[_Union[TrackSubscribed, _Mapping]] = ..., room_moved: _Optional[_Union[RoomMovedResponse, _Mapping]] = ..., media_sections_requirement: _Optional[_Union[MediaSectionsRequirement, _Mapping]] = ..., subscribed_audio_codec_update: _Optional[_Union[SubscribedAudioCodecUpdate, _Mapping]] = ...) -> None: ...

class SimulcastCodec(_message.Message):
    __slots__ = ("codec", "cid", "layers", "video_layer_mode")
    CODEC_FIELD_NUMBER: _ClassVar[int]
    CID_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    VIDEO_LAYER_MODE_FIELD_NUMBER: _ClassVar[int]
    codec: str
    cid: str
    layers: _containers.RepeatedCompositeFieldContainer[_models.VideoLayer]
    video_layer_mode: _models.VideoLayer.Mode
    def __init__(self, codec: _Optional[str] = ..., cid: _Optional[str] = ..., layers: _Optional[_Iterable[_Union[_models.VideoLayer, _Mapping]]] = ..., video_layer_mode: _Optional[_Union[_models.VideoLayer.Mode, str]] = ...) -> None: ...

class AddTrackRequest(_message.Message):
    __slots__ = ("cid", "name", "type", "width", "height", "muted", "disable_dtx", "source", "layers", "simulcast_codecs", "sid", "stereo", "disable_red", "encryption", "stream", "backup_codec_policy", "audio_features")
    CID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    MUTED_FIELD_NUMBER: _ClassVar[int]
    DISABLE_DTX_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    SIMULCAST_CODECS_FIELD_NUMBER: _ClassVar[int]
    SID_FIELD_NUMBER: _ClassVar[int]
    STEREO_FIELD_NUMBER: _ClassVar[int]
    DISABLE_RED_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    BACKUP_CODEC_POLICY_FIELD_NUMBER: _ClassVar[int]
    AUDIO_FEATURES_FIELD_NUMBER: _ClassVar[int]
    cid: str
    name: str
    type: _models.TrackType
    width: int
    height: int
    muted: bool
    disable_dtx: bool
    source: _models.TrackSource
    layers: _containers.RepeatedCompositeFieldContainer[_models.VideoLayer]
    simulcast_codecs: _containers.RepeatedCompositeFieldContainer[SimulcastCodec]
    sid: str
    stereo: bool
    disable_red: bool
    encryption: _models.Encryption.Type
    stream: str
    backup_codec_policy: _models.BackupCodecPolicy
    audio_features: _containers.RepeatedScalarFieldContainer[_models.AudioTrackFeature]
    def __init__(self, cid: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[_models.TrackType, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., muted: bool = ..., disable_dtx: bool = ..., source: _Optional[_Union[_models.TrackSource, str]] = ..., layers: _Optional[_Iterable[_Union[_models.VideoLayer, _Mapping]]] = ..., simulcast_codecs: _Optional[_Iterable[_Union[SimulcastCodec, _Mapping]]] = ..., sid: _Optional[str] = ..., stereo: bool = ..., disable_red: bool = ..., encryption: _Optional[_Union[_models.Encryption.Type, str]] = ..., stream: _Optional[str] = ..., backup_codec_policy: _Optional[_Union[_models.BackupCodecPolicy, str]] = ..., audio_features: _Optional[_Iterable[_Union[_models.AudioTrackFeature, str]]] = ...) -> None: ...

class TrickleRequest(_message.Message):
    __slots__ = ("candidateInit", "target", "final")
    CANDIDATEINIT_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    FINAL_FIELD_NUMBER: _ClassVar[int]
    candidateInit: str
    target: SignalTarget
    final: bool
    def __init__(self, candidateInit: _Optional[str] = ..., target: _Optional[_Union[SignalTarget, str]] = ..., final: bool = ...) -> None: ...

class MuteTrackRequest(_message.Message):
    __slots__ = ("sid", "muted")
    SID_FIELD_NUMBER: _ClassVar[int]
    MUTED_FIELD_NUMBER: _ClassVar[int]
    sid: str
    muted: bool
    def __init__(self, sid: _Optional[str] = ..., muted: bool = ...) -> None: ...

class JoinResponse(_message.Message):
    __slots__ = ("room", "participant", "other_participants", "server_version", "ice_servers", "subscriber_primary", "alternative_url", "client_configuration", "server_region", "ping_timeout", "ping_interval", "server_info", "sif_trailer", "enabled_publish_codecs", "fast_publish")
    ROOM_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    OTHER_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    SERVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    ICE_SERVERS_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBER_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    ALTERNATIVE_URL_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SERVER_REGION_FIELD_NUMBER: _ClassVar[int]
    PING_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    PING_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    SERVER_INFO_FIELD_NUMBER: _ClassVar[int]
    SIF_TRAILER_FIELD_NUMBER: _ClassVar[int]
    ENABLED_PUBLISH_CODECS_FIELD_NUMBER: _ClassVar[int]
    FAST_PUBLISH_FIELD_NUMBER: _ClassVar[int]
    room: _models.Room
    participant: _models.ParticipantInfo
    other_participants: _containers.RepeatedCompositeFieldContainer[_models.ParticipantInfo]
    server_version: str
    ice_servers: _containers.RepeatedCompositeFieldContainer[ICEServer]
    subscriber_primary: bool
    alternative_url: str
    client_configuration: _models.ClientConfiguration
    server_region: str
    ping_timeout: int
    ping_interval: int
    server_info: _models.ServerInfo
    sif_trailer: bytes
    enabled_publish_codecs: _containers.RepeatedCompositeFieldContainer[_models.Codec]
    fast_publish: bool
    def __init__(self, room: _Optional[_Union[_models.Room, _Mapping]] = ..., participant: _Optional[_Union[_models.ParticipantInfo, _Mapping]] = ..., other_participants: _Optional[_Iterable[_Union[_models.ParticipantInfo, _Mapping]]] = ..., server_version: _Optional[str] = ..., ice_servers: _Optional[_Iterable[_Union[ICEServer, _Mapping]]] = ..., subscriber_primary: bool = ..., alternative_url: _Optional[str] = ..., client_configuration: _Optional[_Union[_models.ClientConfiguration, _Mapping]] = ..., server_region: _Optional[str] = ..., ping_timeout: _Optional[int] = ..., ping_interval: _Optional[int] = ..., server_info: _Optional[_Union[_models.ServerInfo, _Mapping]] = ..., sif_trailer: _Optional[bytes] = ..., enabled_publish_codecs: _Optional[_Iterable[_Union[_models.Codec, _Mapping]]] = ..., fast_publish: bool = ...) -> None: ...

class ReconnectResponse(_message.Message):
    __slots__ = ("ice_servers", "client_configuration", "server_info", "last_message_seq")
    ICE_SERVERS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SERVER_INFO_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_SEQ_FIELD_NUMBER: _ClassVar[int]
    ice_servers: _containers.RepeatedCompositeFieldContainer[ICEServer]
    client_configuration: _models.ClientConfiguration
    server_info: _models.ServerInfo
    last_message_seq: int
    def __init__(self, ice_servers: _Optional[_Iterable[_Union[ICEServer, _Mapping]]] = ..., client_configuration: _Optional[_Union[_models.ClientConfiguration, _Mapping]] = ..., server_info: _Optional[_Union[_models.ServerInfo, _Mapping]] = ..., last_message_seq: _Optional[int] = ...) -> None: ...

class TrackPublishedResponse(_message.Message):
    __slots__ = ("cid", "track")
    CID_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    cid: str
    track: _models.TrackInfo
    def __init__(self, cid: _Optional[str] = ..., track: _Optional[_Union[_models.TrackInfo, _Mapping]] = ...) -> None: ...

class TrackUnpublishedResponse(_message.Message):
    __slots__ = ("track_sid",)
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    track_sid: str
    def __init__(self, track_sid: _Optional[str] = ...) -> None: ...

class SessionDescription(_message.Message):
    __slots__ = ("type", "sdp", "id", "mid_to_track_id")
    class MidToTrackIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SDP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MID_TO_TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    type: str
    sdp: str
    id: int
    mid_to_track_id: _containers.ScalarMap[str, str]
    def __init__(self, type: _Optional[str] = ..., sdp: _Optional[str] = ..., id: _Optional[int] = ..., mid_to_track_id: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ParticipantUpdate(_message.Message):
    __slots__ = ("participants",)
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    participants: _containers.RepeatedCompositeFieldContainer[_models.ParticipantInfo]
    def __init__(self, participants: _Optional[_Iterable[_Union[_models.ParticipantInfo, _Mapping]]] = ...) -> None: ...

class UpdateSubscription(_message.Message):
    __slots__ = ("track_sids", "subscribe", "participant_tracks")
    TRACK_SIDS_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_TRACKS_FIELD_NUMBER: _ClassVar[int]
    track_sids: _containers.RepeatedScalarFieldContainer[str]
    subscribe: bool
    participant_tracks: _containers.RepeatedCompositeFieldContainer[_models.ParticipantTracks]
    def __init__(self, track_sids: _Optional[_Iterable[str]] = ..., subscribe: bool = ..., participant_tracks: _Optional[_Iterable[_Union[_models.ParticipantTracks, _Mapping]]] = ...) -> None: ...

class UpdateTrackSettings(_message.Message):
    __slots__ = ("track_sids", "disabled", "quality", "width", "height", "fps", "priority")
    TRACK_SIDS_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FPS_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    track_sids: _containers.RepeatedScalarFieldContainer[str]
    disabled: bool
    quality: _models.VideoQuality
    width: int
    height: int
    fps: int
    priority: int
    def __init__(self, track_sids: _Optional[_Iterable[str]] = ..., disabled: bool = ..., quality: _Optional[_Union[_models.VideoQuality, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., fps: _Optional[int] = ..., priority: _Optional[int] = ...) -> None: ...

class UpdateLocalAudioTrack(_message.Message):
    __slots__ = ("track_sid", "features")
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    track_sid: str
    features: _containers.RepeatedScalarFieldContainer[_models.AudioTrackFeature]
    def __init__(self, track_sid: _Optional[str] = ..., features: _Optional[_Iterable[_Union[_models.AudioTrackFeature, str]]] = ...) -> None: ...

class UpdateLocalVideoTrack(_message.Message):
    __slots__ = ("track_sid", "width", "height")
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    track_sid: str
    width: int
    height: int
    def __init__(self, track_sid: _Optional[str] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class LeaveRequest(_message.Message):
    __slots__ = ("can_reconnect", "reason", "action", "regions")
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DISCONNECT: _ClassVar[LeaveRequest.Action]
        RESUME: _ClassVar[LeaveRequest.Action]
        RECONNECT: _ClassVar[LeaveRequest.Action]
    DISCONNECT: LeaveRequest.Action
    RESUME: LeaveRequest.Action
    RECONNECT: LeaveRequest.Action
    CAN_RECONNECT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    can_reconnect: bool
    reason: _models.DisconnectReason
    action: LeaveRequest.Action
    regions: RegionSettings
    def __init__(self, can_reconnect: bool = ..., reason: _Optional[_Union[_models.DisconnectReason, str]] = ..., action: _Optional[_Union[LeaveRequest.Action, str]] = ..., regions: _Optional[_Union[RegionSettings, _Mapping]] = ...) -> None: ...

class UpdateVideoLayers(_message.Message):
    __slots__ = ("track_sid", "layers")
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    track_sid: str
    layers: _containers.RepeatedCompositeFieldContainer[_models.VideoLayer]
    def __init__(self, track_sid: _Optional[str] = ..., layers: _Optional[_Iterable[_Union[_models.VideoLayer, _Mapping]]] = ...) -> None: ...

class UpdateParticipantMetadata(_message.Message):
    __slots__ = ("metadata", "name", "attributes", "request_id")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    metadata: str
    name: str
    attributes: _containers.ScalarMap[str, str]
    request_id: int
    def __init__(self, metadata: _Optional[str] = ..., name: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ..., request_id: _Optional[int] = ...) -> None: ...

class ICEServer(_message.Message):
    __slots__ = ("urls", "username", "credential")
    URLS_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    urls: _containers.RepeatedScalarFieldContainer[str]
    username: str
    credential: str
    def __init__(self, urls: _Optional[_Iterable[str]] = ..., username: _Optional[str] = ..., credential: _Optional[str] = ...) -> None: ...

class SpeakersChanged(_message.Message):
    __slots__ = ("speakers",)
    SPEAKERS_FIELD_NUMBER: _ClassVar[int]
    speakers: _containers.RepeatedCompositeFieldContainer[_models.SpeakerInfo]
    def __init__(self, speakers: _Optional[_Iterable[_Union[_models.SpeakerInfo, _Mapping]]] = ...) -> None: ...

class RoomUpdate(_message.Message):
    __slots__ = ("room",)
    ROOM_FIELD_NUMBER: _ClassVar[int]
    room: _models.Room
    def __init__(self, room: _Optional[_Union[_models.Room, _Mapping]] = ...) -> None: ...

class ConnectionQualityInfo(_message.Message):
    __slots__ = ("participant_sid", "quality", "score")
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    quality: _models.ConnectionQuality
    score: float
    def __init__(self, participant_sid: _Optional[str] = ..., quality: _Optional[_Union[_models.ConnectionQuality, str]] = ..., score: _Optional[float] = ...) -> None: ...

class ConnectionQualityUpdate(_message.Message):
    __slots__ = ("updates",)
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    updates: _containers.RepeatedCompositeFieldContainer[ConnectionQualityInfo]
    def __init__(self, updates: _Optional[_Iterable[_Union[ConnectionQualityInfo, _Mapping]]] = ...) -> None: ...

class StreamStateInfo(_message.Message):
    __slots__ = ("participant_sid", "track_sid", "state")
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    track_sid: str
    state: StreamState
    def __init__(self, participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ..., state: _Optional[_Union[StreamState, str]] = ...) -> None: ...

class StreamStateUpdate(_message.Message):
    __slots__ = ("stream_states",)
    STREAM_STATES_FIELD_NUMBER: _ClassVar[int]
    stream_states: _containers.RepeatedCompositeFieldContainer[StreamStateInfo]
    def __init__(self, stream_states: _Optional[_Iterable[_Union[StreamStateInfo, _Mapping]]] = ...) -> None: ...

class SubscribedQuality(_message.Message):
    __slots__ = ("quality", "enabled")
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    quality: _models.VideoQuality
    enabled: bool
    def __init__(self, quality: _Optional[_Union[_models.VideoQuality, str]] = ..., enabled: bool = ...) -> None: ...

class SubscribedCodec(_message.Message):
    __slots__ = ("codec", "qualities")
    CODEC_FIELD_NUMBER: _ClassVar[int]
    QUALITIES_FIELD_NUMBER: _ClassVar[int]
    codec: str
    qualities: _containers.RepeatedCompositeFieldContainer[SubscribedQuality]
    def __init__(self, codec: _Optional[str] = ..., qualities: _Optional[_Iterable[_Union[SubscribedQuality, _Mapping]]] = ...) -> None: ...

class SubscribedQualityUpdate(_message.Message):
    __slots__ = ("track_sid", "subscribed_qualities", "subscribed_codecs")
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_QUALITIES_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_CODECS_FIELD_NUMBER: _ClassVar[int]
    track_sid: str
    subscribed_qualities: _containers.RepeatedCompositeFieldContainer[SubscribedQuality]
    subscribed_codecs: _containers.RepeatedCompositeFieldContainer[SubscribedCodec]
    def __init__(self, track_sid: _Optional[str] = ..., subscribed_qualities: _Optional[_Iterable[_Union[SubscribedQuality, _Mapping]]] = ..., subscribed_codecs: _Optional[_Iterable[_Union[SubscribedCodec, _Mapping]]] = ...) -> None: ...

class SubscribedAudioCodecUpdate(_message.Message):
    __slots__ = ("track_sid", "subscribed_audio_codecs")
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_AUDIO_CODECS_FIELD_NUMBER: _ClassVar[int]
    track_sid: str
    subscribed_audio_codecs: _containers.RepeatedCompositeFieldContainer[_models.SubscribedAudioCodec]
    def __init__(self, track_sid: _Optional[str] = ..., subscribed_audio_codecs: _Optional[_Iterable[_Union[_models.SubscribedAudioCodec, _Mapping]]] = ...) -> None: ...

class TrackPermission(_message.Message):
    __slots__ = ("participant_sid", "all_tracks", "track_sids", "participant_identity")
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    ALL_TRACKS_FIELD_NUMBER: _ClassVar[int]
    TRACK_SIDS_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    all_tracks: bool
    track_sids: _containers.RepeatedScalarFieldContainer[str]
    participant_identity: str
    def __init__(self, participant_sid: _Optional[str] = ..., all_tracks: bool = ..., track_sids: _Optional[_Iterable[str]] = ..., participant_identity: _Optional[str] = ...) -> None: ...

class SubscriptionPermission(_message.Message):
    __slots__ = ("all_participants", "track_permissions")
    ALL_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    TRACK_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    all_participants: bool
    track_permissions: _containers.RepeatedCompositeFieldContainer[TrackPermission]
    def __init__(self, all_participants: bool = ..., track_permissions: _Optional[_Iterable[_Union[TrackPermission, _Mapping]]] = ...) -> None: ...

class SubscriptionPermissionUpdate(_message.Message):
    __slots__ = ("participant_sid", "track_sid", "allowed")
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    track_sid: str
    allowed: bool
    def __init__(self, participant_sid: _Optional[str] = ..., track_sid: _Optional[str] = ..., allowed: bool = ...) -> None: ...

class RoomMovedResponse(_message.Message):
    __slots__ = ("room", "token", "participant", "other_participants")
    ROOM_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    OTHER_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    room: _models.Room
    token: str
    participant: _models.ParticipantInfo
    other_participants: _containers.RepeatedCompositeFieldContainer[_models.ParticipantInfo]
    def __init__(self, room: _Optional[_Union[_models.Room, _Mapping]] = ..., token: _Optional[str] = ..., participant: _Optional[_Union[_models.ParticipantInfo, _Mapping]] = ..., other_participants: _Optional[_Iterable[_Union[_models.ParticipantInfo, _Mapping]]] = ...) -> None: ...

class SyncState(_message.Message):
    __slots__ = ("answer", "subscription", "publish_tracks", "data_channels", "offer", "track_sids_disabled", "datachannel_receive_states")
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TRACKS_FIELD_NUMBER: _ClassVar[int]
    DATA_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    OFFER_FIELD_NUMBER: _ClassVar[int]
    TRACK_SIDS_DISABLED_FIELD_NUMBER: _ClassVar[int]
    DATACHANNEL_RECEIVE_STATES_FIELD_NUMBER: _ClassVar[int]
    answer: SessionDescription
    subscription: UpdateSubscription
    publish_tracks: _containers.RepeatedCompositeFieldContainer[TrackPublishedResponse]
    data_channels: _containers.RepeatedCompositeFieldContainer[DataChannelInfo]
    offer: SessionDescription
    track_sids_disabled: _containers.RepeatedScalarFieldContainer[str]
    datachannel_receive_states: _containers.RepeatedCompositeFieldContainer[DataChannelReceiveState]
    def __init__(self, answer: _Optional[_Union[SessionDescription, _Mapping]] = ..., subscription: _Optional[_Union[UpdateSubscription, _Mapping]] = ..., publish_tracks: _Optional[_Iterable[_Union[TrackPublishedResponse, _Mapping]]] = ..., data_channels: _Optional[_Iterable[_Union[DataChannelInfo, _Mapping]]] = ..., offer: _Optional[_Union[SessionDescription, _Mapping]] = ..., track_sids_disabled: _Optional[_Iterable[str]] = ..., datachannel_receive_states: _Optional[_Iterable[_Union[DataChannelReceiveState, _Mapping]]] = ...) -> None: ...

class DataChannelReceiveState(_message.Message):
    __slots__ = ("publisher_sid", "last_seq")
    PUBLISHER_SID_FIELD_NUMBER: _ClassVar[int]
    LAST_SEQ_FIELD_NUMBER: _ClassVar[int]
    publisher_sid: str
    last_seq: int
    def __init__(self, publisher_sid: _Optional[str] = ..., last_seq: _Optional[int] = ...) -> None: ...

class DataChannelInfo(_message.Message):
    __slots__ = ("label", "id", "target")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    label: str
    id: int
    target: SignalTarget
    def __init__(self, label: _Optional[str] = ..., id: _Optional[int] = ..., target: _Optional[_Union[SignalTarget, str]] = ...) -> None: ...

class SimulateScenario(_message.Message):
    __slots__ = ("speaker_update", "node_failure", "migration", "server_leave", "switch_candidate_protocol", "subscriber_bandwidth", "disconnect_signal_on_resume", "disconnect_signal_on_resume_no_messages", "leave_request_full_reconnect")
    SPEAKER_UPDATE_FIELD_NUMBER: _ClassVar[int]
    NODE_FAILURE_FIELD_NUMBER: _ClassVar[int]
    MIGRATION_FIELD_NUMBER: _ClassVar[int]
    SERVER_LEAVE_FIELD_NUMBER: _ClassVar[int]
    SWITCH_CANDIDATE_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBER_BANDWIDTH_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_SIGNAL_ON_RESUME_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_SIGNAL_ON_RESUME_NO_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    LEAVE_REQUEST_FULL_RECONNECT_FIELD_NUMBER: _ClassVar[int]
    speaker_update: int
    node_failure: bool
    migration: bool
    server_leave: bool
    switch_candidate_protocol: CandidateProtocol
    subscriber_bandwidth: int
    disconnect_signal_on_resume: bool
    disconnect_signal_on_resume_no_messages: bool
    leave_request_full_reconnect: bool
    def __init__(self, speaker_update: _Optional[int] = ..., node_failure: bool = ..., migration: bool = ..., server_leave: bool = ..., switch_candidate_protocol: _Optional[_Union[CandidateProtocol, str]] = ..., subscriber_bandwidth: _Optional[int] = ..., disconnect_signal_on_resume: bool = ..., disconnect_signal_on_resume_no_messages: bool = ..., leave_request_full_reconnect: bool = ...) -> None: ...

class Ping(_message.Message):
    __slots__ = ("timestamp", "rtt")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RTT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    rtt: int
    def __init__(self, timestamp: _Optional[int] = ..., rtt: _Optional[int] = ...) -> None: ...

class Pong(_message.Message):
    __slots__ = ("last_ping_timestamp", "timestamp")
    LAST_PING_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    last_ping_timestamp: int
    timestamp: int
    def __init__(self, last_ping_timestamp: _Optional[int] = ..., timestamp: _Optional[int] = ...) -> None: ...

class RegionSettings(_message.Message):
    __slots__ = ("regions",)
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    regions: _containers.RepeatedCompositeFieldContainer[RegionInfo]
    def __init__(self, regions: _Optional[_Iterable[_Union[RegionInfo, _Mapping]]] = ...) -> None: ...

class RegionInfo(_message.Message):
    __slots__ = ("region", "url", "distance")
    REGION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    region: str
    url: str
    distance: int
    def __init__(self, region: _Optional[str] = ..., url: _Optional[str] = ..., distance: _Optional[int] = ...) -> None: ...

class SubscriptionResponse(_message.Message):
    __slots__ = ("track_sid", "err")
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    ERR_FIELD_NUMBER: _ClassVar[int]
    track_sid: str
    err: _models.SubscriptionError
    def __init__(self, track_sid: _Optional[str] = ..., err: _Optional[_Union[_models.SubscriptionError, str]] = ...) -> None: ...

class RequestResponse(_message.Message):
    __slots__ = ("request_id", "reason", "message", "trickle", "add_track", "mute", "update_metadata", "update_audio_track", "update_video_track")
    class Reason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[RequestResponse.Reason]
        NOT_FOUND: _ClassVar[RequestResponse.Reason]
        NOT_ALLOWED: _ClassVar[RequestResponse.Reason]
        LIMIT_EXCEEDED: _ClassVar[RequestResponse.Reason]
        QUEUED: _ClassVar[RequestResponse.Reason]
        UNSUPPORTED_TYPE: _ClassVar[RequestResponse.Reason]
        UNCLASSIFIED_ERROR: _ClassVar[RequestResponse.Reason]
    OK: RequestResponse.Reason
    NOT_FOUND: RequestResponse.Reason
    NOT_ALLOWED: RequestResponse.Reason
    LIMIT_EXCEEDED: RequestResponse.Reason
    QUEUED: RequestResponse.Reason
    UNSUPPORTED_TYPE: RequestResponse.Reason
    UNCLASSIFIED_ERROR: RequestResponse.Reason
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRICKLE_FIELD_NUMBER: _ClassVar[int]
    ADD_TRACK_FIELD_NUMBER: _ClassVar[int]
    MUTE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_METADATA_FIELD_NUMBER: _ClassVar[int]
    UPDATE_AUDIO_TRACK_FIELD_NUMBER: _ClassVar[int]
    UPDATE_VIDEO_TRACK_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    reason: RequestResponse.Reason
    message: str
    trickle: TrickleRequest
    add_track: AddTrackRequest
    mute: MuteTrackRequest
    update_metadata: UpdateParticipantMetadata
    update_audio_track: UpdateLocalAudioTrack
    update_video_track: UpdateLocalVideoTrack
    def __init__(self, request_id: _Optional[int] = ..., reason: _Optional[_Union[RequestResponse.Reason, str]] = ..., message: _Optional[str] = ..., trickle: _Optional[_Union[TrickleRequest, _Mapping]] = ..., add_track: _Optional[_Union[AddTrackRequest, _Mapping]] = ..., mute: _Optional[_Union[MuteTrackRequest, _Mapping]] = ..., update_metadata: _Optional[_Union[UpdateParticipantMetadata, _Mapping]] = ..., update_audio_track: _Optional[_Union[UpdateLocalAudioTrack, _Mapping]] = ..., update_video_track: _Optional[_Union[UpdateLocalVideoTrack, _Mapping]] = ...) -> None: ...

class TrackSubscribed(_message.Message):
    __slots__ = ("track_sid",)
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    track_sid: str
    def __init__(self, track_sid: _Optional[str] = ...) -> None: ...

class ConnectionSettings(_message.Message):
    __slots__ = ("auto_subscribe", "adaptive_stream", "subscriber_allow_pause", "disable_ice_lite")
    AUTO_SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    ADAPTIVE_STREAM_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBER_ALLOW_PAUSE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_ICE_LITE_FIELD_NUMBER: _ClassVar[int]
    auto_subscribe: bool
    adaptive_stream: bool
    subscriber_allow_pause: bool
    disable_ice_lite: bool
    def __init__(self, auto_subscribe: bool = ..., adaptive_stream: bool = ..., subscriber_allow_pause: bool = ..., disable_ice_lite: bool = ...) -> None: ...

class JoinRequest(_message.Message):
    __slots__ = ("client_info", "connection_settings", "metadata", "participant_attributes", "add_track_requests", "publisher_offer", "reconnect", "reconnect_reason", "participant_sid", "sync_state")
    class ParticipantAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CLIENT_INFO_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    ADD_TRACK_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    PUBLISHER_OFFER_FIELD_NUMBER: _ClassVar[int]
    RECONNECT_FIELD_NUMBER: _ClassVar[int]
    RECONNECT_REASON_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    SYNC_STATE_FIELD_NUMBER: _ClassVar[int]
    client_info: _models.ClientInfo
    connection_settings: ConnectionSettings
    metadata: str
    participant_attributes: _containers.ScalarMap[str, str]
    add_track_requests: _containers.RepeatedCompositeFieldContainer[AddTrackRequest]
    publisher_offer: SessionDescription
    reconnect: bool
    reconnect_reason: _models.ReconnectReason
    participant_sid: str
    sync_state: SyncState
    def __init__(self, client_info: _Optional[_Union[_models.ClientInfo, _Mapping]] = ..., connection_settings: _Optional[_Union[ConnectionSettings, _Mapping]] = ..., metadata: _Optional[str] = ..., participant_attributes: _Optional[_Mapping[str, str]] = ..., add_track_requests: _Optional[_Iterable[_Union[AddTrackRequest, _Mapping]]] = ..., publisher_offer: _Optional[_Union[SessionDescription, _Mapping]] = ..., reconnect: bool = ..., reconnect_reason: _Optional[_Union[_models.ReconnectReason, str]] = ..., participant_sid: _Optional[str] = ..., sync_state: _Optional[_Union[SyncState, _Mapping]] = ...) -> None: ...

class WrappedJoinRequest(_message.Message):
    __slots__ = ("compression", "join_request")
    class Compression(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[WrappedJoinRequest.Compression]
        GZIP: _ClassVar[WrappedJoinRequest.Compression]
    NONE: WrappedJoinRequest.Compression
    GZIP: WrappedJoinRequest.Compression
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    JOIN_REQUEST_FIELD_NUMBER: _ClassVar[int]
    compression: WrappedJoinRequest.Compression
    join_request: bytes
    def __init__(self, compression: _Optional[_Union[WrappedJoinRequest.Compression, str]] = ..., join_request: _Optional[bytes] = ...) -> None: ...

class MediaSectionsRequirement(_message.Message):
    __slots__ = ("num_audios", "num_videos")
    NUM_AUDIOS_FIELD_NUMBER: _ClassVar[int]
    NUM_VIDEOS_FIELD_NUMBER: _ClassVar[int]
    num_audios: int
    num_videos: int
    def __init__(self, num_audios: _Optional[int] = ..., num_videos: _Optional[int] = ...) -> None: ...
