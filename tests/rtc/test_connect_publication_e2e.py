"""Real-SFU coverage for prepared, ordinary, failed and cancelled audio publications.

Run with LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET set. LIVEKIT_LIB_PATH
must point to a native FFI build supporting ConnectRequest.publish_tracks.
"""

import asyncio
import gc
import math
import os
import uuid
import weakref
from array import array

import pytest
from livekit import api, rtc

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(not os.environ.get("LIVEKIT_URL"), reason="requires a test LiveKit server"),
]


def token(room, identity):
    return (
        api.AccessToken()
        .with_identity(identity)
        .with_grants(api.VideoGrants(room_join=True, room=room))
        .to_jwt()
    )


async def round_trip(single_pc, prepared):
    name = "prepared-audio-" + uuid.uuid4().hex[:12]
    receiver, sender = rtc.Room(), rtc.Room()
    source = rtc.AudioSource(24000, 1)
    track = rtc.LocalAudioTrack.create_audio_track("prepared", source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    subscribed = asyncio.get_running_loop().create_future()
    receiver.on("track_subscribed", lambda remote, *_: subscribed.set_result(remote))
    stream = None
    try:
        await receiver.connect(os.environ["LIVEKIT_URL"], token(name, "listener"))
        await sender.connect(
            os.environ["LIVEKIT_URL"],
            token(name, "agent"),
            rtc.RoomOptions(
                single_peer_connection=single_pc,
                publish_tracks=[(track, options)] if prepared else [],
            ),
        )
        if prepared:
            assert len(sender.local_participant.track_publications) == 1
            publication = next(iter(sender.local_participant.track_publications.values()))
            assert publication.track is track
        else:
            assert not sender.local_participant.track_publications
            publication = await sender.local_participant.publish_track(track, options)
        await asyncio.wait_for(publication.wait_for_subscription(), 10)
        remote = await asyncio.wait_for(subscribed, 10)
        stream = rtc.AudioStream(remote, sample_rate=24000, num_channels=1, capacity=8)
        pcm = array("h", [int(8000 * math.sin(2 * math.pi * 440 * i / 24000)) for i in range(480)])

        async def produce():
            for _ in range(12):
                await source.capture_frame(rtc.AudioFrame(pcm.tobytes(), 24000, 1, 480))
            await source.wait_for_playout()

        async def receive():
            async for event in stream:
                if any(abs(value) > 160 for value in event.frame.data):
                    return
            raise AssertionError("audio ended before receiving non-silent PCM")

        tasks = [
            asyncio.create_task(produce()),
            asyncio.create_task(asyncio.wait_for(receive(), 10)),
        ]
        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        assert len(sender.local_participant.track_publications) == 1
        # Caller-owned track remains usable after connect; it can be unpublished normally.
        await sender.local_participant.unpublish_track(publication.sid)
        assert not sender.local_participant.track_publications
        references = [weakref.ref(source), weakref.ref(track), weakref.ref(publication)]
    finally:
        if stream is not None:
            await stream.aclose()
        await asyncio.gather(sender.disconnect(), receiver.disconnect())
        await source.aclose()
        async with api.LiveKitAPI() as client:
            await client.room.delete_room(api.DeleteRoomRequest(room=name))
    return references


@pytest.mark.parametrize("single_pc", [False, True])
@pytest.mark.parametrize("prepared", [False, True])
async def test_audio_after_prepared_or_normal_publication(single_pc, prepared):
    for _ in range(2):
        references = await round_trip(single_pc, prepared)
        gc.collect()
        assert all(reference() is None for reference in references)


@pytest.mark.parametrize("cancel", [False, True])
async def test_failed_or_cancelled_connect_releases_prepared_track(cancel):
    source = rtc.AudioSource(24000, 1)
    track = rtc.LocalAudioTrack.create_audio_track("prepared", source)
    refs = [weakref.ref(source), weakref.ref(track)]
    room = rtc.Room()
    connect_options = rtc.RoomOptions(publish_tracks=[(track, rtc.TrackPublishOptions())])
    connecting = asyncio.create_task(
        room.connect(os.environ["LIVEKIT_URL"], "invalid-token", connect_options)
    )
    if cancel:
        await asyncio.sleep(0)
        connecting.cancel()
        with pytest.raises(asyncio.CancelledError):
            await connecting
    else:
        with pytest.raises(rtc.ConnectError):
            await connecting
    assert not room.isconnected()
    assert room._local_participant is None
    await source.aclose()
    del source, track, connecting, connect_options
    # A completed task can remain in the event loop's current callback until it yields.
    await asyncio.sleep(0)
    gc.collect()
    assert all(reference() is None for reference in refs)


async def test_cancelled_successful_connect_reclaims_publication():
    """A late successful callback must be disconnected and its owned handles released."""
    for _ in range(2):
        name = "cancel-prepared-" + uuid.uuid4().hex[:12]
        room = rtc.Room()
        source = rtc.AudioSource(24000, 1)
        track = rtc.LocalAudioTrack.create_audio_track("cancelled", source)
        refs = [weakref.ref(source), weakref.ref(track)]
        options = rtc.RoomOptions(publish_tracks=[(track, rtc.TrackPublishOptions())])
        connecting = asyncio.create_task(
            room.connect(os.environ["LIVEKIT_URL"], token(name, "agent"), options)
        )
        await asyncio.sleep(0)
        connecting.cancel()
        try:
            with pytest.raises(asyncio.CancelledError):
                await connecting
            assert not room.isconnected()
            assert room._local_participant is None
            assert not room._is_connecting
            await source.aclose()
        finally:
            async with api.LiveKitAPI() as client:
                await client.room.delete_room(api.DeleteRoomRequest(room=name))
        del source, track, connecting, options
        await asyncio.sleep(0)
        gc.collect()
        assert all(reference() is None for reference in refs)
