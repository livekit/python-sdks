# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: room.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import e2ee_pb2 as e2ee__pb2
from . import handle_pb2 as handle__pb2
from . import participant_pb2 as participant__pb2
from . import track_pb2 as track__pb2
from . import video_frame_pb2 as video__frame__pb2
from . import stats_pb2 as stats__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nroom.proto\x12\rlivekit.proto\x1a\ne2ee.proto\x1a\x0chandle.proto\x1a\x11participant.proto\x1a\x0btrack.proto\x1a\x11video_frame.proto\x1a\x0bstats.proto\"Y\n\x0e\x43onnectRequest\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\r\n\x05token\x18\x02 \x01(\t\x12+\n\x07options\x18\x03 \x01(\x0b\x32\x1a.livekit.proto.RoomOptions\"#\n\x0f\x43onnectResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"\xfd\x02\n\x0f\x43onnectCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\x12\x12\n\x05\x65rror\x18\x02 \x01(\tH\x00\x88\x01\x01\x12&\n\x04room\x18\x03 \x01(\x0b\x32\x18.livekit.proto.OwnedRoom\x12:\n\x11local_participant\x18\x04 \x01(\x0b\x32\x1f.livekit.proto.OwnedParticipant\x12J\n\x0cparticipants\x18\x05 \x03(\x0b\x32\x34.livekit.proto.ConnectCallback.ParticipantWithTracks\x1a\x89\x01\n\x15ParticipantWithTracks\x12\x34\n\x0bparticipant\x18\x01 \x01(\x0b\x32\x1f.livekit.proto.OwnedParticipant\x12:\n\x0cpublications\x18\x02 \x03(\x0b\x32$.livekit.proto.OwnedTrackPublicationB\x08\n\x06_error\"(\n\x11\x44isconnectRequest\x12\x13\n\x0broom_handle\x18\x01 \x01(\x04\"&\n\x12\x44isconnectResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"&\n\x12\x44isconnectCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"\x82\x01\n\x13PublishTrackRequest\x12 \n\x18local_participant_handle\x18\x01 \x01(\x04\x12\x14\n\x0ctrack_handle\x18\x02 \x01(\x04\x12\x33\n\x07options\x18\x03 \x01(\x0b\x32\".livekit.proto.TrackPublishOptions\"(\n\x14PublishTrackResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"\x81\x01\n\x14PublishTrackCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\x12\x12\n\x05\x65rror\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x39\n\x0bpublication\x18\x03 \x01(\x0b\x32$.livekit.proto.OwnedTrackPublicationB\x08\n\x06_error\"g\n\x15UnpublishTrackRequest\x12 \n\x18local_participant_handle\x18\x01 \x01(\x04\x12\x11\n\ttrack_sid\x18\x02 \x01(\t\x12\x19\n\x11stop_on_unpublish\x18\x03 \x01(\x08\"*\n\x16UnpublishTrackResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"H\n\x16UnpublishTrackCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\x12\x12\n\x05\x65rror\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x08\n\x06_error\"\xc8\x01\n\x12PublishDataRequest\x12 \n\x18local_participant_handle\x18\x01 \x01(\x04\x12\x10\n\x08\x64\x61ta_ptr\x18\x02 \x01(\x04\x12\x10\n\x08\x64\x61ta_len\x18\x03 \x01(\x04\x12\x10\n\x08reliable\x18\x04 \x01(\x08\x12\x1c\n\x10\x64\x65stination_sids\x18\x05 \x03(\tB\x02\x18\x01\x12\x12\n\x05topic\x18\x06 \x01(\tH\x00\x88\x01\x01\x12\x1e\n\x16\x64\x65stination_identities\x18\x07 \x03(\tB\x08\n\x06_topic\"\'\n\x13PublishDataResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"E\n\x13PublishDataCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\x12\x12\n\x05\x65rror\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x08\n\x06_error\"\xa6\x01\n\x1bPublishTranscriptionRequest\x12 \n\x18local_participant_handle\x18\x01 \x01(\x04\x12\x1c\n\x14participant_identity\x18\x02 \x01(\t\x12\x10\n\x08track_id\x18\x03 \x01(\t\x12\x35\n\x08segments\x18\x04 \x03(\x0b\x32#.livekit.proto.TranscriptionSegment\"0\n\x1cPublishTranscriptionResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"N\n\x1cPublishTranscriptionCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\x12\x12\n\x05\x65rror\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x08\n\x06_error\"P\n\x1aUpdateLocalMetadataRequest\x12 \n\x18local_participant_handle\x18\x01 \x01(\x04\x12\x10\n\x08metadata\x18\x02 \x01(\t\"/\n\x1bUpdateLocalMetadataResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"/\n\x1bUpdateLocalMetadataCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"H\n\x16UpdateLocalNameRequest\x12 \n\x18local_participant_handle\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\"+\n\x17UpdateLocalNameResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"+\n\x17UpdateLocalNameCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"E\n\x14SetSubscribedRequest\x12\x11\n\tsubscribe\x18\x01 \x01(\x08\x12\x1a\n\x12publication_handle\x18\x02 \x01(\x04\"\x17\n\x15SetSubscribedResponse\"-\n\x16GetSessionStatsRequest\x12\x13\n\x0broom_handle\x18\x01 \x01(\x04\"+\n\x17GetSessionStatsResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\"\xae\x01\n\x17GetSessionStatsCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x01(\x04\x12\x12\n\x05\x65rror\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x30\n\x0fpublisher_stats\x18\x03 \x03(\x0b\x32\x17.livekit.proto.RtcStats\x12\x31\n\x10subscriber_stats\x18\x04 \x03(\x0b\x32\x17.livekit.proto.RtcStatsB\x08\n\x06_error\";\n\rVideoEncoding\x12\x13\n\x0bmax_bitrate\x18\x01 \x01(\x04\x12\x15\n\rmax_framerate\x18\x02 \x01(\x01\"$\n\rAudioEncoding\x12\x13\n\x0bmax_bitrate\x18\x01 \x01(\x04\"\x8a\x02\n\x13TrackPublishOptions\x12\x34\n\x0evideo_encoding\x18\x01 \x01(\x0b\x32\x1c.livekit.proto.VideoEncoding\x12\x34\n\x0e\x61udio_encoding\x18\x02 \x01(\x0b\x32\x1c.livekit.proto.AudioEncoding\x12.\n\x0bvideo_codec\x18\x03 \x01(\x0e\x32\x19.livekit.proto.VideoCodec\x12\x0b\n\x03\x64tx\x18\x04 \x01(\x08\x12\x0b\n\x03red\x18\x05 \x01(\x08\x12\x11\n\tsimulcast\x18\x06 \x01(\x08\x12*\n\x06source\x18\x07 \x01(\x0e\x32\x1a.livekit.proto.TrackSource\"=\n\tIceServer\x12\x0c\n\x04urls\x18\x01 \x03(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\"\x84\x02\n\tRtcConfig\x12@\n\x12ice_transport_type\x18\x01 \x01(\x0e\x32\x1f.livekit.proto.IceTransportTypeH\x00\x88\x01\x01\x12P\n\x1a\x63ontinual_gathering_policy\x18\x02 \x01(\x0e\x32\'.livekit.proto.ContinualGatheringPolicyH\x01\x88\x01\x01\x12-\n\x0bice_servers\x18\x03 \x03(\x0b\x32\x18.livekit.proto.IceServerB\x15\n\x13_ice_transport_typeB\x1d\n\x1b_continual_gathering_policy\"\xe0\x01\n\x0bRoomOptions\x12\x16\n\x0e\x61uto_subscribe\x18\x01 \x01(\x08\x12\x17\n\x0f\x61\x64\x61ptive_stream\x18\x02 \x01(\x08\x12\x10\n\x08\x64ynacast\x18\x03 \x01(\x08\x12-\n\x04\x65\x32\x65\x65\x18\x04 \x01(\x0b\x32\x1a.livekit.proto.E2eeOptionsH\x00\x88\x01\x01\x12\x31\n\nrtc_config\x18\x05 \x01(\x0b\x32\x18.livekit.proto.RtcConfigH\x01\x88\x01\x01\x12\x14\n\x0cjoin_retries\x18\x06 \x01(\rB\x07\n\x05_e2eeB\r\n\x0b_rtc_config\"w\n\x14TranscriptionSegment\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x12\n\nstart_time\x18\x03 \x01(\x04\x12\x10\n\x08\x65nd_time\x18\x04 \x01(\x04\x12\r\n\x05\x66inal\x18\x05 \x01(\x08\x12\x10\n\x08language\x18\x06 \x01(\t\"0\n\nBufferInfo\x12\x10\n\x08\x64\x61ta_ptr\x18\x01 \x01(\x04\x12\x10\n\x08\x64\x61ta_len\x18\x02 \x01(\x04\"e\n\x0bOwnedBuffer\x12-\n\x06handle\x18\x01 \x01(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12\'\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x19.livekit.proto.BufferInfo\"\xbb\x0c\n\tRoomEvent\x12\x13\n\x0broom_handle\x18\x01 \x01(\x04\x12\x44\n\x15participant_connected\x18\x02 \x01(\x0b\x32#.livekit.proto.ParticipantConnectedH\x00\x12J\n\x18participant_disconnected\x18\x03 \x01(\x0b\x32&.livekit.proto.ParticipantDisconnectedH\x00\x12\x43\n\x15local_track_published\x18\x04 \x01(\x0b\x32\".livekit.proto.LocalTrackPublishedH\x00\x12G\n\x17local_track_unpublished\x18\x05 \x01(\x0b\x32$.livekit.proto.LocalTrackUnpublishedH\x00\x12\x38\n\x0ftrack_published\x18\x06 \x01(\x0b\x32\x1d.livekit.proto.TrackPublishedH\x00\x12<\n\x11track_unpublished\x18\x07 \x01(\x0b\x32\x1f.livekit.proto.TrackUnpublishedH\x00\x12:\n\x10track_subscribed\x18\x08 \x01(\x0b\x32\x1e.livekit.proto.TrackSubscribedH\x00\x12>\n\x12track_unsubscribed\x18\t \x01(\x0b\x32 .livekit.proto.TrackUnsubscribedH\x00\x12K\n\x19track_subscription_failed\x18\n \x01(\x0b\x32&.livekit.proto.TrackSubscriptionFailedH\x00\x12\x30\n\x0btrack_muted\x18\x0b \x01(\x0b\x32\x19.livekit.proto.TrackMutedH\x00\x12\x34\n\rtrack_unmuted\x18\x0c \x01(\x0b\x32\x1b.livekit.proto.TrackUnmutedH\x00\x12G\n\x17\x61\x63tive_speakers_changed\x18\r \x01(\x0b\x32$.livekit.proto.ActiveSpeakersChangedH\x00\x12\x43\n\x15room_metadata_changed\x18\x0e \x01(\x0b\x32\".livekit.proto.RoomMetadataChangedH\x00\x12\x39\n\x10room_sid_changed\x18\x0f \x01(\x0b\x32\x1d.livekit.proto.RoomSidChangedH\x00\x12Q\n\x1cparticipant_metadata_changed\x18\x10 \x01(\x0b\x32).livekit.proto.ParticipantMetadataChangedH\x00\x12I\n\x18participant_name_changed\x18\x11 \x01(\x0b\x32%.livekit.proto.ParticipantNameChangedH\x00\x12M\n\x1a\x63onnection_quality_changed\x18\x12 \x01(\x0b\x32\'.livekit.proto.ConnectionQualityChangedH\x00\x12I\n\x18\x63onnection_state_changed\x18\x13 \x01(\x0b\x32%.livekit.proto.ConnectionStateChangedH\x00\x12\x33\n\x0c\x64isconnected\x18\x15 \x01(\x0b\x32\x1b.livekit.proto.DisconnectedH\x00\x12\x33\n\x0creconnecting\x18\x16 \x01(\x0b\x32\x1b.livekit.proto.ReconnectingH\x00\x12\x31\n\x0breconnected\x18\x17 \x01(\x0b\x32\x1a.livekit.proto.ReconnectedH\x00\x12=\n\x12\x65\x32\x65\x65_state_changed\x18\x18 \x01(\x0b\x32\x1f.livekit.proto.E2eeStateChangedH\x00\x12%\n\x03\x65os\x18\x19 \x01(\x0b\x32\x16.livekit.proto.RoomEOSH\x00\x12\x41\n\x14\x64\x61ta_packet_received\x18\x1a \x01(\x0b\x32!.livekit.proto.DataPacketReceivedH\x00\x42\t\n\x07message\"7\n\x08RoomInfo\x12\x0b\n\x03sid\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t\"a\n\tOwnedRoom\x12-\n\x06handle\x18\x01 \x01(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12%\n\x04info\x18\x02 \x01(\x0b\x32\x17.livekit.proto.RoomInfo\"E\n\x14ParticipantConnected\x12-\n\x04info\x18\x01 \x01(\x0b\x32\x1f.livekit.proto.OwnedParticipant\"2\n\x17ParticipantDisconnected\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\"(\n\x13LocalTrackPublished\x12\x11\n\ttrack_sid\x18\x01 \x01(\t\"0\n\x15LocalTrackUnpublished\x12\x17\n\x0fpublication_sid\x18\x01 \x01(\t\"d\n\x0eTrackPublished\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x39\n\x0bpublication\x18\x02 \x01(\x0b\x32$.livekit.proto.OwnedTrackPublication\"D\n\x10TrackUnpublished\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x17\n\x0fpublication_sid\x18\x02 \x01(\t\"T\n\x0fTrackSubscribed\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12(\n\x05track\x18\x02 \x01(\x0b\x32\x19.livekit.proto.OwnedTrack\"?\n\x11TrackUnsubscribed\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x11\n\ttrack_sid\x18\x02 \x01(\t\"T\n\x17TrackSubscriptionFailed\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x11\n\ttrack_sid\x18\x02 \x01(\t\x12\r\n\x05\x65rror\x18\x03 \x01(\t\"8\n\nTrackMuted\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x11\n\ttrack_sid\x18\x02 \x01(\t\":\n\x0cTrackUnmuted\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x11\n\ttrack_sid\x18\x02 \x01(\t\"Z\n\x10\x45\x32\x65\x65StateChanged\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12-\n\x05state\x18\x02 \x01(\x0e\x32\x1e.livekit.proto.EncryptionState\"1\n\x15\x41\x63tiveSpeakersChanged\x12\x18\n\x10participant_sids\x18\x01 \x03(\t\"\'\n\x13RoomMetadataChanged\x12\x10\n\x08metadata\x18\x01 \x01(\t\"\x1d\n\x0eRoomSidChanged\x12\x0b\n\x03sid\x18\x01 \x01(\t\"G\n\x1aParticipantMetadataChanged\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x10\n\x08metadata\x18\x02 \x01(\t\"?\n\x16ParticipantNameChanged\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"f\n\x18\x43onnectionQualityChanged\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x31\n\x07quality\x18\x02 \x01(\x0e\x32 .livekit.proto.ConnectionQuality\"T\n\nUserPacket\x12(\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x1a.livekit.proto.OwnedBuffer\x12\x12\n\x05topic\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x08\n\x06_topic\"5\n\x07SipDTMF\x12\x0c\n\x04\x63ode\x18\x01 \x01(\r\x12\x12\n\x05\x64igit\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x08\n\x06_digit\"\xf5\x01\n\x12\x44\x61taPacketReceived\x12+\n\x04kind\x18\x01 \x01(\x0e\x32\x1d.livekit.proto.DataPacketKind\x12\x1c\n\x14participant_identity\x18\x02 \x01(\t\x12 \n\x0fparticipant_sid\x18\x03 \x01(\tB\x02\x18\x01H\x01\x88\x01\x01\x12)\n\x04user\x18\x04 \x01(\x0b\x32\x19.livekit.proto.UserPacketH\x00\x12*\n\x08sip_dtmf\x18\x05 \x01(\x0b\x32\x16.livekit.proto.SipDTMFH\x00\x42\x07\n\x05valueB\x12\n\x10_participant_sid\"G\n\x16\x43onnectionStateChanged\x12-\n\x05state\x18\x01 \x01(\x0e\x32\x1e.livekit.proto.ConnectionState\"\x0b\n\tConnected\"\x0e\n\x0c\x44isconnected\"\x0e\n\x0cReconnecting\"\r\n\x0bReconnected\"\t\n\x07RoomEOS*P\n\x10IceTransportType\x12\x13\n\x0fTRANSPORT_RELAY\x10\x00\x12\x14\n\x10TRANSPORT_NOHOST\x10\x01\x12\x11\n\rTRANSPORT_ALL\x10\x02*C\n\x18\x43ontinualGatheringPolicy\x12\x0f\n\x0bGATHER_ONCE\x10\x00\x12\x16\n\x12GATHER_CONTINUALLY\x10\x01*`\n\x11\x43onnectionQuality\x12\x10\n\x0cQUALITY_POOR\x10\x00\x12\x10\n\x0cQUALITY_GOOD\x10\x01\x12\x15\n\x11QUALITY_EXCELLENT\x10\x02\x12\x10\n\x0cQUALITY_LOST\x10\x03*S\n\x0f\x43onnectionState\x12\x15\n\x11\x43ONN_DISCONNECTED\x10\x00\x12\x12\n\x0e\x43ONN_CONNECTED\x10\x01\x12\x15\n\x11\x43ONN_RECONNECTING\x10\x02*3\n\x0e\x44\x61taPacketKind\x12\x0e\n\nKIND_LOSSY\x10\x00\x12\x11\n\rKIND_RELIABLE\x10\x01\x42\x10\xaa\x02\rLiveKit.Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'room_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\rLiveKit.Proto'
  _globals['_PUBLISHDATAREQUEST'].fields_by_name['destination_sids']._options = None
  _globals['_PUBLISHDATAREQUEST'].fields_by_name['destination_sids']._serialized_options = b'\030\001'
  _globals['_DATAPACKETRECEIVED'].fields_by_name['participant_sid']._options = None
  _globals['_DATAPACKETRECEIVED'].fields_by_name['participant_sid']._serialized_options = b'\030\001'
  _globals['_ICETRANSPORTTYPE']._serialized_start=7287
  _globals['_ICETRANSPORTTYPE']._serialized_end=7367
  _globals['_CONTINUALGATHERINGPOLICY']._serialized_start=7369
  _globals['_CONTINUALGATHERINGPOLICY']._serialized_end=7436
  _globals['_CONNECTIONQUALITY']._serialized_start=7438
  _globals['_CONNECTIONQUALITY']._serialized_end=7534
  _globals['_CONNECTIONSTATE']._serialized_start=7536
  _globals['_CONNECTIONSTATE']._serialized_end=7619
  _globals['_DATAPACKETKIND']._serialized_start=7621
  _globals['_DATAPACKETKIND']._serialized_end=7672
  _globals['_CONNECTREQUEST']._serialized_start=119
  _globals['_CONNECTREQUEST']._serialized_end=208
  _globals['_CONNECTRESPONSE']._serialized_start=210
  _globals['_CONNECTRESPONSE']._serialized_end=245
  _globals['_CONNECTCALLBACK']._serialized_start=248
  _globals['_CONNECTCALLBACK']._serialized_end=629
  _globals['_CONNECTCALLBACK_PARTICIPANTWITHTRACKS']._serialized_start=482
  _globals['_CONNECTCALLBACK_PARTICIPANTWITHTRACKS']._serialized_end=619
  _globals['_DISCONNECTREQUEST']._serialized_start=631
  _globals['_DISCONNECTREQUEST']._serialized_end=671
  _globals['_DISCONNECTRESPONSE']._serialized_start=673
  _globals['_DISCONNECTRESPONSE']._serialized_end=711
  _globals['_DISCONNECTCALLBACK']._serialized_start=713
  _globals['_DISCONNECTCALLBACK']._serialized_end=751
  _globals['_PUBLISHTRACKREQUEST']._serialized_start=754
  _globals['_PUBLISHTRACKREQUEST']._serialized_end=884
  _globals['_PUBLISHTRACKRESPONSE']._serialized_start=886
  _globals['_PUBLISHTRACKRESPONSE']._serialized_end=926
  _globals['_PUBLISHTRACKCALLBACK']._serialized_start=929
  _globals['_PUBLISHTRACKCALLBACK']._serialized_end=1058
  _globals['_UNPUBLISHTRACKREQUEST']._serialized_start=1060
  _globals['_UNPUBLISHTRACKREQUEST']._serialized_end=1163
  _globals['_UNPUBLISHTRACKRESPONSE']._serialized_start=1165
  _globals['_UNPUBLISHTRACKRESPONSE']._serialized_end=1207
  _globals['_UNPUBLISHTRACKCALLBACK']._serialized_start=1209
  _globals['_UNPUBLISHTRACKCALLBACK']._serialized_end=1281
  _globals['_PUBLISHDATAREQUEST']._serialized_start=1284
  _globals['_PUBLISHDATAREQUEST']._serialized_end=1484
  _globals['_PUBLISHDATARESPONSE']._serialized_start=1486
  _globals['_PUBLISHDATARESPONSE']._serialized_end=1525
  _globals['_PUBLISHDATACALLBACK']._serialized_start=1527
  _globals['_PUBLISHDATACALLBACK']._serialized_end=1596
  _globals['_PUBLISHTRANSCRIPTIONREQUEST']._serialized_start=1599
  _globals['_PUBLISHTRANSCRIPTIONREQUEST']._serialized_end=1765
  _globals['_PUBLISHTRANSCRIPTIONRESPONSE']._serialized_start=1767
  _globals['_PUBLISHTRANSCRIPTIONRESPONSE']._serialized_end=1815
  _globals['_PUBLISHTRANSCRIPTIONCALLBACK']._serialized_start=1817
  _globals['_PUBLISHTRANSCRIPTIONCALLBACK']._serialized_end=1895
  _globals['_UPDATELOCALMETADATAREQUEST']._serialized_start=1897
  _globals['_UPDATELOCALMETADATAREQUEST']._serialized_end=1977
  _globals['_UPDATELOCALMETADATARESPONSE']._serialized_start=1979
  _globals['_UPDATELOCALMETADATARESPONSE']._serialized_end=2026
  _globals['_UPDATELOCALMETADATACALLBACK']._serialized_start=2028
  _globals['_UPDATELOCALMETADATACALLBACK']._serialized_end=2075
  _globals['_UPDATELOCALNAMEREQUEST']._serialized_start=2077
  _globals['_UPDATELOCALNAMEREQUEST']._serialized_end=2149
  _globals['_UPDATELOCALNAMERESPONSE']._serialized_start=2151
  _globals['_UPDATELOCALNAMERESPONSE']._serialized_end=2194
  _globals['_UPDATELOCALNAMECALLBACK']._serialized_start=2196
  _globals['_UPDATELOCALNAMECALLBACK']._serialized_end=2239
  _globals['_SETSUBSCRIBEDREQUEST']._serialized_start=2241
  _globals['_SETSUBSCRIBEDREQUEST']._serialized_end=2310
  _globals['_SETSUBSCRIBEDRESPONSE']._serialized_start=2312
  _globals['_SETSUBSCRIBEDRESPONSE']._serialized_end=2335
  _globals['_GETSESSIONSTATSREQUEST']._serialized_start=2337
  _globals['_GETSESSIONSTATSREQUEST']._serialized_end=2382
  _globals['_GETSESSIONSTATSRESPONSE']._serialized_start=2384
  _globals['_GETSESSIONSTATSRESPONSE']._serialized_end=2427
  _globals['_GETSESSIONSTATSCALLBACK']._serialized_start=2430
  _globals['_GETSESSIONSTATSCALLBACK']._serialized_end=2604
  _globals['_VIDEOENCODING']._serialized_start=2606
  _globals['_VIDEOENCODING']._serialized_end=2665
  _globals['_AUDIOENCODING']._serialized_start=2667
  _globals['_AUDIOENCODING']._serialized_end=2703
  _globals['_TRACKPUBLISHOPTIONS']._serialized_start=2706
  _globals['_TRACKPUBLISHOPTIONS']._serialized_end=2972
  _globals['_ICESERVER']._serialized_start=2974
  _globals['_ICESERVER']._serialized_end=3035
  _globals['_RTCCONFIG']._serialized_start=3038
  _globals['_RTCCONFIG']._serialized_end=3298
  _globals['_ROOMOPTIONS']._serialized_start=3301
  _globals['_ROOMOPTIONS']._serialized_end=3525
  _globals['_TRANSCRIPTIONSEGMENT']._serialized_start=3527
  _globals['_TRANSCRIPTIONSEGMENT']._serialized_end=3646
  _globals['_BUFFERINFO']._serialized_start=3648
  _globals['_BUFFERINFO']._serialized_end=3696
  _globals['_OWNEDBUFFER']._serialized_start=3698
  _globals['_OWNEDBUFFER']._serialized_end=3799
  _globals['_ROOMEVENT']._serialized_start=3802
  _globals['_ROOMEVENT']._serialized_end=5397
  _globals['_ROOMINFO']._serialized_start=5399
  _globals['_ROOMINFO']._serialized_end=5454
  _globals['_OWNEDROOM']._serialized_start=5456
  _globals['_OWNEDROOM']._serialized_end=5553
  _globals['_PARTICIPANTCONNECTED']._serialized_start=5555
  _globals['_PARTICIPANTCONNECTED']._serialized_end=5624
  _globals['_PARTICIPANTDISCONNECTED']._serialized_start=5626
  _globals['_PARTICIPANTDISCONNECTED']._serialized_end=5676
  _globals['_LOCALTRACKPUBLISHED']._serialized_start=5678
  _globals['_LOCALTRACKPUBLISHED']._serialized_end=5718
  _globals['_LOCALTRACKUNPUBLISHED']._serialized_start=5720
  _globals['_LOCALTRACKUNPUBLISHED']._serialized_end=5768
  _globals['_TRACKPUBLISHED']._serialized_start=5770
  _globals['_TRACKPUBLISHED']._serialized_end=5870
  _globals['_TRACKUNPUBLISHED']._serialized_start=5872
  _globals['_TRACKUNPUBLISHED']._serialized_end=5940
  _globals['_TRACKSUBSCRIBED']._serialized_start=5942
  _globals['_TRACKSUBSCRIBED']._serialized_end=6026
  _globals['_TRACKUNSUBSCRIBED']._serialized_start=6028
  _globals['_TRACKUNSUBSCRIBED']._serialized_end=6091
  _globals['_TRACKSUBSCRIPTIONFAILED']._serialized_start=6093
  _globals['_TRACKSUBSCRIPTIONFAILED']._serialized_end=6177
  _globals['_TRACKMUTED']._serialized_start=6179
  _globals['_TRACKMUTED']._serialized_end=6235
  _globals['_TRACKUNMUTED']._serialized_start=6237
  _globals['_TRACKUNMUTED']._serialized_end=6295
  _globals['_E2EESTATECHANGED']._serialized_start=6297
  _globals['_E2EESTATECHANGED']._serialized_end=6387
  _globals['_ACTIVESPEAKERSCHANGED']._serialized_start=6389
  _globals['_ACTIVESPEAKERSCHANGED']._serialized_end=6438
  _globals['_ROOMMETADATACHANGED']._serialized_start=6440
  _globals['_ROOMMETADATACHANGED']._serialized_end=6479
  _globals['_ROOMSIDCHANGED']._serialized_start=6481
  _globals['_ROOMSIDCHANGED']._serialized_end=6510
  _globals['_PARTICIPANTMETADATACHANGED']._serialized_start=6512
  _globals['_PARTICIPANTMETADATACHANGED']._serialized_end=6583
  _globals['_PARTICIPANTNAMECHANGED']._serialized_start=6585
  _globals['_PARTICIPANTNAMECHANGED']._serialized_end=6648
  _globals['_CONNECTIONQUALITYCHANGED']._serialized_start=6650
  _globals['_CONNECTIONQUALITYCHANGED']._serialized_end=6752
  _globals['_USERPACKET']._serialized_start=6754
  _globals['_USERPACKET']._serialized_end=6838
  _globals['_SIPDTMF']._serialized_start=6840
  _globals['_SIPDTMF']._serialized_end=6893
  _globals['_DATAPACKETRECEIVED']._serialized_start=6896
  _globals['_DATAPACKETRECEIVED']._serialized_end=7141
  _globals['_CONNECTIONSTATECHANGED']._serialized_start=7143
  _globals['_CONNECTIONSTATECHANGED']._serialized_end=7214
  _globals['_CONNECTED']._serialized_start=7216
  _globals['_CONNECTED']._serialized_end=7227
  _globals['_DISCONNECTED']._serialized_start=7229
  _globals['_DISCONNECTED']._serialized_end=7243
  _globals['_RECONNECTING']._serialized_start=7245
  _globals['_RECONNECTING']._serialized_end=7259
  _globals['_RECONNECTED']._serialized_start=7261
  _globals['_RECONNECTED']._serialized_end=7274
  _globals['_ROOMEOS']._serialized_start=7276
  _globals['_ROOMEOS']._serialized_end=7285
# @@protoc_insertion_point(module_scope)
