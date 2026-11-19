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


def test_once_passes_only_the_arguments_the_callback_takes() -> None:
    emitter = EventEmitter[str]()
    calls: list[Any] = []

    @emitter.once("event")
    def on_event(first: Any) -> None:
        calls.append(first)

    emitter.emit("event", 1, 2, 3)  # like on(), the extra arguments are dropped
    emitter.emit("event", 4)

    assert calls == [1]


def test_once_runs_a_callback_without_a_signature() -> None:
    emitter = EventEmitter[str]()
    results: list[Any] = []

    emitter.once("event", min)  # builtins like min expose no signature
    emitter.once("event", lambda *args: results.append(args))
    emitter.emit("event", 2, 1)
    emitter.emit("event", 3, 4)

    assert results == [(2, 1)]
    assert not emitter._events["event"]


def test_off_removes_a_once_handler() -> None:
    emitter = EventEmitter[str]()
    calls: list[str] = []

    def handler() -> None:
        calls.append("x")

    class Listener:
        def handle(self) -> None:
            calls.append("method")

    listener = Listener()
    emitter.once("event", handler)
    emitter.once("event", listener.handle)
    emitter.off("event", handler)
    emitter.off("event", listener.handle)  # a new bound method object, equal to the first
    emitter.emit("event")

    assert calls == []


def test_once_trims_to_the_callback_signature_at_emit_time() -> None:
    emitter = EventEmitter[str]()
    calls: list[tuple[Any, Any]] = []

    def handler(a: Any, b: Any) -> None:
        calls.append((a, b))

    callback = functools.partial(handler, b="registered")
    emitter.once("event", callback)
    callback.keywords.clear()  # a partial's signature can change after registration
    emitter.emit("event", 1, 2)

    assert calls == [(1, 2)]


def test_off_does_not_compare_unrelated_once_callbacks() -> None:
    emitter = EventEmitter[str]()

    class Strict:
        def __call__(self) -> None:
            pass

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Strict):
                raise ValueError("compared with an unrelated callable")
            return other is self

        __hash__ = object.__hash__

    def plain() -> None:
        pass

    emitter.once("event", Strict())
    emitter.on("event", plain)
    emitter.off("event", plain)

    assert len(emitter._events["event"]) == 1


def test_an_on_handler_with_a_once_callback_attribute_keeps_its_signature() -> None:
    emitter = EventEmitter[str]()
    calls: list[Any] = []

    def handler(value: Any) -> None:
        calls.append(value)

    handler._once_callback = lambda: None  # type: ignore[attr-defined]
    emitter.on("event", handler)
    emitter.emit("event", 1)

    assert calls == [1]
