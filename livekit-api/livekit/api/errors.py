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

from __future__ import annotations

from typing import Dict, Optional


class ServerError(Exception):
    def __init__(
        self,
        code: str,
        msg: str,
        *,
        status: int,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        self._code = code
        self._msg = msg
        self._status = status
        self._metadata = metadata or {}

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._msg

    @property
    def status(self) -> int:
        """HTTP status code"""
        return self._status

    @property
    def metadata(self) -> Dict[str, str]:
        """Server-provided error metadata"""
        return self._metadata

    def __str__(self) -> str:
        result = f"ServerError(code={self.code}, message={self.message}, status={self.status}"
        if self.metadata:
            result += f", metadata={self.metadata}"
        result += ")"
        return result


class ServerErrorCode:
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
