from . import agent_dispatch as _agent_dispatch
from . import rtc as _rtc
from .logger_pb import options as _options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WhatsAppCallDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WHATSAPP_CALL_DIRECTION_INBOUND: _ClassVar[WhatsAppCallDirection]
    WHATSAPP_CALL_DIRECTION_OUTBOUND: _ClassVar[WhatsAppCallDirection]
WHATSAPP_CALL_DIRECTION_INBOUND: WhatsAppCallDirection
WHATSAPP_CALL_DIRECTION_OUTBOUND: WhatsAppCallDirection

class DialWhatsAppCallRequest(_message.Message):
    __slots__ = ("whatsapp_phone_number_id", "whatsapp_to_phone_number", "whatsapp_api_key", "whatsapp_cloud_api_version", "whatsapp_biz_opaque_callback_data", "room_name", "agents", "participant_identity", "participant_name", "participant_metadata", "participant_attributes", "destination_country")
    class ParticipantAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    WHATSAPP_PHONE_NUMBER_ID_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_TO_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_API_KEY_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_CLOUD_API_VERSION_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_BIZ_OPAQUE_CALLBACK_DATA_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_METADATA_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    whatsapp_phone_number_id: str
    whatsapp_to_phone_number: str
    whatsapp_api_key: str
    whatsapp_cloud_api_version: str
    whatsapp_biz_opaque_callback_data: str
    room_name: str
    agents: _containers.RepeatedCompositeFieldContainer[_agent_dispatch.RoomAgentDispatch]
    participant_identity: str
    participant_name: str
    participant_metadata: str
    participant_attributes: _containers.ScalarMap[str, str]
    destination_country: str
    def __init__(self, whatsapp_phone_number_id: _Optional[str] = ..., whatsapp_to_phone_number: _Optional[str] = ..., whatsapp_api_key: _Optional[str] = ..., whatsapp_cloud_api_version: _Optional[str] = ..., whatsapp_biz_opaque_callback_data: _Optional[str] = ..., room_name: _Optional[str] = ..., agents: _Optional[_Iterable[_Union[_agent_dispatch.RoomAgentDispatch, _Mapping]]] = ..., participant_identity: _Optional[str] = ..., participant_name: _Optional[str] = ..., participant_metadata: _Optional[str] = ..., participant_attributes: _Optional[_Mapping[str, str]] = ..., destination_country: _Optional[str] = ...) -> None: ...

class DialWhatsAppCallResponse(_message.Message):
    __slots__ = ("whatsapp_call_id", "room_name")
    WHATSAPP_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    whatsapp_call_id: str
    room_name: str
    def __init__(self, whatsapp_call_id: _Optional[str] = ..., room_name: _Optional[str] = ...) -> None: ...

class DisconnectWhatsAppCallRequest(_message.Message):
    __slots__ = ("whatsapp_call_id", "whatsapp_api_key")
    WHATSAPP_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_API_KEY_FIELD_NUMBER: _ClassVar[int]
    whatsapp_call_id: str
    whatsapp_api_key: str
    def __init__(self, whatsapp_call_id: _Optional[str] = ..., whatsapp_api_key: _Optional[str] = ...) -> None: ...

class DisconnectWhatsAppCallResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConnectWhatsAppCallRequest(_message.Message):
    __slots__ = ("whatsapp_call_id", "sdp")
    WHATSAPP_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    SDP_FIELD_NUMBER: _ClassVar[int]
    whatsapp_call_id: str
    sdp: _rtc.SessionDescription
    def __init__(self, whatsapp_call_id: _Optional[str] = ..., sdp: _Optional[_Union[_rtc.SessionDescription, _Mapping]] = ...) -> None: ...

class ConnectWhatsAppCallResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AcceptWhatsAppCallRequest(_message.Message):
    __slots__ = ("whatsapp_phone_number_id", "whatsapp_api_key", "whatsapp_cloud_api_version", "whatsapp_call_id", "whatsapp_biz_opaque_callback_data", "sdp", "room_name", "agents", "participant_identity", "participant_name", "participant_metadata", "participant_attributes", "destination_country")
    class ParticipantAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    WHATSAPP_PHONE_NUMBER_ID_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_API_KEY_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_CLOUD_API_VERSION_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_BIZ_OPAQUE_CALLBACK_DATA_FIELD_NUMBER: _ClassVar[int]
    SDP_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_METADATA_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    whatsapp_phone_number_id: str
    whatsapp_api_key: str
    whatsapp_cloud_api_version: str
    whatsapp_call_id: str
    whatsapp_biz_opaque_callback_data: str
    sdp: _rtc.SessionDescription
    room_name: str
    agents: _containers.RepeatedCompositeFieldContainer[_agent_dispatch.RoomAgentDispatch]
    participant_identity: str
    participant_name: str
    participant_metadata: str
    participant_attributes: _containers.ScalarMap[str, str]
    destination_country: str
    def __init__(self, whatsapp_phone_number_id: _Optional[str] = ..., whatsapp_api_key: _Optional[str] = ..., whatsapp_cloud_api_version: _Optional[str] = ..., whatsapp_call_id: _Optional[str] = ..., whatsapp_biz_opaque_callback_data: _Optional[str] = ..., sdp: _Optional[_Union[_rtc.SessionDescription, _Mapping]] = ..., room_name: _Optional[str] = ..., agents: _Optional[_Iterable[_Union[_agent_dispatch.RoomAgentDispatch, _Mapping]]] = ..., participant_identity: _Optional[str] = ..., participant_name: _Optional[str] = ..., participant_metadata: _Optional[str] = ..., participant_attributes: _Optional[_Mapping[str, str]] = ..., destination_country: _Optional[str] = ...) -> None: ...

class AcceptWhatsAppCallResponse(_message.Message):
    __slots__ = ("room_name",)
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    room_name: str
    def __init__(self, room_name: _Optional[str] = ...) -> None: ...

class WhatsAppCall(_message.Message):
    __slots__ = ("whatsapp_call_id", "direction")
    WHATSAPP_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    whatsapp_call_id: str
    direction: WhatsAppCallDirection
    def __init__(self, whatsapp_call_id: _Optional[str] = ..., direction: _Optional[_Union[WhatsAppCallDirection, str]] = ...) -> None: ...
