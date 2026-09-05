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

"""Unit tests for RPC interceptors.

These exercise the interceptor chain around `perform_rpc` and the incoming handler
dispatch without a server: the FFI call is replaced by a stub, and the participant is
built without a room. No credentials required.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import pytest

from livekit import rtc
from livekit.rtc.participant import LocalParticipant
from livekit.rtc.rpc import IncomingRpcNext, OutgoingRpcNext, RpcCallInfo, RpcInvocationData


def _participant() -> LocalParticipant:
    # bypass __init__: no FFI handle is needed for the interceptor chain itself
    lp = LocalParticipant.__new__(LocalParticipant)
    lp._rpc_handlers = {}
    lp._rpc_interceptors = []
    return lp


class Recorder(rtc.RpcInterceptor):
    def __init__(self, name: str, log: list[str]) -> None:
        self.name = name
        self.log = log

    async def intercept_outgoing(self, call: RpcCallInfo, next: OutgoingRpcNext) -> str:
        self.log.append(f"{self.name}:out:{call.method}>")
        try:
            return await next(call)
        finally:
            self.log.append(f"{self.name}:out:{call.method}<")

    async def intercept_incoming(
        self, invocation: RpcInvocationData, next: IncomingRpcNext
    ) -> Optional[str]:
        self.log.append(f"{self.name}:in:{invocation.method}>")
        try:
            return await next(invocation)
        finally:
            self.log.append(f"{self.name}:in:{invocation.method}<")


async def test_outgoing_interceptors_wrap_the_call_in_registration_order() -> None:
    lp = _participant()
    log: list[str] = []
    calls: list[RpcCallInfo] = []

    async def fake_ffi(call: RpcCallInfo) -> str:
        calls.append(call)
        log.append("ffi")
        return "pong"

    lp._perform_rpc_ffi = fake_ffi  # type: ignore[method-assign]
    lp.add_rpc_interceptor(Recorder("a", log))
    lp.add_rpc_interceptor(Recorder("b", log))

    result = await lp.perform_rpc(
        destination_identity="bob", method="ping", payload="{}", response_timeout=3.0
    )

    assert result == "pong"
    assert log == ["a:out:ping>", "b:out:ping>", "ffi", "b:out:ping<", "a:out:ping<"]
    assert calls == [
        RpcCallInfo(
            destination_identity="bob",
            method="ping",
            payload="{}",
            response_timeout=3.0,
            max_round_trip_latency=None,
        )
    ]


async def test_outgoing_interceptor_sees_remote_errors_and_can_rewrite_the_call() -> None:
    lp = _participant()
    seen: list[BaseException] = []

    async def fake_ffi(call: RpcCallInfo) -> str:
        assert call.payload == '{"traced": true}'
        raise rtc.RpcError._built_in(rtc.RpcError.ErrorCode.RECIPIENT_NOT_FOUND)

    class Rewrite(rtc.RpcInterceptor):
        async def intercept_outgoing(self, call: RpcCallInfo, next: OutgoingRpcNext) -> str:
            try:
                return await next(
                    RpcCallInfo(call.destination_identity, call.method, '{"traced": true}')
                )
            except rtc.RpcError as e:
                seen.append(e)
                raise

    lp._perform_rpc_ffi = fake_ffi  # type: ignore[method-assign]
    lp.add_rpc_interceptor(Rewrite())

    with pytest.raises(rtc.RpcError) as info:
        await lp.perform_rpc(destination_identity="nobody", method="ping", payload="{}")
    assert info.value.code == rtc.RpcError.ErrorCode.RECIPIENT_NOT_FOUND
    assert seen == [info.value]


async def test_incoming_interceptors_wrap_the_handler_and_see_the_method() -> None:
    lp = _participant()
    log: list[str] = []
    lp.add_rpc_interceptor(Recorder("a", log))

    async def greet(data: RpcInvocationData) -> str:
        assert data.method == "greet"
        return f"hello {data.caller_identity}"

    lp._rpc_handlers["greet"] = greet  # register without the FFI round trip

    result = await lp._run_incoming_chain(
        RpcInvocationData("req-1", "alice", "{}", 5.0, method="greet")
    )

    assert result == "hello alice"
    assert log == ["a:in:greet>", "a:in:greet<"]


async def test_incoming_chain_reports_unsupported_method_through_interceptors() -> None:
    lp = _participant()
    seen: list[rtc.RpcError] = []

    class Observe(rtc.RpcInterceptor):
        async def intercept_incoming(
            self, invocation: RpcInvocationData, next: IncomingRpcNext
        ) -> Optional[str]:
            try:
                return await next(invocation)
            except rtc.RpcError as e:
                seen.append(e)
                raise

    lp.add_rpc_interceptor(Observe())

    with pytest.raises(rtc.RpcError) as info:
        await lp._run_incoming_chain(
            RpcInvocationData("req-1", "alice", "{}", 5.0, method="missing")
        )
    assert info.value.code == rtc.RpcError.ErrorCode.UNSUPPORTED_METHOD
    assert seen == [info.value]


async def test_incoming_chain_surfaces_handler_exceptions_and_timeouts() -> None:
    lp = _participant()
    seen: list[BaseException] = []

    class Observe(rtc.RpcInterceptor):
        async def intercept_incoming(
            self, invocation: RpcInvocationData, next: IncomingRpcNext
        ) -> Optional[str]:
            try:
                return await next(invocation)
            except BaseException as e:
                seen.append(e)
                raise

    lp.add_rpc_interceptor(Observe())

    async def boom(data: RpcInvocationData) -> str:
        raise ValueError("bad input")

    async def slow(data: RpcInvocationData) -> str:
        await asyncio.sleep(1.0)
        return "late"

    def sync_ok(data: RpcInvocationData) -> str:
        return "sync"

    lp._rpc_handlers.update({"boom": boom, "slow": slow, "sync_ok": sync_ok})

    # the raw handler exception reaches interceptors; the SDK maps it to APPLICATION_ERROR
    # only when building the response, outside the chain
    with pytest.raises(ValueError):
        await lp._run_incoming_chain(RpcInvocationData("r1", "alice", "{}", 5.0, method="boom"))
    assert isinstance(seen[-1], ValueError)

    # the deadline cancels the chain (interceptors see the cancellation) and the caller
    # gets RESPONSE_TIMEOUT
    with pytest.raises(rtc.RpcError) as info:
        await lp._run_incoming_chain(RpcInvocationData("r2", "alice", "{}", 0.01, method="slow"))
    assert info.value.code == rtc.RpcError.ErrorCode.RESPONSE_TIMEOUT
    assert isinstance(seen[-1], asyncio.CancelledError)

    result = await lp._run_incoming_chain(
        RpcInvocationData("r3", "alice", "{}", 5.0, method="sync_ok")
    )
    assert result == "sync"


@pytest.mark.parametrize("delay_position", ["before_next", "after_next"])
async def test_response_deadline_covers_interceptor_time(delay_position: str) -> None:
    """An interceptor that burns the deadline, on either side of ``next``, times the call out
    instead of handing the handler a fresh full timeout."""
    lp = _participant()
    handler_ran = asyncio.Event()

    class Slow(rtc.RpcInterceptor):
        async def intercept_incoming(
            self, invocation: RpcInvocationData, next: IncomingRpcNext
        ) -> Optional[str]:
            if delay_position == "before_next":
                await asyncio.sleep(1.0)
            result = await next(invocation)
            if delay_position == "after_next":
                await asyncio.sleep(1.0)
            return result

    async def fast(data: RpcInvocationData) -> str:
        handler_ran.set()
        return "fast"

    lp.add_rpc_interceptor(Slow())
    lp._rpc_handlers["fast"] = fast

    start = asyncio.get_running_loop().time()
    with pytest.raises(rtc.RpcError) as info:
        await lp._run_incoming_chain(RpcInvocationData("r1", "alice", "{}", 0.05, method="fast"))
    assert info.value.code == rtc.RpcError.ErrorCode.RESPONSE_TIMEOUT
    assert asyncio.get_running_loop().time() - start < 0.5
    assert handler_ran.is_set() == (delay_position == "after_next")


async def test_timeout_raised_inside_the_chain_is_not_the_response_deadline() -> None:
    """An interceptor (or handler) whose own I/O times out raises TimeoutError well before
    the response deadline. That is an application failure, not RESPONSE_TIMEOUT."""
    lp = _participant()

    class UpstreamTimesOut(rtc.RpcInterceptor):
        async def intercept_incoming(
            self, invocation: RpcInvocationData, next: IncomingRpcNext
        ) -> Optional[str]:
            raise asyncio.TimeoutError("upstream lookup timed out")

    lp.add_rpc_interceptor(UpstreamTimesOut())
    lp._rpc_handlers["m"] = lambda data: "unused"

    # propagates as the original TimeoutError, which _handle_rpc_method_invocation maps to
    # APPLICATION_ERROR like any other handler exception
    with pytest.raises(asyncio.TimeoutError) as info:
        await lp._run_incoming_chain(RpcInvocationData("r1", "alice", "{}", 5.0, method="m"))
    assert not isinstance(info.value, rtc.RpcError)
    assert str(info.value) == "upstream lookup timed out"

    async def handler_times_out(data: RpcInvocationData) -> str:
        raise asyncio.TimeoutError("db timed out")

    lp2 = _participant()
    lp2._rpc_handlers["m"] = handler_times_out
    with pytest.raises(asyncio.TimeoutError):
        await lp2._run_incoming_chain(RpcInvocationData("r2", "alice", "{}", 5.0, method="m"))


async def test_outside_cancellation_maps_to_recipient_disconnected() -> None:
    lp = _participant()
    started = asyncio.Event()

    async def hang(data: RpcInvocationData) -> str:
        started.set()
        await asyncio.sleep(10)
        return "never"

    lp._rpc_handlers["hang"] = hang
    task = asyncio.ensure_future(
        lp._run_incoming_chain(RpcInvocationData("r1", "alice", "{}", 5.0, method="hang"))
    )
    await started.wait()
    task.cancel()  # what the room does when it disconnects mid-invocation
    with pytest.raises(rtc.RpcError) as info:
        await task
    assert info.value.code == rtc.RpcError.ErrorCode.RECIPIENT_DISCONNECTED


async def test_add_and_remove_interceptors() -> None:
    lp = _participant()
    log: list[str] = []
    a = Recorder("a", log)

    lp.add_rpc_interceptor(a)
    lp.add_rpc_interceptor(a)  # duplicate add is a no-op
    assert lp._rpc_interceptors == [a]

    lp.remove_rpc_interceptor(a)
    lp.remove_rpc_interceptor(a)  # removing twice is fine
    assert lp._rpc_interceptors == []

    async def fake_ffi(call: RpcCallInfo) -> str:
        return "ok"

    lp._perform_rpc_ffi = fake_ffi  # type: ignore[method-assign]
    assert await lp.perform_rpc(destination_identity="bob", method="m", payload="") == "ok"
    assert log == []


def test_registration_is_by_identity_not_equality() -> None:
    class Equalish(rtc.RpcInterceptor):
        def __eq__(self, other: object) -> bool:
            return isinstance(other, Equalish)

        def __hash__(self) -> int:
            return 1

    lp = _participant()
    first, second = Equalish(), Equalish()
    assert first == second and first is not second

    lp.add_rpc_interceptor(first)
    lp.add_rpc_interceptor(second)
    assert len(lp._rpc_interceptors) == 2, "distinct interceptors that compare equal coexist"

    lp.remove_rpc_interceptor(second)
    assert len(lp._rpc_interceptors) == 1
    assert lp._rpc_interceptors[0] is first, "only the exact instance is removed"


def test_invocation_data_defaults_keep_positional_construction() -> None:
    # existing code constructs it positionally without `method`
    data = RpcInvocationData("req", "alice", "{}", 2.5)
    assert data.method == ""
