from ..logger_pb import options as _options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentDevMessage(_message.Message):
    __slots__ = ("get_running_jobs_request", "get_running_jobs_response", "server_info", "credentials")
    GET_RUNNING_JOBS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    GET_RUNNING_JOBS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SERVER_INFO_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    get_running_jobs_request: GetRunningAgentJobsRequest
    get_running_jobs_response: GetRunningAgentJobsResponse
    server_info: ServerInfo
    credentials: Credentials
    def __init__(self, get_running_jobs_request: _Optional[_Union[GetRunningAgentJobsRequest, _Mapping]] = ..., get_running_jobs_response: _Optional[_Union[GetRunningAgentJobsResponse, _Mapping]] = ..., server_info: _Optional[_Union[ServerInfo, _Mapping]] = ..., credentials: _Optional[_Union[Credentials, _Mapping]] = ...) -> None: ...

class ServerInfo(_message.Message):
    __slots__ = ("agent_name", "url", "supports_token_mode")
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_TOKEN_MODE_FIELD_NUMBER: _ClassVar[int]
    agent_name: str
    url: str
    supports_token_mode: bool
    def __init__(self, agent_name: _Optional[str] = ..., url: _Optional[str] = ..., supports_token_mode: bool = ...) -> None: ...

class Credentials(_message.Message):
    __slots__ = ("url", "token", "expires_at")
    URL_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    url: str
    token: str
    expires_at: int
    def __init__(self, url: _Optional[str] = ..., token: _Optional[str] = ..., expires_at: _Optional[int] = ...) -> None: ...

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
