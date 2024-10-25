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


class RpcError(Exception):
    """
    Specialized error handling for RPC methods.

    Instances of this type, when thrown in a method handler, will have their `message`
    serialized and sent across the wire. The caller will receive an equivalent error on the other side.

    Build-in types are included but developers may use any string, with a max length of 256 bytes.
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

        Error codes 1001-1999 are reserved for built-in errors (see RpcError.ErrorCode for their meanings).
        """
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data

    @classmethod
    def from_proto(cls, proto: proto_rpc.RpcError) -> "RpcError":
        return cls(proto.code, proto.message, proto.data)

    def to_proto(self) -> proto_rpc.RpcError:
        return proto_rpc.RpcError(code=self.code, message=self.message, data=self.data)

    @classmethod
    def _built_in(
        cls, code: "RpcError.ErrorCode", data: Optional[str] = None
    ) -> "RpcError":
        """
        Creates an error object from the ErrorCode, with an auto-populated message.
        """
        message = cls.ErrorMessage[code]
        return cls(code, message, data)
