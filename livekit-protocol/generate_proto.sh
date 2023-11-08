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

API_PROTOCOL=./protocol
API_OUT_PYTHON=./livekit/protocol
 
protoc \
    -I=$API_PROTOCOL \
    --python_out=$API_OUT_PYTHON \
    --mypy_out=$API_OUT_PYTHON \
    $API_PROTOCOL/livekit_egress.proto \
    $API_PROTOCOL/livekit_room.proto \
    $API_PROTOCOL/livekit_webhook.proto \
    $API_PROTOCOL/livekit_ingress.proto \
    $API_PROTOCOL/livekit_models.proto \
    $API_PROTOCOL/livekit_agent.proto


touch -a "$API_OUT_PYTHON/__init__.py"


# Patch the proto stubs

# 1. rename the files
# 2. change the imports to relative imports
# 3. add __init__.py to the directory
# 4. remove livekit_ prefix
# 5. remove _pb2 suffix

mv "$API_OUT_PYTHON/livekit_egress_pb2.py" "$API_OUT_PYTHON/egress.py"
mv "$API_OUT_PYTHON/livekit_egress_pb2.pyi" "$API_OUT_PYTHON/egress.pyi"
mv "$API_OUT_PYTHON/livekit_room_pb2.py" "$API_OUT_PYTHON/room.py"
mv "$API_OUT_PYTHON/livekit_room_pb2.pyi" "$API_OUT_PYTHON/room.pyi"
mv "$API_OUT_PYTHON/livekit_webhook_pb2.py" "$API_OUT_PYTHON/webhook.py"
mv "$API_OUT_PYTHON/livekit_webhook_pb2.pyi" "$API_OUT_PYTHON/webhook.pyi"
mv "$API_OUT_PYTHON/livekit_ingress_pb2.py" "$API_OUT_PYTHON/ingress.py"
mv "$API_OUT_PYTHON/livekit_ingress_pb2.pyi" "$API_OUT_PYTHON/ingress.pyi"
mv "$API_OUT_PYTHON/livekit_models_pb2.py" "$API_OUT_PYTHON/models.py"
mv "$API_OUT_PYTHON/livekit_models_pb2.pyi" "$API_OUT_PYTHON/models.pyi"
mv "$API_OUT_PYTHON/livekit_agent_pb2.py" "$API_OUT_PYTHON/agent.py"
mv "$API_OUT_PYTHON/livekit_agent_pb2.pyi" "$API_OUT_PYTHON/agent.pyi"

perl -i -pe 's|^(import (livekit_egress_pb2\|livekit_room_pb2\|livekit_webhook_pb2\|livekit_ingress_pb2\|livekit_models_pb2\|livekit_agent_pb2))|from . $1|g' "$API_OUT_PYTHON"/*.py "$API_OUT_PYTHON"/*.pyi

perl -i -pe 's|livekit_(\w+)_pb2|${1}|g' "$API_OUT_PYTHON"/*.py "$API_OUT_PYTHON"/*.pyi
