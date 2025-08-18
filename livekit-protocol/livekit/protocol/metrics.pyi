from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MetricLabel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENTS_LLM_TTFT: _ClassVar[MetricLabel]
    AGENTS_STT_TTFT: _ClassVar[MetricLabel]
    AGENTS_TTS_TTFB: _ClassVar[MetricLabel]
    CLIENT_VIDEO_SUBSCRIBER_FREEZE_COUNT: _ClassVar[MetricLabel]
    CLIENT_VIDEO_SUBSCRIBER_TOTAL_FREEZE_DURATION: _ClassVar[MetricLabel]
    CLIENT_VIDEO_SUBSCRIBER_PAUSE_COUNT: _ClassVar[MetricLabel]
    CLIENT_VIDEO_SUBSCRIBER_TOTAL_PAUSES_DURATION: _ClassVar[MetricLabel]
    CLIENT_AUDIO_SUBSCRIBER_CONCEALED_SAMPLES: _ClassVar[MetricLabel]
    CLIENT_AUDIO_SUBSCRIBER_SILENT_CONCEALED_SAMPLES: _ClassVar[MetricLabel]
    CLIENT_AUDIO_SUBSCRIBER_CONCEALMENT_EVENTS: _ClassVar[MetricLabel]
    CLIENT_AUDIO_SUBSCRIBER_INTERRUPTION_COUNT: _ClassVar[MetricLabel]
    CLIENT_AUDIO_SUBSCRIBER_TOTAL_INTERRUPTION_DURATION: _ClassVar[MetricLabel]
    CLIENT_SUBSCRIBER_JITTER_BUFFER_DELAY: _ClassVar[MetricLabel]
    CLIENT_SUBSCRIBER_JITTER_BUFFER_EMITTED_COUNT: _ClassVar[MetricLabel]
    CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_BANDWIDTH: _ClassVar[MetricLabel]
    CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_CPU: _ClassVar[MetricLabel]
    CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_OTHER: _ClassVar[MetricLabel]
    PUBLISHER_RTT: _ClassVar[MetricLabel]
    SERVER_MESH_RTT: _ClassVar[MetricLabel]
    SUBSCRIBER_RTT: _ClassVar[MetricLabel]
    METRIC_LABEL_PREDEFINED_MAX_VALUE: _ClassVar[MetricLabel]
AGENTS_LLM_TTFT: MetricLabel
AGENTS_STT_TTFT: MetricLabel
AGENTS_TTS_TTFB: MetricLabel
CLIENT_VIDEO_SUBSCRIBER_FREEZE_COUNT: MetricLabel
CLIENT_VIDEO_SUBSCRIBER_TOTAL_FREEZE_DURATION: MetricLabel
CLIENT_VIDEO_SUBSCRIBER_PAUSE_COUNT: MetricLabel
CLIENT_VIDEO_SUBSCRIBER_TOTAL_PAUSES_DURATION: MetricLabel
CLIENT_AUDIO_SUBSCRIBER_CONCEALED_SAMPLES: MetricLabel
CLIENT_AUDIO_SUBSCRIBER_SILENT_CONCEALED_SAMPLES: MetricLabel
CLIENT_AUDIO_SUBSCRIBER_CONCEALMENT_EVENTS: MetricLabel
CLIENT_AUDIO_SUBSCRIBER_INTERRUPTION_COUNT: MetricLabel
CLIENT_AUDIO_SUBSCRIBER_TOTAL_INTERRUPTION_DURATION: MetricLabel
CLIENT_SUBSCRIBER_JITTER_BUFFER_DELAY: MetricLabel
CLIENT_SUBSCRIBER_JITTER_BUFFER_EMITTED_COUNT: MetricLabel
CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_BANDWIDTH: MetricLabel
CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_CPU: MetricLabel
CLIENT_VIDEO_PUBLISHER_QUALITY_LIMITATION_DURATION_OTHER: MetricLabel
PUBLISHER_RTT: MetricLabel
SERVER_MESH_RTT: MetricLabel
SUBSCRIBER_RTT: MetricLabel
METRIC_LABEL_PREDEFINED_MAX_VALUE: MetricLabel

class MetricsBatch(_message.Message):
    __slots__ = ("timestamp_ms", "normalized_timestamp", "str_data", "time_series", "events")
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    NORMALIZED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STR_DATA_FIELD_NUMBER: _ClassVar[int]
    TIME_SERIES_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    timestamp_ms: int
    normalized_timestamp: _timestamp_pb2.Timestamp
    str_data: _containers.RepeatedScalarFieldContainer[str]
    time_series: _containers.RepeatedCompositeFieldContainer[TimeSeriesMetric]
    events: _containers.RepeatedCompositeFieldContainer[EventMetric]
    def __init__(self, timestamp_ms: _Optional[int] = ..., normalized_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., str_data: _Optional[_Iterable[str]] = ..., time_series: _Optional[_Iterable[_Union[TimeSeriesMetric, _Mapping]]] = ..., events: _Optional[_Iterable[_Union[EventMetric, _Mapping]]] = ...) -> None: ...

class TimeSeriesMetric(_message.Message):
    __slots__ = ("label", "participant_identity", "track_sid", "samples", "rid")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    label: int
    participant_identity: int
    track_sid: int
    samples: _containers.RepeatedCompositeFieldContainer[MetricSample]
    rid: int
    def __init__(self, label: _Optional[int] = ..., participant_identity: _Optional[int] = ..., track_sid: _Optional[int] = ..., samples: _Optional[_Iterable[_Union[MetricSample, _Mapping]]] = ..., rid: _Optional[int] = ...) -> None: ...

class MetricSample(_message.Message):
    __slots__ = ("timestamp_ms", "normalized_timestamp", "value")
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    NORMALIZED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp_ms: int
    normalized_timestamp: _timestamp_pb2.Timestamp
    value: float
    def __init__(self, timestamp_ms: _Optional[int] = ..., normalized_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class EventMetric(_message.Message):
    __slots__ = ("label", "participant_identity", "track_sid", "start_timestamp_ms", "end_timestamp_ms", "normalized_start_timestamp", "normalized_end_timestamp", "metadata", "rid")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    TRACK_SID_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    NORMALIZED_START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    NORMALIZED_END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    label: int
    participant_identity: int
    track_sid: int
    start_timestamp_ms: int
    end_timestamp_ms: int
    normalized_start_timestamp: _timestamp_pb2.Timestamp
    normalized_end_timestamp: _timestamp_pb2.Timestamp
    metadata: str
    rid: int
    def __init__(self, label: _Optional[int] = ..., participant_identity: _Optional[int] = ..., track_sid: _Optional[int] = ..., start_timestamp_ms: _Optional[int] = ..., end_timestamp_ms: _Optional[int] = ..., normalized_start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., normalized_end_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., metadata: _Optional[str] = ..., rid: _Optional[int] = ...) -> None: ...
