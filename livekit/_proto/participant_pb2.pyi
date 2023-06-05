import track_pb2 as _track_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParticipantInfo(_message.Message):
    __slots__ = ["sid", "name", "identity", "metadata", "publications"]
    SID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PUBLICATIONS_FIELD_NUMBER: _ClassVar[int]
    sid: str
    name: str
    identity: str
    metadata: str
    publications: _containers.RepeatedCompositeFieldContainer[_track_pb2.TrackPublicationInfo]
    def __init__(self, sid: _Optional[str] = ..., name: _Optional[str] = ..., identity: _Optional[str] = ..., metadata: _Optional[str] = ..., publications: _Optional[_Iterable[_Union[_track_pb2.TrackPublicationInfo, _Mapping]]] = ...) -> None: ...

class ParticipantEvent(_message.Message):
    __slots__ = ["participant_sid", "speaking_changed"]
    PARTICIPANT_SID_FIELD_NUMBER: _ClassVar[int]
    SPEAKING_CHANGED_FIELD_NUMBER: _ClassVar[int]
    participant_sid: str
    speaking_changed: IsSpeakingChanged
    def __init__(self, participant_sid: _Optional[str] = ..., speaking_changed: _Optional[_Union[IsSpeakingChanged, _Mapping]] = ...) -> None: ...

class IsSpeakingChanged(_message.Message):
    __slots__ = ["speaking"]
    SPEAKING_FIELD_NUMBER: _ClassVar[int]
    speaking: bool
    def __init__(self, speaking: bool = ...) -> None: ...
