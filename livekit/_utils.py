import asyncio
import threading
from collections import deque
from contextlib import contextmanager
from typing import Callable, Generic, List, Optional, TypeVar

T = TypeVar('T')


class RingQueue(Generic[T]):
    def __init__(self, capacity: int = 0) -> None:
        self._capacity = capacity
        self._queue: deque[T] = deque()
        self._event = asyncio.Event()

    def put(self, item: T) -> None:
        if self._capacity > 0 and len(self._queue) == self._capacity:
            self._queue.pop()
        self._queue.append(item)
        self._event.set()

    async def get(self) -> T:
        while len(self._queue) == 0:
            await self._event.wait()
        self._event.clear()
        return self._queue.popleft()


class BroadcastQueue(Generic[T]):
    def __init__(self) -> None:
        self._subscribers: List[asyncio.Queue[T]] = []

    def len_subscribers(self) -> int:
        return len(self._subscribers)

    def put_nowait(self, item: T) -> None:
        for queue in self._subscribers:
            queue.put_nowait(item)

    def subscribe(self) -> asyncio.Queue[T]:
        queue = asyncio.Queue[T]()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[T]) -> None:
        self._subscribers.remove(queue)

    @contextmanager
    def observe(self):
        queue = self.subscribe()
        try:
            yield queue
        finally:
            self.unsubscribe(queue)

    async def join(self) -> None:
        for queue in self._subscribers:
            await queue.join()


# thread safe variant of BroadcastQueue (lock + call_soon_threadsafe)
# used by the FFI client to send events from a unknown thread to the corresponding
# asyncio event loop
class BroadcastChannel(Generic[T]):
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subscribers: List[asyncio.Queue[T]] = []

    def put(self, item: T) -> None:
        with self._lock:
            for queue in self._subscribers:
                loop: asyncio.AbstractEventLoop = queue._loop
                loop.call_soon_threadsafe(queue.put_nowait, item)

    def subscribe(self, loop: Optional[asyncio.AbstractEventLoop] = None) \
            -> asyncio.Queue[T]:
        with self._lock:
            queue = asyncio.Queue[T]()
            queue._loop = loop or asyncio.get_event_loop()
            self._subscribers.append(queue)
            return queue

    def unsubscribe(self, queue: asyncio.Queue[T]) -> None:
        with self._lock:
            self._subscribers.remove(queue)

    @contextmanager
    def observe(self):
        queue = self.subscribe()
        try:
            yield queue
        finally:
            self.unsubscribe(queue)


async def wait_for(queue: asyncio.Queue[T], fnc: Callable[[T], bool]) \
        -> T:
    """ Wait for an event that matches the given function.
    The previous events are discarded.
    """

    while True:
        event = await queue.get()
        if fnc(event):
            # task_done must be manually called for the returned item
            return event

        queue.task_done()
