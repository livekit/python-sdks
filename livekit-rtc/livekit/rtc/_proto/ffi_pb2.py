# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ffi.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import e2ee_pb2 as e2ee__pb2
from . import track_pb2 as track__pb2
from . import track_publication_pb2 as track__publication__pb2
from . import room_pb2 as room__pb2
from . import video_frame_pb2 as video__frame__pb2
from . import audio_frame_pb2 as audio__frame__pb2
from . import rpc_pb2 as rpc__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tffi.proto\x12\rlivekit.proto\x1a\ne2ee.proto\x1a\x0btrack.proto\x1a\x17track_publication.proto\x1a\nroom.proto\x1a\x11video_frame.proto\x1a\x11\x61udio_frame.proto\x1a\trpc.proto\"\xf7\x16\n\nFfiRequest\x12\x30\n\x07\x64ispose\x18\x02 \x01(\x0b\x32\x1d.livekit.proto.DisposeRequestH\x00\x12\x30\n\x07\x63onnect\x18\x03 \x01(\x0b\x32\x1d.livekit.proto.ConnectRequestH\x00\x12\x36\n\ndisconnect\x18\x04 \x01(\x0b\x32 .livekit.proto.DisconnectRequestH\x00\x12;\n\rpublish_track\x18\x05 \x01(\x0b\x32\".livekit.proto.PublishTrackRequestH\x00\x12?\n\x0funpublish_track\x18\x06 \x01(\x0b\x32$.livekit.proto.UnpublishTrackRequestH\x00\x12\x39\n\x0cpublish_data\x18\x07 \x01(\x0b\x32!.livekit.proto.PublishDataRequestH\x00\x12=\n\x0eset_subscribed\x18\x08 \x01(\x0b\x32#.livekit.proto.SetSubscribedRequestH\x00\x12\x44\n\x12set_local_metadata\x18\t \x01(\x0b\x32&.livekit.proto.SetLocalMetadataRequestH\x00\x12<\n\x0eset_local_name\x18\n \x01(\x0b\x32\".livekit.proto.SetLocalNameRequestH\x00\x12H\n\x14set_local_attributes\x18\x0b \x01(\x0b\x32(.livekit.proto.SetLocalAttributesRequestH\x00\x12\x42\n\x11get_session_stats\x18\x0c \x01(\x0b\x32%.livekit.proto.GetSessionStatsRequestH\x00\x12K\n\x15publish_transcription\x18\r \x01(\x0b\x32*.livekit.proto.PublishTranscriptionRequestH\x00\x12@\n\x10publish_sip_dtmf\x18\x0e \x01(\x0b\x32$.livekit.proto.PublishSipDtmfRequestH\x00\x12\x44\n\x12\x63reate_video_track\x18\x0f \x01(\x0b\x32&.livekit.proto.CreateVideoTrackRequestH\x00\x12\x44\n\x12\x63reate_audio_track\x18\x10 \x01(\x0b\x32&.livekit.proto.CreateAudioTrackRequestH\x00\x12@\n\x10local_track_mute\x18\x11 \x01(\x0b\x32$.livekit.proto.LocalTrackMuteRequestH\x00\x12\x46\n\x13\x65nable_remote_track\x18\x12 \x01(\x0b\x32\'.livekit.proto.EnableRemoteTrackRequestH\x00\x12\x33\n\tget_stats\x18\x13 \x01(\x0b\x32\x1e.livekit.proto.GetStatsRequestH\x00\x12@\n\x10new_video_stream\x18\x14 \x01(\x0b\x32$.livekit.proto.NewVideoStreamRequestH\x00\x12@\n\x10new_video_source\x18\x15 \x01(\x0b\x32$.livekit.proto.NewVideoSourceRequestH\x00\x12\x46\n\x13\x63\x61pture_video_frame\x18\x16 \x01(\x0b\x32\'.livekit.proto.CaptureVideoFrameRequestH\x00\x12;\n\rvideo_convert\x18\x17 \x01(\x0b\x32\".livekit.proto.VideoConvertRequestH\x00\x12Y\n\x1dvideo_stream_from_participant\x18\x18 \x01(\x0b\x32\x30.livekit.proto.VideoStreamFromParticipantRequestH\x00\x12@\n\x10new_audio_stream\x18\x19 \x01(\x0b\x32$.livekit.proto.NewAudioStreamRequestH\x00\x12@\n\x10new_audio_source\x18\x1a \x01(\x0b\x32$.livekit.proto.NewAudioSourceRequestH\x00\x12\x46\n\x13\x63\x61pture_audio_frame\x18\x1b \x01(\x0b\x32\'.livekit.proto.CaptureAudioFrameRequestH\x00\x12\x44\n\x12\x63lear_audio_buffer\x18\x1c \x01(\x0b\x32&.livekit.proto.ClearAudioBufferRequestH\x00\x12\x46\n\x13new_audio_resampler\x18\x1d \x01(\x0b\x32\'.livekit.proto.NewAudioResamplerRequestH\x00\x12\x44\n\x12remix_and_resample\x18\x1e \x01(\x0b\x32&.livekit.proto.RemixAndResampleRequestH\x00\x12*\n\x04\x65\x32\x65\x65\x18\x1f \x01(\x0b\x32\x1a.livekit.proto.E2eeRequestH\x00\x12Y\n\x1d\x61udio_stream_from_participant\x18  \x01(\x0b\x32\x30.livekit.proto.AudioStreamFromParticipantRequestH\x00\x12\x42\n\x11new_sox_resampler\x18! \x01(\x0b\x32%.livekit.proto.NewSoxResamplerRequestH\x00\x12\x44\n\x12push_sox_resampler\x18\" \x01(\x0b\x32&.livekit.proto.PushSoxResamplerRequestH\x00\x12\x46\n\x13\x66lush_sox_resampler\x18# \x01(\x0b\x32\'.livekit.proto.FlushSoxResamplerRequestH\x00\x12\x42\n\x11send_chat_message\x18$ \x01(\x0b\x32%.livekit.proto.SendChatMessageRequestH\x00\x12\x42\n\x11\x65\x64it_chat_message\x18% \x01(\x0b\x32%.livekit.proto.EditChatMessageRequestH\x00\x12\x37\n\x0bperform_rpc\x18& \x01(\x0b\x32 .livekit.proto.PerformRpcRequestH\x00\x12\x46\n\x13register_rpc_method\x18\' \x01(\x0b\x32\'.livekit.proto.RegisterRpcMethodRequestH\x00\x12J\n\x15unregister_rpc_method\x18( \x01(\x0b\x32).livekit.proto.UnregisterRpcMethodRequestH\x00\x12[\n\x1erpc_method_invocation_response\x18) \x01(\x0b\x32\x31.livekit.proto.RpcMethodInvocationResponseRequestH\x00\x12]\n\x1f\x65nable_remote_track_publication\x18* \x01(\x0b\x32\x32.livekit.proto.EnableRemoteTrackPublicationRequestH\x00\x12p\n)update_remote_track_publication_dimension\x18+ \x01(\x0b\x32;.livekit.proto.UpdateRemoteTrackPublicationDimensionRequestH\x00\x42\t\n\x07message\"\xdd\x16\n\x0b\x46\x66iResponse\x12\x31\n\x07\x64ispose\x18\x02 \x01(\x0b\x32\x1e.livekit.proto.DisposeResponseH\x00\x12\x31\n\x07\x63onnect\x18\x03 \x01(\x0b\x32\x1e.livekit.proto.ConnectResponseH\x00\x12\x37\n\ndisconnect\x18\x04 \x01(\x0b\x32!.livekit.proto.DisconnectResponseH\x00\x12<\n\rpublish_track\x18\x05 \x01(\x0b\x32#.livekit.proto.PublishTrackResponseH\x00\x12@\n\x0funpublish_track\x18\x06 \x01(\x0b\x32%.livekit.proto.UnpublishTrackResponseH\x00\x12:\n\x0cpublish_data\x18\x07 \x01(\x0b\x32\".livekit.proto.PublishDataResponseH\x00\x12>\n\x0eset_subscribed\x18\x08 \x01(\x0b\x32$.livekit.proto.SetSubscribedResponseH\x00\x12\x45\n\x12set_local_metadata\x18\t \x01(\x0b\x32\'.livekit.proto.SetLocalMetadataResponseH\x00\x12=\n\x0eset_local_name\x18\n \x01(\x0b\x32#.livekit.proto.SetLocalNameResponseH\x00\x12I\n\x14set_local_attributes\x18\x0b \x01(\x0b\x32).livekit.proto.SetLocalAttributesResponseH\x00\x12\x43\n\x11get_session_stats\x18\x0c \x01(\x0b\x32&.livekit.proto.GetSessionStatsResponseH\x00\x12L\n\x15publish_transcription\x18\r \x01(\x0b\x32+.livekit.proto.PublishTranscriptionResponseH\x00\x12\x41\n\x10publish_sip_dtmf\x18\x0e \x01(\x0b\x32%.livekit.proto.PublishSipDtmfResponseH\x00\x12\x45\n\x12\x63reate_video_track\x18\x0f \x01(\x0b\x32\'.livekit.proto.CreateVideoTrackResponseH\x00\x12\x45\n\x12\x63reate_audio_track\x18\x10 \x01(\x0b\x32\'.livekit.proto.CreateAudioTrackResponseH\x00\x12\x41\n\x10local_track_mute\x18\x11 \x01(\x0b\x32%.livekit.proto.LocalTrackMuteResponseH\x00\x12G\n\x13\x65nable_remote_track\x18\x12 \x01(\x0b\x32(.livekit.proto.EnableRemoteTrackResponseH\x00\x12\x34\n\tget_stats\x18\x13 \x01(\x0b\x32\x1f.livekit.proto.GetStatsResponseH\x00\x12\x41\n\x10new_video_stream\x18\x14 \x01(\x0b\x32%.livekit.proto.NewVideoStreamResponseH\x00\x12\x41\n\x10new_video_source\x18\x15 \x01(\x0b\x32%.livekit.proto.NewVideoSourceResponseH\x00\x12G\n\x13\x63\x61pture_video_frame\x18\x16 \x01(\x0b\x32(.livekit.proto.CaptureVideoFrameResponseH\x00\x12<\n\rvideo_convert\x18\x17 \x01(\x0b\x32#.livekit.proto.VideoConvertResponseH\x00\x12Z\n\x1dvideo_stream_from_participant\x18\x18 \x01(\x0b\x32\x31.livekit.proto.VideoStreamFromParticipantResponseH\x00\x12\x41\n\x10new_audio_stream\x18\x19 \x01(\x0b\x32%.livekit.proto.NewAudioStreamResponseH\x00\x12\x41\n\x10new_audio_source\x18\x1a \x01(\x0b\x32%.livekit.proto.NewAudioSourceResponseH\x00\x12G\n\x13\x63\x61pture_audio_frame\x18\x1b \x01(\x0b\x32(.livekit.proto.CaptureAudioFrameResponseH\x00\x12\x45\n\x12\x63lear_audio_buffer\x18\x1c \x01(\x0b\x32\'.livekit.proto.ClearAudioBufferResponseH\x00\x12G\n\x13new_audio_resampler\x18\x1d \x01(\x0b\x32(.livekit.proto.NewAudioResamplerResponseH\x00\x12\x45\n\x12remix_and_resample\x18\x1e \x01(\x0b\x32\'.livekit.proto.RemixAndResampleResponseH\x00\x12Z\n\x1d\x61udio_stream_from_participant\x18\x1f \x01(\x0b\x32\x31.livekit.proto.AudioStreamFromParticipantResponseH\x00\x12+\n\x04\x65\x32\x65\x65\x18  \x01(\x0b\x32\x1b.livekit.proto.E2eeResponseH\x00\x12\x43\n\x11new_sox_resampler\x18! \x01(\x0b\x32&.livekit.proto.NewSoxResamplerResponseH\x00\x12\x45\n\x12push_sox_resampler\x18\" \x01(\x0b\x32\'.livekit.proto.PushSoxResamplerResponseH\x00\x12G\n\x13\x66lush_sox_resampler\x18# \x01(\x0b\x32(.livekit.proto.FlushSoxResamplerResponseH\x00\x12\x43\n\x11send_chat_message\x18$ \x01(\x0b\x32&.livekit.proto.SendChatMessageResponseH\x00\x12\x38\n\x0bperform_rpc\x18% \x01(\x0b\x32!.livekit.proto.PerformRpcResponseH\x00\x12G\n\x13register_rpc_method\x18& \x01(\x0b\x32(.livekit.proto.RegisterRpcMethodResponseH\x00\x12K\n\x15unregister_rpc_method\x18\' \x01(\x0b\x32*.livekit.proto.UnregisterRpcMethodResponseH\x00\x12\\\n\x1erpc_method_invocation_response\x18( \x01(\x0b\x32\x32.livekit.proto.RpcMethodInvocationResponseResponseH\x00\x12^\n\x1f\x65nable_remote_track_publication\x18) \x01(\x0b\x32\x33.livekit.proto.EnableRemoteTrackPublicationResponseH\x00\x12q\n)update_remote_track_publication_dimension\x18* \x01(\x0b\x32<.livekit.proto.UpdateRemoteTrackPublicationDimensionResponseH\x00\x42\t\n\x07message\"\x8a\x0b\n\x08\x46\x66iEvent\x12.\n\nroom_event\x18\x01 \x01(\x0b\x32\x18.livekit.proto.RoomEventH\x00\x12\x30\n\x0btrack_event\x18\x02 \x01(\x0b\x32\x19.livekit.proto.TrackEventH\x00\x12=\n\x12video_stream_event\x18\x03 \x01(\x0b\x32\x1f.livekit.proto.VideoStreamEventH\x00\x12=\n\x12\x61udio_stream_event\x18\x04 \x01(\x0b\x32\x1f.livekit.proto.AudioStreamEventH\x00\x12\x31\n\x07\x63onnect\x18\x05 \x01(\x0b\x32\x1e.livekit.proto.ConnectCallbackH\x00\x12\x37\n\ndisconnect\x18\x07 \x01(\x0b\x32!.livekit.proto.DisconnectCallbackH\x00\x12\x31\n\x07\x64ispose\x18\x08 \x01(\x0b\x32\x1e.livekit.proto.DisposeCallbackH\x00\x12<\n\rpublish_track\x18\t \x01(\x0b\x32#.livekit.proto.PublishTrackCallbackH\x00\x12@\n\x0funpublish_track\x18\n \x01(\x0b\x32%.livekit.proto.UnpublishTrackCallbackH\x00\x12:\n\x0cpublish_data\x18\x0b \x01(\x0b\x32\".livekit.proto.PublishDataCallbackH\x00\x12L\n\x15publish_transcription\x18\x0c \x01(\x0b\x32+.livekit.proto.PublishTranscriptionCallbackH\x00\x12G\n\x13\x63\x61pture_audio_frame\x18\r \x01(\x0b\x32(.livekit.proto.CaptureAudioFrameCallbackH\x00\x12\x45\n\x12set_local_metadata\x18\x0e \x01(\x0b\x32\'.livekit.proto.SetLocalMetadataCallbackH\x00\x12=\n\x0eset_local_name\x18\x0f \x01(\x0b\x32#.livekit.proto.SetLocalNameCallbackH\x00\x12I\n\x14set_local_attributes\x18\x10 \x01(\x0b\x32).livekit.proto.SetLocalAttributesCallbackH\x00\x12\x34\n\tget_stats\x18\x11 \x01(\x0b\x32\x1f.livekit.proto.GetStatsCallbackH\x00\x12\'\n\x04logs\x18\x12 \x01(\x0b\x32\x17.livekit.proto.LogBatchH\x00\x12\x43\n\x11get_session_stats\x18\x13 \x01(\x0b\x32&.livekit.proto.GetSessionStatsCallbackH\x00\x12%\n\x05panic\x18\x14 \x01(\x0b\x32\x14.livekit.proto.PanicH\x00\x12\x41\n\x10publish_sip_dtmf\x18\x15 \x01(\x0b\x32%.livekit.proto.PublishSipDtmfCallbackH\x00\x12>\n\x0c\x63hat_message\x18\x16 \x01(\x0b\x32&.livekit.proto.SendChatMessageCallbackH\x00\x12\x38\n\x0bperform_rpc\x18\x17 \x01(\x0b\x32!.livekit.proto.PerformRpcCallbackH\x00\x12H\n\x15rpc_method_invocation\x18\x18 \x01(\x0b\x32\'.livekit.proto.RpcMethodInvocationEventH\x00\x42\t\n\x07message\"\x1f\n\x0e\x44isposeRequest\x12\r\n\x05\x61sync\x18\x01 \x02(\x08\"#\n\x0f\x44isposeResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"#\n\x0f\x44isposeCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"\x85\x01\n\tLogRecord\x12&\n\x05level\x18\x01 \x02(\x0e\x32\x17.livekit.proto.LogLevel\x12\x0e\n\x06target\x18\x02 \x02(\t\x12\x13\n\x0bmodule_path\x18\x03 \x01(\t\x12\x0c\n\x04\x66ile\x18\x04 \x01(\t\x12\x0c\n\x04line\x18\x05 \x01(\r\x12\x0f\n\x07message\x18\x06 \x02(\t\"5\n\x08LogBatch\x12)\n\x07records\x18\x01 \x03(\x0b\x32\x18.livekit.proto.LogRecord\"\x18\n\x05Panic\x12\x0f\n\x07message\x18\x01 \x02(\t*S\n\x08LogLevel\x12\r\n\tLOG_ERROR\x10\x00\x12\x0c\n\x08LOG_WARN\x10\x01\x12\x0c\n\x08LOG_INFO\x10\x02\x12\r\n\tLOG_DEBUG\x10\x03\x12\r\n\tLOG_TRACE\x10\x04\x42\x10\xaa\x02\rLiveKit.Proto')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ffi_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\rLiveKit.Proto'
  _globals['_LOGLEVEL']._serialized_start=7734
  _globals['_LOGLEVEL']._serialized_end=7817
  _globals['_FFIREQUEST']._serialized_start=140
  _globals['_FFIREQUEST']._serialized_end=3075
  _globals['_FFIRESPONSE']._serialized_start=3078
  _globals['_FFIRESPONSE']._serialized_end=5987
  _globals['_FFIEVENT']._serialized_start=5990
  _globals['_FFIEVENT']._serialized_end=7408
  _globals['_DISPOSEREQUEST']._serialized_start=7410
  _globals['_DISPOSEREQUEST']._serialized_end=7441
  _globals['_DISPOSERESPONSE']._serialized_start=7443
  _globals['_DISPOSERESPONSE']._serialized_end=7478
  _globals['_DISPOSECALLBACK']._serialized_start=7480
  _globals['_DISPOSECALLBACK']._serialized_end=7515
  _globals['_LOGRECORD']._serialized_start=7518
  _globals['_LOGRECORD']._serialized_end=7651
  _globals['_LOGBATCH']._serialized_start=7653
  _globals['_LOGBATCH']._serialized_end=7706
  _globals['_PANIC']._serialized_start=7708
  _globals['_PANIC']._serialized_end=7732
# @@protoc_insertion_point(module_scope)
