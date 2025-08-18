from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from . import models as _models
from . import room as _room
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SIPStatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIP_STATUS_UNKNOWN: _ClassVar[SIPStatusCode]
    SIP_STATUS_TRYING: _ClassVar[SIPStatusCode]
    SIP_STATUS_RINGING: _ClassVar[SIPStatusCode]
    SIP_STATUS_CALL_IS_FORWARDED: _ClassVar[SIPStatusCode]
    SIP_STATUS_QUEUED: _ClassVar[SIPStatusCode]
    SIP_STATUS_SESSION_PROGRESS: _ClassVar[SIPStatusCode]
    SIP_STATUS_OK: _ClassVar[SIPStatusCode]
    SIP_STATUS_ACCEPTED: _ClassVar[SIPStatusCode]
    SIP_STATUS_MOVED_PERMANENTLY: _ClassVar[SIPStatusCode]
    SIP_STATUS_MOVED_TEMPORARILY: _ClassVar[SIPStatusCode]
    SIP_STATUS_USE_PROXY: _ClassVar[SIPStatusCode]
    SIP_STATUS_BAD_REQUEST: _ClassVar[SIPStatusCode]
    SIP_STATUS_UNAUTHORIZED: _ClassVar[SIPStatusCode]
    SIP_STATUS_PAYMENT_REQUIRED: _ClassVar[SIPStatusCode]
    SIP_STATUS_FORBIDDEN: _ClassVar[SIPStatusCode]
    SIP_STATUS_NOTFOUND: _ClassVar[SIPStatusCode]
    SIP_STATUS_METHOD_NOT_ALLOWED: _ClassVar[SIPStatusCode]
    SIP_STATUS_NOT_ACCEPTABLE: _ClassVar[SIPStatusCode]
    SIP_STATUS_PROXY_AUTH_REQUIRED: _ClassVar[SIPStatusCode]
    SIP_STATUS_REQUEST_TIMEOUT: _ClassVar[SIPStatusCode]
    SIP_STATUS_CONFLICT: _ClassVar[SIPStatusCode]
    SIP_STATUS_GONE: _ClassVar[SIPStatusCode]
    SIP_STATUS_REQUEST_ENTITY_TOO_LARGE: _ClassVar[SIPStatusCode]
    SIP_STATUS_REQUEST_URI_TOO_LONG: _ClassVar[SIPStatusCode]
    SIP_STATUS_UNSUPPORTED_MEDIA_TYPE: _ClassVar[SIPStatusCode]
    SIP_STATUS_REQUESTED_RANGE_NOT_SATISFIABLE: _ClassVar[SIPStatusCode]
    SIP_STATUS_BAD_EXTENSION: _ClassVar[SIPStatusCode]
    SIP_STATUS_EXTENSION_REQUIRED: _ClassVar[SIPStatusCode]
    SIP_STATUS_INTERVAL_TOO_BRIEF: _ClassVar[SIPStatusCode]
    SIP_STATUS_TEMPORARILY_UNAVAILABLE: _ClassVar[SIPStatusCode]
    SIP_STATUS_CALL_TRANSACTION_DOES_NOT_EXISTS: _ClassVar[SIPStatusCode]
    SIP_STATUS_LOOP_DETECTED: _ClassVar[SIPStatusCode]
    SIP_STATUS_TOO_MANY_HOPS: _ClassVar[SIPStatusCode]
    SIP_STATUS_ADDRESS_INCOMPLETE: _ClassVar[SIPStatusCode]
    SIP_STATUS_AMBIGUOUS: _ClassVar[SIPStatusCode]
    SIP_STATUS_BUSY_HERE: _ClassVar[SIPStatusCode]
    SIP_STATUS_REQUEST_TERMINATED: _ClassVar[SIPStatusCode]
    SIP_STATUS_NOT_ACCEPTABLE_HERE: _ClassVar[SIPStatusCode]
    SIP_STATUS_INTERNAL_SERVER_ERROR: _ClassVar[SIPStatusCode]
    SIP_STATUS_NOT_IMPLEMENTED: _ClassVar[SIPStatusCode]
    SIP_STATUS_BAD_GATEWAY: _ClassVar[SIPStatusCode]
    SIP_STATUS_SERVICE_UNAVAILABLE: _ClassVar[SIPStatusCode]
    SIP_STATUS_GATEWAY_TIMEOUT: _ClassVar[SIPStatusCode]
    SIP_STATUS_VERSION_NOT_SUPPORTED: _ClassVar[SIPStatusCode]
    SIP_STATUS_MESSAGE_TOO_LARGE: _ClassVar[SIPStatusCode]
    SIP_STATUS_GLOBAL_BUSY_EVERYWHERE: _ClassVar[SIPStatusCode]
    SIP_STATUS_GLOBAL_DECLINE: _ClassVar[SIPStatusCode]
    SIP_STATUS_GLOBAL_DOES_NOT_EXIST_ANYWHERE: _ClassVar[SIPStatusCode]
    SIP_STATUS_GLOBAL_NOT_ACCEPTABLE: _ClassVar[SIPStatusCode]

class SIPTransport(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIP_TRANSPORT_AUTO: _ClassVar[SIPTransport]
    SIP_TRANSPORT_UDP: _ClassVar[SIPTransport]
    SIP_TRANSPORT_TCP: _ClassVar[SIPTransport]
    SIP_TRANSPORT_TLS: _ClassVar[SIPTransport]

class SIPHeaderOptions(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIP_NO_HEADERS: _ClassVar[SIPHeaderOptions]
    SIP_X_HEADERS: _ClassVar[SIPHeaderOptions]
    SIP_ALL_HEADERS: _ClassVar[SIPHeaderOptions]

class SIPMediaEncryption(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIP_MEDIA_ENCRYPT_DISABLE: _ClassVar[SIPMediaEncryption]
    SIP_MEDIA_ENCRYPT_ALLOW: _ClassVar[SIPMediaEncryption]
    SIP_MEDIA_ENCRYPT_REQUIRE: _ClassVar[SIPMediaEncryption]

class SIPCallStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCS_CALL_INCOMING: _ClassVar[SIPCallStatus]
    SCS_PARTICIPANT_JOINED: _ClassVar[SIPCallStatus]
    SCS_ACTIVE: _ClassVar[SIPCallStatus]
    SCS_DISCONNECTED: _ClassVar[SIPCallStatus]
    SCS_ERROR: _ClassVar[SIPCallStatus]

class SIPTransferStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STS_TRANSFER_ONGOING: _ClassVar[SIPTransferStatus]
    STS_TRANSFER_FAILED: _ClassVar[SIPTransferStatus]
    STS_TRANSFER_SUCCESSFUL: _ClassVar[SIPTransferStatus]

class SIPFeature(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NONE: _ClassVar[SIPFeature]
    KRISP_ENABLED: _ClassVar[SIPFeature]

class SIPCallDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCD_UNKNOWN: _ClassVar[SIPCallDirection]
    SCD_INBOUND: _ClassVar[SIPCallDirection]
    SCD_OUTBOUND: _ClassVar[SIPCallDirection]
SIP_STATUS_UNKNOWN: SIPStatusCode
SIP_STATUS_TRYING: SIPStatusCode
SIP_STATUS_RINGING: SIPStatusCode
SIP_STATUS_CALL_IS_FORWARDED: SIPStatusCode
SIP_STATUS_QUEUED: SIPStatusCode
SIP_STATUS_SESSION_PROGRESS: SIPStatusCode
SIP_STATUS_OK: SIPStatusCode
SIP_STATUS_ACCEPTED: SIPStatusCode
SIP_STATUS_MOVED_PERMANENTLY: SIPStatusCode
SIP_STATUS_MOVED_TEMPORARILY: SIPStatusCode
SIP_STATUS_USE_PROXY: SIPStatusCode
SIP_STATUS_BAD_REQUEST: SIPStatusCode
SIP_STATUS_UNAUTHORIZED: SIPStatusCode
SIP_STATUS_PAYMENT_REQUIRED: SIPStatusCode
SIP_STATUS_FORBIDDEN: SIPStatusCode
SIP_STATUS_NOTFOUND: SIPStatusCode
SIP_STATUS_METHOD_NOT_ALLOWED: SIPStatusCode
SIP_STATUS_NOT_ACCEPTABLE: SIPStatusCode
SIP_STATUS_PROXY_AUTH_REQUIRED: SIPStatusCode
SIP_STATUS_REQUEST_TIMEOUT: SIPStatusCode
SIP_STATUS_CONFLICT: SIPStatusCode
SIP_STATUS_GONE: SIPStatusCode
SIP_STATUS_REQUEST_ENTITY_TOO_LARGE: SIPStatusCode
SIP_STATUS_REQUEST_URI_TOO_LONG: SIPStatusCode
SIP_STATUS_UNSUPPORTED_MEDIA_TYPE: SIPStatusCode
SIP_STATUS_REQUESTED_RANGE_NOT_SATISFIABLE: SIPStatusCode
SIP_STATUS_BAD_EXTENSION: SIPStatusCode
SIP_STATUS_EXTENSION_REQUIRED: SIPStatusCode
SIP_STATUS_INTERVAL_TOO_BRIEF: SIPStatusCode
SIP_STATUS_TEMPORARILY_UNAVAILABLE: SIPStatusCode
SIP_STATUS_CALL_TRANSACTION_DOES_NOT_EXISTS: SIPStatusCode
SIP_STATUS_LOOP_DETECTED: SIPStatusCode
SIP_STATUS_TOO_MANY_HOPS: SIPStatusCode
SIP_STATUS_ADDRESS_INCOMPLETE: SIPStatusCode
SIP_STATUS_AMBIGUOUS: SIPStatusCode
SIP_STATUS_BUSY_HERE: SIPStatusCode
SIP_STATUS_REQUEST_TERMINATED: SIPStatusCode
SIP_STATUS_NOT_ACCEPTABLE_HERE: SIPStatusCode
SIP_STATUS_INTERNAL_SERVER_ERROR: SIPStatusCode
SIP_STATUS_NOT_IMPLEMENTED: SIPStatusCode
SIP_STATUS_BAD_GATEWAY: SIPStatusCode
SIP_STATUS_SERVICE_UNAVAILABLE: SIPStatusCode
SIP_STATUS_GATEWAY_TIMEOUT: SIPStatusCode
SIP_STATUS_VERSION_NOT_SUPPORTED: SIPStatusCode
SIP_STATUS_MESSAGE_TOO_LARGE: SIPStatusCode
SIP_STATUS_GLOBAL_BUSY_EVERYWHERE: SIPStatusCode
SIP_STATUS_GLOBAL_DECLINE: SIPStatusCode
SIP_STATUS_GLOBAL_DOES_NOT_EXIST_ANYWHERE: SIPStatusCode
SIP_STATUS_GLOBAL_NOT_ACCEPTABLE: SIPStatusCode
SIP_TRANSPORT_AUTO: SIPTransport
SIP_TRANSPORT_UDP: SIPTransport
SIP_TRANSPORT_TCP: SIPTransport
SIP_TRANSPORT_TLS: SIPTransport
SIP_NO_HEADERS: SIPHeaderOptions
SIP_X_HEADERS: SIPHeaderOptions
SIP_ALL_HEADERS: SIPHeaderOptions
SIP_MEDIA_ENCRYPT_DISABLE: SIPMediaEncryption
SIP_MEDIA_ENCRYPT_ALLOW: SIPMediaEncryption
SIP_MEDIA_ENCRYPT_REQUIRE: SIPMediaEncryption
SCS_CALL_INCOMING: SIPCallStatus
SCS_PARTICIPANT_JOINED: SIPCallStatus
SCS_ACTIVE: SIPCallStatus
SCS_DISCONNECTED: SIPCallStatus
SCS_ERROR: SIPCallStatus
STS_TRANSFER_ONGOING: SIPTransferStatus
STS_TRANSFER_FAILED: SIPTransferStatus
STS_TRANSFER_SUCCESSFUL: SIPTransferStatus
NONE: SIPFeature
KRISP_ENABLED: SIPFeature
SCD_UNKNOWN: SIPCallDirection
SCD_INBOUND: SIPCallDirection
SCD_OUTBOUND: SIPCallDirection

class SIPStatus(_message.Message):
    __slots__ = ("code", "status")
    CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    code: SIPStatusCode
    status: str
    def __init__(self, code: _Optional[_Union[SIPStatusCode, str]] = ..., status: _Optional[str] = ...) -> None: ...

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

class UpdateSIPInboundTrunkRequest(_message.Message):
    __slots__ = ("sip_trunk_id", "replace", "update")
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    REPLACE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    replace: SIPInboundTrunkInfo
    update: SIPInboundTrunkUpdate
    def __init__(self, sip_trunk_id: _Optional[str] = ..., replace: _Optional[_Union[SIPInboundTrunkInfo, _Mapping]] = ..., update: _Optional[_Union[SIPInboundTrunkUpdate, _Mapping]] = ...) -> None: ...

class SIPInboundTrunkInfo(_message.Message):
    __slots__ = ("sip_trunk_id", "name", "metadata", "numbers", "allowed_addresses", "allowed_numbers", "auth_username", "auth_password", "headers", "headers_to_attributes", "attributes_to_headers", "include_headers", "ringing_timeout", "max_call_duration", "krisp_enabled", "media_encryption")
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
    class AttributesToHeadersEntry(_message.Message):
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
    ATTRIBUTES_TO_HEADERS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RINGING_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_CALL_DURATION_FIELD_NUMBER: _ClassVar[int]
    KRISP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
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
    attributes_to_headers: _containers.ScalarMap[str, str]
    include_headers: SIPHeaderOptions
    ringing_timeout: _duration_pb2.Duration
    max_call_duration: _duration_pb2.Duration
    krisp_enabled: bool
    media_encryption: SIPMediaEncryption
    def __init__(self, sip_trunk_id: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., numbers: _Optional[_Iterable[str]] = ..., allowed_addresses: _Optional[_Iterable[str]] = ..., allowed_numbers: _Optional[_Iterable[str]] = ..., auth_username: _Optional[str] = ..., auth_password: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ..., headers_to_attributes: _Optional[_Mapping[str, str]] = ..., attributes_to_headers: _Optional[_Mapping[str, str]] = ..., include_headers: _Optional[_Union[SIPHeaderOptions, str]] = ..., ringing_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., max_call_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., krisp_enabled: bool = ..., media_encryption: _Optional[_Union[SIPMediaEncryption, str]] = ...) -> None: ...

class SIPInboundTrunkUpdate(_message.Message):
    __slots__ = ("numbers", "allowed_addresses", "allowed_numbers", "auth_username", "auth_password", "name", "metadata", "media_encryption")
    NUMBERS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    AUTH_USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    numbers: _models.ListUpdate
    allowed_addresses: _models.ListUpdate
    allowed_numbers: _models.ListUpdate
    auth_username: str
    auth_password: str
    name: str
    metadata: str
    media_encryption: SIPMediaEncryption
    def __init__(self, numbers: _Optional[_Union[_models.ListUpdate, _Mapping]] = ..., allowed_addresses: _Optional[_Union[_models.ListUpdate, _Mapping]] = ..., allowed_numbers: _Optional[_Union[_models.ListUpdate, _Mapping]] = ..., auth_username: _Optional[str] = ..., auth_password: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., media_encryption: _Optional[_Union[SIPMediaEncryption, str]] = ...) -> None: ...

class CreateSIPOutboundTrunkRequest(_message.Message):
    __slots__ = ("trunk",)
    TRUNK_FIELD_NUMBER: _ClassVar[int]
    trunk: SIPOutboundTrunkInfo
    def __init__(self, trunk: _Optional[_Union[SIPOutboundTrunkInfo, _Mapping]] = ...) -> None: ...

class UpdateSIPOutboundTrunkRequest(_message.Message):
    __slots__ = ("sip_trunk_id", "replace", "update")
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    REPLACE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    replace: SIPOutboundTrunkInfo
    update: SIPOutboundTrunkUpdate
    def __init__(self, sip_trunk_id: _Optional[str] = ..., replace: _Optional[_Union[SIPOutboundTrunkInfo, _Mapping]] = ..., update: _Optional[_Union[SIPOutboundTrunkUpdate, _Mapping]] = ...) -> None: ...

class SIPOutboundTrunkInfo(_message.Message):
    __slots__ = ("sip_trunk_id", "name", "metadata", "address", "destination_country", "transport", "numbers", "auth_username", "auth_password", "headers", "headers_to_attributes", "attributes_to_headers", "include_headers", "media_encryption")
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
    class AttributesToHeadersEntry(_message.Message):
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
    DESTINATION_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    NUMBERS_FIELD_NUMBER: _ClassVar[int]
    AUTH_USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_TO_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_TO_HEADERS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    name: str
    metadata: str
    address: str
    destination_country: str
    transport: SIPTransport
    numbers: _containers.RepeatedScalarFieldContainer[str]
    auth_username: str
    auth_password: str
    headers: _containers.ScalarMap[str, str]
    headers_to_attributes: _containers.ScalarMap[str, str]
    attributes_to_headers: _containers.ScalarMap[str, str]
    include_headers: SIPHeaderOptions
    media_encryption: SIPMediaEncryption
    def __init__(self, sip_trunk_id: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., address: _Optional[str] = ..., destination_country: _Optional[str] = ..., transport: _Optional[_Union[SIPTransport, str]] = ..., numbers: _Optional[_Iterable[str]] = ..., auth_username: _Optional[str] = ..., auth_password: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ..., headers_to_attributes: _Optional[_Mapping[str, str]] = ..., attributes_to_headers: _Optional[_Mapping[str, str]] = ..., include_headers: _Optional[_Union[SIPHeaderOptions, str]] = ..., media_encryption: _Optional[_Union[SIPMediaEncryption, str]] = ...) -> None: ...

class SIPOutboundTrunkUpdate(_message.Message):
    __slots__ = ("address", "transport", "destination_country", "numbers", "auth_username", "auth_password", "name", "metadata", "media_encryption")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    NUMBERS_FIELD_NUMBER: _ClassVar[int]
    AUTH_USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    address: str
    transport: SIPTransport
    destination_country: str
    numbers: _models.ListUpdate
    auth_username: str
    auth_password: str
    name: str
    metadata: str
    media_encryption: SIPMediaEncryption
    def __init__(self, address: _Optional[str] = ..., transport: _Optional[_Union[SIPTransport, str]] = ..., destination_country: _Optional[str] = ..., numbers: _Optional[_Union[_models.ListUpdate, _Mapping]] = ..., auth_username: _Optional[str] = ..., auth_password: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., media_encryption: _Optional[_Union[SIPMediaEncryption, str]] = ...) -> None: ...

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
    __slots__ = ("page",)
    PAGE_FIELD_NUMBER: _ClassVar[int]
    page: _models.Pagination
    def __init__(self, page: _Optional[_Union[_models.Pagination, _Mapping]] = ...) -> None: ...

class ListSIPTrunkResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SIPTrunkInfo]
    def __init__(self, items: _Optional[_Iterable[_Union[SIPTrunkInfo, _Mapping]]] = ...) -> None: ...

class ListSIPInboundTrunkRequest(_message.Message):
    __slots__ = ("page", "trunk_ids", "numbers")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    NUMBERS_FIELD_NUMBER: _ClassVar[int]
    page: _models.Pagination
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    numbers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, page: _Optional[_Union[_models.Pagination, _Mapping]] = ..., trunk_ids: _Optional[_Iterable[str]] = ..., numbers: _Optional[_Iterable[str]] = ...) -> None: ...

class ListSIPInboundTrunkResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SIPInboundTrunkInfo]
    def __init__(self, items: _Optional[_Iterable[_Union[SIPInboundTrunkInfo, _Mapping]]] = ...) -> None: ...

class ListSIPOutboundTrunkRequest(_message.Message):
    __slots__ = ("page", "trunk_ids", "numbers")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    NUMBERS_FIELD_NUMBER: _ClassVar[int]
    page: _models.Pagination
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    numbers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, page: _Optional[_Union[_models.Pagination, _Mapping]] = ..., trunk_ids: _Optional[_Iterable[str]] = ..., numbers: _Optional[_Iterable[str]] = ...) -> None: ...

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
    __slots__ = ("dispatch_rule", "rule", "trunk_ids", "hide_phone_number", "inbound_numbers", "name", "metadata", "attributes", "room_preset", "room_config")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DISPATCH_RULE_FIELD_NUMBER: _ClassVar[int]
    RULE_FIELD_NUMBER: _ClassVar[int]
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    HIDE_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    INBOUND_NUMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    ROOM_PRESET_FIELD_NUMBER: _ClassVar[int]
    ROOM_CONFIG_FIELD_NUMBER: _ClassVar[int]
    dispatch_rule: SIPDispatchRuleInfo
    rule: SIPDispatchRule
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    hide_phone_number: bool
    inbound_numbers: _containers.RepeatedScalarFieldContainer[str]
    name: str
    metadata: str
    attributes: _containers.ScalarMap[str, str]
    room_preset: str
    room_config: _room.RoomConfiguration
    def __init__(self, dispatch_rule: _Optional[_Union[SIPDispatchRuleInfo, _Mapping]] = ..., rule: _Optional[_Union[SIPDispatchRule, _Mapping]] = ..., trunk_ids: _Optional[_Iterable[str]] = ..., hide_phone_number: bool = ..., inbound_numbers: _Optional[_Iterable[str]] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ..., room_preset: _Optional[str] = ..., room_config: _Optional[_Union[_room.RoomConfiguration, _Mapping]] = ...) -> None: ...

class UpdateSIPDispatchRuleRequest(_message.Message):
    __slots__ = ("sip_dispatch_rule_id", "replace", "update")
    SIP_DISPATCH_RULE_ID_FIELD_NUMBER: _ClassVar[int]
    REPLACE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    sip_dispatch_rule_id: str
    replace: SIPDispatchRuleInfo
    update: SIPDispatchRuleUpdate
    def __init__(self, sip_dispatch_rule_id: _Optional[str] = ..., replace: _Optional[_Union[SIPDispatchRuleInfo, _Mapping]] = ..., update: _Optional[_Union[SIPDispatchRuleUpdate, _Mapping]] = ...) -> None: ...

class SIPDispatchRuleInfo(_message.Message):
    __slots__ = ("sip_dispatch_rule_id", "rule", "trunk_ids", "hide_phone_number", "inbound_numbers", "name", "metadata", "attributes", "room_preset", "room_config", "krisp_enabled", "media_encryption")
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
    ROOM_PRESET_FIELD_NUMBER: _ClassVar[int]
    ROOM_CONFIG_FIELD_NUMBER: _ClassVar[int]
    KRISP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    sip_dispatch_rule_id: str
    rule: SIPDispatchRule
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    hide_phone_number: bool
    inbound_numbers: _containers.RepeatedScalarFieldContainer[str]
    name: str
    metadata: str
    attributes: _containers.ScalarMap[str, str]
    room_preset: str
    room_config: _room.RoomConfiguration
    krisp_enabled: bool
    media_encryption: SIPMediaEncryption
    def __init__(self, sip_dispatch_rule_id: _Optional[str] = ..., rule: _Optional[_Union[SIPDispatchRule, _Mapping]] = ..., trunk_ids: _Optional[_Iterable[str]] = ..., hide_phone_number: bool = ..., inbound_numbers: _Optional[_Iterable[str]] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ..., room_preset: _Optional[str] = ..., room_config: _Optional[_Union[_room.RoomConfiguration, _Mapping]] = ..., krisp_enabled: bool = ..., media_encryption: _Optional[_Union[SIPMediaEncryption, str]] = ...) -> None: ...

class SIPDispatchRuleUpdate(_message.Message):
    __slots__ = ("trunk_ids", "rule", "name", "metadata", "attributes", "media_encryption")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    RULE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    trunk_ids: _models.ListUpdate
    rule: SIPDispatchRule
    name: str
    metadata: str
    attributes: _containers.ScalarMap[str, str]
    media_encryption: SIPMediaEncryption
    def __init__(self, trunk_ids: _Optional[_Union[_models.ListUpdate, _Mapping]] = ..., rule: _Optional[_Union[SIPDispatchRule, _Mapping]] = ..., name: _Optional[str] = ..., metadata: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ..., media_encryption: _Optional[_Union[SIPMediaEncryption, str]] = ...) -> None: ...

class ListSIPDispatchRuleRequest(_message.Message):
    __slots__ = ("page", "dispatch_rule_ids", "trunk_ids")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_RULE_IDS_FIELD_NUMBER: _ClassVar[int]
    TRUNK_IDS_FIELD_NUMBER: _ClassVar[int]
    page: _models.Pagination
    dispatch_rule_ids: _containers.RepeatedScalarFieldContainer[str]
    trunk_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, page: _Optional[_Union[_models.Pagination, _Mapping]] = ..., dispatch_rule_ids: _Optional[_Iterable[str]] = ..., trunk_ids: _Optional[_Iterable[str]] = ...) -> None: ...

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

class SIPOutboundConfig(_message.Message):
    __slots__ = ("hostname", "destination_country", "transport", "auth_username", "auth_password", "headers_to_attributes", "attributes_to_headers")
    class HeadersToAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class AttributesToHeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    AUTH_USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    HEADERS_TO_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_TO_HEADERS_FIELD_NUMBER: _ClassVar[int]
    hostname: str
    destination_country: str
    transport: SIPTransport
    auth_username: str
    auth_password: str
    headers_to_attributes: _containers.ScalarMap[str, str]
    attributes_to_headers: _containers.ScalarMap[str, str]
    def __init__(self, hostname: _Optional[str] = ..., destination_country: _Optional[str] = ..., transport: _Optional[_Union[SIPTransport, str]] = ..., auth_username: _Optional[str] = ..., auth_password: _Optional[str] = ..., headers_to_attributes: _Optional[_Mapping[str, str]] = ..., attributes_to_headers: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CreateSIPParticipantRequest(_message.Message):
    __slots__ = ("sip_trunk_id", "trunk", "sip_call_to", "sip_number", "room_name", "participant_identity", "participant_name", "participant_metadata", "participant_attributes", "dtmf", "play_ringtone", "play_dialtone", "hide_phone_number", "headers", "include_headers", "ringing_timeout", "max_call_duration", "krisp_enabled", "media_encryption", "wait_until_answered")
    class ParticipantAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SIP_TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    TRUNK_FIELD_NUMBER: _ClassVar[int]
    SIP_CALL_TO_FIELD_NUMBER: _ClassVar[int]
    SIP_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_METADATA_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DTMF_FIELD_NUMBER: _ClassVar[int]
    PLAY_RINGTONE_FIELD_NUMBER: _ClassVar[int]
    PLAY_DIALTONE_FIELD_NUMBER: _ClassVar[int]
    HIDE_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RINGING_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_CALL_DURATION_FIELD_NUMBER: _ClassVar[int]
    KRISP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    WAIT_UNTIL_ANSWERED_FIELD_NUMBER: _ClassVar[int]
    sip_trunk_id: str
    trunk: SIPOutboundConfig
    sip_call_to: str
    sip_number: str
    room_name: str
    participant_identity: str
    participant_name: str
    participant_metadata: str
    participant_attributes: _containers.ScalarMap[str, str]
    dtmf: str
    play_ringtone: bool
    play_dialtone: bool
    hide_phone_number: bool
    headers: _containers.ScalarMap[str, str]
    include_headers: SIPHeaderOptions
    ringing_timeout: _duration_pb2.Duration
    max_call_duration: _duration_pb2.Duration
    krisp_enabled: bool
    media_encryption: SIPMediaEncryption
    wait_until_answered: bool
    def __init__(self, sip_trunk_id: _Optional[str] = ..., trunk: _Optional[_Union[SIPOutboundConfig, _Mapping]] = ..., sip_call_to: _Optional[str] = ..., sip_number: _Optional[str] = ..., room_name: _Optional[str] = ..., participant_identity: _Optional[str] = ..., participant_name: _Optional[str] = ..., participant_metadata: _Optional[str] = ..., participant_attributes: _Optional[_Mapping[str, str]] = ..., dtmf: _Optional[str] = ..., play_ringtone: bool = ..., play_dialtone: bool = ..., hide_phone_number: bool = ..., headers: _Optional[_Mapping[str, str]] = ..., include_headers: _Optional[_Union[SIPHeaderOptions, str]] = ..., ringing_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., max_call_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., krisp_enabled: bool = ..., media_encryption: _Optional[_Union[SIPMediaEncryption, str]] = ..., wait_until_answered: bool = ...) -> None: ...

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
    __slots__ = ("participant_identity", "room_name", "transfer_to", "play_dialtone", "headers", "ringing_timeout")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_TO_FIELD_NUMBER: _ClassVar[int]
    PLAY_DIALTONE_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    RINGING_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    participant_identity: str
    room_name: str
    transfer_to: str
    play_dialtone: bool
    headers: _containers.ScalarMap[str, str]
    ringing_timeout: _duration_pb2.Duration
    def __init__(self, participant_identity: _Optional[str] = ..., room_name: _Optional[str] = ..., transfer_to: _Optional[str] = ..., play_dialtone: bool = ..., headers: _Optional[_Mapping[str, str]] = ..., ringing_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class SIPCallInfo(_message.Message):
    __slots__ = ("call_id", "trunk_id", "dispatch_rule_id", "region", "room_name", "room_id", "participant_identity", "participant_attributes", "from_uri", "to_uri", "created_at", "started_at", "ended_at", "enabled_features", "call_direction", "call_status", "created_at_ns", "started_at_ns", "ended_at_ns", "disconnect_reason", "error", "call_status_code", "audio_codec", "media_encryption")
    class ParticipantAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CALL_ID_FIELD_NUMBER: _ClassVar[int]
    TRUNK_ID_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_RULE_ID_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    FROM_URI_FIELD_NUMBER: _ClassVar[int]
    TO_URI_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FEATURES_FIELD_NUMBER: _ClassVar[int]
    CALL_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    CALL_STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_NS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_NS_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_NS_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_REASON_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CALL_STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    AUDIO_CODEC_FIELD_NUMBER: _ClassVar[int]
    MEDIA_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    call_id: str
    trunk_id: str
    dispatch_rule_id: str
    region: str
    room_name: str
    room_id: str
    participant_identity: str
    participant_attributes: _containers.ScalarMap[str, str]
    from_uri: SIPUri
    to_uri: SIPUri
    created_at: int
    started_at: int
    ended_at: int
    enabled_features: _containers.RepeatedScalarFieldContainer[SIPFeature]
    call_direction: SIPCallDirection
    call_status: SIPCallStatus
    created_at_ns: int
    started_at_ns: int
    ended_at_ns: int
    disconnect_reason: _models.DisconnectReason
    error: str
    call_status_code: SIPStatus
    audio_codec: str
    media_encryption: str
    def __init__(self, call_id: _Optional[str] = ..., trunk_id: _Optional[str] = ..., dispatch_rule_id: _Optional[str] = ..., region: _Optional[str] = ..., room_name: _Optional[str] = ..., room_id: _Optional[str] = ..., participant_identity: _Optional[str] = ..., participant_attributes: _Optional[_Mapping[str, str]] = ..., from_uri: _Optional[_Union[SIPUri, _Mapping]] = ..., to_uri: _Optional[_Union[SIPUri, _Mapping]] = ..., created_at: _Optional[int] = ..., started_at: _Optional[int] = ..., ended_at: _Optional[int] = ..., enabled_features: _Optional[_Iterable[_Union[SIPFeature, str]]] = ..., call_direction: _Optional[_Union[SIPCallDirection, str]] = ..., call_status: _Optional[_Union[SIPCallStatus, str]] = ..., created_at_ns: _Optional[int] = ..., started_at_ns: _Optional[int] = ..., ended_at_ns: _Optional[int] = ..., disconnect_reason: _Optional[_Union[_models.DisconnectReason, str]] = ..., error: _Optional[str] = ..., call_status_code: _Optional[_Union[SIPStatus, _Mapping]] = ..., audio_codec: _Optional[str] = ..., media_encryption: _Optional[str] = ...) -> None: ...

class SIPTransferInfo(_message.Message):
    __slots__ = ("transfer_id", "call_id", "transfer_to", "transfer_initiated_at_ns", "transfer_completed_at_ns", "transfer_status", "error", "transfer_status_code")
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    CALL_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_TO_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_INITIATED_AT_NS_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_COMPLETED_AT_NS_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    call_id: str
    transfer_to: str
    transfer_initiated_at_ns: int
    transfer_completed_at_ns: int
    transfer_status: SIPTransferStatus
    error: str
    transfer_status_code: SIPStatus
    def __init__(self, transfer_id: _Optional[str] = ..., call_id: _Optional[str] = ..., transfer_to: _Optional[str] = ..., transfer_initiated_at_ns: _Optional[int] = ..., transfer_completed_at_ns: _Optional[int] = ..., transfer_status: _Optional[_Union[SIPTransferStatus, str]] = ..., error: _Optional[str] = ..., transfer_status_code: _Optional[_Union[SIPStatus, _Mapping]] = ...) -> None: ...

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
    port: int
    transport: SIPTransport
    def __init__(self, user: _Optional[str] = ..., host: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[int] = ..., transport: _Optional[_Union[SIPTransport, str]] = ...) -> None: ...
