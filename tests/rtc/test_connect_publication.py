"""Connect-time publications are installed before room events are released."""

import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from livekit import rtc
from livekit.rtc._ffi_client import FfiClient, FfiQueue
from livekit.rtc._proto import ffi_pb2 as ffi
from livekit.rtc._proto import track_pb2


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["success", "failure", "cancel"])
async def test_connect_prepared_publication_state_and_cleanup(monkeypatch, outcome):
    queue = FfiQueue[ffi.FfiEvent]()
    track = Mock(spec=rtc.LocalAudioTrack)
    track._ffi_handle = SimpleNamespace(handle=42)
    track._info = track_pb2.TrackInfo()
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    options.audio_encoding.max_bitrate = 32000
    options.dtx = False
    observed = []
    pending = []
    ready = asyncio.Event()
    room = rtc.Room()

    def request(req):
        response = ffi.FfiResponse()
        event = ffi.FfiEvent()
        which = req.WhichOneof("message")
        if which == "connect":
            initial = req.connect.publish_tracks[0]
            assert initial.track_handle == 42
            assert initial.options == options
            response.connect.async_id = event.connect.async_id = 7
            if outcome == "failure":
                event.connect.error = "publication rejected"
            else:
                result = event.connect.result
                result.room.handle.id = 1
                result.room.info.sid = "RM_prepared"
                result.local_participant.handle.id = 2
                publication = result.local_publications.add(track_handle=42).publication
                publication.handle.id = 3
                publication.info.sid = "TR_prepared"
            if outcome == "cancel":
                pending.append(event)
                ready.set()
                return response
        elif which == "ready_for_room_event":
            if outcome == "cancel":
                return response
            publication = room.local_participant.track_publications["TR_prepared"]
            assert publication.track is track
            assert track._info.sid == publication.sid
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
            "wss://example.invalid", "test", rtc.RoomOptions(publish_tracks=[(track, options)])
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
        assert observed[0][1] is track
        await room.disconnect()
        room._ffi_handle = None
    assert not room._is_connecting
    assert not queue._subscribers
    if outcome != "success":
        assert room._local_participant is None
        assert not track._info.sid


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
