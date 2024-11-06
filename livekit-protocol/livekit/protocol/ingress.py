# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: livekit_ingress.proto
# Protobuf Python Version: 5.28.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    3,
    '',
    'livekit_ingress.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import models as _models_


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15livekit_ingress.proto\x12\x07livekit\x1a\x14livekit_models.proto\"\xf7\x02\n\x14\x43reateIngressRequest\x12)\n\ninput_type\x18\x01 \x01(\x0e\x32\x15.livekit.IngressInput\x12\x0b\n\x03url\x18\t \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x11\n\troom_name\x18\x03 \x01(\t\x12\x1c\n\x14participant_identity\x18\x04 \x01(\t\x12\x18\n\x10participant_name\x18\x05 \x01(\t\x12\x1c\n\x14participant_metadata\x18\n \x01(\t\x12\x1e\n\x12\x62ypass_transcoding\x18\x08 \x01(\x08\x42\x02\x18\x01\x12\x1f\n\x12\x65nable_transcoding\x18\x0b \x01(\x08H\x00\x88\x01\x01\x12+\n\x05\x61udio\x18\x06 \x01(\x0b\x32\x1c.livekit.IngressAudioOptions\x12+\n\x05video\x18\x07 \x01(\x0b\x32\x1c.livekit.IngressVideoOptionsB\x15\n\x13_enable_transcoding\"\xcd\x01\n\x13IngressAudioOptions\x12\x0c\n\x04name\x18\x01 \x01(\t\x12$\n\x06source\x18\x02 \x01(\x0e\x32\x14.livekit.TrackSource\x12\x35\n\x06preset\x18\x03 \x01(\x0e\x32#.livekit.IngressAudioEncodingPresetH\x00\x12\x37\n\x07options\x18\x04 \x01(\x0b\x32$.livekit.IngressAudioEncodingOptionsH\x00\x42\x12\n\x10\x65ncoding_options\"\xcd\x01\n\x13IngressVideoOptions\x12\x0c\n\x04name\x18\x01 \x01(\t\x12$\n\x06source\x18\x02 \x01(\x0e\x32\x14.livekit.TrackSource\x12\x35\n\x06preset\x18\x03 \x01(\x0e\x32#.livekit.IngressVideoEncodingPresetH\x00\x12\x37\n\x07options\x18\x04 \x01(\x0b\x32$.livekit.IngressVideoEncodingOptionsH\x00\x42\x12\n\x10\x65ncoding_options\"\x7f\n\x1bIngressAudioEncodingOptions\x12(\n\x0b\x61udio_codec\x18\x01 \x01(\x0e\x32\x13.livekit.AudioCodec\x12\x0f\n\x07\x62itrate\x18\x02 \x01(\r\x12\x13\n\x0b\x64isable_dtx\x18\x03 \x01(\x08\x12\x10\n\x08\x63hannels\x18\x04 \x01(\r\"\x80\x01\n\x1bIngressVideoEncodingOptions\x12(\n\x0bvideo_codec\x18\x01 \x01(\x0e\x32\x13.livekit.VideoCodec\x12\x12\n\nframe_rate\x18\x02 \x01(\x01\x12#\n\x06layers\x18\x03 \x03(\x0b\x32\x13.livekit.VideoLayer\"\xce\x03\n\x0bIngressInfo\x12\x12\n\ningress_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nstream_key\x18\x03 \x01(\t\x12\x0b\n\x03url\x18\x04 \x01(\t\x12)\n\ninput_type\x18\x05 \x01(\x0e\x32\x15.livekit.IngressInput\x12\x1e\n\x12\x62ypass_transcoding\x18\r \x01(\x08\x42\x02\x18\x01\x12\x1f\n\x12\x65nable_transcoding\x18\x0f \x01(\x08H\x00\x88\x01\x01\x12+\n\x05\x61udio\x18\x06 \x01(\x0b\x32\x1c.livekit.IngressAudioOptions\x12+\n\x05video\x18\x07 \x01(\x0b\x32\x1c.livekit.IngressVideoOptions\x12\x11\n\troom_name\x18\x08 \x01(\t\x12\x1c\n\x14participant_identity\x18\t \x01(\t\x12\x18\n\x10participant_name\x18\n \x01(\t\x12\x1c\n\x14participant_metadata\x18\x0e \x01(\t\x12\x10\n\x08reusable\x18\x0b \x01(\x08\x12$\n\x05state\x18\x0c \x01(\x0b\x32\x15.livekit.IngressStateB\x15\n\x13_enable_transcoding\"\x9e\x03\n\x0cIngressState\x12,\n\x06status\x18\x01 \x01(\x0e\x32\x1c.livekit.IngressState.Status\x12\r\n\x05\x65rror\x18\x02 \x01(\t\x12\'\n\x05video\x18\x03 \x01(\x0b\x32\x18.livekit.InputVideoState\x12\'\n\x05\x61udio\x18\x04 \x01(\x0b\x32\x18.livekit.InputAudioState\x12\x0f\n\x07room_id\x18\x05 \x01(\t\x12\x12\n\nstarted_at\x18\x07 \x01(\x03\x12\x10\n\x08\x65nded_at\x18\x08 \x01(\x03\x12\x12\n\nupdated_at\x18\n \x01(\x03\x12\x13\n\x0bresource_id\x18\t \x01(\t\x12\"\n\x06tracks\x18\x06 \x03(\x0b\x32\x12.livekit.TrackInfo\"{\n\x06Status\x12\x15\n\x11\x45NDPOINT_INACTIVE\x10\x00\x12\x16\n\x12\x45NDPOINT_BUFFERING\x10\x01\x12\x17\n\x13\x45NDPOINT_PUBLISHING\x10\x02\x12\x12\n\x0e\x45NDPOINT_ERROR\x10\x03\x12\x15\n\x11\x45NDPOINT_COMPLETE\x10\x04\"o\n\x0fInputVideoState\x12\x11\n\tmime_type\x18\x01 \x01(\t\x12\x17\n\x0f\x61verage_bitrate\x18\x02 \x01(\r\x12\r\n\x05width\x18\x03 \x01(\r\x12\x0e\n\x06height\x18\x04 \x01(\r\x12\x11\n\tframerate\x18\x05 \x01(\x01\"d\n\x0fInputAudioState\x12\x11\n\tmime_type\x18\x01 \x01(\t\x12\x17\n\x0f\x61verage_bitrate\x18\x02 \x01(\r\x12\x10\n\x08\x63hannels\x18\x03 \x01(\r\x12\x13\n\x0bsample_rate\x18\x04 \x01(\r\"\xef\x02\n\x14UpdateIngressRequest\x12\x12\n\ningress_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x11\n\troom_name\x18\x03 \x01(\t\x12\x1c\n\x14participant_identity\x18\x04 \x01(\t\x12\x18\n\x10participant_name\x18\x05 \x01(\t\x12\x1c\n\x14participant_metadata\x18\t \x01(\t\x12#\n\x12\x62ypass_transcoding\x18\x08 \x01(\x08\x42\x02\x18\x01H\x00\x88\x01\x01\x12\x1f\n\x12\x65nable_transcoding\x18\n \x01(\x08H\x01\x88\x01\x01\x12+\n\x05\x61udio\x18\x06 \x01(\x0b\x32\x1c.livekit.IngressAudioOptions\x12+\n\x05video\x18\x07 \x01(\x0b\x32\x1c.livekit.IngressVideoOptionsB\x15\n\x13_bypass_transcodingB\x15\n\x13_enable_transcoding\";\n\x12ListIngressRequest\x12\x11\n\troom_name\x18\x01 \x01(\t\x12\x12\n\ningress_id\x18\x02 \x01(\t\":\n\x13ListIngressResponse\x12#\n\x05items\x18\x01 \x03(\x0b\x32\x14.livekit.IngressInfo\"*\n\x14\x44\x65leteIngressRequest\x12\x12\n\ningress_id\x18\x01 \x01(\t*=\n\x0cIngressInput\x12\x0e\n\nRTMP_INPUT\x10\x00\x12\x0e\n\nWHIP_INPUT\x10\x01\x12\r\n\tURL_INPUT\x10\x02*I\n\x1aIngressAudioEncodingPreset\x12\x16\n\x12OPUS_STEREO_96KBPS\x10\x00\x12\x13\n\x0fOPUS_MONO_64KBS\x10\x01*\x84\x03\n\x1aIngressVideoEncodingPreset\x12\x1c\n\x18H264_720P_30FPS_3_LAYERS\x10\x00\x12\x1d\n\x19H264_1080P_30FPS_3_LAYERS\x10\x01\x12\x1c\n\x18H264_540P_25FPS_2_LAYERS\x10\x02\x12\x1b\n\x17H264_720P_30FPS_1_LAYER\x10\x03\x12\x1c\n\x18H264_1080P_30FPS_1_LAYER\x10\x04\x12(\n$H264_720P_30FPS_3_LAYERS_HIGH_MOTION\x10\x05\x12)\n%H264_1080P_30FPS_3_LAYERS_HIGH_MOTION\x10\x06\x12(\n$H264_540P_25FPS_2_LAYERS_HIGH_MOTION\x10\x07\x12\'\n#H264_720P_30FPS_1_LAYER_HIGH_MOTION\x10\x08\x12(\n$H264_1080P_30FPS_1_LAYER_HIGH_MOTION\x10\t2\xa5\x02\n\x07Ingress\x12\x44\n\rCreateIngress\x12\x1d.livekit.CreateIngressRequest\x1a\x14.livekit.IngressInfo\x12\x44\n\rUpdateIngress\x12\x1d.livekit.UpdateIngressRequest\x1a\x14.livekit.IngressInfo\x12H\n\x0bListIngress\x12\x1b.livekit.ListIngressRequest\x1a\x1c.livekit.ListIngressResponse\x12\x44\n\rDeleteIngress\x12\x1d.livekit.DeleteIngressRequest\x1a\x14.livekit.IngressInfoBFZ#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ingress', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_CREATEINGRESSREQUEST'].fields_by_name['bypass_transcoding']._loaded_options = None
  _globals['_CREATEINGRESSREQUEST'].fields_by_name['bypass_transcoding']._serialized_options = b'\030\001'
  _globals['_INGRESSINFO'].fields_by_name['bypass_transcoding']._loaded_options = None
  _globals['_INGRESSINFO'].fields_by_name['bypass_transcoding']._serialized_options = b'\030\001'
  _globals['_UPDATEINGRESSREQUEST'].fields_by_name['bypass_transcoding']._loaded_options = None
  _globals['_UPDATEINGRESSREQUEST'].fields_by_name['bypass_transcoding']._serialized_options = b'\030\001'
  _globals['_INGRESSINPUT']._serialized_start=2742
  _globals['_INGRESSINPUT']._serialized_end=2803
  _globals['_INGRESSAUDIOENCODINGPRESET']._serialized_start=2805
  _globals['_INGRESSAUDIOENCODINGPRESET']._serialized_end=2878
  _globals['_INGRESSVIDEOENCODINGPRESET']._serialized_start=2881
  _globals['_INGRESSVIDEOENCODINGPRESET']._serialized_end=3269
  _globals['_CREATEINGRESSREQUEST']._serialized_start=57
  _globals['_CREATEINGRESSREQUEST']._serialized_end=432
  _globals['_INGRESSAUDIOOPTIONS']._serialized_start=435
  _globals['_INGRESSAUDIOOPTIONS']._serialized_end=640
  _globals['_INGRESSVIDEOOPTIONS']._serialized_start=643
  _globals['_INGRESSVIDEOOPTIONS']._serialized_end=848
  _globals['_INGRESSAUDIOENCODINGOPTIONS']._serialized_start=850
  _globals['_INGRESSAUDIOENCODINGOPTIONS']._serialized_end=977
  _globals['_INGRESSVIDEOENCODINGOPTIONS']._serialized_start=980
  _globals['_INGRESSVIDEOENCODINGOPTIONS']._serialized_end=1108
  _globals['_INGRESSINFO']._serialized_start=1111
  _globals['_INGRESSINFO']._serialized_end=1573
  _globals['_INGRESSSTATE']._serialized_start=1576
  _globals['_INGRESSSTATE']._serialized_end=1990
  _globals['_INGRESSSTATE_STATUS']._serialized_start=1867
  _globals['_INGRESSSTATE_STATUS']._serialized_end=1990
  _globals['_INPUTVIDEOSTATE']._serialized_start=1992
  _globals['_INPUTVIDEOSTATE']._serialized_end=2103
  _globals['_INPUTAUDIOSTATE']._serialized_start=2105
  _globals['_INPUTAUDIOSTATE']._serialized_end=2205
  _globals['_UPDATEINGRESSREQUEST']._serialized_start=2208
  _globals['_UPDATEINGRESSREQUEST']._serialized_end=2575
  _globals['_LISTINGRESSREQUEST']._serialized_start=2577
  _globals['_LISTINGRESSREQUEST']._serialized_end=2636
  _globals['_LISTINGRESSRESPONSE']._serialized_start=2638
  _globals['_LISTINGRESSRESPONSE']._serialized_end=2696
  _globals['_DELETEINGRESSREQUEST']._serialized_start=2698
  _globals['_DELETEINGRESSREQUEST']._serialized_end=2740
  _globals['_INGRESS']._serialized_start=3272
  _globals['_INGRESS']._serialized_end=3565
# @@protoc_insertion_point(module_scope)
