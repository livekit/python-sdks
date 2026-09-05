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

    handle = _incoming_chain(lp)
    result = await handle(RpcInvocationData("req-1", "alice", "{}", 5.0, method="greet"))

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
    handle = _incoming_chain(lp)

    with pytest.raises(rtc.RpcError) as info:
        await handle(RpcInvocationData("req-1", "alice", "{}", 5.0, method="missing"))
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
    handle = _incoming_chain(lp)

    # the raw handler exception reaches interceptors; the SDK maps it to APPLICATION_ERROR
    # only when building the response, outside the chain
    with pytest.raises(ValueError):
        await handle(RpcInvocationData("r1", "alice", "{}", 5.0, method="boom"))
    assert isinstance(seen[-1], ValueError)

    with pytest.raises(rtc.RpcError) as info:
        await handle(RpcInvocationData("r2", "alice", "{}", 0.01, method="slow"))
    assert info.value.code == rtc.RpcError.ErrorCode.RESPONSE_TIMEOUT
    assert seen[-1] is info.value

    assert await handle(RpcInvocationData("r3", "alice", "{}", 5.0, method="sync_ok")) == "sync"


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


def test_invocation_data_defaults_keep_positional_construction() -> None:
    # existing code constructs it positionally without `method`
    data = RpcInvocationData("req", "alice", "{}", 2.5)
    assert data.method == ""


def _incoming_chain(lp: LocalParticipant) -> IncomingRpcNext:
    from livekit.rtc.rpc import _chain_incoming

    return _chain_incoming(list(lp._rpc_interceptors), lp._invoke_rpc_handler)
