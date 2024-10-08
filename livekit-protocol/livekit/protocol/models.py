# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: livekit_models.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
import metrics as _metrics_


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14livekit_models.proto\x12\x07livekit\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x15livekit_metrics.proto\"\xc9\x02\n\x04Room\x12\x0b\n\x03sid\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x15\n\rempty_timeout\x18\x03 \x01(\r\x12\x19\n\x11\x64\x65parture_timeout\x18\x0e \x01(\r\x12\x18\n\x10max_participants\x18\x04 \x01(\r\x12\x15\n\rcreation_time\x18\x05 \x01(\x03\x12\x15\n\rturn_password\x18\x06 \x01(\t\x12&\n\x0e\x65nabled_codecs\x18\x07 \x03(\x0b\x32\x0e.livekit.Codec\x12\x10\n\x08metadata\x18\x08 \x01(\t\x12\x18\n\x10num_participants\x18\t \x01(\r\x12\x16\n\x0enum_publishers\x18\x0b \x01(\r\x12\x18\n\x10\x61\x63tive_recording\x18\n \x01(\x08\x12&\n\x07version\x18\r \x01(\x0b\x32\x15.livekit.TimedVersion\"(\n\x05\x43odec\x12\x0c\n\x04mime\x18\x01 \x01(\t\x12\x11\n\tfmtp_line\x18\x02 \x01(\t\"9\n\x0cPlayoutDelay\x12\x0f\n\x07\x65nabled\x18\x01 \x01(\x08\x12\x0b\n\x03min\x18\x02 \x01(\r\x12\x0b\n\x03max\x18\x03 \x01(\r\"\x85\x02\n\x15ParticipantPermission\x12\x15\n\rcan_subscribe\x18\x01 \x01(\x08\x12\x13\n\x0b\x63\x61n_publish\x18\x02 \x01(\x08\x12\x18\n\x10\x63\x61n_publish_data\x18\x03 \x01(\x08\x12\x31\n\x13\x63\x61n_publish_sources\x18\t \x03(\x0e\x32\x14.livekit.TrackSource\x12\x0e\n\x06hidden\x18\x07 \x01(\x08\x12\x14\n\x08recorder\x18\x08 \x01(\x08\x42\x02\x18\x01\x12\x1b\n\x13\x63\x61n_update_metadata\x18\n \x01(\x08\x12\x11\n\x05\x61gent\x18\x0b \x01(\x08\x42\x02\x18\x01\x12\x1d\n\x15\x63\x61n_subscribe_metrics\x18\x0c \x01(\x08\"\xf8\x04\n\x0fParticipantInfo\x12\x0b\n\x03sid\x18\x01 \x01(\t\x12\x10\n\x08identity\x18\x02 \x01(\t\x12-\n\x05state\x18\x03 \x01(\x0e\x32\x1e.livekit.ParticipantInfo.State\x12\"\n\x06tracks\x18\x04 \x03(\x0b\x32\x12.livekit.TrackInfo\x12\x10\n\x08metadata\x18\x05 \x01(\t\x12\x11\n\tjoined_at\x18\x06 \x01(\x03\x12\x0c\n\x04name\x18\t \x01(\t\x12\x0f\n\x07version\x18\n \x01(\r\x12\x32\n\npermission\x18\x0b \x01(\x0b\x32\x1e.livekit.ParticipantPermission\x12\x0e\n\x06region\x18\x0c \x01(\t\x12\x14\n\x0cis_publisher\x18\r \x01(\x08\x12+\n\x04kind\x18\x0e \x01(\x0e\x32\x1d.livekit.ParticipantInfo.Kind\x12<\n\nattributes\x18\x0f \x03(\x0b\x32(.livekit.ParticipantInfo.AttributesEntry\x12\x34\n\x11\x64isconnect_reason\x18\x10 \x01(\x0e\x32\x19.livekit.DisconnectReason\x1a\x31\n\x0f\x41ttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\">\n\x05State\x12\x0b\n\x07JOINING\x10\x00\x12\n\n\x06JOINED\x10\x01\x12\n\n\x06\x41\x43TIVE\x10\x02\x12\x10\n\x0c\x44ISCONNECTED\x10\x03\"A\n\x04Kind\x12\x0c\n\x08STANDARD\x10\x00\x12\x0b\n\x07INGRESS\x10\x01\x12\n\n\x06\x45GRESS\x10\x02\x12\x07\n\x03SIP\x10\x03\x12\t\n\x05\x41GENT\x10\x04\"3\n\nEncryption\"%\n\x04Type\x12\x08\n\x04NONE\x10\x00\x12\x07\n\x03GCM\x10\x01\x12\n\n\x06\x43USTOM\x10\x02\"f\n\x12SimulcastCodecInfo\x12\x11\n\tmime_type\x18\x01 \x01(\t\x12\x0b\n\x03mid\x18\x02 \x01(\t\x12\x0b\n\x03\x63id\x18\x03 \x01(\t\x12#\n\x06layers\x18\x04 \x03(\x0b\x32\x13.livekit.VideoLayer\"\xf5\x03\n\tTrackInfo\x12\x0b\n\x03sid\x18\x01 \x01(\t\x12 \n\x04type\x18\x02 \x01(\x0e\x32\x12.livekit.TrackType\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\r\n\x05muted\x18\x04 \x01(\x08\x12\r\n\x05width\x18\x05 \x01(\r\x12\x0e\n\x06height\x18\x06 \x01(\r\x12\x11\n\tsimulcast\x18\x07 \x01(\x08\x12\x13\n\x0b\x64isable_dtx\x18\x08 \x01(\x08\x12$\n\x06source\x18\t \x01(\x0e\x32\x14.livekit.TrackSource\x12#\n\x06layers\x18\n \x03(\x0b\x32\x13.livekit.VideoLayer\x12\x11\n\tmime_type\x18\x0b \x01(\t\x12\x0b\n\x03mid\x18\x0c \x01(\t\x12+\n\x06\x63odecs\x18\r \x03(\x0b\x32\x1b.livekit.SimulcastCodecInfo\x12\x0e\n\x06stereo\x18\x0e \x01(\x08\x12\x13\n\x0b\x64isable_red\x18\x0f \x01(\x08\x12,\n\nencryption\x18\x10 \x01(\x0e\x32\x18.livekit.Encryption.Type\x12\x0e\n\x06stream\x18\x11 \x01(\t\x12&\n\x07version\x18\x12 \x01(\x0b\x32\x15.livekit.TimedVersion\x12\x32\n\x0e\x61udio_features\x18\x13 \x03(\x0e\x32\x1a.livekit.AudioTrackFeature\"r\n\nVideoLayer\x12&\n\x07quality\x18\x01 \x01(\x0e\x32\x15.livekit.VideoQuality\x12\r\n\x05width\x18\x02 \x01(\r\x12\x0e\n\x06height\x18\x03 \x01(\r\x12\x0f\n\x07\x62itrate\x18\x04 \x01(\r\x12\x0c\n\x04ssrc\x18\x05 \x01(\r\"\xa7\x04\n\nDataPacket\x12*\n\x04kind\x18\x01 \x01(\x0e\x32\x18.livekit.DataPacket.KindB\x02\x18\x01\x12\x1c\n\x14participant_identity\x18\x04 \x01(\t\x12\x1e\n\x16\x64\x65stination_identities\x18\x05 \x03(\t\x12#\n\x04user\x18\x02 \x01(\x0b\x32\x13.livekit.UserPacketH\x00\x12\x33\n\x07speaker\x18\x03 \x01(\x0b\x32\x1c.livekit.ActiveSpeakerUpdateB\x02\x18\x01H\x00\x12$\n\x08sip_dtmf\x18\x06 \x01(\x0b\x32\x10.livekit.SipDTMFH\x00\x12/\n\rtranscription\x18\x07 \x01(\x0b\x32\x16.livekit.TranscriptionH\x00\x12(\n\x07metrics\x18\x08 \x01(\x0b\x32\x15.livekit.MetricsBatchH\x00\x12,\n\x0c\x63hat_message\x18\t \x01(\x0b\x32\x14.livekit.ChatMessageH\x00\x12*\n\x0brpc_request\x18\n \x01(\x0b\x32\x13.livekit.RpcRequestH\x00\x12\"\n\x07rpc_ack\x18\x0b \x01(\x0b\x32\x0f.livekit.RpcAckH\x00\x12,\n\x0crpc_response\x18\x0c \x01(\x0b\x32\x14.livekit.RpcResponseH\x00\"\x1f\n\x04Kind\x12\x0c\n\x08RELIABLE\x10\x00\x12\t\n\x05LOSSY\x10\x01\x42\x07\n\x05value\"=\n\x13\x41\x63tiveSpeakerUpdate\x12&\n\x08speakers\x18\x01 \x03(\x0b\x32\x14.livekit.SpeakerInfo\"9\n\x0bSpeakerInfo\x12\x0b\n\x03sid\x18\x01 \x01(\t\x12\r\n\x05level\x18\x02 \x01(\x02\x12\x0e\n\x06\x61\x63tive\x18\x03 \x01(\x08\"\xa0\x02\n\nUserPacket\x12\x1b\n\x0fparticipant_sid\x18\x01 \x01(\tB\x02\x18\x01\x12 \n\x14participant_identity\x18\x05 \x01(\tB\x02\x18\x01\x12\x0f\n\x07payload\x18\x02 \x01(\x0c\x12\x1c\n\x10\x64\x65stination_sids\x18\x03 \x03(\tB\x02\x18\x01\x12\"\n\x16\x64\x65stination_identities\x18\x06 \x03(\tB\x02\x18\x01\x12\x12\n\x05topic\x18\x04 \x01(\tH\x00\x88\x01\x01\x12\x0f\n\x02id\x18\x08 \x01(\tH\x01\x88\x01\x01\x12\x17\n\nstart_time\x18\t \x01(\x04H\x02\x88\x01\x01\x12\x15\n\x08\x65nd_time\x18\n \x01(\x04H\x03\x88\x01\x01\x42\x08\n\x06_topicB\x05\n\x03_idB\r\n\x0b_start_timeB\x0b\n\t_end_time\"&\n\x07SipDTMF\x12\x0c\n\x04\x63ode\x18\x03 \x01(\r\x12\r\n\x05\x64igit\x18\x04 \x01(\t\"|\n\rTranscription\x12(\n transcribed_participant_identity\x18\x02 \x01(\t\x12\x10\n\x08track_id\x18\x03 \x01(\t\x12/\n\x08segments\x18\x04 \x03(\x0b\x32\x1d.livekit.TranscriptionSegment\"w\n\x14TranscriptionSegment\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x12\n\nstart_time\x18\x03 \x01(\x04\x12\x10\n\x08\x65nd_time\x18\x04 \x01(\x04\x12\r\n\x05\x66inal\x18\x05 \x01(\x08\x12\x10\n\x08language\x18\x06 \x01(\t\"\x91\x01\n\x0b\x43hatMessage\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\x12\x1b\n\x0e\x65\x64it_timestamp\x18\x03 \x01(\x03H\x00\x88\x01\x01\x12\x0f\n\x07message\x18\x04 \x01(\t\x12\x0f\n\x07\x64\x65leted\x18\x05 \x01(\x08\x12\x11\n\tgenerated\x18\x06 \x01(\x08\x42\x11\n\x0f_edit_timestamp\"g\n\nRpcRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06method\x18\x02 \x01(\t\x12\x0f\n\x07payload\x18\x03 \x01(\t\x12\x1b\n\x13response_timeout_ms\x18\x04 \x01(\r\x12\x0f\n\x07version\x18\x05 \x01(\r\"\x1c\n\x06RpcAck\x12\x12\n\nrequest_id\x18\x01 \x01(\t\"a\n\x0bRpcResponse\x12\x12\n\nrequest_id\x18\x01 \x01(\t\x12\x11\n\x07payload\x18\x02 \x01(\tH\x00\x12\"\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x11.livekit.RpcErrorH\x00\x42\x07\n\x05value\"7\n\x08RpcError\x12\x0c\n\x04\x63ode\x18\x01 \x01(\r\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\t\"@\n\x11ParticipantTracks\x12\x17\n\x0fparticipant_sid\x18\x01 \x01(\t\x12\x12\n\ntrack_sids\x18\x02 \x03(\t\"\xce\x01\n\nServerInfo\x12,\n\x07\x65\x64ition\x18\x01 \x01(\x0e\x32\x1b.livekit.ServerInfo.Edition\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x10\n\x08protocol\x18\x03 \x01(\x05\x12\x0e\n\x06region\x18\x04 \x01(\t\x12\x0f\n\x07node_id\x18\x05 \x01(\t\x12\x12\n\ndebug_info\x18\x06 \x01(\t\x12\x16\n\x0e\x61gent_protocol\x18\x07 \x01(\x05\"\"\n\x07\x45\x64ition\x12\x0c\n\x08Standard\x10\x00\x12\t\n\x05\x43loud\x10\x01\"\x8a\x03\n\nClientInfo\x12$\n\x03sdk\x18\x01 \x01(\x0e\x32\x17.livekit.ClientInfo.SDK\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x10\n\x08protocol\x18\x03 \x01(\x05\x12\n\n\x02os\x18\x04 \x01(\t\x12\x12\n\nos_version\x18\x05 \x01(\t\x12\x14\n\x0c\x64\x65vice_model\x18\x06 \x01(\t\x12\x0f\n\x07\x62rowser\x18\x07 \x01(\t\x12\x17\n\x0f\x62rowser_version\x18\x08 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\t \x01(\t\x12\x0f\n\x07network\x18\n \x01(\t\x12\x12\n\nother_sdks\x18\x0b \x01(\t\"\x9c\x01\n\x03SDK\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x06\n\x02JS\x10\x01\x12\t\n\x05SWIFT\x10\x02\x12\x0b\n\x07\x41NDROID\x10\x03\x12\x0b\n\x07\x46LUTTER\x10\x04\x12\x06\n\x02GO\x10\x05\x12\t\n\x05UNITY\x10\x06\x12\x10\n\x0cREACT_NATIVE\x10\x07\x12\x08\n\x04RUST\x10\x08\x12\n\n\x06PYTHON\x10\t\x12\x07\n\x03\x43PP\x10\n\x12\r\n\tUNITY_WEB\x10\x0b\x12\x08\n\x04NODE\x10\x0c\"\x8c\x02\n\x13\x43lientConfiguration\x12*\n\x05video\x18\x01 \x01(\x0b\x32\x1b.livekit.VideoConfiguration\x12+\n\x06screen\x18\x02 \x01(\x0b\x32\x1b.livekit.VideoConfiguration\x12\x37\n\x11resume_connection\x18\x03 \x01(\x0e\x32\x1c.livekit.ClientConfigSetting\x12\x30\n\x0f\x64isabled_codecs\x18\x04 \x01(\x0b\x32\x17.livekit.DisabledCodecs\x12\x31\n\x0b\x66orce_relay\x18\x05 \x01(\x0e\x32\x1c.livekit.ClientConfigSetting\"L\n\x12VideoConfiguration\x12\x36\n\x10hardware_encoder\x18\x01 \x01(\x0e\x32\x1c.livekit.ClientConfigSetting\"Q\n\x0e\x44isabledCodecs\x12\x1e\n\x06\x63odecs\x18\x01 \x03(\x0b\x32\x0e.livekit.Codec\x12\x1f\n\x07publish\x18\x02 \x03(\x0b\x32\x0e.livekit.Codec\"\x80\x02\n\x08RTPDrift\x12.\n\nstart_time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x10\n\x08\x64uration\x18\x03 \x01(\x01\x12\x17\n\x0fstart_timestamp\x18\x04 \x01(\x04\x12\x15\n\rend_timestamp\x18\x05 \x01(\x04\x12\x17\n\x0frtp_clock_ticks\x18\x06 \x01(\x04\x12\x15\n\rdrift_samples\x18\x07 \x01(\x03\x12\x10\n\x08\x64rift_ms\x18\x08 \x01(\x01\x12\x12\n\nclock_rate\x18\t \x01(\x01\"\xd6\n\n\x08RTPStats\x12.\n\nstart_time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x10\n\x08\x64uration\x18\x03 \x01(\x01\x12\x0f\n\x07packets\x18\x04 \x01(\r\x12\x13\n\x0bpacket_rate\x18\x05 \x01(\x01\x12\r\n\x05\x62ytes\x18\x06 \x01(\x04\x12\x14\n\x0cheader_bytes\x18\' \x01(\x04\x12\x0f\n\x07\x62itrate\x18\x07 \x01(\x01\x12\x14\n\x0cpackets_lost\x18\x08 \x01(\r\x12\x18\n\x10packet_loss_rate\x18\t \x01(\x01\x12\x1e\n\x16packet_loss_percentage\x18\n \x01(\x02\x12\x19\n\x11packets_duplicate\x18\x0b \x01(\r\x12\x1d\n\x15packet_duplicate_rate\x18\x0c \x01(\x01\x12\x17\n\x0f\x62ytes_duplicate\x18\r \x01(\x04\x12\x1e\n\x16header_bytes_duplicate\x18( \x01(\x04\x12\x19\n\x11\x62itrate_duplicate\x18\x0e \x01(\x01\x12\x17\n\x0fpackets_padding\x18\x0f \x01(\r\x12\x1b\n\x13packet_padding_rate\x18\x10 \x01(\x01\x12\x15\n\rbytes_padding\x18\x11 \x01(\x04\x12\x1c\n\x14header_bytes_padding\x18) \x01(\x04\x12\x17\n\x0f\x62itrate_padding\x18\x12 \x01(\x01\x12\x1c\n\x14packets_out_of_order\x18\x13 \x01(\r\x12\x0e\n\x06\x66rames\x18\x14 \x01(\r\x12\x12\n\nframe_rate\x18\x15 \x01(\x01\x12\x16\n\x0ejitter_current\x18\x16 \x01(\x01\x12\x12\n\njitter_max\x18\x17 \x01(\x01\x12:\n\rgap_histogram\x18\x18 \x03(\x0b\x32#.livekit.RTPStats.GapHistogramEntry\x12\r\n\x05nacks\x18\x19 \x01(\r\x12\x11\n\tnack_acks\x18% \x01(\r\x12\x13\n\x0bnack_misses\x18\x1a \x01(\r\x12\x15\n\rnack_repeated\x18& \x01(\r\x12\x0c\n\x04plis\x18\x1b \x01(\r\x12,\n\x08last_pli\x18\x1c \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0c\n\x04\x66irs\x18\x1d \x01(\r\x12,\n\x08last_fir\x18\x1e \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x13\n\x0brtt_current\x18\x1f \x01(\r\x12\x0f\n\x07rtt_max\x18  \x01(\r\x12\x12\n\nkey_frames\x18! \x01(\r\x12\x32\n\x0elast_key_frame\x18\" \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x17\n\x0flayer_lock_plis\x18# \x01(\r\x12\x37\n\x13last_layer_lock_pli\x18$ \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\'\n\x0cpacket_drift\x18, \x01(\x0b\x32\x11.livekit.RTPDrift\x12+\n\x10ntp_report_drift\x18- \x01(\x0b\x32\x11.livekit.RTPDrift\x12/\n\x14rebased_report_drift\x18. \x01(\x0b\x32\x11.livekit.RTPDrift\x12\x30\n\x15received_report_drift\x18/ \x01(\x0b\x32\x11.livekit.RTPDrift\x1a\x33\n\x11GapHistogramEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\r:\x02\x38\x01\"\xa2\x01\n\x15RTCPSenderReportState\x12\x15\n\rrtp_timestamp\x18\x01 \x01(\r\x12\x19\n\x11rtp_timestamp_ext\x18\x02 \x01(\x04\x12\x15\n\rntp_timestamp\x18\x03 \x01(\x04\x12\n\n\x02\x61t\x18\x04 \x01(\x03\x12\x13\n\x0b\x61t_adjusted\x18\x05 \x01(\x03\x12\x0f\n\x07packets\x18\x06 \x01(\r\x12\x0e\n\x06octets\x18\x07 \x01(\x04\"\xc9\x02\n\x11RTPForwarderState\x12\x0f\n\x07started\x18\x01 \x01(\x08\x12\x1f\n\x17reference_layer_spatial\x18\x02 \x01(\x05\x12\x16\n\x0epre_start_time\x18\x03 \x01(\x03\x12\x1b\n\x13\x65xt_first_timestamp\x18\x04 \x01(\x04\x12$\n\x1c\x64ummy_start_timestamp_offset\x18\x05 \x01(\x04\x12+\n\nrtp_munger\x18\x06 \x01(\x0b\x32\x17.livekit.RTPMungerState\x12-\n\nvp8_munger\x18\x07 \x01(\x0b\x32\x17.livekit.VP8MungerStateH\x00\x12;\n\x13sender_report_state\x18\x08 \x03(\x0b\x32\x1e.livekit.RTCPSenderReportStateB\x0e\n\x0c\x63odec_munger\"\xcb\x01\n\x0eRTPMungerState\x12 \n\x18\x65xt_last_sequence_number\x18\x01 \x01(\x04\x12\'\n\x1f\x65xt_second_last_sequence_number\x18\x02 \x01(\x04\x12\x1a\n\x12\x65xt_last_timestamp\x18\x03 \x01(\x04\x12!\n\x19\x65xt_second_last_timestamp\x18\x04 \x01(\x04\x12\x13\n\x0blast_marker\x18\x05 \x01(\x08\x12\x1a\n\x12second_last_marker\x18\x06 \x01(\x08\"\xb8\x01\n\x0eVP8MungerState\x12\x1b\n\x13\x65xt_last_picture_id\x18\x01 \x01(\x05\x12\x17\n\x0fpicture_id_used\x18\x02 \x01(\x08\x12\x18\n\x10last_tl0_pic_idx\x18\x03 \x01(\r\x12\x18\n\x10tl0_pic_idx_used\x18\x04 \x01(\x08\x12\x10\n\x08tid_used\x18\x05 \x01(\x08\x12\x14\n\x0clast_key_idx\x18\x06 \x01(\r\x12\x14\n\x0ckey_idx_used\x18\x07 \x01(\x08\"1\n\x0cTimedVersion\x12\x12\n\nunix_micro\x18\x01 \x01(\x03\x12\r\n\x05ticks\x18\x02 \x01(\x05*/\n\nAudioCodec\x12\x0e\n\nDEFAULT_AC\x10\x00\x12\x08\n\x04OPUS\x10\x01\x12\x07\n\x03\x41\x41\x43\x10\x02*V\n\nVideoCodec\x12\x0e\n\nDEFAULT_VC\x10\x00\x12\x11\n\rH264_BASELINE\x10\x01\x12\r\n\tH264_MAIN\x10\x02\x12\r\n\tH264_HIGH\x10\x03\x12\x07\n\x03VP8\x10\x04*)\n\nImageCodec\x12\x0e\n\nIC_DEFAULT\x10\x00\x12\x0b\n\x07IC_JPEG\x10\x01*+\n\tTrackType\x12\t\n\x05\x41UDIO\x10\x00\x12\t\n\x05VIDEO\x10\x01\x12\x08\n\x04\x44\x41TA\x10\x02*`\n\x0bTrackSource\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06\x43\x41MERA\x10\x01\x12\x0e\n\nMICROPHONE\x10\x02\x12\x10\n\x0cSCREEN_SHARE\x10\x03\x12\x16\n\x12SCREEN_SHARE_AUDIO\x10\x04*6\n\x0cVideoQuality\x12\x07\n\x03LOW\x10\x00\x12\n\n\x06MEDIUM\x10\x01\x12\x08\n\x04HIGH\x10\x02\x12\x07\n\x03OFF\x10\x03*@\n\x11\x43onnectionQuality\x12\x08\n\x04POOR\x10\x00\x12\x08\n\x04GOOD\x10\x01\x12\r\n\tEXCELLENT\x10\x02\x12\x08\n\x04LOST\x10\x03*;\n\x13\x43lientConfigSetting\x12\t\n\x05UNSET\x10\x00\x12\x0c\n\x08\x44ISABLED\x10\x01\x12\x0b\n\x07\x45NABLED\x10\x02*\xec\x01\n\x10\x44isconnectReason\x12\x12\n\x0eUNKNOWN_REASON\x10\x00\x12\x14\n\x10\x43LIENT_INITIATED\x10\x01\x12\x16\n\x12\x44UPLICATE_IDENTITY\x10\x02\x12\x13\n\x0fSERVER_SHUTDOWN\x10\x03\x12\x17\n\x13PARTICIPANT_REMOVED\x10\x04\x12\x10\n\x0cROOM_DELETED\x10\x05\x12\x12\n\x0eSTATE_MISMATCH\x10\x06\x12\x10\n\x0cJOIN_FAILURE\x10\x07\x12\r\n\tMIGRATION\x10\x08\x12\x10\n\x0cSIGNAL_CLOSE\x10\t\x12\x0f\n\x0bROOM_CLOSED\x10\n*\x89\x01\n\x0fReconnectReason\x12\x0e\n\nRR_UNKNOWN\x10\x00\x12\x1a\n\x16RR_SIGNAL_DISCONNECTED\x10\x01\x12\x17\n\x13RR_PUBLISHER_FAILED\x10\x02\x12\x18\n\x14RR_SUBSCRIBER_FAILED\x10\x03\x12\x17\n\x13RR_SWITCH_CANDIDATE\x10\x04*T\n\x11SubscriptionError\x12\x0e\n\nSE_UNKNOWN\x10\x00\x12\x18\n\x14SE_CODEC_UNSUPPORTED\x10\x01\x12\x15\n\x11SE_TRACK_NOTFOUND\x10\x02*\xa3\x01\n\x11\x41udioTrackFeature\x12\r\n\tTF_STEREO\x10\x00\x12\r\n\tTF_NO_DTX\x10\x01\x12\x18\n\x14TF_AUTO_GAIN_CONTROL\x10\x02\x12\x18\n\x14TF_ECHO_CANCELLATION\x10\x03\x12\x18\n\x14TF_NOISE_SUPPRESSION\x10\x04\x12\"\n\x1eTF_ENHANCED_NOISE_CANCELLATION\x10\x05\x42\x46Z#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_PARTICIPANTPERMISSION'].fields_by_name['recorder']._options = None
  _globals['_PARTICIPANTPERMISSION'].fields_by_name['recorder']._serialized_options = b'\030\001'
  _globals['_PARTICIPANTPERMISSION'].fields_by_name['agent']._options = None
  _globals['_PARTICIPANTPERMISSION'].fields_by_name['agent']._serialized_options = b'\030\001'
  _globals['_PARTICIPANTINFO_ATTRIBUTESENTRY']._options = None
  _globals['_PARTICIPANTINFO_ATTRIBUTESENTRY']._serialized_options = b'8\001'
  _globals['_DATAPACKET'].fields_by_name['kind']._options = None
  _globals['_DATAPACKET'].fields_by_name['kind']._serialized_options = b'\030\001'
  _globals['_DATAPACKET'].fields_by_name['speaker']._options = None
  _globals['_DATAPACKET'].fields_by_name['speaker']._serialized_options = b'\030\001'
  _globals['_USERPACKET'].fields_by_name['participant_sid']._options = None
  _globals['_USERPACKET'].fields_by_name['participant_sid']._serialized_options = b'\030\001'
  _globals['_USERPACKET'].fields_by_name['participant_identity']._options = None
  _globals['_USERPACKET'].fields_by_name['participant_identity']._serialized_options = b'\030\001'
  _globals['_USERPACKET'].fields_by_name['destination_sids']._options = None
  _globals['_USERPACKET'].fields_by_name['destination_sids']._serialized_options = b'\030\001'
  _globals['_USERPACKET'].fields_by_name['destination_identities']._options = None
  _globals['_USERPACKET'].fields_by_name['destination_identities']._serialized_options = b'\030\001'
  _globals['_RTPSTATS_GAPHISTOGRAMENTRY']._options = None
  _globals['_RTPSTATS_GAPHISTOGRAMENTRY']._serialized_options = b'8\001'
  _globals['_AUDIOCODEC']._serialized_start=7564
  _globals['_AUDIOCODEC']._serialized_end=7611
  _globals['_VIDEOCODEC']._serialized_start=7613
  _globals['_VIDEOCODEC']._serialized_end=7699
  _globals['_IMAGECODEC']._serialized_start=7701
  _globals['_IMAGECODEC']._serialized_end=7742
  _globals['_TRACKTYPE']._serialized_start=7744
  _globals['_TRACKTYPE']._serialized_end=7787
  _globals['_TRACKSOURCE']._serialized_start=7789
  _globals['_TRACKSOURCE']._serialized_end=7885
  _globals['_VIDEOQUALITY']._serialized_start=7887
  _globals['_VIDEOQUALITY']._serialized_end=7941
  _globals['_CONNECTIONQUALITY']._serialized_start=7943
  _globals['_CONNECTIONQUALITY']._serialized_end=8007
  _globals['_CLIENTCONFIGSETTING']._serialized_start=8009
  _globals['_CLIENTCONFIGSETTING']._serialized_end=8068
  _globals['_DISCONNECTREASON']._serialized_start=8071
  _globals['_DISCONNECTREASON']._serialized_end=8307
  _globals['_RECONNECTREASON']._serialized_start=8310
  _globals['_RECONNECTREASON']._serialized_end=8447
  _globals['_SUBSCRIPTIONERROR']._serialized_start=8449
  _globals['_SUBSCRIPTIONERROR']._serialized_end=8533
  _globals['_AUDIOTRACKFEATURE']._serialized_start=8536
  _globals['_AUDIOTRACKFEATURE']._serialized_end=8699
  _globals['_ROOM']._serialized_start=90
  _globals['_ROOM']._serialized_end=419
  _globals['_CODEC']._serialized_start=421
  _globals['_CODEC']._serialized_end=461
  _globals['_PLAYOUTDELAY']._serialized_start=463
  _globals['_PLAYOUTDELAY']._serialized_end=520
  _globals['_PARTICIPANTPERMISSION']._serialized_start=523
  _globals['_PARTICIPANTPERMISSION']._serialized_end=784
  _globals['_PARTICIPANTINFO']._serialized_start=787
  _globals['_PARTICIPANTINFO']._serialized_end=1419
  _globals['_PARTICIPANTINFO_ATTRIBUTESENTRY']._serialized_start=1239
  _globals['_PARTICIPANTINFO_ATTRIBUTESENTRY']._serialized_end=1288
  _globals['_PARTICIPANTINFO_STATE']._serialized_start=1290
  _globals['_PARTICIPANTINFO_STATE']._serialized_end=1352
  _globals['_PARTICIPANTINFO_KIND']._serialized_start=1354
  _globals['_PARTICIPANTINFO_KIND']._serialized_end=1419
  _globals['_ENCRYPTION']._serialized_start=1421
  _globals['_ENCRYPTION']._serialized_end=1472
  _globals['_ENCRYPTION_TYPE']._serialized_start=1435
  _globals['_ENCRYPTION_TYPE']._serialized_end=1472
  _globals['_SIMULCASTCODECINFO']._serialized_start=1474
  _globals['_SIMULCASTCODECINFO']._serialized_end=1576
  _globals['_TRACKINFO']._serialized_start=1579
  _globals['_TRACKINFO']._serialized_end=2080
  _globals['_VIDEOLAYER']._serialized_start=2082
  _globals['_VIDEOLAYER']._serialized_end=2196
  _globals['_DATAPACKET']._serialized_start=2199
  _globals['_DATAPACKET']._serialized_end=2750
  _globals['_DATAPACKET_KIND']._serialized_start=2710
  _globals['_DATAPACKET_KIND']._serialized_end=2741
  _globals['_ACTIVESPEAKERUPDATE']._serialized_start=2752
  _globals['_ACTIVESPEAKERUPDATE']._serialized_end=2813
  _globals['_SPEAKERINFO']._serialized_start=2815
  _globals['_SPEAKERINFO']._serialized_end=2872
  _globals['_USERPACKET']._serialized_start=2875
  _globals['_USERPACKET']._serialized_end=3163
  _globals['_SIPDTMF']._serialized_start=3165
  _globals['_SIPDTMF']._serialized_end=3203
  _globals['_TRANSCRIPTION']._serialized_start=3205
  _globals['_TRANSCRIPTION']._serialized_end=3329
  _globals['_TRANSCRIPTIONSEGMENT']._serialized_start=3331
  _globals['_TRANSCRIPTIONSEGMENT']._serialized_end=3450
  _globals['_CHATMESSAGE']._serialized_start=3453
  _globals['_CHATMESSAGE']._serialized_end=3598
  _globals['_RPCREQUEST']._serialized_start=3600
  _globals['_RPCREQUEST']._serialized_end=3703
  _globals['_RPCACK']._serialized_start=3705
  _globals['_RPCACK']._serialized_end=3733
  _globals['_RPCRESPONSE']._serialized_start=3735
  _globals['_RPCRESPONSE']._serialized_end=3832
  _globals['_RPCERROR']._serialized_start=3834
  _globals['_RPCERROR']._serialized_end=3889
  _globals['_PARTICIPANTTRACKS']._serialized_start=3891
  _globals['_PARTICIPANTTRACKS']._serialized_end=3955
  _globals['_SERVERINFO']._serialized_start=3958
  _globals['_SERVERINFO']._serialized_end=4164
  _globals['_SERVERINFO_EDITION']._serialized_start=4130
  _globals['_SERVERINFO_EDITION']._serialized_end=4164
  _globals['_CLIENTINFO']._serialized_start=4167
  _globals['_CLIENTINFO']._serialized_end=4561
  _globals['_CLIENTINFO_SDK']._serialized_start=4405
  _globals['_CLIENTINFO_SDK']._serialized_end=4561
  _globals['_CLIENTCONFIGURATION']._serialized_start=4564
  _globals['_CLIENTCONFIGURATION']._serialized_end=4832
  _globals['_VIDEOCONFIGURATION']._serialized_start=4834
  _globals['_VIDEOCONFIGURATION']._serialized_end=4910
  _globals['_DISABLEDCODECS']._serialized_start=4912
  _globals['_DISABLEDCODECS']._serialized_end=4993
  _globals['_RTPDRIFT']._serialized_start=4996
  _globals['_RTPDRIFT']._serialized_end=5252
  _globals['_RTPSTATS']._serialized_start=5255
  _globals['_RTPSTATS']._serialized_end=6621
  _globals['_RTPSTATS_GAPHISTOGRAMENTRY']._serialized_start=6570
  _globals['_RTPSTATS_GAPHISTOGRAMENTRY']._serialized_end=6621
  _globals['_RTCPSENDERREPORTSTATE']._serialized_start=6624
  _globals['_RTCPSENDERREPORTSTATE']._serialized_end=6786
  _globals['_RTPFORWARDERSTATE']._serialized_start=6789
  _globals['_RTPFORWARDERSTATE']._serialized_end=7118
  _globals['_RTPMUNGERSTATE']._serialized_start=7121
  _globals['_RTPMUNGERSTATE']._serialized_end=7324
  _globals['_VP8MUNGERSTATE']._serialized_start=7327
  _globals['_VP8MUNGERSTATE']._serialized_end=7511
  _globals['_TIMEDVERSION']._serialized_start=7513
  _globals['_TIMEDVERSION']._serialized_end=7562
# @@protoc_insertion_point(module_scope)
