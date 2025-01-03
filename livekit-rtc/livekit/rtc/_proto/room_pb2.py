# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: room.proto
# Protobuf Python Version: 5.26.1
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nroom.proto\x12\rlivekit.proto\x1a\ne2ee.proto\x1a\x0chandle.proto\x1a\x11participant.proto\x1a\x0btrack.proto\x1a\x11video_frame.proto\x1a\x0bstats.proto\"Y\n\x0e\x43onnectRequest\x12\x0b\n\x03url\x18\x01 \x02(\t\x12\r\n\x05token\x18\x02 \x02(\t\x12+\n\x07options\x18\x03 \x02(\x0b\x32\x1a.livekit.proto.RoomOptions\"#\n\x0f\x43onnectResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"\xbf\x03\n\x0f\x43onnectCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\x0f\n\x05\x65rror\x18\x02 \x01(\tH\x00\x12\x37\n\x06result\x18\x03 \x01(\x0b\x32%.livekit.proto.ConnectCallback.ResultH\x00\x1a\x89\x01\n\x15ParticipantWithTracks\x12\x34\n\x0bparticipant\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedParticipant\x12:\n\x0cpublications\x18\x02 \x03(\x0b\x32$.livekit.proto.OwnedTrackPublication\x1a\xb8\x01\n\x06Result\x12&\n\x04room\x18\x01 \x02(\x0b\x32\x18.livekit.proto.OwnedRoom\x12:\n\x11local_participant\x18\x02 \x02(\x0b\x32\x1f.livekit.proto.OwnedParticipant\x12J\n\x0cparticipants\x18\x03 \x03(\x0b\x32\x34.livekit.proto.ConnectCallback.ParticipantWithTracksB\t\n\x07message\"(\n\x11\x44isconnectRequest\x12\x13\n\x0broom_handle\x18\x01 \x02(\x04\"&\n\x12\x44isconnectResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"&\n\x12\x44isconnectCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"\x82\x01\n\x13PublishTrackRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x14\n\x0ctrack_handle\x18\x02 \x02(\x04\x12\x33\n\x07options\x18\x03 \x02(\x0b\x32\".livekit.proto.TrackPublishOptions\"(\n\x14PublishTrackResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"\x81\x01\n\x14PublishTrackCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\x0f\n\x05\x65rror\x18\x02 \x01(\tH\x00\x12;\n\x0bpublication\x18\x03 \x01(\x0b\x32$.livekit.proto.OwnedTrackPublicationH\x00\x42\t\n\x07message\"g\n\x15UnpublishTrackRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x11\n\ttrack_sid\x18\x02 \x02(\t\x12\x19\n\x11stop_on_unpublish\x18\x03 \x02(\x08\"*\n\x16UnpublishTrackResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"9\n\x16UnpublishTrackCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"\xb9\x01\n\x12PublishDataRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x10\n\x08\x64\x61ta_ptr\x18\x02 \x02(\x04\x12\x10\n\x08\x64\x61ta_len\x18\x03 \x02(\x04\x12\x10\n\x08reliable\x18\x04 \x02(\x08\x12\x1c\n\x10\x64\x65stination_sids\x18\x05 \x03(\tB\x02\x18\x01\x12\r\n\x05topic\x18\x06 \x01(\t\x12\x1e\n\x16\x64\x65stination_identities\x18\x07 \x03(\t\"\'\n\x13PublishDataResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"6\n\x13PublishDataCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"\xa6\x01\n\x1bPublishTranscriptionRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x1c\n\x14participant_identity\x18\x02 \x02(\t\x12\x10\n\x08track_id\x18\x03 \x02(\t\x12\x35\n\x08segments\x18\x04 \x03(\x0b\x32#.livekit.proto.TranscriptionSegment\"0\n\x1cPublishTranscriptionResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"?\n\x1cPublishTranscriptionCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"v\n\x15PublishSipDtmfRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x0c\n\x04\x63ode\x18\x02 \x02(\r\x12\r\n\x05\x64igit\x18\x03 \x02(\t\x12\x1e\n\x16\x64\x65stination_identities\x18\x04 \x03(\t\"*\n\x16PublishSipDtmfResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"9\n\x16PublishSipDtmfCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"M\n\x17SetLocalMetadataRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x10\n\x08metadata\x18\x02 \x02(\t\",\n\x18SetLocalMetadataResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\";\n\x18SetLocalMetadataCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"\x84\x01\n\x16SendChatMessageRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x0f\n\x07message\x18\x02 \x02(\t\x12\x1e\n\x16\x64\x65stination_identities\x18\x03 \x03(\t\x12\x17\n\x0fsender_identity\x18\x04 \x01(\t\"\xbc\x01\n\x16\x45\x64itChatMessageRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x11\n\tedit_text\x18\x02 \x02(\t\x12\x34\n\x10original_message\x18\x03 \x02(\x0b\x32\x1a.livekit.proto.ChatMessage\x12\x1e\n\x16\x64\x65stination_identities\x18\x04 \x03(\t\x12\x17\n\x0fsender_identity\x18\x05 \x01(\t\"+\n\x17SendChatMessageResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"{\n\x17SendChatMessageCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\x0f\n\x05\x65rror\x18\x02 \x01(\tH\x00\x12\x32\n\x0c\x63hat_message\x18\x03 \x01(\x0b\x32\x1a.livekit.proto.ChatMessageH\x00\x42\t\n\x07message\"q\n\x19SetLocalAttributesRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x32\n\nattributes\x18\x02 \x03(\x0b\x32\x1e.livekit.proto.AttributesEntry\"-\n\x0f\x41ttributesEntry\x12\x0b\n\x03key\x18\x01 \x02(\t\x12\r\n\x05value\x18\x02 \x02(\t\".\n\x1aSetLocalAttributesResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"=\n\x1aSetLocalAttributesCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"E\n\x13SetLocalNameRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x0c\n\x04name\x18\x02 \x02(\t\"(\n\x14SetLocalNameResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"7\n\x14SetLocalNameCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"E\n\x14SetSubscribedRequest\x12\x11\n\tsubscribe\x18\x01 \x02(\x08\x12\x1a\n\x12publication_handle\x18\x02 \x02(\x04\"\x17\n\x15SetSubscribedResponse\"-\n\x16GetSessionStatsRequest\x12\x13\n\x0broom_handle\x18\x01 \x02(\x04\"+\n\x17GetSessionStatsResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"\xf7\x01\n\x17GetSessionStatsCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\x0f\n\x05\x65rror\x18\x02 \x01(\tH\x00\x12?\n\x06result\x18\x03 \x01(\x0b\x32-.livekit.proto.GetSessionStatsCallback.ResultH\x00\x1am\n\x06Result\x12\x30\n\x0fpublisher_stats\x18\x01 \x03(\x0b\x32\x17.livekit.proto.RtcStats\x12\x31\n\x10subscriber_stats\x18\x02 \x03(\x0b\x32\x17.livekit.proto.RtcStatsB\t\n\x07message\";\n\rVideoEncoding\x12\x13\n\x0bmax_bitrate\x18\x01 \x02(\x04\x12\x15\n\rmax_framerate\x18\x02 \x02(\x01\"$\n\rAudioEncoding\x12\x13\n\x0bmax_bitrate\x18\x01 \x02(\x04\"\x9a\x02\n\x13TrackPublishOptions\x12\x34\n\x0evideo_encoding\x18\x01 \x01(\x0b\x32\x1c.livekit.proto.VideoEncoding\x12\x34\n\x0e\x61udio_encoding\x18\x02 \x01(\x0b\x32\x1c.livekit.proto.AudioEncoding\x12.\n\x0bvideo_codec\x18\x03 \x01(\x0e\x32\x19.livekit.proto.VideoCodec\x12\x0b\n\x03\x64tx\x18\x04 \x01(\x08\x12\x0b\n\x03red\x18\x05 \x01(\x08\x12\x11\n\tsimulcast\x18\x06 \x01(\x08\x12*\n\x06source\x18\x07 \x01(\x0e\x32\x1a.livekit.proto.TrackSource\x12\x0e\n\x06stream\x18\x08 \x01(\t\"=\n\tIceServer\x12\x0c\n\x04urls\x18\x01 \x03(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\"\xc4\x01\n\tRtcConfig\x12;\n\x12ice_transport_type\x18\x01 \x01(\x0e\x32\x1f.livekit.proto.IceTransportType\x12K\n\x1a\x63ontinual_gathering_policy\x18\x02 \x01(\x0e\x32\'.livekit.proto.ContinualGatheringPolicy\x12-\n\x0bice_servers\x18\x03 \x03(\x0b\x32\x18.livekit.proto.IceServer\"\xbe\x01\n\x0bRoomOptions\x12\x16\n\x0e\x61uto_subscribe\x18\x01 \x01(\x08\x12\x17\n\x0f\x61\x64\x61ptive_stream\x18\x02 \x01(\x08\x12\x10\n\x08\x64ynacast\x18\x03 \x01(\x08\x12(\n\x04\x65\x32\x65\x65\x18\x04 \x01(\x0b\x32\x1a.livekit.proto.E2eeOptions\x12,\n\nrtc_config\x18\x05 \x01(\x0b\x32\x18.livekit.proto.RtcConfig\x12\x14\n\x0cjoin_retries\x18\x06 \x01(\r\"w\n\x14TranscriptionSegment\x12\n\n\x02id\x18\x01 \x02(\t\x12\x0c\n\x04text\x18\x02 \x02(\t\x12\x12\n\nstart_time\x18\x03 \x02(\x04\x12\x10\n\x08\x65nd_time\x18\x04 \x02(\x04\x12\r\n\x05\x66inal\x18\x05 \x02(\x08\x12\x10\n\x08language\x18\x06 \x02(\t\"0\n\nBufferInfo\x12\x10\n\x08\x64\x61ta_ptr\x18\x01 \x02(\x04\x12\x10\n\x08\x64\x61ta_len\x18\x02 \x02(\x04\"e\n\x0bOwnedBuffer\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12\'\n\x04\x64\x61ta\x18\x02 \x02(\x0b\x32\x19.livekit.proto.BufferInfo\"\xdd\x0e\n\tRoomEvent\x12\x13\n\x0broom_handle\x18\x01 \x02(\x04\x12\x44\n\x15participant_connected\x18\x02 \x01(\x0b\x32#.livekit.proto.ParticipantConnectedH\x00\x12J\n\x18participant_disconnected\x18\x03 \x01(\x0b\x32&.livekit.proto.ParticipantDisconnectedH\x00\x12\x43\n\x15local_track_published\x18\x04 \x01(\x0b\x32\".livekit.proto.LocalTrackPublishedH\x00\x12G\n\x17local_track_unpublished\x18\x05 \x01(\x0b\x32$.livekit.proto.LocalTrackUnpublishedH\x00\x12\x45\n\x16local_track_subscribed\x18\x06 \x01(\x0b\x32#.livekit.proto.LocalTrackSubscribedH\x00\x12\x38\n\x0ftrack_published\x18\x07 \x01(\x0b\x32\x1d.livekit.proto.TrackPublishedH\x00\x12<\n\x11track_unpublished\x18\x08 \x01(\x0b\x32\x1f.livekit.proto.TrackUnpublishedH\x00\x12:\n\x10track_subscribed\x18\t \x01(\x0b\x32\x1e.livekit.proto.TrackSubscribedH\x00\x12>\n\x12track_unsubscribed\x18\n \x01(\x0b\x32 .livekit.proto.TrackUnsubscribedH\x00\x12K\n\x19track_subscription_failed\x18\x0b \x01(\x0b\x32&.livekit.proto.TrackSubscriptionFailedH\x00\x12\x30\n\x0btrack_muted\x18\x0c \x01(\x0b\x32\x19.livekit.proto.TrackMutedH\x00\x12\x34\n\rtrack_unmuted\x18\r \x01(\x0b\x32\x1b.livekit.proto.TrackUnmutedH\x00\x12G\n\x17\x61\x63tive_speakers_changed\x18\x0e \x01(\x0b\x32$.livekit.proto.ActiveSpeakersChangedH\x00\x12\x43\n\x15room_metadata_changed\x18\x0f \x01(\x0b\x32\".livekit.proto.RoomMetadataChangedH\x00\x12\x39\n\x10room_sid_changed\x18\x10 \x01(\x0b\x32\x1d.livekit.proto.RoomSidChangedH\x00\x12Q\n\x1cparticipant_metadata_changed\x18\x11 \x01(\x0b\x32).livekit.proto.ParticipantMetadataChangedH\x00\x12I\n\x18participant_name_changed\x18\x12 \x01(\x0b\x32%.livekit.proto.ParticipantNameChangedH\x00\x12U\n\x1eparticipant_attributes_changed\x18\x13 \x01(\x0b\x32+.livekit.proto.ParticipantAttributesChangedH\x00\x12M\n\x1a\x63onnection_quality_changed\x18\x14 \x01(\x0b\x32\'.livekit.proto.ConnectionQualityChangedH\x00\x12I\n\x18\x63onnection_state_changed\x18\x15 \x01(\x0b\x32%.livekit.proto.ConnectionStateChangedH\x00\x12\x33\n\x0c\x64isconnected\x18\x16 \x01(\x0b\x32\x1b.livekit.proto.DisconnectedH\x00\x12\x33\n\x0creconnecting\x18\x17 \x01(\x0b\x32\x1b.livekit.proto.ReconnectingH\x00\x12\x31\n\x0breconnected\x18\x18 \x01(\x0b\x32\x1a.livekit.proto.ReconnectedH\x00\x12=\n\x12\x65\x32\x65\x65_state_changed\x18\x19 \x01(\x0b\x32\x1f.livekit.proto.E2eeStateChangedH\x00\x12%\n\x03\x65os\x18\x1a \x01(\x0b\x32\x16.livekit.proto.RoomEOSH\x00\x12\x41\n\x14\x64\x61ta_packet_received\x18\x1b \x01(\x0b\x32!.livekit.proto.DataPacketReceivedH\x00\x12\x46\n\x16transcription_received\x18\x1c \x01(\x0b\x32$.livekit.proto.TranscriptionReceivedH\x00\x12:\n\x0c\x63hat_message\x18\x1d \x01(\x0b\x32\".livekit.proto.ChatMessageReceivedH\x00\x42\t\n\x07message\"7\n\x08RoomInfo\x12\x0b\n\x03sid\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x10\n\x08metadata\x18\x03 \x02(\t\"a\n\tOwnedRoom\x12-\n\x06handle\x18\x01 \x02(\x0b\x32\x1d.livekit.proto.FfiOwnedHandle\x12%\n\x04info\x18\x02 \x02(\x0b\x32\x17.livekit.proto.RoomInfo\"E\n\x14ParticipantConnected\x12-\n\x04info\x18\x01 \x02(\x0b\x32\x1f.livekit.proto.OwnedParticipant\"7\n\x17ParticipantDisconnected\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\"(\n\x13LocalTrackPublished\x12\x11\n\ttrack_sid\x18\x01 \x02(\t\"0\n\x15LocalTrackUnpublished\x12\x17\n\x0fpublication_sid\x18\x01 \x02(\t\")\n\x14LocalTrackSubscribed\x12\x11\n\ttrack_sid\x18\x02 \x02(\t\"i\n\x0eTrackPublished\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x39\n\x0bpublication\x18\x02 \x02(\x0b\x32$.livekit.proto.OwnedTrackPublication\"I\n\x10TrackUnpublished\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x17\n\x0fpublication_sid\x18\x02 \x02(\t\"Y\n\x0fTrackSubscribed\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12(\n\x05track\x18\x02 \x02(\x0b\x32\x19.livekit.proto.OwnedTrack\"D\n\x11TrackUnsubscribed\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x11\n\ttrack_sid\x18\x02 \x02(\t\"Y\n\x17TrackSubscriptionFailed\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x11\n\ttrack_sid\x18\x02 \x02(\t\x12\r\n\x05\x65rror\x18\x03 \x02(\t\"=\n\nTrackMuted\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x11\n\ttrack_sid\x18\x02 \x02(\t\"?\n\x0cTrackUnmuted\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x11\n\ttrack_sid\x18\x02 \x02(\t\"_\n\x10\x45\x32\x65\x65StateChanged\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12-\n\x05state\x18\x02 \x02(\x0e\x32\x1e.livekit.proto.EncryptionState\"7\n\x15\x41\x63tiveSpeakersChanged\x12\x1e\n\x16participant_identities\x18\x01 \x03(\t\"\'\n\x13RoomMetadataChanged\x12\x10\n\x08metadata\x18\x01 \x02(\t\"\x1d\n\x0eRoomSidChanged\x12\x0b\n\x03sid\x18\x01 \x02(\t\"L\n\x1aParticipantMetadataChanged\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x10\n\x08metadata\x18\x02 \x02(\t\"\xac\x01\n\x1cParticipantAttributesChanged\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x32\n\nattributes\x18\x02 \x03(\x0b\x32\x1e.livekit.proto.AttributesEntry\x12:\n\x12\x63hanged_attributes\x18\x03 \x03(\x0b\x32\x1e.livekit.proto.AttributesEntry\"D\n\x16ParticipantNameChanged\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x0c\n\x04name\x18\x02 \x02(\t\"k\n\x18\x43onnectionQualityChanged\x12\x1c\n\x14participant_identity\x18\x01 \x02(\t\x12\x31\n\x07quality\x18\x02 \x02(\x0e\x32 .livekit.proto.ConnectionQuality\"E\n\nUserPacket\x12(\n\x04\x64\x61ta\x18\x01 \x02(\x0b\x32\x1a.livekit.proto.OwnedBuffer\x12\r\n\x05topic\x18\x02 \x01(\t\"y\n\x0b\x43hatMessage\x12\n\n\x02id\x18\x01 \x02(\t\x12\x11\n\ttimestamp\x18\x02 \x02(\x03\x12\x0f\n\x07message\x18\x03 \x02(\t\x12\x16\n\x0e\x65\x64it_timestamp\x18\x04 \x01(\x03\x12\x0f\n\x07\x64\x65leted\x18\x05 \x01(\x08\x12\x11\n\tgenerated\x18\x06 \x01(\x08\"`\n\x13\x43hatMessageReceived\x12+\n\x07message\x18\x01 \x02(\x0b\x32\x1a.livekit.proto.ChatMessage\x12\x1c\n\x14participant_identity\x18\x02 \x02(\t\"&\n\x07SipDTMF\x12\x0c\n\x04\x63ode\x18\x01 \x02(\r\x12\r\n\x05\x64igit\x18\x02 \x01(\t\"\xbf\x01\n\x12\x44\x61taPacketReceived\x12+\n\x04kind\x18\x01 \x02(\x0e\x32\x1d.livekit.proto.DataPacketKind\x12\x1c\n\x14participant_identity\x18\x02 \x02(\t\x12)\n\x04user\x18\x04 \x01(\x0b\x32\x19.livekit.proto.UserPacketH\x00\x12*\n\x08sip_dtmf\x18\x05 \x01(\x0b\x32\x16.livekit.proto.SipDTMFH\x00\x42\x07\n\x05value\"\x7f\n\x15TranscriptionReceived\x12\x1c\n\x14participant_identity\x18\x01 \x01(\t\x12\x11\n\ttrack_sid\x18\x02 \x01(\t\x12\x35\n\x08segments\x18\x03 \x03(\x0b\x32#.livekit.proto.TranscriptionSegment\"G\n\x16\x43onnectionStateChanged\x12-\n\x05state\x18\x01 \x02(\x0e\x32\x1e.livekit.proto.ConnectionState\"\x0b\n\tConnected\"?\n\x0c\x44isconnected\x12/\n\x06reason\x18\x01 \x02(\x0e\x32\x1f.livekit.proto.DisconnectReason\"\x0e\n\x0cReconnecting\"\r\n\x0bReconnected\"\t\n\x07RoomEOS*P\n\x10IceTransportType\x12\x13\n\x0fTRANSPORT_RELAY\x10\x00\x12\x14\n\x10TRANSPORT_NOHOST\x10\x01\x12\x11\n\rTRANSPORT_ALL\x10\x02*C\n\x18\x43ontinualGatheringPolicy\x12\x0f\n\x0bGATHER_ONCE\x10\x00\x12\x16\n\x12GATHER_CONTINUALLY\x10\x01*`\n\x11\x43onnectionQuality\x12\x10\n\x0cQUALITY_POOR\x10\x00\x12\x10\n\x0cQUALITY_GOOD\x10\x01\x12\x15\n\x11QUALITY_EXCELLENT\x10\x02\x12\x10\n\x0cQUALITY_LOST\x10\x03*S\n\x0f\x43onnectionState\x12\x15\n\x11\x43ONN_DISCONNECTED\x10\x00\x12\x12\n\x0e\x43ONN_CONNECTED\x10\x01\x12\x15\n\x11\x43ONN_RECONNECTING\x10\x02*3\n\x0e\x44\x61taPacketKind\x12\x0e\n\nKIND_LOSSY\x10\x00\x12\x11\n\rKIND_RELIABLE\x10\x01*\xec\x01\n\x10\x44isconnectReason\x12\x12\n\x0eUNKNOWN_REASON\x10\x00\x12\x14\n\x10\x43LIENT_INITIATED\x10\x01\x12\x16\n\x12\x44UPLICATE_IDENTITY\x10\x02\x12\x13\n\x0fSERVER_SHUTDOWN\x10\x03\x12\x17\n\x13PARTICIPANT_REMOVED\x10\x04\x12\x10\n\x0cROOM_DELETED\x10\x05\x12\x12\n\x0eSTATE_MISMATCH\x10\x06\x12\x10\n\x0cJOIN_FAILURE\x10\x07\x12\r\n\tMIGRATION\x10\x08\x12\x10\n\x0cSIGNAL_CLOSE\x10\t\x12\x0f\n\x0bROOM_CLOSED\x10\nB\x10\xaa\x02\rLiveKit.Proto')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'room_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\rLiveKit.Proto'
  _globals['_PUBLISHDATAREQUEST'].fields_by_name['destination_sids']._loaded_options = None
  _globals['_PUBLISHDATAREQUEST'].fields_by_name['destination_sids']._serialized_options = b'\030\001'
  _globals['_ICETRANSPORTTYPE']._serialized_start=9177
  _globals['_ICETRANSPORTTYPE']._serialized_end=9257
  _globals['_CONTINUALGATHERINGPOLICY']._serialized_start=9259
  _globals['_CONTINUALGATHERINGPOLICY']._serialized_end=9326
  _globals['_CONNECTIONQUALITY']._serialized_start=9328
  _globals['_CONNECTIONQUALITY']._serialized_end=9424
  _globals['_CONNECTIONSTATE']._serialized_start=9426
  _globals['_CONNECTIONSTATE']._serialized_end=9509
  _globals['_DATAPACKETKIND']._serialized_start=9511
  _globals['_DATAPACKETKIND']._serialized_end=9562
  _globals['_DISCONNECTREASON']._serialized_start=9565
  _globals['_DISCONNECTREASON']._serialized_end=9801
  _globals['_CONNECTREQUEST']._serialized_start=119
  _globals['_CONNECTREQUEST']._serialized_end=208
  _globals['_CONNECTRESPONSE']._serialized_start=210
  _globals['_CONNECTRESPONSE']._serialized_end=245
  _globals['_CONNECTCALLBACK']._serialized_start=248
  _globals['_CONNECTCALLBACK']._serialized_end=695
  _globals['_CONNECTCALLBACK_PARTICIPANTWITHTRACKS']._serialized_start=360
  _globals['_CONNECTCALLBACK_PARTICIPANTWITHTRACKS']._serialized_end=497
  _globals['_CONNECTCALLBACK_RESULT']._serialized_start=500
  _globals['_CONNECTCALLBACK_RESULT']._serialized_end=684
  _globals['_DISCONNECTREQUEST']._serialized_start=697
  _globals['_DISCONNECTREQUEST']._serialized_end=737
  _globals['_DISCONNECTRESPONSE']._serialized_start=739
  _globals['_DISCONNECTRESPONSE']._serialized_end=777
  _globals['_DISCONNECTCALLBACK']._serialized_start=779
  _globals['_DISCONNECTCALLBACK']._serialized_end=817
  _globals['_PUBLISHTRACKREQUEST']._serialized_start=820
  _globals['_PUBLISHTRACKREQUEST']._serialized_end=950
  _globals['_PUBLISHTRACKRESPONSE']._serialized_start=952
  _globals['_PUBLISHTRACKRESPONSE']._serialized_end=992
  _globals['_PUBLISHTRACKCALLBACK']._serialized_start=995
  _globals['_PUBLISHTRACKCALLBACK']._serialized_end=1124
  _globals['_UNPUBLISHTRACKREQUEST']._serialized_start=1126
  _globals['_UNPUBLISHTRACKREQUEST']._serialized_end=1229
  _globals['_UNPUBLISHTRACKRESPONSE']._serialized_start=1231
  _globals['_UNPUBLISHTRACKRESPONSE']._serialized_end=1273
  _globals['_UNPUBLISHTRACKCALLBACK']._serialized_start=1275
  _globals['_UNPUBLISHTRACKCALLBACK']._serialized_end=1332
  _globals['_PUBLISHDATAREQUEST']._serialized_start=1335
  _globals['_PUBLISHDATAREQUEST']._serialized_end=1520
  _globals['_PUBLISHDATARESPONSE']._serialized_start=1522
  _globals['_PUBLISHDATARESPONSE']._serialized_end=1561
  _globals['_PUBLISHDATACALLBACK']._serialized_start=1563
  _globals['_PUBLISHDATACALLBACK']._serialized_end=1617
  _globals['_PUBLISHTRANSCRIPTIONREQUEST']._serialized_start=1620
  _globals['_PUBLISHTRANSCRIPTIONREQUEST']._serialized_end=1786
  _globals['_PUBLISHTRANSCRIPTIONRESPONSE']._serialized_start=1788
  _globals['_PUBLISHTRANSCRIPTIONRESPONSE']._serialized_end=1836
  _globals['_PUBLISHTRANSCRIPTIONCALLBACK']._serialized_start=1838
  _globals['_PUBLISHTRANSCRIPTIONCALLBACK']._serialized_end=1901
  _globals['_PUBLISHSIPDTMFREQUEST']._serialized_start=1903
  _globals['_PUBLISHSIPDTMFREQUEST']._serialized_end=2021
  _globals['_PUBLISHSIPDTMFRESPONSE']._serialized_start=2023
  _globals['_PUBLISHSIPDTMFRESPONSE']._serialized_end=2065
  _globals['_PUBLISHSIPDTMFCALLBACK']._serialized_start=2067
  _globals['_PUBLISHSIPDTMFCALLBACK']._serialized_end=2124
  _globals['_SETLOCALMETADATAREQUEST']._serialized_start=2126
  _globals['_SETLOCALMETADATAREQUEST']._serialized_end=2203
  _globals['_SETLOCALMETADATARESPONSE']._serialized_start=2205
  _globals['_SETLOCALMETADATARESPONSE']._serialized_end=2249
  _globals['_SETLOCALMETADATACALLBACK']._serialized_start=2251
  _globals['_SETLOCALMETADATACALLBACK']._serialized_end=2310
  _globals['_SENDCHATMESSAGEREQUEST']._serialized_start=2313
  _globals['_SENDCHATMESSAGEREQUEST']._serialized_end=2445
  _globals['_EDITCHATMESSAGEREQUEST']._serialized_start=2448
  _globals['_EDITCHATMESSAGEREQUEST']._serialized_end=2636
  _globals['_SENDCHATMESSAGERESPONSE']._serialized_start=2638
  _globals['_SENDCHATMESSAGERESPONSE']._serialized_end=2681
  _globals['_SENDCHATMESSAGECALLBACK']._serialized_start=2683
  _globals['_SENDCHATMESSAGECALLBACK']._serialized_end=2806
  _globals['_SETLOCALATTRIBUTESREQUEST']._serialized_start=2808
  _globals['_SETLOCALATTRIBUTESREQUEST']._serialized_end=2921
  _globals['_ATTRIBUTESENTRY']._serialized_start=2923
  _globals['_ATTRIBUTESENTRY']._serialized_end=2968
  _globals['_SETLOCALATTRIBUTESRESPONSE']._serialized_start=2970
  _globals['_SETLOCALATTRIBUTESRESPONSE']._serialized_end=3016
  _globals['_SETLOCALATTRIBUTESCALLBACK']._serialized_start=3018
  _globals['_SETLOCALATTRIBUTESCALLBACK']._serialized_end=3079
  _globals['_SETLOCALNAMEREQUEST']._serialized_start=3081
  _globals['_SETLOCALNAMEREQUEST']._serialized_end=3150
  _globals['_SETLOCALNAMERESPONSE']._serialized_start=3152
  _globals['_SETLOCALNAMERESPONSE']._serialized_end=3192
  _globals['_SETLOCALNAMECALLBACK']._serialized_start=3194
  _globals['_SETLOCALNAMECALLBACK']._serialized_end=3249
  _globals['_SETSUBSCRIBEDREQUEST']._serialized_start=3251
  _globals['_SETSUBSCRIBEDREQUEST']._serialized_end=3320
  _globals['_SETSUBSCRIBEDRESPONSE']._serialized_start=3322
  _globals['_SETSUBSCRIBEDRESPONSE']._serialized_end=3345
  _globals['_GETSESSIONSTATSREQUEST']._serialized_start=3347
  _globals['_GETSESSIONSTATSREQUEST']._serialized_end=3392
  _globals['_GETSESSIONSTATSRESPONSE']._serialized_start=3394
  _globals['_GETSESSIONSTATSRESPONSE']._serialized_end=3437
  _globals['_GETSESSIONSTATSCALLBACK']._serialized_start=3440
  _globals['_GETSESSIONSTATSCALLBACK']._serialized_end=3687
  _globals['_GETSESSIONSTATSCALLBACK_RESULT']._serialized_start=3567
  _globals['_GETSESSIONSTATSCALLBACK_RESULT']._serialized_end=3676
  _globals['_VIDEOENCODING']._serialized_start=3689
  _globals['_VIDEOENCODING']._serialized_end=3748
  _globals['_AUDIOENCODING']._serialized_start=3750
  _globals['_AUDIOENCODING']._serialized_end=3786
  _globals['_TRACKPUBLISHOPTIONS']._serialized_start=3789
  _globals['_TRACKPUBLISHOPTIONS']._serialized_end=4071
  _globals['_ICESERVER']._serialized_start=4073
  _globals['_ICESERVER']._serialized_end=4134
  _globals['_RTCCONFIG']._serialized_start=4137
  _globals['_RTCCONFIG']._serialized_end=4333
  _globals['_ROOMOPTIONS']._serialized_start=4336
  _globals['_ROOMOPTIONS']._serialized_end=4526
  _globals['_TRANSCRIPTIONSEGMENT']._serialized_start=4528
  _globals['_TRANSCRIPTIONSEGMENT']._serialized_end=4647
  _globals['_BUFFERINFO']._serialized_start=4649
  _globals['_BUFFERINFO']._serialized_end=4697
  _globals['_OWNEDBUFFER']._serialized_start=4699
  _globals['_OWNEDBUFFER']._serialized_end=4800
  _globals['_ROOMEVENT']._serialized_start=4803
  _globals['_ROOMEVENT']._serialized_end=6688
  _globals['_ROOMINFO']._serialized_start=6690
  _globals['_ROOMINFO']._serialized_end=6745
  _globals['_OWNEDROOM']._serialized_start=6747
  _globals['_OWNEDROOM']._serialized_end=6844
  _globals['_PARTICIPANTCONNECTED']._serialized_start=6846
  _globals['_PARTICIPANTCONNECTED']._serialized_end=6915
  _globals['_PARTICIPANTDISCONNECTED']._serialized_start=6917
  _globals['_PARTICIPANTDISCONNECTED']._serialized_end=6972
  _globals['_LOCALTRACKPUBLISHED']._serialized_start=6974
  _globals['_LOCALTRACKPUBLISHED']._serialized_end=7014
  _globals['_LOCALTRACKUNPUBLISHED']._serialized_start=7016
  _globals['_LOCALTRACKUNPUBLISHED']._serialized_end=7064
  _globals['_LOCALTRACKSUBSCRIBED']._serialized_start=7066
  _globals['_LOCALTRACKSUBSCRIBED']._serialized_end=7107
  _globals['_TRACKPUBLISHED']._serialized_start=7109
  _globals['_TRACKPUBLISHED']._serialized_end=7214
  _globals['_TRACKUNPUBLISHED']._serialized_start=7216
  _globals['_TRACKUNPUBLISHED']._serialized_end=7289
  _globals['_TRACKSUBSCRIBED']._serialized_start=7291
  _globals['_TRACKSUBSCRIBED']._serialized_end=7380
  _globals['_TRACKUNSUBSCRIBED']._serialized_start=7382
  _globals['_TRACKUNSUBSCRIBED']._serialized_end=7450
  _globals['_TRACKSUBSCRIPTIONFAILED']._serialized_start=7452
  _globals['_TRACKSUBSCRIPTIONFAILED']._serialized_end=7541
  _globals['_TRACKMUTED']._serialized_start=7543
  _globals['_TRACKMUTED']._serialized_end=7604
  _globals['_TRACKUNMUTED']._serialized_start=7606
  _globals['_TRACKUNMUTED']._serialized_end=7669
  _globals['_E2EESTATECHANGED']._serialized_start=7671
  _globals['_E2EESTATECHANGED']._serialized_end=7766
  _globals['_ACTIVESPEAKERSCHANGED']._serialized_start=7768
  _globals['_ACTIVESPEAKERSCHANGED']._serialized_end=7823
  _globals['_ROOMMETADATACHANGED']._serialized_start=7825
  _globals['_ROOMMETADATACHANGED']._serialized_end=7864
  _globals['_ROOMSIDCHANGED']._serialized_start=7866
  _globals['_ROOMSIDCHANGED']._serialized_end=7895
  _globals['_PARTICIPANTMETADATACHANGED']._serialized_start=7897
  _globals['_PARTICIPANTMETADATACHANGED']._serialized_end=7973
  _globals['_PARTICIPANTATTRIBUTESCHANGED']._serialized_start=7976
  _globals['_PARTICIPANTATTRIBUTESCHANGED']._serialized_end=8148
  _globals['_PARTICIPANTNAMECHANGED']._serialized_start=8150
  _globals['_PARTICIPANTNAMECHANGED']._serialized_end=8218
  _globals['_CONNECTIONQUALITYCHANGED']._serialized_start=8220
  _globals['_CONNECTIONQUALITYCHANGED']._serialized_end=8327
  _globals['_USERPACKET']._serialized_start=8329
  _globals['_USERPACKET']._serialized_end=8398
  _globals['_CHATMESSAGE']._serialized_start=8400
  _globals['_CHATMESSAGE']._serialized_end=8521
  _globals['_CHATMESSAGERECEIVED']._serialized_start=8523
  _globals['_CHATMESSAGERECEIVED']._serialized_end=8619
  _globals['_SIPDTMF']._serialized_start=8621
  _globals['_SIPDTMF']._serialized_end=8659
  _globals['_DATAPACKETRECEIVED']._serialized_start=8662
  _globals['_DATAPACKETRECEIVED']._serialized_end=8853
  _globals['_TRANSCRIPTIONRECEIVED']._serialized_start=8855
  _globals['_TRANSCRIPTIONRECEIVED']._serialized_end=8982
  _globals['_CONNECTIONSTATECHANGED']._serialized_start=8984
  _globals['_CONNECTIONSTATECHANGED']._serialized_end=9055
  _globals['_CONNECTED']._serialized_start=9057
  _globals['_CONNECTED']._serialized_end=9068
  _globals['_DISCONNECTED']._serialized_start=9070
  _globals['_DISCONNECTED']._serialized_end=9133
  _globals['_RECONNECTING']._serialized_start=9135
  _globals['_RECONNECTING']._serialized_end=9149
  _globals['_RECONNECTED']._serialized_start=9151
  _globals['_RECONNECTED']._serialized_end=9164
  _globals['_ROOMEOS']._serialized_start=9166
  _globals['_ROOMEOS']._serialized_end=9175
# @@protoc_insertion_point(module_scope)
