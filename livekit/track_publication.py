from livekit._proto import track_pb2 as proto_track
from ._proto import track_pb2 as proto_track
from .track import Track


class TrackPublication():
    def __init__(self, info: proto_track.TrackPublicationInfo):
        self._info = info
        self.track: Track = None

    @property
    def sid(self) -> str:
        return self._info.sid

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def kind(self) -> proto_track.TrackKind:
        return self._info.kind

    @property
    def source(self) -> proto_track.TrackSource:
        return self._info.source

    @property
    def simulcasted(self) -> bool:
        return self._info.simulcasted

    @property
    def width(self) -> int:
        return self._info.width

    @property
    def height(self) -> int:
        return self._info.height

    @property
    def mime_type(self) -> str:
        return self._info.mime_type

    @property
    def muted(self) -> bool:
        return self._info.muted


class LocalTrackPublication(TrackPublication):
    def __init__(self, info: proto_track.TrackPublicationInfo):
        super().__init__(info)


class RemoteTrackPublication(TrackPublication):
    def __init__(self, info: proto_track.TrackPublicationInfo):
        super().__init__(info)
