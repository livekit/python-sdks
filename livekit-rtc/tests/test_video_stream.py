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

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

from livekit import rtc
from livekit.rtc._ffi_client import FfiClient
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._proto import video_frame_pb2 as proto_video_frame


def test_video_stream_del_without_ffi_queue() -> None:
    # A partially constructed VideoStream collected during error in __init__
    # must not raise AttributeError when __del__ is called.
    stream = rtc.VideoStream.__new__(rtc.VideoStream)
    stream.__del__()


async def test_video_stream_eos_terminates_iteration() -> None:
    track = MagicMock(spec=rtc.Track)
    stream_info = MagicMock()
    stream_info.handle.id = 12345
    stream_info.info = MagicMock()

    with patch.object(rtc.VideoStream, "_create_owned_stream", return_value=stream_info):
        video_stream = rtc.VideoStream(track)
        # Mark mock handle disposed so GC does not attempt to drop non-existent handle
        video_stream._ffi_handle._disposed = True

        async def consume() -> list[rtc.VideoFrameEvent]:
            frames: list[rtc.VideoFrameEvent] = []
            async for frame in video_stream:
                frames.append(frame)
            return frames

        consume_task = asyncio.create_task(consume())

        # Send EOS event for this stream handle
        event = proto_ffi.FfiEvent()
        event.video_stream_event.stream_handle = 12345
        event.video_stream_event.eos.CopyFrom(proto_video_frame.VideoStreamEOS())
        FfiClient.instance.queue.put(event)

        # Iteration must complete cleanly without hanging
        frames = await asyncio.wait_for(consume_task, timeout=2.0)
        assert frames == []

        await video_stream.aclose()
