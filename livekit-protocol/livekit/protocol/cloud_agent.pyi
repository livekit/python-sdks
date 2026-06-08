from google.protobuf import timestamp_pb2 as _timestamp_pb2
from .logger_pb import options as _options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentSecretKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_SECRET_KIND_UNKNOWN: _ClassVar[AgentSecretKind]
    AGENT_SECRET_KIND_ENVIRONMENT: _ClassVar[AgentSecretKind]
    AGENT_SECRET_KIND_FILE: _ClassVar[AgentSecretKind]

class AgentEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_EVENT_TYPE_UNKNOWN: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_APPLICATION_CRASHED: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_RESTARTED_HIGH_DISK_USAGE: _ClassVar[AgentEventType]
    AGENT_EVENT_TYPE_RESTARTED_HIGH_MEMORY_USAGE: _ClassVar[AgentEventType]
AGENT_SECRET_KIND_UNKNOWN: AgentSecretKind
AGENT_SECRET_KIND_ENVIRONMENT: AgentSecretKind
AGENT_SECRET_KIND_FILE: AgentSecretKind
AGENT_EVENT_TYPE_UNKNOWN: AgentEventType
AGENT_EVENT_TYPE_APPLICATION_CRASHED: AgentEventType
AGENT_EVENT_TYPE_RESTARTED_HIGH_DISK_USAGE: AgentEventType
AGENT_EVENT_TYPE_RESTARTED_HIGH_MEMORY_USAGE: AgentEventType

class AgentEvent(_message.Message):
    __slots__ = ("type", "count", "timestamp")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    type: AgentEventType
    count: int
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, type: _Optional[_Union[AgentEventType, str]] = ..., count: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AgentSecret(_message.Message):
    __slots__ = ("name", "value", "created_at", "updated_at", "kind", "deployments")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: bytes
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    kind: AgentSecretKind
    deployments: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., value: _Optional[bytes] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., kind: _Optional[_Union[AgentSecretKind, str]] = ..., deployments: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateAgentRequest(_message.Message):
    __slots__ = ("agent_name", "secrets", "replicas", "max_replicas", "cpu_req", "regions")
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    REPLICAS_FIELD_NUMBER: _ClassVar[int]
    MAX_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    CPU_REQ_FIELD_NUMBER: _ClassVar[int]
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    agent_name: str
    secrets: _containers.RepeatedCompositeFieldContainer[AgentSecret]
    replicas: int
    max_replicas: int
    cpu_req: str
    regions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, agent_name: _Optional[str] = ..., secrets: _Optional[_Iterable[_Union[AgentSecret, _Mapping]]] = ..., replicas: _Optional[int] = ..., max_replicas: _Optional[int] = ..., cpu_req: _Optional[str] = ..., regions: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateAgentResponse(_message.Message):
    __slots__ = ("agent_id", "agent_name", "status", "version", "presigned_url", "tag", "server_regions", "presigned_post_request")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PRESIGNED_URL_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    SERVER_REGIONS_FIELD_NUMBER: _ClassVar[int]
    PRESIGNED_POST_REQUEST_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    status: str
    version: str
    presigned_url: str
    tag: str
    server_regions: _containers.RepeatedScalarFieldContainer[str]
    presigned_post_request: PresignedPostRequest
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., status: _Optional[str] = ..., version: _Optional[str] = ..., presigned_url: _Optional[str] = ..., tag: _Optional[str] = ..., server_regions: _Optional[_Iterable[str]] = ..., presigned_post_request: _Optional[_Union[PresignedPostRequest, _Mapping]] = ...) -> None: ...

class CreateAgentV2Request(_message.Message):
    __slots__ = ("secrets", "regions")
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    secrets: _containers.RepeatedCompositeFieldContainer[AgentSecret]
    regions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, secrets: _Optional[_Iterable[_Union[AgentSecret, _Mapping]]] = ..., regions: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateAgentV2Response(_message.Message):
    __slots__ = ("agent_id", "status", "server_regions")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVER_REGIONS_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    status: str
    server_regions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, agent_id: _Optional[str] = ..., status: _Optional[str] = ..., server_regions: _Optional[_Iterable[str]] = ...) -> None: ...

class PresignedPostRequest(_message.Message):
    __slots__ = ("url", "values")
    class ValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URL_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    url: str
    values: _containers.ScalarMap[str, str]
    def __init__(self, url: _Optional[str] = ..., values: _Optional[_Mapping[str, str]] = ...) -> None: ...

class AgentDeployment(_message.Message):
    __slots__ = ("region", "agent_id", "status", "replicas", "min_replicas", "max_replicas", "cpu_req", "cur_cpu", "cur_mem", "mem_req", "mem_limit", "cpu_limit", "server_region", "events", "deployment", "version", "agent_name", "deployment_enabled")
    REGION_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REPLICAS_FIELD_NUMBER: _ClassVar[int]
    MIN_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    MAX_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    CPU_REQ_FIELD_NUMBER: _ClassVar[int]
    CUR_CPU_FIELD_NUMBER: _ClassVar[int]
    CUR_MEM_FIELD_NUMBER: _ClassVar[int]
    MEM_REQ_FIELD_NUMBER: _ClassVar[int]
    MEM_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CPU_LIMIT_FIELD_NUMBER: _ClassVar[int]
    SERVER_REGION_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_ENABLED_FIELD_NUMBER: _ClassVar[int]
    region: str
    agent_id: str
    status: str
    replicas: int
    min_replicas: int
    max_replicas: int
    cpu_req: str
    cur_cpu: str
    cur_mem: str
    mem_req: str
    mem_limit: str
    cpu_limit: str
    server_region: str
    events: _containers.RepeatedCompositeFieldContainer[AgentEvent]
    deployment: str
    version: str
    agent_name: str
    deployment_enabled: bool
    def __init__(self, region: _Optional[str] = ..., agent_id: _Optional[str] = ..., status: _Optional[str] = ..., replicas: _Optional[int] = ..., min_replicas: _Optional[int] = ..., max_replicas: _Optional[int] = ..., cpu_req: _Optional[str] = ..., cur_cpu: _Optional[str] = ..., cur_mem: _Optional[str] = ..., mem_req: _Optional[str] = ..., mem_limit: _Optional[str] = ..., cpu_limit: _Optional[str] = ..., server_region: _Optional[str] = ..., events: _Optional[_Iterable[_Union[AgentEvent, _Mapping]]] = ..., deployment: _Optional[str] = ..., version: _Optional[str] = ..., agent_name: _Optional[str] = ..., deployment_enabled: bool = ...) -> None: ...

class AgentInfo(_message.Message):
    __slots__ = ("agent_id", "agent_name", "version", "agent_deployments", "secrets", "deployed_at")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    AGENT_DEPLOYMENTS_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    DEPLOYED_AT_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    version: str
    agent_deployments: _containers.RepeatedCompositeFieldContainer[AgentDeployment]
    secrets: _containers.RepeatedCompositeFieldContainer[AgentSecret]
    deployed_at: _timestamp_pb2.Timestamp
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., version: _Optional[str] = ..., agent_deployments: _Optional[_Iterable[_Union[AgentDeployment, _Mapping]]] = ..., secrets: _Optional[_Iterable[_Union[AgentSecret, _Mapping]]] = ..., deployed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListAgentsRequest(_message.Message):
    __slots__ = ("agent_name", "agent_id")
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    agent_name: str
    agent_id: str
    def __init__(self, agent_name: _Optional[str] = ..., agent_id: _Optional[str] = ...) -> None: ...

class ListAgentsResponse(_message.Message):
    __slots__ = ("agents",)
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    agents: _containers.RepeatedCompositeFieldContainer[AgentInfo]
    def __init__(self, agents: _Optional[_Iterable[_Union[AgentInfo, _Mapping]]] = ...) -> None: ...

class AgentVersion(_message.Message):
    __slots__ = ("version", "current", "created_at", "deployed_at", "attributes", "status", "owner", "draining", "active")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DEPLOYED_AT_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    DRAINING_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    version: str
    current: bool
    created_at: _timestamp_pb2.Timestamp
    deployed_at: _timestamp_pb2.Timestamp
    attributes: _containers.ScalarMap[str, str]
    status: str
    owner: str
    draining: bool
    active: bool
    def __init__(self, version: _Optional[str] = ..., current: bool = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., deployed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., attributes: _Optional[_Mapping[str, str]] = ..., status: _Optional[str] = ..., owner: _Optional[str] = ..., draining: bool = ..., active: bool = ...) -> None: ...

class ListAgentVersionsRequest(_message.Message):
    __slots__ = ("agent_id", "agent_name")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ...) -> None: ...

class ListAgentVersionsResponse(_message.Message):
    __slots__ = ("versions",)
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    versions: _containers.RepeatedCompositeFieldContainer[AgentVersion]
    def __init__(self, versions: _Optional[_Iterable[_Union[AgentVersion, _Mapping]]] = ...) -> None: ...

class UpdateAgentRequest(_message.Message):
    __slots__ = ("agent_id", "agent_name", "replicas", "max_replicas", "cpu_req", "regions", "secrets")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    REPLICAS_FIELD_NUMBER: _ClassVar[int]
    MAX_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    CPU_REQ_FIELD_NUMBER: _ClassVar[int]
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    replicas: int
    max_replicas: int
    cpu_req: str
    regions: _containers.RepeatedScalarFieldContainer[str]
    secrets: _containers.RepeatedCompositeFieldContainer[AgentSecret]
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., replicas: _Optional[int] = ..., max_replicas: _Optional[int] = ..., cpu_req: _Optional[str] = ..., regions: _Optional[_Iterable[str]] = ..., secrets: _Optional[_Iterable[_Union[AgentSecret, _Mapping]]] = ...) -> None: ...

class UpdateAgentResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class RestartAgentRequest(_message.Message):
    __slots__ = ("agent_id",)
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    def __init__(self, agent_id: _Optional[str] = ...) -> None: ...

class RestartAgentResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class DeployAgentRequest(_message.Message):
    __slots__ = ("agent_id", "agent_name", "secrets", "replicas", "max_replicas", "cpu_req", "deployment")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    REPLICAS_FIELD_NUMBER: _ClassVar[int]
    MAX_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    CPU_REQ_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    secrets: _containers.RepeatedCompositeFieldContainer[AgentSecret]
    replicas: int
    max_replicas: int
    cpu_req: str
    deployment: str
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., secrets: _Optional[_Iterable[_Union[AgentSecret, _Mapping]]] = ..., replicas: _Optional[int] = ..., max_replicas: _Optional[int] = ..., cpu_req: _Optional[str] = ..., deployment: _Optional[str] = ...) -> None: ...

class DeployAgentResponse(_message.Message):
    __slots__ = ("success", "message", "agent_id", "presigned_url", "tag", "presigned_post_request", "deployment")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRESIGNED_URL_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    PRESIGNED_POST_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    agent_id: str
    presigned_url: str
    tag: str
    presigned_post_request: PresignedPostRequest
    deployment: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., agent_id: _Optional[str] = ..., presigned_url: _Optional[str] = ..., tag: _Optional[str] = ..., presigned_post_request: _Optional[_Union[PresignedPostRequest, _Mapping]] = ..., deployment: _Optional[str] = ...) -> None: ...

class DeployAgentV2Request(_message.Message):
    __slots__ = ("agent_id", "secrets", "deployment")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    secrets: _containers.RepeatedCompositeFieldContainer[AgentSecret]
    deployment: str
    def __init__(self, agent_id: _Optional[str] = ..., secrets: _Optional[_Iterable[_Union[AgentSecret, _Mapping]]] = ..., deployment: _Optional[str] = ...) -> None: ...

class DeployAgentV2Response(_message.Message):
    __slots__ = ("success", "message", "agent_id", "tag", "presigned_req", "deployment")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    PRESIGNED_REQ_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    agent_id: str
    tag: str
    presigned_req: PresignedPostRequest
    deployment: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., agent_id: _Optional[str] = ..., tag: _Optional[str] = ..., presigned_req: _Optional[_Union[PresignedPostRequest, _Mapping]] = ..., deployment: _Optional[str] = ...) -> None: ...

class UpdateAgentSecretsRequest(_message.Message):
    __slots__ = ("agent_id", "agent_name", "overwrite", "secrets", "remove")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    REMOVE_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    overwrite: bool
    secrets: _containers.RepeatedCompositeFieldContainer[AgentSecret]
    remove: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., overwrite: bool = ..., secrets: _Optional[_Iterable[_Union[AgentSecret, _Mapping]]] = ..., remove: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateAgentSecretsResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class RollbackAgentRequest(_message.Message):
    __slots__ = ("agent_id", "agent_name", "version")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    version: str
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class RollbackAgentResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class DeleteAgentRequest(_message.Message):
    __slots__ = ("agent_id", "agent_name", "deployment")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    deployment: str
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., deployment: _Optional[str] = ...) -> None: ...

class DeleteAgentResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class ListAgentSecretsRequest(_message.Message):
    __slots__ = ("agent_id", "agent_name")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    agent_name: str
    def __init__(self, agent_id: _Optional[str] = ..., agent_name: _Optional[str] = ...) -> None: ...

class ListAgentSecretsResponse(_message.Message):
    __slots__ = ("secrets",)
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    secrets: _containers.RepeatedCompositeFieldContainer[AgentSecret]
    def __init__(self, secrets: _Optional[_Iterable[_Union[AgentSecret, _Mapping]]] = ...) -> None: ...

class SettingsParam(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ClientSettingsResponse(_message.Message):
    __slots__ = ("params",)
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: _containers.RepeatedCompositeFieldContainer[SettingsParam]
    def __init__(self, params: _Optional[_Iterable[_Union[SettingsParam, _Mapping]]] = ...) -> None: ...

class ClientSettingsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrivateLink(_message.Message):
    __slots__ = ("private_link_id", "name", "region", "port", "endpoint", "connection_endpoint", "cloud_region", "aws")
    class AWSConfig(_message.Message):
        __slots__ = ("endpoint",)
        ENDPOINT_FIELD_NUMBER: _ClassVar[int]
        endpoint: str
        def __init__(self, endpoint: _Optional[str] = ...) -> None: ...
    PRIVATE_LINK_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    CLOUD_REGION_FIELD_NUMBER: _ClassVar[int]
    AWS_FIELD_NUMBER: _ClassVar[int]
    private_link_id: str
    name: str
    region: str
    port: int
    endpoint: str
    connection_endpoint: str
    cloud_region: str
    aws: PrivateLink.AWSConfig
    def __init__(self, private_link_id: _Optional[str] = ..., name: _Optional[str] = ..., region: _Optional[str] = ..., port: _Optional[int] = ..., endpoint: _Optional[str] = ..., connection_endpoint: _Optional[str] = ..., cloud_region: _Optional[str] = ..., aws: _Optional[_Union[PrivateLink.AWSConfig, _Mapping]] = ...) -> None: ...

class PrivateLinkStatus(_message.Message):
    __slots__ = ("status", "updated_at", "reason")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PRIVATE_LINK_STATUS_UNKNOWN: _ClassVar[PrivateLinkStatus.Status]
        PRIVATE_LINK_STATUS_PROVISIONING: _ClassVar[PrivateLinkStatus.Status]
        PRIVATE_LINK_STATUS_PENDING_APPROVAL: _ClassVar[PrivateLinkStatus.Status]
        PRIVATE_LINK_STATUS_HEALTHY: _ClassVar[PrivateLinkStatus.Status]
        PRIVATE_LINK_STATUS_UNHEALTHY: _ClassVar[PrivateLinkStatus.Status]
        PRIVATE_LINK_STATUS_APPROVED: _ClassVar[PrivateLinkStatus.Status]
    PRIVATE_LINK_STATUS_UNKNOWN: PrivateLinkStatus.Status
    PRIVATE_LINK_STATUS_PROVISIONING: PrivateLinkStatus.Status
    PRIVATE_LINK_STATUS_PENDING_APPROVAL: PrivateLinkStatus.Status
    PRIVATE_LINK_STATUS_HEALTHY: PrivateLinkStatus.Status
    PRIVATE_LINK_STATUS_UNHEALTHY: PrivateLinkStatus.Status
    PRIVATE_LINK_STATUS_APPROVED: PrivateLinkStatus.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    status: PrivateLinkStatus.Status
    updated_at: _timestamp_pb2.Timestamp
    reason: str
    def __init__(self, status: _Optional[_Union[PrivateLinkStatus.Status, str]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., reason: _Optional[str] = ...) -> None: ...

class CreatePrivateLinkRequest(_message.Message):
    __slots__ = ("name", "region", "port", "endpoint", "cloud_region", "aws")
    class AWSCreateConfig(_message.Message):
        __slots__ = ("endpoint",)
        ENDPOINT_FIELD_NUMBER: _ClassVar[int]
        endpoint: str
        def __init__(self, endpoint: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    CLOUD_REGION_FIELD_NUMBER: _ClassVar[int]
    AWS_FIELD_NUMBER: _ClassVar[int]
    name: str
    region: str
    port: int
    endpoint: str
    cloud_region: str
    aws: CreatePrivateLinkRequest.AWSCreateConfig
    def __init__(self, name: _Optional[str] = ..., region: _Optional[str] = ..., port: _Optional[int] = ..., endpoint: _Optional[str] = ..., cloud_region: _Optional[str] = ..., aws: _Optional[_Union[CreatePrivateLinkRequest.AWSCreateConfig, _Mapping]] = ...) -> None: ...

class CreatePrivateLinkResponse(_message.Message):
    __slots__ = ("private_link",)
    PRIVATE_LINK_FIELD_NUMBER: _ClassVar[int]
    private_link: PrivateLink
    def __init__(self, private_link: _Optional[_Union[PrivateLink, _Mapping]] = ...) -> None: ...

class DestroyPrivateLinkRequest(_message.Message):
    __slots__ = ("private_link_id",)
    PRIVATE_LINK_ID_FIELD_NUMBER: _ClassVar[int]
    private_link_id: str
    def __init__(self, private_link_id: _Optional[str] = ...) -> None: ...

class DestroyPrivateLinkResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPrivateLinksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPrivateLinksResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[PrivateLink]
    def __init__(self, items: _Optional[_Iterable[_Union[PrivateLink, _Mapping]]] = ...) -> None: ...

class GetPrivateLinkStatusRequest(_message.Message):
    __slots__ = ("private_link_id",)
    PRIVATE_LINK_ID_FIELD_NUMBER: _ClassVar[int]
    private_link_id: str
    def __init__(self, private_link_id: _Optional[str] = ...) -> None: ...

class GetPrivateLinkStatusResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: PrivateLinkStatus
    def __init__(self, value: _Optional[_Union[PrivateLinkStatus, _Mapping]] = ...) -> None: ...
