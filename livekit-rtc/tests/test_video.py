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

"""End-to-end video publish/subscribe tests."""

import asyncio
import os
import struct
import uuid
import zlib
from pathlib import Path

import numpy as np
import pytest

from livekit import api, rtc


VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 15
VIDEO_COLOR_DURATION_SEC = 1.0
# (name, RGB tuple) — order matters; the subscriber must see them in this sequence.
VIDEO_COLOR_SEQUENCE: list[tuple[str, tuple[int, int, int]]] = [
    ("red", (255, 0, 0)),
    ("green", (0, 255, 0)),
    ("blue", (0, 0, 255)),
    ("white", (255, 255, 255)),
    ("black", (0, 0, 0)),
]


def skip_if_no_credentials():
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
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        .to_jwt()
    )


def unique_room_name(base: str) -> str:
    return f"{base}-{uuid.uuid4().hex[:8]}"


def _solid_color_rgba_frame(width: int, height: int, rgb: tuple[int, int, int]) -> rtc.VideoFrame:
    """Build a solid-color 640x480 RGBA `VideoFrame` for the given RGB triple."""
    pixels = np.empty((height, width, 4), dtype=np.uint8)
    pixels[:, :, 0] = rgb[0]
    pixels[:, :, 1] = rgb[1]
    pixels[:, :, 2] = rgb[2]
    pixels[:, :, 3] = 255
    return rtc.VideoFrame(
        width=width,
        height=height,
        type=rtc.VideoBufferType.RGBA,
        data=pixels.tobytes(),
    )


def _classify_frame_color(
    frame_rgb: np.ndarray,
    palette: list[tuple[str, tuple[int, int, int]]],
) -> tuple[str, float]:
    """Return (nearest palette color name, euclidean distance) for the mean RGB of `frame_rgb`."""
    mean_rgb = frame_rgb[:, :, :3].reshape(-1, 3).mean(axis=0)
    best_name, best_dist = palette[0][0], float("inf")
    for name, rgb in palette:
        dist = float(np.linalg.norm(mean_rgb - np.asarray(rgb, dtype=np.float64)))
        if dist < best_dist:
            best_name, best_dist = name, dist
    return best_name, best_dist


def _save_rgba_frame_as_png(frame_rgba: np.ndarray, path: Path) -> None:
    """Encode an (H, W, 4) uint8 RGBA array to a PNG file using only the stdlib."""
    height, width, _ = frame_rgba.shape
    rgb = np.ascontiguousarray(frame_rgba[:, :, :3], dtype=np.uint8)

    def _chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    signature = b"\x89PNG\r\n\x1a\n"
    # IHDR: width, height, bit depth=8, color type=2 (RGB), compression=0, filter=0, interlace=0
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    # Each scanline must be prefixed with a filter byte (0 = None).
    filter_col = np.zeros((height, 1), dtype=np.uint8)
    scanlines = np.concatenate([filter_col, rgb.reshape(height, width * 3)], axis=1)
    idat = zlib.compress(scanlines.tobytes(), level=6)

    with open(path, "wb") as f:
        f.write(signature)
        f.write(_chunk(b"IHDR", ihdr))
        f.write(_chunk(b"IDAT", idat))
        f.write(_chunk(b"IEND", b""))


@skip_if_no_credentials()
class TestVideoStreamPublishSubscribe:
    """End-to-end: publish a 640x480 color-cycle video and verify colors on the subscriber."""

    async def test_video_stream_publish_subscribe(self):
        """Publish red/green/blue/white/black (1s each, 15fps) and verify color sequence."""
        url = os.environ["LIVEKIT_URL"]
        room_name = unique_room_name("test-video-colors")

        publisher_room = rtc.Room()
        subscriber_room = rtc.Room()

        publisher_token = create_token("video-publisher", room_name)
        subscriber_token = create_token("video-subscriber", room_name)

        track_subscribed_event = asyncio.Event()
        subscribed_track: rtc.Track | None = None

        @subscriber_room.on("track_subscribed")
        def on_track_subscribed(
            track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant,
        ):
            nonlocal subscribed_track
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                subscribed_track = track
                track_subscribed_event.set()

        try:
            await subscriber_room.connect(url, subscriber_token)
            await publisher_room.connect(url, publisher_token)

            source = rtc.VideoSource(VIDEO_WIDTH, VIDEO_HEIGHT)
            track = rtc.LocalVideoTrack.create_video_track("color-cycle", source)
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_CAMERA
            await publisher_room.local_participant.publish_track(track, options)

            await asyncio.wait_for(track_subscribed_event.wait(), timeout=10.0)
            assert subscribed_track is not None

            # Request RGBA frames from the SFU so we don't have to convert per frame.
            video_stream = rtc.VideoStream(subscribed_track, format=rtc.VideoBufferType.RGBA)

            received_frames: list[np.ndarray] = []
            stop_collecting = asyncio.Event()

            async def publish_colors() -> None:
                await track_subscribed_event.wait()
                frame_interval = 1.0 / VIDEO_FPS
                frames_per_color = int(VIDEO_FPS * VIDEO_COLOR_DURATION_SEC)
                loop = asyncio.get_event_loop()
                start = loop.time()
                global_idx = 0
                for _repeat in range(2):
                    for _color_name, rgb in VIDEO_COLOR_SEQUENCE:
                        frame = _solid_color_rgba_frame(VIDEO_WIDTH, VIDEO_HEIGHT, rgb)
                        for _ in range(frames_per_color):
                            source.capture_frame(frame)
                            global_idx += 1
                            target = start + global_idx * frame_interval
                            sleep_for = target - loop.time()
                            if sleep_for > 0:
                                await asyncio.sleep(sleep_for)

            async def collect_frames() -> None:
                async for event in video_stream:
                    vf = event.frame
                    if vf.type != rtc.VideoBufferType.RGBA:
                        vf = vf.convert(rtc.VideoBufferType.RGBA)
                    arr = (
                        np.frombuffer(bytes(vf.data.cast("B")), dtype=np.uint8)
                        .reshape(vf.height, vf.width, 4)
                        .copy()
                    )
                    received_frames.append(arr)
                    if stop_collecting.is_set():
                        break

            collect_task = asyncio.create_task(collect_frames())
            publish_task = asyncio.create_task(publish_colors())

            await publish_task
            # Allow trailing frames to drain before signaling stop.
            await asyncio.sleep(0.5)
            stop_collecting.set()

            try:
                await asyncio.wait_for(collect_task, timeout=3.0)
            except asyncio.TimeoutError:
                collect_task.cancel()
                try:
                    await collect_task
                except (asyncio.CancelledError, BaseException):
                    pass

            await video_stream.aclose()
            await source.aclose()

            assert len(received_frames) > 0, "No video frames received"

            # Classify each received frame against the 5-color palette.
            classified = [
                _classify_frame_color(f, VIDEO_COLOR_SEQUENCE)[0] for f in received_frames
            ]

            # Reduce to stable runs: ignore single-frame transitions at color boundaries.
            runs: list[tuple[str, int]] = []
            for color in classified:
                if runs and runs[-1][0] == color:
                    runs[-1] = (color, runs[-1][1] + 1)
                else:
                    runs.append((color, 1))
            # A stable run has several frames of the same classified color.
            stable_run_min = max(3, VIDEO_FPS // 3)
            dominant = {c for c, n in runs if n >= stable_run_min}

            expected_colors = {name for name, _ in VIDEO_COLOR_SEQUENCE}
            missing_colors = expected_colors - dominant
            assert not missing_colors, (
                f"Expected colors {expected_colors} not all present in subscribed track; "
                f"missing {missing_colors}. Dominant colors: {dominant}. "
                f"Full classified stream: {classified}"
            )

            # Snapshot the first received frame of each expected color to JPEG.
            output_dir = Path(__file__).parent
            saved: dict[str, Path] = {}
            for idx, color_name in enumerate(classified):
                if color_name in saved:
                    continue
                if color_name not in (name for name, _ in VIDEO_COLOR_SEQUENCE):
                    continue
                out_path = output_dir / f"subscriber_recv_frame_color_{color_name}.png"
                _save_rgba_frame_as_png(received_frames[idx], out_path)
                saved[color_name] = out_path
                if len(saved) == len(VIDEO_COLOR_SEQUENCE):
                    break

            expected_names = {name for name, _ in VIDEO_COLOR_SEQUENCE}
            missing = expected_names - saved.keys()
            assert not missing, (
                f"Did not capture a frame for colors: {missing}. Classified stream: {classified}"
            )
        finally:
            await publisher_room.disconnect()
            await subscriber_room.disconnect()
