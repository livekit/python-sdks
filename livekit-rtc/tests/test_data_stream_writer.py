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
from unittest.mock import MagicMock

import pytest

from livekit.rtc.data_stream import TextStreamWriter
from livekit.rtc.participant import LocalParticipant


def test_stream_writer_attributes_default_is_none() -> None:
    participant = MagicMock(spec=LocalParticipant)
    participant.identity = "test-user"
    participant._open_stream_writers = {}

    writer1 = TextStreamWriter(participant, topic="t1")
    writer2 = TextStreamWriter(participant, topic="t2")

    # attributes default should be None rather than a shared mutable dict
    assert writer1._options.attributes == {}
    assert writer2._options.attributes == {}


async def test_aclose_waits_for_inflight_write() -> None:
    participant = MagicMock(spec=LocalParticipant)
    participant.identity = "test-user"
    participant._open_stream_writers = {}

    writer = TextStreamWriter(participant, topic="t")
    writer._register_open(9999)

    order: list[str] = []
    write_in_progress = asyncio.Event()
    allow_write_finish = asyncio.Event()

    async def mock_wait_for_callback(req: object, callback_field: str, response_field: str) -> None:
        if callback_field == "text_stream_writer_write":
            order.append("write_start")
            write_in_progress.set()
            await allow_write_finish.wait()
            order.append("write_done")
        elif callback_field == "text_stream_writer_close":
            order.append("close_sent")

    writer._wait_for_callback = mock_wait_for_callback  # type: ignore[assignment]

    # Start write in background
    write_task = asyncio.create_task(writer.write("chunk"))
    await write_in_progress.wait()

    # Initiate aclose while write is still in flight
    close_task = asyncio.create_task(writer.aclose())

    # Give close_task a chance to run; it must not execute close yet because write holds lock
    await asyncio.sleep(0.01)
    assert order == ["write_start"]

    # Now allow write to complete
    allow_write_finish.set()
    await write_task
    await close_task

    # Close must execute only AFTER write completes
    assert order == ["write_start", "write_done", "close_sent"]
    assert writer._closed is True

    # Subsequent write must immediately reject
    with pytest.raises(RuntimeError, match="Cannot write after stream is closed"):
        await writer.write("late_chunk")
