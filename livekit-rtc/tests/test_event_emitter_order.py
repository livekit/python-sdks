"""Dispatch order for `EventEmitter`.

Handlers used to live in a `set`, so `emit` walked them in hash order. That is
stable for the life of a process and arbitrary between runs, which is the worst
shape a bug can have: a handler that reads a field a peer handler writes during
the same emit is correct on the machine it was written on and wrong somewhere
else, all of the time rather than some of the time.

The ordering tests below pin hashes deliberately. Registering three handlers and
hoping a set shuffles them would pass on the broken implementation roughly one
run in six, and a test that only usually fails is not a regression test.
"""

from __future__ import annotations

from livekit.rtc.event_emitter import EventEmitter


class Handler:
    """A callable whose hash is chosen, so set order is known rather than lucky.

    CPython places small integer hashes by value, so handlers registered with
    descending hashes come back out of a `set` in ascending order, which is the
    exact reverse of how they went in.
    """

    def __init__(self, name: str, hash_value: int, seen: list, action=None) -> None:
        self.name = name
        self._hash = hash_value
        self._seen = seen
        self._action = action

    def __call__(self) -> None:
        self._seen.append(self.name)
        if self._action is not None:
            self._action()

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        return self is other


def test_handlers_run_in_the_order_they_were_registered() -> None:
    seen: list = []
    emitter = EventEmitter[str]()
    for name, h in (("first", 3), ("second", 2), ("third", 1)):
        emitter.on("event", Handler(name, h, seen))

    emitter.emit("event")

    assert seen == ["first", "second", "third"], seen


def test_a_handler_observes_what_an_earlier_handler_wrote() -> None:
    """The reported failure, reduced.

    livekit-agents stamps `speech_id` onto a metrics object by mutating it in one
    handler and expects later subscribers to see the stamped value. Under hash
    order the reporter measured the pre-stamp state in 7 of 12 fresh processes.
    """
    record: dict = {"speech_id": None}
    observed: list = []

    # hashes chosen so a set would dispatch the reader first, before the stamp
    emitter = EventEmitter[str]()
    emitter.on(
        "metrics",
        Handler("stamp", 2, [], lambda: record.__setitem__("speech_id", "abc123")),
    )
    emitter.on(
        "metrics",
        Handler("read", 1, [], lambda: observed.append(record["speech_id"])),
    )
    emitter.emit("metrics")

    assert observed == ["abc123"], observed


def test_registering_the_same_handler_twice_dispatches_it_once() -> None:
    """`set.add` was idempotent and callers rely on that."""
    seen: list = []
    emitter = EventEmitter[str]()
    handler = Handler("only", 1, seen)

    emitter.on("event", handler)
    emitter.on("event", handler)
    emitter.emit("event")

    assert seen == ["only"], seen


def test_re_registering_does_not_move_a_handler_to_the_back() -> None:
    """Otherwise `on` would quietly double as a reordering operation, and a
    caller re-subscribing an existing handler would change what its peers see."""
    seen: list = []
    emitter = EventEmitter[str]()
    first, second = Handler("first", 3, seen), Handler("second", 2, seen)
    emitter.on("event", first)
    emitter.on("event", second)

    emitter.on("event", first)
    emitter.emit("event")

    assert seen == ["first", "second"], seen


def test_unsubscribing_during_dispatch_takes_effect_from_the_next_emit() -> None:
    """`emit` walks a copy, so the emit that removed a handler still runs it.

    That is deliberate and `once` depends on it, but it is worth pinning: moving
    to an ordered container would be an easy place to start iterating the live
    collection instead, which turns an `off` inside a handler into a mutation
    during iteration.
    """
    seen: list = []
    emitter = EventEmitter[str]()

    def first() -> None:
        seen.append("first")
        emitter.off("event", second)

    def second() -> None:
        seen.append("second")

    emitter.on("event", first)
    emitter.on("event", second)
    emitter.emit("event")
    emitter.emit("event")

    assert seen == ["first", "second", "first"], seen


def test_once_fires_once_and_leaves_the_order_alone() -> None:
    seen: list = []
    emitter = EventEmitter[str]()
    emitter.on("event", Handler("before", 3, seen))
    emitter.once("event", Handler("once", 2, seen))
    emitter.on("event", Handler("after", 1, seen))

    emitter.emit("event")
    emitter.emit("event")

    assert seen == ["before", "once", "after", "before", "after"], seen
