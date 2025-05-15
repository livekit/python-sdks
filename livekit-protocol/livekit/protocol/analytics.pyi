from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import models as _models
from . import egress as _egress
from . import ingress as _ingress
from . import sip as _sip
from . import room as _room
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UPSTREAM: _ClassVar[StreamType]
    DOWNSTREAM: _ClassVar[StreamType]

class AnalyticsEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROOM_CREATED: _ClassVar[AnalyticsEventType]
    ROOM_ENDED: _ClassVar[AnalyticsEventType]
    PARTICIPANT_JOINED: _ClassVar[AnalyticsEventType]
    PARTICIPANT_LEFT: _ClassVar[AnalyticsEventType]
    TRACK_PUBLISHED: _ClassVar[AnalyticsEventType]
    TRACK_PUBLISH_REQUESTED: _ClassVar[AnalyticsEventType]
    TRACK_UNPUBLISHED: _ClassVar[AnalyticsEventType]
    TRACK_SUBSCRIBED: _ClassVar[AnalyticsEventType]
    TRACK_SUBSCRIBE_REQUESTED: _ClassVar[AnalyticsEventType]
    TRACK_SUBSCRIBE_FAILED: _ClassVar[AnalyticsEventType]
    TRACK_UNSUBSCRIBED: _ClassVar[AnalyticsEventType]
    TRACK_PUBLISHED_UPDATE: _ClassVar[AnalyticsEventType]
    TRACK_MUTED: _ClassVar[AnalyticsEventType]
    TRACK_UNMUTED: _ClassVar[AnalyticsEventType]
    TRACK_PUBLISH_STATS: _ClassVar[AnalyticsEventType]
    TRACK_SUBSCRIBE_STATS: _ClassVar[AnalyticsEventType]
    PARTICIPANT_ACTIVE: _ClassVar[AnalyticsEventType]
    PARTICIPANT_RESUMED: _ClassVar[AnalyticsEventType]
    EGRESS_STARTED: _ClassVar[AnalyticsEventType]
    EGRESS_ENDED: _ClassVar[AnalyticsEventType]
    EGRESS_UPDATED: _ClassVar[AnalyticsEventType]
    TRACK_MAX_SUBSCRIBED_VIDEO_QUALITY: _ClassVar[AnalyticsEventType]
    RECONNECTED: _ClassVar[AnalyticsEventType]
    INGRESS_CREATED: _ClassVar[AnalyticsEventType]
    INGRESS_DELETED: _ClassVar[AnalyticsEventType]
    INGRESS_STARTED: _ClassVar[AnalyticsEventType]
    INGRESS_ENDED: _ClassVar[AnalyticsEventType]
    INGRESS_UPDATED: _ClassVar[AnalyticsEventType]
    SIP_INBOUND_TRUNK_CREATED: _ClassVar[AnalyticsEventType]
    SIP_INBOUND_TRUNK_DELETED: _ClassVar[AnalyticsEventType]
    SIP_OUTBOUND_TRUNK_CREATED: _ClassVar[AnalyticsEventType]
    SIP_OUTBOUND_TRUNK_DELETED: _ClassVar[AnalyticsEventType]
    SIP_DISPATCH_RULE_CREATED: _ClassVar[AnalyticsEventType]
    SIP_DISPATCH_RULE_DELETED: _ClassVar[AnalyticsEventType]
    SIP_PARTICIPANT_CREATED: _ClassVar[AnalyticsEventType]
    SIP_CALL_INCOMING: _ClassVar[AnalyticsEventType]
    SIP_CALL_STARTED: _ClassVar[AnalyticsEventType]
    SIP_CALL_ENDED: _ClassVar[AnalyticsEventType]
    SIP_TRANSFER_REQUESTED: _ClassVar[AnalyticsEventType]
    SIP_TRANSFER_COMPLETE: _ClassVar[AnalyticsEventType]
    REPORT: _ClassVar[AnalyticsEventType]
    API_CALL: _ClassVar[AnalyticsEventType]
    WEBHOOK: _ClassVar[AnalyticsEventType]
UPSTREAM: StreamType
DOWNSTREAM: StreamType
ROOM_CREATED: AnalyticsEventType
ROOM_ENDED: AnalyticsEventType
PARTICIPANT_JOINED: AnalyticsEventType
PARTICIPANT_LEFT: AnalyticsEventType
TRACK_PUBLISHED: AnalyticsEventType
TRACK_PUBLISH_REQUESTED: AnalyticsEventType
TRACK_UNPUBLISHED: AnalyticsEventType
TRACK_SUBSCRIBED: AnalyticsEventType
TRACK_SUBSCRIBE_REQUESTED: AnalyticsEventType
TRACK_SUBSCRIBE_FAILED: AnalyticsEventType
TRACK_UNSUBSCRIBED: AnalyticsEventType
TRACK_PUBLISHED_UPDATE: AnalyticsEventType
TRACK_MUTED: AnalyticsEventType
TRACK_UNMUTED: AnalyticsEventType
TRACK_PUBLISH_STATS: AnalyticsEventType
TRACK_SUBSCRIBE_STATS: AnalyticsEventType
PARTICIPANT_ACTIVE: AnalyticsEventType
PARTICIPANT_RESUMED: AnalyticsEventType
EGRESS_STARTED: AnalyticsEventType
EGRESS_ENDED: AnalyticsEventType
EGRESS_UPDATED: AnalyticsEventType
TRACK_MAX_SUBSCRIBED_VIDEO_QUALITY: AnalyticsEventType
RECONNECTED: AnalyticsEventType
INGRESS_CREATED: AnalyticsEventType
INGRESS_DELETED: AnalyticsEventType
INGRESS_STARTED: AnalyticsEventType
INGRESS_ENDED: AnalyticsEventType
INGRESS_UPDATED: AnalyticsEventType
SIP_INBOUND_TRUNK_CREATED: AnalyticsEventType
SIP_INBOUND_TRUNK_DELETED: AnalyticsEventType
SIP_OUTBOUND_TRUNK_CREATED: AnalyticsEventType
SIP_OUTBOUND_TRUNK_DELETED: AnalyticsEventType
SIP_DISPATCH_RULE_CREATED: AnalyticsEventType
SIP_DISPATCH_RULE_DELETED: AnalyticsEventType
SIP_PARTICIPANT_CREATED: AnalyticsEventType
SIP_CALL_INCOMING: AnalyticsEventType
SIP_CALL_STARTED: AnalyticsEventType
SIP_CALL_ENDED: AnalyticsEventType
SIP_TRANSFER_REQUESTED: AnalyticsEventType
SIP_TRANSFER_COMPLETE: AnalyticsEventType
REPORT: AnalyticsEventType
API_CALL: AnalyticsEventType
WEBHOOK: AnalyticsEventType

class AnalyticsVideoLayer(_message.Message):
    __slots__ = ("layer", "packets", "bytes", "frames")
    LAYER_FIELD_NUMBER: _ClassVar[int]
    PACKETS_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    layer: int
    packets: int
    bytes: int
    frames: int
    def __init__(self, layer: _Optional[int] = ..., packets: _Optional[int] = ..., bytes: _Optional[int] = ..., frames: _Optional[int] = ...) -> None: ...

class AnalyticsStream(_message.Message):
    __slots__ = ("ssrc", "primary_packets", "primary_bytes", "retransmit_packets", "retransmit_bytes", "padding_packets", "padding_bytes", "packets_lost", "frames", "rtt", "jitter", "nacks", "plis", "firs", "video_layers", "start_time", "end_time", "packets_out_of_order")
    SSRC_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_PACKETS_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_BYTES_FIELD_NUMBER: _ClassVar[int]
    RETRANSMIT_PACKETS_FIELD_NUMBER: _ClassVar[int]
    RETRANSMIT_BYTES_FIELD_NUMBER: _ClassVar[int]
    PADDING_PACKETS_FIELD_NUMBER: _ClassVar[int]
    PADDING_BYTES_FIELD_NUMBER: _ClassVar[int]
    PACKETS_LOST_FIELD_NUMBER: _ClassVar[int]
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    RTT_FIELD_NUMBER: _ClassVar[int]
    JITTER_FIELD_NUMBER: _ClassVar[int]
    NACKS_FIELD_NUMBER: _ClassVar[int]
    PLIS_FIELD_NUMBER: _ClassVar[int]
    FIRS_FIELD_NUMBER: _ClassVar[int]
    VIDEO_LAYERS_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    PACKETS_OUT_OF_ORDER_FIELD_NUMBER: _ClassVar[int]
    ssrc: int
    primary_packets: int
    primary_bytes: int
    retransmit_packets: int
    retransmit_bytes: int
    padding_packets: int
    padding_bytes: int
    packets_lost: int
    frames: int
    rtt: int
    jitter: int
    nacks: int
    plis: int
    firs: int
    video_layers: _containers.RepeatedCompositeFieldContainer[AnalyticsVideoLayer]
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    packets_out_of_order: int
    def __init__(self, ssrc: _Optional[int] = ..., primary_packets: _Optional[int] = ..., primary_bytes: _Optional[int] = ..., retransmit_packets: _Optional[int] = ..., retransmit_bytes: _Optional[int] = ..., padding_packets: _Optional[int] = ..., padding_bytes: _Optional[int] = ..., packets_lost: _Optional[int] = ..., frames: _Optional[int] = ..., rtt: _Optional[int] = ..., jitter: _Optional[int] = ..., nacks: _Optional[int] = ..., plis: _Optional[int] = ..., firs: _Optional[int] = ..., video_layers: _Optional[_Iterable[_Union[AnalyticsVideoLayer, _Mapping]]] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., packets_out_of_order: _Optional[int] = ...) -> None: ...

class AnalyticsStat(_message.Message):
    __slots__ = ("id", "analytics_key", "kind", "time_stamp", "node", "room_id", "room_name", "participant_id", "track_id", "score", "streams", "mime", "min_score", "median_score")
    ID_FIELD_NUMBER: _ClassVar[int]
    ANALYTICS_KEY_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ID_FIELD_NUMBER: _ClassVar[int]
    TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    STREAMS_FIELD_NUMBER: _ClassVar[int]
    MIME_FIELD_NUMBER: _ClassVar[int]
    MIN_SCORE_FIELD_NUMBER: _ClassVar[int]
    MEDIAN_SCORE_FIELD_NUMBER: _ClassVar[int]
    id: str
    analytics_key: str
    kind: StreamType
    time_stamp: _timestamp_pb2.Timestamp
    node: str
    room_id: str
    room_name: str
    participant_id: str
    track_id: str
    score: float
    streams: _containers.RepeatedCompositeFieldContainer[AnalyticsStream]
    mime: str
    min_score: float
    median_score: float
    def __init__(self, id: _Optional[str] = ..., analytics_key: _Optional[str] = ..., kind: _Optional[_Union[StreamType, str]] = ..., time_stamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., node: _Optional[str] = ..., room_id: _Optional[str] = ..., room_name: _Optional[str] = ..., participant_id: _Optional[str] = ..., track_id: _Optional[str] = ..., score: _Optional[float] = ..., streams: _Optional[_Iterable[_Union[AnalyticsStream, _Mapping]]] = ..., mime: _Optional[str] = ..., min_score: _Optional[float] = ..., median_score: _Optional[float] = ...) -> None: ...

class AnalyticsStats(_message.Message):
    __slots__ = ("stats",)
    STATS_FIELD_NUMBER: _ClassVar[int]
    stats: _containers.RepeatedCompositeFieldContainer[AnalyticsStat]
    def __init__(self, stats: _Optional[_Iterable[_Union[AnalyticsStat, _Mapping]]] = ...) -> None: ...

class AnalyticsClientMeta(_message.Message):
    __slots__ = ("region", "node", "client_addr", "client_connect_time", "connection_type", "reconnect_reason", "geo_hash", "country", "isp_asn")
    REGION_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ADDR_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CONNECT_TIME_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    RECONNECT_REASON_FIELD_NUMBER: _ClassVar[int]
    GEO_HASH_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    ISP_ASN_FIELD_NUMBER: _ClassVar[int]
    region: str
    node: str
    client_addr: str
    client_connect_time: int
    connection_type: str
    reconnect_reason: _models.ReconnectReason
    geo_hash: str
    country: str
    isp_asn: int
    def __init__(self, region: _Optional[str] = ..., node: _Optional[str] = ..., client_addr: _Optional[str] = ..., client_connect_time: _Optional[int] = ..., connection_type: _Optional[str] = ..., reconnect_reason: _Optional[_Union[_models.ReconnectReason, str]] = ..., geo_hash: _Optional[str] = ..., country: _Optional[str] = ..., isp_asn: _Optional[int] = ...) -> None: ...

class AnalyticsEvent(_message.Message):
    __slots__ = ("id", "type", "timestamp", "room_id", "room", "participant_id", "participant", "track_id", "track", "analytics_key", "client_info", "client_meta", "egress_id", "ingress_id", "max_subscribed_video_quality", "publisher", "mime", "egress", "ingress", "error", "rtp_stats", "video_layer", "node_id", "sip_call_id", "sip_call", "sip_trunk_id", "sip_inbound_trunk", "sip_outbound_trunk", "sip_dispatch_rule_id", "sip_dispatch_rule", "sip_transfer", "report", "api_call", "webhook")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    ANALYTICS_KEY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_INFO_FIELD_NUMBER: _ClassVar[int]
    CLIENT_META_FIELD_NUMBER: _ClassVar[int]
    EGRESS_ID_FIELD_NUMBER: _ClassVar[int]
    INGRESS_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_SUBSCRIBED_VIDEO_QUALITY_FIELD_NUMBER: _ClassVar[int]
    PUBLISHER_FIELD_NUMBER: _ClassVar[int]
    MIME_FIELD_NUMBER: _ClassVar[int]
    EGRESS_FIELD_NUMBER: _ClassVar[int]
    INGRESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RTP_STATS_FIELD_NUMBER: _ClassVar[int]
    VIDEO_LAYER_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    SIP_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    SIP_CALL_FIELD_NUMBER: _ClassVar[int]
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    SIP_INBOUND_TRUNK_FIELD_NUMBER: _ClassVar[int]
    SIP_OUTBOUND_TRUNK_FIELD_NUMBER: _ClassVar[int]
    SIP_DISPATCH_RULE_ID_FIELD_NUMBER: _ClassVar[int]
    SIP_DISPATCH_RULE_FIELD_NUMBER: _ClassVar[int]
    SIP_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    API_CALL_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: AnalyticsEventType
    timestamp: _timestamp_pb2.Timestamp
    room_id: str
    room: _models.Room
    participant_id: str
    participant: _models.ParticipantInfo
    track_id: str
    track: _models.TrackInfo
    analytics_key: str
    client_info: _models.ClientInfo
    client_meta: AnalyticsClientMeta
    egress_id: str
    ingress_id: str
    max_subscribed_video_quality: _models.VideoQuality
    publisher: _models.ParticipantInfo
    mime: str
    egress: _egress.EgressInfo
    ingress: _ingress.IngressInfo
    error: str
    rtp_stats: _models.RTPStats
    video_layer: int
    node_id: str
    sip_call_id: str
    sip_call: _sip.SIPCallInfo
    sip_trunk_id: str
    sip_inbound_trunk: _sip.SIPInboundTrunkInfo
    sip_outbound_trunk: _sip.SIPOutboundTrunkInfo
    sip_dispatch_rule_id: str
    sip_dispatch_rule: _sip.SIPDispatchRuleInfo
    sip_transfer: _sip.SIPTransferInfo
    report: ReportInfo
    api_call: APICallInfo
    webhook: WebhookInfo
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[AnalyticsEventType, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., room_id: _Optional[str] = ..., room: _Optional[_Union[_models.Room, _Mapping]] = ..., participant_id: _Optional[str] = ..., participant: _Optional[_Union[_models.ParticipantInfo, _Mapping]] = ..., track_id: _Optional[str] = ..., track: _Optional[_Union[_models.TrackInfo, _Mapping]] = ..., analytics_key: _Optional[str] = ..., client_info: _Optional[_Union[_models.ClientInfo, _Mapping]] = ..., client_meta: _Optional[_Union[AnalyticsClientMeta, _Mapping]] = ..., egress_id: _Optional[str] = ..., ingress_id: _Optional[str] = ..., max_subscribed_video_quality: _Optional[_Union[_models.VideoQuality, str]] = ..., publisher: _Optional[_Union[_models.ParticipantInfo, _Mapping]] = ..., mime: _Optional[str] = ..., egress: _Optional[_Union[_egress.EgressInfo, _Mapping]] = ..., ingress: _Optional[_Union[_ingress.IngressInfo, _Mapping]] = ..., error: _Optional[str] = ..., rtp_stats: _Optional[_Union[_models.RTPStats, _Mapping]] = ..., video_layer: _Optional[int] = ..., node_id: _Optional[str] = ..., sip_call_id: _Optional[str] = ..., sip_call: _Optional[_Union[_sip.SIPCallInfo, _Mapping]] = ..., sip_trunk_id: _Optional[str] = ..., sip_inbound_trunk: _Optional[_Union[_sip.SIPInboundTrunkInfo, _Mapping]] = ..., sip_outbound_trunk: _Optional[_Union[_sip.SIPOutboundTrunkInfo, _Mapping]] = ..., sip_dispatch_rule_id: _Optional[str] = ..., sip_dispatch_rule: _Optional[_Union[_sip.SIPDispatchRuleInfo, _Mapping]] = ..., sip_transfer: _Optional[_Union[_sip.SIPTransferInfo, _Mapping]] = ..., report: _Optional[_Union[ReportInfo, _Mapping]] = ..., api_call: _Optional[_Union[APICallInfo, _Mapping]] = ..., webhook: _Optional[_Union[WebhookInfo, _Mapping]] = ...) -> None: ...

class AnalyticsEvents(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[AnalyticsEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[AnalyticsEvent, _Mapping]]] = ...) -> None: ...

class AnalyticsRoomParticipant(_message.Message):
    __slots__ = ("id", "identity", "name", "state", "joined_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    identity: str
    name: str
    state: _models.ParticipantInfo.State
    joined_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., identity: _Optional[str] = ..., name: _Optional[str] = ..., state: _Optional[_Union[_models.ParticipantInfo.State, str]] = ..., joined_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AnalyticsRoom(_message.Message):
    __slots__ = ("id", "name", "project_id", "created_at", "participants")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    project_id: str
    created_at: _timestamp_pb2.Timestamp
    participants: _containers.RepeatedCompositeFieldContainer[AnalyticsRoomParticipant]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., project_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., participants: _Optional[_Iterable[_Union[AnalyticsRoomParticipant, _Mapping]]] = ...) -> None: ...

class AnalyticsNodeRooms(_message.Message):
    __slots__ = ("node_id", "sequence_number", "timestamp", "rooms")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ROOMS_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    sequence_number: int
    timestamp: _timestamp_pb2.Timestamp
    rooms: _containers.RepeatedCompositeFieldContainer[AnalyticsRoom]
    def __init__(self, node_id: _Optional[str] = ..., sequence_number: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., rooms: _Optional[_Iterable[_Union[AnalyticsRoom, _Mapping]]] = ...) -> None: ...

class ReportInfo(_message.Message):
    __slots__ = ("feature_usage",)
    FEATURE_USAGE_FIELD_NUMBER: _ClassVar[int]
    feature_usage: FeatureUsageInfo
    def __init__(self, feature_usage: _Optional[_Union[FeatureUsageInfo, _Mapping]] = ...) -> None: ...

class TimeRange(_message.Message):
    __slots__ = ("started_at", "ended_at")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    ended_at: _timestamp_pb2.Timestamp
    def __init__(self, started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FeatureUsageInfo(_message.Message):
    __slots__ = ("feature", "project_id", "room_name", "room_id", "participant_identity", "participant_id", "track_id", "time_ranges")
    class Feature(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KRISP_NOISE_CANCELLATION: _ClassVar[FeatureUsageInfo.Feature]
        KRISP_BACKGROUND_VOICE_CANCELLATION: _ClassVar[FeatureUsageInfo.Feature]
    KRISP_NOISE_CANCELLATION: FeatureUsageInfo.Feature
    KRISP_BACKGROUND_VOICE_CANCELLATION: FeatureUsageInfo.Feature
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ID_FIELD_NUMBER: _ClassVar[int]
    TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_RANGES_FIELD_NUMBER: _ClassVar[int]
    feature: FeatureUsageInfo.Feature
    project_id: str
    room_name: str
    room_id: str
    participant_identity: str
    participant_id: str
    track_id: str
    time_ranges: _containers.RepeatedCompositeFieldContainer[TimeRange]
    def __init__(self, feature: _Optional[_Union[FeatureUsageInfo.Feature, str]] = ..., project_id: _Optional[str] = ..., room_name: _Optional[str] = ..., room_id: _Optional[str] = ..., participant_identity: _Optional[str] = ..., participant_id: _Optional[str] = ..., track_id: _Optional[str] = ..., time_ranges: _Optional[_Iterable[_Union[TimeRange, _Mapping]]] = ...) -> None: ...

class APICallRequest(_message.Message):
    __slots__ = ("create_room_request", "list_rooms_request", "delete_room_request", "list_participants_request", "room_participant_identity", "mute_room_track_request", "update_participant_request", "update_subscriptions_request", "send_data_request", "update_room_metadata_request")
    CREATE_ROOM_REQUEST_FIELD_NUMBER: _ClassVar[int]
    LIST_ROOMS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DELETE_ROOM_REQUEST_FIELD_NUMBER: _ClassVar[int]
    LIST_PARTICIPANTS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ROOM_PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    MUTE_ROOM_TRACK_REQUEST_FIELD_NUMBER: _ClassVar[int]
    UPDATE_PARTICIPANT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    UPDATE_SUBSCRIPTIONS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SEND_DATA_REQUEST_FIELD_NUMBER: _ClassVar[int]
    UPDATE_ROOM_METADATA_REQUEST_FIELD_NUMBER: _ClassVar[int]
    create_room_request: _room.CreateRoomRequest
    list_rooms_request: _room.ListRoomsRequest
    delete_room_request: _room.DeleteRoomRequest
    list_participants_request: _room.ListParticipantsRequest
    room_participant_identity: _room.RoomParticipantIdentity
    mute_room_track_request: _room.MuteRoomTrackRequest
    update_participant_request: _room.UpdateParticipantRequest
    update_subscriptions_request: _room.UpdateSubscriptionsRequest
    send_data_request: _room.SendDataRequest
    update_room_metadata_request: _room.UpdateRoomMetadataRequest
    def __init__(self, create_room_request: _Optional[_Union[_room.CreateRoomRequest, _Mapping]] = ..., list_rooms_request: _Optional[_Union[_room.ListRoomsRequest, _Mapping]] = ..., delete_room_request: _Optional[_Union[_room.DeleteRoomRequest, _Mapping]] = ..., list_participants_request: _Optional[_Union[_room.ListParticipantsRequest, _Mapping]] = ..., room_participant_identity: _Optional[_Union[_room.RoomParticipantIdentity, _Mapping]] = ..., mute_room_track_request: _Optional[_Union[_room.MuteRoomTrackRequest, _Mapping]] = ..., update_participant_request: _Optional[_Union[_room.UpdateParticipantRequest, _Mapping]] = ..., update_subscriptions_request: _Optional[_Union[_room.UpdateSubscriptionsRequest, _Mapping]] = ..., send_data_request: _Optional[_Union[_room.SendDataRequest, _Mapping]] = ..., update_room_metadata_request: _Optional[_Union[_room.UpdateRoomMetadataRequest, _Mapping]] = ...) -> None: ...

class APICallInfo(_message.Message):
    __slots__ = ("project_id", "request", "service", "method", "node_id", "status", "twirp_error_code", "twirp_error_message", "room_name", "room_id", "participant_identity", "participant_id", "track_id", "started_at", "duration_ns")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TWIRP_ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    TWIRP_ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ID_FIELD_NUMBER: _ClassVar[int]
    TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_NS_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    request: APICallRequest
    service: str
    method: str
    node_id: str
    status: int
    twirp_error_code: str
    twirp_error_message: str
    room_name: str
    room_id: str
    participant_identity: str
    participant_id: str
    track_id: str
    started_at: _timestamp_pb2.Timestamp
    duration_ns: int
    def __init__(self, project_id: _Optional[str] = ..., request: _Optional[_Union[APICallRequest, _Mapping]] = ..., service: _Optional[str] = ..., method: _Optional[str] = ..., node_id: _Optional[str] = ..., status: _Optional[int] = ..., twirp_error_code: _Optional[str] = ..., twirp_error_message: _Optional[str] = ..., room_name: _Optional[str] = ..., room_id: _Optional[str] = ..., participant_identity: _Optional[str] = ..., participant_id: _Optional[str] = ..., track_id: _Optional[str] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration_ns: _Optional[int] = ...) -> None: ...

class WebhookInfo(_message.Message):
    __slots__ = ("event_id", "event", "project_id", "room_name", "room_id", "participant_identity", "participant_id", "track_id", "egress_id", "ingress_id", "created_at", "queued_at", "queue_duration_ns", "sent_at", "send_duration_ns", "url", "num_dropped", "is_dropped", "service_status", "service_error_code", "service_error", "send_error")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ID_FIELD_NUMBER: _ClassVar[int]
    TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    EGRESS_ID_FIELD_NUMBER: _ClassVar[int]
    INGRESS_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    QUEUED_AT_FIELD_NUMBER: _ClassVar[int]
    QUEUE_DURATION_NS_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    SEND_DURATION_NS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    NUM_DROPPED_FIELD_NUMBER: _ClassVar[int]
    IS_DROPPED_FIELD_NUMBER: _ClassVar[int]
    SERVICE_STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ERROR_FIELD_NUMBER: _ClassVar[int]
    SEND_ERROR_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    event: str
    project_id: str
    room_name: str
    room_id: str
    participant_identity: str
    participant_id: str
    track_id: str
    egress_id: str
    ingress_id: str
    created_at: _timestamp_pb2.Timestamp
    queued_at: _timestamp_pb2.Timestamp
    queue_duration_ns: int
    sent_at: _timestamp_pb2.Timestamp
    send_duration_ns: int
    url: str
    num_dropped: int
    is_dropped: bool
    service_status: str
    service_error_code: int
    service_error: str
    send_error: str
    def __init__(self, event_id: _Optional[str] = ..., event: _Optional[str] = ..., project_id: _Optional[str] = ..., room_name: _Optional[str] = ..., room_id: _Optional[str] = ..., participant_identity: _Optional[str] = ..., participant_id: _Optional[str] = ..., track_id: _Optional[str] = ..., egress_id: _Optional[str] = ..., ingress_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., queued_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., queue_duration_ns: _Optional[int] = ..., sent_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., send_duration_ns: _Optional[int] = ..., url: _Optional[str] = ..., num_dropped: _Optional[int] = ..., is_dropped: bool = ..., service_status: _Optional[str] = ..., service_error_code: _Optional[int] = ..., service_error: _Optional[str] = ..., send_error: _Optional[str] = ...) -> None: ...
