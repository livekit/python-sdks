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

from typing import Optional, Dict, Union, ClassVar
from enum import IntEnum
from ._proto import rpc_pb2 as proto_rpc
from dataclasses import dataclass


@dataclass
class RpcInvocationData:
    """Data passed to method handler for incoming RPC invocations

    Attributes:
        request_id (str): The unique request ID. Will match at both sides of the call, useful for debugging or logging.
        caller_identity (str): The unique participant identity of the caller.
        payload (str): The payload of the request. User-definable format, typically JSON.
        response_timeout (float): The maximum time the caller will wait for a response.
    """

    request_id: str
    caller_identity: str
    payload: str
    response_timeout: float


class RpcError(Exception):
    """
    Specialized error handling for RPC methods.

    Instances of this type, when thrown in a method handler, will have their `message`
    serialized and sent across the wire. The caller will receive an equivalent error on the other side.

    Built-in errors are included (codes 1001-1999) but developers may use the code, message, and data fields to create their own errors.
    """

    class ErrorCode(IntEnum):
        APPLICATION_ERROR = 1500
        CONNECTION_TIMEOUT = 1501
        RESPONSE_TIMEOUT = 1502
        RECIPIENT_DISCONNECTED = 1503
        RESPONSE_PAYLOAD_TOO_LARGE = 1504
        SEND_FAILED = 1505

        UNSUPPORTED_METHOD = 1400
        RECIPIENT_NOT_FOUND = 1401
        REQUEST_PAYLOAD_TOO_LARGE = 1402
        UNSUPPORTED_SERVER = 1403
        UNSUPPORTED_VERSION = 1404

    ErrorMessage: ClassVar[Dict[ErrorCode, str]] = {
        ErrorCode.APPLICATION_ERROR: "Application error in method handler",
        ErrorCode.CONNECTION_TIMEOUT: "Connection timeout",
        ErrorCode.RESPONSE_TIMEOUT: "Response timeout",
        ErrorCode.RECIPIENT_DISCONNECTED: "Recipient disconnected",
        ErrorCode.RESPONSE_PAYLOAD_TOO_LARGE: "Response payload too large",
        ErrorCode.SEND_FAILED: "Failed to send",
        ErrorCode.UNSUPPORTED_METHOD: "Method not supported at destination",
        ErrorCode.RECIPIENT_NOT_FOUND: "Recipient not found",
        ErrorCode.REQUEST_PAYLOAD_TOO_LARGE: "Request payload too large",
        ErrorCode.UNSUPPORTED_SERVER: "RPC not supported by server",
        ErrorCode.UNSUPPORTED_VERSION: "Unsupported RPC version",
    }

    def __init__(
        self,
        code: Union[int, "RpcError.ErrorCode"],
        message: str,
        data: Optional[str] = None,
    ):
        """
        Creates an error object with the given code and message, plus an optional data payload.

        If thrown in an RPC method handler, the error will be sent back to the caller.

        Args:
            code (int): Your error code (Error codes 1001-1999 are reserved for built-in errors)
            message (str): A readable error message.
            data (Optional[str]): Optional additional data associated with the error (JSON recommended)
        """
        super().__init__(message)
        self._code = code
        self._message = message
        self._data = data

    @property
    def code(self) -> int:
        """Error code value. Codes 1001-1999 are reserved for built-in errors (see RpcError.ErrorCode for their meanings)."""
        return self._code

    @property
    def message(self) -> str:
        """A readable error message."""
        return self._message

    @property
    def data(self) -> Optional[str]:
        """Optional additional data associated with the error (JSON recommended)."""
        return self._data

    @classmethod
    def _from_proto(cls, proto: proto_rpc.RpcError) -> "RpcError":
        return cls(proto.code, proto.message, proto.data)

    def _to_proto(self) -> proto_rpc.RpcError:
        return proto_rpc.RpcError(code=self.code, message=self.message, data=self.data)

    @classmethod
    def _built_in(
        cls, code: "RpcError.ErrorCode", data: Optional[str] = None
    ) -> "RpcError":
        message = cls.ErrorMessage[code]
        return cls(code, message, data)
