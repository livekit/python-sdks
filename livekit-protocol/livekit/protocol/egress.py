# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: livekit_egress.proto
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
    'livekit_egress.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import models as _models_


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14livekit_egress.proto\x12\x07livekit\x1a\x14livekit_models.proto\"\xcd\x04\n\x1aRoomCompositeEgressRequest\x12\x11\n\troom_name\x18\x01 \x01(\t\x12\x0e\n\x06layout\x18\x02 \x01(\t\x12\x12\n\naudio_only\x18\x03 \x01(\x08\x12\x12\n\nvideo_only\x18\x04 \x01(\x08\x12\x17\n\x0f\x63ustom_base_url\x18\x05 \x01(\t\x12.\n\x04\x66ile\x18\x06 \x01(\x0b\x32\x1a.livekit.EncodedFileOutputB\x02\x18\x01H\x00\x12+\n\x06stream\x18\x07 \x01(\x0b\x32\x15.livekit.StreamOutputB\x02\x18\x01H\x00\x12\x34\n\x08segments\x18\n \x01(\x0b\x32\x1c.livekit.SegmentedFileOutputB\x02\x18\x01H\x00\x12\x30\n\x06preset\x18\x08 \x01(\x0e\x32\x1e.livekit.EncodingOptionsPresetH\x01\x12,\n\x08\x61\x64vanced\x18\t \x01(\x0b\x32\x18.livekit.EncodingOptionsH\x01\x12\x30\n\x0c\x66ile_outputs\x18\x0b \x03(\x0b\x32\x1a.livekit.EncodedFileOutput\x12-\n\x0estream_outputs\x18\x0c \x03(\x0b\x32\x15.livekit.StreamOutput\x12\x35\n\x0fsegment_outputs\x18\r \x03(\x0b\x32\x1c.livekit.SegmentedFileOutput\x12+\n\rimage_outputs\x18\x0e \x03(\x0b\x32\x14.livekit.ImageOutputB\x08\n\x06outputB\t\n\x07options\"\xb0\x04\n\x10WebEgressRequest\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x12\n\naudio_only\x18\x02 \x01(\x08\x12\x12\n\nvideo_only\x18\x03 \x01(\x08\x12\x1a\n\x12\x61wait_start_signal\x18\x0c \x01(\x08\x12.\n\x04\x66ile\x18\x04 \x01(\x0b\x32\x1a.livekit.EncodedFileOutputB\x02\x18\x01H\x00\x12+\n\x06stream\x18\x05 \x01(\x0b\x32\x15.livekit.StreamOutputB\x02\x18\x01H\x00\x12\x34\n\x08segments\x18\x06 \x01(\x0b\x32\x1c.livekit.SegmentedFileOutputB\x02\x18\x01H\x00\x12\x30\n\x06preset\x18\x07 \x01(\x0e\x32\x1e.livekit.EncodingOptionsPresetH\x01\x12,\n\x08\x61\x64vanced\x18\x08 \x01(\x0b\x32\x18.livekit.EncodingOptionsH\x01\x12\x30\n\x0c\x66ile_outputs\x18\t \x03(\x0b\x32\x1a.livekit.EncodedFileOutput\x12-\n\x0estream_outputs\x18\n \x03(\x0b\x32\x15.livekit.StreamOutput\x12\x35\n\x0fsegment_outputs\x18\x0b \x03(\x0b\x32\x1c.livekit.SegmentedFileOutput\x12+\n\rimage_outputs\x18\r \x03(\x0b\x32\x14.livekit.ImageOutputB\x08\n\x06outputB\t\n\x07options\"\x85\x03\n\x18ParticipantEgressRequest\x12\x11\n\troom_name\x18\x01 \x01(\t\x12\x10\n\x08identity\x18\x02 \x01(\t\x12\x14\n\x0cscreen_share\x18\x03 \x01(\x08\x12\x30\n\x06preset\x18\x04 \x01(\x0e\x32\x1e.livekit.EncodingOptionsPresetH\x00\x12,\n\x08\x61\x64vanced\x18\x05 \x01(\x0b\x32\x18.livekit.EncodingOptionsH\x00\x12\x30\n\x0c\x66ile_outputs\x18\x06 \x03(\x0b\x32\x1a.livekit.EncodedFileOutput\x12-\n\x0estream_outputs\x18\x07 \x03(\x0b\x32\x15.livekit.StreamOutput\x12\x35\n\x0fsegment_outputs\x18\x08 \x03(\x0b\x32\x1c.livekit.SegmentedFileOutput\x12+\n\rimage_outputs\x18\t \x03(\x0b\x32\x14.livekit.ImageOutputB\t\n\x07options\"\xad\x04\n\x1bTrackCompositeEgressRequest\x12\x11\n\troom_name\x18\x01 \x01(\t\x12\x16\n\x0e\x61udio_track_id\x18\x02 \x01(\t\x12\x16\n\x0evideo_track_id\x18\x03 \x01(\t\x12.\n\x04\x66ile\x18\x04 \x01(\x0b\x32\x1a.livekit.EncodedFileOutputB\x02\x18\x01H\x00\x12+\n\x06stream\x18\x05 \x01(\x0b\x32\x15.livekit.StreamOutputB\x02\x18\x01H\x00\x12\x34\n\x08segments\x18\x08 \x01(\x0b\x32\x1c.livekit.SegmentedFileOutputB\x02\x18\x01H\x00\x12\x30\n\x06preset\x18\x06 \x01(\x0e\x32\x1e.livekit.EncodingOptionsPresetH\x01\x12,\n\x08\x61\x64vanced\x18\x07 \x01(\x0b\x32\x18.livekit.EncodingOptionsH\x01\x12\x30\n\x0c\x66ile_outputs\x18\x0b \x03(\x0b\x32\x1a.livekit.EncodedFileOutput\x12-\n\x0estream_outputs\x18\x0c \x03(\x0b\x32\x15.livekit.StreamOutput\x12\x35\n\x0fsegment_outputs\x18\r \x03(\x0b\x32\x1c.livekit.SegmentedFileOutput\x12+\n\rimage_outputs\x18\x0e \x03(\x0b\x32\x14.livekit.ImageOutputB\x08\n\x06outputB\t\n\x07options\"\x87\x01\n\x12TrackEgressRequest\x12\x11\n\troom_name\x18\x01 \x01(\t\x12\x10\n\x08track_id\x18\x02 \x01(\t\x12)\n\x04\x66ile\x18\x03 \x01(\x0b\x32\x19.livekit.DirectFileOutputH\x00\x12\x17\n\rwebsocket_url\x18\x04 \x01(\tH\x00\x42\x08\n\x06output\"\x8e\x02\n\x11\x45ncodedFileOutput\x12+\n\tfile_type\x18\x01 \x01(\x0e\x32\x18.livekit.EncodedFileType\x12\x10\n\x08\x66ilepath\x18\x02 \x01(\t\x12\x18\n\x10\x64isable_manifest\x18\x06 \x01(\x08\x12\x1f\n\x02s3\x18\x03 \x01(\x0b\x32\x11.livekit.S3UploadH\x00\x12!\n\x03gcp\x18\x04 \x01(\x0b\x32\x12.livekit.GCPUploadH\x00\x12)\n\x05\x61zure\x18\x05 \x01(\x0b\x32\x18.livekit.AzureBlobUploadH\x00\x12\'\n\x06\x61liOSS\x18\x07 \x01(\x0b\x32\x15.livekit.AliOSSUploadH\x00\x42\x08\n\x06output\"\xa0\x03\n\x13SegmentedFileOutput\x12\x30\n\x08protocol\x18\x01 \x01(\x0e\x32\x1e.livekit.SegmentedFileProtocol\x12\x17\n\x0f\x66ilename_prefix\x18\x02 \x01(\t\x12\x15\n\rplaylist_name\x18\x03 \x01(\t\x12\x1a\n\x12live_playlist_name\x18\x0b \x01(\t\x12\x18\n\x10segment_duration\x18\x04 \x01(\r\x12\x35\n\x0f\x66ilename_suffix\x18\n \x01(\x0e\x32\x1c.livekit.SegmentedFileSuffix\x12\x18\n\x10\x64isable_manifest\x18\x08 \x01(\x08\x12\x1f\n\x02s3\x18\x05 \x01(\x0b\x32\x11.livekit.S3UploadH\x00\x12!\n\x03gcp\x18\x06 \x01(\x0b\x32\x12.livekit.GCPUploadH\x00\x12)\n\x05\x61zure\x18\x07 \x01(\x0b\x32\x18.livekit.AzureBlobUploadH\x00\x12\'\n\x06\x61liOSS\x18\t \x01(\x0b\x32\x15.livekit.AliOSSUploadH\x00\x42\x08\n\x06output\"\xe0\x01\n\x10\x44irectFileOutput\x12\x10\n\x08\x66ilepath\x18\x01 \x01(\t\x12\x18\n\x10\x64isable_manifest\x18\x05 \x01(\x08\x12\x1f\n\x02s3\x18\x02 \x01(\x0b\x32\x11.livekit.S3UploadH\x00\x12!\n\x03gcp\x18\x03 \x01(\x0b\x32\x12.livekit.GCPUploadH\x00\x12)\n\x05\x61zure\x18\x04 \x01(\x0b\x32\x18.livekit.AzureBlobUploadH\x00\x12\'\n\x06\x61liOSS\x18\x06 \x01(\x0b\x32\x15.livekit.AliOSSUploadH\x00\x42\x08\n\x06output\"\xf8\x02\n\x0bImageOutput\x12\x18\n\x10\x63\x61pture_interval\x18\x01 \x01(\r\x12\r\n\x05width\x18\x02 \x01(\x05\x12\x0e\n\x06height\x18\x03 \x01(\x05\x12\x17\n\x0f\x66ilename_prefix\x18\x04 \x01(\t\x12\x31\n\x0f\x66ilename_suffix\x18\x05 \x01(\x0e\x32\x18.livekit.ImageFileSuffix\x12(\n\x0bimage_codec\x18\x06 \x01(\x0e\x32\x13.livekit.ImageCodec\x12\x18\n\x10\x64isable_manifest\x18\x07 \x01(\x08\x12\x1f\n\x02s3\x18\x08 \x01(\x0b\x32\x11.livekit.S3UploadH\x00\x12!\n\x03gcp\x18\t \x01(\x0b\x32\x12.livekit.GCPUploadH\x00\x12)\n\x05\x61zure\x18\n \x01(\x0b\x32\x18.livekit.AzureBlobUploadH\x00\x12\'\n\x06\x61liOSS\x18\x0b \x01(\x0b\x32\x15.livekit.AliOSSUploadH\x00\x42\x08\n\x06output\"\xc8\x02\n\x08S3Upload\x12\x12\n\naccess_key\x18\x01 \x01(\t\x12\x0e\n\x06secret\x18\x02 \x01(\t\x12\x15\n\rsession_token\x18\x0b \x01(\t\x12\x0e\n\x06region\x18\x03 \x01(\t\x12\x10\n\x08\x65ndpoint\x18\x04 \x01(\t\x12\x0e\n\x06\x62ucket\x18\x05 \x01(\t\x12\x18\n\x10\x66orce_path_style\x18\x06 \x01(\x08\x12\x31\n\x08metadata\x18\x07 \x03(\x0b\x32\x1f.livekit.S3Upload.MetadataEntry\x12\x0f\n\x07tagging\x18\x08 \x01(\t\x12\x1b\n\x13\x63ontent_disposition\x18\t \x01(\t\x12#\n\x05proxy\x18\n \x01(\x0b\x32\x14.livekit.ProxyConfig\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"U\n\tGCPUpload\x12\x13\n\x0b\x63redentials\x18\x01 \x01(\t\x12\x0e\n\x06\x62ucket\x18\x02 \x01(\t\x12#\n\x05proxy\x18\x03 \x01(\x0b\x32\x14.livekit.ProxyConfig\"T\n\x0f\x41zureBlobUpload\x12\x14\n\x0c\x61\x63\x63ount_name\x18\x01 \x01(\t\x12\x13\n\x0b\x61\x63\x63ount_key\x18\x02 \x01(\t\x12\x16\n\x0e\x63ontainer_name\x18\x03 \x01(\t\"d\n\x0c\x41liOSSUpload\x12\x12\n\naccess_key\x18\x01 \x01(\t\x12\x0e\n\x06secret\x18\x02 \x01(\t\x12\x0e\n\x06region\x18\x03 \x01(\t\x12\x10\n\x08\x65ndpoint\x18\x04 \x01(\t\x12\x0e\n\x06\x62ucket\x18\x05 \x01(\t\">\n\x0bProxyConfig\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\"G\n\x0cStreamOutput\x12)\n\x08protocol\x18\x01 \x01(\x0e\x32\x17.livekit.StreamProtocol\x12\x0c\n\x04urls\x18\x02 \x03(\t\"\xb7\x02\n\x0f\x45ncodingOptions\x12\r\n\x05width\x18\x01 \x01(\x05\x12\x0e\n\x06height\x18\x02 \x01(\x05\x12\r\n\x05\x64\x65pth\x18\x03 \x01(\x05\x12\x11\n\tframerate\x18\x04 \x01(\x05\x12(\n\x0b\x61udio_codec\x18\x05 \x01(\x0e\x32\x13.livekit.AudioCodec\x12\x15\n\raudio_bitrate\x18\x06 \x01(\x05\x12\x15\n\raudio_quality\x18\x0b \x01(\x05\x12\x17\n\x0f\x61udio_frequency\x18\x07 \x01(\x05\x12(\n\x0bvideo_codec\x18\x08 \x01(\x0e\x32\x13.livekit.VideoCodec\x12\x15\n\rvideo_bitrate\x18\t \x01(\x05\x12\x15\n\rvideo_quality\x18\x0c \x01(\x05\x12\x1a\n\x12key_frame_interval\x18\n \x01(\x01\"8\n\x13UpdateLayoutRequest\x12\x11\n\tegress_id\x18\x01 \x01(\t\x12\x0e\n\x06layout\x18\x02 \x01(\t\"]\n\x13UpdateStreamRequest\x12\x11\n\tegress_id\x18\x01 \x01(\t\x12\x17\n\x0f\x61\x64\x64_output_urls\x18\x02 \x03(\t\x12\x1a\n\x12remove_output_urls\x18\x03 \x03(\t\"I\n\x11ListEgressRequest\x12\x11\n\troom_name\x18\x01 \x01(\t\x12\x11\n\tegress_id\x18\x02 \x01(\t\x12\x0e\n\x06\x61\x63tive\x18\x03 \x01(\x08\"8\n\x12ListEgressResponse\x12\"\n\x05items\x18\x01 \x03(\x0b\x32\x13.livekit.EgressInfo\"&\n\x11StopEgressRequest\x12\x11\n\tegress_id\x18\x01 \x01(\t\"\xb6\x06\n\nEgressInfo\x12\x11\n\tegress_id\x18\x01 \x01(\t\x12\x0f\n\x07room_id\x18\x02 \x01(\t\x12\x11\n\troom_name\x18\r \x01(\t\x12%\n\x06status\x18\x03 \x01(\x0e\x32\x15.livekit.EgressStatus\x12\x12\n\nstarted_at\x18\n \x01(\x03\x12\x10\n\x08\x65nded_at\x18\x0b \x01(\x03\x12\x12\n\nupdated_at\x18\x12 \x01(\x03\x12\x0f\n\x07\x64\x65tails\x18\x15 \x01(\t\x12\r\n\x05\x65rror\x18\t \x01(\t\x12\x12\n\nerror_code\x18\x16 \x01(\x05\x12=\n\x0eroom_composite\x18\x04 \x01(\x0b\x32#.livekit.RoomCompositeEgressRequestH\x00\x12(\n\x03web\x18\x0e \x01(\x0b\x32\x19.livekit.WebEgressRequestH\x00\x12\x38\n\x0bparticipant\x18\x13 \x01(\x0b\x32!.livekit.ParticipantEgressRequestH\x00\x12?\n\x0ftrack_composite\x18\x05 \x01(\x0b\x32$.livekit.TrackCompositeEgressRequestH\x00\x12,\n\x05track\x18\x06 \x01(\x0b\x32\x1b.livekit.TrackEgressRequestH\x00\x12-\n\x06stream\x18\x07 \x01(\x0b\x32\x17.livekit.StreamInfoListB\x02\x18\x01H\x01\x12%\n\x04\x66ile\x18\x08 \x01(\x0b\x32\x11.livekit.FileInfoB\x02\x18\x01H\x01\x12-\n\x08segments\x18\x0c \x01(\x0b\x32\x15.livekit.SegmentsInfoB\x02\x18\x01H\x01\x12+\n\x0estream_results\x18\x0f \x03(\x0b\x32\x13.livekit.StreamInfo\x12\'\n\x0c\x66ile_results\x18\x10 \x03(\x0b\x32\x11.livekit.FileInfo\x12.\n\x0fsegment_results\x18\x11 \x03(\x0b\x32\x15.livekit.SegmentsInfo\x12*\n\rimage_results\x18\x14 \x03(\x0b\x32\x13.livekit.ImagesInfoB\t\n\x07requestB\x08\n\x06result\"7\n\x0eStreamInfoList\x12!\n\x04info\x18\x01 \x03(\x0b\x32\x13.livekit.StreamInfo:\x02\x18\x01\"\xbc\x01\n\nStreamInfo\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x12\n\nstarted_at\x18\x02 \x01(\x03\x12\x10\n\x08\x65nded_at\x18\x03 \x01(\x03\x12\x10\n\x08\x64uration\x18\x04 \x01(\x03\x12*\n\x06status\x18\x05 \x01(\x0e\x32\x1a.livekit.StreamInfo.Status\x12\r\n\x05\x65rror\x18\x06 \x01(\t\".\n\x06Status\x12\n\n\x06\x41\x43TIVE\x10\x00\x12\x0c\n\x08\x46INISHED\x10\x01\x12\n\n\x06\x46\x41ILED\x10\x02\"t\n\x08\x46ileInfo\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x12\n\nstarted_at\x18\x02 \x01(\x03\x12\x10\n\x08\x65nded_at\x18\x03 \x01(\x03\x12\x10\n\x08\x64uration\x18\x06 \x01(\x03\x12\x0c\n\x04size\x18\x04 \x01(\x03\x12\x10\n\x08location\x18\x05 \x01(\t\"\xd9\x01\n\x0cSegmentsInfo\x12\x15\n\rplaylist_name\x18\x01 \x01(\t\x12\x1a\n\x12live_playlist_name\x18\x08 \x01(\t\x12\x10\n\x08\x64uration\x18\x02 \x01(\x03\x12\x0c\n\x04size\x18\x03 \x01(\x03\x12\x19\n\x11playlist_location\x18\x04 \x01(\t\x12\x1e\n\x16live_playlist_location\x18\t \x01(\t\x12\x15\n\rsegment_count\x18\x05 \x01(\x03\x12\x12\n\nstarted_at\x18\x06 \x01(\x03\x12\x10\n\x08\x65nded_at\x18\x07 \x01(\x03\"`\n\nImagesInfo\x12\x17\n\x0f\x66ilename_prefix\x18\x04 \x01(\t\x12\x13\n\x0bimage_count\x18\x01 \x01(\x03\x12\x12\n\nstarted_at\x18\x02 \x01(\x03\x12\x10\n\x08\x65nded_at\x18\x03 \x01(\x03\"\xeb\x01\n\x15\x41utoParticipantEgress\x12\x30\n\x06preset\x18\x01 \x01(\x0e\x32\x1e.livekit.EncodingOptionsPresetH\x00\x12,\n\x08\x61\x64vanced\x18\x02 \x01(\x0b\x32\x18.livekit.EncodingOptionsH\x00\x12\x30\n\x0c\x66ile_outputs\x18\x03 \x03(\x0b\x32\x1a.livekit.EncodedFileOutput\x12\x35\n\x0fsegment_outputs\x18\x04 \x03(\x0b\x32\x1c.livekit.SegmentedFileOutputB\t\n\x07options\"\xdf\x01\n\x0f\x41utoTrackEgress\x12\x10\n\x08\x66ilepath\x18\x01 \x01(\t\x12\x18\n\x10\x64isable_manifest\x18\x05 \x01(\x08\x12\x1f\n\x02s3\x18\x02 \x01(\x0b\x32\x11.livekit.S3UploadH\x00\x12!\n\x03gcp\x18\x03 \x01(\x0b\x32\x12.livekit.GCPUploadH\x00\x12)\n\x05\x61zure\x18\x04 \x01(\x0b\x32\x18.livekit.AzureBlobUploadH\x00\x12\'\n\x06\x61liOSS\x18\x06 \x01(\x0b\x32\x15.livekit.AliOSSUploadH\x00\x42\x08\n\x06output*9\n\x0f\x45ncodedFileType\x12\x14\n\x10\x44\x45\x46\x41ULT_FILETYPE\x10\x00\x12\x07\n\x03MP4\x10\x01\x12\x07\n\x03OGG\x10\x02*N\n\x15SegmentedFileProtocol\x12#\n\x1f\x44\x45\x46\x41ULT_SEGMENTED_FILE_PROTOCOL\x10\x00\x12\x10\n\x0cHLS_PROTOCOL\x10\x01*/\n\x13SegmentedFileSuffix\x12\t\n\x05INDEX\x10\x00\x12\r\n\tTIMESTAMP\x10\x01*E\n\x0fImageFileSuffix\x12\x16\n\x12IMAGE_SUFFIX_INDEX\x10\x00\x12\x1a\n\x16IMAGE_SUFFIX_TIMESTAMP\x10\x01*9\n\x0eStreamProtocol\x12\x14\n\x10\x44\x45\x46\x41ULT_PROTOCOL\x10\x00\x12\x08\n\x04RTMP\x10\x01\x12\x07\n\x03SRT\x10\x02*\xcf\x01\n\x15\x45ncodingOptionsPreset\x12\x10\n\x0cH264_720P_30\x10\x00\x12\x10\n\x0cH264_720P_60\x10\x01\x12\x11\n\rH264_1080P_30\x10\x02\x12\x11\n\rH264_1080P_60\x10\x03\x12\x19\n\x15PORTRAIT_H264_720P_30\x10\x04\x12\x19\n\x15PORTRAIT_H264_720P_60\x10\x05\x12\x1a\n\x16PORTRAIT_H264_1080P_30\x10\x06\x12\x1a\n\x16PORTRAIT_H264_1080P_60\x10\x07*\x9f\x01\n\x0c\x45gressStatus\x12\x13\n\x0f\x45GRESS_STARTING\x10\x00\x12\x11\n\rEGRESS_ACTIVE\x10\x01\x12\x11\n\rEGRESS_ENDING\x10\x02\x12\x13\n\x0f\x45GRESS_COMPLETE\x10\x03\x12\x11\n\rEGRESS_FAILED\x10\x04\x12\x12\n\x0e\x45GRESS_ABORTED\x10\x05\x12\x18\n\x14\x45GRESS_LIMIT_REACHED\x10\x06\x32\x9c\x05\n\x06\x45gress\x12T\n\x18StartRoomCompositeEgress\x12#.livekit.RoomCompositeEgressRequest\x1a\x13.livekit.EgressInfo\x12@\n\x0eStartWebEgress\x12\x19.livekit.WebEgressRequest\x1a\x13.livekit.EgressInfo\x12P\n\x16StartParticipantEgress\x12!.livekit.ParticipantEgressRequest\x1a\x13.livekit.EgressInfo\x12V\n\x19StartTrackCompositeEgress\x12$.livekit.TrackCompositeEgressRequest\x1a\x13.livekit.EgressInfo\x12\x44\n\x10StartTrackEgress\x12\x1b.livekit.TrackEgressRequest\x1a\x13.livekit.EgressInfo\x12\x41\n\x0cUpdateLayout\x12\x1c.livekit.UpdateLayoutRequest\x1a\x13.livekit.EgressInfo\x12\x41\n\x0cUpdateStream\x12\x1c.livekit.UpdateStreamRequest\x1a\x13.livekit.EgressInfo\x12\x45\n\nListEgress\x12\x1a.livekit.ListEgressRequest\x1a\x1b.livekit.ListEgressResponse\x12=\n\nStopEgress\x12\x1a.livekit.StopEgressRequest\x1a\x13.livekit.EgressInfoBFZ#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'egress', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_ROOMCOMPOSITEEGRESSREQUEST'].fields_by_name['file']._loaded_options = None
  _globals['_ROOMCOMPOSITEEGRESSREQUEST'].fields_by_name['file']._serialized_options = b'\030\001'
  _globals['_ROOMCOMPOSITEEGRESSREQUEST'].fields_by_name['stream']._loaded_options = None
  _globals['_ROOMCOMPOSITEEGRESSREQUEST'].fields_by_name['stream']._serialized_options = b'\030\001'
  _globals['_ROOMCOMPOSITEEGRESSREQUEST'].fields_by_name['segments']._loaded_options = None
  _globals['_ROOMCOMPOSITEEGRESSREQUEST'].fields_by_name['segments']._serialized_options = b'\030\001'
  _globals['_WEBEGRESSREQUEST'].fields_by_name['file']._loaded_options = None
  _globals['_WEBEGRESSREQUEST'].fields_by_name['file']._serialized_options = b'\030\001'
  _globals['_WEBEGRESSREQUEST'].fields_by_name['stream']._loaded_options = None
  _globals['_WEBEGRESSREQUEST'].fields_by_name['stream']._serialized_options = b'\030\001'
  _globals['_WEBEGRESSREQUEST'].fields_by_name['segments']._loaded_options = None
  _globals['_WEBEGRESSREQUEST'].fields_by_name['segments']._serialized_options = b'\030\001'
  _globals['_TRACKCOMPOSITEEGRESSREQUEST'].fields_by_name['file']._loaded_options = None
  _globals['_TRACKCOMPOSITEEGRESSREQUEST'].fields_by_name['file']._serialized_options = b'\030\001'
  _globals['_TRACKCOMPOSITEEGRESSREQUEST'].fields_by_name['stream']._loaded_options = None
  _globals['_TRACKCOMPOSITEEGRESSREQUEST'].fields_by_name['stream']._serialized_options = b'\030\001'
  _globals['_TRACKCOMPOSITEEGRESSREQUEST'].fields_by_name['segments']._loaded_options = None
  _globals['_TRACKCOMPOSITEEGRESSREQUEST'].fields_by_name['segments']._serialized_options = b'\030\001'
  _globals['_S3UPLOAD_METADATAENTRY']._loaded_options = None
  _globals['_S3UPLOAD_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_EGRESSINFO'].fields_by_name['stream']._loaded_options = None
  _globals['_EGRESSINFO'].fields_by_name['stream']._serialized_options = b'\030\001'
  _globals['_EGRESSINFO'].fields_by_name['file']._loaded_options = None
  _globals['_EGRESSINFO'].fields_by_name['file']._serialized_options = b'\030\001'
  _globals['_EGRESSINFO'].fields_by_name['segments']._loaded_options = None
  _globals['_EGRESSINFO'].fields_by_name['segments']._serialized_options = b'\030\001'
  _globals['_STREAMINFOLIST']._loaded_options = None
  _globals['_STREAMINFOLIST']._serialized_options = b'\030\001'
  _globals['_ENCODEDFILETYPE']._serialized_start=6954
  _globals['_ENCODEDFILETYPE']._serialized_end=7011
  _globals['_SEGMENTEDFILEPROTOCOL']._serialized_start=7013
  _globals['_SEGMENTEDFILEPROTOCOL']._serialized_end=7091
  _globals['_SEGMENTEDFILESUFFIX']._serialized_start=7093
  _globals['_SEGMENTEDFILESUFFIX']._serialized_end=7140
  _globals['_IMAGEFILESUFFIX']._serialized_start=7142
  _globals['_IMAGEFILESUFFIX']._serialized_end=7211
  _globals['_STREAMPROTOCOL']._serialized_start=7213
  _globals['_STREAMPROTOCOL']._serialized_end=7270
  _globals['_ENCODINGOPTIONSPRESET']._serialized_start=7273
  _globals['_ENCODINGOPTIONSPRESET']._serialized_end=7480
  _globals['_EGRESSSTATUS']._serialized_start=7483
  _globals['_EGRESSSTATUS']._serialized_end=7642
  _globals['_ROOMCOMPOSITEEGRESSREQUEST']._serialized_start=56
  _globals['_ROOMCOMPOSITEEGRESSREQUEST']._serialized_end=645
  _globals['_WEBEGRESSREQUEST']._serialized_start=648
  _globals['_WEBEGRESSREQUEST']._serialized_end=1208
  _globals['_PARTICIPANTEGRESSREQUEST']._serialized_start=1211
  _globals['_PARTICIPANTEGRESSREQUEST']._serialized_end=1600
  _globals['_TRACKCOMPOSITEEGRESSREQUEST']._serialized_start=1603
  _globals['_TRACKCOMPOSITEEGRESSREQUEST']._serialized_end=2160
  _globals['_TRACKEGRESSREQUEST']._serialized_start=2163
  _globals['_TRACKEGRESSREQUEST']._serialized_end=2298
  _globals['_ENCODEDFILEOUTPUT']._serialized_start=2301
  _globals['_ENCODEDFILEOUTPUT']._serialized_end=2571
  _globals['_SEGMENTEDFILEOUTPUT']._serialized_start=2574
  _globals['_SEGMENTEDFILEOUTPUT']._serialized_end=2990
  _globals['_DIRECTFILEOUTPUT']._serialized_start=2993
  _globals['_DIRECTFILEOUTPUT']._serialized_end=3217
  _globals['_IMAGEOUTPUT']._serialized_start=3220
  _globals['_IMAGEOUTPUT']._serialized_end=3596
  _globals['_S3UPLOAD']._serialized_start=3599
  _globals['_S3UPLOAD']._serialized_end=3927
  _globals['_S3UPLOAD_METADATAENTRY']._serialized_start=3880
  _globals['_S3UPLOAD_METADATAENTRY']._serialized_end=3927
  _globals['_GCPUPLOAD']._serialized_start=3929
  _globals['_GCPUPLOAD']._serialized_end=4014
  _globals['_AZUREBLOBUPLOAD']._serialized_start=4016
  _globals['_AZUREBLOBUPLOAD']._serialized_end=4100
  _globals['_ALIOSSUPLOAD']._serialized_start=4102
  _globals['_ALIOSSUPLOAD']._serialized_end=4202
  _globals['_PROXYCONFIG']._serialized_start=4204
  _globals['_PROXYCONFIG']._serialized_end=4266
  _globals['_STREAMOUTPUT']._serialized_start=4268
  _globals['_STREAMOUTPUT']._serialized_end=4339
  _globals['_ENCODINGOPTIONS']._serialized_start=4342
  _globals['_ENCODINGOPTIONS']._serialized_end=4653
  _globals['_UPDATELAYOUTREQUEST']._serialized_start=4655
  _globals['_UPDATELAYOUTREQUEST']._serialized_end=4711
  _globals['_UPDATESTREAMREQUEST']._serialized_start=4713
  _globals['_UPDATESTREAMREQUEST']._serialized_end=4806
  _globals['_LISTEGRESSREQUEST']._serialized_start=4808
  _globals['_LISTEGRESSREQUEST']._serialized_end=4881
  _globals['_LISTEGRESSRESPONSE']._serialized_start=4883
  _globals['_LISTEGRESSRESPONSE']._serialized_end=4939
  _globals['_STOPEGRESSREQUEST']._serialized_start=4941
  _globals['_STOPEGRESSREQUEST']._serialized_end=4979
  _globals['_EGRESSINFO']._serialized_start=4982
  _globals['_EGRESSINFO']._serialized_end=5804
  _globals['_STREAMINFOLIST']._serialized_start=5806
  _globals['_STREAMINFOLIST']._serialized_end=5861
  _globals['_STREAMINFO']._serialized_start=5864
  _globals['_STREAMINFO']._serialized_end=6052
  _globals['_STREAMINFO_STATUS']._serialized_start=6006
  _globals['_STREAMINFO_STATUS']._serialized_end=6052
  _globals['_FILEINFO']._serialized_start=6054
  _globals['_FILEINFO']._serialized_end=6170
  _globals['_SEGMENTSINFO']._serialized_start=6173
  _globals['_SEGMENTSINFO']._serialized_end=6390
  _globals['_IMAGESINFO']._serialized_start=6392
  _globals['_IMAGESINFO']._serialized_end=6488
  _globals['_AUTOPARTICIPANTEGRESS']._serialized_start=6491
  _globals['_AUTOPARTICIPANTEGRESS']._serialized_end=6726
  _globals['_AUTOTRACKEGRESS']._serialized_start=6729
  _globals['_AUTOTRACKEGRESS']._serialized_end=6952
  _globals['_EGRESS']._serialized_start=7645
  _globals['_EGRESS']._serialized_end=8313
# @@protoc_insertion_point(module_scope)
