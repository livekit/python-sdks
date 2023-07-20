#!/bin/bash

FFI_PROTOCOL=./client-sdk-rust/livekit-ffi/protocol
OUT_PYTHON=./livekit/_proto

protoc \
    -I=$FFI_PROTOCOL \
    --python_out=$OUT_PYTHON \
    --mypy_out=$OUT_PYTHON \
    $FFI_PROTOCOL/audio_frame.proto \
    $FFI_PROTOCOL/ffi.proto \
    $FFI_PROTOCOL/handle.proto \
    $FFI_PROTOCOL/participant.proto \
    $FFI_PROTOCOL/room.proto \
    $FFI_PROTOCOL/track.proto \
    $FFI_PROTOCOL/video_frame.proto

touch -a "$OUT_PYTHON/__init__.py"

for f in "$OUT_PYTHON"/*.py "$OUT_PYTHON"/*.pyi; do
    perl -i -pe 's|^(import (audio_frame_pb2\|ffi_pb2\|handle_pb2\|participant_pb2\|room_pb2\|track_pb2\|video_frame_pb2))|from . $1|g' "$f"
done

