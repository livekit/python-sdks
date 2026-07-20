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
    __slots__ = ("id", "project_id", "status", "agent_description", "error", "created_at", "jobs", "agent_name", "scenario_group", "ended_at", "job_count", "passed_count", "failed_count", "num_simulations", "usage", "concurrency", "mode", "metrics", "summary_zstd")
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
        __slots__ = ("id", "status", "instructions", "error", "agent_expectations", "label", "tags", "room_name", "started_at", "ended_at", "room_id", "usage", "metrics")
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
        METRICS_FIELD_NUMBER: _ClassVar[int]
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
        metrics: SimulationRun.JobMetrics
        def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[SimulationRun.Job.Status, str]] = ..., instructions: _Optional[str] = ..., error: _Optional[str] = ..., agent_expectations: _Optional[str] = ..., label: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., room_name: _Optional[str] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., room_id: _Optional[str] = ..., usage: _Optional[_Union[SimulationRun.Job.Usage, _Mapping]] = ..., metrics: _Optional[_Union[SimulationRun.JobMetrics, _Mapping]] = ...) -> None: ...
    class JobMetrics(_message.Message):
        __slots__ = ("accuracy_score", "experience_score", "task_completion", "stt", "llm", "tts", "conversation", "simulator", "turns", "judge_model", "audio_judge_model", "has_remote_session", "t0")
        class STT(_message.Message):
            __slots__ = ("wer", "words", "word_errors", "cer", "chars", "char_errors", "keyterm_recall", "keyterms_uttered", "keyterms_recognized", "transcription_latency_ms")
            WER_FIELD_NUMBER: _ClassVar[int]
            WORDS_FIELD_NUMBER: _ClassVar[int]
            WORD_ERRORS_FIELD_NUMBER: _ClassVar[int]
            CER_FIELD_NUMBER: _ClassVar[int]
            CHARS_FIELD_NUMBER: _ClassVar[int]
            CHAR_ERRORS_FIELD_NUMBER: _ClassVar[int]
            KEYTERM_RECALL_FIELD_NUMBER: _ClassVar[int]
            KEYTERMS_UTTERED_FIELD_NUMBER: _ClassVar[int]
            KEYTERMS_RECOGNIZED_FIELD_NUMBER: _ClassVar[int]
            TRANSCRIPTION_LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
            wer: float
            words: int
            word_errors: int
            cer: float
            chars: int
            char_errors: int
            keyterm_recall: float
            keyterms_uttered: int
            keyterms_recognized: int
            transcription_latency_ms: int
            def __init__(self, wer: _Optional[float] = ..., words: _Optional[int] = ..., word_errors: _Optional[int] = ..., cer: _Optional[float] = ..., chars: _Optional[int] = ..., char_errors: _Optional[int] = ..., keyterm_recall: _Optional[float] = ..., keyterms_uttered: _Optional[int] = ..., keyterms_recognized: _Optional[int] = ..., transcription_latency_ms: _Optional[int] = ...) -> None: ...
        class LLM(_message.Message):
            __slots__ = ("ttft_ms", "ttfs_ms", "tokens_per_second", "conciseness_score")
            TTFT_MS_FIELD_NUMBER: _ClassVar[int]
            TTFS_MS_FIELD_NUMBER: _ClassVar[int]
            TOKENS_PER_SECOND_FIELD_NUMBER: _ClassVar[int]
            CONCISENESS_SCORE_FIELD_NUMBER: _ClassVar[int]
            ttft_ms: int
            ttfs_ms: int
            tokens_per_second: float
            conciseness_score: float
            def __init__(self, ttft_ms: _Optional[int] = ..., ttfs_ms: _Optional[int] = ..., tokens_per_second: _Optional[float] = ..., conciseness_score: _Optional[float] = ...) -> None: ...
        class TTS(_message.Message):
            __slots__ = ("ttfa_ms", "ttfb_ms", "wer", "words", "word_errors", "cer", "chars", "char_errors", "speech_rate_wpm", "naturalness_score", "enunciation_score")
            TTFA_MS_FIELD_NUMBER: _ClassVar[int]
            TTFB_MS_FIELD_NUMBER: _ClassVar[int]
            WER_FIELD_NUMBER: _ClassVar[int]
            WORDS_FIELD_NUMBER: _ClassVar[int]
            WORD_ERRORS_FIELD_NUMBER: _ClassVar[int]
            CER_FIELD_NUMBER: _ClassVar[int]
            CHARS_FIELD_NUMBER: _ClassVar[int]
            CHAR_ERRORS_FIELD_NUMBER: _ClassVar[int]
            SPEECH_RATE_WPM_FIELD_NUMBER: _ClassVar[int]
            NATURALNESS_SCORE_FIELD_NUMBER: _ClassVar[int]
            ENUNCIATION_SCORE_FIELD_NUMBER: _ClassVar[int]
            ttfa_ms: int
            ttfb_ms: int
            wer: float
            words: int
            word_errors: int
            cer: float
            chars: int
            char_errors: int
            speech_rate_wpm: float
            naturalness_score: float
            enunciation_score: float
            def __init__(self, ttfa_ms: _Optional[int] = ..., ttfb_ms: _Optional[int] = ..., wer: _Optional[float] = ..., words: _Optional[int] = ..., word_errors: _Optional[int] = ..., cer: _Optional[float] = ..., chars: _Optional[int] = ..., char_errors: _Optional[int] = ..., speech_rate_wpm: _Optional[float] = ..., naturalness_score: _Optional[float] = ..., enunciation_score: _Optional[float] = ...) -> None: ...
        class Conversation(_message.Message):
            __slots__ = ("turn_taking_score", "response_latency_p50_ms", "response_latency_p95_ms", "response_latency_p99_ms", "agent_yield_latency_ms", "eot_misprediction_count", "overlap_ratio", "overlap_speech_ms", "total_speech_ms", "silence_total_ms", "awkward_silence_count", "unanswered_persona_turns", "false_interruption_count", "false_interruption_unrecovered_count", "agent_reported_e2e_latency_ms")
            TURN_TAKING_SCORE_FIELD_NUMBER: _ClassVar[int]
            RESPONSE_LATENCY_P50_MS_FIELD_NUMBER: _ClassVar[int]
            RESPONSE_LATENCY_P95_MS_FIELD_NUMBER: _ClassVar[int]
            RESPONSE_LATENCY_P99_MS_FIELD_NUMBER: _ClassVar[int]
            AGENT_YIELD_LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
            EOT_MISPREDICTION_COUNT_FIELD_NUMBER: _ClassVar[int]
            OVERLAP_RATIO_FIELD_NUMBER: _ClassVar[int]
            OVERLAP_SPEECH_MS_FIELD_NUMBER: _ClassVar[int]
            TOTAL_SPEECH_MS_FIELD_NUMBER: _ClassVar[int]
            SILENCE_TOTAL_MS_FIELD_NUMBER: _ClassVar[int]
            AWKWARD_SILENCE_COUNT_FIELD_NUMBER: _ClassVar[int]
            UNANSWERED_PERSONA_TURNS_FIELD_NUMBER: _ClassVar[int]
            FALSE_INTERRUPTION_COUNT_FIELD_NUMBER: _ClassVar[int]
            FALSE_INTERRUPTION_UNRECOVERED_COUNT_FIELD_NUMBER: _ClassVar[int]
            AGENT_REPORTED_E2E_LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
            turn_taking_score: float
            response_latency_p50_ms: int
            response_latency_p95_ms: int
            response_latency_p99_ms: int
            agent_yield_latency_ms: int
            eot_misprediction_count: int
            overlap_ratio: float
            overlap_speech_ms: int
            total_speech_ms: int
            silence_total_ms: int
            awkward_silence_count: int
            unanswered_persona_turns: int
            false_interruption_count: int
            false_interruption_unrecovered_count: int
            agent_reported_e2e_latency_ms: int
            def __init__(self, turn_taking_score: _Optional[float] = ..., response_latency_p50_ms: _Optional[int] = ..., response_latency_p95_ms: _Optional[int] = ..., response_latency_p99_ms: _Optional[int] = ..., agent_yield_latency_ms: _Optional[int] = ..., eot_misprediction_count: _Optional[int] = ..., overlap_ratio: _Optional[float] = ..., overlap_speech_ms: _Optional[int] = ..., total_speech_ms: _Optional[int] = ..., silence_total_ms: _Optional[int] = ..., awkward_silence_count: _Optional[int] = ..., unanswered_persona_turns: _Optional[int] = ..., false_interruption_count: _Optional[int] = ..., false_interruption_unrecovered_count: _Optional[int] = ..., agent_reported_e2e_latency_ms: _Optional[int] = ...) -> None: ...
        class Simulator(_message.Message):
            __slots__ = ("early_termination", "late_termination")
            EARLY_TERMINATION_FIELD_NUMBER: _ClassVar[int]
            LATE_TERMINATION_FIELD_NUMBER: _ClassVar[int]
            early_termination: bool
            late_termination: bool
            def __init__(self, early_termination: bool = ..., late_termination: bool = ...) -> None: ...
        class Turn(_message.Message):
            __slots__ = ("index", "role", "start_ms", "end_ms", "response_latency_ms", "transcription_delay_ms", "llm_ttft_ms", "llm_ttfs_ms", "tts_ttfa_ms", "tts_ttfb_ms", "agent_reported_e2e_latency_ms", "conciseness_score", "naturalness_score", "enunciation_score", "flags")
            INDEX_FIELD_NUMBER: _ClassVar[int]
            ROLE_FIELD_NUMBER: _ClassVar[int]
            START_MS_FIELD_NUMBER: _ClassVar[int]
            END_MS_FIELD_NUMBER: _ClassVar[int]
            RESPONSE_LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
            TRANSCRIPTION_DELAY_MS_FIELD_NUMBER: _ClassVar[int]
            LLM_TTFT_MS_FIELD_NUMBER: _ClassVar[int]
            LLM_TTFS_MS_FIELD_NUMBER: _ClassVar[int]
            TTS_TTFA_MS_FIELD_NUMBER: _ClassVar[int]
            TTS_TTFB_MS_FIELD_NUMBER: _ClassVar[int]
            AGENT_REPORTED_E2E_LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
            CONCISENESS_SCORE_FIELD_NUMBER: _ClassVar[int]
            NATURALNESS_SCORE_FIELD_NUMBER: _ClassVar[int]
            ENUNCIATION_SCORE_FIELD_NUMBER: _ClassVar[int]
            FLAGS_FIELD_NUMBER: _ClassVar[int]
            index: int
            role: _agent_session.ChatRole
            start_ms: int
            end_ms: int
            response_latency_ms: int
            transcription_delay_ms: int
            llm_ttft_ms: int
            llm_ttfs_ms: int
            tts_ttfa_ms: int
            tts_ttfb_ms: int
            agent_reported_e2e_latency_ms: int
            conciseness_score: float
            naturalness_score: float
            enunciation_score: float
            flags: _containers.RepeatedScalarFieldContainer[str]
            def __init__(self, index: _Optional[int] = ..., role: _Optional[_Union[_agent_session.ChatRole, str]] = ..., start_ms: _Optional[int] = ..., end_ms: _Optional[int] = ..., response_latency_ms: _Optional[int] = ..., transcription_delay_ms: _Optional[int] = ..., llm_ttft_ms: _Optional[int] = ..., llm_ttfs_ms: _Optional[int] = ..., tts_ttfa_ms: _Optional[int] = ..., tts_ttfb_ms: _Optional[int] = ..., agent_reported_e2e_latency_ms: _Optional[int] = ..., conciseness_score: _Optional[float] = ..., naturalness_score: _Optional[float] = ..., enunciation_score: _Optional[float] = ..., flags: _Optional[_Iterable[str]] = ...) -> None: ...
        ACCURACY_SCORE_FIELD_NUMBER: _ClassVar[int]
        EXPERIENCE_SCORE_FIELD_NUMBER: _ClassVar[int]
        TASK_COMPLETION_FIELD_NUMBER: _ClassVar[int]
        STT_FIELD_NUMBER: _ClassVar[int]
        LLM_FIELD_NUMBER: _ClassVar[int]
        TTS_FIELD_NUMBER: _ClassVar[int]
        CONVERSATION_FIELD_NUMBER: _ClassVar[int]
        SIMULATOR_FIELD_NUMBER: _ClassVar[int]
        TURNS_FIELD_NUMBER: _ClassVar[int]
        JUDGE_MODEL_FIELD_NUMBER: _ClassVar[int]
        AUDIO_JUDGE_MODEL_FIELD_NUMBER: _ClassVar[int]
        HAS_REMOTE_SESSION_FIELD_NUMBER: _ClassVar[int]
        T0_FIELD_NUMBER: _ClassVar[int]
        accuracy_score: float
        experience_score: float
        task_completion: float
        stt: SimulationRun.JobMetrics.STT
        llm: SimulationRun.JobMetrics.LLM
        tts: SimulationRun.JobMetrics.TTS
        conversation: SimulationRun.JobMetrics.Conversation
        simulator: SimulationRun.JobMetrics.Simulator
        turns: _containers.RepeatedCompositeFieldContainer[SimulationRun.JobMetrics.Turn]
        judge_model: str
        audio_judge_model: str
        has_remote_session: bool
        t0: _timestamp_pb2.Timestamp
        def __init__(self, accuracy_score: _Optional[float] = ..., experience_score: _Optional[float] = ..., task_completion: _Optional[float] = ..., stt: _Optional[_Union[SimulationRun.JobMetrics.STT, _Mapping]] = ..., llm: _Optional[_Union[SimulationRun.JobMetrics.LLM, _Mapping]] = ..., tts: _Optional[_Union[SimulationRun.JobMetrics.TTS, _Mapping]] = ..., conversation: _Optional[_Union[SimulationRun.JobMetrics.Conversation, _Mapping]] = ..., simulator: _Optional[_Union[SimulationRun.JobMetrics.Simulator, _Mapping]] = ..., turns: _Optional[_Iterable[_Union[SimulationRun.JobMetrics.Turn, _Mapping]]] = ..., judge_model: _Optional[str] = ..., audio_judge_model: _Optional[str] = ..., has_remote_session: bool = ..., t0: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class RunMetrics(_message.Message):
        __slots__ = ("accuracy_score", "experience_score", "scenario_pass_rate", "stt", "llm", "tts", "conversation", "jobs_total", "jobs_measured", "jobs_simulator_fault")
        ACCURACY_SCORE_FIELD_NUMBER: _ClassVar[int]
        EXPERIENCE_SCORE_FIELD_NUMBER: _ClassVar[int]
        SCENARIO_PASS_RATE_FIELD_NUMBER: _ClassVar[int]
        STT_FIELD_NUMBER: _ClassVar[int]
        LLM_FIELD_NUMBER: _ClassVar[int]
        TTS_FIELD_NUMBER: _ClassVar[int]
        CONVERSATION_FIELD_NUMBER: _ClassVar[int]
        JOBS_TOTAL_FIELD_NUMBER: _ClassVar[int]
        JOBS_MEASURED_FIELD_NUMBER: _ClassVar[int]
        JOBS_SIMULATOR_FAULT_FIELD_NUMBER: _ClassVar[int]
        accuracy_score: float
        experience_score: float
        scenario_pass_rate: float
        stt: SimulationRun.JobMetrics.STT
        llm: SimulationRun.JobMetrics.LLM
        tts: SimulationRun.JobMetrics.TTS
        conversation: SimulationRun.JobMetrics.Conversation
        jobs_total: int
        jobs_measured: int
        jobs_simulator_fault: int
        def __init__(self, accuracy_score: _Optional[float] = ..., experience_score: _Optional[float] = ..., scenario_pass_rate: _Optional[float] = ..., stt: _Optional[_Union[SimulationRun.JobMetrics.STT, _Mapping]] = ..., llm: _Optional[_Union[SimulationRun.JobMetrics.LLM, _Mapping]] = ..., tts: _Optional[_Union[SimulationRun.JobMetrics.TTS, _Mapping]] = ..., conversation: _Optional[_Union[SimulationRun.JobMetrics.Conversation, _Mapping]] = ..., jobs_total: _Optional[int] = ..., jobs_measured: _Optional[int] = ..., jobs_simulator_fault: _Optional[int] = ...) -> None: ...
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
    METRICS_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_ZSTD_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    status: SimulationRun.Status
    agent_description: str
    error: str
    created_at: _timestamp_pb2.Timestamp
    jobs: _containers.RepeatedCompositeFieldContainer[SimulationRun.Job]
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
    metrics: SimulationRun.RunMetrics
    summary_zstd: bytes
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ..., status: _Optional[_Union[SimulationRun.Status, str]] = ..., agent_description: _Optional[str] = ..., error: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., jobs: _Optional[_Iterable[_Union[SimulationRun.Job, _Mapping]]] = ..., agent_name: _Optional[str] = ..., scenario_group: _Optional[_Union[ScenarioGroup, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., job_count: _Optional[int] = ..., passed_count: _Optional[int] = ..., failed_count: _Optional[int] = ..., num_simulations: _Optional[int] = ..., usage: _Optional[_Union[SimulationRun.Usage, _Mapping]] = ..., concurrency: _Optional[int] = ..., mode: _Optional[_Union[SimulationMode, str]] = ..., metrics: _Optional[_Union[SimulationRun.RunMetrics, _Mapping]] = ..., summary_zstd: _Optional[bytes] = ...) -> None: ...

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
