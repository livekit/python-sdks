"""Unit tests for BroadcastQueue subscriber removal.

``Room._listen_task`` calls ``BroadcastQueue.join()`` after every event, so a
subscriber that goes away (for example a cancelled ``publish_track``) must not
leave that join waiting on events nobody will finish.
"""

from __future__ import annotations

import asyncio

import pytest

from livekit.rtc._utils import BroadcastQueue


async def _join_finishes(queue: BroadcastQueue, timeout: float = 1.0) -> bool:
    try:
        await asyncio.wait_for(queue.join(), timeout)
    except asyncio.TimeoutError:
        return False
    return True


@pytest.mark.asyncio
async def test_join_waits_for_a_subscriber_that_has_not_finished() -> None:
    broadcast: BroadcastQueue[int] = BroadcastQueue()
    subscriber = broadcast.subscribe()
    broadcast.put_nowait(1)

    assert not await _join_finishes(broadcast, timeout=0.1)

    await subscriber.get()
    subscriber.task_done()
    assert await _join_finishes(broadcast)


@pytest.mark.asyncio
async def test_unsubscribe_releases_a_join_waiting_on_a_queued_event() -> None:
    broadcast: BroadcastQueue[int] = BroadcastQueue()
    subscriber = broadcast.subscribe()
    broadcast.put_nowait(1)

    joiner = asyncio.create_task(broadcast.join())
    await asyncio.sleep(0)
    assert not joiner.done()

    broadcast.unsubscribe(subscriber)

    await asyncio.wait_for(joiner, 1.0)
    assert broadcast.len_subscribers() == 0


@pytest.mark.asyncio
async def test_unsubscribe_releases_a_join_waiting_on_an_event_that_was_taken() -> None:
    broadcast: BroadcastQueue[int] = BroadcastQueue()
    subscriber = broadcast.subscribe()
    broadcast.put_nowait(1)
    await subscriber.get()  # taken, but the subscriber never calls task_done()

    joiner = asyncio.create_task(broadcast.join())
    await asyncio.sleep(0)
    assert not joiner.done()

    broadcast.unsubscribe(subscriber)

    await asyncio.wait_for(joiner, 1.0)


@pytest.mark.asyncio
async def test_unsubscribe_keeps_other_subscribers_in_the_join() -> None:
    broadcast: BroadcastQueue[int] = BroadcastQueue()
    gone = broadcast.subscribe()
    staying = broadcast.subscribe()
    broadcast.put_nowait(1)

    joiner = asyncio.create_task(broadcast.join())
    await asyncio.sleep(0)
    broadcast.unsubscribe(gone)
    await asyncio.sleep(0.05)
    assert not joiner.done()

    await staying.get()
    staying.task_done()
    await asyncio.wait_for(joiner, 1.0)


@pytest.mark.asyncio
async def test_unsubscribe_after_every_event_is_finished_is_a_no_op() -> None:
    broadcast: BroadcastQueue[int] = BroadcastQueue()
    subscriber = broadcast.subscribe()
    broadcast.put_nowait(1)
    await subscriber.get()
    subscriber.task_done()

    broadcast.unsubscribe(subscriber)

    assert await _join_finishes(broadcast)
