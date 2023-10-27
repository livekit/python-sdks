# Copyright 2023 LiveKit, Inc.
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

from typing import Dict, Type, TypeVar

import aiohttp
from google.protobuf.message import Message

DEFAULT_PREFIX = "/twirp"


class TwirpError(Exception):
    def __init__(self, code: str, msg: str) -> None:
        self.code = code
        self.msg = msg


class TwirpErrorCode:
    CANCELED = "canceled"
    UNKNOWN = "unknown"
    INVALID_ARGUMENT = "invalid_argument"
    MALFORMED = "malformed"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    NOT_FOUND = "not_found"
    BAD_ROUTE = "bad_route"
    ALREADY_EXISTS = "already_exists"
    PERMISSION_DENIED = "permission_denied"
    UNAUTHENTICATED = "unauthenticated"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    FAILED_PRECONDITION = "failed_precondition"
    ABORTED = "aborted"
    OUT_OF_RANGE = "out_of_range"
    UNIMPLEMENTED = "unimplemented"
    INTERNAL = "internal"
    UNAVAILABLE = "unavailable"
    DATA_LOSS = "dataloss"


T = TypeVar("T", bound=Message)


class TwirpClient:
    def __init__(self, host: str, pkg: str, prefix: str = DEFAULT_PREFIX) -> None:
        self.host = host
        self.pkg = pkg
        self.prefix = prefix
        self.session = aiohttp.ClientSession()

    async def request(
        self,
        service: str,
        method: str,
        data: Message,
        headers: Dict[str, str],
        response_class: Type[T],
    ) -> T:
        url = f"{self.host}/{self.prefix}/{self.pkg}.{service}/{method}"
        headers["Content-Type"] = "application/protobuf"

        serialized_data = data.SerializeToString()
        async with self.session.post(
            url, headers=headers, data=serialized_data
        ) as resp:
            if resp.status == 200:
                return response_class.FromString(await resp.read())
            else:
                # when we have an error, Twirp always encode it in json
                error_data = await resp.json()
                raise TwirpError(error_data["code"], error_data["msg"])

    async def aclose(self):
        await self.session.close()
