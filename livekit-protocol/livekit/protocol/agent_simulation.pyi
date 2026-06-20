from .agent_pb import agent_session as _agent_session
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import cloud_agent as _cloud_agent
from . import models as _models
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SimulationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIMULATION_MODE_UNSPECIFIED: _ClassVar[SimulationMode]
    SIMULATION_MODE_TEXT: _ClassVar[SimulationMode]
    SIMULATION_MODE_AUDIO: _ClassVar[SimulationMode]
SIMULATION_MODE_UNSPECIFIED: SimulationMode
SIMULATION_MODE_TEXT: SimulationMode
SIMULATION_MODE_AUDIO: SimulationMode

class SimulationRunSummary(_message.Message):
    __slots__ = ("passed", "failed", "going_well", "to_improve", "issues", "chat_history")
    class ChatHistoryEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _agent_session.ChatContext
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_agent_session.ChatContext, _Mapping]] = ...) -> None: ...
    class Issue(_message.Message):
        __slots__ = ("description", "suggestion", "label")
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        SUGGESTION_FIELD_NUMBER: _ClassVar[int]
        LABEL_FIELD_NUMBER: _ClassVar[int]
        description: str
        suggestion: str
        label: str
        def __init__(self, description: _Optional[str] = ..., suggestion: _Optional[str] = ..., label: _Optional[str] = ...) -> None: ...
    PASSED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    GOING_WELL_FIELD_NUMBER: _ClassVar[int]
    TO_IMPROVE_FIELD_NUMBER: _ClassVar[int]
    ISSUES_FIELD_NUMBER: _ClassVar[int]
    CHAT_HISTORY_FIELD_NUMBER: _ClassVar[int]
    passed: int
    failed: int
    going_well: str
    to_improve: str
    issues: _containers.RepeatedCompositeFieldContainer[SimulationRunSummary.Issue]
    chat_history: _containers.MessageMap[str, _agent_session.ChatContext]
    def __init__(self, passed: _Optional[int] = ..., failed: _Optional[int] = ..., going_well: _Optional[str] = ..., to_improve: _Optional[str] = ..., issues: _Optional[_Iterable[_Union[SimulationRunSummary.Issue, _Mapping]]] = ..., chat_history: _Optional[_Mapping[str, _agent_session.ChatContext]] = ...) -> None: ...

class SimulationRun(_message.Message):
    __slots__ = ("id", "project_id", "status", "agent_description", "error", "created_at", "jobs", "summary", "agent_name", "scenario_group", "ended_at", "job_count", "passed_count", "failed_count", "num_simulations", "usage", "concurrency", "mode")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_PENDING_UPLOAD: _ClassVar[SimulationRun.Status]
        STATUS_GENERATING: _ClassVar[SimulationRun.Status]
        STATUS_RUNNING: _ClassVar[SimulationRun.Status]
        STATUS_SUMMARIZING: _ClassVar[SimulationRun.Status]
        STATUS_COMPLETED: _ClassVar[SimulationRun.Status]
        STATUS_FAILED: _ClassVar[SimulationRun.Status]
        STATUS_CANCELLED: _ClassVar[SimulationRun.Status]
    STATUS_PENDING_UPLOAD: SimulationRun.Status
    STATUS_GENERATING: SimulationRun.Status
    STATUS_RUNNING: SimulationRun.Status
    STATUS_SUMMARIZING: SimulationRun.Status
    STATUS_COMPLETED: SimulationRun.Status
    STATUS_FAILED: SimulationRun.Status
    STATUS_CANCELLED: SimulationRun.Status
    class Job(_message.Message):
        __slots__ = ("id", "status", "instructions", "error", "agent_expectations", "label", "tags", "room_name", "started_at", "ended_at", "room_id", "usage")
        class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            STATUS_PENDING: _ClassVar[SimulationRun.Job.Status]
            STATUS_RUNNING: _ClassVar[SimulationRun.Job.Status]
            STATUS_COMPLETED: _ClassVar[SimulationRun.Job.Status]
            STATUS_FAILED: _ClassVar[SimulationRun.Job.Status]
            STATUS_CANCELLED: _ClassVar[SimulationRun.Job.Status]
        STATUS_PENDING: SimulationRun.Job.Status
        STATUS_RUNNING: SimulationRun.Job.Status
        STATUS_COMPLETED: SimulationRun.Job.Status
        STATUS_FAILED: SimulationRun.Job.Status
        STATUS_CANCELLED: SimulationRun.Job.Status
        class Usage(_message.Message):
            __slots__ = ("text_turns_count", "audio_turns_count")
            TEXT_TURNS_COUNT_FIELD_NUMBER: _ClassVar[int]
            AUDIO_TURNS_COUNT_FIELD_NUMBER: _ClassVar[int]
            text_turns_count: int
            audio_turns_count: int
            def __init__(self, text_turns_count: _Optional[int] = ..., audio_turns_count: _Optional[int] = ...) -> None: ...
        ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        AGENT_EXPECTATIONS_FIELD_NUMBER: _ClassVar[int]
        LABEL_FIELD_NUMBER: _ClassVar[int]
        TAGS_FIELD_NUMBER: _ClassVar[int]
        ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        ENDED_AT_FIELD_NUMBER: _ClassVar[int]
        ROOM_ID_FIELD_NUMBER: _ClassVar[int]
        USAGE_FIELD_NUMBER: _ClassVar[int]
        id: str
        status: SimulationRun.Job.Status
        instructions: str
        error: str
        agent_expectations: str
        label: str
        tags: _containers.RepeatedScalarFieldContainer[str]
        room_name: str
        started_at: _timestamp_pb2.Timestamp
        ended_at: _timestamp_pb2.Timestamp
        room_id: str
        usage: SimulationRun.Job.Usage
        def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[SimulationRun.Job.Status, str]] = ..., instructions: _Optional[str] = ..., error: _Optional[str] = ..., agent_expectations: _Optional[str] = ..., label: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., room_name: _Optional[str] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., room_id: _Optional[str] = ..., usage: _Optional[_Union[SimulationRun.Job.Usage, _Mapping]] = ...) -> None: ...
    class Create(_message.Message):
        __slots__ = ()
        class Request(_message.Message):
            __slots__ = ("project_id", "agent_name", "num_simulations", "region", "scenario_group", "concurrency", "mode")
            PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
            AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
            NUM_SIMULATIONS_FIELD_NUMBER: _ClassVar[int]
            REGION_FIELD_NUMBER: _ClassVar[int]
            SCENARIO_GROUP_FIELD_NUMBER: _ClassVar[int]
            CONCURRENCY_FIELD_NUMBER: _ClassVar[int]
            MODE_FIELD_NUMBER: _ClassVar[int]
            project_id: str
            agent_name: str
            num_simulations: int
            region: str
            scenario_group: ScenarioGroup
            concurrency: int
            mode: SimulationMode
            def __init__(self, project_id: _Optional[str] = ..., agent_name: _Optional[str] = ..., num_simulations: _Optional[int] = ..., region: _Optional[str] = ..., scenario_group: _Optional[_Union[ScenarioGroup, _Mapping]] = ..., concurrency: _Optional[int] = ..., mode: _Optional[_Union[SimulationMode, str]] = ...) -> None: ...
        class Response(_message.Message):
            __slots__ = ("simulation_run_id", "presigned_post_request")
            SIMULATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
            PRESIGNED_POST_REQUEST_FIELD_NUMBER: _ClassVar[int]
            simulation_run_id: str
            presigned_post_request: _cloud_agent.PresignedPostRequest
            def __init__(self, simulation_run_id: _Optional[str] = ..., presigned_post_request: _Optional[_Union[_cloud_agent.PresignedPostRequest, _Mapping]] = ...) -> None: ...
        def __init__(self) -> None: ...
    class ConfirmSourceUpload(_message.Message):
        __slots__ = ()
        class Request(_message.Message):
            __slots__ = ("project_id", "simulation_run_id", "code_entrypoint")
            PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
            SIMULATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
            CODE_ENTRYPOINT_FIELD_NUMBER: _ClassVar[int]
            project_id: str
            simulation_run_id: str
            code_entrypoint: str
            def __init__(self, project_id: _Optional[str] = ..., simulation_run_id: _Optional[str] = ..., code_entrypoint: _Optional[str] = ...) -> None: ...
        class Response(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        def __init__(self) -> None: ...
    class Get(_message.Message):
        __slots__ = ()
        class Request(_message.Message):
            __slots__ = ("project_id", "simulation_run_id")
            PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
            SIMULATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
            project_id: str
            simulation_run_id: str
            def __init__(self, project_id: _Optional[str] = ..., simulation_run_id: _Optional[str] = ...) -> None: ...
        class Response(_message.Message):
            __slots__ = ("run",)
            RUN_FIELD_NUMBER: _ClassVar[int]
            run: SimulationRun
            def __init__(self, run: _Optional[_Union[SimulationRun, _Mapping]] = ...) -> None: ...
        def __init__(self) -> None: ...
    class List(_message.Message):
        __slots__ = ()
        class Request(_message.Message):
            __slots__ = ("project_id", "status", "page_token")
            PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
            STATUS_FIELD_NUMBER: _ClassVar[int]
            PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
            project_id: str
            status: SimulationRun.Status
            page_token: _models.TokenPagination
            def __init__(self, project_id: _Optional[str] = ..., status: _Optional[_Union[SimulationRun.Status, str]] = ..., page_token: _Optional[_Union[_models.TokenPagination, _Mapping]] = ...) -> None: ...
        class Response(_message.Message):
            __slots__ = ("runs", "next_page_token")
            RUNS_FIELD_NUMBER: _ClassVar[int]
            NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
            runs: _containers.RepeatedCompositeFieldContainer[SimulationRun]
            next_page_token: _models.TokenPagination
            def __init__(self, runs: _Optional[_Iterable[_Union[SimulationRun, _Mapping]]] = ..., next_page_token: _Optional[_Union[_models.TokenPagination, _Mapping]] = ...) -> None: ...
        def __init__(self) -> None: ...
    class Cancel(_message.Message):
        __slots__ = ()
        class Request(_message.Message):
            __slots__ = ("project_id", "simulation_run_id")
            PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
            SIMULATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
            project_id: str
            simulation_run_id: str
            def __init__(self, project_id: _Optional[str] = ..., simulation_run_id: _Optional[str] = ...) -> None: ...
        class Response(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        def __init__(self) -> None: ...
    class Usage(_message.Message):
        __slots__ = ("text_turns_count", "audio_turns_count")
        TEXT_TURNS_COUNT_FIELD_NUMBER: _ClassVar[int]
        AUDIO_TURNS_COUNT_FIELD_NUMBER: _ClassVar[int]
        text_turns_count: int
        audio_turns_count: int
        def __init__(self, text_turns_count: _Optional[int] = ..., audio_turns_count: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AGENT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    JOBS_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SCENARIO_GROUP_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    JOB_COUNT_FIELD_NUMBER: _ClassVar[int]
    PASSED_COUNT_FIELD_NUMBER: _ClassVar[int]
    FAILED_COUNT_FIELD_NUMBER: _ClassVar[int]
    NUM_SIMULATIONS_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    CONCURRENCY_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    status: SimulationRun.Status
    agent_description: str
    error: str
    created_at: _timestamp_pb2.Timestamp
    jobs: _containers.RepeatedCompositeFieldContainer[SimulationRun.Job]
    summary: SimulationRunSummary
    agent_name: str
    scenario_group: ScenarioGroup
    ended_at: _timestamp_pb2.Timestamp
    job_count: int
    passed_count: int
    failed_count: int
    num_simulations: int
    usage: SimulationRun.Usage
    concurrency: int
    mode: SimulationMode
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ..., status: _Optional[_Union[SimulationRun.Status, str]] = ..., agent_description: _Optional[str] = ..., error: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., jobs: _Optional[_Iterable[_Union[SimulationRun.Job, _Mapping]]] = ..., summary: _Optional[_Union[SimulationRunSummary, _Mapping]] = ..., agent_name: _Optional[str] = ..., scenario_group: _Optional[_Union[ScenarioGroup, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., job_count: _Optional[int] = ..., passed_count: _Optional[int] = ..., failed_count: _Optional[int] = ..., num_simulations: _Optional[int] = ..., usage: _Optional[_Union[SimulationRun.Usage, _Mapping]] = ..., concurrency: _Optional[int] = ..., mode: _Optional[_Union[SimulationMode, str]] = ...) -> None: ...

class Scenario(_message.Message):
    __slots__ = ("label", "instructions", "agent_expectations", "tags", "userdata")
    class CreateFromSession(_message.Message):
        __slots__ = ()
        class Request(_message.Message):
            __slots__ = ("project_id", "room_id", "region")
            PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
            ROOM_ID_FIELD_NUMBER: _ClassVar[int]
            REGION_FIELD_NUMBER: _ClassVar[int]
            project_id: str
            room_id: str
            region: str
            def __init__(self, project_id: _Optional[str] = ..., room_id: _Optional[str] = ..., region: _Optional[str] = ...) -> None: ...
        class Response(_message.Message):
            __slots__ = ("scenario",)
            SCENARIO_FIELD_NUMBER: _ClassVar[int]
            scenario: Scenario
            def __init__(self, scenario: _Optional[_Union[Scenario, _Mapping]] = ...) -> None: ...
        def __init__(self) -> None: ...
    class TagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    LABEL_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    AGENT_EXPECTATIONS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    USERDATA_FIELD_NUMBER: _ClassVar[int]
    label: str
    instructions: str
    agent_expectations: str
    tags: _containers.ScalarMap[str, str]
    userdata: str
    def __init__(self, label: _Optional[str] = ..., instructions: _Optional[str] = ..., agent_expectations: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ..., userdata: _Optional[str] = ...) -> None: ...

class ScenarioGroup(_message.Message):
    __slots__ = ("name", "scenarios")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCENARIOS_FIELD_NUMBER: _ClassVar[int]
    name: str
    scenarios: _containers.RepeatedCompositeFieldContainer[Scenario]
    def __init__(self, name: _Optional[str] = ..., scenarios: _Optional[_Iterable[_Union[Scenario, _Mapping]]] = ...) -> None: ...

class SimulationDispatch(_message.Message):
    __slots__ = ("simulation_run_id", "job_id", "scenario", "mode")
    SIMULATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    SCENARIO_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    simulation_run_id: str
    job_id: str
    scenario: Scenario
    mode: SimulationMode
    def __init__(self, simulation_run_id: _Optional[str] = ..., job_id: _Optional[str] = ..., scenario: _Optional[_Union[Scenario, _Mapping]] = ..., mode: _Optional[_Union[SimulationMode, str]] = ...) -> None: ...
