import asyncio
from collections import deque
from typing import Callable, Generic, List, TypeVar

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


class Queue(asyncio.Queue[T]):
    """ asyncio.Queue with utility functions. """

    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize)

    async def wait_for(self, fnc: Callable[[T], bool]) \
            -> T:
        """ Wait for an event that matches the given function.
        The previous events are discarded.
        """

        while True:
            event = await self.get()
            if fnc(event):
                # task_done must be manually called for the returned item
                return event

            self.task_done()


class BroadcastQueue(Generic[T]):
    """ Queue with multiple subscribers. """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._subscribers: List[Queue[T]] = []

    def len_subscribers(self) -> int:
        return len(self._subscribers)

    def put_nowait(self, item: T) -> None:
        for queue in self._subscribers:
            queue.put_nowait(item)

    def subscribe(self) -> Queue[T]:
        queue = Queue[T]()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: Queue[T]) -> None:
        self._subscribers.remove(queue)

    async def join(self) -> None:
        async with self._lock:
            subs = self._subscribers.copy()
            for queue in subs:
                await queue.join()
