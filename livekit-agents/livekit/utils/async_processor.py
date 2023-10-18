import asyncio
from typing import TypeVar, Generic, Optional
from collections.abc import Callable 

T = TypeVar('T')
U = TypeVar('U')


class AsyncProcessor(Generic[T, U]):
    """Convert a blocking syncrounous function into an async execution. 
       For example, this is useful for running async pytorch inference.
    """

    def __init__(self, processor_fn: Callable[[T], U], executor: Optional[any] = None):
        """Constructor for AsyncProcessor
        Args:
            processor_fn (callable): Function to process data. Never called concurrently, only one at a time.
            executor (any, optional): Executor to run the processor_fn on via loop.run_in_executor(). Defaults to None.
        """
        self._executor = executor
        self._lock = asyncio.Lock()
        self._processor_fn = processor_fn

    async def push_data(self, data):
        loop = asyncio.get_event_loop()
        async with self._lock:
            res = await loop.run_in_executor(self._executor, self._processor_fn, data)
            return res
