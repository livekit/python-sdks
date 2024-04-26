from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateSIPTrunkRequest(_message.Message):
    __slots__ = ("inbound_addresses", "outbound_address", "outbound_number", "inbound_numbers_regex", "inbound_numbers", "inbound_username", "inbound_password", "outbound_username", "outbound_password")
    INBOUND_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_REGEX_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    INBOUND_USERNAME_FIELD_NUMBER: _ClassVar[int]
    INBOUND_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_USERNAME_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    inbound_addresses: _containers.RepeatedScalarFieldContainer[str]
    outbound_address: str
    outbound_number: str
    inbound_numbers_regex: _containers.RepeatedScalarFieldContainer[str]
    inbound_numbers: _containers.RepeatedScalarFieldContainer[str]
    inbound_username: str
    inbound_password: str
    outbound_username: str
    outbound_password: str
    def __init__(self, inbound_addresses: _Optional[_Iterable[str]] = ..., outbound_address: _Optional[str] = ..., outbound_number: _Optional[str] = ..., inbound_numbers_regex: _Optional[_Iterable[str]] = ..., inbound_numbers: _Optional[_Iterable[str]] = ..., inbound_username: _Optional[str] = ..., inbound_password: _Optional[str] = ..., outbound_username: _Optional[str] = ..., outbound_password: _Optional[str] = ...) -> None: ...

class SIPTrunkInfo(_message.Message):
    __slots__ = ("sip_trunk_id", "inbound_addresses", "outbound_address", "outbound_number", "inbound_numbers_regex", "inbound_numbers", "inbound_username", "inbound_password", "outbound_username", "outbound_password")
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    INBOUND_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_REGEX_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    INBOUND_USERNAME_FIELD_NUMBER: _ClassVar[int]
    INBOUND_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_USERNAME_FIELD_NUMBER: _ClassVar[int]
    OUTBOUND_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    inbound_addresses: _containers.RepeatedScalarFieldContainer[str]
    outbound_address: str
    outbound_number: str
    inbound_numbers_regex: _containers.RepeatedScalarFieldContainer[str]
    inbound_numbers: _containers.RepeatedScalarFieldContainer[str]
    inbound_username: str
    inbound_password: str
    outbound_username: str
    outbound_password: str
    def __init__(self, sip_trunk_id: _Optional[str] = ..., inbound_addresses: _Optional[_Iterable[str]] = ..., outbound_address: _Optional[str] = ..., outbound_number: _Optional[str] = ..., inbound_numbers_regex: _Optional[_Iterable[str]] = ..., inbound_numbers: _Optional[_Iterable[str]] = ..., inbound_username: _Optional[str] = ..., inbound_password: _Optional[str] = ..., outbound_username: _Optional[str] = ..., outbound_password: _Optional[str] = ...) -> None: ...

class ListSIPTrunkRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSIPTrunkResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SIPTrunkInfo]
    def __init__(self, items: _Optional[_Iterable[_Union[SIPTrunkInfo, _Mapping]]] = ...) -> None: ...

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

class SIPDispatchRule(_message.Message):
    __slots__ = ("dispatch_rule_direct", "dispatch_rule_individual")
    DISPATCH_RULE_DIRECT_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_RULE_INDIVIDUAL_FIELD_NUMBER: _ClassVar[int]
    dispatch_rule_direct: SIPDispatchRuleDirect
    dispatch_rule_individual: SIPDispatchRuleIndividual
    def __init__(self, dispatch_rule_direct: _Optional[_Union[SIPDispatchRuleDirect, _Mapping]] = ..., dispatch_rule_individual: _Optional[_Union[SIPDispatchRuleIndividual, _Mapping]] = ...) -> None: ...

class CreateSIPDispatchRuleRequest(_message.Message):
    __slots__ = ("rule", "trunk_ids", "hide_phone_number")
    RULE_FIELD_NUMBER: _ClassVar[int]
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    HIDE_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    rule: SIPDispatchRule
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    hide_phone_number: bool
    def __init__(self, rule: _Optional[_Union[SIPDispatchRule, _Mapping]] = ..., trunk_ids: _Optional[_Iterable[str]] = ..., hide_phone_number: bool = ...) -> None: ...

class SIPDispatchRuleInfo(_message.Message):
    __slots__ = ("sip_dispatch_rule_id", "rule", "trunk_ids", "hide_phone_number")
    SIP_DISPATCH_RULE_ID_FIELD_NUMBER: _ClassVar[int]
    RULE_FIELD_NUMBER: _ClassVar[int]
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    HIDE_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    sip_dispatch_rule_id: str
    rule: SIPDispatchRule
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    hide_phone_number: bool
    def __init__(self, sip_dispatch_rule_id: _Optional[str] = ..., rule: _Optional[_Union[SIPDispatchRule, _Mapping]] = ..., trunk_ids: _Optional[_Iterable[str]] = ..., hide_phone_number: bool = ...) -> None: ...

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
    __slots__ = ("sip_trunk_id", "sip_call_to", "room_name", "participant_identity", "dtmf", "play_ringtone")
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    SIP_CALL_TO_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    DTMF_FIELD_NUMBER: _ClassVar[int]
    PLAY_RINGTONE_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    sip_call_to: str
    room_name: str
    participant_identity: str
    dtmf: str
    play_ringtone: bool
    def __init__(self, sip_trunk_id: _Optional[str] = ..., sip_call_to: _Optional[str] = ..., room_name: _Optional[str] = ..., participant_identity: _Optional[str] = ..., dtmf: _Optional[str] = ..., play_ringtone: bool = ...) -> None: ...

class SIPParticipantInfo(_message.Message):
    __slots__ = ("participant_id", "participant_identity", "room_name")
    PARTICIPANT_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    participant_id: str
    participant_identity: str
    room_name: str
    def __init__(self, participant_id: _Optional[str] = ..., participant_identity: _Optional[str] = ..., room_name: _Optional[str] = ...) -> None: ...
