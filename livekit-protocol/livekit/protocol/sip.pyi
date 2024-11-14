from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from . import models as _models
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SIPTransport(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIP_TRANSPORT_AUTO: _ClassVar[SIPTransport]
    SIP_TRANSPORT_UDP: _ClassVar[SIPTransport]
    SIP_TRANSPORT_TCP: _ClassVar[SIPTransport]
    SIP_TRANSPORT_TLS: _ClassVar[SIPTransport]

class SIPCallStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCS_CALL_INCOMING: _ClassVar[SIPCallStatus]
    SCS_PARTICIPANT_JOINED: _ClassVar[SIPCallStatus]
    SCS_ACTIVE: _ClassVar[SIPCallStatus]
    SCS_DISCONNECTED: _ClassVar[SIPCallStatus]
    SCS_ERROR: _ClassVar[SIPCallStatus]
SIP_TRANSPORT_AUTO: SIPTransport
SIP_TRANSPORT_UDP: SIPTransport
SIP_TRANSPORT_TCP: SIPTransport
SIP_TRANSPORT_TLS: SIPTransport
SCS_CALL_INCOMING: SIPCallStatus
SCS_PARTICIPANT_JOINED: SIPCallStatus
SCS_ACTIVE: SIPCallStatus
SCS_DISCONNECTED: SIPCallStatus
SCS_ERROR: SIPCallStatus

class CreateSIPTrunkRequest(_message.Message):
    __slots__ = ("inbound_addresses", "outbound_address", "outbound_number", "inbound_numbers_regex", "inbound_numbers", "inbound_username", "inbound_password", "outbound_username", "outbound_password", "name", "metadata")
    INBOUND_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_REGEX_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    INBOUND_USERNAME_FIELD_NUMBER: _ClassVar[int]
    INBOUND_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_USERNAME_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    inbound_addresses: _containers.RepeatedScalarFieldContainer[str]
    outbound_address: str
    outbound_number: str
    inbound_numbers_regex: _containers.RepeatedScalarFieldContainer[str]
    inbound_numbers: _containers.RepeatedScalarFieldContainer[str]
    inbound_username: str
    inbound_password: str
    outbound_username: str
    outbound_password: str
    name: str
    metadata: str
    def __init__(self, inbound_addresses: _Optional[_Iterable[str]] = ..., outbound_address: _Optional[str] = ..., outbound_number: _Optional[str] = ..., inbound_numbers_regex: _Optional[_Iterable[str]] = ..., inbound_numbers: _Optional[_Iterable[str]] = ..., inbound_username: _Optional[str] = ..., inbound_password: _Optional[str] = ..., outbound_username: _Optional[str] = ..., outbound_password: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ...) -> None: ...

class SIPTrunkInfo(_message.Message):
    __slots__ = ("sip_trunk_id", "kind", "inbound_addresses", "outbound_address", "outbound_number", "transport", "inbound_numbers_regex", "inbound_numbers", "inbound_username", "inbound_password", "outbound_username", "outbound_password", "name", "metadata")
    class TrunkKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRUNK_LEGACY: _ClassVar[SIPTrunkInfo.TrunkKind]
        TRUNK_INBOUND: _ClassVar[SIPTrunkInfo.TrunkKind]
        TRUNK_OUTBOUND: _ClassVar[SIPTrunkInfo.TrunkKind]
    TRUNK_LEGACY: SIPTrunkInfo.TrunkKind
    TRUNK_INBOUND: SIPTrunkInfo.TrunkKind
    TRUNK_OUTBOUND: SIPTrunkInfo.TrunkKind
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    INBOUND_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_REGEX_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    INBOUND_USERNAME_FIELD_NUMBER: _ClassVar[int]
    INBOUND_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_USERNAME_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    kind: SIPTrunkInfo.TrunkKind
    inbound_addresses: _containers.RepeatedScalarFieldContainer[str]
    outbound_address: str
    outbound_number: str
    transport: SIPTransport
    inbound_numbers_regex: _containers.RepeatedScalarFieldContainer[str]
    inbound_numbers: _containers.RepeatedScalarFieldContainer[str]
    inbound_username: str
    inbound_password: str
    outbound_username: str
    outbound_password: str
    name: str
    metadata: str
    def __init__(self, sip_trunk_id: _Optional[str] = ..., kind: _Optional[_Union[SIPTrunkInfo.TrunkKind, str]] = ..., inbound_addresses: _Optional[_Iterable[str]] = ..., outbound_address: _Optional[str] = ..., outbound_number: _Optional[str] = ..., transport: _Optional[_Union[SIPTransport, str]] = ..., inbound_numbers_regex: _Optional[_Iterable[str]] = ..., inbound_numbers: _Optional[_Iterable[str]] = ..., inbound_username: _Optional[str] = ..., inbound_password: _Optional[str] = ..., outbound_username: _Optional[str] = ..., outbound_password: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ...) -> None: ...

class CreateSIPInboundTrunkRequest(_message.Message):
    __slots__ = ("trunk",)
    TRUNK_FIELD_NUMBER: _ClassVar[int]
    trunk: SIPInboundTrunkInfo
    def __init__(self, trunk: _Optional[_Union[SIPInboundTrunkInfo, _Mapping]] = ...) -> None: ...

class SIPInboundTrunkInfo(_message.Message):
    __slots__ = ("sip_trunk_id", "name", "metadata", "numbers", "allowed_addresses", "allowed_numbers", "auth_username", "auth_password", "headers", "headers_to_attributes", "ringing_timeout", "max_call_duration", "krisp_enabled")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class HeadersToAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NUMBERS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    AUTH_USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_TO_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    RINGING_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_CALL_DURATION_FIELD_NUMBER: _ClassVar[int]
    KRISP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    name: str
    metadata: str
    numbers: _containers.RepeatedScalarFieldContainer[str]
    allowed_addresses: _containers.RepeatedScalarFieldContainer[str]
    allowed_numbers: _containers.RepeatedScalarFieldContainer[str]
    auth_username: str
    auth_password: str
    headers: _containers.ScalarMap[str, str]
    headers_to_attributes: _containers.ScalarMap[str, str]
    ringing_timeout: _duration_pb2.Duration
    max_call_duration: _duration_pb2.Duration
    krisp_enabled: bool
    def __init__(self, sip_trunk_id: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., numbers: _Optional[_Iterable[str]] = ..., allowed_addresses: _Optional[_Iterable[str]] = ..., allowed_numbers: _Optional[_Iterable[str]] = ..., auth_username: _Optional[str] = ..., auth_password: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ..., headers_to_attributes: _Optional[_Mapping[str, str]] = ..., ringing_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., max_call_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., krisp_enabled: bool = ...) -> None: ...

class CreateSIPOutboundTrunkRequest(_message.Message):
    __slots__ = ("trunk",)
    TRUNK_FIELD_NUMBER: _ClassVar[int]
    trunk: SIPOutboundTrunkInfo
    def __init__(self, trunk: _Optional[_Union[SIPOutboundTrunkInfo, _Mapping]] = ...) -> None: ...

class SIPOutboundTrunkInfo(_message.Message):
    __slots__ = ("sip_trunk_id", "name", "metadata", "address", "transport", "numbers", "auth_username", "auth_password", "headers", "headers_to_attributes")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class HeadersToAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    NUMBERS_FIELD_NUMBER: _ClassVar[int]
    AUTH_USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_TO_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    name: str
    metadata: str
    address: str
    transport: SIPTransport
    numbers: _containers.RepeatedScalarFieldContainer[str]
    auth_username: str
    auth_password: str
    headers: _containers.ScalarMap[str, str]
    headers_to_attributes: _containers.ScalarMap[str, str]
    def __init__(self, sip_trunk_id: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., address: _Optional[str] = ..., transport: _Optional[_Union[SIPTransport, str]] = ..., numbers: _Optional[_Iterable[str]] = ..., auth_username: _Optional[str] = ..., auth_password: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ..., headers_to_attributes: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetSIPInboundTrunkRequest(_message.Message):
    __slots__ = ("sip_trunk_id",)
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    def __init__(self, sip_trunk_id: _Optional[str] = ...) -> None: ...

class GetSIPInboundTrunkResponse(_message.Message):
    __slots__ = ("trunk",)
    TRUNK_FIELD_NUMBER: _ClassVar[int]
    trunk: SIPInboundTrunkInfo
    def __init__(self, trunk: _Optional[_Union[SIPInboundTrunkInfo, _Mapping]] = ...) -> None: ...

class GetSIPOutboundTrunkRequest(_message.Message):
    __slots__ = ("sip_trunk_id",)
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    def __init__(self, sip_trunk_id: _Optional[str] = ...) -> None: ...

class GetSIPOutboundTrunkResponse(_message.Message):
    __slots__ = ("trunk",)
    TRUNK_FIELD_NUMBER: _ClassVar[int]
    trunk: SIPOutboundTrunkInfo
    def __init__(self, trunk: _Optional[_Union[SIPOutboundTrunkInfo, _Mapping]] = ...) -> None: ...

class ListSIPTrunkRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSIPTrunkResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SIPTrunkInfo]
    def __init__(self, items: _Optional[_Iterable[_Union[SIPTrunkInfo, _Mapping]]] = ...) -> None: ...

class ListSIPInboundTrunkRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSIPInboundTrunkResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SIPInboundTrunkInfo]
    def __init__(self, items: _Optional[_Iterable[_Union[SIPInboundTrunkInfo, _Mapping]]] = ...) -> None: ...

class ListSIPOutboundTrunkRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSIPOutboundTrunkResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SIPOutboundTrunkInfo]
    def __init__(self, items: _Optional[_Iterable[_Union[SIPOutboundTrunkInfo, _Mapping]]] = ...) -> None: ...

class DeleteSIPTrunkRequest(_message.Message):
    __slots__ = ("sip_trunk_id",)
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    def __init__(self, sip_trunk_id: _Optional[str] = ...) -> None: ...

class SIPDispatchRuleDirect(_message.Message):
    __slots__ = ("room_name", "pin")
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    room_name: str
    pin: str
    def __init__(self, room_name: _Optional[str] = ..., pin: _Optional[str] = ...) -> None: ...

class SIPDispatchRuleIndividual(_message.Message):
    __slots__ = ("room_prefix", "pin")
    ROOM_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    room_prefix: str
    pin: str
    def __init__(self, room_prefix: _Optional[str] = ..., pin: _Optional[str] = ...) -> None: ...

class SIPDispatchRuleCallee(_message.Message):
    __slots__ = ("room_prefix", "pin", "randomize")
    ROOM_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    RANDOMIZE_FIELD_NUMBER: _ClassVar[int]
    room_prefix: str
    pin: str
    randomize: bool
    def __init__(self, room_prefix: _Optional[str] = ..., pin: _Optional[str] = ..., randomize: bool = ...) -> None: ...

class SIPDispatchRule(_message.Message):
    __slots__ = ("dispatch_rule_direct", "dispatch_rule_individual", "dispatch_rule_callee")
    DISPATCH_RULE_DIRECT_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_RULE_INDIVIDUAL_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_RULE_CALLEE_FIELD_NUMBER: _ClassVar[int]
    dispatch_rule_direct: SIPDispatchRuleDirect
    dispatch_rule_individual: SIPDispatchRuleIndividual
    dispatch_rule_callee: SIPDispatchRuleCallee
    def __init__(self, dispatch_rule_direct: _Optional[_Union[SIPDispatchRuleDirect, _Mapping]] = ..., dispatch_rule_individual: _Optional[_Union[SIPDispatchRuleIndividual, _Mapping]] = ..., dispatch_rule_callee: _Optional[_Union[SIPDispatchRuleCallee, _Mapping]] = ...) -> None: ...

class CreateSIPDispatchRuleRequest(_message.Message):
    __slots__ = ("rule", "trunk_ids", "hide_phone_number", "inbound_numbers", "name", "metadata", "attributes")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RULE_FIELD_NUMBER: _ClassVar[int]
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    HIDE_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    rule: SIPDispatchRule
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    hide_phone_number: bool
    inbound_numbers: _containers.RepeatedScalarFieldContainer[str]
    name: str
    metadata: str
    attributes: _containers.ScalarMap[str, str]
    def __init__(self, rule: _Optional[_Union[SIPDispatchRule, _Mapping]] = ..., trunk_ids: _Optional[_Iterable[str]] = ..., hide_phone_number: bool = ..., inbound_numbers: _Optional[_Iterable[str]] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ...) -> None: ...

class SIPDispatchRuleInfo(_message.Message):
    __slots__ = ("sip_dispatch_rule_id", "rule", "trunk_ids", "hide_phone_number", "inbound_numbers", "name", "metadata", "attributes")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SIP_DISPATCH_RULE_ID_FIELD_NUMBER: _ClassVar[int]
    RULE_FIELD_NUMBER: _ClassVar[int]
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    HIDE_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    sip_dispatch_rule_id: str
    rule: SIPDispatchRule
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    hide_phone_number: bool
    inbound_numbers: _containers.RepeatedScalarFieldContainer[str]
    name: str
    metadata: str
    attributes: _containers.ScalarMap[str, str]
    def __init__(self, sip_dispatch_rule_id: _Optional[str] = ..., rule: _Optional[_Union[SIPDispatchRule, _Mapping]] = ..., trunk_ids: _Optional[_Iterable[str]] = ..., hide_phone_number: bool = ..., inbound_numbers: _Optional[_Iterable[str]] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ListSIPDispatchRuleRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSIPDispatchRuleResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SIPDispatchRuleInfo]
    def __init__(self, items: _Optional[_Iterable[_Union[SIPDispatchRuleInfo, _Mapping]]] = ...) -> None: ...

class DeleteSIPDispatchRuleRequest(_message.Message):
    __slots__ = ("sip_dispatch_rule_id",)
    SIP_DISPATCH_RULE_ID_FIELD_NUMBER: _ClassVar[int]
    sip_dispatch_rule_id: str
    def __init__(self, sip_dispatch_rule_id: _Optional[str] = ...) -> None: ...

class CreateSIPParticipantRequest(_message.Message):
    __slots__ = ("sip_trunk_id", "sip_call_to", "room_name", "participant_identity", "participant_name", "participant_metadata", "participant_attributes", "dtmf", "play_ringtone", "play_dialtone", "hide_phone_number", "ringing_timeout", "max_call_duration", "enable_krisp")
    class ParticipantAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    SIP_CALL_TO_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_METADATA_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DTMF_FIELD_NUMBER: _ClassVar[int]
    PLAY_RINGTONE_FIELD_NUMBER: _ClassVar[int]
    PLAY_DIALTONE_FIELD_NUMBER: _ClassVar[int]
    HIDE_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    RINGING_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_CALL_DURATION_FIELD_NUMBER: _ClassVar[int]
    ENABLE_KRISP_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    sip_call_to: str
    room_name: str
    participant_identity: str
    participant_name: str
    participant_metadata: str
    participant_attributes: _containers.ScalarMap[str, str]
    dtmf: str
    play_ringtone: bool
    play_dialtone: bool
    hide_phone_number: bool
    ringing_timeout: _duration_pb2.Duration
    max_call_duration: _duration_pb2.Duration
    enable_krisp: bool
    def __init__(self, sip_trunk_id: _Optional[str] = ..., sip_call_to: _Optional[str] = ..., room_name: _Optional[str] = ..., participant_identity: _Optional[str] = ..., participant_name: _Optional[str] = ..., participant_metadata: _Optional[str] = ..., participant_attributes: _Optional[_Mapping[str, str]] = ..., dtmf: _Optional[str] = ..., play_ringtone: bool = ..., play_dialtone: bool = ..., hide_phone_number: bool = ..., ringing_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., max_call_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., enable_krisp: bool = ...) -> None: ...

class SIPParticipantInfo(_message.Message):
    __slots__ = ("participant_id", "participant_identity", "room_name", "sip_call_id")
    PARTICIPANT_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    SIP_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    participant_id: str
    participant_identity: str
    room_name: str
    sip_call_id: str
    def __init__(self, participant_id: _Optional[str] = ..., participant_identity: _Optional[str] = ..., room_name: _Optional[str] = ..., sip_call_id: _Optional[str] = ...) -> None: ...

class TransferSIPParticipantRequest(_message.Message):
    __slots__ = ("participant_identity", "room_name", "transfer_to", "play_dialtone")
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_TO_FIELD_NUMBER: _ClassVar[int]
    PLAY_DIALTONE_FIELD_NUMBER: _ClassVar[int]
    participant_identity: str
    room_name: str
    transfer_to: str
    play_dialtone: bool
    def __init__(self, participant_identity: _Optional[str] = ..., room_name: _Optional[str] = ..., transfer_to: _Optional[str] = ..., play_dialtone: bool = ...) -> None: ...

class SIPCallInfo(_message.Message):
    __slots__ = ("call_id", "trunk_id", "room_name", "room_id", "participant_identity", "from_uri", "to_uri", "call_status", "created_at", "started_at", "ended_at", "disconnect_reason", "error")
    CALL_ID_FIELD_NUMBER: _ClassVar[int]
    TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    FROM_URI_FIELD_NUMBER: _ClassVar[int]
    TO_URI_FIELD_NUMBER: _ClassVar[int]
    CALL_STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_REASON_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    call_id: str
    trunk_id: str
    room_name: str
    room_id: str
    participant_identity: str
    from_uri: SIPUri
    to_uri: SIPUri
    call_status: SIPCallStatus
    created_at: int
    started_at: int
    ended_at: int
    disconnect_reason: _models.DisconnectReason
    error: str
    def __init__(self, call_id: _Optional[str] = ..., trunk_id: _Optional[str] = ..., room_name: _Optional[str] = ..., room_id: _Optional[str] = ..., participant_identity: _Optional[str] = ..., from_uri: _Optional[_Union[SIPUri, _Mapping]] = ..., to_uri: _Optional[_Union[SIPUri, _Mapping]] = ..., call_status: _Optional[_Union[SIPCallStatus, str]] = ..., created_at: _Optional[int] = ..., started_at: _Optional[int] = ..., ended_at: _Optional[int] = ..., disconnect_reason: _Optional[_Union[_models.DisconnectReason, str]] = ..., error: _Optional[str] = ...) -> None: ...

class SIPUri(_message.Message):
    __slots__ = ("user", "host", "ip", "port", "transport")
    USER_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    user: str
    host: str
    ip: str
    port: str
    transport: SIPTransport
    def __init__(self, user: _Optional[str] = ..., host: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[str] = ..., transport: _Optional[_Union[SIPTransport, str]] = ...) -> None: ...
