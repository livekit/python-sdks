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

"""Regression tests for AudioSource.clear_queue."""

from __future__ import annotations

import asyncio
import time

from livekit import rtc

SAMPLE_RATE = 24000


async def test_clear_queue_cuts_a_capture_longer_than_the_queue() -> None:
    """Audio captured before clear_queue stops right after it.

    A frame longer than the queue is fed to it chunk by chunk; clear_queue must also drop the
    chunks not queued yet, or they keep playing after an interruption.
    """
    source = rtc.AudioSource(SAMPLE_RATE, 1, queue_size_ms=50)
    track = rtc.LocalAudioTrack.create_audio_track("clear", source)
    stream = rtc.AudioStream(track, sample_rate=SAMPLE_RATE, num_channels=1)
    heard: list[float] = []

    async def listen() -> None:
        async for event in stream:
            if any(event.frame.data):
                heard.append(time.monotonic())

    listener = asyncio.create_task(listen())
    samples = SAMPLE_RATE // 2  # 500 ms, ten times the queue
    frame = rtc.AudioFrame(b"\xe8\x03" * samples, SAMPLE_RATE, 1, samples)
    try:
        capture = asyncio.create_task(source.capture_frame(frame))
        await asyncio.sleep(0.025)
        cleared = time.monotonic()
        source.clear_queue()
        # the next reply starts at once, while the cut capture winds down
        silence = SAMPLE_RATE // 100
        await source.capture_frame(rtc.AudioFrame(b"\x00\x00" * silence, SAMPLE_RATE, 1, silence))
        await asyncio.wait_for(capture, 0.1)
        await asyncio.sleep(0.6)
    finally:
        listener.cancel()
        await asyncio.gather(listener, return_exceptions=True)
        await stream.aclose()
        await source.aclose()

    after_clear = max((t - cleared for t in heard), default=0.0)
    assert after_clear < 0.02, f"audio played {after_clear * 1000:.0f} ms after clear_queue"
