"""Demux opaque VP8/VP9 WebM for pre-encoded media-track publishing."""

from __future__ import annotations

from typing import Iterator

import av
from livekit import rtc


def demux(container: av.container.InputContainer) -> Iterator[rtc.EncodedVideoFrame]:
    """Read timestamped VP8/VP9 packets, including from non-seekable live WebM.

    Media-track publishing does not preserve the WebM container. Reject alpha
    rather than silently dropping data that ordinary VP8/VP9 RTP cannot represent.
    """
    if not container.streams.video:
        raise ValueError("WebM has no video stream")
    stream = container.streams.video[0]
    codecs = {"vp8": rtc.VideoCodec.VP8, "vp9": rtc.VideoCodec.VP9}
    codec = codecs.get(stream.codec_context.name)
    if codec is None:
        raise ValueError("this example supports VP8/VP9 WebM only")
    if stream.metadata.get("alpha_mode") == "1":
        raise ValueError("WebM alpha requires a transport that preserves the WebM container")

    last_timestamp = None
    for packet in container.demux(stream):
        if not packet.size:
            continue  # PyAV's flush sentinel, not a video frame.
        if packet.pts is None or packet.time_base is None:
            raise ValueError("WebM packet is missing its presentation timestamp")
        timestamp = int(packet.pts * packet.time_base * 1_000_000)
        if last_timestamp is not None and timestamp <= last_timestamp:
            raise ValueError("WebM presentation timestamps must increase")
        last_timestamp = timestamp
        data = bytes(packet)
        if packet.get_sidedata("matroska_block_additional"):
            raise ValueError("WebM BlockAdditional cannot be discarded by media-track publishing")
        yield rtc.EncodedVideoFrame(
            data=data,
            width=stream.width,
            height=stream.height,
            codec=codec,
            frame_type=(
                rtc.EncodedFrameType.ENCODED_FRAME_KEY
                if packet.is_keyframe
                else rtc.EncodedFrameType.ENCODED_FRAME_DELTA
            ),
            timestamp_us=timestamp,
        )
