"""Forward intact WebM from a file or HTTP response over a LiveKit byte stream."""

from __future__ import annotations

import argparse
import asyncio
import os
from collections.abc import AsyncIterator

import aiofiles
import aiohttp
from livekit import api, rtc

_CHUNK_SIZE = 15_000


async def read_chunks(source: str) -> AsyncIterator[bytes]:
    if source.startswith(("http://", "https://")):
        timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(source) as response:
                response.raise_for_status()
                async for chunk in response.content.iter_chunked(_CHUNK_SIZE):
                    yield chunk
    else:
        async with aiofiles.open(source, "rb") as file:
            while chunk := await file.read(_CHUNK_SIZE):
                yield chunk


async def send_webm(
    participant: rtc.LocalParticipant, chunks: AsyncIterator[bytes], *, recipient: str
) -> None:
    writer = await participant.stream_bytes(
        name="video.webm",
        topic="webm",
        mime_type="video/webm",
        destination_identities=[recipient],
    )
    reason = "WebM source interrupted"
    try:
        async for chunk in chunks:
            await writer.write(chunk)
        reason = ""
    finally:
        await writer.aclose(reason=reason)


async def main(args: argparse.Namespace) -> None:
    room = rtc.Room()
    token = (
        api.AccessToken()
        .with_identity("webm-byte-publisher")
        .with_grants(api.VideoGrants(room_join=True, room=args.room))
        .to_jwt()
    )
    try:
        await room.connect(os.environ["LIVEKIT_URL"], token)
        if args.recipient not in room.remote_participants:
            raise ValueError("recipient must join and register its 'webm' handler before sending")
        chunks = read_chunks(args.input)
        try:
            await send_webm(room.local_participant, chunks, recipient=args.recipient)
        finally:
            await chunks.aclose()
    finally:
        await room.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="valid streaming WebM file or HTTP(S) URL")
    parser.add_argument("--room", default="webm-stream")
    parser.add_argument("--recipient", required=True, help="identity of the prepared receiver")
    asyncio.run(main(parser.parse_args()))
