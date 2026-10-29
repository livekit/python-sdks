from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class WorkerInfo(_message.Message):
    __slots__ = ("worker_type", "agent_name", "active_jobs", "sdk_version", "worker_load", "protocol_version")
    WORKER_TYPE_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_JOBS_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSION_FIELD_NUMBER: _ClassVar[int]
    WORKER_LOAD_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    worker_type: str
    agent_name: str
    active_jobs: float
    sdk_version: str
    worker_load: float
    protocol_version: int
    def __init__(self, worker_type: _Optional[str] = ..., agent_name: _Optional[str] = ..., active_jobs: _Optional[float] = ..., sdk_version: _Optional[str] = ..., worker_load: _Optional[float] = ..., protocol_version: _Optional[int] = ...) -> None: ...
