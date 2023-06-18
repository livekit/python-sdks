import handle_pb2 as _handle_pb2
import track_pb2 as _track_pb2
import room_pb2 as _room_pb2
import participant_pb2 as _participant_pb2
import video_frame_pb2 as _video_frame_pb2
import audio_frame_pb2 as _audio_frame_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FfiRequest(_message.Message):
    __slots__ = ["initialize", "dispose", "connect", "disconnect", "publish_track", "unpublish_track", "publish_data", "create_video_track", "create_audio_track", "alloc_video_buffer", "new_video_stream", "new_video_source", "capture_video_frame", "to_i420", "to_argb", "alloc_audio_buffer", "new_audio_stream", "new_audio_source", "capture_audio_frame", "new_audio_resampler", "remix_and_resample"]
    INITIALIZE_FIELD_NUMBER: _ClassVar[int]
    DISPOSE_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    UNPUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_DATA_FIELD_NUMBER: _ClassVar[int]
    CREATE_VIDEO_TRACK_FIELD_NUMBER: _ClassVar[int]
    CREATE_AUDIO_TRACK_FIELD_NUMBER: _ClassVar[int]
    ALLOC_VIDEO_BUFFER_FIELD_NUMBER: _ClassVar[int]
    NEW_VIDEO_STREAM_FIELD_NUMBER: _ClassVar[int]
    NEW_VIDEO_SOURCE_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_VIDEO_FRAME_FIELD_NUMBER: _ClassVar[int]
    TO_I420_FIELD_NUMBER: _ClassVar[int]
    TO_ARGB_FIELD_NUMBER: _ClassVar[int]
    ALLOC_AUDIO_BUFFER_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_STREAM_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_SOURCE_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_AUDIO_FRAME_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_RESAMPLER_FIELD_NUMBER: _ClassVar[int]
    REMIX_AND_RESAMPLE_FIELD_NUMBER: _ClassVar[int]
    initialize: InitializeRequest
    dispose: DisposeRequest
    connect: _room_pb2.ConnectRequest
    disconnect: _room_pb2.DisconnectRequest
    publish_track: _room_pb2.PublishTrackRequest
    unpublish_track: _room_pb2.UnpublishTrackRequest
    publish_data: _room_pb2.PublishDataRequest
    create_video_track: _track_pb2.CreateVideoTrackRequest
    create_audio_track: _track_pb2.CreateAudioTrackRequest
    alloc_video_buffer: _video_frame_pb2.AllocVideoBufferRequest
    new_video_stream: _video_frame_pb2.NewVideoStreamRequest
    new_video_source: _video_frame_pb2.NewVideoSourceRequest
    capture_video_frame: _video_frame_pb2.CaptureVideoFrameRequest
    to_i420: _video_frame_pb2.ToI420Request
    to_argb: _video_frame_pb2.ToArgbRequest
    alloc_audio_buffer: _audio_frame_pb2.AllocAudioBufferRequest
    new_audio_stream: _audio_frame_pb2.NewAudioStreamRequest
    new_audio_source: _audio_frame_pb2.NewAudioSourceRequest
    capture_audio_frame: _audio_frame_pb2.CaptureAudioFrameRequest
    new_audio_resampler: _audio_frame_pb2.NewAudioResamplerRequest
    remix_and_resample: _audio_frame_pb2.RemixAndResampleRequest
    def __init__(self, initialize: _Optional[_Union[InitializeRequest, _Mapping]] = ..., dispose: _Optional[_Union[DisposeRequest, _Mapping]] = ..., connect: _Optional[_Union[_room_pb2.ConnectRequest, _Mapping]] = ..., disconnect: _Optional[_Union[_room_pb2.DisconnectRequest, _Mapping]] = ..., publish_track: _Optional[_Union[_room_pb2.PublishTrackRequest, _Mapping]] = ..., unpublish_track: _Optional[_Union[_room_pb2.UnpublishTrackRequest, _Mapping]] = ..., publish_data: _Optional[_Union[_room_pb2.PublishDataRequest, _Mapping]] = ..., create_video_track: _Optional[_Union[_track_pb2.CreateVideoTrackRequest, _Mapping]] = ..., create_audio_track: _Optional[_Union[_track_pb2.CreateAudioTrackRequest, _Mapping]] = ..., alloc_video_buffer: _Optional[_Union[_video_frame_pb2.AllocVideoBufferRequest, _Mapping]] = ..., new_video_stream: _Optional[_Union[_video_frame_pb2.NewVideoStreamRequest, _Mapping]] = ..., new_video_source: _Optional[_Union[_video_frame_pb2.NewVideoSourceRequest, _Mapping]] = ..., capture_video_frame: _Optional[_Union[_video_frame_pb2.CaptureVideoFrameRequest, _Mapping]] = ..., to_i420: _Optional[_Union[_video_frame_pb2.ToI420Request, _Mapping]] = ..., to_argb: _Optional[_Union[_video_frame_pb2.ToArgbRequest, _Mapping]] = ..., alloc_audio_buffer: _Optional[_Union[_audio_frame_pb2.AllocAudioBufferRequest, _Mapping]] = ..., new_audio_stream: _Optional[_Union[_audio_frame_pb2.NewAudioStreamRequest, _Mapping]] = ..., new_audio_source: _Optional[_Union[_audio_frame_pb2.NewAudioSourceRequest, _Mapping]] = ..., capture_audio_frame: _Optional[_Union[_audio_frame_pb2.CaptureAudioFrameRequest, _Mapping]] = ..., new_audio_resampler: _Optional[_Union[_audio_frame_pb2.NewAudioResamplerRequest, _Mapping]] = ..., remix_and_resample: _Optional[_Union[_audio_frame_pb2.RemixAndResampleRequest, _Mapping]] = ...) -> None: ...

class FfiResponse(_message.Message):
    __slots__ = ["initialize", "dispose", "connect", "disconnect", "publish_track", "unpublish_track", "publish_data", "create_video_track", "create_audio_track", "alloc_video_buffer", "new_video_stream", "new_video_source", "capture_video_frame", "to_i420", "to_argb", "alloc_audio_buffer", "new_audio_stream", "new_audio_source", "capture_audio_frame", "new_audio_resampler", "remix_and_resample"]
    INITIALIZE_FIELD_NUMBER: _ClassVar[int]
    DISPOSE_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    UNPUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_DATA_FIELD_NUMBER: _ClassVar[int]
    CREATE_VIDEO_TRACK_FIELD_NUMBER: _ClassVar[int]
    CREATE_AUDIO_TRACK_FIELD_NUMBER: _ClassVar[int]
    ALLOC_VIDEO_BUFFER_FIELD_NUMBER: _ClassVar[int]
    NEW_VIDEO_STREAM_FIELD_NUMBER: _ClassVar[int]
    NEW_VIDEO_SOURCE_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_VIDEO_FRAME_FIELD_NUMBER: _ClassVar[int]
    TO_I420_FIELD_NUMBER: _ClassVar[int]
    TO_ARGB_FIELD_NUMBER: _ClassVar[int]
    ALLOC_AUDIO_BUFFER_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_STREAM_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_SOURCE_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_AUDIO_FRAME_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_RESAMPLER_FIELD_NUMBER: _ClassVar[int]
    REMIX_AND_RESAMPLE_FIELD_NUMBER: _ClassVar[int]
    initialize: InitializeResponse
    dispose: DisposeResponse
    connect: _room_pb2.ConnectResponse
    disconnect: _room_pb2.DisconnectResponse
    publish_track: _room_pb2.PublishTrackResponse
    unpublish_track: _room_pb2.UnpublishTrackResponse
    publish_data: _room_pb2.PublishDataResponse
    create_video_track: _track_pb2.CreateVideoTrackResponse
    create_audio_track: _track_pb2.CreateAudioTrackResponse
    alloc_video_buffer: _video_frame_pb2.AllocVideoBufferResponse
    new_video_stream: _video_frame_pb2.NewVideoStreamResponse
    new_video_source: _video_frame_pb2.NewVideoSourceResponse
    capture_video_frame: _video_frame_pb2.CaptureVideoFrameResponse
    to_i420: _video_frame_pb2.ToI420Response
    to_argb: _video_frame_pb2.ToArgbResponse
    alloc_audio_buffer: _audio_frame_pb2.AllocAudioBufferResponse
    new_audio_stream: _audio_frame_pb2.NewAudioStreamResponse
    new_audio_source: _audio_frame_pb2.NewAudioSourceResponse
    capture_audio_frame: _audio_frame_pb2.CaptureAudioFrameResponse
    new_audio_resampler: _audio_frame_pb2.NewAudioResamplerResponse
    remix_and_resample: _audio_frame_pb2.RemixAndResampleResponse
    def __init__(self, initialize: _Optional[_Union[InitializeResponse, _Mapping]] = ..., dispose: _Optional[_Union[DisposeResponse, _Mapping]] = ..., connect: _Optional[_Union[_room_pb2.ConnectResponse, _Mapping]] = ..., disconnect: _Optional[_Union[_room_pb2.DisconnectResponse, _Mapping]] = ..., publish_track: _Optional[_Union[_room_pb2.PublishTrackResponse, _Mapping]] = ..., unpublish_track: _Optional[_Union[_room_pb2.UnpublishTrackResponse, _Mapping]] = ..., publish_data: _Optional[_Union[_room_pb2.PublishDataResponse, _Mapping]] = ..., create_video_track: _Optional[_Union[_track_pb2.CreateVideoTrackResponse, _Mapping]] = ..., create_audio_track: _Optional[_Union[_track_pb2.CreateAudioTrackResponse, _Mapping]] = ..., alloc_video_buffer: _Optional[_Union[_video_frame_pb2.AllocVideoBufferResponse, _Mapping]] = ..., new_video_stream: _Optional[_Union[_video_frame_pb2.NewVideoStreamResponse, _Mapping]] = ..., new_video_source: _Optional[_Union[_video_frame_pb2.NewVideoSourceResponse, _Mapping]] = ..., capture_video_frame: _Optional[_Union[_video_frame_pb2.CaptureVideoFrameResponse, _Mapping]] = ..., to_i420: _Optional[_Union[_video_frame_pb2.ToI420Response, _Mapping]] = ..., to_argb: _Optional[_Union[_video_frame_pb2.ToArgbResponse, _Mapping]] = ..., alloc_audio_buffer: _Optional[_Union[_audio_frame_pb2.AllocAudioBufferResponse, _Mapping]] = ..., new_audio_stream: _Optional[_Union[_audio_frame_pb2.NewAudioStreamResponse, _Mapping]] = ..., new_audio_source: _Optional[_Union[_audio_frame_pb2.NewAudioSourceResponse, _Mapping]] = ..., capture_audio_frame: _Optional[_Union[_audio_frame_pb2.CaptureAudioFrameResponse, _Mapping]] = ..., new_audio_resampler: _Optional[_Union[_audio_frame_pb2.NewAudioResamplerResponse, _Mapping]] = ..., remix_and_resample: _Optional[_Union[_audio_frame_pb2.RemixAndResampleResponse, _Mapping]] = ...) -> None: ...

class FfiEvent(_message.Message):
    __slots__ = ["room_event", "track_event", "participant_event", "video_stream_event", "audio_stream_event", "connect", "disconnect", "dispose", "publish_track", "publish_data"]
    ROOM_EVENT_FIELD_NUMBER: _ClassVar[int]
    TRACK_EVENT_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_EVENT_FIELD_NUMBER: _ClassVar[int]
    VIDEO_STREAM_EVENT_FIELD_NUMBER: _ClassVar[int]
    AUDIO_STREAM_EVENT_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_FIELD_NUMBER: _ClassVar[int]
    DISPOSE_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_DATA_FIELD_NUMBER: _ClassVar[int]
    room_event: _room_pb2.RoomEvent
    track_event: _track_pb2.TrackEvent
    participant_event: _participant_pb2.ParticipantEvent
    video_stream_event: _video_frame_pb2.VideoStreamEvent
    audio_stream_event: _audio_frame_pb2.AudioStreamEvent
    connect: _room_pb2.ConnectCallback
    disconnect: _room_pb2.DisconnectCallback
    dispose: DisposeCallback
    publish_track: _room_pb2.PublishTrackCallback
    publish_data: _room_pb2.PublishDataCallback
    def __init__(self, room_event: _Optional[_Union[_room_pb2.RoomEvent, _Mapping]] = ..., track_event: _Optional[_Union[_track_pb2.TrackEvent, _Mapping]] = ..., participant_event: _Optional[_Union[_participant_pb2.ParticipantEvent, _Mapping]] = ..., video_stream_event: _Optional[_Union[_video_frame_pb2.VideoStreamEvent, _Mapping]] = ..., audio_stream_event: _Optional[_Union[_audio_frame_pb2.AudioStreamEvent, _Mapping]] = ..., connect: _Optional[_Union[_room_pb2.ConnectCallback, _Mapping]] = ..., disconnect: _Optional[_Union[_room_pb2.DisconnectCallback, _Mapping]] = ..., dispose: _Optional[_Union[DisposeCallback, _Mapping]] = ..., publish_track: _Optional[_Union[_room_pb2.PublishTrackCallback, _Mapping]] = ..., publish_data: _Optional[_Union[_room_pb2.PublishDataCallback, _Mapping]] = ...) -> None: ...

class InitializeRequest(_message.Message):
    __slots__ = ["event_callback_ptr"]
    EVENT_CALLBACK_PTR_FIELD_NUMBER: _ClassVar[int]
    event_callback_ptr: int
    def __init__(self, event_callback_ptr: _Optional[int] = ...) -> None: ...

class InitializeResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class DisposeRequest(_message.Message):
    __slots__ = []
    ASYNC_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...

class DisposeResponse(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ...) -> None: ...

class DisposeCallback(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FfiAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FfiAsyncId, _Mapping]] = ...) -> None: ...
