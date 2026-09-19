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


class _OrderedHandler:
    """A callable whose hash is fixed, so a set orders it independently of registration."""

    def __init__(self, name: str, hash_value: int, sink: list[str]) -> None:
        self._name = name
        self._hash = hash_value
        self._sink = sink

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        return self is other

    def __call__(self) -> None:
        self._sink.append(self._name)


def test_handlers_run_in_registration_order() -> None:
    # Handlers were kept in a set, so dispatch order was hash-derived. The hashes here are
    # picked so a set yields them in the opposite order to the one they were added in.
    emitter = EventEmitter[str]()
    order: list[str] = []

    emitter.on("event", _OrderedHandler("first", 5, order))
    emitter.on("event", _OrderedHandler("second", 1, order))

    emitter.emit("event")
    assert order == ["first", "second"]


def test_a_mutating_handler_runs_before_a_peer_that_reads_it() -> None:
    # The livekit-agents case: one handler stamps a field onto the emitted object and a
    # user handler registered later reads it. Registration order has to decide.
    class Event:
        def __init__(self) -> None:
            self.speech_id: Any = None

    class Stamp:
        def __hash__(self) -> int:
            return 5

        def __eq__(self, other: object) -> bool:
            return self is other

        def __call__(self, ev: Event) -> None:
            ev.speech_id = "speech_1"

    class Read:
        def __init__(self, sink: list[Any]) -> None:
            self._sink = sink

        def __hash__(self) -> int:
            return 1

        def __eq__(self, other: object) -> bool:
            return self is other

        def __call__(self, ev: Event) -> None:
            self._sink.append(ev.speech_id)

    emitter = EventEmitter[str]()
    seen: list[Any] = []
    emitter.on("metrics", Stamp())
    emitter.on("metrics", Read(seen))

    for _ in range(5):
        emitter.emit("metrics", Event())

    assert seen == ["speech_1"] * 5


def test_off_still_removes_a_handler() -> None:
    emitter = EventEmitter[str]()
    calls: list[str] = []

    @emitter.on("event")
    def keep() -> None:
        calls.append("keep")

    @emitter.on("event")
    def drop() -> None:
        calls.append("drop")

    emitter.off("event", drop)
    emitter.off("event", drop)  # removing twice must not raise
    emitter.emit("event")
    assert calls == ["keep"]


def test_registering_the_same_handler_twice_keeps_one_entry() -> None:
    emitter = EventEmitter[str]()
    calls: list[str] = []

    def handler() -> None:
        calls.append("x")

    emitter.on("event", handler)
    emitter.on("event", handler)
    emitter.emit("event")
    assert calls == ["x"]
