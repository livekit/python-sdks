# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: livekit_webhook.proto
# Protobuf Python Version: 4.25.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import models as _models_
from . import egress as _egress_
from . import ingress as _ingress_


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15livekit_webhook.proto\x12\x07livekit\x1a\x14livekit_models.proto\x1a\x14livekit_egress.proto\x1a\x15livekit_ingress.proto\"\x97\x02\n\x0cWebhookEvent\x12\r\n\x05\x65vent\x18\x01 \x01(\t\x12\x1b\n\x04room\x18\x02 \x01(\x0b\x32\r.livekit.Room\x12-\n\x0bparticipant\x18\x03 \x01(\x0b\x32\x18.livekit.ParticipantInfo\x12(\n\x0b\x65gress_info\x18\t \x01(\x0b\x32\x13.livekit.EgressInfo\x12*\n\x0cingress_info\x18\n \x01(\x0b\x32\x14.livekit.IngressInfo\x12!\n\x05track\x18\x08 \x01(\x0b\x32\x12.livekit.TrackInfo\x12\n\n\x02id\x18\x06 \x01(\t\x12\x12\n\ncreated_at\x18\x07 \x01(\x03\x12\x13\n\x0bnum_dropped\x18\x0b \x01(\x05\x42\x46Z#github.com/livekit/protocol/livekit\xaa\x02\rLiveKit.Proto\xea\x02\x0eLiveKit::Protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'webhook', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z#github.com/livekit/protocol/livekit\252\002\rLiveKit.Proto\352\002\016LiveKit::Proto'
  _globals['_WEBHOOKEVENT']._serialized_start=102
  _globals['_WEBHOOKEVENT']._serialized_end=381
# @@protoc_insertion_point(module_scope)
