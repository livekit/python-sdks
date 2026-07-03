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

"""Regression tests for AudioStream.__init__ error handling."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from livekit import rtc


async def test_failed_stream_creation_does_not_orphan_run_task() -> None:
    """If owned-stream creation fails, __init__ must not leave a running _run task.

    _run dereferences self._ffi_handle, which is only assigned once stream creation
    succeeds. Scheduling the task before that assignment leaves an orphaned task that
    raises AttributeError from the event loop, uncatchable by the caller.
    """
    track = MagicMock(spec=rtc.Track)
    before = asyncio.all_tasks()

    with patch.object(
        rtc.AudioStream,
        "_create_owned_stream",
        side_effect=RuntimeError("track already closed"),
    ):
        with pytest.raises(RuntimeError, match="track already closed"):
            rtc.AudioStream(track)

    orphaned = [
        t
        for t in asyncio.all_tasks() - before
        if getattr(t.get_coro(), "__qualname__", "") == "AudioStream._run"
    ]
    for t in orphaned:
        t.cancel()

    assert not orphaned
