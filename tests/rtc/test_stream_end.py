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

"""Audio and video stream iteration at end of stream, without a native FFI."""

from __future__ import annotations

import asyncio
import gc
from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from livekit import rtc
from livekit.rtc import audio_stream, video_stream
from livekit.rtc._ffi_client import FfiClient, FfiQueue
from livekit.rtc._proto import ffi_pb2 as proto_ffi

STREAM_HANDLE = 7


@pytest.fixture(autouse=True)
def fake_ffi(monkeypatch: pytest.MonkeyPatch) -> Iterator[MagicMock]:
    ffi = MagicMock()
    ffi.queue = FfiQueue[proto_ffi.FfiEvent]()
    monkeypatch.setattr(FfiClient, "_instance", ffi)
    yield ffi
    # stream finalizers unsubscribe from the FFI queue, so run them while it is faked
    gc.collect()


def _ffi_handle(handle: int) -> SimpleNamespace:
    return SimpleNamespace(handle=handle, disposed=False, dispose=lambda: None)


def _track() -> MagicMock:
    track = MagicMock()
    track._ffi_handle.handle = 1
    return track


def _response(kind: str) -> proto_ffi.FfiResponse:
    response = proto_ffi.FfiResponse()
    getattr(response, kind).stream.handle.id = STREAM_HANDLE
    return response


def _audio_frame_event() -> proto_ffi.FfiEvent:
    event = proto_ffi.FfiEvent()
    event.audio_stream_event.stream_handle = STREAM_HANDLE
    event.audio_stream_event.frame_received.frame.handle.id = 1
    return event


def _audio_eos_event() -> proto_ffi.FfiEvent:
    event = proto_ffi.FfiEvent()
    event.audio_stream_event.stream_handle = STREAM_HANDLE
    event.audio_stream_event.eos.SetInParent()
    return event


def _video_frame_event() -> proto_ffi.FfiEvent:
    event = proto_ffi.FfiEvent()
    event.video_stream_event.stream_handle = STREAM_HANDLE
    event.video_stream_event.frame_received.buffer.handle.id = 1
    return event


def _video_eos_event() -> proto_ffi.FfiEvent:
    event = proto_ffi.FfiEvent()
    event.video_stream_event.stream_handle = STREAM_HANDLE
    event.video_stream_event.eos.SetInParent()
    return event


async def _collect(stream: rtc.AudioStream | rtc.VideoStream) -> list:
    async def read() -> list:
        return [event async for event in stream]

    return await asyncio.wait_for(read(), timeout=2)


async def test_audio_stream_delivers_frames_queued_before_eos() -> None:
    with (
        patch.object(FfiClient.instance, "request", return_value=_response("new_audio_stream")),
        patch.object(audio_stream, "FfiHandle", side_effect=_ffi_handle),
        patch.object(audio_stream.AudioFrame, "_from_owned_info", side_effect=lambda _: object()),
    ):
        stream = rtc.AudioStream(_track())
        for event in (_audio_frame_event(), _audio_frame_event(), _audio_eos_event()):
            FfiClient.instance.queue.put(event)
        # let the stream's task consume every event before the reader starts
        await asyncio.wait_for(stream._task, timeout=2)

        assert len(await _collect(stream)) == 2


async def test_video_stream_delivers_frames_queued_before_eos() -> None:
    with (
        patch.object(FfiClient.instance, "request", return_value=_response("new_video_stream")),
        patch.object(video_stream, "FfiHandle", side_effect=_ffi_handle),
        patch.object(video_stream.VideoFrame, "_from_owned_info", side_effect=lambda _: object()),
    ):
        stream = rtc.VideoStream(_track())
        for event in (_video_frame_event(), _video_frame_event(), _video_eos_event()):
            FfiClient.instance.queue.put(event)
        await asyncio.wait_for(stream._task, timeout=2)

        assert len(await _collect(stream)) == 2


async def test_video_stream_ends_when_eos_arrives_during_read() -> None:
    with (
        patch.object(FfiClient.instance, "request", return_value=_response("new_video_stream")),
        patch.object(video_stream, "FfiHandle", side_effect=_ffi_handle),
    ):
        stream = rtc.VideoStream(_track())
        reader = asyncio.ensure_future(_collect(stream))
        await asyncio.sleep(0.05)  # the reader is now waiting for a frame
        FfiClient.instance.queue.put(_video_eos_event())

        assert await asyncio.wait_for(reader, timeout=2) == []


async def test_audio_stream_keeps_last_frame_when_bounded_queue_is_full_at_eos() -> None:
    with (
        patch.object(FfiClient.instance, "request", return_value=_response("new_audio_stream")),
        patch.object(audio_stream, "FfiHandle", side_effect=_ffi_handle),
        patch.object(audio_stream.AudioFrame, "_from_owned_info", side_effect=lambda _: object()),
    ):
        stream = rtc.AudioStream(_track(), capacity=1)
        for event in (_audio_frame_event(), _audio_eos_event()):
            FfiClient.instance.queue.put(event)
        await asyncio.wait_for(stream._task, timeout=2)

        assert len(await _collect(stream)) == 1


async def test_video_stream_keeps_last_frame_when_bounded_queue_is_full_at_eos() -> None:
    with (
        patch.object(FfiClient.instance, "request", return_value=_response("new_video_stream")),
        patch.object(video_stream, "FfiHandle", side_effect=_ffi_handle),
        patch.object(video_stream.VideoFrame, "_from_owned_info", side_effect=lambda _: object()),
    ):
        stream = rtc.VideoStream(_track(), capacity=1)
        for event in (_video_frame_event(), _video_eos_event()):
            FfiClient.instance.queue.put(event)
        await asyncio.wait_for(stream._task, timeout=2)

        assert len(await _collect(stream)) == 1
