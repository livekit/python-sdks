"""Run with `uv run --with 'av>=16.1' pytest tests/rtc/test_webm_example.py`."""

from __future__ import annotations

import asyncio
import importlib.util
import io
import os
import struct
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


@pytest.fixture(scope="module")
def alpha_webm() -> bytes:
    """Synthetic media only; alpha is intentionally larger than one RTP packet."""
    buf = io.BytesIO()
    with av.open(buf, "w", format="webm", options={"live": "1", "cluster_time_limit": "1"}) as c:
        stream = c.add_stream("libvpx-vp9", rate=25)
        stream.width = stream.height = 160
        stream.pix_fmt = "yuva420p"
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


def test_demux_preserves_compressed_color_and_alpha(alpha_webm: bytes) -> None:
    with av.open(io.BytesIO(alpha_webm)) as c:
        packets = [p for p in c.demux(video=0) if p.size]
    with av.open(io.BytesIO(alpha_webm)) as c:
        # No decode call: payloads must be byte-for-byte identical to the demuxer.
        frames = list(webm.demux(c, experimental_alpha=True))
    assert len(frames) == len(packets) == 12
    assert [f.timestamp_us for f in frames] == list(range(0, 480000, 40000))
    for frame, packet in zip(frames, packets):
        color, alpha = webm.unpack_alpha(frame.data)
        assert color == bytes(packet)
        assert alpha == bytes(packet.get_sidedata("matroska_block_additional"))[8:]
        assert frame.frame_type == (
            rtc.EncodedFrameType.ENCODED_FRAME_KEY
            if packet.is_keyframe
            else rtc.EncodedFrameType.ENCODED_FRAME_DELTA
        )
    assert len(webm.unpack_alpha(frames[0].data)[1]) > 1200


def test_alpha_requires_explicit_opt_in(alpha_webm: bytes) -> None:
    with av.open(io.BytesIO(alpha_webm)) as c:
        with pytest.raises(ValueError, match="alpha"):
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
    with av.open(io.BytesIO(buf.getvalue())) as c:
        with pytest.raises(ValueError, match="AlphaMode"):
            next(webm.demux(c, experimental_alpha=True))


def test_demux_before_pipe_eof(alpha_webm: bytes) -> None:
    read_fd, write_fd = os.pipe()
    decoded_first = threading.Event()
    writer_closed = threading.Event()

    def write() -> None:
        try:
            with os.fdopen(write_fd, "wb") as pipe:
                for start in range(0, len(alpha_webm), 4096):
                    pipe.write(alpha_webm[start : start + 4096])
                    pipe.flush()
                decoded_first.wait(5)
        finally:
            writer_closed.set()

    writer = threading.Thread(target=write)
    writer.start()
    try:
        with (
            os.fdopen(read_fd, "rb") as pipe,
            av.open(
                pipe,
                format="webm",
                buffer_size=4096,
                options={"probesize": "4096", "analyzeduration": "0"},
            ) as c,
        ):
            frames = webm.demux(c, experimental_alpha=True)
            first = next(frames)
            assert not writer_closed.is_set()
            decoded_first.set()
            assert first.frame_type == rtc.EncodedFrameType.ENCODED_FRAME_KEY
            assert len(list(frames)) == 11
    finally:
        decoded_first.set()
        writer.join(timeout=5)
        assert not writer.is_alive()


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"short",
        b"caa" + struct.pack(">II4sB", 1, 2, b"LKWA", 2),
        b"caa" + struct.pack(">II4sB", 1, 3, b"LKWA", 1),
        b"caa" + struct.pack(">II4sB", 0, 3, b"LKWA", 1),
        b"caa" + struct.pack(">II4sB", 1, 2, b"NOPE", 1),
    ],
)
def test_reject_bad_envelopes(data: bytes) -> None:
    with pytest.raises(ValueError):
        webm.unpack_alpha(data)


def test_bound_envelope_size(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(webm, "_MAX_FRAME_BYTES", 32)
    with pytest.raises(ValueError, match="limit"):
        webm.pack_alpha(b"c" * 16, b"a" * 16)
    with pytest.raises(ValueError):
        webm.pack_alpha(b"", b"a")
    with pytest.raises(ValueError):
        webm.unpack_alpha(b"x" * 33)


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


def test_http_stream_before_response_finishes(alpha_webm: bytes) -> None:
    from http.server import BaseHTTPRequestHandler, HTTPServer

    first_frame, response_finished = threading.Event(), threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "video/webm")
            self.end_headers()
            self.wfile.write(alpha_webm)
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
            frame = next(webm.demux(c, experimental_alpha=True))
            assert not response_finished.is_set()
            assert webm.unpack_alpha(frame.data)[1]
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
