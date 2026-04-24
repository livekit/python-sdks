from . import agent_session as _agent_session
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AudioEncoding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUDIO_ENCODING_PCM_S16LE: _ClassVar[AudioEncoding]
    AUDIO_ENCODING_OPUS: _ClassVar[AudioEncoding]
AUDIO_ENCODING_PCM_S16LE: AudioEncoding
AUDIO_ENCODING_OPUS: AudioEncoding

class SessionSettings(_message.Message):
    __slots__ = ("sample_rate", "encoding", "eot_settings", "interruption_settings")
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    EOT_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    INTERRUPTION_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    sample_rate: int
    encoding: AudioEncoding
    eot_settings: EotSettings
    interruption_settings: InterruptionSettings
    def __init__(self, sample_rate: _Optional[int] = ..., encoding: _Optional[_Union[AudioEncoding, str]] = ..., eot_settings: _Optional[_Union[EotSettings, _Mapping]] = ..., interruption_settings: _Optional[_Union[InterruptionSettings, _Mapping]] = ...) -> None: ...

class InferenceError(_message.Message):
    __slots__ = ("message", "code")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    message: str
    code: int
    def __init__(self, message: _Optional[str] = ..., code: _Optional[int] = ...) -> None: ...

class EotSettings(_message.Message):
    __slots__ = ("detection_interval",)
    DETECTION_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    detection_interval: _duration_pb2.Duration
    def __init__(self, detection_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class InterruptionSettings(_message.Message):
    __slots__ = ("threshold", "min_frames", "max_audio_duration", "audio_prefix_duration", "detection_interval")
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    MIN_FRAMES_FIELD_NUMBER: _ClassVar[int]
    MAX_AUDIO_DURATION_FIELD_NUMBER: _ClassVar[int]
    AUDIO_PREFIX_DURATION_FIELD_NUMBER: _ClassVar[int]
    DETECTION_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    threshold: float
    min_frames: int
    max_audio_duration: _duration_pb2.Duration
    audio_prefix_duration: _duration_pb2.Duration
    detection_interval: _duration_pb2.Duration
    def __init__(self, threshold: _Optional[float] = ..., min_frames: _Optional[int] = ..., max_audio_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., audio_prefix_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., detection_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class SessionCreate(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: SessionSettings
    def __init__(self, settings: _Optional[_Union[SessionSettings, _Mapping]] = ...) -> None: ...

class InputAudio(_message.Message):
    __slots__ = ("audio", "created_at", "num_samples")
    AUDIO_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    NUM_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    audio: bytes
    created_at: _timestamp_pb2.Timestamp
    num_samples: int
    def __init__(self, audio: _Optional[bytes] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., num_samples: _Optional[int] = ...) -> None: ...

class EotInputChatContext(_message.Message):
    __slots__ = ("messages",)
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[_agent_session.ChatMessage]
    def __init__(self, messages: _Optional[_Iterable[_Union[_agent_session.ChatMessage, _Mapping]]] = ...) -> None: ...

class SessionFlush(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SessionClose(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class InferenceStart(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class InferenceStop(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class BufferStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BufferStop(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClientMessage(_message.Message):
    __slots__ = ("created_at", "session_create", "input_audio", "session_flush", "session_close", "inference_start", "inference_stop", "buffer_start", "buffer_stop", "eot_input_chat_context")
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SESSION_CREATE_FIELD_NUMBER: _ClassVar[int]
    INPUT_AUDIO_FIELD_NUMBER: _ClassVar[int]
    SESSION_FLUSH_FIELD_NUMBER: _ClassVar[int]
    SESSION_CLOSE_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_START_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_STOP_FIELD_NUMBER: _ClassVar[int]
    BUFFER_START_FIELD_NUMBER: _ClassVar[int]
    BUFFER_STOP_FIELD_NUMBER: _ClassVar[int]
    EOT_INPUT_CHAT_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    created_at: _timestamp_pb2.Timestamp
    session_create: SessionCreate
    input_audio: InputAudio
    session_flush: SessionFlush
    session_close: SessionClose
    inference_start: InferenceStart
    inference_stop: InferenceStop
    buffer_start: BufferStart
    buffer_stop: BufferStop
    eot_input_chat_context: EotInputChatContext
    def __init__(self, created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., session_create: _Optional[_Union[SessionCreate, _Mapping]] = ..., input_audio: _Optional[_Union[InputAudio, _Mapping]] = ..., session_flush: _Optional[_Union[SessionFlush, _Mapping]] = ..., session_close: _Optional[_Union[SessionClose, _Mapping]] = ..., inference_start: _Optional[_Union[InferenceStart, _Mapping]] = ..., inference_stop: _Optional[_Union[InferenceStop, _Mapping]] = ..., buffer_start: _Optional[_Union[BufferStart, _Mapping]] = ..., buffer_stop: _Optional[_Union[BufferStop, _Mapping]] = ..., eot_input_chat_context: _Optional[_Union[EotInputChatContext, _Mapping]] = ...) -> None: ...

class EotInferenceRequest(_message.Message):
    __slots__ = ("audio", "assistant_text", "encoding", "sample_rate")
    AUDIO_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_TEXT_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    audio: bytes
    assistant_text: str
    encoding: AudioEncoding
    sample_rate: int
    def __init__(self, audio: _Optional[bytes] = ..., assistant_text: _Optional[str] = ..., encoding: _Optional[_Union[AudioEncoding, str]] = ..., sample_rate: _Optional[int] = ...) -> None: ...

class InterruptionInferenceRequest(_message.Message):
    __slots__ = ("audio", "encoding", "sample_rate")
    AUDIO_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    audio: bytes
    encoding: AudioEncoding
    sample_rate: int
    def __init__(self, audio: _Optional[bytes] = ..., encoding: _Optional[_Union[AudioEncoding, str]] = ..., sample_rate: _Optional[int] = ...) -> None: ...

class InferenceRequest(_message.Message):
    __slots__ = ("eot_inference_request", "interruption_inference_request")
    EOT_INFERENCE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    INTERRUPTION_INFERENCE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    eot_inference_request: EotInferenceRequest
    interruption_inference_request: InterruptionInferenceRequest
    def __init__(self, eot_inference_request: _Optional[_Union[EotInferenceRequest, _Mapping]] = ..., interruption_inference_request: _Optional[_Union[InterruptionInferenceRequest, _Mapping]] = ...) -> None: ...

class InferenceStats(_message.Message):
    __slots__ = ("earliest_client_created_at", "latest_client_created_at", "client_e2e_latency", "server_e2e_latency", "preprocessing_duration", "inference_duration")
    EARLIEST_CLIENT_CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    LATEST_CLIENT_CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_E2E_LATENCY_FIELD_NUMBER: _ClassVar[int]
    SERVER_E2E_LATENCY_FIELD_NUMBER: _ClassVar[int]
    PREPROCESSING_DURATION_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_DURATION_FIELD_NUMBER: _ClassVar[int]
    earliest_client_created_at: _timestamp_pb2.Timestamp
    latest_client_created_at: _timestamp_pb2.Timestamp
    client_e2e_latency: _duration_pb2.Duration
    server_e2e_latency: _duration_pb2.Duration
    preprocessing_duration: _duration_pb2.Duration
    inference_duration: _duration_pb2.Duration
    def __init__(self, earliest_client_created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., latest_client_created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., client_e2e_latency: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., server_e2e_latency: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., preprocessing_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., inference_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class EotInferenceResponse(_message.Message):
    __slots__ = ("probability", "stats")
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    probability: float
    stats: InferenceStats
    def __init__(self, probability: _Optional[float] = ..., stats: _Optional[_Union[InferenceStats, _Mapping]] = ...) -> None: ...

class InterruptionInferenceResponse(_message.Message):
    __slots__ = ("is_interruption", "probabilities", "stats")
    IS_INTERRUPTION_FIELD_NUMBER: _ClassVar[int]
    PROBABILITIES_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    is_interruption: bool
    probabilities: _containers.RepeatedScalarFieldContainer[float]
    stats: InferenceStats
    def __init__(self, is_interruption: bool = ..., probabilities: _Optional[_Iterable[float]] = ..., stats: _Optional[_Union[InferenceStats, _Mapping]] = ...) -> None: ...

class InferenceResponse(_message.Message):
    __slots__ = ("eot_inference_response", "interruption_inference_response")
    EOT_INFERENCE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    INTERRUPTION_INFERENCE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    eot_inference_response: EotInferenceResponse
    interruption_inference_response: InterruptionInferenceResponse
    def __init__(self, eot_inference_response: _Optional[_Union[EotInferenceResponse, _Mapping]] = ..., interruption_inference_response: _Optional[_Union[InterruptionInferenceResponse, _Mapping]] = ...) -> None: ...

class SessionCreated(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class InferenceStarted(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class InferenceStopped(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SessionClosed(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EotPrediction(_message.Message):
    __slots__ = ("probability", "inference_stats", "backend")
    class EotBackend(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EOT_BACKEND_UNKNOWN: _ClassVar[EotPrediction.EotBackend]
        EOT_BACKEND_MULTIMODAL: _ClassVar[EotPrediction.EotBackend]
        EOT_BACKEND_TEXT: _ClassVar[EotPrediction.EotBackend]
    EOT_BACKEND_UNKNOWN: EotPrediction.EotBackend
    EOT_BACKEND_MULTIMODAL: EotPrediction.EotBackend
    EOT_BACKEND_TEXT: EotPrediction.EotBackend
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_STATS_FIELD_NUMBER: _ClassVar[int]
    BACKEND_FIELD_NUMBER: _ClassVar[int]
    probability: float
    inference_stats: InferenceStats
    backend: EotPrediction.EotBackend
    def __init__(self, probability: _Optional[float] = ..., inference_stats: _Optional[_Union[InferenceStats, _Mapping]] = ..., backend: _Optional[_Union[EotPrediction.EotBackend, str]] = ...) -> None: ...

class InterruptionPrediction(_message.Message):
    __slots__ = ("is_interruption", "probabilities", "inference_stats")
    IS_INTERRUPTION_FIELD_NUMBER: _ClassVar[int]
    PROBABILITIES_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_STATS_FIELD_NUMBER: _ClassVar[int]
    is_interruption: bool
    probabilities: _containers.RepeatedScalarFieldContainer[float]
    inference_stats: InferenceStats
    def __init__(self, is_interruption: bool = ..., probabilities: _Optional[_Iterable[float]] = ..., inference_stats: _Optional[_Union[InferenceStats, _Mapping]] = ...) -> None: ...

class ServerMessage(_message.Message):
    __slots__ = ("server_created_at", "request_id", "client_created_at", "session_created", "inference_started", "inference_stopped", "session_closed", "error", "eot_prediction", "interruption_prediction")
    SERVER_CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SESSION_CREATED_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_STARTED_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_STOPPED_FIELD_NUMBER: _ClassVar[int]
    SESSION_CLOSED_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    EOT_PREDICTION_FIELD_NUMBER: _ClassVar[int]
    INTERRUPTION_PREDICTION_FIELD_NUMBER: _ClassVar[int]
    server_created_at: _timestamp_pb2.Timestamp
    request_id: str
    client_created_at: _timestamp_pb2.Timestamp
    session_created: SessionCreated
    inference_started: InferenceStarted
    inference_stopped: InferenceStopped
    session_closed: SessionClosed
    error: InferenceError
    eot_prediction: EotPrediction
    interruption_prediction: InterruptionPrediction
    def __init__(self, server_created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., request_id: _Optional[str] = ..., client_created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., session_created: _Optional[_Union[SessionCreated, _Mapping]] = ..., inference_started: _Optional[_Union[InferenceStarted, _Mapping]] = ..., inference_stopped: _Optional[_Union[InferenceStopped, _Mapping]] = ..., session_closed: _Optional[_Union[SessionClosed, _Mapping]] = ..., error: _Optional[_Union[InferenceError, _Mapping]] = ..., eot_prediction: _Optional[_Union[EotPrediction, _Mapping]] = ..., interruption_prediction: _Optional[_Union[InterruptionPrediction, _Mapping]] = ...) -> None: ...
