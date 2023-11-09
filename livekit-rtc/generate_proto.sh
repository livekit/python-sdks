#!/bin/bash
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
# This script requires protobuf-compiler and https://github.com/nipunn1313/mypy-protobuf

FFI_PROTOCOL=./rust-sdks/livekit-ffi/protocol
FFI_OUT_PYTHON=./livekit/rtc/_proto

# ffi

protoc \
    -I=$FFI_PROTOCOL \
    --python_out=$FFI_OUT_PYTHON \
    --mypy_out=$FFI_OUT_PYTHON \
    $FFI_PROTOCOL/audio_frame.proto \
    $FFI_PROTOCOL/ffi.proto \
    $FFI_PROTOCOL/handle.proto \
    $FFI_PROTOCOL/participant.proto \
    $FFI_PROTOCOL/room.proto \
    $FFI_PROTOCOL/track.proto \
    $FFI_PROTOCOL/video_frame.proto \
    $FFI_PROTOCOL/e2ee.proto \
    $FFI_PROTOCOL/stats.proto

touch -a "$FFI_OUT_PYTHON/__init__.py"

for f in "$FFI_OUT_PYTHON"/*.py "$FFI_OUT_PYTHON"/*.pyi; do
    perl -i -pe 's|^(import (audio_frame_pb2\|ffi_pb2\|handle_pb2\|participant_pb2\|room_pb2\|track_pb2\|video_frame_pb2\|e2ee_pb2\|stats_pb2))|from . $1|g' "$f"
done
