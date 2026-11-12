from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import agent_session as _agent_session
from ..logger_pb import options as _options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentThread(_message.Message):
    __slots__ = ()
    class SortOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SORT_ORDER_UNSPECIFIED: _ClassVar[AgentThread.SortOrder]
        SORT_ORDER_ASC: _ClassVar[AgentThread.SortOrder]
        SORT_ORDER_DESC: _ClassVar[AgentThread.SortOrder]
    SORT_ORDER_UNSPECIFIED: AgentThread.SortOrder
    SORT_ORDER_ASC: AgentThread.SortOrder
    SORT_ORDER_DESC: AgentThread.SortOrder
    class CreateRequest(_message.Message):
        __slots__ = ("scope", "attributes", "idle_ttl")
        class AttributesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        SCOPE_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
        IDLE_TTL_FIELD_NUMBER: _ClassVar[int]
        scope: str
        attributes: _containers.ScalarMap[str, str]
        idle_ttl: _duration_pb2.Duration
        def __init__(self, scope: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ..., idle_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class GetRequest(_message.Message):
        __slots__ = ("thread_id",)
        THREAD_ID_FIELD_NUMBER: _ClassVar[int]
        thread_id: str
        def __init__(self, thread_id: _Optional[str] = ...) -> None: ...
    class ListRequest(_message.Message):
        __slots__ = ("scope", "page_token", "limit")
        SCOPE_FIELD_NUMBER: _ClassVar[int]
        PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
        LIMIT_FIELD_NUMBER: _ClassVar[int]
        scope: str
        page_token: str
        limit: int
        def __init__(self, scope: _Optional[str] = ..., page_token: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...
    class ListResponse(_message.Message):
        __slots__ = ("threads", "next_page_token")
        THREADS_FIELD_NUMBER: _ClassVar[int]
        NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
        threads: _containers.RepeatedCompositeFieldContainer[AgentThread.Thread]
        next_page_token: str
        def __init__(self, threads: _Optional[_Iterable[_Union[AgentThread.Thread, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...
    class UpdateRequest(_message.Message):
        __slots__ = ("thread_id", "attributes", "idle_ttl")
        class AttributesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        THREAD_ID_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
        IDLE_TTL_FIELD_NUMBER: _ClassVar[int]
        thread_id: str
        attributes: _containers.ScalarMap[str, str]
        idle_ttl: _duration_pb2.Duration
        def __init__(self, thread_id: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ..., idle_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class DeleteRequest(_message.Message):
        __slots__ = ("thread_id",)
        THREAD_ID_FIELD_NUMBER: _ClassVar[int]
        thread_id: str
        def __init__(self, thread_id: _Optional[str] = ...) -> None: ...
    class DeleteResponse(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GetItemsRequest(_message.Message):
        __slots__ = ("thread_id", "agent", "page_token", "limit", "sort_order")
        THREAD_ID_FIELD_NUMBER: _ClassVar[int]
        AGENT_FIELD_NUMBER: _ClassVar[int]
        PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
        LIMIT_FIELD_NUMBER: _ClassVar[int]
        SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
        thread_id: str
        agent: str
        page_token: str
        limit: int
        sort_order: AgentThread.SortOrder
        def __init__(self, thread_id: _Optional[str] = ..., agent: _Optional[str] = ..., page_token: _Optional[str] = ..., limit: _Optional[int] = ..., sort_order: _Optional[_Union[AgentThread.SortOrder, str]] = ...) -> None: ...
    class GetItemsResponse(_message.Message):
        __slots__ = ("items", "next_page_token")
        ITEMS_FIELD_NUMBER: _ClassVar[int]
        NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
        items: _containers.RepeatedCompositeFieldContainer[AgentThread.Item]
        next_page_token: str
        def __init__(self, items: _Optional[_Iterable[_Union[AgentThread.Item, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...
    class Item(_message.Message):
        __slots__ = ("agent", "seq", "message_id", "item")
        AGENT_FIELD_NUMBER: _ClassVar[int]
        SEQ_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
        ITEM_FIELD_NUMBER: _ClassVar[int]
        agent: str
        seq: int
        message_id: str
        item: _agent_session.ChatContext.ChatItem
        def __init__(self, agent: _Optional[str] = ..., seq: _Optional[int] = ..., message_id: _Optional[str] = ..., item: _Optional[_Union[_agent_session.ChatContext.ChatItem, _Mapping]] = ...) -> None: ...
    class Thread(_message.Message):
        __slots__ = ("thread_id", "scope", "attributes", "created_at", "last_active", "expires_at", "idle_ttl", "database_id")
        class AttributesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        THREAD_ID_FIELD_NUMBER: _ClassVar[int]
        SCOPE_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        LAST_ACTIVE_FIELD_NUMBER: _ClassVar[int]
        EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
        IDLE_TTL_FIELD_NUMBER: _ClassVar[int]
        DATABASE_ID_FIELD_NUMBER: _ClassVar[int]
        thread_id: str
        scope: str
        attributes: _containers.ScalarMap[str, str]
        created_at: _timestamp_pb2.Timestamp
        last_active: _timestamp_pb2.Timestamp
        expires_at: _timestamp_pb2.Timestamp
        idle_ttl: _duration_pb2.Duration
        database_id: str
        def __init__(self, thread_id: _Optional[str] = ..., scope: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_active: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., idle_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., database_id: _Optional[str] = ...) -> None: ...
    def __init__(self) -> None: ...

class AgentTask(_message.Message):
    __slots__ = ()
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[AgentTask.Status]
        RUNNING: _ClassVar[AgentTask.Status]
        COMPLETED: _ClassVar[AgentTask.Status]
        FAILED: _ClassVar[AgentTask.Status]
        CANCELED: _ClassVar[AgentTask.Status]
    UNSPECIFIED: AgentTask.Status
    RUNNING: AgentTask.Status
    COMPLETED: AgentTask.Status
    FAILED: AgentTask.Status
    CANCELED: AgentTask.Status
    class GetTasksRequest(_message.Message):
        __slots__ = ("thread_id", "status", "page_token", "limit")
        THREAD_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
        LIMIT_FIELD_NUMBER: _ClassVar[int]
        thread_id: str
        status: AgentTask.Status
        page_token: str
        limit: int
        def __init__(self, thread_id: _Optional[str] = ..., status: _Optional[_Union[AgentTask.Status, str]] = ..., page_token: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...
    class GetTasksResponse(_message.Message):
        __slots__ = ("tasks", "next_page_token")
        TASKS_FIELD_NUMBER: _ClassVar[int]
        NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
        tasks: _containers.RepeatedCompositeFieldContainer[AgentTask.Task]
        next_page_token: str
        def __init__(self, tasks: _Optional[_Iterable[_Union[AgentTask.Task, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...
    class Task(_message.Message):
        __slots__ = ("task_id", "thread_id", "name", "status", "updated_at")
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        THREAD_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
        task_id: str
        thread_id: str
        name: str
        status: AgentTask.Status
        updated_at: _timestamp_pb2.Timestamp
        def __init__(self, task_id: _Optional[str] = ..., thread_id: _Optional[str] = ..., name: _Optional[str] = ..., status: _Optional[_Union[AgentTask.Status, str]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    def __init__(self) -> None: ...
