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

import asyncio
from typing import Any, List, Optional, Union

import pytest

from livekit.api.sip_service import SipService
from livekit.protocol.models import ListUpdate

# (method, list argument, field of request.update)
LIST_FIELDS = [
    ("update_inbound_trunk_fields", "numbers", "numbers"),
    ("update_inbound_trunk_fields", "allowed_addresses", "allowed_addresses"),
    ("update_inbound_trunk_fields", "allowed_numbers", "allowed_numbers"),
    ("update_outbound_trunk_fields", "numbers", "numbers"),
    ("update_dispatch_rule_fields", "trunk_ids", "trunk_ids"),
]


def _sent_update(method: str, arg: str, value: Optional[Union[ListUpdate, List[str]]]) -> Any:
    sent: List[Any] = []

    async def request(
        service: str, rpc: str, data: Any, headers: Any, response_class: Any, **kwargs: Any
    ) -> Any:
        sent.append(data)
        return response_class()

    svc = SipService(None, "https://example.livekit.cloud", "key", "secret")  # type: ignore[arg-type]
    svc._client.request = request  # type: ignore[method-assign, assignment]
    asyncio.run(getattr(svc, method)("ID_1", **{arg: value}))
    return sent[0].update


@pytest.mark.parametrize(("method", "arg", "field"), LIST_FIELDS)
def test_list_update_clear_is_sent(method: str, arg: str, field: str) -> None:
    update = _sent_update(method, arg, ListUpdate(clear=True))
    assert getattr(update, field) == ListUpdate(clear=True)


@pytest.mark.parametrize(("method", "arg", "field"), LIST_FIELDS)
def test_list_and_list_update_values_are_still_sent(method: str, arg: str, field: str) -> None:
    assert getattr(_sent_update(method, arg, ["a", "b"]), field) == ListUpdate(set=["a", "b"])
    change = ListUpdate(add=["a"], remove=["b"])
    assert getattr(_sent_update(method, arg, change), field) == change


@pytest.mark.parametrize(("method", "arg", "field"), LIST_FIELDS)
def test_omitted_list_is_not_sent(method: str, arg: str, field: str) -> None:
    assert not _sent_update(method, arg, None).HasField(field)
