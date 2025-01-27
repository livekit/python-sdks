# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: livekit_agent.proto
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
    'livekit_agent.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import models as _models_


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13livekit_agent.proto\x12\x07livekit\x1a\x14livekit_models.proto\"\x86\x02\n\x03Job\x12\n\n\x02id\x18\x01 \x01(\t\x12\x13\n\x0b\x64ispatch_id\x18\t \x01(\t\x12\x1e\n\x04type\x18\x02 \x01(\x0e\x32\x10.livekit.JobType\x12\x1b\n\x04room\x18\x03 \x01(\x0b\x32\r.livekit.Room\x12\x32\n\x0bparticipant\x18\x04 \x01(\x0b\x32\x18.livekit.ParticipantInfoH\x00\x88\x01\x01\x12\x15\n\tnamespace\x18\x05 \x01(\tB\x02\x18\x01\x12\x10\n\x08metadata\x18\x06 \x01(\t\x12\x12\n\nagent_name\x18\x07 \x01(\t\x12 \n\x05state\x18\x08 \x01(\x0b\x32\x11.livekit.JobStateB\x0e\n\x0c_participant\"\x95\x01\n\x08JobState\x12\"\n\x06status\x18\x01 \x01(\x0e\x32\x12.livekit.JobStatus\x12\r\n\x05\x65rror\x18\x02 \x01(\t\x12\x12\n\nstarted_at\x18\x03 \x01(\x03\x12\x10\n\x08\x65nded_at\x18\x04 \x01(\x03\x12\x12\n\nupdated_at\x18\x05 \x01(\x03\x12\x1c\n\x14participant_identity\x18\x06 \x01(\t\"\xf8\x02\n\rWorkerMessage\x12\x32\n\x08register\x18\x01 \x01(\x0b\x32\x1e.livekit.RegisterWorkerRequestH\x00\x12\x35\n\x0c\x61vailability\x18\x02 \x01(\x0b\x32\x1d.livekit.AvailabilityResponseH\x00\x12\x34\n\rupdate_worker\x18\x03 \x01(\x0b\x32\x1b.livekit.UpdateWorkerStatusH\x00\x12.\n\nupdate_job\x18\x04 \x01(\x0b\x32\x18.livekit.UpdateJobStatusH\x00\x12#\n\x04ping\x18\x05 \x01(\x0b\x32\x13.livekit.WorkerPingH\x00\x12\x33\n\x0csimulate_job\x18\x06 \x01(\x0b\x32\x1b.livekit.SimulateJobRequestH\x00\x12\x31\n\x0bmigrate_job\x18\x07 \x01(\x0b\x32\x1a.livekit.MigrateJobRequestH\x00\x42\t\n\x07message\"\x88\x02\n\rServerMessage\x12\x33\n\x08register\x18\x01 \x01(\x0b\x32\x1f.livekit.RegisterWorkerResponseH\x00\x12\x34\n\x0c\x61vailability\x18\x02 \x01(\x0b\x32\x1c.livekit.AvailabilityRequestH\x00\x12,\n\nassignment\x18\x03 \x01(\x0b\x32\x16.livekit.JobAssignmentH\x00\x12.\n\x0btermination\x18\x05 \x01(\x0b\x32\x17.livekit.JobTerminationH\x00\x12#\n\x04pong\x18\x04 \x01(\x0b\x32\x13.livekit.WorkerPongH\x00\x42\t\n\x07message\"\x80\x01\n\x12SimulateJobRequest\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.livekit.JobType\x12\x1b\n\x04room\x18\x02 \x01(\x0b\x32\r.livekit.Room\x12-\n\x0bparticipant\x18\x03 \x01(\x0b\x32\x18.livekit.ParticipantInfo\"\x1f\n\nWorkerPing\x12\x11\n\ttimestamp\x18\x01 \x01(\x03\"7\n\nWorkerPong\x12\x16\n\x0elast_timestamp\x18\x01 \x01(\x03\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\"\xd6\x01\n\x15RegisterWorkerRequest\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.livekit.JobType\x12\x12\n\nagent_name\x18\x08 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t\x12\x15\n\rping_interval\x18\x05 \x01(\r\x12\x16\n\tnamespace\x18\x06 \x01(\tH\x00\x88\x01\x01\x12;\n\x13\x61llowed_permissions\x18\x07 \x01(\x0b\x32\x1e.livekit.ParticipantPermissionB\x0c\n\n_namespace\"U\n\x16RegisterWorkerResponse\x12\x11\n\tworker_id\x18\x01 \x01(\t\x12(\n\x0bserver_info\x18\x03 \x01(\x0b\x32\x13.livekit.ServerInfo\"$\n\x11MigrateJobRequest\x12\x0f\n\x07job_ids\x18\x02 \x03(\t\"B\n\x13\x41vailabilityRequest\x12\x19\n\x03job\x18\x01 \x01(\x0b\x32\x0c.livekit.Job\x12\x10\n\x08resuming\x18\x02 \x01(\x08\"\xc0\x02\n\x14\x41vailabilityResponse\x12\x0e\n\x06job_id\x18\x01 \x01(\t\x12\x11\n\tavailable\x18\x02 \x01(\x08\x12\x17\n\x0fsupports_resume\x18\x03 \x01(\x08\x12\x18\n\x10participant_name\x18\x04 \x01(\t\x12\x1c\n\x14participant_identity\x18\x05 \x01(\t\x12\x1c\n\x14participant_metadata\x18\x06 \x01(\t\x12X\n\x16participant_attributes\x18\x07 \x03(\x0b\x32\x38.livekit.AvailabilityResponse.ParticipantAttributesEntry\x1a<\n\x1aParticipantAttributesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"T\n\x0fUpdateJobStatus\x12\x0e\n\x06job_id\x18\x01 \x01(\t\x12\"\n\x06status\x18\x02 \x01(\x0e\x32\x12.livekit.JobStatus\x12\r\n\x05\x65rror\x18\x03 \x01(\t\"l\n\x12UpdateWorkerStatus\x12*\n\x06status\x18\x01 \x01(\x0e\x32\x15.livekit.WorkerStatusH\x00\x88\x01\x01\x12\x0c\n\x04load\x18\x03 \x01(\x02\x12\x11\n\tjob_count\x18\x04 \x01(\rB\t\n\x07_status\"S\n\rJobAssignment\x12\x19\n\x03job\x18\x01 \x01(\x0b\x32\x0c.livekit.Job\x12\x10\n\x03url\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\r\n\x05token\x18\x03 \x01(\tB\x06\n\x04_url\" \n\x0eJobTermination\x12\x0e\n\x06job_id\x18\x01 \x01(\t*(\n\x07JobType\x12\x0b\n\x07JT_ROOM\x10\x00\x12\x10\n\x0cJT_PUBLISHER\x10\x01*-\n\x0cWorkerStatus\x12\x10\n\x0cWS_AVAILABLE\x10\x00\x12\x0b\n\x07WS_FULL\x10\x01*J\n\tJobStatus\x12\x0e\n\nJS_PENDING\x10\x00\x12\x0e\n\nJS_RUNNING\x10\x01\x12\x0e\n\nJS_SUCCESS\x10\x02\x12\r\n\tJS_FAILED\x10\x03\x42\x46Z#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'agent', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_JOB'].fields_by_name['namespace']._loaded_options = None
  _globals['_JOB'].fields_by_name['namespace']._serialized_options = b'\030\001'
  _globals['_AVAILABILITYRESPONSE_PARTICIPANTATTRIBUTESENTRY']._loaded_options = None
  _globals['_AVAILABILITYRESPONSE_PARTICIPANTATTRIBUTESENTRY']._serialized_options = b'8\001'
  _globals['_JOBTYPE']._serialized_start=2386
  _globals['_JOBTYPE']._serialized_end=2426
  _globals['_WORKERSTATUS']._serialized_start=2428
  _globals['_WORKERSTATUS']._serialized_end=2473
  _globals['_JOBSTATUS']._serialized_start=2475
  _globals['_JOBSTATUS']._serialized_end=2549
  _globals['_JOB']._serialized_start=55
  _globals['_JOB']._serialized_end=317
  _globals['_JOBSTATE']._serialized_start=320
  _globals['_JOBSTATE']._serialized_end=469
  _globals['_WORKERMESSAGE']._serialized_start=472
  _globals['_WORKERMESSAGE']._serialized_end=848
  _globals['_SERVERMESSAGE']._serialized_start=851
  _globals['_SERVERMESSAGE']._serialized_end=1115
  _globals['_SIMULATEJOBREQUEST']._serialized_start=1118
  _globals['_SIMULATEJOBREQUEST']._serialized_end=1246
  _globals['_WORKERPING']._serialized_start=1248
  _globals['_WORKERPING']._serialized_end=1279
  _globals['_WORKERPONG']._serialized_start=1281
  _globals['_WORKERPONG']._serialized_end=1336
  _globals['_REGISTERWORKERREQUEST']._serialized_start=1339
  _globals['_REGISTERWORKERREQUEST']._serialized_end=1553
  _globals['_REGISTERWORKERRESPONSE']._serialized_start=1555
  _globals['_REGISTERWORKERRESPONSE']._serialized_end=1640
  _globals['_MIGRATEJOBREQUEST']._serialized_start=1642
  _globals['_MIGRATEJOBREQUEST']._serialized_end=1678
  _globals['_AVAILABILITYREQUEST']._serialized_start=1680
  _globals['_AVAILABILITYREQUEST']._serialized_end=1746
  _globals['_AVAILABILITYRESPONSE']._serialized_start=1749
  _globals['_AVAILABILITYRESPONSE']._serialized_end=2069
  _globals['_AVAILABILITYRESPONSE_PARTICIPANTATTRIBUTESENTRY']._serialized_start=2009
  _globals['_AVAILABILITYRESPONSE_PARTICIPANTATTRIBUTESENTRY']._serialized_end=2069
  _globals['_UPDATEJOBSTATUS']._serialized_start=2071
  _globals['_UPDATEJOBSTATUS']._serialized_end=2155
  _globals['_UPDATEWORKERSTATUS']._serialized_start=2157
  _globals['_UPDATEWORKERSTATUS']._serialized_end=2265
  _globals['_JOBASSIGNMENT']._serialized_start=2267
  _globals['_JOBASSIGNMENT']._serialized_end=2350
  _globals['_JOBTERMINATION']._serialized_start=2352
  _globals['_JOBTERMINATION']._serialized_end=2384
# @@protoc_insertion_point(module_scope)
