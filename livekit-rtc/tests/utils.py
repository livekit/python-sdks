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
from typing import Callable, TypeVar

import pytest

from livekit import api

T = TypeVar("T")

_REQUIRED_ENV_VARS = ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")


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
