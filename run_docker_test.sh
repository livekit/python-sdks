#!/usr/bin/env bash
#
# Build the livekit-py-e2e Docker image (if needed) and run e2e_local_test.sh
# inside it. Any args passed are forwarded to pytest via the container's
# entrypoint.
#
# Usage:
#   ./run_docker_test.sh                                  # default: ./tests + livekit-rtc/tests
#   ./run_docker_test.sh -k server_leave                  # filter
#   ./run_docker_test.sh tests/test_connection.py::test_simulate_server_leave
#
# Optional env vars:
#   IMAGE              image tag (default: livekit-py-e2e:latest)
#   DOCKERFILE         path to Dockerfile (default: Dockerfile)
#   FORCE_REBUILD=1    rebuild the image even if it already exists
#   SKIP_BUILD=1       never rebuild; fail if image is missing
#   DOCKER_ARGS        extra args appended to `docker run` (e.g. "--cpus 4")
#   BUILD_LOG          file to tee the docker build output (default: /tmp/docker-build.log)
#   RUN_LOG            file to tee the docker run output (default: /tmp/docker-run.log)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="${IMAGE:-livekit-py-e2e:latest}"
DOCKERFILE="${DOCKERFILE:-${REPO_ROOT}/Dockerfile}"
BUILD_LOG="${BUILD_LOG:-/tmp/docker-build.log}"
RUN_LOG="${RUN_LOG:-/tmp/docker-run.log}"

if ! command -v docker >/dev/null 2>&1; then
    echo "[docker_test] 'docker' not found in PATH." >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "[docker_test] docker daemon is not reachable. Start Docker Desktop / OrbStack / Colima first." >&2
    exit 1
fi

image_exists() {
    docker image inspect "${IMAGE}" >/dev/null 2>&1
}

need_build=0
if [[ "${FORCE_REBUILD:-0}" == "1" ]]; then
    need_build=1
elif ! image_exists; then
    need_build=1
fi

if [[ "${need_build}" -eq 1 ]]; then
    if [[ "${SKIP_BUILD:-0}" == "1" ]]; then
        echo "[docker_test] SKIP_BUILD=1 but image '${IMAGE}' is missing." >&2
        exit 1
    fi
    echo "[docker_test] building ${IMAGE} (log: ${BUILD_LOG})"
    docker build -t "${IMAGE}" -f "${DOCKERFILE}" "${REPO_ROOT}" 2>&1 | tee "${BUILD_LOG}"
else
    echo "[docker_test] reusing existing image ${IMAGE} (set FORCE_REBUILD=1 to rebuild)"
fi

echo "[docker_test] running container (log: ${RUN_LOG})"
# shellcheck disable=SC2086  # DOCKER_ARGS is intentionally word-split.
docker run --rm ${DOCKER_ARGS:-} "${IMAGE}" "$@" 2>&1 | tee "${RUN_LOG}"
