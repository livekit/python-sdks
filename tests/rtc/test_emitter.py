from livekit.rtc import EventEmitter
from typing import Literal
import pytest


def test_events():
    EventTypes = Literal["connected", "reconnected", "disconnected"]
    emitter = EventEmitter[EventTypes]()

    connected_calls = []

    @emitter.once("connected")
    def on_connected():
        connected_calls.append(True)

    emitter.emit("connected")
    emitter.emit("connected")
    assert len(connected_calls) == 1

    emitter.emit("unknown_event")  # type: ignore

    reconnected_calls = []

    @emitter.on("reconnected")
    def on_reconnected():
        reconnected_calls.append(True)

    emitter.emit("reconnected")
    emitter.emit("reconnected")
    assert len(reconnected_calls) == 2

    disconnected_calls = []

    @emitter.on("disconnected")
    def on_disconnected():
        disconnected_calls.append(True)

    @emitter.on("disconnected")
    def on_disconnected_another():
        disconnected_calls.append(True)

    emitter.emit("disconnected")
    emitter.emit("disconnected")
    emitter.off("disconnected", on_disconnected)
    emitter.emit("disconnected")
    assert len(disconnected_calls) == 5


def test_args():
    EventTypes = Literal["whatever"]

    emitter = EventEmitter[EventTypes]()

    calls = []

    @emitter.on("whatever")
    def on_whatever(first, second, third):
        calls.append((first, second, third))

    emitter.emit("whatever", 1, 2, 3)
    emitter.emit("whatever", 1, 2, 3, 4, 5)  # only 3 arguments will be passed

    assert calls == [(1, 2, 3), (1, 2, 3)]

    with pytest.raises(TypeError):
        emitter.emit("whatever", 1, 2)


def test_varargs():
    EventTypes = Literal["whatever"]

    emitter = EventEmitter[EventTypes]()

    calls = []

    @emitter.on("whatever")
    def on_whatever_varargs(*args):
        calls.append(args)

    emitter.emit("whatever", 1, 2, 3, 4, 5)
    emitter.emit("whatever", 1, 2)

    assert calls == [(1, 2, 3, 4, 5), (1, 2)]


def test_throw():
    EventTypes = Literal["error"]

    emitter = EventEmitter[EventTypes]()

    calls = []

    @emitter.on("error")
    def on_error():
        calls.append(True)
        raise ValueError("error")

    @emitter.on("error")
    def on_error_another():
        calls.append(True)

    emitter.emit("error")

    assert len(calls) == 2
