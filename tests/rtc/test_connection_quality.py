"""Unit tests for the local ConnectionQuality enum and the participant property."""

from livekit import rtc
from livekit.rtc._proto import participant_pb2 as proto_participant
from livekit.rtc._proto import room_pb2 as proto_room
from livekit.rtc.participant import _connection_quality_from_proto


def test_enum_values_align_with_proto() -> None:
    CQ = rtc.ConnectionQuality
    assert CQ.QUALITY_UNKNOWN == -1
    assert CQ.QUALITY_POOR == proto_room.ConnectionQuality.QUALITY_POOR
    assert CQ.QUALITY_GOOD == proto_room.ConnectionQuality.QUALITY_GOOD
    assert CQ.QUALITY_EXCELLENT == proto_room.ConnectionQuality.QUALITY_EXCELLENT
    assert CQ.QUALITY_LOST == proto_room.ConnectionQuality.QUALITY_LOST
    # backward compat: still int-comparable like the old proto enum export
    assert CQ.QUALITY_GOOD == 1


def test_from_proto_mapping() -> None:
    assert _connection_quality_from_proto(1) is rtc.ConnectionQuality.QUALITY_GOOD
    assert _connection_quality_from_proto(99) is rtc.ConnectionQuality.QUALITY_UNKNOWN


def test_participant_default_quality_is_unknown() -> None:
    owned = proto_participant.OwnedParticipant()
    owned.info.identity = "test"
    participant = rtc.RemoteParticipant(owned)
    assert participant.connection_quality is rtc.ConnectionQuality.QUALITY_UNKNOWN
