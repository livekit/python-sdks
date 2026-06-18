"""Unit tests for Track-driven FrameProcessor metadata propagation.

These tests drive the **real** `rtc.Track`, `rtc.Room`, `rtc.RemoteParticipant`,
and `rtc.RemoteTrackPublication` objects — constructed via `__new__` injection
to bypass FFI — against a `_RecordingProcessor` test double. They cover the
contract that an attached FrameProcessor receives:
  - `_on_stream_info_updated` / `_on_credentials_updated` on every room transition
    or token refresh,
  - `_on_stream_info_cleared` / `_on_credentials_cleared` when the track leaves a room,
and that `AudioStream.aclose()` honors `auto_close_noise_cancellation`.
"""

from __future__ import annotations

import asyncio
import weakref
from types import SimpleNamespace
from typing import Any, Optional, cast

import pytest

from livekit import rtc
from livekit.rtc._ffi_client import FfiClient
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._proto import participant_pb2 as proto_participant
from livekit.rtc._proto import room_pb2 as proto_room
from livekit.rtc._proto import track_pb2 as proto_track
from livekit.rtc._utils import BroadcastQueue
from livekit.rtc.event_emitter import EventEmitter


# -- real-object helpers ------------------------------------------------------


def _make_room(name: str = "room-x", token: str = "tok-x", url: str = "wss://x") -> rtc.Room:
    """Build a real `rtc.Room` via __new__, injecting just the fields Track reads."""
    room = rtc.Room.__new__(rtc.Room)
    EventEmitter.__init__(room)
    room._info = proto_room.RoomInfo(name=name)
    room._token = token
    room._server_url = url
    room._remote_participants = {}
    room._local_participant = None
    room._ffi_handle = None  # `Room.__del__` reads this on GC
    return room


def _make_remote_participant(identity: str) -> rtc.RemoteParticipant:
    p = rtc.RemoteParticipant.__new__(rtc.RemoteParticipant)
    p._info = proto_participant.ParticipantInfo(identity=identity)
    p._track_publications = {}
    return p


def _make_remote_publication(sid: str) -> rtc.RemoteTrackPublication:
    pub = rtc.RemoteTrackPublication.__new__(rtc.RemoteTrackPublication)
    pub._info = proto_track.TrackPublicationInfo(sid=sid)
    return pub


def _make_local_participant(identity: str) -> rtc.LocalParticipant:
    p = rtc.LocalParticipant.__new__(rtc.LocalParticipant)
    p._info = proto_participant.ParticipantInfo(identity=identity)
    p._track_publications = {}
    return p


def _make_local_publication(sid: str) -> rtc.LocalTrackPublication:
    pub = rtc.LocalTrackPublication.__new__(rtc.LocalTrackPublication)
    pub._info = proto_track.TrackPublicationInfo(sid=sid)
    pub._track = None
    return pub


def _make_track(sid: str = "TR_x") -> rtc.Track:
    track = rtc.Track.__new__(rtc.Track)
    track._info = proto_track.TrackInfo(sid=sid)
    track._ffi_handle = cast(Any, None)
    track._room_ref = None
    track._audio_streams = weakref.WeakSet()
    return track


def _attach_publication(room: rtc.Room, *, identity: str, track_sid: str, pub_sid: str) -> None:
    participant = _make_remote_participant(identity=identity)
    participant._track_publications[track_sid] = _make_remote_publication(sid=pub_sid)
    room._remote_participants[identity] = participant


def _make_stream(
    *,
    track: Optional[rtc.Track] = None,
    processor: Optional[rtc.FrameProcessor[rtc.AudioFrame]] = None,
) -> rtc.AudioStream:
    """Build an AudioStream without going through the FFI-touching __init__."""
    stream = rtc.AudioStream.__new__(rtc.AudioStream)
    stream._track = track
    stream._processor = processor
    stream._audio_filter_module = None
    stream._audio_filter_options = None

    if track is not None:
        track._register_audio_stream(stream)
    return stream


def _make_closeable_stream(
    *,
    track: Optional[rtc.Track] = None,
    processor: Optional[rtc.FrameProcessor[rtc.AudioFrame]] = None,
    auto_close: bool = True,
) -> rtc.AudioStream:
    """Extends _make_stream with the minimal state `aclose()` touches."""
    stream = _make_stream(track=track, processor=processor)
    stream._processor_auto_close = auto_close
    stream._task = asyncio.ensure_future(asyncio.sleep(0))
    stream._ffi_handle = cast(Any, SimpleNamespace(dispose=lambda: None))
    return stream


class _RecordingProcessor(rtc.FrameProcessor[rtc.AudioFrame]):
    def __init__(self) -> None:
        self._enabled = True
        self.stream_info_calls: list[dict[str, str]] = []
        self.credentials_calls: list[dict[str, str]] = []
        self.stream_info_cleared_calls: int = 0
        self.credentials_cleared_calls: int = 0
        self.close_calls = 0

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    def _on_stream_info_updated(
        self, *, room_name: str, participant_identity: str, publication_sid: str
    ) -> None:
        self.stream_info_calls.append(
            {
                "room_name": room_name,
                "participant_identity": participant_identity,
                "publication_sid": publication_sid,
            }
        )

    def _on_stream_info_cleared(self) -> None:
        self.stream_info_cleared_calls += 1

    def _on_credentials_updated(self, *, token: str, url: str) -> None:
        self.credentials_calls.append({"token": token, "url": url})

    def _on_credentials_cleared(self) -> None:
        self.credentials_cleared_calls += 1

    def _process(self, frame: rtc.AudioFrame) -> rtc.AudioFrame:
        return frame

    def _close(self) -> None:
        self.close_calls += 1


def test_processor_receives_lifecycle_callbacks_on_room_attach() -> None:
    room = _make_room(name="room-1", token="tok-1", url="wss://room-1")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room)
    processor = _RecordingProcessor()

    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    assert len(processor.stream_info_calls) == 1
    assert processor.stream_info_calls[0] == {
        "room_name": "room-1",
        "participant_identity": "alice",
        "publication_sid": "PUB_1",
    }
    assert len(processor.credentials_calls) == 1
    assert processor.credentials_calls[0] == {"token": "tok-1", "url": "wss://room-1"}


def test_processor_callbacks_refire_on_track_room_change() -> None:
    room_a = _make_room(name="room-a", token="tok-a", url="wss://a")
    _attach_publication(room_a, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room_a)
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    assert len(processor.stream_info_calls) == 1
    assert len(processor.credentials_calls) == 1

    room_b = _make_room(name="room-b", token="tok-b", url="wss://b")
    _attach_publication(room_b, identity="bob", track_sid="TR_1", pub_sid="PUB_2")
    track._set_room(room_b)

    assert len(processor.stream_info_calls) == 2
    assert processor.stream_info_calls[-1] == {
        "room_name": "room-b",
        "participant_identity": "bob",
        "publication_sid": "PUB_2",
    }
    assert len(processor.credentials_calls) == 2
    assert processor.credentials_calls[-1] == {"token": "tok-b", "url": "wss://b"}


def test_token_refresh_propagates_to_processor() -> None:
    room = _make_room(name="room-1", token="tok-initial", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room)
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    baseline_creds = len(processor.credentials_calls)
    baseline_info = len(processor.stream_info_calls)

    room._token = "tok-rotated"
    room.emit("token_refreshed")

    assert len(processor.credentials_calls) == baseline_creds + 1
    assert processor.credentials_calls[-1] == {"token": "tok-rotated", "url": "wss://r"}
    assert len(processor.stream_info_calls) == baseline_info


def test_repeated_set_room_with_same_room_does_not_double_register_listener() -> None:
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room)
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    track._set_room(room)  # idempotent set with the same room

    baseline = len(processor.credentials_calls)
    room._token = "tok-rotated"
    room.emit("token_refreshed")

    assert len(processor.credentials_calls) == baseline + 1


def test_set_room_swaps_listener_to_new_room() -> None:
    room_a = _make_room(name="a", token="ta", url="wss://a")
    _attach_publication(room_a, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    room_b = _make_room(name="b", token="tb", url="wss://b")
    _attach_publication(room_b, identity="bob", track_sid="TR_1", pub_sid="PUB_2")

    track = _make_track(sid="TR_1")
    track._set_room(room_a)
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    track._set_room(room_b)

    creds_before_a_emit = len(processor.credentials_calls)
    room_a._token = "ta-rotated"
    room_a.emit("token_refreshed")
    assert len(processor.credentials_calls) == creds_before_a_emit, (
        "token_refreshed on the old room must not reach the processor"
    )

    room_b._token = "tb-rotated"
    room_b.emit("token_refreshed")
    assert len(processor.credentials_calls) == creds_before_a_emit + 1
    assert processor.credentials_calls[-1] == {"token": "tb-rotated", "url": "wss://b"}


def test_unregister_audio_stream_stops_metadata_pushes() -> None:
    """After a stream is unregistered from the track, subsequent room events
    (e.g. token_refreshed) must not reach the stream's processor."""
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room)
    processor = _RecordingProcessor()
    stream = _make_stream(track=track, processor=processor)

    track._unregister_audio_stream(stream)

    baseline = len(processor.credentials_calls)
    room._token = "tok-rotated"
    room.emit("token_refreshed")

    assert len(processor.credentials_calls) == baseline, (
        "unregistered stream's processor must not receive credentials on token_refreshed"
    )


def test_track_leaving_room_clears_processor_metadata() -> None:
    """When a track's room transitions to None (e.g. on unsubscribe/unpublish),
    the processor receives `_on_*_cleared` calls."""
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room)
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    assert len(processor.stream_info_calls) == 1
    assert len(processor.credentials_calls) == 1
    assert processor.stream_info_cleared_calls == 0
    assert processor.credentials_cleared_calls == 0

    track._set_room(None)

    # _updated lists unchanged; _cleared counters bumped exactly once each
    assert len(processor.stream_info_calls) == 1
    assert len(processor.credentials_calls) == 1
    assert processor.stream_info_cleared_calls == 1
    assert processor.credentials_cleared_calls == 1


def test_fanout_to_multiple_registered_streams() -> None:
    """A Track with multiple registered AudioStreams fans metadata out to all
    of them on room attach AND on token refresh."""
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room)

    processor1 = _RecordingProcessor()
    processor2 = _RecordingProcessor()
    _s1 = _make_stream(track=track, processor=processor1)  # noqa: F841
    _s2 = _make_stream(track=track, processor=processor2)  # noqa: F841

    # both processors got the initial push on registration
    assert len(processor1.stream_info_calls) == 1
    assert len(processor1.credentials_calls) == 1
    assert len(processor2.stream_info_calls) == 1
    assert len(processor2.credentials_calls) == 1

    room._token = "tok-rotated"
    room.emit("token_refreshed")

    # token refresh fans credentials to BOTH processors; no new stream_info
    assert len(processor1.credentials_calls) == 2
    assert processor1.credentials_calls[-1] == {"token": "tok-rotated", "url": "wss://r"}
    assert len(processor2.credentials_calls) == 2
    assert processor2.credentials_calls[-1] == {"token": "tok-rotated", "url": "wss://r"}
    assert len(processor1.stream_info_calls) == 1
    assert len(processor2.stream_info_calls) == 1


def test_register_audio_stream_before_track_enters_room() -> None:
    """A stream registered against a Track that has no room yet receives no
    metadata until the Track is moved into a room."""
    track = _make_track(sid="TR_1")  # track has no room
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    # nothing pushed yet — Track is roomless
    assert len(processor.stream_info_calls) == 0
    assert len(processor.credentials_calls) == 0

    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track._set_room(room)

    # now the stream's processor sees the metadata
    assert len(processor.stream_info_calls) == 1
    assert processor.stream_info_calls[0] == {
        "room_name": "room-1",
        "participant_identity": "alice",
        "publication_sid": "PUB_1",
    }
    assert len(processor.credentials_calls) == 1
    assert processor.credentials_calls[0] == {"token": "tok-1", "url": "wss://r"}


def test_track_room_cycle_attach_detach_reattach() -> None:
    """Track enters room A → leaves to None → enters room B. Processor sees
    real(A), cleared, real(B); listener fully migrates each time."""
    room_a = _make_room(name="a", token="ta", url="wss://a")
    _attach_publication(room_a, identity="alice", track_sid="TR_1", pub_sid="PUB_A")
    room_b = _make_room(name="b", token="tb", url="wss://b")
    _attach_publication(room_b, identity="bob", track_sid="TR_1", pub_sid="PUB_B")

    track = _make_track(sid="TR_1")
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    track._set_room(room_a)
    track._set_room(None)
    track._set_room(room_b)

    # two real updates (A then B) interleaved with one clear pass
    assert len(processor.stream_info_calls) == 2
    assert processor.stream_info_calls[0]["room_name"] == "a"
    assert processor.stream_info_calls[0]["publication_sid"] == "PUB_A"
    assert processor.stream_info_calls[1]["room_name"] == "b"
    assert processor.stream_info_calls[1]["publication_sid"] == "PUB_B"

    assert len(processor.credentials_calls) == 2
    assert processor.credentials_calls[0] == {"token": "ta", "url": "wss://a"}
    assert processor.credentials_calls[1] == {"token": "tb", "url": "wss://b"}

    assert processor.stream_info_cleared_calls == 1
    assert processor.credentials_cleared_calls == 1

    # listener fully detached from room_a; only room_b reaches the processor now
    creds_after_cycle = len(processor.credentials_calls)
    room_a._token = "ta-rotated"
    room_a.emit("token_refreshed")
    assert len(processor.credentials_calls) == creds_after_cycle, (
        "token_refreshed on the abandoned room must not reach the processor"
    )

    room_b._token = "tb-rotated"
    room_b.emit("token_refreshed")
    assert len(processor.credentials_calls) == creds_after_cycle + 1
    assert processor.credentials_calls[-1] == {"token": "tb-rotated", "url": "wss://b"}


def test_set_room_with_no_registered_streams_is_safe() -> None:
    """Setting a room (or clearing it) on a Track with no registered streams
    must be a safe no-op. Subsequent stream registration still picks up the
    current room's metadata."""
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")

    track = _make_track(sid="TR_1")
    track._set_room(room)  # no streams yet — must not raise
    track._set_room(None)  # detach — must not raise
    track._set_room(room)  # re-attach — still safe

    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    assert len(processor.stream_info_calls) == 1
    assert processor.stream_info_calls[0]["room_name"] == "room-1"
    assert len(processor.credentials_calls) == 1


def test_unregister_one_of_many_streams_only_fans_out_to_remaining() -> None:
    """When one of many streams is unregistered, subsequent token_refresh
    reaches only the remaining streams' processors."""
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room)

    processor1 = _RecordingProcessor()
    processor2 = _RecordingProcessor()
    stream1 = _make_stream(track=track, processor=processor1)
    _stream2 = _make_stream(track=track, processor=processor2)  # noqa: F841

    track._unregister_audio_stream(stream1)

    p1_creds_before = len(processor1.credentials_calls)
    p2_creds_before = len(processor2.credentials_calls)

    room._token = "tok-rotated"
    room.emit("token_refreshed")

    assert len(processor1.credentials_calls) == p1_creds_before, (
        "unregistered stream's processor must not receive the refreshed credentials"
    )
    assert len(processor2.credentials_calls) == p2_creds_before + 1
    assert processor2.credentials_calls[-1] == {"token": "tok-rotated", "url": "wss://r"}


@pytest.mark.asyncio
async def test_aclose_closes_processor_when_auto_close_true() -> None:
    """`aclose()` calls `_close()` on the attached FrameProcessor when
    `auto_close_noise_cancellation` is True (the default)."""
    processor = _RecordingProcessor()
    stream = _make_closeable_stream(processor=processor, auto_close=True)

    await stream.aclose()

    assert processor.close_calls == 1


@pytest.mark.asyncio
async def test_aclose_leaves_processor_open_when_auto_close_false() -> None:
    """`aclose()` does NOT call `_close()` when `auto_close_noise_cancellation`
    is False — the agents SDK path for sharing one processor across many track
    attach/detach cycles."""
    processor = _RecordingProcessor()
    stream = _make_closeable_stream(processor=processor, auto_close=False)

    await stream.aclose()

    assert processor.close_calls == 0


# -- local_track_republished regression ---------------------------------------


def test_local_track_republished_updates_track_sid_and_repushes_metadata() -> None:
    """A full-reconnect republish re-issues the publication SID. The handler must
    keep the local-track invariant (track.sid == publication.sid) intact and
    re-push metadata so attached processors learn the new SID — otherwise the
    SID-based lookup in Track._push_processor_metadata_to_stream fails and the
    processor receives empty participant_identity / publication_sid.
    """
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    local = _make_local_participant("agent")
    room._local_participant = local

    # Local track published under the OLD sid (mirrors publish_track:
    # track.sid == publication.sid).
    track = _make_track(sid="OLD")
    publication = _make_local_publication(sid="OLD")
    publication._track = track
    local._track_publications["OLD"] = publication
    track._set_room(room)

    # Processor attached before the reconnect sees the OLD sid.
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841
    assert processor.stream_info_calls[-1] == {
        "room_name": "room-1",
        "participant_identity": "agent",
        "publication_sid": "OLD",
    }

    # Dispatch a synthetic local_track_republished re-issuing the sid as NEW.
    event = proto_room.RoomEvent(
        local_track_republished=proto_room.LocalTrackRepublished(
            previous_sid="OLD",
            info=proto_track.TrackPublicationInfo(sid="NEW"),
        )
    )
    room._on_room_event(event)

    # Invariant restored + dict rekeyed.
    assert track.sid == "NEW"
    assert "NEW" in local._track_publications
    assert "OLD" not in local._track_publications

    # Existing attached processor was re-pushed with the NEW sid (non-empty).
    assert processor.stream_info_calls[-1] == {
        "room_name": "room-1",
        "participant_identity": "agent",
        "publication_sid": "NEW",
    }

    # Regression guard: a stream created AFTER republish also resolves NEW
    # (the exact path from the bug report — stale track.sid would yield "").
    processor2 = _RecordingProcessor()
    _stream2 = _make_stream(track=track, processor=processor2)  # noqa: F841
    assert processor2.stream_info_calls[-1] == {
        "room_name": "room-1",
        "participant_identity": "agent",
        "publication_sid": "NEW",
    }


# -- unpublish_track / room-event race ----------------------------------------


@pytest.mark.asyncio
async def test_unpublish_track_clears_processor_when_it_wins_the_event_race(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`LocalParticipant.unpublish_track` races the `local_track_unpublished`
    room event. When unpublish wins, the room-event handler later finds the
    publication already gone and skips its `_set_room(None)`. The unpublish path
    must therefore clear the processor itself, otherwise an attached
    FrameProcessor never receives the cleared callbacks (and the token_refreshed
    listener leaks). This drives unpublish_track with a mocked FFI round-trip and
    asserts the clearing happened without any room event firing.
    """
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    local = _make_local_participant("agent")
    local._ffi_handle = cast(Any, SimpleNamespace(handle=1))
    local._room_queue = BroadcastQueue()
    room._local_participant = local

    track = _make_track(sid="OLD")
    publication = _make_local_publication(sid="OLD")
    publication._track = track
    local._track_publications["OLD"] = publication
    track._set_room(room)

    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841
    cleared_info_before = processor.stream_info_cleared_calls
    cleared_creds_before = processor.credentials_cleared_calls

    # unpublish_track subscribes to _room_queue BEFORE calling request(), so a
    # mocked request that broadcasts the matching callback makes wait_for resolve
    # deterministically. The local_track_unpublished room event is never emitted
    # here — this simulates unpublish_track winning the race.
    resp = proto_ffi.FfiResponse()
    resp.unpublish_track.async_id = 1
    cb = proto_ffi.FfiEvent()
    cb.unpublish_track.async_id = 1

    def fake_request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        local._room_queue.put_nowait(cb)
        return resp

    monkeypatch.setattr(FfiClient.instance, "request", fake_request)

    await local.unpublish_track("OLD")

    assert "OLD" not in local._track_publications
    assert publication.track is None
    # the unpublish path cleared the processor's room context even though the
    # room-event handler never ran
    assert processor.stream_info_cleared_calls == cleared_info_before + 1
    assert processor.credentials_cleared_calls == cleared_creds_before + 1


def test_set_room_none_is_idempotent_for_cleared_callbacks() -> None:
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    _attach_publication(room, identity="alice", track_sid="TR_1", pub_sid="PUB_1")
    track = _make_track(sid="TR_1")
    track._set_room(room)
    processor = _RecordingProcessor()
    _stream = _make_stream(track=track, processor=processor)  # noqa: F841

    track._set_room(None)  # first clear (e.g. room event handler)
    track._set_room(None)  # second clear (e.g. unpublish_track on the same track)

    assert processor.stream_info_cleared_calls == 1
    assert processor.credentials_cleared_calls == 1


def test_local_track_unpublished_event_nulls_publication_track() -> None:
    """The `local_track_unpublished` room handler nulls
    `unpublished._track` (mirroring `track_unsubscribed`) after clearing the
    track's room. If only the room event fires (server-side removal with no
    explicit `unpublish_track` call), the publication must not retain a stale
    reference to the track.
    """
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    local = _make_local_participant("agent")
    room._local_participant = local

    track = _make_track(sid="TR_1")
    publication = _make_local_publication(sid="TR_1")
    publication._track = track
    local._track_publications["TR_1"] = publication
    track._set_room(room)

    room._on_room_event(
        proto_room.RoomEvent(
            local_track_unpublished=proto_room.LocalTrackUnpublished(publication_sid="TR_1"),
        )
    )

    assert "TR_1" not in local._track_publications
    assert publication.track is None


def test_token_refresh_listener_only_removed_by_set_room_none() -> None:
    """The `token_refreshed` listener a Track registers on its
    Room is only ever removed by `_set_room(None)`. `Room.disconnect()` does not
    walk tracks to clear them, so the listener (and the Room's strong reference to
    the Track's bound method) lingers until the Room itself is collected. This
    pins the listener lifecycle the leak stems from.
    """
    room = _make_room(name="room-1", token="tok-1", url="wss://r")
    track = _make_track(sid="TR_1")

    def _token_listeners(r: rtc.Room) -> int:
        return len(r._events.get("token_refreshed", set()))

    track._set_room(room)
    assert _token_listeners(room) == 1

    # Only _set_room(None) detaches it. Nothing in disconnect() does this today.
    track._set_room(None)
    assert _token_listeners(room) == 0
