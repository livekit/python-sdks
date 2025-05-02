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

from __future__ import annotations

import asyncio
import uuid
import datetime
from collections.abc import Callable
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Dict, List
from ._proto.room_pb2 import DataStream as proto_DataStream
from ._proto import ffi_pb2 as proto_ffi
from ._proto import room_pb2 as proto_room
from ._ffi_client import FfiClient
from ._utils import split_utf8
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .participant import LocalParticipant

STREAM_CHUNK_SIZE = 15_000


@dataclass
class BaseStreamInfo:
    stream_id: str
    mime_type: str
    topic: str
    timestamp: int
    size: Optional[int]
    attributes: Optional[Dict[str, str]]  # Optional for the attributes dictionary


@dataclass
class TextStreamInfo(BaseStreamInfo):
    attachments: List[str]


class TextStreamReader:
    def __init__(
        self,
        header: proto_DataStream.Header,
    ) -> None:
        self._header = header
        self._info = TextStreamInfo(
            stream_id=header.stream_id,
            mime_type=header.mime_type,
            topic=header.topic,
            timestamp=header.timestamp,
            size=header.total_length,
            attributes=dict(header.attributes),
            attachments=list(header.text_header.attached_stream_ids),
        )
        self._queue: asyncio.Queue[proto_DataStream.Chunk | None] = asyncio.Queue()

    async def _on_chunk_update(self, chunk: proto_DataStream.Chunk):
        await self._queue.put(chunk)

    async def _on_stream_close(self, trailer: proto_DataStream.Trailer):
        self.info.attributes = self.info.attributes or {}
        self.info.attributes.update(trailer.attributes)
        await self._queue.put(None)

    def __aiter__(self) -> AsyncIterator[str]:
        return self

    async def __anext__(self) -> str:
        item = await self._queue.get()
        if item is None:
            raise StopAsyncIteration
        decodedStr = item.content.decode()
        return decodedStr

    @property
    def info(self) -> TextStreamInfo:
        return self._info

    async def read_all(self) -> str:
        final_string = ""
        async for chunk in self:
            final_string += chunk
        return final_string


@dataclass
class ByteStreamInfo(BaseStreamInfo):
    name: str


class ByteStreamReader:
    def __init__(self, header: proto_DataStream.Header, capacity: int = 0) -> None:
        self._header = header
        self._info = ByteStreamInfo(
            stream_id=header.stream_id,
            mime_type=header.mime_type,
            topic=header.topic,
            timestamp=header.timestamp,
            size=header.total_length,
            attributes=dict(header.attributes),
            name=header.byte_header.name,
        )
        self._queue: asyncio.Queue[proto_DataStream.Chunk | None] = asyncio.Queue(capacity)

    async def _on_chunk_update(self, chunk: proto_DataStream.Chunk):
        await self._queue.put(chunk)

    async def _on_stream_close(self, trailer: proto_DataStream.Trailer):
        self.info.attributes = self.info.attributes or {}
        self.info.attributes.update(trailer.attributes)
        await self._queue.put(None)

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self

    async def __anext__(self) -> bytes:
        item = await self._queue.get()
        if item is None:
            raise StopAsyncIteration

        return item.content

    @property
    def info(self) -> ByteStreamInfo:
        return self._info


class BaseStreamWriter:
    def __init__(
        self,
        local_participant: LocalParticipant,
        topic: str = "",
        attributes: Optional[Dict[str, str]] = {},
        stream_id: str | None = None,
        total_size: int | None = None,
        mime_type: str = "",
        destination_identities: Optional[List[str]] = None,
        sender_identity: str | None = None,
    ):
        self._local_participant = local_participant
        if stream_id is None:
            stream_id = str(uuid.uuid4())
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        self._header = proto_DataStream.Header(
            stream_id=stream_id,
            timestamp=timestamp,
            mime_type=mime_type,
            topic=topic,
            attributes=attributes,
            total_length=total_size,
        )
        self._next_chunk_index: int = 0
        self._destination_identities = destination_identities
        self._sender_identity = sender_identity or self._local_participant.identity
        self._closed = False

    async def _send_header(self):
        req = proto_ffi.FfiRequest(
            send_stream_header=proto_room.SendStreamHeaderRequest(
                header=self._header,
                local_participant_handle=self._local_participant._ffi_handle.handle,
                destination_identities=self._destination_identities,
                sender_identity=self._sender_identity,
            )
        )

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.send_stream_header.async_id == resp.send_stream_header.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.send_stream_header.error:
            raise ConnectionError(cb.send_stream_header.error)

    async def _send_chunk(self, chunk: proto_DataStream.Chunk):
        if self._closed:
            raise RuntimeError(f"Cannot send chunk after stream is closed: {chunk}")
        req = proto_ffi.FfiRequest(
            send_stream_chunk=proto_room.SendStreamChunkRequest(
                chunk=chunk,
                local_participant_handle=self._local_participant._ffi_handle.handle,
                sender_identity=self._local_participant.identity,
                destination_identities=self._destination_identities,
            )
        )

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.send_stream_chunk.async_id == resp.send_stream_chunk.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.send_stream_chunk.error:
            raise ConnectionError(cb.send_stream_chunk.error)

    async def _send_trailer(self, trailer: proto_DataStream.Trailer):
        req = proto_ffi.FfiRequest(
            send_stream_trailer=proto_room.SendStreamTrailerRequest(
                trailer=trailer,
                local_participant_handle=self._local_participant._ffi_handle.handle,
                sender_identity=self._local_participant.identity,
            )
        )

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.send_stream_trailer.async_id == resp.send_stream_trailer.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.send_stream_chunk.error:
            raise ConnectionError(cb.send_stream_trailer.error)

    async def aclose(self, *, reason: str = "", attributes: Optional[Dict[str, str]] = None):
        if self._closed:
            raise RuntimeError("Stream already closed")
        self._closed = True
        await self._send_trailer(
            trailer=proto_DataStream.Trailer(
                stream_id=self._header.stream_id, reason=reason, attributes=attributes
            )
        )


class TextStreamWriter(BaseStreamWriter):
    def __init__(
        self,
        local_participant: LocalParticipant,
        *,
        topic: str = "",
        attributes: Optional[Dict[str, str]] = {},
        stream_id: str | None = None,
        total_size: int | None = None,
        reply_to_id: str | None = None,
        destination_identities: Optional[List[str]] = None,
        sender_identity: str | None = None,
    ) -> None:
        super().__init__(
            local_participant,
            topic,
            attributes,
            stream_id,
            total_size,
            mime_type="text/plain",
            destination_identities=destination_identities,
            sender_identity=sender_identity,
        )
        self._header.text_header.operation_type = proto_DataStream.OperationType.CREATE
        if reply_to_id:
            self._header.text_header.reply_to_stream_id = reply_to_id
        self._info = TextStreamInfo(
            stream_id=self._header.stream_id,
            mime_type=self._header.mime_type,
            topic=self._header.topic,
            timestamp=self._header.timestamp,
            size=self._header.total_length,
            attributes=dict(self._header.attributes),
            attachments=list(self._header.text_header.attached_stream_ids),
        )
        self._write_lock = asyncio.Lock()

    async def write(self, text: str):
        async with self._write_lock:
            for chunk in split_utf8(text, STREAM_CHUNK_SIZE):
                content = chunk
                chunk_index = self._next_chunk_index
                self._next_chunk_index += 1
                chunk_msg = proto_DataStream.Chunk(
                    stream_id=self._header.stream_id,
                    chunk_index=chunk_index,
                    content=content,
                )
                await self._send_chunk(chunk_msg)

    @property
    def info(self) -> TextStreamInfo:
        return self._info


class ByteStreamWriter(BaseStreamWriter):
    def __init__(
        self,
        local_participant: LocalParticipant,
        *,
        name: str,
        topic: str = "",
        attributes: Optional[Dict[str, str]] = None,
        stream_id: str | None = None,
        total_size: int | None = None,
        mime_type: str = "application/octet-stream",
        destination_identities: Optional[List[str]] = None,
    ) -> None:
        super().__init__(
            local_participant,
            topic,
            attributes,
            stream_id,
            total_size,
            mime_type=mime_type,
            destination_identities=destination_identities,
        )
        self._header.byte_header.name = name
        self._info = ByteStreamInfo(
            stream_id=self._header.stream_id,
            mime_type=self._header.mime_type,
            topic=self._header.topic,
            timestamp=self._header.timestamp,
            size=self._header.total_length,
            attributes=dict(self._header.attributes),
            name=self._header.byte_header.name,
        )
        self._write_lock = asyncio.Lock()

    async def write(self, data: bytes):
        async with self._write_lock:
            chunked_data = [
                data[i : i + STREAM_CHUNK_SIZE] for i in range(0, len(data), STREAM_CHUNK_SIZE)
            ]

            for chunk in chunked_data:
                chunk_msg = proto_DataStream.Chunk(
                    stream_id=self._header.stream_id,
                    chunk_index=self._next_chunk_index,
                    content=chunk,
                )
                await self._send_chunk(chunk_msg)
                self._next_chunk_index += 1

    @property
    def info(self) -> ByteStreamInfo:
        return self._info


TextStreamHandler = Callable[[TextStreamReader, str], None]
ByteStreamHandler = Callable[[ByteStreamReader, str], None]
