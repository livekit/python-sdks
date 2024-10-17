# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: audio_frame.proto
# Protobuf Python Version: 5.27.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    1,
    '',
    'audio_frame.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import handle_pb2 as handle__pb2
from . import track_pb2 as track__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11\x61udio_frame.proto\x12\rlivekit.proto\x1a\x0chandle.proto\x1a\x0btrack.proto\"\x86\x01\n\x15NewAudioStreamRequest\x12\x14\n\x0ctrack_handle\x18\x01 \x02(\x04\x12,\n\x04type\x18\x02 \x02(\x0e\x32\x1e.livekit.proto.AudioStreamType\x12\x13\n\x0bsample_rate\x18\x03 \x02(\r\x12\x14\n\x0cnum_channels\x18\x04 \x02(\r\"I\n\x16NewAudioStreamResponse\x12/\n\x06stream\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedAudioStream\"\xca\x01\n!AudioStreamFromParticipantRequest\x12\x1a\n\x12participant_handle\x18\x01 \x02(\x04\x12,\n\x04type\x18\x02 \x02(\x0e\x32\x1e.livekit.proto.AudioStreamType\x12\x30\n\x0ctrack_source\x18\x03 \x01(\x0e\x32\x1a.livekit.proto.TrackSource\x12\x13\n\x0bsample_rate\x18\x05 \x02(\r\x12\x14\n\x0cnum_channels\x18\x06 \x02(\r\"U\n\"AudioStreamFromParticipantResponse\x12/\n\x06stream\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedAudioStream\"\xbb\x01\n\x15NewAudioSourceRequest\x12,\n\x04type\x18\x01 \x02(\x0e\x32\x1e.livekit.proto.AudioSourceType\x12\x32\n\x07options\x18\x02 \x01(\x0b\x32!.livekit.proto.AudioSourceOptions\x12\x13\n\x0bsample_rate\x18\x03 \x02(\r\x12\x14\n\x0cnum_channels\x18\x04 \x02(\r\x12\x15\n\rqueue_size_ms\x18\x05 \x02(\r\"I\n\x16NewAudioSourceResponse\x12/\n\x06source\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedAudioSource\"f\n\x18\x43\x61ptureAudioFrameRequest\x12\x15\n\rsource_handle\x18\x01 \x02(\x04\x12\x33\n\x06\x62uffer\x18\x02 \x02(\x0b\x32#.livekit.proto.AudioFrameBufferInfo\"-\n\x19\x43\x61ptureAudioFrameResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"<\n\x19\x43\x61ptureAudioFrameCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"0\n\x17\x43learAudioBufferRequest\x12\x15\n\rsource_handle\x18\x01 \x02(\x04\"\x1a\n\x18\x43learAudioBufferResponse\"\x1a\n\x18NewAudioResamplerRequest\"R\n\x19NewAudioResamplerResponse\x12\x35\n\tresampler\x18\x01 \x02(\x0b\x32\".livekit.proto.OwnedAudioResampler\"\x93\x01\n\x17RemixAndResampleRequest\x12\x18\n\x10resampler_handle\x18\x01 \x02(\x04\x12\x33\n\x06\x62uffer\x18\x02 \x02(\x0b\x32#.livekit.proto.AudioFrameBufferInfo\x12\x14\n\x0cnum_channels\x18\x03 \x02(\r\x12\x13\n\x0bsample_rate\x18\x04 \x02(\r\"P\n\x18RemixAndResampleResponse\x12\x34\n\x06\x62uffer\x18\x01 \x02(\x0b\x32$.livekit.proto.OwnedAudioFrameBuffer\"\x9c\x02\n\x16NewSoxResamplerRequest\x12\x12\n\ninput_rate\x18\x01 \x02(\x01\x12\x13\n\x0boutput_rate\x18\x02 \x02(\x01\x12\x14\n\x0cnum_channels\x18\x03 \x02(\r\x12<\n\x0finput_data_type\x18\x04 \x02(\x0e\x32#.livekit.proto.SoxResamplerDataType\x12=\n\x10output_data_type\x18\x05 \x02(\x0e\x32#.livekit.proto.SoxResamplerDataType\x12\x37\n\x0equality_recipe\x18\x06 \x02(\x0e\x32\x1f.livekit.proto.SoxQualityRecipe\x12\r\n\x05\x66lags\x18\x07 \x02(\r\"l\n\x17NewSoxResamplerResponse\x12\x35\n\tresampler\x18\x01 \x01(\x0b\x32 .livekit.proto.OwnedSoxResamplerH\x00\x12\x0f\n\x05\x65rror\x18\x02 \x01(\tH\x00\x42\t\n\x07message\"S\n\x17PushSoxResamplerRequest\x12\x18\n\x10resampler_handle\x18\x01 \x02(\x04\x12\x10\n\x08\x64\x61ta_ptr\x18\x02 \x02(\x04\x12\x0c\n\x04size\x18\x03 \x02(\r\"K\n\x18PushSoxResamplerResponse\x12\x12\n\noutput_ptr\x18\x01 \x02(\x04\x12\x0c\n\x04size\x18\x02 \x02(\r\x12\r\n\x05\x65rror\x18\x03 \x01(\t\"4\n\x18\x46lushSoxResamplerRequest\x12\x18\n\x10resampler_handle\x18\x01 \x02(\x04\"L\n\x19\x46lushSoxResamplerResponse\x12\x12\n\noutput_ptr\x18\x01 \x02(\x04\x12\x0c\n\x04size\x18\x02 \x02(\r\x12\r\n\x05\x65rror\x18\x03 \x01(\t\"p\n\x14\x41udioFrameBufferInfo\x12\x10\n\x08\x64\x61ta_ptr\x18\x01 \x02(\x04\x12\x14\n\x0cnum_channels\x18\x02 \x02(\r\x12\x13\n\x0bsample_rate\x18\x03 \x02(\r\x12\x1b\n\x13samples_per_channel\x18\x04 \x02(\r\"y\n\x15OwnedAudioFrameBuffer\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12\x31\n\x04info\x18\x02 \x02(\x0b\x32#.livekit.proto.AudioFrameBufferInfo\"?\n\x0f\x41udioStreamInfo\x12,\n\x04type\x18\x01 \x02(\x0e\x32\x1e.livekit.proto.AudioStreamType\"o\n\x10OwnedAudioStream\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12,\n\x04info\x18\x02 \x02(\x0b\x32\x1e.livekit.proto.AudioStreamInfo\"\x9f\x01\n\x10\x41udioStreamEvent\x12\x15\n\rstream_handle\x18\x01 \x02(\x04\x12;\n\x0e\x66rame_received\x18\x02 \x01(\x0b\x32!.livekit.proto.AudioFrameReceivedH\x00\x12,\n\x03\x65os\x18\x03 \x01(\x0b\x32\x1d.livekit.proto.AudioStreamEOSH\x00\x42\t\n\x07message\"I\n\x12\x41udioFrameReceived\x12\x33\n\x05\x66rame\x18\x01 \x02(\x0b\x32$.livekit.proto.OwnedAudioFrameBuffer\"\x10\n\x0e\x41udioStreamEOS\"e\n\x12\x41udioSourceOptions\x12\x19\n\x11\x65\x63ho_cancellation\x18\x01 \x02(\x08\x12\x19\n\x11noise_suppression\x18\x02 \x02(\x08\x12\x19\n\x11\x61uto_gain_control\x18\x03 \x02(\x08\"?\n\x0f\x41udioSourceInfo\x12,\n\x04type\x18\x02 \x02(\x0e\x32\x1e.livekit.proto.AudioSourceType\"o\n\x10OwnedAudioSource\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12,\n\x04info\x18\x02 \x02(\x0b\x32\x1e.livekit.proto.AudioSourceInfo\"\x14\n\x12\x41udioResamplerInfo\"u\n\x13OwnedAudioResampler\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12/\n\x04info\x18\x02 \x02(\x0b\x32!.livekit.proto.AudioResamplerInfo\"\x12\n\x10SoxResamplerInfo\"q\n\x11OwnedSoxResampler\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12-\n\x04info\x18\x02 \x02(\x0b\x32\x1f.livekit.proto.SoxResamplerInfo*J\n\x14SoxResamplerDataType\x12\x18\n\x14SOXR_DATATYPE_INT16I\x10\x00\x12\x18\n\x14SOXR_DATATYPE_INT16S\x10\x01*\x8b\x01\n\x10SoxQualityRecipe\x12\x16\n\x12SOXR_QUALITY_QUICK\x10\x00\x12\x14\n\x10SOXR_QUALITY_LOW\x10\x01\x12\x17\n\x13SOXR_QUALITY_MEDIUM\x10\x02\x12\x15\n\x11SOXR_QUALITY_HIGH\x10\x03\x12\x19\n\x15SOXR_QUALITY_VERYHIGH\x10\x04*\x97\x01\n\x0bSoxFlagBits\x12\x16\n\x12SOXR_ROLLOFF_SMALL\x10\x00\x12\x17\n\x13SOXR_ROLLOFF_MEDIUM\x10\x01\x12\x15\n\x11SOXR_ROLLOFF_NONE\x10\x02\x12\x18\n\x14SOXR_HIGH_PREC_CLOCK\x10\x03\x12\x19\n\x15SOXR_DOUBLE_PRECISION\x10\x04\x12\x0b\n\x07SOXR_VR\x10\x05*A\n\x0f\x41udioStreamType\x12\x17\n\x13\x41UDIO_STREAM_NATIVE\x10\x00\x12\x15\n\x11\x41UDIO_STREAM_HTML\x10\x01**\n\x0f\x41udioSourceType\x12\x17\n\x13\x41UDIO_SOURCE_NATIVE\x10\x00\x42\x10\xaa\x02\rLiveKit.Proto')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'audio_frame_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\rLiveKit.Proto'
  _globals['_SOXRESAMPLERDATATYPE']._serialized_start=3385
  _globals['_SOXRESAMPLERDATATYPE']._serialized_end=3459
  _globals['_SOXQUALITYRECIPE']._serialized_start=3462
  _globals['_SOXQUALITYRECIPE']._serialized_end=3601
  _globals['_SOXFLAGBITS']._serialized_start=3604
  _globals['_SOXFLAGBITS']._serialized_end=3755
  _globals['_AUDIOSTREAMTYPE']._serialized_start=3757
  _globals['_AUDIOSTREAMTYPE']._serialized_end=3822
  _globals['_AUDIOSOURCETYPE']._serialized_start=3824
  _globals['_AUDIOSOURCETYPE']._serialized_end=3866
  _globals['_NEWAUDIOSTREAMREQUEST']._serialized_start=64
  _globals['_NEWAUDIOSTREAMREQUEST']._serialized_end=198
  _globals['_NEWAUDIOSTREAMRESPONSE']._serialized_start=200
  _globals['_NEWAUDIOSTREAMRESPONSE']._serialized_end=273
  _globals['_AUDIOSTREAMFROMPARTICIPANTREQUEST']._serialized_start=276
  _globals['_AUDIOSTREAMFROMPARTICIPANTREQUEST']._serialized_end=478
  _globals['_AUDIOSTREAMFROMPARTICIPANTRESPONSE']._serialized_start=480
  _globals['_AUDIOSTREAMFROMPARTICIPANTRESPONSE']._serialized_end=565
  _globals['_NEWAUDIOSOURCEREQUEST']._serialized_start=568
  _globals['_NEWAUDIOSOURCEREQUEST']._serialized_end=755
  _globals['_NEWAUDIOSOURCERESPONSE']._serialized_start=757
  _globals['_NEWAUDIOSOURCERESPONSE']._serialized_end=830
  _globals['_CAPTUREAUDIOFRAMEREQUEST']._serialized_start=832
  _globals['_CAPTUREAUDIOFRAMEREQUEST']._serialized_end=934
  _globals['_CAPTUREAUDIOFRAMERESPONSE']._serialized_start=936
  _globals['_CAPTUREAUDIOFRAMERESPONSE']._serialized_end=981
  _globals['_CAPTUREAUDIOFRAMECALLBACK']._serialized_start=983
  _globals['_CAPTUREAUDIOFRAMECALLBACK']._serialized_end=1043
  _globals['_CLEARAUDIOBUFFERREQUEST']._serialized_start=1045
  _globals['_CLEARAUDIOBUFFERREQUEST']._serialized_end=1093
  _globals['_CLEARAUDIOBUFFERRESPONSE']._serialized_start=1095
  _globals['_CLEARAUDIOBUFFERRESPONSE']._serialized_end=1121
  _globals['_NEWAUDIORESAMPLERREQUEST']._serialized_start=1123
  _globals['_NEWAUDIORESAMPLERREQUEST']._serialized_end=1149
  _globals['_NEWAUDIORESAMPLERRESPONSE']._serialized_start=1151
  _globals['_NEWAUDIORESAMPLERRESPONSE']._serialized_end=1233
  _globals['_REMIXANDRESAMPLEREQUEST']._serialized_start=1236
  _globals['_REMIXANDRESAMPLEREQUEST']._serialized_end=1383
  _globals['_REMIXANDRESAMPLERESPONSE']._serialized_start=1385
  _globals['_REMIXANDRESAMPLERESPONSE']._serialized_end=1465
  _globals['_NEWSOXRESAMPLERREQUEST']._serialized_start=1468
  _globals['_NEWSOXRESAMPLERREQUEST']._serialized_end=1752
  _globals['_NEWSOXRESAMPLERRESPONSE']._serialized_start=1754
  _globals['_NEWSOXRESAMPLERRESPONSE']._serialized_end=1862
  _globals['_PUSHSOXRESAMPLERREQUEST']._serialized_start=1864
  _globals['_PUSHSOXRESAMPLERREQUEST']._serialized_end=1947
  _globals['_PUSHSOXRESAMPLERRESPONSE']._serialized_start=1949
  _globals['_PUSHSOXRESAMPLERRESPONSE']._serialized_end=2024
  _globals['_FLUSHSOXRESAMPLERREQUEST']._serialized_start=2026
  _globals['_FLUSHSOXRESAMPLERREQUEST']._serialized_end=2078
  _globals['_FLUSHSOXRESAMPLERRESPONSE']._serialized_start=2080
  _globals['_FLUSHSOXRESAMPLERRESPONSE']._serialized_end=2156
  _globals['_AUDIOFRAMEBUFFERINFO']._serialized_start=2158
  _globals['_AUDIOFRAMEBUFFERINFO']._serialized_end=2270
  _globals['_OWNEDAUDIOFRAMEBUFFER']._serialized_start=2272
  _globals['_OWNEDAUDIOFRAMEBUFFER']._serialized_end=2393
  _globals['_AUDIOSTREAMINFO']._serialized_start=2395
  _globals['_AUDIOSTREAMINFO']._serialized_end=2458
  _globals['_OWNEDAUDIOSTREAM']._serialized_start=2460
  _globals['_OWNEDAUDIOSTREAM']._serialized_end=2571
  _globals['_AUDIOSTREAMEVENT']._serialized_start=2574
  _globals['_AUDIOSTREAMEVENT']._serialized_end=2733
  _globals['_AUDIOFRAMERECEIVED']._serialized_start=2735
  _globals['_AUDIOFRAMERECEIVED']._serialized_end=2808
  _globals['_AUDIOSTREAMEOS']._serialized_start=2810
  _globals['_AUDIOSTREAMEOS']._serialized_end=2826
  _globals['_AUDIOSOURCEOPTIONS']._serialized_start=2828
  _globals['_AUDIOSOURCEOPTIONS']._serialized_end=2929
  _globals['_AUDIOSOURCEINFO']._serialized_start=2931
  _globals['_AUDIOSOURCEINFO']._serialized_end=2994
  _globals['_OWNEDAUDIOSOURCE']._serialized_start=2996
  _globals['_OWNEDAUDIOSOURCE']._serialized_end=3107
  _globals['_AUDIORESAMPLERINFO']._serialized_start=3109
  _globals['_AUDIORESAMPLERINFO']._serialized_end=3129
  _globals['_OWNEDAUDIORESAMPLER']._serialized_start=3131
  _globals['_OWNEDAUDIORESAMPLER']._serialized_end=3248
  _globals['_SOXRESAMPLERINFO']._serialized_start=3250
  _globals['_SOXRESAMPLERINFO']._serialized_end=3268
  _globals['_OWNEDSOXRESAMPLER']._serialized_start=3270
  _globals['_OWNEDSOXRESAMPLER']._serialized_end=3383
# @@protoc_insertion_point(module_scope)
