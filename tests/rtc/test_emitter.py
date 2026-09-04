from livekit.rtc import EventEmitter
from typing import Any, Literal
import pytest


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
