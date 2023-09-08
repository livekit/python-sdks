import asyncio
from collections import deque
from typing import Generic, TypeVar

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
