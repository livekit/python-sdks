# Copyright 2026 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Exercise the media streams' and AudioSource's FFI subscriptions without a native FFI."""

import asyncio
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Union
from unittest.mock import patch

import pytest

from livekit import rtc
from livekit.rtc._ffi_client import FfiClient, FfiQueue
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._proto import track_pb2 as proto_track


@pytest.fixture
def queue(monkeypatch: pytest.MonkeyPatch) -> Iterator[FfiQueue[proto_ffi.FfiEvent]]:
    queue = FfiQueue[proto_ffi.FfiEvent]()
    handles = iter(range(100, 200))

    def request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        response = proto_ffi.FfiResponse()
        which = req.WhichOneof("message")
        if which == "new_audio_stream":
            response.new_audio_stream.stream.handle.id = next(handles)
        elif which == "new_video_stream":
            response.new_video_stream.stream.handle.id = next(handles)
        elif which == "new_audio_source":
            response.new_audio_source.source.handle.id = next(handles)
        elif which == "capture_audio_frame":
            response.capture_audio_frame.async_id = 1
        else:
            raise AssertionError(f"unexpected FFI request: {which}")
        return response

    # A different PID prevents synthetic handles from being dropped natively.
    monkeypatch.setattr(
        FfiClient, "_instance", SimpleNamespace(queue=queue, request=request, _pid=-1)
    )
    yield queue
    assert not queue._subscribers


def _create_stream(event_type: str) -> Union[rtc.AudioStream, rtc.VideoStream]:
    track = rtc.Track(proto_track.OwnedTrack())
    if event_type == "audio_stream_event":
        return rtc.AudioStream(track)
    return rtc.VideoStream(track)


def _stream_event(event_type: str, stream_handle: int, *, eos: bool = False) -> proto_ffi.FfiEvent:
    event = proto_ffi.FfiEvent()
    stream_event = getattr(event, event_type)
    stream_event.stream_handle = stream_handle
    if eos:
        stream_event.eos.SetInParent()
    return event


@pytest.mark.parametrize("event_type", ["audio_stream_event", "video_stream_event"])
async def test_stream_does_not_receive_other_streams_events(
    queue: FfiQueue[proto_ffi.FfiEvent], event_type: str
) -> None:
    first = _create_stream(event_type)
    second = _create_stream(event_type)
    loop = asyncio.get_running_loop()
    event = _stream_event(event_type, second._ffi_handle.handle)

    try:
        with patch.object(
            loop, "call_soon_threadsafe", wraps=loop.call_soon_threadsafe
        ) as schedule:
            for _ in range(100):
                queue.put(event)

        # Only the stream the events belong to should incur an event-loop wakeup.
        assert schedule.call_count == 100
        assert all(call.args[0] == second._ffi_queue.put_nowait for call in schedule.call_args_list)
    finally:
        for stream in (first, second):
            queue.put(_stream_event(event_type, stream._ffi_handle.handle, eos=True))
            await asyncio.wait_for(stream.aclose(), 1)


@pytest.mark.parametrize("event_type", ["audio_stream_event", "video_stream_event"])
async def test_stream_receives_events_sent_while_it_is_created(
    queue: FfiQueue[proto_ffi.FfiEvent],
    monkeypatch: pytest.MonkeyPatch,
    event_type: str,
) -> None:
    instance = FfiClient._instance
    assert instance is not None
    create = instance.request

    def request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        response = create(req)
        which = req.WhichOneof("message")
        assert which is not None
        # the native stream can end before the request that created it returns
        handle = getattr(response, which).stream.handle.id
        queue.put(_stream_event(event_type, handle, eos=True))
        return response

    monkeypatch.setattr(instance, "request", request)
    stream = _create_stream(event_type)
    await asyncio.wait_for(stream.aclose(), 1)


async def test_capture_frame_only_receives_its_own_callback(
    queue: FfiQueue[proto_ffi.FfiEvent],
) -> None:
    source = rtc.AudioSource(48000, 1)
    capture = asyncio.create_task(source.capture_frame(rtc.AudioFrame.create(48000, 1, 480)))
    await asyncio.sleep(0)

    loop = asyncio.get_running_loop()
    room_event = proto_ffi.FfiEvent()
    room_event.room_event.SetInParent()
    other_capture = proto_ffi.FfiEvent()
    other_capture.capture_audio_frame.async_id = 2
    try:
        with patch.object(
            loop, "call_soon_threadsafe", wraps=loop.call_soon_threadsafe
        ) as schedule:
            for event in (room_event, _stream_event("audio_stream_event", 1), other_capture):
                queue.put(event)

        # Neither other events nor another capture's callback should wake the capture up.
        assert schedule.call_count == 0
    finally:
        callback = proto_ffi.FfiEvent()
        callback.capture_audio_frame.async_id = 1
        queue.put(callback)
        await asyncio.wait_for(capture, 1)
        await source.aclose()


async def test_capture_frame_receives_callback_sent_before_request_returns(
    queue: FfiQueue[proto_ffi.FfiEvent], monkeypatch: pytest.MonkeyPatch
) -> None:
    instance = FfiClient._instance
    assert instance is not None
    create = instance.request

    def request(req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
        response = create(req)
        if req.WhichOneof("message") == "capture_audio_frame":
            # the native capture can complete before the request that started it returns
            callback = proto_ffi.FfiEvent()
            callback.capture_audio_frame.async_id = response.capture_audio_frame.async_id
            queue.put(callback)
        return response

    monkeypatch.setattr(instance, "request", request)
    source = rtc.AudioSource(48000, 1)
    await asyncio.wait_for(source.capture_frame(rtc.AudioFrame.create(48000, 1, 480)), 1)
    await source.aclose()
