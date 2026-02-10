from . import agent_session as _livekit_agent_session_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TextMessageErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TME_INTERNAL: _ClassVar[TextMessageErrorCode]
    TME_SESSION_STATE_NOT_FOUND: _ClassVar[TextMessageErrorCode]
    TME_TEXT_HANDLER_ERROR: _ClassVar[TextMessageErrorCode]
    TME_PROCESS_CLOSED: _ClassVar[TextMessageErrorCode]
TME_INTERNAL: TextMessageErrorCode
TME_SESSION_STATE_NOT_FOUND: TextMessageErrorCode
TME_TEXT_HANDLER_ERROR: TextMessageErrorCode
TME_PROCESS_CLOSED: TextMessageErrorCode

class AgentSessionState(_message.Message):
    __slots__ = ("version", "snapshot", "delta")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    version: int
    snapshot: bytes
    delta: bytes
    def __init__(self, version: _Optional[int] = ..., snapshot: _Optional[bytes] = ..., delta: _Optional[bytes] = ...) -> None: ...

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

class TextSessionStarted(_message.Message):
    __slots__ = ("session_id", "message_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    message_id: str
    def __init__(self, session_id: _Optional[str] = ..., message_id: _Optional[str] = ...) -> None: ...

class TextResponseEvent(_message.Message):
    __slots__ = ("message_id", "item")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    item: _livekit_agent_session_pb2.ChatContext.ChatItem
    def __init__(self, message_id: _Optional[str] = ..., item: _Optional[_Union[_livekit_agent_session_pb2.ChatContext.ChatItem, _Mapping]] = ...) -> None: ...

class TextSessionComplete(_message.Message):
    __slots__ = ("message_id", "session_state", "error")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_STATE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    session_state: AgentSessionState
    error: TextMessageError
    def __init__(self, message_id: _Optional[str] = ..., session_state: _Optional[_Union[AgentSessionState, _Mapping]] = ..., error: _Optional[_Union[TextMessageError, _Mapping]] = ...) -> None: ...

class TextMessageError(_message.Message):
    __slots__ = ("message", "code")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    message: str
    code: TextMessageErrorCode
    def __init__(self, message: _Optional[str] = ..., code: _Optional[_Union[TextMessageErrorCode, str]] = ...) -> None: ...
