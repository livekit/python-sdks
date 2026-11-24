"""Connect-time publications are installed before room events are released."""

import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from livekit import rtc
from livekit.rtc._ffi_client import FfiClient, FfiHandle, FfiQueue
from livekit.rtc._proto import ffi_pb2 as ffi
from livekit.rtc._proto import track_pb2


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["success", "failure", "cancel"])
@pytest.mark.parametrize("native_preparation", [False, True])
async def test_connect_prepared_publication_state_and_cleanup(
    monkeypatch, outcome, native_preparation
):
    queue = FfiQueue[ffi.FfiEvent]()
    track = Mock(spec=rtc.LocalAudioTrack)
    track._ffi_handle = SimpleNamespace(handle=42)
    track._info = track_pb2.TrackInfo()
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    options.audio_encoding.max_bitrate = 32000
    options.dtx = False
    source = Mock(spec=rtc.AudioSource)
    source._ffi_handle = SimpleNamespace(handle=44)
    audio = rtc.AudioTrackToPublish(source=source, name="prepared", options=options)
    consumed = set()
    dispose = FfiHandle.dispose

    def observe_dispose(handle):
        if not handle.disposed:
            consumed.add(handle.handle)
        dispose(handle)

    monkeypatch.setattr(FfiHandle, "dispose", observe_dispose)
    monkeypatch.setattr(
        rtc.LocalAudioTrack,
        "create_audio_track",
        Mock(side_effect=AssertionError("native track creation must stay inside Rust connect")),
    )
    observed = []
    pending = []
    ready = asyncio.Event()
    room = rtc.Room()

    def request(req):
        response = ffi.FfiResponse()
        event = ffi.FfiEvent()
        which = req.WhichOneof("message")
        if which == "connect":
            if native_preparation:
                initial = req.connect.publish_audio_tracks[0]
                assert initial.source_handle == 44
                assert initial.name == "prepared"
                assert not req.connect.publish_tracks
            else:
                initial = req.connect.publish_tracks[0]
                assert initial.track_handle == 42
                assert not req.connect.publish_audio_tracks
            assert initial.options == options
            response.connect.async_id = event.connect.async_id = 7
            if outcome == "failure":
                event.connect.error = "publication rejected"
            else:
                result = event.connect.result
                result.room.handle.id = 1
                result.room.info.sid = "RM_prepared"
                result.local_participant.handle.id = 2
                initial = result.local_publications.add(
                    track_handle=50 if native_preparation else 42
                )
                publication = initial.publication
                publication.handle.id = 3
                publication.info.sid = "TR_prepared"
                if native_preparation:
                    initial.audio_track_index = 0
                    initial.track.handle.id = 50
                    initial.track.info.name = "prepared"
                    initial.track.info.kind = rtc.TrackKind.KIND_AUDIO
            if outcome == "cancel":
                pending.append(event)
                ready.set()
                return response
        elif which == "ready_for_room_event":
            if outcome == "cancel":
                return response
            publication = room.local_participant.track_publications["TR_prepared"]
            expected = audio.track if native_preparation else track
            assert publication.track is expected
            assert expected._info.sid == publication.sid
            published = ffi.FfiEvent()
            published.room_event.room_handle = 1
            published.room_event.local_track_published.track_sid = publication.sid
            queue.put(published)
            return response
        elif which == "disconnect":
            response.disconnect.async_id = event.disconnect.async_id = 8
            eos = ffi.FfiEvent()
            eos.room_event.room_handle = 1
            eos.room_event.eos.SetInParent()
            queue.put(eos)
        else:
            raise AssertionError(which)
        queue.put(event)
        return response

    # Synthetic handles must never reach the real native handle table.
    monkeypatch.setattr(
        FfiClient, "_instance", SimpleNamespace(queue=queue, request=request, _pid=-1)
    )
    room.on("local_track_published", lambda pub, local: observed.append((pub, local)))
    connecting = asyncio.create_task(
        room.connect(
            "wss://example.invalid",
            "test",
            rtc.RoomOptions(
                publish_tracks=[] if native_preparation else [(track, options)],
                publish_audio_tracks=[audio] if native_preparation else [],
            ),
        )
    )
    if outcome == "cancel":
        await ready.wait()
        connecting.cancel()
        queue.put(pending[0])
        with pytest.raises(asyncio.CancelledError):
            await connecting
    elif outcome == "failure":
        with pytest.raises(rtc.ConnectError, match="publication rejected"):
            await connecting
    else:
        await connecting
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        assert len(observed) == 1
        assert observed[0][1] is (audio.track if native_preparation else track)
        await room.disconnect()
        room._ffi_handle = None
    assert not room._is_connecting
    assert not queue._subscribers
    if outcome != "success":
        assert room._local_participant is None
        assert not track._info.sid
        assert audio.track is None
        if outcome == "cancel" and native_preparation:
            assert 50 in consumed
            assert 3 in consumed
    assert 44 not in consumed  # The caller still owns the source.


@pytest.mark.asyncio
async def test_duplicate_prepared_track_rejected_before_connect(monkeypatch):
    track = Mock(spec=rtc.LocalAudioTrack)
    track._ffi_handle = SimpleNamespace(handle=42)
    options = rtc.TrackPublishOptions()
    room = rtc.Room()
    with pytest.raises(ValueError, match="same track"):
        await room.connect(
            "wss://example.invalid",
            "test",
            rtc.RoomOptions(publish_tracks=[(track, options), (track, options)]),
        )
    assert not room._is_connecting


@pytest.mark.asyncio
async def test_duplicate_audio_description_rejected_before_connect():
    source = Mock(spec=rtc.AudioSource)
    audio = rtc.AudioTrackToPublish(source=source)
    room = rtc.Room()
    with pytest.raises(ValueError, match="same descriptor"):
        await room.connect(
            "wss://example.invalid",
            "test",
            rtc.RoomOptions(publish_audio_tracks=[audio, audio]),
        )
    assert not room._is_connecting
