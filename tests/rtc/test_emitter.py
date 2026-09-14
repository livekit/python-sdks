import asyncio
import functools
import warnings
from typing import Any, Literal
from unittest.mock import AsyncMock

import pytest

from livekit.rtc import EventEmitter


def test_events() -> None:
    EventTypes = Literal["connected", "reconnected", "disconnected"]
    emitter = EventEmitter[EventTypes]()

    connected_calls = []

    @emitter.once("connected")
    def on_connected() -> None:
        connected_calls.append(True)

    emitter.emit("connected")
    emitter.emit("connected")
    assert len(connected_calls) == 1

    emitter.emit("unknown_event")  # type: ignore

    reconnected_calls = []

    @emitter.on("reconnected")
    def on_reconnected() -> None:
        reconnected_calls.append(True)

    emitter.emit("reconnected")
    emitter.emit("reconnected")
    assert len(reconnected_calls) == 2

    disconnected_calls = []

    @emitter.on("disconnected")
    def on_disconnected() -> None:
        disconnected_calls.append(True)

    @emitter.on("disconnected")
    def on_disconnected_another() -> None:
        disconnected_calls.append(True)

    emitter.emit("disconnected")
    emitter.emit("disconnected")
    emitter.off("disconnected", on_disconnected)
    emitter.emit("disconnected")
    assert len(disconnected_calls) == 5


def test_args() -> None:
    EventTypes = Literal["whatever"]

    emitter = EventEmitter[EventTypes]()

    calls = []

    @emitter.on("whatever")
    def on_whatever(first: Any, second: Any, third: Any) -> None:
        calls.append((first, second, third))

    emitter.emit("whatever", 1, 2, 3)
    emitter.emit("whatever", 1, 2, 3, 4, 5)  # only 3 arguments will be passed

    assert calls == [(1, 2, 3), (1, 2, 3)]

    with pytest.raises(TypeError):
        emitter.emit("whatever", 1, 2)


def test_varargs() -> None:
    EventTypes = Literal["whatever"]

    emitter = EventEmitter[EventTypes]()

    calls = []

    @emitter.on("whatever")
    def on_whatever_varargs(*args: Any) -> None:
        calls.append(args)

    emitter.emit("whatever", 1, 2, 3, 4, 5)
    emitter.emit("whatever", 1, 2)

    assert calls == [(1, 2, 3, 4, 5), (1, 2)]


def test_throw() -> None:
    EventTypes = Literal["error"]

    emitter = EventEmitter[EventTypes]()

    calls = []

    @emitter.on("error")
    def on_error() -> None:
        calls.append(True)
        raise ValueError("error")

    @emitter.on("error")
    def on_error_another() -> None:
        calls.append(True)

    emitter.emit("error")

    assert len(calls) == 2


def test_on_does_not_warn() -> None:
    """Registering a callback must not emit a DeprecationWarning.

    `asyncio.iscoroutinefunction` is deprecated in Python 3.14 and slated for removal
    in 3.16; `inspect.iscoroutinefunction` is the supported replacement.
    """
    EventTypes = Literal["connected"]

    emitter = EventEmitter[EventTypes]()

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)

        @emitter.on("connected")
        def on_connected() -> None:
            pass

        emitter.once("connected", on_connected)

    emitter.emit("connected")


def test_on_rejects_async_callback() -> None:
    """`.on()` refuses coroutine functions, however they are spelled."""
    EventTypes = Literal["connected"]

    emitter = EventEmitter[EventTypes]()

    async def on_connected() -> None:
        pass

    with pytest.raises(ValueError, match="Cannot register an async callback"):
        emitter.on("connected", on_connected)

    with pytest.raises(ValueError, match="Cannot register an async callback"):
        emitter.on("connected", functools.partial(on_connected))


def test_on_rejects_sentinel_tagged_callback() -> None:
    """A callable tagged with asyncio's private coroutine sentinel is rejected.

    `asyncio.iscoroutinefunction` honours this tag on every supported version;
    `inspect.iscoroutinefunction` never has. `@asyncio.coroutine` (removed in
    3.11) applied it, and `unittest.mock.AsyncMock` still does.
    """
    marker = getattr(asyncio.coroutines, "_is_coroutine", None)
    if marker is None:
        pytest.skip("asyncio.coroutines._is_coroutine is not defined on this Python")

    EventTypes = Literal["connected"]

    emitter = EventEmitter[EventTypes]()

    def on_connected() -> None:
        pass

    on_connected._is_coroutine = marker  # type: ignore[attr-defined]

    with pytest.raises(ValueError, match="Cannot register an async callback"):
        emitter.on("connected", on_connected)


def test_on_rejects_async_mock() -> None:
    """`AsyncMock` is rejected on every supported version.

    On Python 3.9, `inspect.iscoroutinefunction(AsyncMock())` is False; only the
    sentinel check catches it.
    """
    EventTypes = Literal["connected"]

    emitter = EventEmitter[EventTypes]()

    with pytest.raises(ValueError, match="Cannot register an async callback"):
        emitter.on("connected", AsyncMock())
