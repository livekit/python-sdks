"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
Copyright 2023 LiveKit, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from . import audio_frame_pb2
import builtins
import collections.abc
from . import e2ee_pb2
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
from . import room_pb2
import sys
from . import track_pb2
import typing
from . import video_frame_pb2

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _LogLevel:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _LogLevelEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_LogLevel.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    LOG_ERROR: _LogLevel.ValueType  # 0
    LOG_WARN: _LogLevel.ValueType  # 1
    LOG_INFO: _LogLevel.ValueType  # 2
    LOG_DEBUG: _LogLevel.ValueType  # 3
    LOG_TRACE: _LogLevel.ValueType  # 4

class LogLevel(_LogLevel, metaclass=_LogLevelEnumTypeWrapper): ...

LOG_ERROR: LogLevel.ValueType  # 0
LOG_WARN: LogLevel.ValueType  # 1
LOG_INFO: LogLevel.ValueType  # 2
LOG_DEBUG: LogLevel.ValueType  # 3
LOG_TRACE: LogLevel.ValueType  # 4
global___LogLevel = LogLevel

@typing_extensions.final
class FfiRequest(google.protobuf.message.Message):
    """**How is the livekit-ffi working:
    We refer as the ffi server the Rust server that is running the LiveKit client implementation, and we
    refer as the ffi client the foreign language that commumicates with the ffi server. (e.g Python SDK, Unity SDK, etc...)

    We expose the Rust client implementation of livekit using the protocol defined here.
    Everything starts with a FfiRequest, which is a oneof message that contains all the possible
    requests that can be made to the ffi server.
    The server will then respond with a FfiResponse, which is also a oneof message that contains
    all the possible responses.
    The first request sent to the server must be an InitializeRequest, which contains the a pointer
    to the callback function that will be used to send events and async responses to the ffi client.
    (e.g participant joined, track published, etc...)

    **Useful things know when collaborating on the protocol:**
    Everything is subject to discussion and change :-)

    - The ffi client implementation must never forget to correctly dispose all the owned handles
      that it receives from the server.

    Therefore, the ffi client is easier to implement if there is less handles to manage.

    - We are mainly using FfiHandle on info messages (e.g: RoomInfo, TrackInfo, etc...)
      For this reason, info are only sent once, at creation (We're not using them for updates, we can infer them from
      events on the client implementation).
      e.g: set speaking to true when we receive a ActiveSpeakerChanged event.

    This is the input of livekit_ffi_request function
    We always expect a response (FFIResponse, even if it's empty)
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DISPOSE_FIELD_NUMBER: builtins.int
    CONNECT_FIELD_NUMBER: builtins.int
    DISCONNECT_FIELD_NUMBER: builtins.int
    PUBLISH_TRACK_FIELD_NUMBER: builtins.int
    UNPUBLISH_TRACK_FIELD_NUMBER: builtins.int
    PUBLISH_DATA_FIELD_NUMBER: builtins.int
    SET_SUBSCRIBED_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_METADATA_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_NAME_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_ATTRIBUTES_FIELD_NUMBER: builtins.int
    GET_SESSION_STATS_FIELD_NUMBER: builtins.int
    PUBLISH_TRANSCRIPTION_FIELD_NUMBER: builtins.int
    CREATE_VIDEO_TRACK_FIELD_NUMBER: builtins.int
    CREATE_AUDIO_TRACK_FIELD_NUMBER: builtins.int
    GET_STATS_FIELD_NUMBER: builtins.int
    NEW_VIDEO_STREAM_FIELD_NUMBER: builtins.int
    NEW_VIDEO_SOURCE_FIELD_NUMBER: builtins.int
    CAPTURE_VIDEO_FRAME_FIELD_NUMBER: builtins.int
    VIDEO_CONVERT_FIELD_NUMBER: builtins.int
    NEW_AUDIO_STREAM_FIELD_NUMBER: builtins.int
    NEW_AUDIO_SOURCE_FIELD_NUMBER: builtins.int
    CAPTURE_AUDIO_FRAME_FIELD_NUMBER: builtins.int
    NEW_AUDIO_RESAMPLER_FIELD_NUMBER: builtins.int
    REMIX_AND_RESAMPLE_FIELD_NUMBER: builtins.int
    E2EE_FIELD_NUMBER: builtins.int
    @property
    def dispose(self) -> global___DisposeRequest: ...
    @property
    def connect(self) -> room_pb2.ConnectRequest:
        """Room"""
    @property
    def disconnect(self) -> room_pb2.DisconnectRequest: ...
    @property
    def publish_track(self) -> room_pb2.PublishTrackRequest: ...
    @property
    def unpublish_track(self) -> room_pb2.UnpublishTrackRequest: ...
    @property
    def publish_data(self) -> room_pb2.PublishDataRequest: ...
    @property
    def set_subscribed(self) -> room_pb2.SetSubscribedRequest: ...
    @property
    def update_local_metadata(self) -> room_pb2.SetLocalMetadataRequest: ...
    @property
    def update_local_name(self) -> room_pb2.SetLocalNameRequest: ...
    @property
    def update_local_attributes(self) -> room_pb2.SetLocalAttributesRequest: ...
    @property
    def get_session_stats(self) -> room_pb2.GetSessionStatsRequest: ...
    @property
    def publish_transcription(self) -> room_pb2.PublishTranscriptionRequest: ...
    @property
    def create_video_track(self) -> track_pb2.CreateVideoTrackRequest:
        """Track"""
    @property
    def create_audio_track(self) -> track_pb2.CreateAudioTrackRequest: ...
    @property
    def get_stats(self) -> track_pb2.GetStatsRequest: ...
    @property
    def new_video_stream(self) -> video_frame_pb2.NewVideoStreamRequest:
        """Video"""
    @property
    def new_video_source(self) -> video_frame_pb2.NewVideoSourceRequest: ...
    @property
    def capture_video_frame(self) -> video_frame_pb2.CaptureVideoFrameRequest: ...
    @property
    def video_convert(self) -> video_frame_pb2.VideoConvertRequest: ...
    @property
    def new_audio_stream(self) -> audio_frame_pb2.NewAudioStreamRequest:
        """Audio"""
    @property
    def new_audio_source(self) -> audio_frame_pb2.NewAudioSourceRequest: ...
    @property
    def capture_audio_frame(self) -> audio_frame_pb2.CaptureAudioFrameRequest: ...
    @property
    def new_audio_resampler(self) -> audio_frame_pb2.NewAudioResamplerRequest: ...
    @property
    def remix_and_resample(self) -> audio_frame_pb2.RemixAndResampleRequest: ...
    @property
    def e2ee(self) -> e2ee_pb2.E2eeRequest: ...
    def __init__(
        self,
        *,
        dispose: global___DisposeRequest | None = ...,
        connect: room_pb2.ConnectRequest | None = ...,
        disconnect: room_pb2.DisconnectRequest | None = ...,
        publish_track: room_pb2.PublishTrackRequest | None = ...,
        unpublish_track: room_pb2.UnpublishTrackRequest | None = ...,
        publish_data: room_pb2.PublishDataRequest | None = ...,
        set_subscribed: room_pb2.SetSubscribedRequest | None = ...,
        update_local_metadata: room_pb2.SetLocalMetadataRequest | None = ...,
        update_local_name: room_pb2.SetLocalNameRequest | None = ...,
        update_local_attributes: room_pb2.SetLocalAttributesRequest | None = ...,
        get_session_stats: room_pb2.GetSessionStatsRequest | None = ...,
        publish_transcription: room_pb2.PublishTranscriptionRequest | None = ...,
        create_video_track: track_pb2.CreateVideoTrackRequest | None = ...,
        create_audio_track: track_pb2.CreateAudioTrackRequest | None = ...,
        get_stats: track_pb2.GetStatsRequest | None = ...,
        new_video_stream: video_frame_pb2.NewVideoStreamRequest | None = ...,
        new_video_source: video_frame_pb2.NewVideoSourceRequest | None = ...,
        capture_video_frame: video_frame_pb2.CaptureVideoFrameRequest | None = ...,
        video_convert: video_frame_pb2.VideoConvertRequest | None = ...,
        new_audio_stream: audio_frame_pb2.NewAudioStreamRequest | None = ...,
        new_audio_source: audio_frame_pb2.NewAudioSourceRequest | None = ...,
        capture_audio_frame: audio_frame_pb2.CaptureAudioFrameRequest | None = ...,
        new_audio_resampler: audio_frame_pb2.NewAudioResamplerRequest | None = ...,
        remix_and_resample: audio_frame_pb2.RemixAndResampleRequest | None = ...,
        e2ee: e2ee_pb2.E2eeRequest | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["capture_audio_frame", b"capture_audio_frame", "capture_video_frame", b"capture_video_frame", "connect", b"connect", "create_audio_track", b"create_audio_track", "create_video_track", b"create_video_track", "disconnect", b"disconnect", "dispose", b"dispose", "e2ee", b"e2ee", "get_session_stats", b"get_session_stats", "get_stats", b"get_stats", "message", b"message", "new_audio_resampler", b"new_audio_resampler", "new_audio_source", b"new_audio_source", "new_audio_stream", b"new_audio_stream", "new_video_source", b"new_video_source", "new_video_stream", b"new_video_stream", "publish_data", b"publish_data", "publish_track", b"publish_track", "publish_transcription", b"publish_transcription", "remix_and_resample", b"remix_and_resample", "set_subscribed", b"set_subscribed", "unpublish_track", b"unpublish_track", "update_local_attributes", b"update_local_attributes", "update_local_metadata", b"update_local_metadata", "update_local_name", b"update_local_name", "video_convert", b"video_convert"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["capture_audio_frame", b"capture_audio_frame", "capture_video_frame", b"capture_video_frame", "connect", b"connect", "create_audio_track", b"create_audio_track", "create_video_track", b"create_video_track", "disconnect", b"disconnect", "dispose", b"dispose", "e2ee", b"e2ee", "get_session_stats", b"get_session_stats", "get_stats", b"get_stats", "message", b"message", "new_audio_resampler", b"new_audio_resampler", "new_audio_source", b"new_audio_source", "new_audio_stream", b"new_audio_stream", "new_video_source", b"new_video_source", "new_video_stream", b"new_video_stream", "publish_data", b"publish_data", "publish_track", b"publish_track", "publish_transcription", b"publish_transcription", "remix_and_resample", b"remix_and_resample", "set_subscribed", b"set_subscribed", "unpublish_track", b"unpublish_track", "update_local_attributes", b"update_local_attributes", "update_local_metadata", b"update_local_metadata", "update_local_name", b"update_local_name", "video_convert", b"video_convert"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["message", b"message"]) -> typing_extensions.Literal["dispose", "connect", "disconnect", "publish_track", "unpublish_track", "publish_data", "set_subscribed", "update_local_metadata", "update_local_name", "update_local_attributes", "get_session_stats", "publish_transcription", "create_video_track", "create_audio_track", "get_stats", "new_video_stream", "new_video_source", "capture_video_frame", "video_convert", "new_audio_stream", "new_audio_source", "capture_audio_frame", "new_audio_resampler", "remix_and_resample", "e2ee"] | None: ...

global___FfiRequest = FfiRequest

@typing_extensions.final
class FfiResponse(google.protobuf.message.Message):
    """This is the output of livekit_ffi_request function."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DISPOSE_FIELD_NUMBER: builtins.int
    CONNECT_FIELD_NUMBER: builtins.int
    DISCONNECT_FIELD_NUMBER: builtins.int
    PUBLISH_TRACK_FIELD_NUMBER: builtins.int
    UNPUBLISH_TRACK_FIELD_NUMBER: builtins.int
    PUBLISH_DATA_FIELD_NUMBER: builtins.int
    SET_SUBSCRIBED_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_METADATA_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_NAME_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_ATTRIBUTES_FIELD_NUMBER: builtins.int
    GET_SESSION_STATS_FIELD_NUMBER: builtins.int
    PUBLISH_TRANSCRIPTION_FIELD_NUMBER: builtins.int
    CREATE_VIDEO_TRACK_FIELD_NUMBER: builtins.int
    CREATE_AUDIO_TRACK_FIELD_NUMBER: builtins.int
    GET_STATS_FIELD_NUMBER: builtins.int
    NEW_VIDEO_STREAM_FIELD_NUMBER: builtins.int
    NEW_VIDEO_SOURCE_FIELD_NUMBER: builtins.int
    CAPTURE_VIDEO_FRAME_FIELD_NUMBER: builtins.int
    VIDEO_CONVERT_FIELD_NUMBER: builtins.int
    NEW_AUDIO_STREAM_FIELD_NUMBER: builtins.int
    NEW_AUDIO_SOURCE_FIELD_NUMBER: builtins.int
    CAPTURE_AUDIO_FRAME_FIELD_NUMBER: builtins.int
    NEW_AUDIO_RESAMPLER_FIELD_NUMBER: builtins.int
    REMIX_AND_RESAMPLE_FIELD_NUMBER: builtins.int
    E2EE_FIELD_NUMBER: builtins.int
    @property
    def dispose(self) -> global___DisposeResponse: ...
    @property
    def connect(self) -> room_pb2.ConnectResponse:
        """Room"""
    @property
    def disconnect(self) -> room_pb2.DisconnectResponse: ...
    @property
    def publish_track(self) -> room_pb2.PublishTrackResponse: ...
    @property
    def unpublish_track(self) -> room_pb2.UnpublishTrackResponse: ...
    @property
    def publish_data(self) -> room_pb2.PublishDataResponse: ...
    @property
    def set_subscribed(self) -> room_pb2.SetSubscribedResponse: ...
    @property
    def update_local_metadata(self) -> room_pb2.SetLocalMetadataResponse: ...
    @property
    def update_local_name(self) -> room_pb2.SetLocalNameResponse: ...
    @property
    def update_local_attributes(self) -> room_pb2.SetLocalAttributesResponse: ...
    @property
    def get_session_stats(self) -> room_pb2.GetSessionStatsResponse: ...
    @property
    def publish_transcription(self) -> room_pb2.PublishTranscriptionResponse: ...
    @property
    def create_video_track(self) -> track_pb2.CreateVideoTrackResponse:
        """Track"""
    @property
    def create_audio_track(self) -> track_pb2.CreateAudioTrackResponse: ...
    @property
    def get_stats(self) -> track_pb2.GetStatsResponse: ...
    @property
    def new_video_stream(self) -> video_frame_pb2.NewVideoStreamResponse:
        """Video"""
    @property
    def new_video_source(self) -> video_frame_pb2.NewVideoSourceResponse: ...
    @property
    def capture_video_frame(self) -> video_frame_pb2.CaptureVideoFrameResponse: ...
    @property
    def video_convert(self) -> video_frame_pb2.VideoConvertResponse: ...
    @property
    def new_audio_stream(self) -> audio_frame_pb2.NewAudioStreamResponse:
        """Audio"""
    @property
    def new_audio_source(self) -> audio_frame_pb2.NewAudioSourceResponse: ...
    @property
    def capture_audio_frame(self) -> audio_frame_pb2.CaptureAudioFrameResponse: ...
    @property
    def new_audio_resampler(self) -> audio_frame_pb2.NewAudioResamplerResponse: ...
    @property
    def remix_and_resample(self) -> audio_frame_pb2.RemixAndResampleResponse: ...
    @property
    def e2ee(self) -> e2ee_pb2.E2eeResponse: ...
    def __init__(
        self,
        *,
        dispose: global___DisposeResponse | None = ...,
        connect: room_pb2.ConnectResponse | None = ...,
        disconnect: room_pb2.DisconnectResponse | None = ...,
        publish_track: room_pb2.PublishTrackResponse | None = ...,
        unpublish_track: room_pb2.UnpublishTrackResponse | None = ...,
        publish_data: room_pb2.PublishDataResponse | None = ...,
        set_subscribed: room_pb2.SetSubscribedResponse | None = ...,
        update_local_metadata: room_pb2.SetLocalMetadataResponse | None = ...,
        update_local_name: room_pb2.SetLocalNameResponse | None = ...,
        update_local_attributes: room_pb2.SetLocalAttributesResponse | None = ...,
        get_session_stats: room_pb2.GetSessionStatsResponse | None = ...,
        publish_transcription: room_pb2.PublishTranscriptionResponse | None = ...,
        create_video_track: track_pb2.CreateVideoTrackResponse | None = ...,
        create_audio_track: track_pb2.CreateAudioTrackResponse | None = ...,
        get_stats: track_pb2.GetStatsResponse | None = ...,
        new_video_stream: video_frame_pb2.NewVideoStreamResponse | None = ...,
        new_video_source: video_frame_pb2.NewVideoSourceResponse | None = ...,
        capture_video_frame: video_frame_pb2.CaptureVideoFrameResponse | None = ...,
        video_convert: video_frame_pb2.VideoConvertResponse | None = ...,
        new_audio_stream: audio_frame_pb2.NewAudioStreamResponse | None = ...,
        new_audio_source: audio_frame_pb2.NewAudioSourceResponse | None = ...,
        capture_audio_frame: audio_frame_pb2.CaptureAudioFrameResponse | None = ...,
        new_audio_resampler: audio_frame_pb2.NewAudioResamplerResponse | None = ...,
        remix_and_resample: audio_frame_pb2.RemixAndResampleResponse | None = ...,
        e2ee: e2ee_pb2.E2eeResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["capture_audio_frame", b"capture_audio_frame", "capture_video_frame", b"capture_video_frame", "connect", b"connect", "create_audio_track", b"create_audio_track", "create_video_track", b"create_video_track", "disconnect", b"disconnect", "dispose", b"dispose", "e2ee", b"e2ee", "get_session_stats", b"get_session_stats", "get_stats", b"get_stats", "message", b"message", "new_audio_resampler", b"new_audio_resampler", "new_audio_source", b"new_audio_source", "new_audio_stream", b"new_audio_stream", "new_video_source", b"new_video_source", "new_video_stream", b"new_video_stream", "publish_data", b"publish_data", "publish_track", b"publish_track", "publish_transcription", b"publish_transcription", "remix_and_resample", b"remix_and_resample", "set_subscribed", b"set_subscribed", "unpublish_track", b"unpublish_track", "update_local_attributes", b"update_local_attributes", "update_local_metadata", b"update_local_metadata", "update_local_name", b"update_local_name", "video_convert", b"video_convert"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["capture_audio_frame", b"capture_audio_frame", "capture_video_frame", b"capture_video_frame", "connect", b"connect", "create_audio_track", b"create_audio_track", "create_video_track", b"create_video_track", "disconnect", b"disconnect", "dispose", b"dispose", "e2ee", b"e2ee", "get_session_stats", b"get_session_stats", "get_stats", b"get_stats", "message", b"message", "new_audio_resampler", b"new_audio_resampler", "new_audio_source", b"new_audio_source", "new_audio_stream", b"new_audio_stream", "new_video_source", b"new_video_source", "new_video_stream", b"new_video_stream", "publish_data", b"publish_data", "publish_track", b"publish_track", "publish_transcription", b"publish_transcription", "remix_and_resample", b"remix_and_resample", "set_subscribed", b"set_subscribed", "unpublish_track", b"unpublish_track", "update_local_attributes", b"update_local_attributes", "update_local_metadata", b"update_local_metadata", "update_local_name", b"update_local_name", "video_convert", b"video_convert"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["message", b"message"]) -> typing_extensions.Literal["dispose", "connect", "disconnect", "publish_track", "unpublish_track", "publish_data", "set_subscribed", "update_local_metadata", "update_local_name", "update_local_attributes", "get_session_stats", "publish_transcription", "create_video_track", "create_audio_track", "get_stats", "new_video_stream", "new_video_source", "capture_video_frame", "video_convert", "new_audio_stream", "new_audio_source", "capture_audio_frame", "new_audio_resampler", "remix_and_resample", "e2ee"] | None: ...

global___FfiResponse = FfiResponse

@typing_extensions.final
class FfiEvent(google.protobuf.message.Message):
    """To minimize complexity, participant events are not included in the protocol.
    It is easily deducible from the room events and it turned out that is is easier to implement
    on the ffi client side.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ROOM_EVENT_FIELD_NUMBER: builtins.int
    TRACK_EVENT_FIELD_NUMBER: builtins.int
    VIDEO_STREAM_EVENT_FIELD_NUMBER: builtins.int
    AUDIO_STREAM_EVENT_FIELD_NUMBER: builtins.int
    CONNECT_FIELD_NUMBER: builtins.int
    DISCONNECT_FIELD_NUMBER: builtins.int
    DISPOSE_FIELD_NUMBER: builtins.int
    PUBLISH_TRACK_FIELD_NUMBER: builtins.int
    UNPUBLISH_TRACK_FIELD_NUMBER: builtins.int
    PUBLISH_DATA_FIELD_NUMBER: builtins.int
    PUBLISH_TRANSCRIPTION_FIELD_NUMBER: builtins.int
    CAPTURE_AUDIO_FRAME_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_METADATA_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_NAME_FIELD_NUMBER: builtins.int
    UPDATE_LOCAL_ATTRIBUTES_FIELD_NUMBER: builtins.int
    GET_STATS_FIELD_NUMBER: builtins.int
    LOGS_FIELD_NUMBER: builtins.int
    GET_SESSION_STATS_FIELD_NUMBER: builtins.int
    PANIC_FIELD_NUMBER: builtins.int
    @property
    def room_event(self) -> room_pb2.RoomEvent: ...
    @property
    def track_event(self) -> track_pb2.TrackEvent: ...
    @property
    def video_stream_event(self) -> video_frame_pb2.VideoStreamEvent: ...
    @property
    def audio_stream_event(self) -> audio_frame_pb2.AudioStreamEvent: ...
    @property
    def connect(self) -> room_pb2.ConnectCallback: ...
    @property
    def disconnect(self) -> room_pb2.DisconnectCallback: ...
    @property
    def dispose(self) -> global___DisposeCallback: ...
    @property
    def publish_track(self) -> room_pb2.PublishTrackCallback: ...
    @property
    def unpublish_track(self) -> room_pb2.UnpublishTrackCallback: ...
    @property
    def publish_data(self) -> room_pb2.PublishDataCallback: ...
    @property
    def publish_transcription(self) -> room_pb2.PublishTranscriptionCallback: ...
    @property
    def capture_audio_frame(self) -> audio_frame_pb2.CaptureAudioFrameCallback: ...
    @property
    def update_local_metadata(self) -> room_pb2.SetLocalMetadataCallback: ...
    @property
    def update_local_name(self) -> room_pb2.SetLocalNameCallback: ...
    @property
    def update_local_attributes(self) -> room_pb2.SetLocalAttributesCallback: ...
    @property
    def get_stats(self) -> track_pb2.GetStatsCallback: ...
    @property
    def logs(self) -> global___LogBatch: ...
    @property
    def get_session_stats(self) -> room_pb2.GetSessionStatsCallback: ...
    @property
    def panic(self) -> global___Panic: ...
    def __init__(
        self,
        *,
        room_event: room_pb2.RoomEvent | None = ...,
        track_event: track_pb2.TrackEvent | None = ...,
        video_stream_event: video_frame_pb2.VideoStreamEvent | None = ...,
        audio_stream_event: audio_frame_pb2.AudioStreamEvent | None = ...,
        connect: room_pb2.ConnectCallback | None = ...,
        disconnect: room_pb2.DisconnectCallback | None = ...,
        dispose: global___DisposeCallback | None = ...,
        publish_track: room_pb2.PublishTrackCallback | None = ...,
        unpublish_track: room_pb2.UnpublishTrackCallback | None = ...,
        publish_data: room_pb2.PublishDataCallback | None = ...,
        publish_transcription: room_pb2.PublishTranscriptionCallback | None = ...,
        capture_audio_frame: audio_frame_pb2.CaptureAudioFrameCallback | None = ...,
        update_local_metadata: room_pb2.SetLocalMetadataCallback | None = ...,
        update_local_name: room_pb2.SetLocalNameCallback | None = ...,
        update_local_attributes: room_pb2.SetLocalAttributesCallback | None = ...,
        get_stats: track_pb2.GetStatsCallback | None = ...,
        logs: global___LogBatch | None = ...,
        get_session_stats: room_pb2.GetSessionStatsCallback | None = ...,
        panic: global___Panic | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["audio_stream_event", b"audio_stream_event", "capture_audio_frame", b"capture_audio_frame", "connect", b"connect", "disconnect", b"disconnect", "dispose", b"dispose", "get_session_stats", b"get_session_stats", "get_stats", b"get_stats", "logs", b"logs", "message", b"message", "panic", b"panic", "publish_data", b"publish_data", "publish_track", b"publish_track", "publish_transcription", b"publish_transcription", "room_event", b"room_event", "track_event", b"track_event", "unpublish_track", b"unpublish_track", "update_local_attributes", b"update_local_attributes", "update_local_metadata", b"update_local_metadata", "update_local_name", b"update_local_name", "video_stream_event", b"video_stream_event"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["audio_stream_event", b"audio_stream_event", "capture_audio_frame", b"capture_audio_frame", "connect", b"connect", "disconnect", b"disconnect", "dispose", b"dispose", "get_session_stats", b"get_session_stats", "get_stats", b"get_stats", "logs", b"logs", "message", b"message", "panic", b"panic", "publish_data", b"publish_data", "publish_track", b"publish_track", "publish_transcription", b"publish_transcription", "room_event", b"room_event", "track_event", b"track_event", "unpublish_track", b"unpublish_track", "update_local_attributes", b"update_local_attributes", "update_local_metadata", b"update_local_metadata", "update_local_name", b"update_local_name", "video_stream_event", b"video_stream_event"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["message", b"message"]) -> typing_extensions.Literal["room_event", "track_event", "video_stream_event", "audio_stream_event", "connect", "disconnect", "dispose", "publish_track", "unpublish_track", "publish_data", "publish_transcription", "capture_audio_frame", "update_local_metadata", "update_local_name", "update_local_attributes", "get_stats", "logs", "get_session_stats", "panic"] | None: ...

global___FfiEvent = FfiEvent

@typing_extensions.final
class DisposeRequest(google.protobuf.message.Message):
    """Stop all rooms synchronously (Do we need async here?).
    e.g: This is used for the Unity Editor after each assemblies reload.
    TODO(theomonnom): Implement a debug mode where we can find all leaked handles?
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ASYNC_FIELD_NUMBER: builtins.int
    def __init__(
        self,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["async", b"async"]) -> None: ...

global___DisposeRequest = DisposeRequest

@typing_extensions.final
class DisposeResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ASYNC_ID_FIELD_NUMBER: builtins.int
    async_id: builtins.int
    """None if sync"""
    def __init__(
        self,
        *,
        async_id: builtins.int | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_async_id", b"_async_id", "async_id", b"async_id"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_async_id", b"_async_id", "async_id", b"async_id"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_async_id", b"_async_id"]) -> typing_extensions.Literal["async_id"] | None: ...

global___DisposeResponse = DisposeResponse

@typing_extensions.final
class DisposeCallback(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ASYNC_ID_FIELD_NUMBER: builtins.int
    async_id: builtins.int
    def __init__(
        self,
        *,
        async_id: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["async_id", b"async_id"]) -> None: ...

global___DisposeCallback = DisposeCallback

@typing_extensions.final
class LogRecord(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    LEVEL_FIELD_NUMBER: builtins.int
    TARGET_FIELD_NUMBER: builtins.int
    MODULE_PATH_FIELD_NUMBER: builtins.int
    FILE_FIELD_NUMBER: builtins.int
    LINE_FIELD_NUMBER: builtins.int
    MESSAGE_FIELD_NUMBER: builtins.int
    level: global___LogLevel.ValueType
    target: builtins.str
    """e.g "livekit", "libwebrtc", "tokio-tungstenite", etc..."""
    module_path: builtins.str
    file: builtins.str
    line: builtins.int
    message: builtins.str
    def __init__(
        self,
        *,
        level: global___LogLevel.ValueType = ...,
        target: builtins.str = ...,
        module_path: builtins.str | None = ...,
        file: builtins.str | None = ...,
        line: builtins.int | None = ...,
        message: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_file", b"_file", "_line", b"_line", "_module_path", b"_module_path", "file", b"file", "line", b"line", "module_path", b"module_path"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_file", b"_file", "_line", b"_line", "_module_path", b"_module_path", "file", b"file", "level", b"level", "line", b"line", "message", b"message", "module_path", b"module_path", "target", b"target"]) -> None: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_file", b"_file"]) -> typing_extensions.Literal["file"] | None: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_line", b"_line"]) -> typing_extensions.Literal["line"] | None: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_module_path", b"_module_path"]) -> typing_extensions.Literal["module_path"] | None: ...

global___LogRecord = LogRecord

@typing_extensions.final
class LogBatch(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    RECORDS_FIELD_NUMBER: builtins.int
    @property
    def records(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___LogRecord]: ...
    def __init__(
        self,
        *,
        records: collections.abc.Iterable[global___LogRecord] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["records", b"records"]) -> None: ...

global___LogBatch = LogBatch

@typing_extensions.final
class Panic(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MESSAGE_FIELD_NUMBER: builtins.int
    message: builtins.str
    def __init__(
        self,
        *,
        message: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["message", b"message"]) -> None: ...

global___Panic = Panic
