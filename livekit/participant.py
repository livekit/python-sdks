from ._proto import participant_pb2 as proto_participant
from .track_publication import TrackPublication


class Participant():
    def __init__(self, info: proto_participant.ParticipantInfo):
        self._info = info
        self._tracks: dict[str, TrackPublication] = {}

    @property
    def sid(self) -> str:
        return self._info.sid

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def identity(self) -> str:
        return self._info.identity

    @property
    def metadata(self) -> str:
        return self._info.metadata


class LocalParticipant(Participant):
    def __init__(self, info: proto_participant.ParticipantInfo):
        super().__init__(info)


class RemoteParticipant(Participant):
    def __init__(self, info: proto_participant.ParticipantInfo):
        super().__init__(info)
