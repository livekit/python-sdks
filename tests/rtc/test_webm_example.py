"""Run with `uv run --with 'av>=16.1' pytest tests/rtc/test_webm_example.py`."""

from __future__ import annotations

import asyncio
import importlib.util
import io
import os
import threading
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

av = pytest.importorskip(
    "av", minversion="16.1", reason="optional WebM example dependency (Python 3.10+)"
)
from livekit import rtc  # noqa: E402

_EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "preencoded-webm"
_spec = importlib.util.spec_from_file_location("webm", _EXAMPLE / "webm.py")
webm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(webm)


def make_webm(*, alpha: bool) -> bytes:
    """Generate synthetic streaming WebM without private media fixtures."""
    buf = io.BytesIO()
    with av.open(buf, "w", format="webm", options={"live": "1", "cluster_time_limit": "1"}) as c:
        stream = c.add_stream("libvpx-vp9", rate=25)
        stream.width = stream.height = 160
        stream.pix_fmt = "yuva420p" if alpha else "yuv420p"
        stream.options = {
            "deadline": "realtime",
            "cpu-used": "8",
            "lag-in-frames": "0",
            "auto-alt-ref": "0",
        }
        pixels = np.random.default_rng(4).integers(0, 256, (160, 160, 4), dtype=np.uint8)
        for i in range(12):
            frame = av.VideoFrame.from_ndarray(pixels, format="rgba")
            frame.pts = i
            frame.time_base = Fraction(1, 25)
            c.mux(stream.encode(frame))
        c.mux(stream.encode(None))
    return buf.getvalue()


@pytest.fixture(scope="module")
def opaque_webm() -> bytes:
    return make_webm(alpha=False)


@pytest.fixture(scope="module")
def alpha_webm() -> bytes:
    return make_webm(alpha=True)


def test_demux_preserves_compressed_video(opaque_webm: bytes) -> None:
    with av.open(io.BytesIO(opaque_webm)) as c:
        packets = [p for p in c.demux(video=0) if p.size]
    with av.open(io.BytesIO(opaque_webm)) as c:
        frames = list(webm.demux(c))
    assert len(frames) == len(packets) == 12
    assert [f.timestamp_us for f in frames] == list(range(0, 480000, 40000))
    for frame, packet in zip(frames, packets):
        assert frame.data == bytes(packet)
        assert frame.frame_type == (
            rtc.EncodedFrameType.ENCODED_FRAME_KEY
            if packet.is_keyframe
            else rtc.EncodedFrameType.ENCODED_FRAME_DELTA
        )


def test_reject_alpha_webm(alpha_webm: bytes) -> None:
    with av.open(io.BytesIO(alpha_webm)) as c:
        with pytest.raises(ValueError, match="alpha.*preserves the WebM container"):
            next(webm.demux(c))


@pytest.mark.parametrize("codec", ["libvpx", "libvpx-vp9"])
def test_opaque_webm(codec: str) -> None:
    buf = io.BytesIO()
    with av.open(buf, "w", format="webm") as c:
        stream = c.add_stream(codec, rate=25)
        stream.width = stream.height = 16
        stream.pix_fmt = "yuv420p"
        stream.options = {"deadline": "realtime", "lag-in-frames": "0"}
        c.mux(
            stream.encode(
                av.VideoFrame.from_ndarray(np.zeros((16, 16, 3), dtype=np.uint8), format="rgb24")
            )
        )
        c.mux(stream.encode(None))
    with av.open(io.BytesIO(buf.getvalue())) as c:
        packets = [bytes(p) for p in c.demux(video=0) if p.size]
    with av.open(io.BytesIO(buf.getvalue())) as c:
        assert [f.data for f in webm.demux(c)] == packets


def test_demux_before_pipe_eof(opaque_webm: bytes) -> None:
    class PipeReader(io.BufferedReader):
        def seekable(self) -> bool:
            # Windows can report an anonymous pipe as seekable; FFmpeg must not seek it.
            return False

    read_fd, write_fd = os.pipe()
    decoded_first = threading.Event()
    writer_closed = threading.Event()

    def write() -> None:
        try:
            with os.fdopen(write_fd, "wb") as pipe:
                for start in range(0, len(opaque_webm), 4096):
                    pipe.write(opaque_webm[start : start + 4096])
                    pipe.flush()
                decoded_first.wait(5)
        finally:
            writer_closed.set()

    writer = threading.Thread(target=write)
    writer.start()
    try:
        with (
            PipeReader(io.FileIO(read_fd, "rb")) as pipe,
            av.open(
                pipe,
                format="webm",
                buffer_size=4096,
                options={"probesize": "4096", "analyzeduration": "0"},
            ) as c,
        ):
            frames = webm.demux(c)
            first = next(frames)
            assert not writer_closed.is_set()
            decoded_first.set()
            assert first.frame_type == rtc.EncodedFrameType.ENCODED_FRAME_KEY
            assert len(list(frames)) == 11
    finally:
        decoded_first.set()
        writer.join(timeout=5)
        assert not writer.is_alive()


async def test_cancel_waits_for_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "webm", webm)
    spec = importlib.util.spec_from_file_location("webm_publisher", _EXAMPLE / "publish.py")
    publisher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(publisher)
    started, release, finished = threading.Event(), threading.Event(), threading.Event()

    def frames():
        started.set()
        assert release.wait(5)
        finished.set()
        yield 1

    task = asyncio.create_task(publisher.read_next(iter(frames())))
    try:
        assert await asyncio.to_thread(started.wait, 5)
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert finished.is_set()
    finally:
        release.set()


def test_http_stream_before_response_finishes(opaque_webm: bytes) -> None:
    from http.server import BaseHTTPRequestHandler, HTTPServer

    first_frame, response_finished = threading.Event(), threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "video/webm")
            self.end_headers()
            self.wfile.write(opaque_webm)
            self.wfile.flush()
            first_frame.wait(5)
            response_finished.set()

        def log_message(self, *args) -> None:
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.handle_request)
    worker.start()
    try:
        with av.open(
            f"http://127.0.0.1:{server.server_port}/live.webm",
            format="webm",
            timeout=(5.0, 5.0),
            options={"probesize": "4096", "analyzeduration": "0"},
        ) as c:
            frame = next(webm.demux(c))
            assert not response_finished.is_set()
            assert frame.data
    finally:
        first_frame.set()
        worker.join(timeout=5)
        server.server_close()
        assert not worker.is_alive()


@pytest.mark.parametrize("broken_input", [False, True])
async def test_publish_primes_keyframe_and_cleans_up(
    monkeypatch: pytest.MonkeyPatch, broken_input: bool
) -> None:
    import sys
    from types import SimpleNamespace

    monkeypatch.setitem(sys.modules, "webm", webm)
    spec = importlib.util.spec_from_file_location("webm_publisher", _EXAMPLE / "publish.py")
    publisher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(publisher)
    sent = []
    closed = []
    unpublished = []

    class Source:
        def __init__(self, *args):
            pass

        def capture_frame(self, frame):
            sent.append(frame)
            return True

        def take_feedback(self):
            return rtc.EncodedVideoSourceFeedback(
                False, rtc.EncodedRateControl(100000, 25) if len(sent) > 1 else None
            )

        async def aclose(self):
            closed.append(True)

    async def subscribed():
        pass

    async def publish_track(*args):
        return SimpleNamespace(sid="track", wait_for_subscription=subscribed)

    async def unpublish_track(sid):
        unpublished.append(sid)

    monkeypatch.setattr(publisher.rtc, "EncodedVideoSource", Source)
    monkeypatch.setattr(publisher.rtc.LocalVideoTrack, "create_video_track", lambda *args: None)
    room = SimpleNamespace(
        local_participant=SimpleNamespace(
            publish_track=publish_track, unpublish_track=unpublish_track
        )
    )

    def frames():
        yield rtc.EncodedVideoFrame(
            b"key", 16, 16, rtc.VideoCodec.VP9, rtc.EncodedFrameType.ENCODED_FRAME_KEY, 0
        )
        if broken_input:
            raise ValueError("broken stream")
        yield rtc.EncodedVideoFrame(
            b"delta", 16, 16, rtc.VideoCodec.VP9, rtc.EncodedFrameType.ENCODED_FRAME_DELTA, 40000
        )

    if broken_input:
        with pytest.raises(ValueError, match="broken stream"):
            await publisher.publish(room, frames(), name="test")
    else:
        task = asyncio.create_task(publisher.publish(room, frames(), name="test"))
        try:

            async def wait_for_frames():
                while len(sent) < 3:
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(wait_for_frames(), 5)
            assert not task.done()  # EOF must not immediately tear down the track.
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
    assert [f.data for f in sent] == (
        [b"key", b"key"] if broken_input else [b"key", b"key", b"delta"]
    )
    assert sent[1].timestamp_us > sent[0].timestamp_us
    assert closed == [True]
    assert unpublished == ["track"]


_byte_example = _EXAMPLE.parent / "webm-byte-stream" / "stream_webm.py"
_byte_spec = importlib.util.spec_from_file_location("stream_webm", _byte_example)
byte_publisher = importlib.util.module_from_spec(_byte_spec)
_byte_spec.loader.exec_module(byte_publisher)


@pytest.mark.parametrize("failure", [None, ValueError, asyncio.CancelledError])
async def test_byte_publisher_preserves_chunks_and_closes(alpha_webm: bytes, failure) -> None:
    from types import SimpleNamespace

    written, reasons, options = [], [], []

    async def write(chunk):
        written.append(chunk)

    async def close(**kwargs):
        reasons.append(kwargs["reason"])

    async def open_stream(**kwargs):
        options.append(kwargs)
        return SimpleNamespace(write=write, aclose=close)

    async def chunks():
        yield alpha_webm[:15000]
        if failure:
            raise failure()
        yield alpha_webm[15000:]

    participant = SimpleNamespace(stream_bytes=open_stream)
    if failure:
        with pytest.raises(failure):
            await byte_publisher.send_webm(participant, chunks(), recipient="viewer")
        assert b"".join(written) == alpha_webm[:15000]
        assert reasons == ["WebM source interrupted"]
    else:
        await byte_publisher.send_webm(participant, chunks(), recipient="viewer")
        assert b"".join(written) == alpha_webm
        assert reasons == [""]
    assert options == [
        dict(
            name="video.webm",
            topic="webm",
            mime_type="video/webm",
            destination_identities=["viewer"],
        )
    ]


async def test_byte_file_reader(alpha_webm: bytes, tmp_path: Path) -> None:
    path = tmp_path / "alpha.webm"
    path.write_bytes(alpha_webm)
    chunks = [chunk async for chunk in byte_publisher.read_chunks(str(path))]
    assert all(0 < len(chunk) <= 15000 for chunk in chunks)
    assert b"".join(chunks) == alpha_webm


async def test_byte_http_reader_before_eof(alpha_webm: bytes) -> None:
    from aiohttp import web

    first_received = asyncio.Event()

    async def handle(request):
        response = web.StreamResponse(headers={"Content-Type": "video/webm"})
        await response.prepare(request)
        await response.write(alpha_webm[:15000])
        await asyncio.wait_for(first_received.wait(), 5)
        await response.write(alpha_webm[15000:])
        return response

    app = web.Application()
    app.router.add_get("/video.webm", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    chunks = byte_publisher.read_chunks(f"http://127.0.0.1:{port}/video.webm")
    try:
        first = await asyncio.wait_for(chunks.__anext__(), 5)
        assert first and alpha_webm.startswith(first)
        first_received.set()
        received = first + b"".join([chunk async for chunk in chunks])
        assert received == alpha_webm
    finally:
        first_received.set()
        await chunks.aclose()
        await runner.cleanup()


async def test_byte_stream_preserves_alpha_webm_before_eof(alpha_webm: bytes) -> None:
    """Round-trip a complete standard WebM through the real LiveKit byte API."""
    import contextlib
    import uuid

    from livekit import api

    if not all(os.getenv(key) for key in ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")):
        pytest.skip("LiveKit server credentials are required")

    room_name = f"webm-bytes-{uuid.uuid4().hex}"
    sender, receiver = rtc.Room(), rtc.Room()
    first_received = asyncio.Event()
    completed = asyncio.get_running_loop().create_future()
    consumers = []

    async def consume(reader):
        try:
            assert reader.info.mime_type == "video/webm"
            received = bytearray()
            async for chunk in reader:
                received.extend(chunk)
                first_received.set()
            completed.set_result(bytes(received))
        except Exception as exc:
            first_received.set()
            if not completed.done():
                completed.set_exception(exc)
        finally:
            reader.close()

    def on_stream(reader, identity):
        consumers.append(asyncio.create_task(consume(reader)))

    receiver.register_byte_stream_handler("webm", on_stream)

    def token(identity):
        return (
            api.AccessToken()
            .with_identity(identity)
            .with_grants(api.VideoGrants(room_join=True, room=room_name))
            .to_jwt()
        )

    async def chunks():
        yield alpha_webm[:15000]
        # Do not produce the rest until the receiver sees a chunk. This fails
        # if delivery buffers the whole WebM until EOF.
        await asyncio.wait_for(first_received.wait(), 10)
        yield alpha_webm[15000:]

    try:
        await receiver.connect(os.environ["LIVEKIT_URL"], token("viewer"))
        await sender.connect(os.environ["LIVEKIT_URL"], token("sender"))
        await asyncio.wait_for(
            byte_publisher.send_webm(sender.local_participant, chunks(), recipient="viewer"), 20
        )
        received = await asyncio.wait_for(completed, 10)
        assert received == alpha_webm
        with av.open(io.BytesIO(received)) as container:
            assert container.streams.video[0].metadata["alpha_mode"] == "1"
            packets = [p for p in container.demux(video=0) if p.size]
            assert len(packets) == 12
            assert all(p.get_sidedata("matroska_block_additional") for p in packets)
    finally:
        for task in consumers:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        await sender.disconnect()
        await receiver.disconnect()
