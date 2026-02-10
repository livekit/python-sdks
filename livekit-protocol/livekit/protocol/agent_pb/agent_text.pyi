from . import agent_session as _livekit_agent_session_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TextMessageErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INTERNAL_ERROR: _ClassVar[TextMessageErrorCode]
    SESSION_STATE_NOT_FOUND: _ClassVar[TextMessageErrorCode]
    TEXT_HANDLER_ERROR: _ClassVar[TextMessageErrorCode]
    PROCESS_CLOSED: _ClassVar[TextMessageErrorCode]
INTERNAL_ERROR: TextMessageErrorCode
SESSION_STATE_NOT_FOUND: TextMessageErrorCode
TEXT_HANDLER_ERROR: TextMessageErrorCode
PROCESS_CLOSED: TextMessageErrorCode

class TextMessageRequest(_message.Message):
    __slots__ = ("text", "message_id", "session_id", "agent_name", "metadata", "session_state")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SESSION_STATE_FIELD_NUMBER: _ClassVar[int]
    text: str
    message_id: str
    session_id: str
    agent_name: str
    metadata: str
    session_state: AgentSessionState
    def __init__(self, text: _Optional[str] = ..., message_id: _Optional[str] = ..., session_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., metadata: _Optional[str] = ..., session_state: _Optional[_Union[AgentSessionState, _Mapping]] = ...) -> None: ...

class TextMessageResponse(_message.Message):
    __slots__ = ("message_id", "session_id", "message", "function_call", "function_call_output", "agent_handoff", "complete")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_CALL_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_CALL_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    AGENT_HANDOFF_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    session_id: str
    message: _livekit_agent_session_pb2.ChatMessage
    function_call: _livekit_agent_session_pb2.FunctionCall
    function_call_output: _livekit_agent_session_pb2.FunctionCallOutput
    agent_handoff: _livekit_agent_session_pb2.AgentHandoff
    complete: TextMessageComplete
    def __init__(self, message_id: _Optional[str] = ..., session_id: _Optional[str] = ..., message: _Optional[_Union[_livekit_agent_session_pb2.ChatMessage, _Mapping]] = ..., function_call: _Optional[_Union[_livekit_agent_session_pb2.FunctionCall, _Mapping]] = ..., function_call_output: _Optional[_Union[_livekit_agent_session_pb2.FunctionCallOutput, _Mapping]] = ..., agent_handoff: _Optional[_Union[_livekit_agent_session_pb2.AgentHandoff, _Mapping]] = ..., complete: _Optional[_Union[TextMessageComplete, _Mapping]] = ...) -> None: ...

class TextMessageComplete(_message.Message):
    __slots__ = ("session_state", "error")
    SESSION_STATE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    session_state: AgentSessionState
    error: TextMessageError
    def __init__(self, session_state: _Optional[_Union[AgentSessionState, _Mapping]] = ..., error: _Optional[_Union[TextMessageError, _Mapping]] = ...) -> None: ...

class AgentSessionState(_message.Message):
    __slots__ = ("version", "snapshot", "delta")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    version: int
    snapshot: bytes
    delta: bytes
    def __init__(self, version: _Optional[int] = ..., snapshot: _Optional[bytes] = ..., delta: _Optional[bytes] = ...) -> None: ...

class TextMessageError(_message.Message):
    __slots__ = ("message", "code")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    message: str
    code: TextMessageErrorCode
    def __init__(self, message: _Optional[str] = ..., code: _Optional[_Union[TextMessageErrorCode, str]] = ...) -> None: ...
