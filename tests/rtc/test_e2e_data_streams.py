"""
End-to-end tests for data streams (text/byte streams over the FFI-backed
rust implementation). Mirrors the node SDK's e2e_data_streams tests, plus
coverage of receiver-side payload caps, abnormal termination, and trailer
attributes.

Requirements:
- LIVEKIT_URL: LiveKit server URL
- LIVEKIT_API_KEY: API key for authentication
- LIVEKIT_API_SECRET: API secret for authentication

Tests will be skipped if these environment variables are not set.

Usage:
    pytest test_e2e_data_streams.py -v
"""

import asyncio
import os
import time
import uuid
from typing import Any, List, Optional, Tuple

import pytest

from livekit import api, rtc


def skip_if_no_credentials() -> Any:
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    return pytest.mark.skipif(
        bool(missing), reason=f"Missing environment variables: {', '.join(missing)}"
    )


def create_token(identity: str, room_name: str) -> str:
    return (
        api.AccessToken()
        .with_identity(identity)
        .with_name(identity)
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )


def unique_room_name(base: str) -> str:
    return f"{base}-{uuid.uuid4().hex[:8]}"


def pseudo_random_text(length: int, seed: int = 0x5EED) -> str:
    """Deterministic pseudo-random lowercase text (mulberry32 PRNG).

    Random lowercase carries ~4.7 bits of entropy per 8-bit byte, so deflate
    compresses it well under its raw size — exercising the chunked-compressed
    wire path.
    """
    a = seed & 0xFFFFFFFF
    chars: List[str] = []
    for _ in range(length):
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = a
        t = (t ^ (t >> 15)) * (t | 1) & 0xFFFFFFFF
        t = (t + ((t ^ (t >> 7)) * (t | 61) & 0xFFFFFFFF)) & 0xFFFFFFFF
        t = t ^ (t >> 14)
        chars.append(chr(97 + t % 26))
    return "".join(chars)


async def connect_rooms(
    room_name: str,
    *,
    receiver_options: Optional[rtc.RoomOptions] = None,
) -> Tuple[rtc.Room, rtc.Room]:
    """Connects a (receiver, sender) room pair and waits for mutual visibility."""
    url = os.getenv("LIVEKIT_URL")
    assert url is not None

    receiver = rtc.Room()
    sender = rtc.Room()
    await receiver.connect(
        url, create_token("receiver", room_name), receiver_options or rtc.RoomOptions()
    )
    await sender.connect(url, create_token("sender", room_name))

    deadline = asyncio.get_event_loop().time() + 5.0
    while asyncio.get_event_loop().time() < deadline:
        if len(receiver.remote_participants) == 1 and len(sender.remote_participants) == 1:
            break
        await asyncio.sleep(0.05)
    else:
        raise AssertionError("participants did not become visible to each other")

    return receiver, sender


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_send_text_small() -> None:
    """Small text via send_text: info assertions + round trip."""
    receiver, sender = await connect_rooms(unique_room_name("ds-text-small"))
    try:
        text_to_send = "some-text"
        received: asyncio.Future[str] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.TextStreamReader, participant_identity: str) -> None:
            assert participant_identity == "sender"

            async def read() -> None:
                received.set_result(await reader.read_all())

            asyncio.create_task(read())

        receiver.register_text_stream_handler("some-topic", handler)

        info = await sender.local_participant.send_text(text_to_send, topic="some-topic")
        assert info.stream_id
        assert abs(info.timestamp - time.time() * 1000) <= 2_000
        assert info.size == len(text_to_send.encode())
        assert info.mime_type == "text/plain"
        assert info.topic == "some-topic"

        assert await asyncio.wait_for(received, timeout=5.0) == text_to_send
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_stream_bytes_small() -> None:
    """Small byte stream via the incremental writer."""
    receiver, sender = await connect_rooms(unique_room_name("ds-bytes-small"))
    try:
        bytes_to_send = b"\xfa" * 16
        received: asyncio.Future[bytes] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.ByteStreamReader, participant_identity: str) -> None:
            assert participant_identity == "sender"

            async def read() -> None:
                chunks = [chunk async for chunk in reader]
                received.set_result(b"".join(chunks))

            asyncio.create_task(read())

        receiver.register_byte_stream_handler("some-topic", handler)

        writer = await sender.local_participant.stream_bytes(
            "test-bytes", topic="some-topic", total_size=len(bytes_to_send)
        )
        assert writer.info.stream_id
        assert abs(writer.info.timestamp - time.time() * 1000) <= 2_000
        assert writer.info.mime_type == "application/octet-stream"
        assert writer.info.topic == "some-topic"
        assert writer.info.name == "test-bytes"
        await writer.write(bytes_to_send)
        await writer.aclose()

        assert await asyncio.wait_for(received, timeout=5.0) == bytes_to_send
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_send_text_large_compressible() -> None:
    """~50KB of pseudo-random lowercase: too big to inline and compresses well,
    exercising the chunked + deflate-raw wire path (rust compresses, rust
    decompresses, python reads)."""
    receiver, sender = await connect_rooms(unique_room_name("ds-text-large"))
    try:
        text = pseudo_random_text(50_000)
        received: asyncio.Future[str] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.TextStreamReader, _identity: str) -> None:
            async def read() -> None:
                received.set_result(await reader.read_all())

            asyncio.create_task(read())

        receiver.register_text_stream_handler("large-text", handler)

        info = await sender.local_participant.send_text(text, topic="large-text")
        assert info.size == len(text.encode())

        assert await asyncio.wait_for(received, timeout=10.0) == text
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_send_text_compress_false() -> None:
    """compress=False round-trips the payload uncompressed."""
    receiver, sender = await connect_rooms(unique_room_name("ds-text-nocompress"))
    try:
        text = pseudo_random_text(50_000)
        received: asyncio.Future[str] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.TextStreamReader, _identity: str) -> None:
            async def read() -> None:
                received.set_result(await reader.read_all())

            asyncio.create_task(read())

        receiver.register_text_stream_handler("nocompress-text", handler)

        await sender.local_participant.send_text(text, topic="nocompress-text", compress=False)

        assert await asyncio.wait_for(received, timeout=10.0) == text
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_stream_bytes_large_incompressible() -> None:
    """Large uniform-random payload spanning many chunks (uncompressed path)."""
    receiver, sender = await connect_rooms(unique_room_name("ds-bytes-random"))
    try:
        payload = os.urandom(1_000_000)
        received: asyncio.Future[bytes] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.ByteStreamReader, _identity: str) -> None:
            async def read() -> None:
                chunks = [chunk async for chunk in reader]
                received.set_result(b"".join(chunks))

            asyncio.create_task(read())

        receiver.register_byte_stream_handler("random-bytes", handler)

        writer = await sender.local_participant.stream_bytes(
            "random-bytes", topic="random-bytes", total_size=len(payload)
        )
        write_chunk_size = 64 * 1024
        for offset in range(0, len(payload), write_chunk_size):
            await writer.write(payload[offset : offset + write_chunk_size])
        await writer.aclose()

        result = await asyncio.wait_for(received, timeout=20.0)
        assert len(result) == len(payload)
        assert result == payload
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_stream_bytes_large_patterned() -> None:
    """50KB patterned payload via the byte-stream writer."""
    receiver, sender = await connect_rooms(unique_room_name("ds-bytes-patterned"))
    try:
        payload = bytes(i % 251 for i in range(50_000))
        received: asyncio.Future[bytes] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.ByteStreamReader, _identity: str) -> None:
            async def read() -> None:
                chunks = [chunk async for chunk in reader]
                received.set_result(b"".join(chunks))

            asyncio.create_task(read())

        receiver.register_byte_stream_handler("patterned-bytes", handler)

        writer = await sender.local_participant.stream_bytes(
            "patterned", topic="patterned-bytes", total_size=len(payload)
        )
        await writer.write(payload)
        await writer.aclose()

        assert await asyncio.wait_for(received, timeout=10.0) == payload
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_stream_text_incremental_unicode() -> None:
    """Multiple writes with multi-byte characters: UTF-8-aware chunking must
    not split codepoints."""
    receiver, sender = await connect_rooms(unique_room_name("ds-text-unicode"))
    try:
        pieces = ["héllo wörld — ", "日本語のテキスト、", "🌍🚀 emoji tail"]
        expected = "".join(pieces)
        received: asyncio.Future[str] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.TextStreamReader, _identity: str) -> None:
            async def read() -> None:
                received.set_result(await reader.read_all())

            asyncio.create_task(read())

        receiver.register_text_stream_handler("unicode-text", handler)

        writer = await sender.local_participant.stream_text(topic="unicode-text")
        for piece in pieces:
            await writer.write(piece)
        await writer.aclose()

        assert await asyncio.wait_for(received, timeout=5.0) == expected
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_receiver_rejects_oversized_payload() -> None:
    """A receiver with a small max_payload_byte_length must reject an
    oversized stream with StreamError rather than delivering truncated data."""
    receiver, sender = await connect_rooms(
        unique_room_name("ds-payload-cap"),
        receiver_options=rtc.RoomOptions(
            data_stream=rtc.DataStreamOptions(max_payload_byte_length=1_000)
        ),
    )
    try:
        text = pseudo_random_text(50_000)
        result: asyncio.Future[BaseException] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.TextStreamReader, _identity: str) -> None:
            async def read() -> None:
                try:
                    data = await reader.read_all()
                    result.set_exception(
                        AssertionError(f"expected StreamError, read {len(data)} chars")
                    )
                except rtc.StreamError as e:
                    result.set_result(e)

            asyncio.create_task(read())

        receiver.register_text_stream_handler("capped-topic", handler)

        await sender.local_participant.send_text(text, topic="capped-topic")

        error = await asyncio.wait_for(result, timeout=10.0)
        assert "maximum size" in str(error)
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_abnormal_close_raises_on_receiver() -> None:
    """Closing a stream with a reason mid-transfer must raise StreamError on
    the receiving reader."""
    receiver, sender = await connect_rooms(unique_room_name("ds-abnormal-close"))
    try:
        result: asyncio.Future[BaseException] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.TextStreamReader, _identity: str) -> None:
            async def read() -> None:
                try:
                    data = await reader.read_all()
                    result.set_exception(
                        AssertionError(f"expected StreamError, read {len(data)} chars")
                    )
                except rtc.StreamError as e:
                    result.set_result(e)

            asyncio.create_task(read())

        receiver.register_text_stream_handler("abort-topic", handler)

        writer = await sender.local_participant.stream_text(topic="abort-topic")
        await writer.write("partial data")
        await writer.aclose(reason="cancelled by test")

        error = await asyncio.wait_for(result, timeout=5.0)
        assert "cancelled by test" in str(error)
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_trailer_attributes_merged_into_info() -> None:
    """Attributes passed to aclose() must appear in the receiving reader's
    info after a clean EOS."""
    receiver, sender = await connect_rooms(unique_room_name("ds-trailer-attrs"))
    try:
        received: asyncio.Future[Tuple[str, rtc.TextStreamInfo]] = (
            asyncio.get_event_loop().create_future()
        )

        def handler(reader: rtc.TextStreamReader, _identity: str) -> None:
            async def read() -> None:
                text = await reader.read_all()
                received.set_result((text, reader.info))

            asyncio.create_task(read())

        receiver.register_text_stream_handler("attrs-topic", handler)

        writer = await sender.local_participant.stream_text(
            topic="attrs-topic", attributes={"initial": "yes"}
        )
        await writer.write("hello")
        await writer.aclose(attributes={"result": "ok", "count": "1"})

        text, info = await asyncio.wait_for(received, timeout=5.0)
        assert text == "hello"
        assert info.attributes is not None
        assert info.attributes.get("initial") == "yes"
        assert info.attributes.get("result") == "ok"
        assert info.attributes.get("count") == "1"
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_receiver_disconnect_mid_stream() -> None:
    """Disconnecting the receiving room mid-stream must surface StreamError to
    the reader instead of hanging."""
    receiver, sender = await connect_rooms(unique_room_name("ds-disconnect"))
    try:
        result: asyncio.Future[BaseException] = asyncio.get_event_loop().create_future()
        handler_called = asyncio.Event()

        def handler(reader: rtc.TextStreamReader, _identity: str) -> None:
            handler_called.set()

            async def read() -> None:
                try:
                    await reader.read_all()
                    result.set_exception(AssertionError("expected StreamError, got clean EOF"))
                except rtc.StreamError as e:
                    result.set_result(e)

            asyncio.create_task(read())

        receiver.register_text_stream_handler("disconnect-topic", handler)

        writer = await sender.local_participant.stream_text(topic="disconnect-topic")
        await writer.write("partial data")
        await asyncio.wait_for(handler_called.wait(), timeout=5.0)

        await receiver.disconnect()

        error = await asyncio.wait_for(result, timeout=5.0)
        assert isinstance(error, rtc.StreamError)

        await writer.aclose()
    finally:
        await sender.disconnect()


@pytest.mark.asyncio
@skip_if_no_credentials()  # type: ignore[untyped-decorator]
async def test_send_file_round_trip(tmp_path: Any) -> None:
    """send_file hands the path to the FFI, which reads and streams the file;
    the receiver gets the payload plus the derived name, size, and mime type."""
    receiver, sender = await connect_rooms(unique_room_name("ds-file"))
    try:
        payload = os.urandom(64_000)
        file_path = tmp_path / "test-payload.bin"
        file_path.write_bytes(payload)

        received: asyncio.Future[bytes] = asyncio.get_event_loop().create_future()
        received_info: asyncio.Future[rtc.ByteStreamInfo] = asyncio.get_event_loop().create_future()

        def handler(reader: rtc.ByteStreamReader, participant_identity: str) -> None:
            assert participant_identity == "sender"
            received_info.set_result(reader.info)

            async def read() -> None:
                chunks = [chunk async for chunk in reader]
                received.set_result(b"".join(chunks))

            asyncio.create_task(read())

        receiver.register_byte_stream_handler("file-topic", handler)

        info = await sender.local_participant.send_file(str(file_path), topic="file-topic")
        assert info.stream_id
        assert info.name == "test-payload.bin"
        assert info.size == len(payload)

        assert await asyncio.wait_for(received, timeout=10.0) == payload
        reader_info = await asyncio.wait_for(received_info, timeout=5.0)
        assert reader_info.name == "test-payload.bin"
        assert reader_info.size == len(payload)
        assert reader_info.mime_type == "application/octet-stream"
    finally:
        await asyncio.gather(receiver.disconnect(), sender.disconnect())
