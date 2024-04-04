from . import models as _models
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JT_ROOM: _ClassVar[JobType]
    JT_PUBLISHER: _ClassVar[JobType]

class WorkerStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WS_AVAILABLE: _ClassVar[WorkerStatus]
    WS_FULL: _ClassVar[WorkerStatus]

class JobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JS_UNKNOWN: _ClassVar[JobStatus]
    JS_SUCCESS: _ClassVar[JobStatus]
    JS_FAILED: _ClassVar[JobStatus]
JT_ROOM: JobType
JT_PUBLISHER: JobType
WS_AVAILABLE: WorkerStatus
WS_FULL: WorkerStatus
JS_UNKNOWN: JobStatus
JS_SUCCESS: JobStatus
JS_FAILED: JobStatus

class WorkerInfo(_message.Message):
    __slots__ = ("id", "namespace", "version", "name", "type", "allowed_permissions")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    namespace: str
    version: str
    name: str
    type: JobType
    allowed_permissions: _models.ParticipantPermission
    def __init__(self, id: _Optional[str] = ..., namespace: _Optional[str] = ..., version: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[JobType, str]] = ..., allowed_permissions: _Optional[_Union[_models.ParticipantPermission, _Mapping]] = ...) -> None: ...

class AgentInfo(_message.Message):
    __slots__ = ("id", "name", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    version: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class Job(_message.Message):
    __slots__ = ("id", "type", "room", "participant", "namespace")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: JobType
    room: _models.Room
    participant: _models.ParticipantInfo
    namespace: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[JobType, str]] = ..., room: _Optional[_Union[_models.Room, _Mapping]] = ..., participant: _Optional[_Union[_models.ParticipantInfo, _Mapping]] = ..., namespace: _Optional[str] = ...) -> None: ...

class WorkerMessage(_message.Message):
    __slots__ = ("register", "availability", "update_worker", "update_job", "ping", "simulate_job", "migrate_job")
    REGISTER_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    UPDATE_WORKER_FIELD_NUMBER: _ClassVar[int]
    UPDATE_JOB_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    SIMULATE_JOB_FIELD_NUMBER: _ClassVar[int]
    MIGRATE_JOB_FIELD_NUMBER: _ClassVar[int]
    register: RegisterWorkerRequest
    availability: AvailabilityResponse
    update_worker: UpdateWorkerStatus
    update_job: UpdateJobStatus
    ping: WorkerPing
    simulate_job: SimulateJobRequest
    migrate_job: MigrateJobRequest
    def __init__(self, register: _Optional[_Union[RegisterWorkerRequest, _Mapping]] = ..., availability: _Optional[_Union[AvailabilityResponse, _Mapping]] = ..., update_worker: _Optional[_Union[UpdateWorkerStatus, _Mapping]] = ..., update_job: _Optional[_Union[UpdateJobStatus, _Mapping]] = ..., ping: _Optional[_Union[WorkerPing, _Mapping]] = ..., simulate_job: _Optional[_Union[SimulateJobRequest, _Mapping]] = ..., migrate_job: _Optional[_Union[MigrateJobRequest, _Mapping]] = ...) -> None: ...

class ServerMessage(_message.Message):
    __slots__ = ("register", "availability", "assignment", "pong")
    REGISTER_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
    PONG_FIELD_NUMBER: _ClassVar[int]
    register: RegisterWorkerResponse
    availability: AvailabilityRequest
    assignment: JobAssignment
    pong: WorkerPong
    def __init__(self, register: _Optional[_Union[RegisterWorkerResponse, _Mapping]] = ..., availability: _Optional[_Union[AvailabilityRequest, _Mapping]] = ..., assignment: _Optional[_Union[JobAssignment, _Mapping]] = ..., pong: _Optional[_Union[WorkerPong, _Mapping]] = ...) -> None: ...

class SimulateJobRequest(_message.Message):
    __slots__ = ("type", "room", "participant")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    type: JobType
    room: _models.Room
    participant: _models.ParticipantInfo
    def __init__(self, type: _Optional[_Union[JobType, str]] = ..., room: _Optional[_Union[_models.Room, _Mapping]] = ..., participant: _Optional[_Union[_models.ParticipantInfo, _Mapping]] = ...) -> None: ...

class WorkerPing(_message.Message):
    __slots__ = ("timestamp",)
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    def __init__(self, timestamp: _Optional[int] = ...) -> None: ...

class WorkerPong(_message.Message):
    __slots__ = ("last_timestamp", "timestamp")
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    last_timestamp: int
    timestamp: int
    def __init__(self, last_timestamp: _Optional[int] = ..., timestamp: _Optional[int] = ...) -> None: ...

class RegisterWorkerRequest(_message.Message):
    __slots__ = ("type", "version", "name", "ping_interval", "namespace", "allowed_permissions")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PING_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    type: JobType
    version: str
    name: str
    ping_interval: int
    namespace: str
    allowed_permissions: _models.ParticipantPermission
    def __init__(self, type: _Optional[_Union[JobType, str]] = ..., version: _Optional[str] = ..., name: _Optional[str] = ..., ping_interval: _Optional[int] = ..., namespace: _Optional[str] = ..., allowed_permissions: _Optional[_Union[_models.ParticipantPermission, _Mapping]] = ...) -> None: ...

class RegisterWorkerResponse(_message.Message):
    __slots__ = ("worker_id", "server_info")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_INFO_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    server_info: _models.ServerInfo
    def __init__(self, worker_id: _Optional[str] = ..., server_info: _Optional[_Union[_models.ServerInfo, _Mapping]] = ...) -> None: ...

class MigrateJobRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class AvailabilityRequest(_message.Message):
    __slots__ = ("job", "resuming")
    JOB_FIELD_NUMBER: _ClassVar[int]
    RESUMING_FIELD_NUMBER: _ClassVar[int]
    job: Job
    resuming: bool
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ..., resuming: bool = ...) -> None: ...

class AvailabilityResponse(_message.Message):
    __slots__ = ("job_id", "available", "supports_resume", "participant_name", "participant_identity", "participant_metadata")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_RESUME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_METADATA_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    available: bool
    supports_resume: bool
    participant_name: str
    participant_identity: str
    participant_metadata: str
    def __init__(self, job_id: _Optional[str] = ..., available: bool = ..., supports_resume: bool = ..., participant_name: _Optional[str] = ..., participant_identity: _Optional[str] = ..., participant_metadata: _Optional[str] = ...) -> None: ...

class UpdateJobStatus(_message.Message):
    __slots__ = ("job_id", "status", "error", "metadata", "load")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    status: JobStatus
    error: str
    metadata: str
    load: float
    def __init__(self, job_id: _Optional[str] = ..., status: _Optional[_Union[JobStatus, str]] = ..., error: _Optional[str] = ..., metadata: _Optional[str] = ..., load: _Optional[float] = ...) -> None: ...

class UpdateWorkerStatus(_message.Message):
    __slots__ = ("status", "metadata", "load")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIELD_NUMBER: _ClassVar[int]
    status: WorkerStatus
    metadata: str
    load: float
    def __init__(self, status: _Optional[_Union[WorkerStatus, str]] = ..., metadata: _Optional[str] = ..., load: _Optional[float] = ...) -> None: ...

class JobAssignment(_message.Message):
    __slots__ = ("job", "url", "token")
    JOB_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    job: Job
    url: str
    token: str
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ..., url: _Optional[str] = ..., token: _Optional[str] = ...) -> None: ...
