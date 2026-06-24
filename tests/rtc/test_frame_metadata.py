from __future__ import annotations

import weakref
from types import SimpleNamespace
from typing import cast

import pytest

from livekit import rtc
from livekit.rtc import video_source as video_source_module
from livekit.rtc._ffi_client import FfiHandle
from livekit.rtc._proto import e2ee_pb2 as proto_e2ee
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._proto import handle_pb2 as proto_handle
from livekit.rtc._proto import participant_pb2 as proto_participant
from livekit.rtc._proto import room_pb2 as proto_room
from livekit.rtc._proto import track_pb2 as proto_track
from livekit.rtc.participant import LocalParticipant
from livekit.rtc.track import Track


def _publication_info(
    sid: str,
    *,
    frame_metadata_features: list[proto_track.FrameMetadataFeature.ValueType] | None = None,
) -> proto_track.TrackPublicationInfo:
    return proto_track.TrackPublicationInfo(
        sid=sid,
        name="camera",
        kind=proto_track.KIND_VIDEO,
        source=proto_track.SOURCE_CAMERA,
        simulcasted=False,
        width=640,
        height=360,
        mime_type="video/VP8",
        muted=False,
        remote=False,
        encryption_type=proto_e2ee.NONE,
        frame_metadata_features=frame_metadata_features or [],
    )


def _owned_publication(
    sid: str,
    *,
    frame_metadata_features: list[proto_track.FrameMetadataFeature.ValueType] | None = None,
) -> proto_track.OwnedTrackPublication:
    return proto_track.OwnedTrackPublication(
        handle=proto_handle.FfiOwnedHandle(id=0),
        info=_publication_info(sid, frame_metadata_features=frame_metadata_features),
    )


def test_frame_metadata_symbols_are_exported() -> None:
    metadata = rtc.FrameMetadata(user_timestamp=123, frame_id=7)

    assert rtc.FrameMetadataFeature.FMF_USER_TIMESTAMP == proto_track.FMF_USER_TIMESTAMP
    assert rtc.FrameMetadataFeature.FMF_FRAME_ID == proto_track.FMF_FRAME_ID
    assert metadata.HasField("user_timestamp")
    assert metadata.HasField("frame_id")


@pytest.mark.asyncio
async def test_track_publication_exposes_frame_metadata_features() -> None:
    publication = rtc.LocalTrackPublication(
        _owned_publication(
            "TR_OLD",
            frame_metadata_features=[
                proto_track.FMF_USER_TIMESTAMP,
                proto_track.FMF_FRAME_ID,
            ],
        )
    )

    assert publication.frame_metadata_features == [
        proto_track.FMF_USER_TIMESTAMP,
        proto_track.FMF_FRAME_ID,
    ]


def test_packet_trailer_names_remain_as_deprecated_aliases() -> None:
    # The old "Packet Trailer" names are kept as backwards-compatible aliases.
    # The type name forwards to FrameMetadataFeature (incl. the new FMF_* values)...
    assert rtc.PacketTrailerFeature.FMF_USER_TIMESTAMP == rtc.FrameMetadataFeature.FMF_USER_TIMESTAMP

    # ...and the old PTF_* value names still resolve, with a DeprecationWarning.
    with pytest.deprecated_call():
        assert rtc.PacketTrailerFeature.PTF_USER_TIMESTAMP == rtc.FrameMetadataFeature.FMF_USER_TIMESTAMP
    with pytest.deprecated_call():
        assert rtc.PacketTrailerFeature.PTF_FRAME_ID == rtc.FrameMetadataFeature.FMF_FRAME_ID


@pytest.mark.asyncio
async def test_packet_trailer_features_property_is_deprecated_alias() -> None:
    publication = rtc.LocalTrackPublication(
        _owned_publication(
            "TR_OLD",
            frame_metadata_features=[proto_track.FMF_USER_TIMESTAMP],
        )
    )

    with pytest.deprecated_call():
        assert publication.packet_trailer_features == publication.frame_metadata_features


def test_video_source_capture_frame_copies_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_requests: list[proto_ffi.FfiRequest] = []

    class FakeClient:
        def request(self, req: proto_ffi.FfiRequest) -> None:
            captured_requests.append(req)

    class FakeFfiClient:
        instance = FakeClient()

    monkeypatch.setattr(video_source_module, "FfiClient", FakeFfiClient)

    source = video_source_module.VideoSource.__new__(video_source_module.VideoSource)
    source._ffi_handle = cast(FfiHandle, SimpleNamespace(handle=42))
    frame = rtc.VideoFrame(
        width=1,
        height=1,
        type=rtc.VideoBufferType.RGBA,
        data=bytes([0, 0, 0, 255]),
    )

    source.capture_frame(
        frame,
        timestamp_us=99,
        rotation=rtc.VideoRotation.VIDEO_ROTATION_90,
        metadata=rtc.FrameMetadata(user_timestamp=123, frame_id=7),
    )

    request = captured_requests[0]
    assert request.capture_video_frame.source_handle == 42
    assert request.capture_video_frame.timestamp_us == 99
    assert request.capture_video_frame.rotation == rtc.VideoRotation.VIDEO_ROTATION_90
    assert request.capture_video_frame.HasField("metadata")
    assert request.capture_video_frame.metadata.user_timestamp == 123
    assert request.capture_video_frame.metadata.frame_id == 7


@pytest.mark.asyncio
async def test_local_track_republished_updates_existing_publication() -> None:
    room = rtc.Room()
    local_participant = LocalParticipant(
        room._room_queue,
        proto_participant.OwnedParticipant(
            handle=proto_handle.FfiOwnedHandle(id=0),
            info=proto_participant.ParticipantInfo(
                sid="PA_LOCAL",
                identity="publisher",
                name="publisher",
                state=proto_participant.PARTICIPANT_STATE_ACTIVE,
                metadata="",
                kind=proto_participant.PARTICIPANT_KIND_STANDARD,
                disconnect_reason=proto_participant.UNKNOWN_REASON,
                joined_at=0,
                permission=proto_participant.ParticipantPermission(),
            ),
        ),
    )
    room._local_participant = local_participant

    publication = rtc.LocalTrackPublication(
        _owned_publication(
            "TR_OLD",
            frame_metadata_features=[proto_track.FMF_USER_TIMESTAMP],
        )
    )
    # Build a real Track via __new__ (bypassing FFI) so the republish handler's
    # track.sid invariant update and _set_room(...) re-push both work.
    track = Track.__new__(Track)
    track._info = proto_track.TrackInfo(sid="TR_OLD")
    track._ffi_handle = cast(FfiHandle, None)
    track._room_ref = None
    track._audio_streams = weakref.WeakSet()
    publication._track = track
    local_participant._track_publications[publication.sid] = publication

    room._on_room_event(
        proto_room.RoomEvent(
            room_handle=0,
            local_track_republished=proto_room.LocalTrackRepublished(
                publication_handle=0,
                previous_sid="TR_OLD",
                info=_publication_info(
                    "TR_NEW",
                    frame_metadata_features=[
                        proto_track.FMF_USER_TIMESTAMP,
                        proto_track.FMF_FRAME_ID,
                    ],
                ),
            ),
        )
    )

    assert "TR_OLD" not in local_participant.track_publications
    assert local_participant.track_publications["TR_NEW"] is publication
    assert publication.sid == "TR_NEW"
    assert publication.frame_metadata_features == [
        proto_track.FMF_USER_TIMESTAMP,
        proto_track.FMF_FRAME_ID,
    ]
