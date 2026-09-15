from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pocketstation as pks

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from publish import to_livekit_frame, wait_until_done


class AudioConversionTest(unittest.TestCase):
    def test_stereo_float32_samples_become_mono_pcm16(self) -> None:
        source = SimpleNamespace(
            samples=memoryview(bytearray()),
            sample_rate_hz=48_000,
            channel_count=2,
            sample_count=4,
        )
        source.samples = [-1.5, -0.5, 0.5, 1.5]

        frame = to_livekit_frame(cast(pks.AudioFrame, source))

        self.assertEqual(frame.sample_rate, 48_000)
        self.assertEqual(frame.num_channels, 1)
        self.assertEqual(frame.samples_per_channel, 2)
        self.assertEqual(list(frame.data), [-32_767, 32_767])


class ActiveWaitTest(unittest.IsolatedAsyncioTestCase):
    async def test_returns_when_pocketstation_stops(self) -> None:
        disconnected = asyncio.Event()
        running = SimpleNamespace(is_stopped=False)

        async def stop_capture() -> None:
            await asyncio.sleep(0.01)
            running.is_stopped = True

        stop_task = asyncio.create_task(stop_capture())
        await asyncio.wait_for(
            wait_until_done(disconnected, running, duration=0.0),
            timeout=0.2,
        )
        await stop_task

        self.assertFalse(disconnected.is_set())


if __name__ == "__main__":
    unittest.main()
