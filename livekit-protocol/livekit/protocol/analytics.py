# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: livekit_analytics.proto
# Protobuf Python Version: 5.27.3
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
    3,
    '',
    'livekit_analytics.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from . import models as _models_
from . import egress as _egress_
from . import ingress as _ingress_


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17livekit_analytics.proto\x12\x07livekit\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x14livekit_models.proto\x1a\x14livekit_egress.proto\x1a\x15livekit_ingress.proto\"T\n\x13\x41nalyticsVideoLayer\x12\r\n\x05layer\x18\x01 \x01(\x05\x12\x0f\n\x07packets\x18\x02 \x01(\r\x12\r\n\x05\x62ytes\x18\x03 \x01(\x04\x12\x0e\n\x06\x66rames\x18\x04 \x01(\r\"\xb5\x03\n\x0f\x41nalyticsStream\x12\x0c\n\x04ssrc\x18\x01 \x01(\r\x12\x17\n\x0fprimary_packets\x18\x02 \x01(\r\x12\x15\n\rprimary_bytes\x18\x03 \x01(\x04\x12\x1a\n\x12retransmit_packets\x18\x04 \x01(\r\x12\x18\n\x10retransmit_bytes\x18\x05 \x01(\x04\x12\x17\n\x0fpadding_packets\x18\x06 \x01(\r\x12\x15\n\rpadding_bytes\x18\x07 \x01(\x04\x12\x14\n\x0cpackets_lost\x18\x08 \x01(\r\x12\x0e\n\x06\x66rames\x18\t \x01(\r\x12\x0b\n\x03rtt\x18\n \x01(\r\x12\x0e\n\x06jitter\x18\x0b \x01(\r\x12\r\n\x05nacks\x18\x0c \x01(\r\x12\x0c\n\x04plis\x18\r \x01(\r\x12\x0c\n\x04\x66irs\x18\x0e \x01(\r\x12\x32\n\x0cvideo_layers\x18\x0f \x03(\x0b\x32\x1c.livekit.AnalyticsVideoLayer\x12.\n\nstart_time\x18\x11 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x12 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xd2\x02\n\rAnalyticsStat\x12\n\n\x02id\x18\x0e \x01(\t\x12\x15\n\ranalytics_key\x18\x01 \x01(\t\x12!\n\x04kind\x18\x02 \x01(\x0e\x32\x13.livekit.StreamType\x12.\n\ntime_stamp\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0c\n\x04node\x18\x04 \x01(\t\x12\x0f\n\x07room_id\x18\x05 \x01(\t\x12\x11\n\troom_name\x18\x06 \x01(\t\x12\x16\n\x0eparticipant_id\x18\x07 \x01(\t\x12\x10\n\x08track_id\x18\x08 \x01(\t\x12\r\n\x05score\x18\t \x01(\x02\x12)\n\x07streams\x18\n \x03(\x0b\x32\x18.livekit.AnalyticsStream\x12\x0c\n\x04mime\x18\x0b \x01(\t\x12\x11\n\tmin_score\x18\x0c \x01(\x02\x12\x14\n\x0cmedian_score\x18\r \x01(\x02\"7\n\x0e\x41nalyticsStats\x12%\n\x05stats\x18\x01 \x03(\x0b\x32\x16.livekit.AnalyticsStat\"\x9a\x02\n\x13\x41nalyticsClientMeta\x12\x0e\n\x06region\x18\x01 \x01(\t\x12\x0c\n\x04node\x18\x02 \x01(\t\x12\x13\n\x0b\x63lient_addr\x18\x03 \x01(\t\x12\x1b\n\x13\x63lient_connect_time\x18\x04 \x01(\r\x12\x17\n\x0f\x63onnection_type\x18\x05 \x01(\t\x12\x32\n\x10reconnect_reason\x18\x06 \x01(\x0e\x32\x18.livekit.ReconnectReason\x12\x15\n\x08geo_hash\x18\x07 \x01(\tH\x00\x88\x01\x01\x12\x14\n\x07\x63ountry\x18\x08 \x01(\tH\x01\x88\x01\x01\x12\x14\n\x07isp_asn\x18\t \x01(\rH\x02\x88\x01\x01\x42\x0b\n\t_geo_hashB\n\n\x08_countryB\n\n\x08_isp_asn\"\xda\x05\n\x0e\x41nalyticsEvent\x12\n\n\x02id\x18\x19 \x01(\t\x12)\n\x04type\x18\x01 \x01(\x0e\x32\x1b.livekit.AnalyticsEventType\x12-\n\ttimestamp\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0f\n\x07room_id\x18\x03 \x01(\t\x12\x1b\n\x04room\x18\x04 \x01(\x0b\x32\r.livekit.Room\x12\x16\n\x0eparticipant_id\x18\x05 \x01(\t\x12-\n\x0bparticipant\x18\x06 \x01(\x0b\x32\x18.livekit.ParticipantInfo\x12\x10\n\x08track_id\x18\x07 \x01(\t\x12!\n\x05track\x18\x08 \x01(\x0b\x32\x12.livekit.TrackInfo\x12\x15\n\ranalytics_key\x18\n \x01(\t\x12(\n\x0b\x63lient_info\x18\x0b \x01(\x0b\x32\x13.livekit.ClientInfo\x12\x31\n\x0b\x63lient_meta\x18\x0c \x01(\x0b\x32\x1c.livekit.AnalyticsClientMeta\x12\x11\n\tegress_id\x18\r \x01(\t\x12\x12\n\ningress_id\x18\x13 \x01(\t\x12;\n\x1cmax_subscribed_video_quality\x18\x0e \x01(\x0e\x32\x15.livekit.VideoQuality\x12+\n\tpublisher\x18\x0f \x01(\x0b\x32\x18.livekit.ParticipantInfo\x12\x0c\n\x04mime\x18\x10 \x01(\t\x12#\n\x06\x65gress\x18\x11 \x01(\x0b\x32\x13.livekit.EgressInfo\x12%\n\x07ingress\x18\x12 \x01(\x0b\x32\x14.livekit.IngressInfo\x12\r\n\x05\x65rror\x18\x14 \x01(\t\x12$\n\trtp_stats\x18\x15 \x01(\x0b\x32\x11.livekit.RTPStats\x12\x13\n\x0bvideo_layer\x18\x16 \x01(\x05\x12\x0f\n\x07node_id\x18\x18 \x01(\t\":\n\x0f\x41nalyticsEvents\x12\'\n\x06\x65vents\x18\x01 \x03(\x0b\x32\x17.livekit.AnalyticsEvent\"\xa4\x01\n\x18\x41nalyticsRoomParticipant\x12\n\n\x02id\x18\x01 \x01(\t\x12\x10\n\x08identity\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12-\n\x05state\x18\x04 \x01(\x0e\x32\x1e.livekit.ParticipantInfo.State\x12-\n\tjoined_at\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xa6\x01\n\rAnalyticsRoom\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nproject_id\x18\x05 \x01(\t\x12.\n\ncreated_at\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x37\n\x0cparticipants\x18\x04 \x03(\x0b\x32!.livekit.AnalyticsRoomParticipant\"\x94\x01\n\x12\x41nalyticsNodeRooms\x12\x0f\n\x07node_id\x18\x01 \x01(\t\x12\x17\n\x0fsequence_number\x18\x02 \x01(\x04\x12-\n\ttimestamp\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12%\n\x05rooms\x18\x04 \x03(\x0b\x32\x16.livekit.AnalyticsRoom**\n\nStreamType\x12\x0c\n\x08UPSTREAM\x10\x00\x12\x0e\n\nDOWNSTREAM\x10\x01*\x95\x05\n\x12\x41nalyticsEventType\x12\x10\n\x0cROOM_CREATED\x10\x00\x12\x0e\n\nROOM_ENDED\x10\x01\x12\x16\n\x12PARTICIPANT_JOINED\x10\x02\x12\x14\n\x10PARTICIPANT_LEFT\x10\x03\x12\x13\n\x0fTRACK_PUBLISHED\x10\x04\x12\x1b\n\x17TRACK_PUBLISH_REQUESTED\x10\x14\x12\x15\n\x11TRACK_UNPUBLISHED\x10\x05\x12\x14\n\x10TRACK_SUBSCRIBED\x10\x06\x12\x1d\n\x19TRACK_SUBSCRIBE_REQUESTED\x10\x15\x12\x1a\n\x16TRACK_SUBSCRIBE_FAILED\x10\x19\x12\x16\n\x12TRACK_UNSUBSCRIBED\x10\x07\x12\x1a\n\x16TRACK_PUBLISHED_UPDATE\x10\n\x12\x0f\n\x0bTRACK_MUTED\x10\x17\x12\x11\n\rTRACK_UNMUTED\x10\x18\x12\x17\n\x13TRACK_PUBLISH_STATS\x10\x1a\x12\x19\n\x15TRACK_SUBSCRIBE_STATS\x10\x1b\x12\x16\n\x12PARTICIPANT_ACTIVE\x10\x0b\x12\x17\n\x13PARTICIPANT_RESUMED\x10\x16\x12\x12\n\x0e\x45GRESS_STARTED\x10\x0c\x12\x10\n\x0c\x45GRESS_ENDED\x10\r\x12\x12\n\x0e\x45GRESS_UPDATED\x10\x1c\x12&\n\"TRACK_MAX_SUBSCRIBED_VIDEO_QUALITY\x10\x0e\x12\x0f\n\x0bRECONNECTED\x10\x0f\x12\x13\n\x0fINGRESS_CREATED\x10\x12\x12\x13\n\x0fINGRESS_DELETED\x10\x13\x12\x13\n\x0fINGRESS_STARTED\x10\x10\x12\x11\n\rINGRESS_ENDED\x10\x11\x12\x13\n\x0fINGRESS_UPDATED\x10\x1d\x42\x46Z#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analytics', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_STREAMTYPE']._serialized_start=2625
  _globals['_STREAMTYPE']._serialized_end=2667
  _globals['_ANALYTICSEVENTTYPE']._serialized_start=2670
  _globals['_ANALYTICSEVENTTYPE']._serialized_end=3331
  _globals['_ANALYTICSVIDEOLAYER']._serialized_start=136
  _globals['_ANALYTICSVIDEOLAYER']._serialized_end=220
  _globals['_ANALYTICSSTREAM']._serialized_start=223
  _globals['_ANALYTICSSTREAM']._serialized_end=660
  _globals['_ANALYTICSSTAT']._serialized_start=663
  _globals['_ANALYTICSSTAT']._serialized_end=1001
  _globals['_ANALYTICSSTATS']._serialized_start=1003
  _globals['_ANALYTICSSTATS']._serialized_end=1058
  _globals['_ANALYTICSCLIENTMETA']._serialized_start=1061
  _globals['_ANALYTICSCLIENTMETA']._serialized_end=1343
  _globals['_ANALYTICSEVENT']._serialized_start=1346
  _globals['_ANALYTICSEVENT']._serialized_end=2076
  _globals['_ANALYTICSEVENTS']._serialized_start=2078
  _globals['_ANALYTICSEVENTS']._serialized_end=2136
  _globals['_ANALYTICSROOMPARTICIPANT']._serialized_start=2139
  _globals['_ANALYTICSROOMPARTICIPANT']._serialized_end=2303
  _globals['_ANALYTICSROOM']._serialized_start=2306
  _globals['_ANALYTICSROOM']._serialized_end=2472
  _globals['_ANALYTICSNODEROOMS']._serialized_start=2475
  _globals['_ANALYTICSNODEROOMS']._serialized_end=2623
# @@protoc_insertion_point(module_scope)
