# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: video_frame.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import handle_pb2 as handle__pb2
from . import track_pb2 as track__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11video_frame.proto\x12\rlivekit.proto\x1a\x0chandle.proto\x1a\x0btrack.proto\"\xa5\x01\n\x15NewVideoStreamRequest\x12\x14\n\x0ctrack_handle\x18\x01 \x02(\x04\x12,\n\x04type\x18\x02 \x02(\x0e\x32\x1e.livekit.proto.VideoStreamType\x12.\n\x06\x66ormat\x18\x03 \x01(\x0e\x32\x1e.livekit.proto.VideoBufferType\x12\x18\n\x10normalize_stride\x18\x04 \x01(\x08\"I\n\x16NewVideoStreamResponse\x12/\n\x06stream\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedVideoStream\"\xe9\x01\n!VideoStreamFromParticipantRequest\x12\x1a\n\x12participant_handle\x18\x01 \x02(\x04\x12,\n\x04type\x18\x02 \x02(\x0e\x32\x1e.livekit.proto.VideoStreamType\x12\x30\n\x0ctrack_source\x18\x03 \x02(\x0e\x32\x1a.livekit.proto.TrackSource\x12.\n\x06\x66ormat\x18\x04 \x01(\x0e\x32\x1e.livekit.proto.VideoBufferType\x12\x18\n\x10normalize_stride\x18\x05 \x01(\x08\"U\n\"VideoStreamFromParticipantResponse\x12/\n\x06stream\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedVideoStream\"\x7f\n\x15NewVideoSourceRequest\x12,\n\x04type\x18\x01 \x02(\x0e\x32\x1e.livekit.proto.VideoSourceType\x12\x38\n\nresolution\x18\x02 \x02(\x0b\x32$.livekit.proto.VideoSourceResolution\"I\n\x16NewVideoSourceResponse\x12/\n\x06source\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedVideoSource\"\xa7\x01\n\x18\x43\x61ptureVideoFrameRequest\x12\x15\n\rsource_handle\x18\x01 \x02(\x04\x12.\n\x06\x62uffer\x18\x02 \x02(\x0b\x32\x1e.livekit.proto.VideoBufferInfo\x12\x14\n\x0ctimestamp_us\x18\x03 \x02(\x03\x12.\n\x08rotation\x18\x04 \x02(\x0e\x32\x1c.livekit.proto.VideoRotation\"\x1b\n\x19\x43\x61ptureVideoFrameResponse\"\x87\x01\n\x13VideoConvertRequest\x12\x0e\n\x06\x66lip_y\x18\x01 \x01(\x08\x12.\n\x06\x62uffer\x18\x02 \x02(\x0b\x32\x1e.livekit.proto.VideoBufferInfo\x12\x30\n\x08\x64st_type\x18\x03 \x02(\x0e\x32\x1e.livekit.proto.VideoBufferType\"e\n\x14VideoConvertResponse\x12\x0f\n\x05\x65rror\x18\x01 \x01(\tH\x00\x12\x31\n\x06\x62uffer\x18\x02 \x01(\x0b\x32\x1f.livekit.proto.OwnedVideoBufferH\x00\x42\t\n\x07message\"D\n\x0fVideoResolution\x12\r\n\x05width\x18\x01 \x02(\r\x12\x0e\n\x06height\x18\x02 \x02(\r\x12\x12\n\nframe_rate\x18\x03 \x02(\x01\"\x83\x02\n\x0fVideoBufferInfo\x12,\n\x04type\x18\x01 \x02(\x0e\x32\x1e.livekit.proto.VideoBufferType\x12\r\n\x05width\x18\x02 \x02(\r\x12\x0e\n\x06height\x18\x03 \x02(\r\x12\x10\n\x08\x64\x61ta_ptr\x18\x04 \x02(\x04\x12\x0e\n\x06stride\x18\x06 \x02(\r\x12@\n\ncomponents\x18\x07 \x03(\x0b\x32,.livekit.proto.VideoBufferInfo.ComponentInfo\x1a?\n\rComponentInfo\x12\x10\n\x08\x64\x61ta_ptr\x18\x01 \x02(\x04\x12\x0e\n\x06stride\x18\x02 \x02(\r\x12\x0c\n\x04size\x18\x03 \x02(\r\"o\n\x10OwnedVideoBuffer\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12,\n\x04info\x18\x02 \x02(\x0b\x32\x1e.livekit.proto.VideoBufferInfo\"?\n\x0fVideoStreamInfo\x12,\n\x04type\x18\x01 \x02(\x0e\x32\x1e.livekit.proto.VideoStreamType\"o\n\x10OwnedVideoStream\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12,\n\x04info\x18\x02 \x02(\x0b\x32\x1e.livekit.proto.VideoStreamInfo\"\x9f\x01\n\x10VideoStreamEvent\x12\x15\n\rstream_handle\x18\x01 \x02(\x04\x12;\n\x0e\x66rame_received\x18\x02 \x01(\x0b\x32!.livekit.proto.VideoFrameReceivedH\x00\x12,\n\x03\x65os\x18\x03 \x01(\x0b\x32\x1d.livekit.proto.VideoStreamEOSH\x00\x42\t\n\x07message\"\x8b\x01\n\x12VideoFrameReceived\x12/\n\x06\x62uffer\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedVideoBuffer\x12\x14\n\x0ctimestamp_us\x18\x02 \x02(\x03\x12.\n\x08rotation\x18\x03 \x02(\x0e\x32\x1c.livekit.proto.VideoRotation\"\x10\n\x0eVideoStreamEOS\"6\n\x15VideoSourceResolution\x12\r\n\x05width\x18\x01 \x02(\r\x12\x0e\n\x06height\x18\x02 \x02(\r\"?\n\x0fVideoSourceInfo\x12,\n\x04type\x18\x01 \x02(\x0e\x32\x1e.livekit.proto.VideoSourceType\"o\n\x10OwnedVideoSource\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12,\n\x04info\x18\x02 \x02(\x0b\x32\x1e.livekit.proto.VideoSourceInfo*1\n\nVideoCodec\x12\x07\n\x03VP8\x10\x00\x12\x08\n\x04H264\x10\x01\x12\x07\n\x03\x41V1\x10\x02\x12\x07\n\x03VP9\x10\x03*l\n\rVideoRotation\x12\x14\n\x10VIDEO_ROTATION_0\x10\x00\x12\x15\n\x11VIDEO_ROTATION_90\x10\x01\x12\x16\n\x12VIDEO_ROTATION_180\x10\x02\x12\x16\n\x12VIDEO_ROTATION_270\x10\x03*\x81\x01\n\x0fVideoBufferType\x12\x08\n\x04RGBA\x10\x00\x12\x08\n\x04\x41\x42GR\x10\x01\x12\x08\n\x04\x41RGB\x10\x02\x12\x08\n\x04\x42GRA\x10\x03\x12\t\n\x05RGB24\x10\x04\x12\x08\n\x04I420\x10\x05\x12\t\n\x05I420A\x10\x06\x12\x08\n\x04I422\x10\x07\x12\x08\n\x04I444\x10\x08\x12\x08\n\x04I010\x10\t\x12\x08\n\x04NV12\x10\n*Y\n\x0fVideoStreamType\x12\x17\n\x13VIDEO_STREAM_NATIVE\x10\x00\x12\x16\n\x12VIDEO_STREAM_WEBGL\x10\x01\x12\x15\n\x11VIDEO_STREAM_HTML\x10\x02**\n\x0fVideoSourceType\x12\x17\n\x13VIDEO_SOURCE_NATIVE\x10\x00\x42\x10\xaa\x02\rLiveKit.Proto')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'video_frame_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\rLiveKit.Proto'
  _globals['_VIDEOCODEC']._serialized_start=2452
  _globals['_VIDEOCODEC']._serialized_end=2501
  _globals['_VIDEOROTATION']._serialized_start=2503
  _globals['_VIDEOROTATION']._serialized_end=2611
  _globals['_VIDEOBUFFERTYPE']._serialized_start=2614
  _globals['_VIDEOBUFFERTYPE']._serialized_end=2743
  _globals['_VIDEOSTREAMTYPE']._serialized_start=2745
  _globals['_VIDEOSTREAMTYPE']._serialized_end=2834
  _globals['_VIDEOSOURCETYPE']._serialized_start=2836
  _globals['_VIDEOSOURCETYPE']._serialized_end=2878
  _globals['_NEWVIDEOSTREAMREQUEST']._serialized_start=64
  _globals['_NEWVIDEOSTREAMREQUEST']._serialized_end=229
  _globals['_NEWVIDEOSTREAMRESPONSE']._serialized_start=231
  _globals['_NEWVIDEOSTREAMRESPONSE']._serialized_end=304
  _globals['_VIDEOSTREAMFROMPARTICIPANTREQUEST']._serialized_start=307
  _globals['_VIDEOSTREAMFROMPARTICIPANTREQUEST']._serialized_end=540
  _globals['_VIDEOSTREAMFROMPARTICIPANTRESPONSE']._serialized_start=542
  _globals['_VIDEOSTREAMFROMPARTICIPANTRESPONSE']._serialized_end=627
  _globals['_NEWVIDEOSOURCEREQUEST']._serialized_start=629
  _globals['_NEWVIDEOSOURCEREQUEST']._serialized_end=756
  _globals['_NEWVIDEOSOURCERESPONSE']._serialized_start=758
  _globals['_NEWVIDEOSOURCERESPONSE']._serialized_end=831
  _globals['_CAPTUREVIDEOFRAMEREQUEST']._serialized_start=834
  _globals['_CAPTUREVIDEOFRAMEREQUEST']._serialized_end=1001
  _globals['_CAPTUREVIDEOFRAMERESPONSE']._serialized_start=1003
  _globals['_CAPTUREVIDEOFRAMERESPONSE']._serialized_end=1030
  _globals['_VIDEOCONVERTREQUEST']._serialized_start=1033
  _globals['_VIDEOCONVERTREQUEST']._serialized_end=1168
  _globals['_VIDEOCONVERTRESPONSE']._serialized_start=1170
  _globals['_VIDEOCONVERTRESPONSE']._serialized_end=1271
  _globals['_VIDEORESOLUTION']._serialized_start=1273
  _globals['_VIDEORESOLUTION']._serialized_end=1341
  _globals['_VIDEOBUFFERINFO']._serialized_start=1344
  _globals['_VIDEOBUFFERINFO']._serialized_end=1603
  _globals['_VIDEOBUFFERINFO_COMPONENTINFO']._serialized_start=1540
  _globals['_VIDEOBUFFERINFO_COMPONENTINFO']._serialized_end=1603
  _globals['_OWNEDVIDEOBUFFER']._serialized_start=1605
  _globals['_OWNEDVIDEOBUFFER']._serialized_end=1716
  _globals['_VIDEOSTREAMINFO']._serialized_start=1718
  _globals['_VIDEOSTREAMINFO']._serialized_end=1781
  _globals['_OWNEDVIDEOSTREAM']._serialized_start=1783
  _globals['_OWNEDVIDEOSTREAM']._serialized_end=1894
  _globals['_VIDEOSTREAMEVENT']._serialized_start=1897
  _globals['_VIDEOSTREAMEVENT']._serialized_end=2056
  _globals['_VIDEOFRAMERECEIVED']._serialized_start=2059
  _globals['_VIDEOFRAMERECEIVED']._serialized_end=2198
  _globals['_VIDEOSTREAMEOS']._serialized_start=2200
  _globals['_VIDEOSTREAMEOS']._serialized_end=2216
  _globals['_VIDEOSOURCERESOLUTION']._serialized_start=2218
  _globals['_VIDEOSOURCERESOLUTION']._serialized_end=2272
  _globals['_VIDEOSOURCEINFO']._serialized_start=2274
  _globals['_VIDEOSOURCEINFO']._serialized_end=2337
  _globals['_OWNEDVIDEOSOURCE']._serialized_start=2339
  _globals['_OWNEDVIDEOSOURCE']._serialized_end=2450
# @@protoc_insertion_point(module_scope)
