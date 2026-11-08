#!/usr/bin/env bash
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

# Regenerates ../livekit/api/_public_api from openapi.yaml with OpenAPI Generator
# (python generator, asyncio library: aiohttp + pydantic), keeping only the
# operations the thread and database services call. Requires java and uv.
#
#   ./generate.sh                            regenerate from the vendored openapi.yaml
#   ./generate.sh <public-api-server> [ref]  vendor pkg/api/v1/openapi.yaml at ref
#                                            (default origin/main) first

set -euo pipefail
cd "$(dirname "$0")"

GENERATOR_VERSION=7.26.0
GENERATOR_SHA256=1760050094997b9cc790cc1350be095f15da8c08a996b184d3eadc4ccda5e35e
OPERATIONS=(
    ThreadService_CreateThread
    ThreadService_GetThread
    ThreadService_ListThreads
    ThreadService_UpdateThread
    ThreadService_DeleteThread
    ThreadService_GetThreadItems
    ThreadService_GetThreadTasks
    DatabaseService_CreateDatabase
    DatabaseService_GetDatabase
    DatabaseService_ListDatabases
    DatabaseService_DeleteDatabase
    DatabaseService_ExportDatabase
)

if [ $# -ge 1 ]; then
    SERVER=$1
    REF=${2:-origin/main}
    SHA=$(git -C "$SERVER" rev-parse "$REF")
    {
        echo "# Vendored from livekit/public-api-server@$SHA:pkg/api/v1/openapi.yaml"
        echo "# Regenerate the client with generate.sh; do not edit by hand."
        git -C "$SERVER" show "$SHA:pkg/api/v1/openapi.yaml"
    } > openapi.yaml
fi

JAR_DIR=${XDG_CACHE_HOME:-$HOME/.cache}/openapi-generator
JAR=$JAR_DIR/openapi-generator-cli-$GENERATOR_VERSION.jar
if [ ! -f "$JAR" ]; then
    mkdir -p "$JAR_DIR"
    curl -sSfL -o "$JAR.tmp" \
        "https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/$GENERATOR_VERSION/openapi-generator-cli-$GENERATOR_VERSION.jar"
    mv "$JAR.tmp" "$JAR"
fi
echo "$GENERATOR_SHA256  $JAR" | shasum -a 256 -c - > /dev/null

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# Keep the listed operations and the schemas they reference.
uv run --quiet --no-project --with pyyaml==6.0.2 python - openapi.yaml "$WORK/spec.yaml" "${OPERATIONS[@]}" <<'EOF'
import sys

import yaml

src, dst, *operations = sys.argv[1:]
spec = yaml.safe_load(open(src))
wanted = set(operations)
paths = {}
for path, item in spec["paths"].items():
    kept = {m: op for m, op in item.items() if op.get("operationId") in wanted}
    if kept:
        paths[path] = kept
missing = wanted - {op["operationId"] for item in paths.values() for op in item.values()}
if missing:
    sys.exit(f"openapi.yaml lacks operations: {sorted(missing)}")

schemas = spec["components"]["schemas"]
# Name each inline request body after its operation (ThreadService_CreateThread ->
# ThreadServiceCreateThreadBody) rather than the generator's Request, Request1, ...
for item in paths.values():
    for op in item.values():
        content = op.get("requestBody", {}).get("content", {}).get("application/json")
        if content and "$ref" not in content["schema"]:
            name = op["operationId"].replace("_", "") + "Body"
            schemas[name] = content["schema"]
            content["schema"] = {"$ref": f"#/components/schemas/{name}"}

keep: set = set()


def walk(node):
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            name = ref.rsplit("/", 1)[1]
            if name not in keep:
                keep.add(name)
                walk(schemas[name])
        for value in node.values():
            walk(value)
    elif isinstance(node, list):
        for value in node:
            walk(value)


walk(paths)
spec["paths"] = paths
spec["components"]["schemas"] = {k: v for k, v in schemas.items() if k in keep}
yaml.safe_dump(spec, open(dst, "w"), sort_keys=False)
EOF

java -jar "$JAR" generate \
    --input-spec "$WORK/spec.yaml" \
    --generator-name python \
    --library asyncio \
    --package-name livekit.api._public_api \
    --output "$WORK/out" \
    --additional-properties generateSourceCodeOnly=true \
    --global-property apiTests=false,modelTests=false,apiDocs=false,modelDocs=false \
    > "$WORK/generator.log" 2>&1 || { cat "$WORK/generator.log"; exit 1; }

OUT=../livekit/api/_public_api
rm -rf "$OUT"
mv "$WORK/out/livekit/api/_public_api" "$OUT"
rm -f "$OUT/README.md" "$OUT"/*.md
