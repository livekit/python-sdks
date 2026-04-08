from . import agent as _agent
from .logger_pb import options as _options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobRestartPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JRP_ON_FAILURE: _ClassVar[JobRestartPolicy]
    JRP_NEVER: _ClassVar[JobRestartPolicy]
JRP_ON_FAILURE: JobRestartPolicy
JRP_NEVER: JobRestartPolicy

class CreateAgentDispatchRequest(_message.Message):
    __slots__ = ("agent_name", "room", "metadata", "restart_policy")
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RESTART_POLICY_FIELD_NUMBER: _ClassVar[int]
    agent_name: str
    room: str
    metadata: str
    restart_policy: JobRestartPolicy
    def __init__(self, agent_name: _Optional[str] = ..., room: _Optional[str] = ..., metadata: _Optional[str] = ..., restart_policy: _Optional[_Union[JobRestartPolicy, str]] = ...) -> None: ...

class RoomAgentDispatch(_message.Message):
    __slots__ = ("agent_name", "metadata", "restart_policy")
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RESTART_POLICY_FIELD_NUMBER: _ClassVar[int]
    agent_name: str
    metadata: str
    restart_policy: JobRestartPolicy
    def __init__(self, agent_name: _Optional[str] = ..., metadata: _Optional[str] = ..., restart_policy: _Optional[_Union[JobRestartPolicy, str]] = ...) -> None: ...

class DeleteAgentDispatchRequest(_message.Message):
    __slots__ = ("dispatch_id", "room")
    DISPATCH_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    dispatch_id: str
    room: str
    def __init__(self, dispatch_id: _Optional[str] = ..., room: _Optional[str] = ...) -> None: ...

class ListAgentDispatchRequest(_message.Message):
    __slots__ = ("dispatch_id", "room")
    DISPATCH_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    dispatch_id: str
    room: str
    def __init__(self, dispatch_id: _Optional[str] = ..., room: _Optional[str] = ...) -> None: ...

class ListAgentDispatchResponse(_message.Message):
    __slots__ = ("agent_dispatches",)
    AGENT_DISPATCHES_FIELD_NUMBER: _ClassVar[int]
    agent_dispatches: _containers.RepeatedCompositeFieldContainer[AgentDispatch]
    def __init__(self, agent_dispatches: _Optional[_Iterable[_Union[AgentDispatch, _Mapping]]] = ...) -> None: ...

class AgentDispatch(_message.Message):
    __slots__ = ("id", "agent_name", "room", "metadata", "state", "restart_policy")
    ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    RESTART_POLICY_FIELD_NUMBER: _ClassVar[int]
    id: str
    agent_name: str
    room: str
    metadata: str
    state: AgentDispatchState
    restart_policy: JobRestartPolicy
    def __init__(self, id: _Optional[str] = ..., agent_name: _Optional[str] = ..., room: _Optional[str] = ..., metadata: _Optional[str] = ..., state: _Optional[_Union[AgentDispatchState, _Mapping]] = ..., restart_policy: _Optional[_Union[JobRestartPolicy, str]] = ...) -> None: ...

class AgentDispatchState(_message.Message):
    __slots__ = ("jobs", "created_at", "deleted_at")
    JOBS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[_agent.Job]
    created_at: int
    deleted_at: int
    def __init__(self, jobs: _Optional[_Iterable[_Union[_agent.Job, _Mapping]]] = ..., created_at: _Optional[int] = ..., deleted_at: _Optional[int] = ...) -> None: ...
