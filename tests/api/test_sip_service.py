import asyncio
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from google.protobuf.duration_pb2 import Duration
from livekit import api


@pytest.mark.parametrize("operation", ["create", "transfer"])
@pytest.mark.parametrize(
    ("timeout", "expected"),
    [(None, 3.75), (3.5, 3.75), (4.0, 4.0)],
    ids=["default", "clamp", "longer"],
)
def test_fractional_ringing_timeout(operation, timeout, expected):
    async def run():
        response = MagicMock(status=200, read=AsyncMock(return_value=b""))
        session = MagicMock(spec=aiohttp.ClientSession)
        session.post.return_value.__aenter__.return_value = response
        sdk = api.LiveKitAPI.with_token("unused", "http://localhost:7880", session=session)
        ringing = Duration(seconds=1, nanos=750_000_000)

        if operation == "create":
            await sdk.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(wait_until_answered=True, ringing_timeout=ringing),
                timeout=timeout,
            )
        else:
            await sdk.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(ringing_timeout=ringing), timeout=timeout
            )

        session.post.assert_called_once()
        assert session.post.call_args.kwargs["timeout"].total == expected

    asyncio.run(run())
