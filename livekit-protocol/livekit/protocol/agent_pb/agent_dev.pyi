from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentDevMessage(_message.Message):
    __slots__ = ("get_running_jobs_request", "get_running_jobs_response")
    GET_RUNNING_JOBS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    GET_RUNNING_JOBS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    get_running_jobs_request: GetRunningAgentJobsRequest
    get_running_jobs_response: GetRunningAgentJobsResponse
    def __init__(self, get_running_jobs_request: _Optional[_Union[GetRunningAgentJobsRequest, _Mapping]] = ..., get_running_jobs_response: _Optional[_Union[GetRunningAgentJobsResponse, _Mapping]] = ...) -> None: ...

class GetRunningAgentJobsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetRunningAgentJobsResponse(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[RunningAgentJobInfo]
    def __init__(self, jobs: _Optional[_Iterable[_Union[RunningAgentJobInfo, _Mapping]]] = ...) -> None: ...

class RunningAgentJobInfo(_message.Message):
    __slots__ = ("job", "accept_name", "accept_identity", "accept_metadata", "url", "token", "worker_id", "mock_job")
    JOB_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_METADATA_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    MOCK_JOB_FIELD_NUMBER: _ClassVar[int]
    job: bytes
    accept_name: str
    accept_identity: str
    accept_metadata: str
    url: str
    token: str
    worker_id: str
    mock_job: bool
    def __init__(self, job: _Optional[bytes] = ..., accept_name: _Optional[str] = ..., accept_identity: _Optional[str] = ..., accept_metadata: _Optional[str] = ..., url: _Optional[str] = ..., token: _Optional[str] = ..., worker_id: _Optional[str] = ..., mock_job: bool = ...) -> None: ...
