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

import uuid
import datetime
from dataclasses import dataclass
from typing import AsyncIterator, Optional, TypedDict, Dict, List
from ._proto.room_pb2 import DataStream as proto_DataStream
from ._utils import RingQueue
from .participant import LocalParticipant, PublishDataError
from ._proto import ffi_pb2 as proto_ffi
from ._proto import room_pb2 as proto_room
from ._ffi_client import FfiClient


STREAM_CHUNK_SIZE = 15_000


@dataclass
class BaseStreamInfo(TypedDict):
    id: str
    mime_type: str
    topic: str
    timestamp: int
    size: Optional[int]  # Optional means it can be an int or None
    extensions: Optional[Dict[str, str]]  # Optional for the extensions dictionary


@dataclass
class TextStreamInfo(BaseStreamInfo):
    attachments: List[str]
    pass


@dataclass
class TextStreamUpdate:
    current: str
    collected: str


class TextStreamReader:
    def __init__(self, header: proto_DataStream.Header, capacity: int = 0) -> None:
        self._header = header
        self._info = TextStreamInfo(
            id=header.stream_id,
            mime_type=header.mime_type,
            topic=header.topic,
            timestamp=header.timestamp,
            size=header.total_length,
            extensions=dict(header.extensions),
            attachments=list(header.text_header.attached_stream_ids),
        )
        self._queue: RingQueue[proto_DataStream.Chunk | None] = RingQueue(capacity)
        self._chunks: Dict[str, proto_DataStream.Chunk] = {}

    def _on_chunk_update(self, chunk: proto_DataStream.Chunk):
        self._queue.put(chunk)

    def _on_stream_close(self, trailer: proto_DataStream.Trailer):
        self._queue.put(None)

    def __aiter__(self) -> AsyncIterator[TextStreamUpdate]:
        return self

    async def __anext__(self) -> TextStreamUpdate:
        item = await self._queue.get()
        if item is None:
            raise StopAsyncIteration
        decodedStr = item.content.decode()

        self._chunks[item.stream_id] = item
        chunk_list = list(self._chunks.values())
        chunk_list.sort(key=lambda chunk: chunk.chunk_index)
        collected: str = "".join(map(lambda chunk: chunk.content.decode(), chunk_list))
        return TextStreamUpdate(current=decodedStr, collected=collected)

    @property
    def info(self) -> TextStreamInfo:
        return self._info


@dataclass
class FileStreamInfo(BaseStreamInfo):
    file_name: str
    pass


class FileStreamReader:
    def __init__(self, header: proto_DataStream.Header, capacity: int = 0) -> None:
        self._header = header
        self._info = FileStreamInfo(
            id=header.stream_id,
            mime_type=header.mime_type,
            topic=header.topic,
            timestamp=header.timestamp,
            size=header.total_length,
            extensions=dict(header.extensions),
            file_name=header.file_header.file_name,
        )
        self._queue: RingQueue[proto_DataStream.Chunk | None] = RingQueue(capacity)

    def _on_chunk_update(self, chunk: proto_DataStream.Chunk):
        self._queue.put(chunk)

    def _on_stream_close(self, trailer: proto_DataStream.Trailer):
        self._queue.put(None)

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self

    async def __anext__(self) -> bytes:
        item = await self._queue.get()
        if item is None:
            raise StopAsyncIteration

        return item.content

    @property
    def info(self) -> FileStreamInfo:
        return self._info


class BaseStreamWriter:
    def __init__(
        self,
        local_participant: LocalParticipant,
        topic: str = "",
        extensions: Optional[Dict[str, str]] = {},
        stream_id: str | None = None,
        total_size: int | None = None,
        mime_type: str = "",
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
            extensions=extensions,
            total_length=total_size,
        )
        self._next_chunk_index: int = 0

    async def _send_header(self, destination_identities: List[str] = []):
        req = proto_ffi.FfiRequest(
            send_stream_header=proto_room.SendStreamHeaderRequest(
                header=self._header,
                local_participant_handle=self._local_participant._ffi_handle.handle,
                destination_identities=destination_identities,
            )
        )

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.send_stream_header.async_id
                == resp.send_stream_header.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.send_stream_header.error:
            raise PublishDataError(cb.send_stream_header.error)

    async def _send_chunk(self, chunk: proto_DataStream.Chunk):
        req = proto_ffi.FfiRequest(
            send_stream_chunk=proto_room.SendStreamChunkRequest(
                chunk=chunk,
                local_participant_handle=self._local_participant._ffi_handle.handle,
            )
        )

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.send_stream_chunk.async_id
                == resp.send_stream_chunk.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.send_stream_chunk.error:
            raise PublishDataError(cb.send_stream_chunk.error)

    async def _send_trailer(self, trailer: proto_DataStream.Trailer):
        req = proto_ffi.FfiRequest(
            send_stream_trailer=proto_room.SendStreamTrailer(
                trailer=trailer,
                local_participant_handle=self._local_participant._ffi_handle.handle,
            )
        )

        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: e.send_stream_trailer.async_id
                == resp.send_stream_trailer.async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if cb.send_stream_chunk.error:
            raise PublishDataError(cb.send_stream_trailer.error)

    async def close(self):
        await self._send_trailer()


class TextStreamWriter(BaseStreamWriter):
    def __init__(
        self,
        local_participant: LocalParticipant,
        topic: str = "",
        extensions: Optional[Dict[str, str]] = {},
        stream_id: str | None = None,
        total_size: int | None = None,
        reply_to_id: str | None = None,
    ) -> None:
        super().__init__(
            local_participant,
            topic,
            extensions,
            stream_id,
            total_size,
            mime_type="text/plain",
        )
        if reply_to_id:
            self._header.text_header.reply_to_stream_id = reply_to_id
        self._info = TextStreamInfo(
            id=self._header.stream_id,
            mime_type=self._header.mime_type,
            topic=self._header.topic,
            timestamp=self._header.timestamp,
            size=self._header.total_length,
            extensions=dict(self._header.extensions),
            attachments=list(self._header.text_header.attached_stream_ids),
        )

    async def write(self, text: str, chunk_index: int | None = None):
        content = text.encode()
        if len(content) > STREAM_CHUNK_SIZE:
            raise ValueError("maximum chunk size exceeded")
        if chunk_index is None:
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


class FileStreamWriter(BaseStreamWriter):
    def __init__(
        self,
        local_participant: LocalParticipant,
        file_name: str,
        topic: str = "",
        extensions: Optional[Dict[str, str]] = {},
        stream_id: str | None = None,
        total_size: int | None = None,
        mime_type: str = "",
    ) -> None:
        super().__init__(
            local_participant,
            topic,
            extensions,
            stream_id,
            total_size,
            mime_type=mime_type,
        )
        self._header.file_header.file_name = file_name
        self._info = FileStreamInfo(
            id=self._header.stream_id,
            mime_type=self._header.mime_type,
            topic=self._header.topic,
            timestamp=self._header.timestamp,
            size=self._header.total_length,
            extensions=dict(self._header.extensions),
            file_name=self._header.file_header.file_name,
        )

    async def write(self, data: bytes, chunk_index: int | None = None):
        if len(data) > STREAM_CHUNK_SIZE:
            raise ValueError("maximum chunk size exceeded")

        if chunk_index is None:
            chunk_index = self._next_chunk_index
            self._next_chunk_index += 1
        chunk_msg = proto_DataStream.Chunk(
            stream_id=self._header.stream_id, chunk_index=chunk_index, content=data
        )
        await self._send_chunk(chunk_msg)

    @property
    def info(self) -> FileStreamInfo:
        return self._info
