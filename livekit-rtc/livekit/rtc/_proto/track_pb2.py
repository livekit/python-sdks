# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: track.proto
# Protobuf Python Version: 5.29.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    2,
    '',
    'track.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import e2ee_pb2 as e2ee__pb2
from . import handle_pb2 as handle__pb2
from . import stats_pb2 as stats__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0btrack.proto\x12\rlivekit.proto\x1a\ne2ee.proto\x1a\x0chandle.proto\x1a\x0bstats.proto\">\n\x17\x43reateVideoTrackRequest\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x15\n\rsource_handle\x18\x02 \x02(\x04\"D\n\x18\x43reateVideoTrackResponse\x12(\n\x05track\x18\x01 \x02(\x0b\x32\x19.livekit.proto.OwnedTrack\">\n\x17\x43reateAudioTrackRequest\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x15\n\rsource_handle\x18\x02 \x02(\x04\"D\n\x18\x43reateAudioTrackResponse\x12(\n\x05track\x18\x01 \x02(\x0b\x32\x19.livekit.proto.OwnedTrack\"\'\n\x0fGetStatsRequest\x12\x14\n\x0ctrack_handle\x18\x01 \x02(\x04\"$\n\x10GetStatsResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"[\n\x10GetStatsCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\x12&\n\x05stats\x18\x03 \x03(\x0b\x32\x17.livekit.proto.RtcStats\"\x0c\n\nTrackEvent\"\xa3\x02\n\x14TrackPublicationInfo\x12\x0b\n\x03sid\x18\x01 \x02(\t\x12\x0c\n\x04name\x18\x02 \x02(\t\x12&\n\x04kind\x18\x03 \x02(\x0e\x32\x18.livekit.proto.TrackKind\x12*\n\x06source\x18\x04 \x02(\x0e\x32\x1a.livekit.proto.TrackSource\x12\x13\n\x0bsimulcasted\x18\x05 \x02(\x08\x12\r\n\x05width\x18\x06 \x02(\r\x12\x0e\n\x06height\x18\x07 \x02(\r\x12\x11\n\tmime_type\x18\x08 \x02(\t\x12\r\n\x05muted\x18\t \x02(\x08\x12\x0e\n\x06remote\x18\n \x02(\x08\x12\x36\n\x0f\x65ncryption_type\x18\x0b \x02(\x0e\x32\x1d.livekit.proto.EncryptionType\"y\n\x15OwnedTrackPublication\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12\x31\n\x04info\x18\x02 \x02(\x0b\x32#.livekit.proto.TrackPublicationInfo\"\x9f\x01\n\tTrackInfo\x12\x0b\n\x03sid\x18\x01 \x02(\t\x12\x0c\n\x04name\x18\x02 \x02(\t\x12&\n\x04kind\x18\x03 \x02(\x0e\x32\x18.livekit.proto.TrackKind\x12\x30\n\x0cstream_state\x18\x04 \x02(\x0e\x32\x1a.livekit.proto.StreamState\x12\r\n\x05muted\x18\x05 \x02(\x08\x12\x0e\n\x06remote\x18\x06 \x02(\x08\"c\n\nOwnedTrack\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12&\n\x04info\x18\x02 \x02(\x0b\x32\x18.livekit.proto.TrackInfo\";\n\x15LocalTrackMuteRequest\x12\x14\n\x0ctrack_handle\x18\x01 \x02(\x04\x12\x0c\n\x04mute\x18\x02 \x02(\x08\"\'\n\x16LocalTrackMuteResponse\x12\r\n\x05muted\x18\x01 \x02(\x08\"A\n\x18\x45nableRemoteTrackRequest\x12\x14\n\x0ctrack_handle\x18\x01 \x02(\x04\x12\x0f\n\x07\x65nabled\x18\x02 \x02(\x08\",\n\x19\x45nableRemoteTrackResponse\x12\x0f\n\x07\x65nabled\x18\x01 \x02(\x08\"\xac\x01\n&SetTrackSubscriptionPermissionsRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12 \n\x18\x61ll_participants_allowed\x18\x02 \x02(\x08\x12>\n\x0bpermissions\x18\x03 \x03(\x0b\x32).livekit.proto.ParticipantTrackPermission\"i\n\x1aParticipantTrackPermission\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x11\n\tallow_all\x18\x02 \x01(\x08\x12\x1a\n\x12\x61llowed_track_sids\x18\x03 \x03(\t\")\n\'SetTrackSubscriptionPermissionsResponse*=\n\tTrackKind\x12\x10\n\x0cKIND_UNKNOWN\x10\x00\x12\x0e\n\nKIND_AUDIO\x10\x01\x12\x0e\n\nKIND_VIDEO\x10\x02*\x81\x01\n\x0bTrackSource\x12\x12\n\x0eSOURCE_UNKNOWN\x10\x00\x12\x11\n\rSOURCE_CAMERA\x10\x01\x12\x15\n\x11SOURCE_MICROPHONE\x10\x02\x12\x16\n\x12SOURCE_SCREENSHARE\x10\x03\x12\x1c\n\x18SOURCE_SCREENSHARE_AUDIO\x10\x04*D\n\x0bStreamState\x12\x11\n\rSTATE_UNKNOWN\x10\x00\x12\x10\n\x0cSTATE_ACTIVE\x10\x01\x12\x10\n\x0cSTATE_PAUSED\x10\x02\x42\x10\xaa\x02\rLiveKit.Proto')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'track_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\rLiveKit.Proto'
  _globals['_TRACKKIND']._serialized_start=1743
  _globals['_TRACKKIND']._serialized_end=1804
  _globals['_TRACKSOURCE']._serialized_start=1807
  _globals['_TRACKSOURCE']._serialized_end=1936
  _globals['_STREAMSTATE']._serialized_start=1938
  _globals['_STREAMSTATE']._serialized_end=2006
  _globals['_CREATEVIDEOTRACKREQUEST']._serialized_start=69
  _globals['_CREATEVIDEOTRACKREQUEST']._serialized_end=131
  _globals['_CREATEVIDEOTRACKRESPONSE']._serialized_start=133
  _globals['_CREATEVIDEOTRACKRESPONSE']._serialized_end=201
  _globals['_CREATEAUDIOTRACKREQUEST']._serialized_start=203
  _globals['_CREATEAUDIOTRACKREQUEST']._serialized_end=265
  _globals['_CREATEAUDIOTRACKRESPONSE']._serialized_start=267
  _globals['_CREATEAUDIOTRACKRESPONSE']._serialized_end=335
  _globals['_GETSTATSREQUEST']._serialized_start=337
  _globals['_GETSTATSREQUEST']._serialized_end=376
  _globals['_GETSTATSRESPONSE']._serialized_start=378
  _globals['_GETSTATSRESPONSE']._serialized_end=414
  _globals['_GETSTATSCALLBACK']._serialized_start=416
  _globals['_GETSTATSCALLBACK']._serialized_end=507
  _globals['_TRACKEVENT']._serialized_start=509
  _globals['_TRACKEVENT']._serialized_end=521
  _globals['_TRACKPUBLICATIONINFO']._serialized_start=524
  _globals['_TRACKPUBLICATIONINFO']._serialized_end=815
  _globals['_OWNEDTRACKPUBLICATION']._serialized_start=817
  _globals['_OWNEDTRACKPUBLICATION']._serialized_end=938
  _globals['_TRACKINFO']._serialized_start=941
  _globals['_TRACKINFO']._serialized_end=1100
  _globals['_OWNEDTRACK']._serialized_start=1102
  _globals['_OWNEDTRACK']._serialized_end=1201
  _globals['_LOCALTRACKMUTEREQUEST']._serialized_start=1203
  _globals['_LOCALTRACKMUTEREQUEST']._serialized_end=1262
  _globals['_LOCALTRACKMUTERESPONSE']._serialized_start=1264
  _globals['_LOCALTRACKMUTERESPONSE']._serialized_end=1303
  _globals['_ENABLEREMOTETRACKREQUEST']._serialized_start=1305
  _globals['_ENABLEREMOTETRACKREQUEST']._serialized_end=1370
  _globals['_ENABLEREMOTETRACKRESPONSE']._serialized_start=1372
  _globals['_ENABLEREMOTETRACKRESPONSE']._serialized_end=1416
  _globals['_SETTRACKSUBSCRIPTIONPERMISSIONSREQUEST']._serialized_start=1419
  _globals['_SETTRACKSUBSCRIPTIONPERMISSIONSREQUEST']._serialized_end=1591
  _globals['_PARTICIPANTTRACKPERMISSION']._serialized_start=1593
  _globals['_PARTICIPANTTRACKPERMISSION']._serialized_end=1698
  _globals['_SETTRACKSUBSCRIPTIONPERMISSIONSRESPONSE']._serialized_start=1700
  _globals['_SETTRACKSUBSCRIPTIONPERMISSIONSRESPONSE']._serialized_end=1741
# @@protoc_insertion_point(module_scope)
