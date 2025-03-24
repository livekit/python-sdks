# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: rpc.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\trpc.proto\x12\rlivekit.proto\"7\n\x08RpcError\x12\x0c\n\x04\x63ode\x18\x01 \x02(\r\x12\x0f\n\x07message\x18\x02 \x02(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\t\"\x91\x01\n\x11PerformRpcRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x1c\n\x14\x64\x65stination_identity\x18\x02 \x02(\t\x12\x0e\n\x06method\x18\x03 \x02(\t\x12\x0f\n\x07payload\x18\x04 \x02(\t\x12\x1b\n\x13response_timeout_ms\x18\x05 \x01(\r\"?\n\x18RegisterRpcMethodRequest\x12\x13\n\x0broom_handle\x18\x01 \x02(\x04\x12\x0e\n\x06method\x18\x02 \x02(\t\"A\n\x1aUnregisterRpcMethodRequest\x12\x13\n\x0broom_handle\x18\x01 \x02(\x04\x12\x0e\n\x06method\x18\x02 \x02(\t\"\x96\x01\n\"RpcMethodInvocationResponseRequest\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x15\n\rinvocation_id\x18\x02 \x02(\x04\x12\x0f\n\x07payload\x18\x03 \x01(\t\x12&\n\x05\x65rror\x18\x04 \x01(\x0b\x32\x17.livekit.proto.RpcError\"&\n\x12PerformRpcResponse\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\"\x1b\n\x19RegisterRpcMethodResponse\"\x1d\n\x1bUnregisterRpcMethodResponse\"4\n#RpcMethodInvocationResponseResponse\x12\r\n\x05\x65rror\x18\x01 \x01(\t\"_\n\x12PerformRpcCallback\x12\x10\n\x08\x61sync_id\x18\x01 \x02(\x04\x12\x0f\n\x07payload\x18\x02 \x01(\t\x12&\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x17.livekit.proto.RpcError\"\xbe\x01\n\x18RpcMethodInvocationEvent\x12 \n\x18local_participant_handle\x18\x01 \x02(\x04\x12\x15\n\rinvocation_id\x18\x02 \x02(\x04\x12\x0e\n\x06method\x18\x03 \x02(\t\x12\x12\n\nrequest_id\x18\x04 \x02(\t\x12\x17\n\x0f\x63\x61ller_identity\x18\x05 \x02(\t\x12\x0f\n\x07payload\x18\x06 \x02(\t\x12\x1b\n\x13response_timeout_ms\x18\x07 \x02(\rB\x10\xaa\x02\rLiveKit.Proto')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'rpc_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\rLiveKit.Proto'
  _globals['_RPCERROR']._serialized_start=28
  _globals['_RPCERROR']._serialized_end=83
  _globals['_PERFORMRPCREQUEST']._serialized_start=86
  _globals['_PERFORMRPCREQUEST']._serialized_end=231
  _globals['_REGISTERRPCMETHODREQUEST']._serialized_start=233
  _globals['_REGISTERRPCMETHODREQUEST']._serialized_end=296
  _globals['_UNREGISTERRPCMETHODREQUEST']._serialized_start=298
  _globals['_UNREGISTERRPCMETHODREQUEST']._serialized_end=363
  _globals['_RPCMETHODINVOCATIONRESPONSEREQUEST']._serialized_start=366
  _globals['_RPCMETHODINVOCATIONRESPONSEREQUEST']._serialized_end=516
  _globals['_PERFORMRPCRESPONSE']._serialized_start=518
  _globals['_PERFORMRPCRESPONSE']._serialized_end=556
  _globals['_REGISTERRPCMETHODRESPONSE']._serialized_start=558
  _globals['_REGISTERRPCMETHODRESPONSE']._serialized_end=585
  _globals['_UNREGISTERRPCMETHODRESPONSE']._serialized_start=587
  _globals['_UNREGISTERRPCMETHODRESPONSE']._serialized_end=616
  _globals['_RPCMETHODINVOCATIONRESPONSERESPONSE']._serialized_start=618
  _globals['_RPCMETHODINVOCATIONRESPONSERESPONSE']._serialized_end=670
  _globals['_PERFORMRPCCALLBACK']._serialized_start=672
  _globals['_PERFORMRPCCALLBACK']._serialized_end=767
  _globals['_RPCMETHODINVOCATIONEVENT']._serialized_start=770
  _globals['_RPCMETHODINVOCATIONEVENT']._serialized_end=960
# @@protoc_insertion_point(module_scope)
