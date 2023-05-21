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

class DisposeCallback(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FFIAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FFIAsyncId, _Mapping]] = ...) -> None: ...

class DisposeRequest(_message.Message):
    __slots__ = []
    ASYNC_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...

class DisposeResponse(_message.Message):
    __slots__ = ["async_id"]
    ASYNC_ID_FIELD_NUMBER: _ClassVar[int]
    async_id: _handle_pb2.FFIAsyncId
    def __init__(self, async_id: _Optional[_Union[_handle_pb2.FFIAsyncId, _Mapping]] = ...) -> None: ...

class FFIEvent(_message.Message):
    __slots__ = ["audio_stream_event", "connect", "dispose", "participant_event", "publish_track", "room_event", "track_event", "video_stream_event"]
    AUDIO_STREAM_EVENT_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    DISPOSE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_EVENT_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    ROOM_EVENT_FIELD_NUMBER: _ClassVar[int]
    TRACK_EVENT_FIELD_NUMBER: _ClassVar[int]
    VIDEO_STREAM_EVENT_FIELD_NUMBER: _ClassVar[int]
    audio_stream_event: _audio_frame_pb2.AudioStreamEvent
    connect: _room_pb2.ConnectCallback
    dispose: DisposeCallback
    participant_event: _participant_pb2.ParticipantEvent
    publish_track: _room_pb2.PublishTrackCallback
    room_event: _room_pb2.RoomEvent
    track_event: _track_pb2.TrackEvent
    video_stream_event: _video_frame_pb2.VideoStreamEvent
    def __init__(self, room_event: _Optional[_Union[_room_pb2.RoomEvent, _Mapping]] = ..., track_event: _Optional[_Union[_track_pb2.TrackEvent, _Mapping]] = ..., participant_event: _Optional[_Union[_participant_pb2.ParticipantEvent, _Mapping]] = ..., video_stream_event: _Optional[_Union[_video_frame_pb2.VideoStreamEvent, _Mapping]] = ..., audio_stream_event: _Optional[_Union[_audio_frame_pb2.AudioStreamEvent, _Mapping]] = ..., connect: _Optional[_Union[_room_pb2.ConnectCallback, _Mapping]] = ..., dispose: _Optional[_Union[DisposeCallback, _Mapping]] = ..., publish_track: _Optional[_Union[_room_pb2.PublishTrackCallback, _Mapping]] = ...) -> None: ...

class FFIRequest(_message.Message):
    __slots__ = ["alloc_audio_buffer", "alloc_video_buffer", "capture_audio_frame", "capture_video_frame", "connect", "create_audio_track", "create_video_track", "disconnect", "dispose", "initialize", "new_audio_resampler", "new_audio_source", "new_audio_stream", "new_video_source", "new_video_stream", "publish_track", "remix_and_resample", "to_argb", "to_i420", "unpublish_track"]
    ALLOC_AUDIO_BUFFER_FIELD_NUMBER: _ClassVar[int]
    ALLOC_VIDEO_BUFFER_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_AUDIO_FRAME_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_VIDEO_FRAME_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    CREATE_AUDIO_TRACK_FIELD_NUMBER: _ClassVar[int]
    CREATE_VIDEO_TRACK_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_FIELD_NUMBER: _ClassVar[int]
    DISPOSE_FIELD_NUMBER: _ClassVar[int]
    INITIALIZE_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_RESAMPLER_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_SOURCE_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_STREAM_FIELD_NUMBER: _ClassVar[int]
    NEW_VIDEO_SOURCE_FIELD_NUMBER: _ClassVar[int]
    NEW_VIDEO_STREAM_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    REMIX_AND_RESAMPLE_FIELD_NUMBER: _ClassVar[int]
    TO_ARGB_FIELD_NUMBER: _ClassVar[int]
    TO_I420_FIELD_NUMBER: _ClassVar[int]
    UNPUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    alloc_audio_buffer: _audio_frame_pb2.AllocAudioBufferRequest
    alloc_video_buffer: _video_frame_pb2.AllocVideoBufferRequest
    capture_audio_frame: _audio_frame_pb2.CaptureAudioFrameRequest
    capture_video_frame: _video_frame_pb2.CaptureVideoFrameRequest
    connect: _room_pb2.ConnectRequest
    create_audio_track: _track_pb2.CreateAudioTrackRequest
    create_video_track: _track_pb2.CreateVideoTrackRequest
    disconnect: _room_pb2.DisconnectRequest
    dispose: DisposeRequest
    initialize: InitializeRequest
    new_audio_resampler: _audio_frame_pb2.NewAudioResamplerRequest
    new_audio_source: _audio_frame_pb2.NewAudioSourceRequest
    new_audio_stream: _audio_frame_pb2.NewAudioStreamRequest
    new_video_source: _video_frame_pb2.NewVideoSourceRequest
    new_video_stream: _video_frame_pb2.NewVideoStreamRequest
    publish_track: _room_pb2.PublishTrackRequest
    remix_and_resample: _audio_frame_pb2.RemixAndResampleRequest
    to_argb: _video_frame_pb2.ToARGBRequest
    to_i420: _video_frame_pb2.ToI420Request
    unpublish_track: _room_pb2.UnpublishTrackRequest
    def __init__(self, initialize: _Optional[_Union[InitializeRequest, _Mapping]] = ..., dispose: _Optional[_Union[DisposeRequest, _Mapping]] = ..., connect: _Optional[_Union[_room_pb2.ConnectRequest, _Mapping]] = ..., disconnect: _Optional[_Union[_room_pb2.DisconnectRequest, _Mapping]] = ..., publish_track: _Optional[_Union[_room_pb2.PublishTrackRequest, _Mapping]] = ..., unpublish_track: _Optional[_Union[_room_pb2.UnpublishTrackRequest, _Mapping]] = ..., create_video_track: _Optional[_Union[_track_pb2.CreateVideoTrackRequest, _Mapping]] = ..., create_audio_track: _Optional[_Union[_track_pb2.CreateAudioTrackRequest, _Mapping]] = ..., alloc_video_buffer: _Optional[_Union[_video_frame_pb2.AllocVideoBufferRequest, _Mapping]] = ..., new_video_stream: _Optional[_Union[_video_frame_pb2.NewVideoStreamRequest, _Mapping]] = ..., new_video_source: _Optional[_Union[_video_frame_pb2.NewVideoSourceRequest, _Mapping]] = ..., capture_video_frame: _Optional[_Union[_video_frame_pb2.CaptureVideoFrameRequest, _Mapping]] = ..., to_i420: _Optional[_Union[_video_frame_pb2.ToI420Request, _Mapping]] = ..., to_argb: _Optional[_Union[_video_frame_pb2.ToARGBRequest, _Mapping]] = ..., alloc_audio_buffer: _Optional[_Union[_audio_frame_pb2.AllocAudioBufferRequest, _Mapping]] = ..., new_audio_stream: _Optional[_Union[_audio_frame_pb2.NewAudioStreamRequest, _Mapping]] = ..., new_audio_source: _Optional[_Union[_audio_frame_pb2.NewAudioSourceRequest, _Mapping]] = ..., capture_audio_frame: _Optional[_Union[_audio_frame_pb2.CaptureAudioFrameRequest, _Mapping]] = ..., new_audio_resampler: _Optional[_Union[_audio_frame_pb2.NewAudioResamplerRequest, _Mapping]] = ..., remix_and_resample: _Optional[_Union[_audio_frame_pb2.RemixAndResampleRequest, _Mapping]] = ...) -> None: ...

class FFIResponse(_message.Message):
    __slots__ = ["alloc_audio_buffer", "alloc_video_buffer", "capture_audio_frame", "capture_video_frame", "connect", "create_audio_track", "create_video_track", "disconnect", "dispose", "initialize", "new_audio_resampler", "new_audio_source", "new_audio_stream", "new_video_source", "new_video_stream", "publish_track", "remix_and_resample", "to_argb", "to_i420", "unpublish_track"]
    ALLOC_AUDIO_BUFFER_FIELD_NUMBER: _ClassVar[int]
    ALLOC_VIDEO_BUFFER_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_AUDIO_FRAME_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_VIDEO_FRAME_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    CREATE_AUDIO_TRACK_FIELD_NUMBER: _ClassVar[int]
    CREATE_VIDEO_TRACK_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_FIELD_NUMBER: _ClassVar[int]
    DISPOSE_FIELD_NUMBER: _ClassVar[int]
    INITIALIZE_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_RESAMPLER_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_SOURCE_FIELD_NUMBER: _ClassVar[int]
    NEW_AUDIO_STREAM_FIELD_NUMBER: _ClassVar[int]
    NEW_VIDEO_SOURCE_FIELD_NUMBER: _ClassVar[int]
    NEW_VIDEO_STREAM_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    REMIX_AND_RESAMPLE_FIELD_NUMBER: _ClassVar[int]
    TO_ARGB_FIELD_NUMBER: _ClassVar[int]
    TO_I420_FIELD_NUMBER: _ClassVar[int]
    UNPUBLISH_TRACK_FIELD_NUMBER: _ClassVar[int]
    alloc_audio_buffer: _audio_frame_pb2.AllocAudioBufferResponse
    alloc_video_buffer: _video_frame_pb2.AllocVideoBufferResponse
    capture_audio_frame: _audio_frame_pb2.CaptureAudioFrameResponse
    capture_video_frame: _video_frame_pb2.CaptureVideoFrameResponse
    connect: _room_pb2.ConnectResponse
    create_audio_track: _track_pb2.CreateAudioTrackResponse
    create_video_track: _track_pb2.CreateVideoTrackResponse
    disconnect: _room_pb2.DisconnectResponse
    dispose: DisposeResponse
    initialize: InitializeResponse
    new_audio_resampler: _audio_frame_pb2.NewAudioResamplerResponse
    new_audio_source: _audio_frame_pb2.NewAudioSourceResponse
    new_audio_stream: _audio_frame_pb2.NewAudioStreamResponse
    new_video_source: _video_frame_pb2.NewVideoSourceResponse
    new_video_stream: _video_frame_pb2.NewVideoStreamResponse
    publish_track: _room_pb2.PublishTrackResponse
    remix_and_resample: _audio_frame_pb2.RemixAndResampleResponse
    to_argb: _video_frame_pb2.ToARGBResponse
    to_i420: _video_frame_pb2.ToI420Response
    unpublish_track: _room_pb2.UnpublishTrackResponse
    def __init__(self, initialize: _Optional[_Union[InitializeResponse, _Mapping]] = ..., dispose: _Optional[_Union[DisposeResponse, _Mapping]] = ..., connect: _Optional[_Union[_room_pb2.ConnectResponse, _Mapping]] = ..., disconnect: _Optional[_Union[_room_pb2.DisconnectResponse, _Mapping]] = ..., publish_track: _Optional[_Union[_room_pb2.PublishTrackResponse, _Mapping]] = ..., unpublish_track: _Optional[_Union[_room_pb2.UnpublishTrackResponse, _Mapping]] = ..., create_video_track: _Optional[_Union[_track_pb2.CreateVideoTrackResponse, _Mapping]] = ..., create_audio_track: _Optional[_Union[_track_pb2.CreateAudioTrackResponse, _Mapping]] = ..., alloc_video_buffer: _Optional[_Union[_video_frame_pb2.AllocVideoBufferResponse, _Mapping]] = ..., new_video_stream: _Optional[_Union[_video_frame_pb2.NewVideoStreamResponse, _Mapping]] = ..., new_video_source: _Optional[_Union[_video_frame_pb2.NewVideoSourceResponse, _Mapping]] = ..., capture_video_frame: _Optional[_Union[_video_frame_pb2.CaptureVideoFrameResponse, _Mapping]] = ..., to_i420: _Optional[_Union[_video_frame_pb2.ToI420Response, _Mapping]] = ..., to_argb: _Optional[_Union[_video_frame_pb2.ToARGBResponse, _Mapping]] = ..., alloc_audio_buffer: _Optional[_Union[_audio_frame_pb2.AllocAudioBufferResponse, _Mapping]] = ..., new_audio_stream: _Optional[_Union[_audio_frame_pb2.NewAudioStreamResponse, _Mapping]] = ..., new_audio_source: _Optional[_Union[_audio_frame_pb2.NewAudioSourceResponse, _Mapping]] = ..., capture_audio_frame: _Optional[_Union[_audio_frame_pb2.CaptureAudioFrameResponse, _Mapping]] = ..., new_audio_resampler: _Optional[_Union[_audio_frame_pb2.NewAudioResamplerResponse, _Mapping]] = ..., remix_and_resample: _Optional[_Union[_audio_frame_pb2.RemixAndResampleResponse, _Mapping]] = ...) -> None: ...

class InitializeRequest(_message.Message):
    __slots__ = ["event_callback_ptr"]
    EVENT_CALLBACK_PTR_FIELD_NUMBER: _ClassVar[int]
    event_callback_ptr: int
    def __init__(self, event_callback_ptr: _Optional[int] = ...) -> None: ...

class InitializeResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
