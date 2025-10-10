from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChatRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DEVELOPER: _ClassVar[ChatRole]
    SYSTEM: _ClassVar[ChatRole]
    USER: _ClassVar[ChatRole]
    ASSISTANT: _ClassVar[ChatRole]
DEVELOPER: ChatRole
SYSTEM: ChatRole
USER: ChatRole
ASSISTANT: ChatRole

class MetricsReport(_message.Message):
    __slots__ = ("started_speaking_at", "stopped_speaking_at", "transcription_delay", "end_of_turn_delay", "on_user_turn_completed_delay", "llm_node_ttft", "tts_node_ttfb", "e2e_latency")
    STARTED_SPEAKING_AT_FIELD_NUMBER: _ClassVar[int]
    STOPPED_SPEAKING_AT_FIELD_NUMBER: _ClassVar[int]
    TRANSCRIPTION_DELAY_FIELD_NUMBER: _ClassVar[int]
    END_OF_TURN_DELAY_FIELD_NUMBER: _ClassVar[int]
    ON_USER_TURN_COMPLETED_DELAY_FIELD_NUMBER: _ClassVar[int]
    LLM_NODE_TTFT_FIELD_NUMBER: _ClassVar[int]
    TTS_NODE_TTFB_FIELD_NUMBER: _ClassVar[int]
    E2E_LATENCY_FIELD_NUMBER: _ClassVar[int]
    started_speaking_at: _timestamp_pb2.Timestamp
    stopped_speaking_at: _timestamp_pb2.Timestamp
    transcription_delay: float
    end_of_turn_delay: float
    on_user_turn_completed_delay: float
    llm_node_ttft: float
    tts_node_ttfb: float
    e2e_latency: float
    def __init__(self, started_speaking_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., stopped_speaking_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., transcription_delay: _Optional[float] = ..., end_of_turn_delay: _Optional[float] = ..., on_user_turn_completed_delay: _Optional[float] = ..., llm_node_ttft: _Optional[float] = ..., tts_node_ttfb: _Optional[float] = ..., e2e_latency: _Optional[float] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("id", "role", "content", "interrupted", "transcript_confidence", "extra", "metrics", "created_at")
    class ChatContent(_message.Message):
        __slots__ = ("text",)
        TEXT_FIELD_NUMBER: _ClassVar[int]
        text: str
        def __init__(self, text: _Optional[str] = ...) -> None: ...
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    INTERRUPTED_FIELD_NUMBER: _ClassVar[int]
    TRANSCRIPT_CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    role: ChatRole
    content: _containers.RepeatedCompositeFieldContainer[ChatMessage.ChatContent]
    interrupted: bool
    transcript_confidence: float
    extra: _containers.ScalarMap[str, str]
    metrics: MetricsReport
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., role: _Optional[_Union[ChatRole, str]] = ..., content: _Optional[_Iterable[_Union[ChatMessage.ChatContent, _Mapping]]] = ..., interrupted: bool = ..., transcript_confidence: _Optional[float] = ..., extra: _Optional[_Mapping[str, str]] = ..., metrics: _Optional[_Union[MetricsReport, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FunctionCall(_message.Message):
    __slots__ = ("id", "call_id", "arguments", "name", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    CALL_ID_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    call_id: str
    arguments: str
    name: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., call_id: _Optional[str] = ..., arguments: _Optional[str] = ..., name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FunctionCallOutput(_message.Message):
    __slots__ = ("id", "name", "call_id", "output", "is_error", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CALL_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    IS_ERROR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    call_id: str
    output: str
    is_error: bool
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., call_id: _Optional[str] = ..., output: _Optional[str] = ..., is_error: bool = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AgentHandoff(_message.Message):
    __slots__ = ("id", "old_agent_id", "new_agent_id", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    OLD_AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    old_agent_id: str
    new_agent_id: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., old_agent_id: _Optional[str] = ..., new_agent_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ChatContext(_message.Message):
    __slots__ = ("items",)
    class ChatItem(_message.Message):
        __slots__ = ("message", "function_call", "function_call_output", "agent_handoff")
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        FUNCTION_CALL_FIELD_NUMBER: _ClassVar[int]
        FUNCTION_CALL_OUTPUT_FIELD_NUMBER: _ClassVar[int]
        AGENT_HANDOFF_FIELD_NUMBER: _ClassVar[int]
        message: ChatMessage
        function_call: FunctionCall
        function_call_output: FunctionCallOutput
        agent_handoff: AgentHandoff
        def __init__(self, message: _Optional[_Union[ChatMessage, _Mapping]] = ..., function_call: _Optional[_Union[FunctionCall, _Mapping]] = ..., function_call_output: _Optional[_Union[FunctionCallOutput, _Mapping]] = ..., agent_handoff: _Optional[_Union[AgentHandoff, _Mapping]] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ChatContext.ChatItem]
    def __init__(self, items: _Optional[_Iterable[_Union[ChatContext.ChatItem, _Mapping]]] = ...) -> None: ...
