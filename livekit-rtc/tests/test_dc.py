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
from typing import Optional

import pytest

from livekit import rtc

from utils import (  # type: ignore[import-not-found]
    await_event,
    connect_room,
    ensure_participants_visible,
    ensure_rooms_all_connected,
    expect_room_event,
    skip_if_no_credentials,
    unique_room_name,
    wait_until,
)


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


@skip_if_no_credentials()  # type: ignore[untyped-decorator]
@pytest.mark.asyncio
async def test_data_one_to_one() -> None:
    """sender targets a single identity; only that identity receives."""
    room_name = unique_room_name("py-dc-1to1")

    sender = rtc.Room()
    receiver = rtc.Room()
    bystander = rtc.Room()

    await connect_room("sender", room_name, room=sender)
    await connect_room("receiver", room_name, room=receiver)
    await connect_room("bystander", room_name, room=bystander)
    await ensure_rooms_all_connected([sender, receiver, bystander])
    await ensure_participants_visible(sender, ["receiver", "bystander"])

    receiver_collector = _DataCollector(receiver, sender_identity="sender")
    bystander_collector = _DataCollector(bystander, sender_identity="sender")

    receiver_got = expect_room_event(
        receiver,
        "data_received",
        predicate=lambda packet: (
            packet.participant is not None and packet.participant.identity == "sender"
        ),
    )

    payload = b"hello receiver"
    await sender.local_participant.publish_data(payload, destination_identities=["receiver"])

    await await_event(receiver_got)
    assert receiver_collector.payloads() == [payload]
    await _assert_no_data(bystander, bystander_collector)

    await asyncio.gather(sender.disconnect(), receiver.disconnect(), bystander.disconnect())


@skip_if_no_credentials()  # type: ignore[untyped-decorator]
@pytest.mark.asyncio
async def test_data_one_to_many_targeted() -> None:
    """sender targets a subset of identities; only that subset receives."""
    room_name = unique_room_name("py-dc-1tomany")

    sender = rtc.Room()
    r1 = rtc.Room()
    r2 = rtc.Room()
    excluded = rtc.Room()

    await connect_room("sender", room_name, room=sender)
    await connect_room("r1", room_name, room=r1)
    await connect_room("r2", room_name, room=r2)
    await connect_room("excluded", room_name, room=excluded)
    await ensure_rooms_all_connected([sender, r1, r2, excluded])
    await ensure_participants_visible(sender, ["r1", "r2", "excluded"])

    r1_collector = _DataCollector(r1, sender_identity="sender")
    r2_collector = _DataCollector(r2, sender_identity="sender")
    excluded_collector = _DataCollector(excluded, sender_identity="sender")

    r1_got = expect_room_event(
        r1,
        "data_received",
        predicate=lambda packet: (
            packet.participant is not None and packet.participant.identity == "sender"
        ),
    )
    r2_got = expect_room_event(
        r2,
        "data_received",
        predicate=lambda packet: (
            packet.participant is not None and packet.participant.identity == "sender"
        ),
    )

    payload = b"hello selected"
    await sender.local_participant.publish_data(payload, destination_identities=["r1", "r2"])

    await asyncio.gather(await_event(r1_got), await_event(r2_got))
    assert r1_collector.payloads() == [payload]
    assert r2_collector.payloads() == [payload]
    await _assert_no_data(excluded, excluded_collector)

    await asyncio.gather(
        sender.disconnect(), r1.disconnect(), r2.disconnect(), excluded.disconnect()
    )


@skip_if_no_credentials()  # type: ignore[untyped-decorator]
@pytest.mark.asyncio
async def test_data_broadcast() -> None:
    """Empty `destination_identities` broadcasts to every other participant."""
    room_name = unique_room_name("py-dc-broadcast")

    sender = rtc.Room()
    receivers = [rtc.Room() for _ in range(3)]
    receiver_idents = [f"r{i}" for i in range(len(receivers))]

    await connect_room("sender", room_name, room=sender)
    for room, ident in zip(receivers, receiver_idents):
        await connect_room(ident, room_name, room=room)
    await ensure_rooms_all_connected([sender, *receivers])
    await ensure_participants_visible(sender, receiver_idents)

    collectors = [_DataCollector(room, sender_identity="sender") for room in receivers]
    received_futures = [
        expect_room_event(
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

    await asyncio.gather(*(await_event(f) for f in received_futures))
    for ident, collector in zip(receiver_idents, collectors):
        assert collector.payloads() == [payload], f"{ident} payloads mismatch"

    await asyncio.gather(sender.disconnect(), *(r.disconnect() for r in receivers))


@skip_if_no_credentials()  # type: ignore[untyped-decorator]
@pytest.mark.asyncio
async def test_data_topic_passthrough() -> None:
    """Topic field is preserved end-to-end and observable by every receiver."""
    room_name = unique_room_name("py-dc-topic")

    sender = rtc.Room()
    r1 = rtc.Room()
    r2 = rtc.Room()

    await connect_room("sender", room_name, room=sender)
    await connect_room("r1", room_name, room=r1)
    await connect_room("r2", room_name, room=r2)
    await ensure_rooms_all_connected([sender, r1, r2])
    await ensure_participants_visible(sender, ["r1", "r2"])

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

    await wait_until(
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


@skip_if_no_credentials()  # type: ignore[untyped-decorator]
@pytest.mark.asyncio
async def test_data_targeted_with_topic() -> None:
    """Targeted send carries the topic; non-targets receive nothing."""
    room_name = unique_room_name("py-dc-targeted-topic")

    sender = rtc.Room()
    target = rtc.Room()
    other = rtc.Room()

    await connect_room("sender", room_name, room=sender)
    await connect_room("target", room_name, room=target)
    await connect_room("other", room_name, room=other)
    await ensure_rooms_all_connected([sender, target, other])
    await ensure_participants_visible(sender, ["target", "other"])

    target_collector = _DataCollector(target, sender_identity="sender")
    other_collector = _DataCollector(other, sender_identity="sender")

    target_got = expect_room_event(
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

    await await_event(target_got)
    assert target_collector.payloads() == [payload]
    assert target_collector.topics() == [topic]
    await _assert_no_data(other, other_collector)

    await asyncio.gather(sender.disconnect(), target.disconnect(), other.disconnect())
