# Copyright 2026 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Shared helpers used across the livekit-rtc test suite."""

from __future__ import annotations

import asyncio
import os
import uuid
from typing import Any, Callable, Optional, TypeVar

import pytest

from livekit import api, rtc
from livekit.rtc.room import EventTypes

T = TypeVar("T")

_REQUIRED_ENV_VARS = ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")
DEFAULT_WAIT_TIMEOUT = 30.0
DEFAULT_WAIT_INTERVAL = 0.1


def skip_if_no_credentials() -> pytest.MarkDecorator:
    """pytest mark that skips when any LiveKit credentials env var is missing."""
    missing = [var for var in _REQUIRED_ENV_VARS if not os.getenv(var)]
    return pytest.mark.skipif(
        bool(missing), reason=f"Missing environment variables: {', '.join(missing)}"
    )


def create_token(identity: str, room_name: str) -> str:
    """Build a room-join JWT for the given identity/room."""
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
    """Suffix the base with a short random token so concurrent runs don't collide."""
    return f"{base}-{uuid.uuid4().hex[:8]}"


async def assert_eventually(
    condition: Callable[[], T],
    timeout: float = 15.0,
    interval: float = 0.1,
    message: str = "Condition not met within timeout",
) -> T:
    """Poll `condition()` until it returns a truthy value or `timeout` elapses."""
    deadline = asyncio.get_event_loop().time() + timeout
    last_result: T | None = None
    while asyncio.get_event_loop().time() < deadline:
        last_result = condition()
        if last_result:
            return last_result
        await asyncio.sleep(interval)
    raise AssertionError(f"{message} (last result: {last_result})")


async def wait_until(
    predicate: Callable[[], bool],
    *,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
    interval: float = DEFAULT_WAIT_INTERVAL,
    message: str = "condition not met",
) -> None:
    """Poll `predicate()` until it returns True or `timeout` elapses."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return
        await asyncio.sleep(interval)
    raise AssertionError(f"timeout waiting: {message}")


async def ensure_rooms_all_connected(
    rooms: list[rtc.Room],
    *,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
) -> None:
    """Wait until every `Room` in `rooms` reaches CONN_CONNECTED."""
    await wait_until(
        lambda: all(r.connection_state == rtc.ConnectionState.CONN_CONNECTED for r in rooms),
        timeout=timeout,
        message="not all rooms reached CONN_CONNECTED",
    )


async def ensure_participants_visible(
    observer: rtc.Room,
    identities: list[str],
    *,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
) -> None:
    """Wait until `observer` sees every identity in `identities` as a remote participant."""

    def _all_visible() -> bool:
        seen = {p.identity for p in observer.remote_participants.values()}
        return all(ident in seen for ident in identities)

    await wait_until(
        _all_visible,
        timeout=timeout,
        message=(
            f"not all identities visible to {observer.local_participant.identity}: {identities}"
        ),
    )


def expect_room_event(
    room: rtc.Room,
    event: EventTypes,
    predicate: Optional[Callable[..., bool]] = None,
) -> "asyncio.Future[tuple[Any, ...]]":
    """Register a one-shot handler for `event` returning a `Future` resolved with the event args.

    `predicate` (if given) filters events; the handler is unregistered after the future resolves.
    """
    loop = asyncio.get_running_loop()
    fut: "asyncio.Future[tuple[Any, ...]]" = loop.create_future()

    def _on_event(*args: Any, **kwargs: Any) -> None:
        if fut.done():
            return
        if predicate is None or predicate(*args, **kwargs):
            fut.set_result(args)
            room.off(event, _on_event)

    room.on(event, _on_event)
    return fut


async def await_event(
    fut: "asyncio.Future[Any]",
    timeout: float = DEFAULT_WAIT_TIMEOUT,
) -> None:
    """Await a future from `expect_room_event` with a descriptive timeout failure."""
    try:
        await asyncio.wait_for(fut, timeout=timeout)
    except asyncio.TimeoutError as e:
        raise AssertionError("timed out waiting for event") from e


async def connect_room(
    identity: str,
    room_name: str,
    *,
    room: Optional[rtc.Room] = None,
    options: Optional[rtc.RoomOptions] = None,
) -> rtc.Room:
    """Build a token for `identity`/`room_name` and connect.

    If `room` is provided it is connected in place; otherwise a fresh `rtc.Room`
    is created. Returns the connected room.
    """
    if room is None:
        room = rtc.Room()
    url = os.environ["LIVEKIT_URL"]
    token = create_token(identity, room_name)
    if options is None:
        await room.connect(url, token)
    else:
        await room.connect(url, token, options=options)
    return room


async def ensure_track_subscribed(
    room: rtc.Room,
    track_sid: str,
    *,
    timeout: float = DEFAULT_WAIT_TIMEOUT,
) -> rtc.RemoteTrackPublication:
    """Wait until some remote participant in `room` has subscribed to `track_sid`."""
    holder: dict[str, rtc.RemoteTrackPublication] = {}

    def _has_subscribed() -> bool:
        for participant in room.remote_participants.values():
            pub = participant.track_publications.get(track_sid)
            if pub is not None and pub.subscribed and pub.track is not None:
                holder["pub"] = pub
                return True
        return False

    await wait_until(
        _has_subscribed,
        timeout=timeout,
        message=f"room did not subscribe to track {track_sid}",
    )
    return holder["pub"]


async def publish_dummy_video(
    source: rtc.VideoSource,
    stop_event: asyncio.Event,
    *,
    width: int = 320,
    height: int = 180,
    fps: int = 15,
) -> None:
    """Continuously capture ARGB frames into `source` until `stop_event` is set.

    Pixel values vary frame-to-frame so encryption tests see distinct ciphertexts.
    """
    pixel_count = width * height
    frame_idx = 0
    while not stop_event.is_set():
        fill = frame_idx % 256
        pixel = bytes((255, fill, (fill + 85) % 256, (fill + 170) % 256))
        buf = pixel * pixel_count
        frame = rtc.VideoFrame(width, height, rtc.VideoBufferType.ARGB, buf)
        source.capture_frame(frame)
        frame_idx += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=1.0 / fps)
        except asyncio.TimeoutError:
            pass
