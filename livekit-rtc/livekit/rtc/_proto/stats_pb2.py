# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: stats.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bstats.proto\x12\rlivekit.proto\"\xd9\x17\n\x08RtcStats\x12.\n\x05\x63odec\x18\x03 \x01(\x0b\x32\x1d.livekit.proto.RtcStats.CodecH\x00\x12\x39\n\x0binbound_rtp\x18\x04 \x01(\x0b\x32\".livekit.proto.RtcStats.InboundRtpH\x00\x12;\n\x0coutbound_rtp\x18\x05 \x01(\x0b\x32#.livekit.proto.RtcStats.OutboundRtpH\x00\x12\x46\n\x12remote_inbound_rtp\x18\x06 \x01(\x0b\x32(.livekit.proto.RtcStats.RemoteInboundRtpH\x00\x12H\n\x13remote_outbound_rtp\x18\x07 \x01(\x0b\x32).livekit.proto.RtcStats.RemoteOutboundRtpH\x00\x12;\n\x0cmedia_source\x18\x08 \x01(\x0b\x32#.livekit.proto.RtcStats.MediaSourceH\x00\x12=\n\rmedia_playout\x18\t \x01(\x0b\x32$.livekit.proto.RtcStats.MediaPlayoutH\x00\x12\x41\n\x0fpeer_connection\x18\n \x01(\x0b\x32&.livekit.proto.RtcStats.PeerConnectionH\x00\x12;\n\x0c\x64\x61ta_channel\x18\x0b \x01(\x0b\x32#.livekit.proto.RtcStats.DataChannelH\x00\x12\x36\n\ttransport\x18\x0c \x01(\x0b\x32!.livekit.proto.RtcStats.TransportH\x00\x12?\n\x0e\x63\x61ndidate_pair\x18\r \x01(\x0b\x32%.livekit.proto.RtcStats.CandidatePairH\x00\x12\x41\n\x0flocal_candidate\x18\x0e \x01(\x0b\x32&.livekit.proto.RtcStats.LocalCandidateH\x00\x12\x43\n\x10remote_candidate\x18\x0f \x01(\x0b\x32\'.livekit.proto.RtcStats.RemoteCandidateH\x00\x12:\n\x0b\x63\x65rtificate\x18\x10 \x01(\x0b\x32#.livekit.proto.RtcStats.CertificateH\x00\x12.\n\x05track\x18\x11 \x01(\x0b\x32\x1d.livekit.proto.RtcStats.TrackH\x00\x1a[\n\x05\x43odec\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12(\n\x05\x63odec\x18\x02 \x02(\x0b\x32\x19.livekit.proto.CodecStats\x1a\xd5\x01\n\nInboundRtp\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12-\n\x06stream\x18\x02 \x02(\x0b\x32\x1d.livekit.proto.RtpStreamStats\x12\x37\n\x08received\x18\x03 \x02(\x0b\x32%.livekit.proto.ReceivedRtpStreamStats\x12\x35\n\x07inbound\x18\x04 \x02(\x0b\x32$.livekit.proto.InboundRtpStreamStats\x1a\xd0\x01\n\x0bOutboundRtp\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12-\n\x06stream\x18\x02 \x02(\x0b\x32\x1d.livekit.proto.RtpStreamStats\x12/\n\x04sent\x18\x03 \x02(\x0b\x32!.livekit.proto.SentRtpStreamStats\x12\x37\n\x08outbound\x18\x04 \x02(\x0b\x32%.livekit.proto.OutboundRtpStreamStats\x1a\xe8\x01\n\x10RemoteInboundRtp\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12-\n\x06stream\x18\x02 \x02(\x0b\x32\x1d.livekit.proto.RtpStreamStats\x12\x37\n\x08received\x18\x03 \x02(\x0b\x32%.livekit.proto.ReceivedRtpStreamStats\x12\x42\n\x0eremote_inbound\x18\x04 \x02(\x0b\x32*.livekit.proto.RemoteInboundRtpStreamStats\x1a\xe3\x01\n\x11RemoteOutboundRtp\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12-\n\x06stream\x18\x02 \x02(\x0b\x32\x1d.livekit.proto.RtpStreamStats\x12/\n\x04sent\x18\x03 \x02(\x0b\x32!.livekit.proto.SentRtpStreamStats\x12\x44\n\x0fremote_outbound\x18\x04 \x02(\x0b\x32+.livekit.proto.RemoteOutboundRtpStreamStats\x1a\xc8\x01\n\x0bMediaSource\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12/\n\x06source\x18\x02 \x02(\x0b\x32\x1f.livekit.proto.MediaSourceStats\x12.\n\x05\x61udio\x18\x03 \x02(\x0b\x32\x1f.livekit.proto.AudioSourceStats\x12.\n\x05video\x18\x04 \x02(\x0b\x32\x1f.livekit.proto.VideoSourceStats\x1aq\n\x0cMediaPlayout\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12\x37\n\raudio_playout\x18\x02 \x02(\x0b\x32 .livekit.proto.AudioPlayoutStats\x1aj\n\x0ePeerConnection\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12.\n\x02pc\x18\x02 \x02(\x0b\x32\".livekit.proto.PeerConnectionStats\x1a\x64\n\x0b\x44\x61taChannel\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12+\n\x02\x64\x63\x18\x02 \x02(\x0b\x32\x1f.livekit.proto.DataChannelStats\x1ag\n\tTransport\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12\x30\n\ttransport\x18\x02 \x02(\x0b\x32\x1d.livekit.proto.TransportStats\x1at\n\rCandidatePair\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12\x39\n\x0e\x63\x61ndidate_pair\x18\x02 \x02(\x0b\x32!.livekit.proto.CandidatePairStats\x1ao\n\x0eLocalCandidate\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12\x33\n\tcandidate\x18\x02 \x02(\x0b\x32 .livekit.proto.IceCandidateStats\x1ap\n\x0fRemoteCandidate\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12\x33\n\tcandidate\x18\x02 \x02(\x0b\x32 .livekit.proto.IceCandidateStats\x1am\n\x0b\x43\x65rtificate\x12(\n\x03rtc\x18\x01 \x02(\x0b\x32\x1b.livekit.proto.RtcStatsData\x12\x34\n\x0b\x63\x65rtificate\x18\x02 \x02(\x0b\x32\x1f.livekit.proto.CertificateStats\x1a\x07\n\x05TrackB\x07\n\x05stats\"-\n\x0cRtcStatsData\x12\n\n\x02id\x18\x01 \x02(\t\x12\x11\n\ttimestamp\x18\x02 \x02(\x03\"\x88\x01\n\nCodecStats\x12\x14\n\x0cpayload_type\x18\x01 \x02(\r\x12\x14\n\x0ctransport_id\x18\x02 \x02(\t\x12\x11\n\tmime_type\x18\x03 \x02(\t\x12\x12\n\nclock_rate\x18\x04 \x02(\r\x12\x10\n\x08\x63hannels\x18\x05 \x02(\r\x12\x15\n\rsdp_fmtp_line\x18\x06 \x02(\t\"T\n\x0eRtpStreamStats\x12\x0c\n\x04ssrc\x18\x01 \x02(\r\x12\x0c\n\x04kind\x18\x02 \x02(\t\x12\x14\n\x0ctransport_id\x18\x03 \x02(\t\x12\x10\n\x08\x63odec_id\x18\x04 \x02(\t\"X\n\x16ReceivedRtpStreamStats\x12\x18\n\x10packets_received\x18\x01 \x02(\x04\x12\x14\n\x0cpackets_lost\x18\x02 \x02(\x03\x12\x0e\n\x06jitter\x18\x03 \x02(\x01\"\x82\x0c\n\x15InboundRtpStreamStats\x12\x18\n\x10track_identifier\x18\x01 \x02(\t\x12\x0b\n\x03mid\x18\x02 \x02(\t\x12\x11\n\tremote_id\x18\x03 \x02(\t\x12\x16\n\x0e\x66rames_decoded\x18\x04 \x02(\r\x12\x1a\n\x12key_frames_decoded\x18\x05 \x02(\r\x12\x17\n\x0f\x66rames_rendered\x18\x06 \x02(\r\x12\x16\n\x0e\x66rames_dropped\x18\x07 \x02(\r\x12\x13\n\x0b\x66rame_width\x18\x08 \x02(\r\x12\x14\n\x0c\x66rame_height\x18\t \x02(\r\x12\x19\n\x11\x66rames_per_second\x18\n \x02(\x01\x12\x0e\n\x06qp_sum\x18\x0b \x02(\x04\x12\x19\n\x11total_decode_time\x18\x0c \x02(\x01\x12\x1f\n\x17total_inter_frame_delay\x18\r \x02(\x01\x12\'\n\x1ftotal_squared_inter_frame_delay\x18\x0e \x02(\x01\x12\x13\n\x0bpause_count\x18\x0f \x02(\r\x12\x1c\n\x14total_pause_duration\x18\x10 \x02(\x01\x12\x14\n\x0c\x66reeze_count\x18\x11 \x02(\r\x12\x1d\n\x15total_freeze_duration\x18\x12 \x02(\x01\x12&\n\x1elast_packet_received_timestamp\x18\x13 \x02(\x01\x12\x1d\n\x15header_bytes_received\x18\x14 \x02(\x04\x12\x19\n\x11packets_discarded\x18\x15 \x02(\x04\x12\x1a\n\x12\x66\x65\x63_bytes_received\x18\x16 \x02(\x04\x12\x1c\n\x14\x66\x65\x63_packets_received\x18\x17 \x02(\x04\x12\x1d\n\x15\x66\x65\x63_packets_discarded\x18\x18 \x02(\x04\x12\x16\n\x0e\x62ytes_received\x18\x19 \x02(\x04\x12\x12\n\nnack_count\x18\x1a \x02(\r\x12\x11\n\tfir_count\x18\x1b \x02(\r\x12\x11\n\tpli_count\x18\x1c \x02(\r\x12\x1e\n\x16total_processing_delay\x18\x1d \x02(\x01\x12#\n\x1b\x65stimated_playout_timestamp\x18\x1e \x02(\x01\x12\x1b\n\x13jitter_buffer_delay\x18\x1f \x02(\x01\x12\"\n\x1ajitter_buffer_target_delay\x18  \x02(\x01\x12#\n\x1bjitter_buffer_emitted_count\x18! \x02(\x04\x12#\n\x1bjitter_buffer_minimum_delay\x18\" \x02(\x01\x12\x1e\n\x16total_samples_received\x18# \x02(\x04\x12\x19\n\x11\x63oncealed_samples\x18$ \x02(\x04\x12 \n\x18silent_concealed_samples\x18% \x02(\x04\x12\x1a\n\x12\x63oncealment_events\x18& \x02(\x04\x12)\n!inserted_samples_for_deceleration\x18\' \x02(\x04\x12(\n removed_samples_for_acceleration\x18( \x02(\x04\x12\x13\n\x0b\x61udio_level\x18) \x02(\x01\x12\x1a\n\x12total_audio_energy\x18* \x02(\x01\x12\x1e\n\x16total_samples_duration\x18+ \x02(\x01\x12\x17\n\x0f\x66rames_received\x18, \x02(\x04\x12\x1e\n\x16\x64\x65\x63oder_implementation\x18- \x02(\t\x12\x12\n\nplayout_id\x18. \x02(\t\x12\x1f\n\x17power_efficient_decoder\x18/ \x02(\x08\x12.\n&frames_assembled_from_multiple_packets\x18\x30 \x02(\x04\x12\x1b\n\x13total_assembly_time\x18\x31 \x02(\x01\x12&\n\x1eretransmitted_packets_received\x18\x32 \x02(\x04\x12$\n\x1cretransmitted_bytes_received\x18\x33 \x02(\x04\x12\x10\n\x08rtx_ssrc\x18\x34 \x02(\r\x12\x10\n\x08\x66\x65\x63_ssrc\x18\x35 \x02(\r\">\n\x12SentRtpStreamStats\x12\x14\n\x0cpackets_sent\x18\x01 \x02(\x04\x12\x12\n\nbytes_sent\x18\x02 \x02(\x04\"\xd1\x07\n\x16OutboundRtpStreamStats\x12\x0b\n\x03mid\x18\x01 \x02(\t\x12\x17\n\x0fmedia_source_id\x18\x02 \x02(\t\x12\x11\n\tremote_id\x18\x03 \x02(\t\x12\x0b\n\x03rid\x18\x04 \x02(\t\x12\x19\n\x11header_bytes_sent\x18\x05 \x02(\x04\x12\"\n\x1aretransmitted_packets_sent\x18\x06 \x02(\x04\x12 \n\x18retransmitted_bytes_sent\x18\x07 \x02(\x04\x12\x10\n\x08rtx_ssrc\x18\x08 \x02(\r\x12\x16\n\x0etarget_bitrate\x18\t \x02(\x01\x12\"\n\x1atotal_encoded_bytes_target\x18\n \x02(\x04\x12\x13\n\x0b\x66rame_width\x18\x0b \x02(\r\x12\x14\n\x0c\x66rame_height\x18\x0c \x02(\r\x12\x19\n\x11\x66rames_per_second\x18\r \x02(\x01\x12\x13\n\x0b\x66rames_sent\x18\x0e \x02(\r\x12\x18\n\x10huge_frames_sent\x18\x0f \x02(\r\x12\x16\n\x0e\x66rames_encoded\x18\x10 \x02(\r\x12\x1a\n\x12key_frames_encoded\x18\x11 \x02(\r\x12\x0e\n\x06qp_sum\x18\x12 \x02(\x04\x12\x19\n\x11total_encode_time\x18\x13 \x02(\x01\x12\x1f\n\x17total_packet_send_delay\x18\x14 \x02(\x01\x12I\n\x19quality_limitation_reason\x18\x15 \x02(\x0e\x32&.livekit.proto.QualityLimitationReason\x12k\n\x1cquality_limitation_durations\x18\x16 \x03(\x0b\x32\x45.livekit.proto.OutboundRtpStreamStats.QualityLimitationDurationsEntry\x12-\n%quality_limitation_resolution_changes\x18\x17 \x02(\r\x12\x12\n\nnack_count\x18\x18 \x02(\r\x12\x11\n\tfir_count\x18\x19 \x02(\r\x12\x11\n\tpli_count\x18\x1a \x02(\r\x12\x1e\n\x16\x65ncoder_implementation\x18\x1b \x02(\t\x12\x1f\n\x17power_efficient_encoder\x18\x1c \x02(\x08\x12\x0e\n\x06\x61\x63tive\x18\x1d \x02(\x08\x12\x18\n\x10scalability_mode\x18\x1e \x02(\t\x1a\x41\n\x1fQualityLimitationDurationsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x01:\x02\x38\x01\"\xa4\x01\n\x1bRemoteInboundRtpStreamStats\x12\x10\n\x08local_id\x18\x01 \x02(\t\x12\x17\n\x0fround_trip_time\x18\x02 \x02(\x01\x12\x1d\n\x15total_round_trip_time\x18\x03 \x02(\x01\x12\x15\n\rfraction_lost\x18\x04 \x02(\x01\x12$\n\x1cround_trip_time_measurements\x18\x05 \x02(\x04\"\xbe\x01\n\x1cRemoteOutboundRtpStreamStats\x12\x10\n\x08local_id\x18\x01 \x02(\t\x12\x18\n\x10remote_timestamp\x18\x02 \x02(\x01\x12\x14\n\x0creports_sent\x18\x03 \x02(\x04\x12\x17\n\x0fround_trip_time\x18\x04 \x02(\x01\x12\x1d\n\x15total_round_trip_time\x18\x05 \x02(\x01\x12$\n\x1cround_trip_time_measurements\x18\x06 \x02(\x04\":\n\x10MediaSourceStats\x12\x18\n\x10track_identifier\x18\x01 \x02(\t\x12\x0c\n\x04kind\x18\x02 \x02(\t\"\xa2\x02\n\x10\x41udioSourceStats\x12\x13\n\x0b\x61udio_level\x18\x01 \x02(\x01\x12\x1a\n\x12total_audio_energy\x18\x02 \x02(\x01\x12\x1e\n\x16total_samples_duration\x18\x03 \x02(\x01\x12\x18\n\x10\x65\x63ho_return_loss\x18\x04 \x02(\x01\x12$\n\x1c\x65\x63ho_return_loss_enhancement\x18\x05 \x02(\x01\x12 \n\x18\x64ropped_samples_duration\x18\x06 \x02(\x01\x12\x1e\n\x16\x64ropped_samples_events\x18\x07 \x02(\r\x12\x1b\n\x13total_capture_delay\x18\x08 \x02(\x01\x12\x1e\n\x16total_samples_captured\x18\t \x02(\x04\"\\\n\x10VideoSourceStats\x12\r\n\x05width\x18\x01 \x02(\r\x12\x0e\n\x06height\x18\x02 \x02(\r\x12\x0e\n\x06\x66rames\x18\x03 \x02(\r\x12\x19\n\x11\x66rames_per_second\x18\x04 \x02(\x01\"\xc5\x01\n\x11\x41udioPlayoutStats\x12\x0c\n\x04kind\x18\x01 \x02(\t\x12$\n\x1csynthesized_samples_duration\x18\x02 \x02(\x01\x12\"\n\x1asynthesized_samples_events\x18\x03 \x02(\r\x12\x1e\n\x16total_samples_duration\x18\x04 \x02(\x01\x12\x1b\n\x13total_playout_delay\x18\x05 \x02(\x01\x12\x1b\n\x13total_samples_count\x18\x06 \x02(\x04\"Q\n\x13PeerConnectionStats\x12\x1c\n\x14\x64\x61ta_channels_opened\x18\x01 \x02(\r\x12\x1c\n\x14\x64\x61ta_channels_closed\x18\x02 \x02(\r\"\xe2\x01\n\x10\x44\x61taChannelStats\x12\r\n\x05label\x18\x01 \x02(\t\x12\x10\n\x08protocol\x18\x02 \x02(\t\x12\x1f\n\x17\x64\x61ta_channel_identifier\x18\x03 \x02(\x05\x12.\n\x05state\x18\x04 \x01(\x0e\x32\x1f.livekit.proto.DataChannelState\x12\x15\n\rmessages_sent\x18\x05 \x02(\r\x12\x12\n\nbytes_sent\x18\x06 \x02(\x04\x12\x19\n\x11messages_received\x18\x07 \x02(\r\x12\x16\n\x0e\x62ytes_received\x18\x08 \x02(\x04\"\x9c\x04\n\x0eTransportStats\x12\x14\n\x0cpackets_sent\x18\x01 \x02(\x04\x12\x18\n\x10packets_received\x18\x02 \x02(\x04\x12\x12\n\nbytes_sent\x18\x03 \x02(\x04\x12\x16\n\x0e\x62ytes_received\x18\x04 \x02(\x04\x12(\n\x08ice_role\x18\x05 \x02(\x0e\x32\x16.livekit.proto.IceRole\x12#\n\x1bice_local_username_fragment\x18\x06 \x02(\t\x12\x35\n\ndtls_state\x18\x07 \x01(\x0e\x32!.livekit.proto.DtlsTransportState\x12\x33\n\tice_state\x18\x08 \x01(\x0e\x32 .livekit.proto.IceTransportState\x12\"\n\x1aselected_candidate_pair_id\x18\t \x02(\t\x12\x1c\n\x14local_certificate_id\x18\n \x02(\t\x12\x1d\n\x15remote_certificate_id\x18\x0b \x02(\t\x12\x13\n\x0btls_version\x18\x0c \x02(\t\x12\x13\n\x0b\x64tls_cipher\x18\r \x02(\t\x12*\n\tdtls_role\x18\x0e \x02(\x0e\x32\x17.livekit.proto.DtlsRole\x12\x13\n\x0bsrtp_cipher\x18\x0f \x02(\t\x12\'\n\x1fselected_candidate_pair_changes\x18\x10 \x02(\r\"\xa4\x05\n\x12\x43\x61ndidatePairStats\x12\x14\n\x0ctransport_id\x18\x01 \x02(\t\x12\x1a\n\x12local_candidate_id\x18\x02 \x02(\t\x12\x1b\n\x13remote_candidate_id\x18\x03 \x02(\t\x12\x33\n\x05state\x18\x04 \x01(\x0e\x32$.livekit.proto.IceCandidatePairState\x12\x11\n\tnominated\x18\x05 \x02(\x08\x12\x14\n\x0cpackets_sent\x18\x06 \x02(\x04\x12\x18\n\x10packets_received\x18\x07 \x02(\x04\x12\x12\n\nbytes_sent\x18\x08 \x02(\x04\x12\x16\n\x0e\x62ytes_received\x18\t \x02(\x04\x12\"\n\x1alast_packet_sent_timestamp\x18\n \x02(\x01\x12&\n\x1elast_packet_received_timestamp\x18\x0b \x02(\x01\x12\x1d\n\x15total_round_trip_time\x18\x0c \x02(\x01\x12\x1f\n\x17\x63urrent_round_trip_time\x18\r \x02(\x01\x12\"\n\x1a\x61vailable_outgoing_bitrate\x18\x0e \x02(\x01\x12\"\n\x1a\x61vailable_incoming_bitrate\x18\x0f \x02(\x01\x12\x19\n\x11requests_received\x18\x10 \x02(\x04\x12\x15\n\rrequests_sent\x18\x11 \x02(\x04\x12\x1a\n\x12responses_received\x18\x12 \x02(\x04\x12\x16\n\x0eresponses_sent\x18\x13 \x02(\x04\x12\x1d\n\x15\x63onsent_requests_sent\x18\x14 \x02(\x04\x12!\n\x19packets_discarded_on_send\x18\x15 \x02(\r\x12\x1f\n\x17\x62ytes_discarded_on_send\x18\x16 \x02(\x04\"\x89\x03\n\x11IceCandidateStats\x12\x14\n\x0ctransport_id\x18\x01 \x02(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x02(\t\x12\x0c\n\x04port\x18\x03 \x02(\x05\x12\x10\n\x08protocol\x18\x04 \x02(\t\x12\x37\n\x0e\x63\x61ndidate_type\x18\x05 \x01(\x0e\x32\x1f.livekit.proto.IceCandidateType\x12\x10\n\x08priority\x18\x06 \x02(\x05\x12\x0b\n\x03url\x18\x07 \x02(\t\x12\x41\n\x0erelay_protocol\x18\x08 \x01(\x0e\x32).livekit.proto.IceServerTransportProtocol\x12\x12\n\nfoundation\x18\t \x02(\t\x12\x17\n\x0frelated_address\x18\n \x02(\t\x12\x14\n\x0crelated_port\x18\x0b \x02(\x05\x12\x19\n\x11username_fragment\x18\x0c \x02(\t\x12\x34\n\x08tcp_type\x18\r \x01(\x0e\x32\".livekit.proto.IceTcpCandidateType\"\x81\x01\n\x10\x43\x65rtificateStats\x12\x13\n\x0b\x66ingerprint\x18\x01 \x02(\t\x12\x1d\n\x15\x66ingerprint_algorithm\x18\x02 \x02(\t\x12\x1a\n\x12\x62\x61se64_certificate\x18\x03 \x02(\t\x12\x1d\n\x15issuer_certificate_id\x18\x04 \x02(\t*Q\n\x10\x44\x61taChannelState\x12\x11\n\rDC_CONNECTING\x10\x00\x12\x0b\n\x07\x44\x43_OPEN\x10\x01\x12\x0e\n\nDC_CLOSING\x10\x02\x12\r\n\tDC_CLOSED\x10\x03*r\n\x17QualityLimitationReason\x12\x13\n\x0fLIMITATION_NONE\x10\x00\x12\x12\n\x0eLIMITATION_CPU\x10\x01\x12\x18\n\x14LIMITATION_BANDWIDTH\x10\x02\x12\x14\n\x10LIMITATION_OTHER\x10\x03*C\n\x07IceRole\x12\x0f\n\x0bICE_UNKNOWN\x10\x00\x12\x13\n\x0fICE_CONTROLLING\x10\x01\x12\x12\n\x0eICE_CONTROLLED\x10\x02*\x9f\x01\n\x12\x44tlsTransportState\x12\x16\n\x12\x44TLS_TRANSPORT_NEW\x10\x00\x12\x1d\n\x19\x44TLS_TRANSPORT_CONNECTING\x10\x01\x12\x1c\n\x18\x44TLS_TRANSPORT_CONNECTED\x10\x02\x12\x19\n\x15\x44TLS_TRANSPORT_CLOSED\x10\x03\x12\x19\n\x15\x44TLS_TRANSPORT_FAILED\x10\x04*\xd4\x01\n\x11IceTransportState\x12\x15\n\x11ICE_TRANSPORT_NEW\x10\x00\x12\x1a\n\x16ICE_TRANSPORT_CHECKING\x10\x01\x12\x1b\n\x17ICE_TRANSPORT_CONNECTED\x10\x02\x12\x1b\n\x17ICE_TRANSPORT_COMPLETED\x10\x03\x12\x1e\n\x1aICE_TRANSPORT_DISCONNECTED\x10\x04\x12\x18\n\x14ICE_TRANSPORT_FAILED\x10\x05\x12\x18\n\x14ICE_TRANSPORT_CLOSED\x10\x06*>\n\x08\x44tlsRole\x12\x0f\n\x0b\x44TLS_CLIENT\x10\x00\x12\x0f\n\x0b\x44TLS_SERVER\x10\x01\x12\x10\n\x0c\x44TLS_UNKNOWN\x10\x02*u\n\x15IceCandidatePairState\x12\x0f\n\x0bPAIR_FROZEN\x10\x00\x12\x10\n\x0cPAIR_WAITING\x10\x01\x12\x14\n\x10PAIR_IN_PROGRESS\x10\x02\x12\x0f\n\x0bPAIR_FAILED\x10\x03\x12\x12\n\x0ePAIR_SUCCEEDED\x10\x04*=\n\x10IceCandidateType\x12\x08\n\x04HOST\x10\x00\x12\t\n\x05SRFLX\x10\x01\x12\t\n\x05PRFLX\x10\x02\x12\t\n\x05RELAY\x10\x03*U\n\x1aIceServerTransportProtocol\x12\x11\n\rTRANSPORT_UDP\x10\x00\x12\x11\n\rTRANSPORT_TCP\x10\x01\x12\x11\n\rTRANSPORT_TLS\x10\x02*T\n\x13IceTcpCandidateType\x12\x14\n\x10\x43\x41NDIDATE_ACTIVE\x10\x00\x12\x15\n\x11\x43\x41NDIDATE_PASSIVE\x10\x01\x12\x10\n\x0c\x43\x41NDIDATE_SO\x10\x02\x42\x10\xaa\x02\rLiveKit.Proto')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'stats_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\rLiveKit.Proto'
  _globals['_OUTBOUNDRTPSTREAMSTATS_QUALITYLIMITATIONDURATIONSENTRY']._loaded_options = None
  _globals['_OUTBOUNDRTPSTREAMSTATS_QUALITYLIMITATIONDURATIONSENTRY']._serialized_options = b'8\001'
  _globals['_DATACHANNELSTATE']._serialized_start=9082
  _globals['_DATACHANNELSTATE']._serialized_end=9163
  _globals['_QUALITYLIMITATIONREASON']._serialized_start=9165
  _globals['_QUALITYLIMITATIONREASON']._serialized_end=9279
  _globals['_ICEROLE']._serialized_start=9281
  _globals['_ICEROLE']._serialized_end=9348
  _globals['_DTLSTRANSPORTSTATE']._serialized_start=9351
  _globals['_DTLSTRANSPORTSTATE']._serialized_end=9510
  _globals['_ICETRANSPORTSTATE']._serialized_start=9513
  _globals['_ICETRANSPORTSTATE']._serialized_end=9725
  _globals['_DTLSROLE']._serialized_start=9727
  _globals['_DTLSROLE']._serialized_end=9789
  _globals['_ICECANDIDATEPAIRSTATE']._serialized_start=9791
  _globals['_ICECANDIDATEPAIRSTATE']._serialized_end=9908
  _globals['_ICECANDIDATETYPE']._serialized_start=9910
  _globals['_ICECANDIDATETYPE']._serialized_end=9971
  _globals['_ICESERVERTRANSPORTPROTOCOL']._serialized_start=9973
  _globals['_ICESERVERTRANSPORTPROTOCOL']._serialized_end=10058
  _globals['_ICETCPCANDIDATETYPE']._serialized_start=10060
  _globals['_ICETCPCANDIDATETYPE']._serialized_end=10144
  _globals['_RTCSTATS']._serialized_start=31
  _globals['_RTCSTATS']._serialized_end=3064
  _globals['_RTCSTATS_CODEC']._serialized_start=974
  _globals['_RTCSTATS_CODEC']._serialized_end=1065
  _globals['_RTCSTATS_INBOUNDRTP']._serialized_start=1068
  _globals['_RTCSTATS_INBOUNDRTP']._serialized_end=1281
  _globals['_RTCSTATS_OUTBOUNDRTP']._serialized_start=1284
  _globals['_RTCSTATS_OUTBOUNDRTP']._serialized_end=1492
  _globals['_RTCSTATS_REMOTEINBOUNDRTP']._serialized_start=1495
  _globals['_RTCSTATS_REMOTEINBOUNDRTP']._serialized_end=1727
  _globals['_RTCSTATS_REMOTEOUTBOUNDRTP']._serialized_start=1730
  _globals['_RTCSTATS_REMOTEOUTBOUNDRTP']._serialized_end=1957
  _globals['_RTCSTATS_MEDIASOURCE']._serialized_start=1960
  _globals['_RTCSTATS_MEDIASOURCE']._serialized_end=2160
  _globals['_RTCSTATS_MEDIAPLAYOUT']._serialized_start=2162
  _globals['_RTCSTATS_MEDIAPLAYOUT']._serialized_end=2275
  _globals['_RTCSTATS_PEERCONNECTION']._serialized_start=2277
  _globals['_RTCSTATS_PEERCONNECTION']._serialized_end=2383
  _globals['_RTCSTATS_DATACHANNEL']._serialized_start=2385
  _globals['_RTCSTATS_DATACHANNEL']._serialized_end=2485
  _globals['_RTCSTATS_TRANSPORT']._serialized_start=2487
  _globals['_RTCSTATS_TRANSPORT']._serialized_end=2590
  _globals['_RTCSTATS_CANDIDATEPAIR']._serialized_start=2592
  _globals['_RTCSTATS_CANDIDATEPAIR']._serialized_end=2708
  _globals['_RTCSTATS_LOCALCANDIDATE']._serialized_start=2710
  _globals['_RTCSTATS_LOCALCANDIDATE']._serialized_end=2821
  _globals['_RTCSTATS_REMOTECANDIDATE']._serialized_start=2823
  _globals['_RTCSTATS_REMOTECANDIDATE']._serialized_end=2935
  _globals['_RTCSTATS_CERTIFICATE']._serialized_start=2937
  _globals['_RTCSTATS_CERTIFICATE']._serialized_end=3046
  _globals['_RTCSTATS_TRACK']._serialized_start=3048
  _globals['_RTCSTATS_TRACK']._serialized_end=3055
  _globals['_RTCSTATSDATA']._serialized_start=3066
  _globals['_RTCSTATSDATA']._serialized_end=3111
  _globals['_CODECSTATS']._serialized_start=3114
  _globals['_CODECSTATS']._serialized_end=3250
  _globals['_RTPSTREAMSTATS']._serialized_start=3252
  _globals['_RTPSTREAMSTATS']._serialized_end=3336
  _globals['_RECEIVEDRTPSTREAMSTATS']._serialized_start=3338
  _globals['_RECEIVEDRTPSTREAMSTATS']._serialized_end=3426
  _globals['_INBOUNDRTPSTREAMSTATS']._serialized_start=3429
  _globals['_INBOUNDRTPSTREAMSTATS']._serialized_end=4967
  _globals['_SENTRTPSTREAMSTATS']._serialized_start=4969
  _globals['_SENTRTPSTREAMSTATS']._serialized_end=5031
  _globals['_OUTBOUNDRTPSTREAMSTATS']._serialized_start=5034
  _globals['_OUTBOUNDRTPSTREAMSTATS']._serialized_end=6011
  _globals['_OUTBOUNDRTPSTREAMSTATS_QUALITYLIMITATIONDURATIONSENTRY']._serialized_start=5946
  _globals['_OUTBOUNDRTPSTREAMSTATS_QUALITYLIMITATIONDURATIONSENTRY']._serialized_end=6011
  _globals['_REMOTEINBOUNDRTPSTREAMSTATS']._serialized_start=6014
  _globals['_REMOTEINBOUNDRTPSTREAMSTATS']._serialized_end=6178
  _globals['_REMOTEOUTBOUNDRTPSTREAMSTATS']._serialized_start=6181
  _globals['_REMOTEOUTBOUNDRTPSTREAMSTATS']._serialized_end=6371
  _globals['_MEDIASOURCESTATS']._serialized_start=6373
  _globals['_MEDIASOURCESTATS']._serialized_end=6431
  _globals['_AUDIOSOURCESTATS']._serialized_start=6434
  _globals['_AUDIOSOURCESTATS']._serialized_end=6724
  _globals['_VIDEOSOURCESTATS']._serialized_start=6726
  _globals['_VIDEOSOURCESTATS']._serialized_end=6818
  _globals['_AUDIOPLAYOUTSTATS']._serialized_start=6821
  _globals['_AUDIOPLAYOUTSTATS']._serialized_end=7018
  _globals['_PEERCONNECTIONSTATS']._serialized_start=7020
  _globals['_PEERCONNECTIONSTATS']._serialized_end=7101
  _globals['_DATACHANNELSTATS']._serialized_start=7104
  _globals['_DATACHANNELSTATS']._serialized_end=7330
  _globals['_TRANSPORTSTATS']._serialized_start=7333
  _globals['_TRANSPORTSTATS']._serialized_end=7873
  _globals['_CANDIDATEPAIRSTATS']._serialized_start=7876
  _globals['_CANDIDATEPAIRSTATS']._serialized_end=8552
  _globals['_ICECANDIDATESTATS']._serialized_start=8555
  _globals['_ICECANDIDATESTATS']._serialized_end=8948
  _globals['_CERTIFICATESTATS']._serialized_start=8951
  _globals['_CERTIFICATESTATS']._serialized_end=9080
# @@protoc_insertion_point(module_scope)
