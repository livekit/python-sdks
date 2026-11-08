"""Integration checks against the actual FFI library selected by LIVEKIT_LIB_PATH."""

import asyncio

import numpy as np
import pytest
from livekit import rtc
from livekit.rtc._ffi_client import FfiClient


@pytest.mark.parametrize("rate,channels", [(8000, 1), (24000, 1), (48000, 2)])
@pytest.mark.parametrize("frame_ms", [7, 10, 20, 50])
async def test_local_sink_exact_pcm(rate, channels, frame_ms):
    source = rtc.AudioSource(rate, channels, queue_size_ms=1000)
    track = rtc.LocalAudioTrack.create_audio_track("batch-test", source)
    stream = rtc.AudioStream(track, sample_rate=rate, num_channels=channels, frame_size_ms=frame_ms)
    count = rate * 210 // 1000 * channels
    data = ((np.arange(count, dtype=np.int32) % 30000) + 1).astype(np.int16)
    received = []

    async def collect():
        length = 0
        async for e in stream:
            assert e.frame.samples_per_channel == rate * frame_ms // 1000
            assert e.frame.sample_rate == rate
            assert e.frame.num_channels == channels
            d = np.asarray(e.frame.data).copy()
            received.append(d)
            length += len(d)
            if length >= count + rate * channels // 2:
                break

    task = asyncio.create_task(collect())
    try:
        await source.capture_frame(
            rtc.AudioFrame(data.tobytes(), rate, channels, count // channels)
        )
        await asyncio.wait_for(task, 3)
        all_data = np.concatenate(received)
        first = np.flatnonzero(all_data)[0]
        assert np.array_equal(all_data[first : first + count], data)
    finally:
        await stream.aclose()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await source.aclose()
        track._ffi_handle.dispose()


async def test_repeated_stream_close_releases_subscription():
    source = rtc.AudioSource(24000, 1, queue_size_ms=100)
    track = rtc.LocalAudioTrack.create_audio_track("close-test", source)
    baseline = len(FfiClient.instance.queue._subscribers)
    try:
        for _ in range(20):
            stream = rtc.AudioStream(track, sample_rate=24000, num_channels=1, frame_size_ms=50)
            await source.capture_frame(rtc.AudioFrame(bytes(480), 24000, 1, 240))
            await stream.aclose()
            assert stream._task.done()
            assert len(FfiClient.instance.queue._subscribers) == baseline
    finally:
        await source.aclose()
        track._ffi_handle.dispose()
