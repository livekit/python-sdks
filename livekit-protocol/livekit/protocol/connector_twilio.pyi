from . import agent_dispatch as _agent_dispatch
from .logger_pb import options as _options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConnectTwilioCallRequest(_message.Message):
    __slots__ = ("twilio_call_direction", "room_name", "agents", "participant_identity", "participant_name", "participant_metadata", "participant_attributes", "destination_country")
    class TwilioCallDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TWILIO_CALL_DIRECTION_INBOUND: _ClassVar[ConnectTwilioCallRequest.TwilioCallDirection]
        TWILIO_CALL_DIRECTION_OUTBOUND: _ClassVar[ConnectTwilioCallRequest.TwilioCallDirection]
    TWILIO_CALL_DIRECTION_INBOUND: ConnectTwilioCallRequest.TwilioCallDirection
    TWILIO_CALL_DIRECTION_OUTBOUND: ConnectTwilioCallRequest.TwilioCallDirection
    class ParticipantAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TWILIO_CALL_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    ROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_METADATA_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    twilio_call_direction: ConnectTwilioCallRequest.TwilioCallDirection
    room_name: str
    agents: _containers.RepeatedCompositeFieldContainer[_agent_dispatch.RoomAgentDispatch]
    participant_identity: str
    participant_name: str
    participant_metadata: str
    participant_attributes: _containers.ScalarMap[str, str]
    destination_country: str
    def __init__(self, twilio_call_direction: _Optional[_Union[ConnectTwilioCallRequest.TwilioCallDirection, str]] = ..., room_name: _Optional[str] = ..., agents: _Optional[_Iterable[_Union[_agent_dispatch.RoomAgentDispatch, _Mapping]]] = ..., participant_identity: _Optional[str] = ..., participant_name: _Optional[str] = ..., participant_metadata: _Optional[str] = ..., participant_attributes: _Optional[_Mapping[str, str]] = ..., destination_country: _Optional[str] = ...) -> None: ...

class ConnectTwilioCallResponse(_message.Message):
    __slots__ = ("connect_url",)
    CONNECT_URL_FIELD_NUMBER: _ClassVar[int]
    connect_url: str
    def __init__(self, connect_url: _Optional[str] = ...) -> None: ...
