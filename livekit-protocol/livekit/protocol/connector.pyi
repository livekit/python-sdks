from . import connector_whatsapp as _connector_whatsapp
from . import connector_twilio as _connector_twilio
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ConnectorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unspecified: _ClassVar[ConnectorType]
    WhatsApp: _ClassVar[ConnectorType]
    Twilio: _ClassVar[ConnectorType]
Unspecified: ConnectorType
WhatsApp: ConnectorType
Twilio: ConnectorType
