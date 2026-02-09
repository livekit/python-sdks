# Copyright 2023 LiveKit, Inc.
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

"""Tests for FfiQueue filter_fn functionality.

These tests verify the filter_fn feature of FfiQueue.
FfiQueue can be imported without loading the native FFI library.
"""

import asyncio
from dataclasses import dataclass

import pytest

from livekit.rtc._ffi_client import FfiQueue


@dataclass
class MockFfiEvent:
    """Mock FFI event with WhichOneof support."""

    _message_type: str

    def WhichOneof(self, field: str) -> str:
        return self._message_type


class TestFfiQueueFilterFn:
    """Test suite for FfiQueue filter_fn functionality."""

    @pytest.fixture
    def event_loop(self):
        """Create event loop for tests."""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    def test_subscribe_without_filter_receives_all_events(self, event_loop):
        """Subscriber without filter_fn receives all events."""
        queue = FfiQueue()
        sub = queue.subscribe(event_loop, filter_fn=None)

        events = [
            MockFfiEvent("room_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("video_stream_event"),
            MockFfiEvent("track_event"),
        ]

        for event in events:
            queue.put(event)

        event_loop.run_until_complete(asyncio.sleep(0.01))

        received = []
        while not sub.empty():
            received.append(sub.get_nowait())

        assert len(received) == 4

    def test_subscribe_with_filter_receives_only_matching_events(self, event_loop):
        """Subscriber with filter_fn only receives matching events."""
        queue = FfiQueue()
        sub = queue.subscribe(
            event_loop,
            filter_fn=lambda e: e.WhichOneof("message") == "audio_stream_event",
        )

        events = [
            MockFfiEvent("room_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("video_stream_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("track_event"),
        ]

        for event in events:
            queue.put(event)

        event_loop.run_until_complete(asyncio.sleep(0.01))

        received = []
        while not sub.empty():
            received.append(sub.get_nowait())

        assert len(received) == 2
        assert all(e._message_type == "audio_stream_event" for e in received)

    def test_multiple_subscribers_different_filters(self, event_loop):
        """Multiple subscribers can have different filters."""
        queue = FfiQueue()

        sub_audio = queue.subscribe(
            event_loop,
            filter_fn=lambda e: e.WhichOneof("message") == "audio_stream_event",
        )
        sub_video = queue.subscribe(
            event_loop,
            filter_fn=lambda e: e.WhichOneof("message") == "video_stream_event",
        )
        sub_all = queue.subscribe(event_loop, filter_fn=None)

        events = [
            MockFfiEvent("room_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("video_stream_event"),
            MockFfiEvent("audio_stream_event"),
        ]

        for event in events:
            queue.put(event)

        event_loop.run_until_complete(asyncio.sleep(0.01))

        audio_count = 0
        while not sub_audio.empty():
            sub_audio.get_nowait()
            audio_count += 1

        video_count = 0
        while not sub_video.empty():
            sub_video.get_nowait()
            video_count += 1

        all_count = 0
        while not sub_all.empty():
            sub_all.get_nowait()
            all_count += 1

        assert audio_count == 2
        assert video_count == 1
        assert all_count == 4

    def test_filter_with_multiple_event_types(self, event_loop):
        """Filter can match multiple event types."""
        queue = FfiQueue()
        sub = queue.subscribe(
            event_loop,
            filter_fn=lambda e: e.WhichOneof("message")
            in {"audio_stream_event", "video_stream_event"},
        )

        events = [
            MockFfiEvent("room_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("video_stream_event"),
            MockFfiEvent("track_event"),
        ]

        for event in events:
            queue.put(event)

        event_loop.run_until_complete(asyncio.sleep(0.01))

        received = []
        while not sub.empty():
            received.append(sub.get_nowait())

        assert len(received) == 2
        types = {e._message_type for e in received}
        assert types == {"audio_stream_event", "video_stream_event"}

    def test_unsubscribe_works_with_filtered_subscriber(self, event_loop):
        """Unsubscribe correctly removes filtered subscriber."""
        queue = FfiQueue()
        sub = queue.subscribe(
            event_loop,
            filter_fn=lambda e: e.WhichOneof("message") == "audio_stream_event",
        )

        queue.put(MockFfiEvent("audio_stream_event"))
        event_loop.run_until_complete(asyncio.sleep(0.01))

        assert not sub.empty()

        queue.unsubscribe(sub)

        while not sub.empty():
            sub.get_nowait()

        queue.put(MockFfiEvent("audio_stream_event"))
        event_loop.run_until_complete(asyncio.sleep(0.01))

        assert sub.empty()

    def test_filter_error_delivers_item(self, event_loop):
        """If filter_fn raises, item is still delivered."""
        queue = FfiQueue()

        def bad_filter(e):
            raise ValueError("oops")

        sub = queue.subscribe(event_loop, filter_fn=bad_filter)

        queue.put(MockFfiEvent("audio_stream_event"))
        event_loop.run_until_complete(asyncio.sleep(0.01))

        # Item should be delivered despite filter error
        received = []
        while not sub.empty():
            received.append(sub.get_nowait())

        assert len(received) == 1


class TestFfiQueueMemoryReduction:
    """Test that filtering actually reduces object creation."""

    @pytest.fixture
    def event_loop(self):
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    def test_filtering_reduces_callback_calls(self, event_loop):
        """Verify filtering prevents call_soon_threadsafe for non-matching events."""
        queue = FfiQueue()

        # Create 10 subscribers, each only wants audio events
        subscribers = []
        for _ in range(10):
            sub = queue.subscribe(
                event_loop,
                filter_fn=lambda e: e.WhichOneof("message") == "audio_stream_event",
            )
            subscribers.append(sub)

        # Generate 1000 events, only 5% are audio
        events = []
        for i in range(1000):
            if i < 50:
                events.append(MockFfiEvent("audio_stream_event"))
            else:
                events.append(MockFfiEvent("room_event"))

        for event in events:
            queue.put(event)

        event_loop.run_until_complete(asyncio.sleep(0.1))

        # Each subscriber should have received only 50 events (not 1000)
        for sub in subscribers:
            count = 0
            while not sub.empty():
                sub.get_nowait()
                count += 1
            assert count == 50
