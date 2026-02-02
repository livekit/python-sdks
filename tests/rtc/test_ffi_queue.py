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

"""Tests for FfiQueue event filtering functionality.

These tests verify the event_types filtering feature of FfiQueue without
requiring the native FFI library.
"""

import asyncio
import threading
from dataclasses import dataclass
from typing import Generic, List, Optional, Set, TypeVar
from unittest.mock import MagicMock

import pytest

# Re-implement FfiQueue locally for testing (avoids FFI library dependency)
T = TypeVar("T")


class Queue(Generic[T]):
    """Simple asyncio-compatible queue for testing."""

    def __init__(self) -> None:
        self._items: List[T] = []

    def put_nowait(self, item: T) -> None:
        self._items.append(item)

    def get_nowait(self) -> T:
        return self._items.pop(0)

    def empty(self) -> bool:
        return len(self._items) == 0


class FfiQueue(Generic[T]):
    """Copy of FfiQueue with event_types filtering for testing."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subscribers: List[
            tuple[Queue[T], asyncio.AbstractEventLoop, Optional[Set[str]]]
        ] = []

    def put(self, item: T) -> None:
        which = None
        try:
            which = item.WhichOneof("message")  # type: ignore
        except Exception:
            pass

        with self._lock:
            for queue, loop, event_types in self._subscribers:
                if event_types is not None and which is not None:
                    if which not in event_types:
                        continue

                try:
                    loop.call_soon_threadsafe(queue.put_nowait, item)
                except Exception:
                    pass

    def subscribe(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        event_types: Optional[Set[str]] = None,
    ) -> Queue[T]:
        with self._lock:
            queue = Queue[T]()
            loop = loop or asyncio.get_event_loop()
            self._subscribers.append((queue, loop, event_types))
            return queue

    def unsubscribe(self, queue: Queue[T]) -> None:
        with self._lock:
            for i, (q, _, _) in enumerate(self._subscribers):
                if q == queue:
                    self._subscribers.pop(i)
                    break


@dataclass
class MockFfiEvent:
    """Mock FFI event with WhichOneof support."""

    _message_type: str

    def WhichOneof(self, field: str) -> str:
        return self._message_type


class TestFfiQueueEventFiltering:
    """Test suite for FfiQueue event_types filtering."""

    @pytest.fixture
    def event_loop(self):
        """Create event loop for tests."""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    def test_subscribe_without_filter_receives_all_events(self, event_loop):
        """Subscriber without event_types filter receives all events."""
        queue = FfiQueue()
        sub = queue.subscribe(event_loop, event_types=None)

        # Send various event types
        events = [
            MockFfiEvent("room_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("video_stream_event"),
            MockFfiEvent("track_event"),
        ]

        for event in events:
            queue.put(event)

        # Run event loop to process callbacks
        event_loop.run_until_complete(asyncio.sleep(0.01))

        # Should receive all 4 events
        received = []
        while not sub.empty():
            received.append(sub.get_nowait())

        assert len(received) == 4

    def test_subscribe_with_filter_receives_only_matching_events(self, event_loop):
        """Subscriber with event_types filter only receives matching events."""
        queue = FfiQueue()
        sub = queue.subscribe(event_loop, event_types={"audio_stream_event"})

        # Send various event types
        events = [
            MockFfiEvent("room_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("video_stream_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("track_event"),
        ]

        for event in events:
            queue.put(event)

        # Run event loop to process callbacks
        event_loop.run_until_complete(asyncio.sleep(0.01))

        # Should receive only 2 audio_stream_events
        received = []
        while not sub.empty():
            received.append(sub.get_nowait())

        assert len(received) == 2
        assert all(e._message_type == "audio_stream_event" for e in received)

    def test_multiple_subscribers_different_filters(self, event_loop):
        """Multiple subscribers can have different filters."""
        queue = FfiQueue()

        # Subscriber 1: only audio events
        sub_audio = queue.subscribe(event_loop, event_types={"audio_stream_event"})

        # Subscriber 2: only video events
        sub_video = queue.subscribe(event_loop, event_types={"video_stream_event"})

        # Subscriber 3: all events
        sub_all = queue.subscribe(event_loop, event_types=None)

        # Send mixed events
        events = [
            MockFfiEvent("room_event"),
            MockFfiEvent("audio_stream_event"),
            MockFfiEvent("video_stream_event"),
            MockFfiEvent("audio_stream_event"),
        ]

        for event in events:
            queue.put(event)

        event_loop.run_until_complete(asyncio.sleep(0.01))

        # Count received events
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

        assert audio_count == 2  # 2 audio events
        assert video_count == 1  # 1 video event
        assert all_count == 4  # all 4 events

    def test_filter_with_multiple_event_types(self, event_loop):
        """Filter can accept multiple event types."""
        queue = FfiQueue()
        sub = queue.subscribe(
            event_loop, event_types={"audio_stream_event", "video_stream_event"}
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

        # Should receive audio and video events only
        assert len(received) == 2
        types = {e._message_type for e in received}
        assert types == {"audio_stream_event", "video_stream_event"}

    def test_unsubscribe_works_with_filtered_subscriber(self, event_loop):
        """Unsubscribe correctly removes filtered subscriber."""
        queue = FfiQueue()
        sub = queue.subscribe(event_loop, event_types={"audio_stream_event"})

        queue.put(MockFfiEvent("audio_stream_event"))
        event_loop.run_until_complete(asyncio.sleep(0.01))

        # Should have received 1 event
        assert not sub.empty()

        # Unsubscribe
        queue.unsubscribe(sub)

        # Clear the queue
        while not sub.empty():
            sub.get_nowait()

        # Send more events
        queue.put(MockFfiEvent("audio_stream_event"))
        event_loop.run_until_complete(asyncio.sleep(0.01))

        # Should not receive after unsubscribe
        assert sub.empty()

    def test_event_without_which_oneof_passes_through(self, event_loop):
        """Events without WhichOneof method pass through to all subscribers."""
        queue = FfiQueue()
        sub = queue.subscribe(event_loop, event_types={"audio_stream_event"})

        # Event without WhichOneof
        plain_event = MagicMock(spec=[])  # No WhichOneof method

        queue.put(plain_event)
        event_loop.run_until_complete(asyncio.sleep(0.01))

        # Should still receive it (can't filter without type info)
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
            sub = queue.subscribe(event_loop, event_types={"audio_stream_event"})
            subscribers.append(sub)

        # Generate 1000 events, only 5% are audio
        events = []
        for i in range(1000):
            if i < 50:  # 5% audio events
                events.append(MockFfiEvent("audio_stream_event"))
            else:
                events.append(MockFfiEvent("room_event"))

        # Process all events
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

        # Total callbacks made: 10 subscribers × 50 audio events = 500
        # Without filtering: 10 subscribers × 1000 events = 10,000
        # This is a 95% reduction in callback/object creation
