from . import models as _models
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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
    JS_PENDING: _ClassVar[JobStatus]
    JS_RUNNING: _ClassVar[JobStatus]
    JS_SUCCESS: _ClassVar[JobStatus]
    JS_FAILED: _ClassVar[JobStatus]
JT_ROOM: JobType
JT_PUBLISHER: JobType
WS_AVAILABLE: WorkerStatus
WS_FULL: WorkerStatus
JS_PENDING: JobStatus
JS_RUNNING: JobStatus
JS_SUCCESS: JobStatus
JS_FAILED: JobStatus

class Job(_message.Message):
    __slots__ = ("id", "dispatch_id", "type", "room", "participant", "namespace", "metadata", "agent_name", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    dispatch_id: str
    type: JobType
    room: _models.Room
    participant: _models.ParticipantInfo
    namespace: str
    metadata: str
    agent_name: str
    state: JobState
    def __init__(self, id: _Optional[str] = ..., dispatch_id: _Optional[str] = ..., type: _Optional[_Union[JobType, str]] = ..., room: _Optional[_Union[_models.Room, _Mapping]] = ..., participant: _Optional[_Union[_models.ParticipantInfo, _Mapping]] = ..., namespace: _Optional[str] = ..., metadata: _Optional[str] = ..., agent_name: _Optional[str] = ..., state: _Optional[_Union[JobState, _Mapping]] = ...) -> None: ...

class JobState(_message.Message):
    __slots__ = ("status", "error", "started_at", "ended_at", "updated_at", "participant_identity")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    status: JobStatus
    error: str
    started_at: int
    ended_at: int
    updated_at: int
    participant_identity: str
    def __init__(self, status: _Optional[_Union[JobStatus, str]] = ..., error: _Optional[str] = ..., started_at: _Optional[int] = ..., ended_at: _Optional[int] = ..., updated_at: _Optional[int] = ..., participant_identity: _Optional[str] = ...) -> None: ...

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
    __slots__ = ("register", "availability", "assignment", "termination", "pong")
    REGISTER_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_FIELD_NUMBER: _ClassVar[int]
    PONG_FIELD_NUMBER: _ClassVar[int]
    register: RegisterWorkerResponse
    availability: AvailabilityRequest
    assignment: JobAssignment
    termination: JobTermination
    pong: WorkerPong
    def __init__(self, register: _Optional[_Union[RegisterWorkerResponse, _Mapping]] = ..., availability: _Optional[_Union[AvailabilityRequest, _Mapping]] = ..., assignment: _Optional[_Union[JobAssignment, _Mapping]] = ..., termination: _Optional[_Union[JobTermination, _Mapping]] = ..., pong: _Optional[_Union[WorkerPong, _Mapping]] = ...) -> None: ...

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
    __slots__ = ("type", "agent_name", "version", "ping_interval", "namespace", "allowed_permissions")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PING_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    type: JobType
    agent_name: str
    version: str
    ping_interval: int
    namespace: str
    allowed_permissions: _models.ParticipantPermission
    def __init__(self, type: _Optional[_Union[JobType, str]] = ..., agent_name: _Optional[str] = ..., version: _Optional[str] = ..., ping_interval: _Optional[int] = ..., namespace: _Optional[str] = ..., allowed_permissions: _Optional[_Union[_models.ParticipantPermission, _Mapping]] = ...) -> None: ...

class RegisterWorkerResponse(_message.Message):
    __slots__ = ("worker_id", "server_info")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_INFO_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    server_info: _models.ServerInfo
    def __init__(self, worker_id: _Optional[str] = ..., server_info: _Optional[_Union[_models.ServerInfo, _Mapping]] = ...) -> None: ...

class MigrateJobRequest(_message.Message):
    __slots__ = ("job_ids",)
    JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    job_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, job_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class AvailabilityRequest(_message.Message):
    __slots__ = ("job", "resuming")
    JOB_FIELD_NUMBER: _ClassVar[int]
    RESUMING_FIELD_NUMBER: _ClassVar[int]
    job: Job
    resuming: bool
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ..., resuming: bool = ...) -> None: ...

class AvailabilityResponse(_message.Message):
    __slots__ = ("job_id", "available", "supports_resume", "participant_name", "participant_identity", "participant_metadata", "participant_attributes")
    class ParticipantAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_RESUME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_METADATA_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    available: bool
    supports_resume: bool
    participant_name: str
    participant_identity: str
    participant_metadata: str
    participant_attributes: _containers.ScalarMap[str, str]
    def __init__(self, job_id: _Optional[str] = ..., available: bool = ..., supports_resume: bool = ..., participant_name: _Optional[str] = ..., participant_identity: _Optional[str] = ..., participant_metadata: _Optional[str] = ..., participant_attributes: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UpdateJobStatus(_message.Message):
    __slots__ = ("job_id", "status", "error")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    status: JobStatus
    error: str
    def __init__(self, job_id: _Optional[str] = ..., status: _Optional[_Union[JobStatus, str]] = ..., error: _Optional[str] = ...) -> None: ...

class UpdateWorkerStatus(_message.Message):
    __slots__ = ("status", "load", "job_count")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIELD_NUMBER: _ClassVar[int]
    JOB_COUNT_FIELD_NUMBER: _ClassVar[int]
    status: WorkerStatus
    load: float
    job_count: int
    def __init__(self, status: _Optional[_Union[WorkerStatus, str]] = ..., load: _Optional[float] = ..., job_count: _Optional[int] = ...) -> None: ...

class JobAssignment(_message.Message):
    __slots__ = ("job", "url", "token")
    JOB_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    job: Job
    url: str
    token: str
    def __init__(self, job: _Optional[_Union[Job, _Mapping]] = ..., url: _Optional[str] = ..., token: _Optional[str] = ...) -> None: ...

class JobTermination(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...
