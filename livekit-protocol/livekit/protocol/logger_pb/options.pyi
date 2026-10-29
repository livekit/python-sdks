from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Sensitivity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SENSITIVITY_UNSPECIFIED: _ClassVar[Sensitivity]
    SENSITIVITY_PII: _ClassVar[Sensitivity]
    SENSITIVITY_SECRET: _ClassVar[Sensitivity]
SENSITIVITY_UNSPECIFIED: Sensitivity
SENSITIVITY_PII: Sensitivity
SENSITIVITY_SECRET: Sensitivity
REDACT_FORMAT_FIELD_NUMBER: int
redact_format: _descriptor.FieldDescriptor
NAME_FIELD_NUMBER: int
name: _descriptor.FieldDescriptor
SENSITIVITY_FIELD_NUMBER: int
sensitivity: _descriptor.FieldDescriptor
