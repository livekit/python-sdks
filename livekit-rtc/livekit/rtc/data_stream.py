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
import datetime
from collections.abc import Callable
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Dict, List
from ._proto import data_stream_pb2 as proto_data_stream
from ._proto import ffi_pb2 as proto_ffi
from ._ffi_client import FfiClient, FfiHandle
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .participant import LocalParticipant

STREAM_CHUNK_SIZE = 15_000
"""Deprecated: chunking now happens inside the FFI; kept for compatibility."""

_DISCONNECT_ERROR = "Disconnected while receiving"


class StreamError(ConnectionError):
    """Raised when a data stream operation fails or an incoming stream
    terminates abnormally (e.g. aborted by the sender or exceeding the
    room's maximum payload length)."""

    def __init__(self, description: str) -> None:
        super().__init__(description)
        self.description = description


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


@dataclass
class ByteStreamInfo(BaseStreamInfo):
    name: str


def _text_stream_info_from_proto(info: proto_data_stream.TextStreamInfo) -> TextStreamInfo:
    return TextStreamInfo(
        stream_id=info.stream_id,
        mime_type=info.mime_type,
        topic=info.topic,
        timestamp=info.timestamp,
        size=info.total_length if info.HasField("total_length") else 0,
        attributes=dict(info.attributes),
        attachments=list(info.attached_stream_ids),
    )


def _byte_stream_info_from_proto(info: proto_data_stream.ByteStreamInfo) -> ByteStreamInfo:
    return ByteStreamInfo(
        stream_id=info.stream_id,
        mime_type=info.mime_type,
        topic=info.topic,
        timestamp=info.timestamp,
        size=info.total_length if info.HasField("total_length") else 0,
        attributes=dict(info.attributes),
        name=info.name,
    )


class TextStreamReader:
    """An incoming text stream.

    Use as an async iterator to receive chunks, or :meth:`read_all` to collect
    the whole payload::

        async for chunk in reader:
            process(chunk)

    A reader subscribes to the FFI event queue as soon as it is handed to your
    handler, so one that is never iterated to completion — abandoned after a
    ``break``, or received by a handler that never reads it — must be closed
    with :meth:`close`, or its subscription lives for the rest of the process.
    Iterating to the end closes the reader for you.

    If the stream terminates abnormally (aborted by the sender, oversized, or
    the room disconnects mid-stream), :class:`StreamError` is raised instead of
    a normal ``StopAsyncIteration``.
    """

    def __init__(
        self,
        owned_info: proto_data_stream.OwnedTextStreamReader,
        *,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        self._info = _text_stream_info_from_proto(owned_info.info)
        # the read_incremental request below consumes the FFI handle, so it
        # must be kept as a raw id and never wrapped in an FfiHandle
        handle_id = owned_info.handle.id
        self._reader_handle = handle_id
        self._on_close = on_close
        self._closed = False
        self._error: Optional[StreamError] = None
        # subscribe before read_incremental so no reader event can be missed
        self._queue = FfiClient.instance.queue.subscribe(
            filter_fn=lambda e: (
                e.WhichOneof("message") == "text_stream_reader_event"
                and e.text_stream_reader_event.reader_handle == handle_id
            ),
        )
        req = proto_ffi.FfiRequest()
        req.text_read_incremental.reader_handle = handle_id
        FfiClient.instance.request(req)

    def __aiter__(self) -> AsyncIterator[str]:
        return self

    async def __anext__(self) -> str:
        while True:
            if self._closed:
                if self._error is not None:
                    raise self._error
                raise StopAsyncIteration
            event: proto_ffi.FfiEvent = await self._queue.get()
            stream_event = event.text_stream_reader_event
            detail = stream_event.WhichOneof("detail")
            if detail == "chunk_received":
                if not stream_event.chunk_received.content:
                    continue
                return stream_event.chunk_received.content
            elif detail == "eos":
                eos = stream_event.eos
                self._info.attributes = self._info.attributes or {}
                self._info.attributes.update(eos.attributes)
                if eos.HasField("error"):
                    self._error = StreamError(eos.error.description)
                self._close()
                if self._error is not None:
                    raise self._error
                raise StopAsyncIteration

    @property
    def info(self) -> TextStreamInfo:
        return self._info

    async def read_all(self) -> str:
        final_string = ""
        async for chunk in self:
            final_string += chunk
        return final_string

    def _unsubscribe(self) -> None:
        """Drops the FFI queue subscription without ending the stream.

        Events already delivered stay in the queue and remain readable; only
        the global subscription, and the filter it runs against every FFI
        event, goes away. Safe to call repeatedly — unsubscribing a queue that
        is no longer registered is a no-op.

        Only the subscription is released: the reader handle was consumed by
        the read_incremental request in __init__, so there is nothing left to
        dispose (and disposing it would drop a handle the FFI server no longer
        owns).
        """
        FfiClient.instance.queue.unsubscribe(self._queue)

    def _wake_pending_reads(self) -> None:
        """Pushes a terminal event into this reader's own queue.

        Closing unsubscribes, so no further FFI event can ever arrive; without
        this, a read already parked in ``await self._queue.get()`` would wait
        forever. The sentinel carries no error, so the woken read raises
        ``StopAsyncIteration`` — or the stored :class:`StreamError`, which
        ``__anext__`` checks first.
        """
        event = proto_ffi.FfiEvent()
        event.text_stream_reader_event.reader_handle = self._reader_handle
        event.text_stream_reader_event.eos.SetInParent()
        self._queue.put_nowait(event)

    def _close(self) -> None:
        if not self._closed:
            self._closed = True
            self._unsubscribe()
            self._wake_pending_reads()
            if self._on_close is not None:
                self._on_close()

    def close(self) -> None:
        """Explicitly close the reader and unsubscribe.

        Call this on a reader you stop consuming before it ends. Closing a
        reader that already reached end-of-stream is a no-op, and iterating a
        closed reader raises ``StopAsyncIteration`` (or :class:`StreamError`
        if the stream had already failed).
        """
        self._close()

    async def aclose(self) -> None:
        self.close()

    def _signal_disconnect(self) -> None:
        """Injects a synthetic EOS-with-error event so pending reads wake up
        and raise StreamError when the room disconnects mid-stream.

        Also drops the queue subscription, which would otherwise outlive the
        room: no further events can arrive once the room is gone, and the
        injected one is already queued. The reader is deliberately left open
        so chunks that arrived before the disconnect are still delivered
        before the StreamError, as they were before this was unsubscribed
        here.
        """
        if self._closed:
            return
        event = proto_ffi.FfiEvent()
        event.text_stream_reader_event.reader_handle = self._reader_handle
        event.text_stream_reader_event.eos.error.description = _DISCONNECT_ERROR
        self._queue.put_nowait(event)
        self._unsubscribe()


class ByteStreamReader:
    """An incoming byte stream.

    Use as an async iterator to receive chunks::

        async for chunk in reader:
            process(chunk)

    A reader subscribes to the FFI event queue as soon as it is handed to your
    handler, so one that is never iterated to completion — abandoned after a
    ``break``, or received by a handler that never reads it — must be closed
    with :meth:`close`, or its subscription lives for the rest of the process.
    Iterating to the end closes the reader for you.

    If the stream terminates abnormally (aborted by the sender, oversized, or
    the room disconnects mid-stream), :class:`StreamError` is raised instead of
    a normal ``StopAsyncIteration``.
    """

    def __init__(
        self,
        owned_info: proto_data_stream.OwnedByteStreamReader,
        capacity: int = 0,
        *,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        # capacity is ignored: chunk delivery is push-based from the FFI
        self._info = _byte_stream_info_from_proto(owned_info.info)
        handle_id = owned_info.handle.id
        self._reader_handle = handle_id
        self._on_close = on_close
        self._closed = False
        self._error: Optional[StreamError] = None
        self._queue = FfiClient.instance.queue.subscribe(
            filter_fn=lambda e: (
                e.WhichOneof("message") == "byte_stream_reader_event"
                and e.byte_stream_reader_event.reader_handle == handle_id
            ),
        )
        req = proto_ffi.FfiRequest()
        req.byte_read_incremental.reader_handle = handle_id
        FfiClient.instance.request(req)

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self

    async def __anext__(self) -> bytes:
        while True:
            if self._closed:
                if self._error is not None:
                    raise self._error
                raise StopAsyncIteration
            event: proto_ffi.FfiEvent = await self._queue.get()
            stream_event = event.byte_stream_reader_event
            detail = stream_event.WhichOneof("detail")
            if detail == "chunk_received":
                if not stream_event.chunk_received.content:
                    continue
                return stream_event.chunk_received.content
            elif detail == "eos":
                eos = stream_event.eos
                self._info.attributes = self._info.attributes or {}
                self._info.attributes.update(eos.attributes)
                if eos.HasField("error"):
                    self._error = StreamError(eos.error.description)
                self._close()
                if self._error is not None:
                    raise self._error
                raise StopAsyncIteration

    @property
    def info(self) -> ByteStreamInfo:
        return self._info

    def _unsubscribe(self) -> None:
        """Drops the FFI queue subscription without ending the stream.

        Events already delivered stay in the queue and remain readable; only
        the global subscription, and the filter it runs against every FFI
        event, goes away. Safe to call repeatedly — unsubscribing a queue that
        is no longer registered is a no-op.

        Only the subscription is released: the reader handle was consumed by
        the read_incremental request in __init__, so there is nothing left to
        dispose (and disposing it would drop a handle the FFI server no longer
        owns).
        """
        FfiClient.instance.queue.unsubscribe(self._queue)

    def _wake_pending_reads(self) -> None:
        """Pushes a terminal event into this reader's own queue.

        Closing unsubscribes, so no further FFI event can ever arrive; without
        this, a read already parked in ``await self._queue.get()`` would wait
        forever. The sentinel carries no error, so the woken read raises
        ``StopAsyncIteration`` — or the stored :class:`StreamError`, which
        ``__anext__`` checks first.
        """
        event = proto_ffi.FfiEvent()
        event.byte_stream_reader_event.reader_handle = self._reader_handle
        event.byte_stream_reader_event.eos.SetInParent()
        self._queue.put_nowait(event)

    def _close(self) -> None:
        if not self._closed:
            self._closed = True
            self._unsubscribe()
            self._wake_pending_reads()
            if self._on_close is not None:
                self._on_close()

    def close(self) -> None:
        """Explicitly close the reader and unsubscribe.

        Call this on a reader you stop consuming before it ends. Closing a
        reader that already reached end-of-stream is a no-op, and iterating a
        closed reader raises ``StopAsyncIteration`` (or :class:`StreamError`
        if the stream had already failed).
        """
        self._close()

    async def aclose(self) -> None:
        self.close()

    def _signal_disconnect(self) -> None:
        """Injects a synthetic EOS-with-error event so pending reads wake up
        and raise StreamError when the room disconnects mid-stream.

        Also drops the queue subscription, which would otherwise outlive the
        room: no further events can arrive once the room is gone, and the
        injected one is already queued. The reader is deliberately left open
        so chunks that arrived before the disconnect are still delivered
        before the StreamError, as they were before this was unsubscribed
        here.
        """
        if self._closed:
            return
        event = proto_ffi.FfiEvent()
        event.byte_stream_reader_event.reader_handle = self._reader_handle
        event.byte_stream_reader_event.eos.error.description = _DISCONNECT_ERROR
        self._queue.put_nowait(event)
        self._unsubscribe()


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
        self._total_size = total_size
        self._sender_identity = sender_identity or self._local_participant.identity
        # the writer handle is assigned by the FFI when the stream is opened;
        # the close request consumes it, so it is kept as a raw id
        self._writer_handle: Optional[int] = None
        self._writer_ffi_handle: Optional[FfiHandle] = None
        self._write_lock = asyncio.Lock()
        self._closed = False

    def _provisional_timestamp(self) -> int:
        return int(datetime.datetime.now().timestamp() * 1000)

    def _register_open(self, handle_id: int) -> None:
        """Takes ownership of a freshly opened writer handle.

        Wrapping it in an FfiHandle means a writer that is simply dropped —
        abandoned, or left behind by an exception or a cancelled task — still
        releases the native writer when it is garbage collected. It is also
        registered with the participant so the room can drop it deterministically
        at disconnect, for writers still referenced at that point. The registry
        holds the handle weakly, so registration does not itself keep an
        abandoned writer alive.
        """
        self._writer_handle = handle_id
        self._writer_ffi_handle = FfiHandle(handle_id)
        self._local_participant._open_stream_writers[handle_id] = self._writer_ffi_handle

    def _unregister_open(self) -> None:
        """Forgets the writer because a close request has been issued for it.

        The close consumes the handle on the native side, so it must no longer
        be dropped by the disconnect cleanup.
        """
        if self._writer_handle is None:
            return
        self._local_participant._open_stream_writers.pop(self._writer_handle, None)
        if self._writer_ffi_handle is not None:
            self._writer_ffi_handle.mark_consumed()

    async def _wait_for_callback(
        self, req: proto_ffi.FfiRequest, callback_field: str, response_field: str
    ) -> proto_ffi.FfiEvent:
        queue = FfiClient.instance.queue.subscribe()
        try:
            resp = FfiClient.instance.request(req)
            async_id = getattr(resp, response_field).async_id
            cb: proto_ffi.FfiEvent = await queue.wait_for(
                lambda e: getattr(e, callback_field).async_id == async_id
            )
        finally:
            FfiClient.instance.queue.unsubscribe(queue)

        if getattr(cb, callback_field).HasField("error"):
            raise StreamError(getattr(cb, callback_field).error.description)
        return cb

    async def aclose(
        self, *, reason: str = "", attributes: Optional[Dict[str, str]] = None
    ) -> None:
        if self._closed:
            raise RuntimeError("Stream already closed")
        if self._writer_handle is None:
            raise RuntimeError("Stream is not open")
        self._closed = True
        # unregister before sending: the request consumes the handle natively,
        # so it must not be dropped again by the disconnect cleanup even if the
        # close itself reports an error
        self._unregister_open()
        await self._send_close(reason=reason, attributes=attributes)

    async def _send_close(self, *, reason: str, attributes: Optional[Dict[str, str]]) -> None:
        raise NotImplementedError


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
        options = proto_data_stream.StreamTextOptions(topic=topic)
        if attributes:
            options.attributes.update(attributes)
        if destination_identities:
            options.destination_identities.extend(destination_identities)
        if stream_id is not None:
            options.id = stream_id
        if reply_to_id:
            options.reply_to_stream_id = reply_to_id
        options.sender_identity = self._sender_identity
        self._options = options
        # provisional info, replaced by the FFI-provided info once opened
        self._info = TextStreamInfo(
            stream_id=stream_id or "",
            mime_type="text/plain",
            topic=topic,
            timestamp=self._provisional_timestamp(),
            size=total_size,
            attributes=dict(attributes) if attributes else {},
            attachments=[],
        )

    async def _send_header(self) -> None:
        req = proto_ffi.FfiRequest()
        req.text_stream_open.local_participant_handle = self._local_participant._ffi_handle.handle
        req.text_stream_open.options.CopyFrom(self._options)
        cb = await self._wait_for_callback(req, "text_stream_open", "text_stream_open")
        owned = cb.text_stream_open.writer
        self._register_open(owned.handle.id)
        self._info = _text_stream_info_from_proto(owned.info)
        if not self._info.size and self._total_size is not None:
            # total_size is not transmitted for text streams; keep it local
            self._info.size = self._total_size

    async def write(self, text: str) -> None:
        async with self._write_lock:
            if self._closed:
                raise RuntimeError("Cannot write after stream is closed")
            if self._writer_handle is None:
                raise RuntimeError("Stream is not open")
            req = proto_ffi.FfiRequest()
            req.text_stream_write.writer_handle = self._writer_handle
            req.text_stream_write.text = text
            await self._wait_for_callback(req, "text_stream_writer_write", "text_stream_write")

    async def _send_close(self, *, reason: str, attributes: Optional[Dict[str, str]]) -> None:
        assert self._writer_handle is not None
        req = proto_ffi.FfiRequest()
        req.text_stream_close.writer_handle = self._writer_handle
        req.text_stream_close.reason = reason
        if attributes:
            req.text_stream_close.attributes.update(attributes)
        await self._wait_for_callback(req, "text_stream_writer_close", "text_stream_close")

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
        options = proto_data_stream.StreamByteOptions(
            topic=topic,
            name=name,
            mime_type=mime_type,
        )
        if attributes:
            options.attributes.update(attributes)
        if destination_identities:
            options.destination_identities.extend(destination_identities)
        if stream_id is not None:
            options.id = stream_id
        if total_size is not None:
            options.total_length = total_size
        options.sender_identity = self._sender_identity
        self._options = options
        # provisional info, replaced by the FFI-provided info once opened
        self._info = ByteStreamInfo(
            stream_id=stream_id or "",
            mime_type=mime_type,
            topic=topic,
            timestamp=self._provisional_timestamp(),
            size=total_size,
            attributes=dict(attributes) if attributes else {},
            name=name,
        )

    async def _send_header(self) -> None:
        req = proto_ffi.FfiRequest()
        req.byte_stream_open.local_participant_handle = self._local_participant._ffi_handle.handle
        req.byte_stream_open.options.CopyFrom(self._options)
        cb = await self._wait_for_callback(req, "byte_stream_open", "byte_stream_open")
        owned = cb.byte_stream_open.writer
        self._register_open(owned.handle.id)
        self._info = _byte_stream_info_from_proto(owned.info)

    async def write(self, data: bytes) -> None:
        async with self._write_lock:
            if self._closed:
                raise RuntimeError("Cannot write after stream is closed")
            if self._writer_handle is None:
                raise RuntimeError("Stream is not open")
            req = proto_ffi.FfiRequest()
            req.byte_stream_write.writer_handle = self._writer_handle
            req.byte_stream_write.bytes = data
            await self._wait_for_callback(req, "byte_stream_writer_write", "byte_stream_write")

    async def _send_close(self, *, reason: str, attributes: Optional[Dict[str, str]]) -> None:
        assert self._writer_handle is not None
        req = proto_ffi.FfiRequest()
        req.byte_stream_close.writer_handle = self._writer_handle
        req.byte_stream_close.reason = reason
        if attributes:
            req.byte_stream_close.attributes.update(attributes)
        await self._wait_for_callback(req, "byte_stream_writer_close", "byte_stream_close")

    @property
    def info(self) -> ByteStreamInfo:
        return self._info


TextStreamHandler = Callable[[TextStreamReader, str], None]
ByteStreamHandler = Callable[[ByteStreamReader, str], None]
