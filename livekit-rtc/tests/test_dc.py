"""End-to-end Test for data-channel scenarios.

Covers one-to-one delivery, broadcasting to all, topic filtering, and targeted
delivery via `destination_identities`.

Requires the following environment variables to run:
    LIVEKIT_URL
    LIVEKIT_API_KEY
    LIVEKIT_API_SECRET
"""

from __future__ import annotations

import asyncio
import os
import uuid
from typing import Callable, Optional

import pytest

from livekit import api, rtc
from livekit.rtc.room import EventTypes


WAIT_TIMEOUT = 20.0
WAIT_INTERVAL = 0.1


def skip_if_no_credentials():
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    return pytest.mark.skipif(
        bool(missing), reason=f"Missing environment variables: {', '.join(missing)}"
    )


def create_token(identity: str, room_name: str) -> str:
    return (
        api.AccessToken()
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        .to_jwt()
    )


def unique_room_name(base: str) -> str:
    return f"{base}-{uuid.uuid4().hex[:8]}"


async def _wait_until(
    predicate: Callable[[], bool],
    *,
    timeout: float = WAIT_TIMEOUT,
    interval: float = WAIT_INTERVAL,
    message: str = "condition not met",
) -> None:
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return
        await asyncio.sleep(interval)
    raise AssertionError(f"timeout waiting: {message}")


async def _connect(room: rtc.Room, identity: str, room_name: str) -> str:
    token = create_token(identity, room_name)
    url = os.environ["LIVEKIT_URL"]
    await room.connect(url, token)
    return token


async def _ensure_all_connected(rooms: list[rtc.Room]) -> None:
    await _wait_until(
        lambda: all(r.connection_state == rtc.ConnectionState.CONN_CONNECTED for r in rooms),
        message="not all rooms reached CONN_CONNECTED",
    )


async def _ensure_visible(observer: rtc.Room, identities: list[str]) -> None:
    """Wait until `observer` sees every identity in `identities` as a remote participant.

    Targeted publishes resolve identities at publish time, so we must let the
    sender's room state catch up before sending."""

    def _all_visible() -> bool:
        seen = {p.identity for p in observer.remote_participants.values()}
        return all(ident in seen for ident in identities)

    await _wait_until(
        _all_visible,
        message=f"not all identities visible to {observer.local_participant.identity}: {identities}",
    )


def _expect_event(
    room: rtc.Room,
    event: EventTypes,
    predicate: Optional[Callable[..., bool]] = None,
) -> asyncio.Future:
    loop = asyncio.get_event_loop()
    fut: asyncio.Future = loop.create_future()

    def _on_event(*args, **kwargs) -> None:
        if fut.done():
            return
        if predicate is None or predicate(*args, **kwargs):
            fut.set_result(args)

    room.on(event, _on_event)
    return fut


async def _await_event(fut: asyncio.Future, timeout: float = WAIT_TIMEOUT) -> None:
    try:
        await asyncio.wait_for(fut, timeout=timeout)
    except asyncio.TimeoutError as e:
        raise AssertionError("timed out waiting for event") from e


class _DataCollector:
    """Collects `data_received` packets matching `sender_identity` (when set)."""

    def __init__(self, room: rtc.Room, sender_identity: Optional[str] = None) -> None:
        self.packets: list[rtc.DataPacket] = []
        self._sender_identity = sender_identity

        def _on_data(packet: rtc.DataPacket) -> None:
            if self._sender_identity is not None and (
                packet.participant is None or packet.participant.identity != self._sender_identity
            ):
                return
            self.packets.append(packet)

        room.on("data_received", _on_data)

    def payloads(self) -> list[bytes]:
        return [p.data for p in self.packets]

    def topics(self) -> list[str | None]:
        return [p.topic for p in self.packets]


async def _assert_no_data(
    room: rtc.Room, collector: _DataCollector, *, settle: float = 1.0
) -> None:
    """Give the server time to deliver, then assert nothing arrived."""
    await asyncio.sleep(settle)
    assert collector.packets == [], (
        f"{room.local_participant.identity} unexpectedly received "
        f"{len(collector.packets)} packet(s): {collector.payloads()}"
    )


@skip_if_no_credentials()
@pytest.mark.asyncio
async def test_data_one_to_one() -> None:
    """sender targets a single identity; only that identity receives."""
    room_name = unique_room_name("py-dc-1to1")

    sender = rtc.Room()
    receiver = rtc.Room()
    bystander = rtc.Room()

    await _connect(sender, "sender", room_name)
    await _connect(receiver, "receiver", room_name)
    await _connect(bystander, "bystander", room_name)
    await _ensure_all_connected([sender, receiver, bystander])
    await _ensure_visible(sender, ["receiver", "bystander"])

    receiver_collector = _DataCollector(receiver, sender_identity="sender")
    bystander_collector = _DataCollector(bystander, sender_identity="sender")

    receiver_got = _expect_event(
        receiver,
        "data_received",
        predicate=lambda packet: (
            packet.participant is not None and packet.participant.identity == "sender"
        ),
    )

    payload = b"hello receiver"
    await sender.local_participant.publish_data(payload, destination_identities=["receiver"])

    await _await_event(receiver_got)
    assert receiver_collector.payloads() == [payload]
    await _assert_no_data(bystander, bystander_collector)

    await asyncio.gather(sender.disconnect(), receiver.disconnect(), bystander.disconnect())


@skip_if_no_credentials()
@pytest.mark.asyncio
async def test_data_one_to_many_targeted() -> None:
    """sender targets a subset of identities; only that subset receives."""
    room_name = unique_room_name("py-dc-1tomany")

    sender = rtc.Room()
    r1 = rtc.Room()
    r2 = rtc.Room()
    excluded = rtc.Room()

    await _connect(sender, "sender", room_name)
    await _connect(r1, "r1", room_name)
    await _connect(r2, "r2", room_name)
    await _connect(excluded, "excluded", room_name)
    await _ensure_all_connected([sender, r1, r2, excluded])
    await _ensure_visible(sender, ["r1", "r2", "excluded"])

    r1_collector = _DataCollector(r1, sender_identity="sender")
    r2_collector = _DataCollector(r2, sender_identity="sender")
    excluded_collector = _DataCollector(excluded, sender_identity="sender")

    r1_got = _expect_event(
        r1,
        "data_received",
        predicate=lambda packet: (
            packet.participant is not None and packet.participant.identity == "sender"
        ),
    )
    r2_got = _expect_event(
        r2,
        "data_received",
        predicate=lambda packet: (
            packet.participant is not None and packet.participant.identity == "sender"
        ),
    )

    payload = b"hello selected"
    await sender.local_participant.publish_data(payload, destination_identities=["r1", "r2"])

    await asyncio.gather(_await_event(r1_got), _await_event(r2_got))
    assert r1_collector.payloads() == [payload]
    assert r2_collector.payloads() == [payload]
    await _assert_no_data(excluded, excluded_collector)

    await asyncio.gather(
        sender.disconnect(), r1.disconnect(), r2.disconnect(), excluded.disconnect()
    )


@skip_if_no_credentials()
@pytest.mark.asyncio
async def test_data_broadcast() -> None:
    """Empty `destination_identities` broadcasts to every other participant."""
    room_name = unique_room_name("py-dc-broadcast")

    sender = rtc.Room()
    receivers = [rtc.Room() for _ in range(3)]
    receiver_idents = [f"r{i}" for i in range(len(receivers))]

    await _connect(sender, "sender", room_name)
    for room, ident in zip(receivers, receiver_idents):
        await _connect(room, ident, room_name)
    await _ensure_all_connected([sender, *receivers])
    await _ensure_visible(sender, receiver_idents)

    collectors = [_DataCollector(room, sender_identity="sender") for room in receivers]
    received_futures = [
        _expect_event(
            room,
            "data_received",
            predicate=lambda packet: (
                packet.participant is not None and packet.participant.identity == "sender"
            ),
        )
        for room in receivers
    ]

    payload = b"hello everyone"
    await sender.local_participant.publish_data(payload)

    await asyncio.gather(*(_await_event(f) for f in received_futures))
    for ident, collector in zip(receiver_idents, collectors):
        assert collector.payloads() == [payload], f"{ident} payloads mismatch"

    await asyncio.gather(sender.disconnect(), *(r.disconnect() for r in receivers))


@skip_if_no_credentials()
@pytest.mark.asyncio
async def test_data_topic_passthrough() -> None:
    """Topic field is preserved end-to-end and observable by every receiver."""
    room_name = unique_room_name("py-dc-topic")

    sender = rtc.Room()
    r1 = rtc.Room()
    r2 = rtc.Room()

    await _connect(sender, "sender", room_name)
    await _connect(r1, "r1", room_name)
    await _connect(r2, "r2", room_name)
    await _ensure_all_connected([sender, r1, r2])
    await _ensure_visible(sender, ["r1", "r2"])

    r1_collector = _DataCollector(r1, sender_identity="sender")
    r2_collector = _DataCollector(r2, sender_identity="sender")

    # Send three messages: two on "chat", one on "telemetry".
    messages = [
        (b"chat-1", "chat"),
        (b"telemetry-1", "telemetry"),
        (b"chat-2", "chat"),
    ]

    def _all_received(collector: _DataCollector) -> bool:
        return len(collector.packets) >= len(messages)

    for payload, topic in messages:
        await sender.local_participant.publish_data(payload, topic=topic)

    await _wait_until(
        lambda: _all_received(r1_collector) and _all_received(r2_collector),
        message="receivers did not get all topic messages",
    )

    expected_pairs = [(payload, topic) for payload, topic in messages]
    for collector, ident in [(r1_collector, "r1"), (r2_collector, "r2")]:
        got = list(zip(collector.payloads(), collector.topics()))
        assert got == expected_pairs, f"{ident} mismatch: expected {expected_pairs}, got {got}"

    # Also verify `chat`-only filtering at the consumer side works as expected.
    chat_only_r1 = [p for p in r1_collector.packets if p.topic == "chat"]
    assert [p.data for p in chat_only_r1] == [b"chat-1", b"chat-2"]

    await asyncio.gather(sender.disconnect(), r1.disconnect(), r2.disconnect())


@skip_if_no_credentials()
@pytest.mark.asyncio
async def test_data_targeted_with_topic() -> None:
    """Targeted send carries the topic; non-targets receive nothing."""
    room_name = unique_room_name("py-dc-targeted-topic")

    sender = rtc.Room()
    target = rtc.Room()
    other = rtc.Room()

    await _connect(sender, "sender", room_name)
    await _connect(target, "target", room_name)
    await _connect(other, "other", room_name)
    await _ensure_all_connected([sender, target, other])
    await _ensure_visible(sender, ["target", "other"])

    target_collector = _DataCollector(target, sender_identity="sender")
    other_collector = _DataCollector(other, sender_identity="sender")

    target_got = _expect_event(
        target,
        "data_received",
        predicate=lambda packet: (
            packet.participant is not None and packet.participant.identity == "sender"
        ),
    )

    payload = b"private ping"
    topic = "private"
    await sender.local_participant.publish_data(
        payload, destination_identities=["target"], topic=topic
    )

    await _await_event(target_got)
    assert target_collector.payloads() == [payload]
    assert target_collector.topics() == [topic]
    await _assert_no_data(other, other_collector)

    await asyncio.gather(sender.disconnect(), target.disconnect(), other.disconnect())
