from __future__ import annotations

import inspect
import os
import pytest

from livekit import rtc
from livekit.rtc import _ffi_client
from livekit.rtc.participant import LocalParticipant
from livekit.rtc._proto import ffi_pb2 as proto_ffi
from livekit.rtc._proto import handle_pb2 as proto_handle
from livekit.rtc._proto import participant_pb2 as proto_participant


def _create_local_participant() -> LocalParticipant:
    room = rtc.Room()
    return LocalParticipant(
        room._room_queue,
        proto_participant.OwnedParticipant(
            handle=proto_handle.FfiOwnedHandle(id=0),
            info=proto_participant.ParticipantInfo(
                sid="PA_TEST",
                identity="tester",
            ),
        ),
    )


def test_publish_data_parameter_default_is_none() -> None:
    sig = inspect.signature(LocalParticipant.publish_data)
    param = sig.parameters["destination_identities"]
    assert param.default is None


@pytest.mark.asyncio
async def test_publish_data_accepts_none_and_sequences(monkeypatch: pytest.MonkeyPatch) -> None:
    lp = _create_local_participant()
    captured_requests: list[proto_ffi.FfiRequest] = []

    class _MockFfiClient:
        def __init__(self) -> None:
            self.queue: _ffi_client.FfiQueue[proto_ffi.FfiEvent] = _ffi_client.FfiQueue()
            self._pid = os.getpid()

        def request(self, req: proto_ffi.FfiRequest) -> proto_ffi.FfiResponse:
            captured_requests.append(req)
            resp = proto_ffi.FfiResponse()
            resp.publish_data.async_id = 42

            ev = proto_ffi.FfiEvent()
            ev.publish_data.async_id = 42
            self.queue.put(ev)
            return resp

    mock_client = _MockFfiClient()
    monkeypatch.setattr(_ffi_client.FfiClient, "_instance", mock_client)

    # 1. Default (omitted)
    await lp.publish_data(b"msg1")
    assert list(captured_requests[-1].publish_data.destination_identities) == []

    # 2. Explicit None
    await lp.publish_data(b"msg2", destination_identities=None)
    assert list(captured_requests[-1].publish_data.destination_identities) == []

    # 3. Explicit empty list
    await lp.publish_data(b"msg3", destination_identities=[])
    assert list(captured_requests[-1].publish_data.destination_identities) == []

    # 4. List of identities
    await lp.publish_data(b"msg4", destination_identities=["user1", "user2"])
    assert list(captured_requests[-1].publish_data.destination_identities) == ["user1", "user2"]

    # 5. Tuple of identities
    await lp.publish_data(b"msg5", destination_identities=("user3", "user4"))
    assert list(captured_requests[-1].publish_data.destination_identities) == ["user3", "user4"]
