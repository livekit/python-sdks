import inspect
import asyncio
from typing import Callable, Dict, Set, Optional, Generic, TypeVar

from .log import logger

T_contra = TypeVar("T_contra", contravariant=True)


class EventEmitter(Generic[T_contra]):
    def __init__(self) -> None:
        """
        Initialize a new instance of EventEmitter.
        """
        self._events: Dict[T_contra, Set[Callable]] = dict()

    def emit(self, event: T_contra, *args) -> None:
        """
        Trigger all callbacks associated with the given event.

        Args:
            event (T): The event to emit.
            *args: Positional arguments to pass to the callbacks.

        Example:
            Basic usage of emit:

            ```python
            emitter = EventEmitter[str]()

            def greet(name):
                print(f"Hello, {name}!")

            emitter.on('greet', greet)
            emitter.emit('greet', 'Alice')  # Output: Hello, Alice!
            ```
        """
        if event in self._events:
            callables = self._events[event].copy()
            for callback in callables:
                try:
                    sig = inspect.signature(callback)
                    params = sig.parameters.values()

                    has_varargs = any(p.kind == p.VAR_POSITIONAL for p in params)
                    if has_varargs:
                        callback(*args)
                    else:
                        positional_params = [
                            p
                            for p in params
                            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                        ]
                        num_params = len(positional_params)
                        num_args = min(len(args), num_params)
                        callback_args = args[:num_args]

                        callback(*callback_args)
                except TypeError:
                    raise
                except Exception:
                    logger.exception(f"failed to emit event {event}")

    def once(self, event: T_contra, callback: Optional[Callable] = None) -> Callable:
        """
        Register a callback to be called only once when the event is emitted.

        If a callback is provided, it registers the callback directly.
        If no callback is provided, it returns a decorator for use with function definitions.

        Args:
            event (T): The event to listen for.
            callback (Callable, optional): The callback to register. Defaults to None.

        Returns:
            Callable: The registered callback or a decorator if callback is None.

        Example:
            Using once with a direct callback:

            ```python
            emitter = EventEmitter[str]()

            def greet_once(name):
                print(f"Hello once, {name}!")

            emitter.once('greet', greet_once)
            emitter.emit('greet', 'Bob')    # Output: Hello once, Bob!
            emitter.emit('greet', 'Bob')    # No output, callback was removed after first call
            ```

            Using once as a decorator:

            ```python
            emitter = EventEmitter[str]()

            @emitter.once('greet')
            def greet_once(name):
                print(f"Hello once, {name}!")

            emitter.emit('greet', 'Bob')    # Output: Hello once, Bob!
            emitter.emit('greet', 'Bob')    # No output
            ```
        """
        if callback is not None:

            def once_callback(*args, **kwargs):
                self.off(event, once_callback)
                callback(*args, **kwargs)

            return self.on(event, once_callback)
        else:

            def decorator(callback: Callable) -> Callable:
                self.once(event, callback)
                return callback

            return decorator

    def on(self, event: T_contra, callback: Optional[Callable] = None) -> Callable:
        """
        Register a callback to be called whenever the event is emitted.

        If a callback is provided, it registers the callback directly.
        If no callback is provided, it returns a decorator for use with function definitions.

        Args:
            event (T): The event to listen for.
            callback (Callable, optional): The callback to register. Defaults to None.

        Returns:
            Callable: The registered callback or a decorator if callback is None.

        Example:
            Using on with a direct callback:

            ```python
            emitter = EventEmitter[str]()

            def greet(name):
                print(f"Hello, {name}!")

            emitter.on('greet', greet)
            emitter.emit('greet', 'Charlie')  # Output: Hello, Charlie!
            ```

            Using on as a decorator:

            ```python
            emitter = EventEmitter[str]()

            @emitter.on('greet')
            def greet(name):
                print(f"Hello, {name}!")

            emitter.emit('greet', 'Charlie')  # Output: Hello, Charlie!
            ```
        """
        if callback is not None:
            if asyncio.iscoroutinefunction(callback):
                raise ValueError(
                    "Cannot register an async callback with `.on()`. Use `asyncio.create_task` within your synchronous callback instead."
                )

            if event not in self._events:
                self._events[event] = set()
            self._events[event].add(callback)
            return callback
        else:

            def decorator(callback: Callable) -> Callable:
                self.on(event, callback)
                return callback

            return decorator

    def off(self, event: T_contra, callback: Callable) -> None:
        """
        Unregister a callback from an event.

        Args:
            event (T): The event to stop listening to.
            callback (Callable): The callback to remove.

        Example:
            Removing a callback:

            ```python
            emitter = EventEmitter[str]()

            def greet(name):
                print(f"Hello, {name}!")

            emitter.on('greet', greet)
            emitter.off('greet', greet)
            emitter.emit('greet', 'Dave')  # No output, callback was removed
            ```
        """
        if event in self._events:
            self._events[event].discard(callback)
