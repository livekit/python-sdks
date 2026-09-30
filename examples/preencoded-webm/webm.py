"""Demux WebM without decoding; prototype a single-track VP9 alpha envelope.

The alpha envelope is experimental, not a negotiated LiveKit or WebRTC format.
It requires a matching receiver to strip it before invoking a video decoder.
"""

from __future__ import annotations

import struct
from typing import Iterator

import av
from livekit import rtc

# Provisional wire format for isolated interoperability experiments only:
# [color access unit][alpha access unit][color_len:u32][alpha_len:u32][LKWA][v1]
# Both lengths are big endian. The footer is inside the encoded frame, before
# any native LiveKit metadata trailer. Do not reuse the 255-byte LKTS metadata
# envelope: alpha access units can span many RTP packets.
_FOOTER = struct.Struct(">II4sB")
_MAX_FRAME_BYTES = 16 * 1024 * 1024


def pack_alpha(color: bytes, alpha: bytes) -> bytes:
    """Package two compressed VP9 access units without inspecting their pixels."""
    if not color or not alpha:
        raise ValueError("color and alpha access units must not be empty")
    if len(color) + len(alpha) + _FOOTER.size > _MAX_FRAME_BYTES:
        raise ValueError("alpha envelope exceeds the 16 MiB example limit")
    return color + alpha + _FOOTER.pack(len(color), len(alpha), b"LKWA", 1)


def unpack_alpha(data: bytes) -> tuple[bytes, bytes]:
    """Validate the experimental envelope and return its compressed components.

    Included to specify and test the wire contract, not as a playback adapter.
    """
    if not _FOOTER.size < len(data) <= _MAX_FRAME_BYTES:
        raise ValueError("invalid alpha envelope size")
    color_size, alpha_size, magic, version = _FOOTER.unpack_from(data, len(data) - _FOOTER.size)
    if magic != b"LKWA" or version != 1:
        raise ValueError("unknown alpha envelope")
    if not color_size or not alpha_size or color_size + alpha_size != len(data) - _FOOTER.size:
        raise ValueError("invalid alpha envelope lengths")
    return data[:color_size], data[color_size : -_FOOTER.size]


def demux(
    container: av.container.InputContainer, *, experimental_alpha: bool = False
) -> Iterator[rtc.EncodedVideoFrame]:
    """Read timestamped VP8/VP9 packets, including from non-seekable live WebM.

    Alpha is rejected by default rather than silently discarded. The opt-in
    prototype requires VP9 and an alpha access unit in every packet; sparse alpha
    and changing dimensions are outside this example's scope.
    """
    if not container.streams.video:
        raise ValueError("WebM has no video stream")
    stream = container.streams.video[0]
    codecs = {"vp8": rtc.VideoCodec.VP8, "vp9": rtc.VideoCodec.VP9}
    codec = codecs.get(stream.codec_context.name)
    if codec is None:
        raise ValueError("this example supports VP8/VP9 WebM only")
    has_alpha = stream.metadata.get("alpha_mode") == "1"
    if has_alpha and not experimental_alpha:
        raise ValueError(
            "WebM has alpha; use the experimental alpha receiver/profile or an opaque source"
        )
    if experimental_alpha and (not has_alpha or codec != rtc.VideoCodec.VP9):
        raise ValueError("experimental alpha requires VP9 WebM with AlphaMode=1")

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
        additional = bytes(packet.get_sidedata("matroska_block_additional"))
        if additional:
            if len(additional) <= 8 or int.from_bytes(additional[:8], "big") != 1:
                raise ValueError("unsupported WebM BlockAdditional mapping")
            if not experimental_alpha:
                raise ValueError("WebM alpha cannot be discarded implicitly")
            data = pack_alpha(data, additional[8:])
        elif experimental_alpha:
            raise ValueError("missing alpha access unit in WebM packet")
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
