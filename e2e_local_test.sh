#!/usr/bin/env bash
#
# Build the livekit-ffi Rust crate, install it into the livekit-rtc Python
# package, prepare the .test-venv, spin up a local livekit-server (dev mode),
# and run E2E tests against it. Server is killed on exit.
#
# Usage:
#   ./e2e_local_test.sh                                   # run ./tests and livekit-rtc/tests
#   ./e2e_local_test.sh tests/test_connection.py         # run a specific file
#   ./e2e_local_test.sh tests/test_connection.py::test_simulate_server_leave
#                                                         # pass any pytest args through
#
# Optional env vars:
#   SKIP_BUILD=1        skip the cargo build + dylib copy step
#   SKIP_VENV=1         skip creating/refreshing the .test-venv (use existing one)
#   CARGO_PROFILE       cargo profile to build (default: release)
#   VENV_DIR            venv directory (default: .test-venv at repo root)
#   LIVEKIT_SERVER_BIN  path to livekit-server (default: livekit-server on PATH)
#   LIVEKIT_BIND        bind address (default: 127.0.0.1)
#   LIVEKIT_PORT        signal port (default: 7880)
#   SERVER_LOG          server log path (default: /tmp/livekit-server.log)
#   SERVER_READY_TIMEOUT seconds to wait for server to listen (default: 15)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RTC_DIR="${REPO_ROOT}/livekit-rtc"
RUST_DIR="${RTC_DIR}/rust-sdks"
RESOURCES_DIR="${RTC_DIR}/livekit/rtc/resources"

CARGO_PROFILE="${CARGO_PROFILE:-release}"
VENV_DIR="${VENV_DIR:-${REPO_ROOT}/.test-venv}"

LIVEKIT_SERVER_BIN="${LIVEKIT_SERVER_BIN:-livekit-server}"
LIVEKIT_BIND="${LIVEKIT_BIND:-127.0.0.1}"
LIVEKIT_PORT="${LIVEKIT_PORT:-7880}"
SERVER_LOG="${SERVER_LOG:-/tmp/livekit-server.log}"
SERVER_READY_TIMEOUT="${SERVER_READY_TIMEOUT:-15}"

# Dev-mode placeholder credentials baked into livekit-server.
DEV_API_KEY="devkey"
DEV_API_SECRET="secret"

# Pick the platform-specific FFI artifact name.
case "$(uname -s)" in
    Darwin)  FFI_LIB_NAME="liblivekit_ffi.dylib" ;;
    Linux)   FFI_LIB_NAME="liblivekit_ffi.so" ;;
    MINGW*|MSYS*|CYGWIN*) FFI_LIB_NAME="livekit_ffi.dll" ;;
    *) echo "[e2e_local] unsupported platform: $(uname -s)" >&2; exit 1 ;;
esac

if ! command -v "${LIVEKIT_SERVER_BIN}" >/dev/null 2>&1; then
    echo "[e2e_local] '${LIVEKIT_SERVER_BIN}' not found in PATH." >&2
    echo "[e2e_local] Install with: brew install livekit (or see https://docs.livekit.io/home/self-hosting/local/)" >&2
    exit 1
fi

if [[ "${SKIP_BUILD:-0}" != "1" ]]; then
    echo "[e2e_local] building livekit-ffi (${CARGO_PROFILE}) ..."
    (
        cd "${RUST_DIR}"
        if [[ "${CARGO_PROFILE}" == "release" ]]; then
            cargo build --release -p livekit-ffi
        else
            cargo build --profile "${CARGO_PROFILE}" -p livekit-ffi
        fi
    )

    SRC_LIB="${RUST_DIR}/target/${CARGO_PROFILE}/${FFI_LIB_NAME}"
    DST_LIB="${RESOURCES_DIR}/${FFI_LIB_NAME}"

    if [[ ! -f "${SRC_LIB}" ]]; then
        echo "[e2e_local] expected ${SRC_LIB} to exist after build" >&2
        exit 1
    fi

    echo "[e2e_local] installing ${FFI_LIB_NAME} -> ${DST_LIB}"
    mkdir -p "${RESOURCES_DIR}"
    cp "${SRC_LIB}" "${DST_LIB}"
else
    echo "[e2e_local] SKIP_BUILD=1, using existing ${RESOURCES_DIR}/${FFI_LIB_NAME}"
fi

if [[ "${SKIP_VENV:-0}" != "1" ]]; then
    if ! command -v uv >/dev/null 2>&1; then
        echo "[e2e_local] 'uv' not found in PATH; install from https://docs.astral.sh/uv/ or set SKIP_VENV=1" >&2
        exit 1
    fi

    if [[ ! -d "${VENV_DIR}" ]]; then
        echo "[e2e_local] creating venv at ${VENV_DIR}"
        uv venv "${VENV_DIR}"
    fi

    # Reinstall livekit-rtc from local source so the venv tracks the freshly
    # built FFI dylib and any local proto / room.py edits.
    echo "[e2e_local] installing livekit-rtc (and siblings) into ${VENV_DIR}"
    uv pip install --python "${VENV_DIR}" --reinstall \
        "${RTC_DIR}" \
        "${REPO_ROOT}/livekit-api" \
        "${REPO_ROOT}/livekit-protocol"
    uv pip install --python "${VENV_DIR}" \
        pytest pytest-asyncio numpy matplotlib
fi

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    echo "[e2e_local] venv not found at ${VENV_DIR}; re-run without SKIP_VENV=1." >&2
    exit 1
fi

if lsof -nP -iTCP:"${LIVEKIT_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "[e2e_local] port ${LIVEKIT_PORT} is already in use; refusing to start another server." >&2
    exit 1
fi

SERVER_PID=""
cleanup() {
    if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" 2>/dev/null; then
        echo "[e2e_local] stopping livekit-server (pid ${SERVER_PID})"
        kill "${SERVER_PID}" 2>/dev/null || true
        wait "${SERVER_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

echo "[e2e_local] starting ${LIVEKIT_SERVER_BIN} --dev --bind ${LIVEKIT_BIND} (log: ${SERVER_LOG})"
"${LIVEKIT_SERVER_BIN}" --dev --bind "${LIVEKIT_BIND}" >"${SERVER_LOG}" 2>&1 &
SERVER_PID=$!

deadline=$(( $(date +%s) + SERVER_READY_TIMEOUT ))
until lsof -nP -iTCP:"${LIVEKIT_PORT}" -sTCP:LISTEN >/dev/null 2>&1; do
    if ! kill -0 "${SERVER_PID}" 2>/dev/null; then
        echo "[e2e_local] livekit-server exited before becoming ready; see ${SERVER_LOG}" >&2
        exit 1
    fi
    if (( $(date +%s) >= deadline )); then
        echo "[e2e_local] livekit-server did not listen on ${LIVEKIT_PORT} within ${SERVER_READY_TIMEOUT}s; see ${SERVER_LOG}" >&2
        exit 1
    fi
    sleep 0.3
done
echo "[e2e_local] livekit-server ready on ws://${LIVEKIT_BIND}:${LIVEKIT_PORT}"

# Prepend the default test roots when no path-like argument was given, so
# things like `./e2e_local_test.sh -k foo` still target the right directories.
# A path-like arg is one that exists on disk, or looks like a pytest node id
# (contains '::', or starts with 'tests/' / 'livekit-' / '/' / './').
has_path=0
for arg in "$@"; do
    if [[ -e "${arg%%::*}" \
       || "${arg}" == *::* \
       || "${arg}" == tests/* \
       || "${arg}" == livekit-* \
       || "${arg}" == /* \
       || "${arg}" == ./* ]]; then
        has_path=1
        break
    fi
done
if [[ "${has_path}" -eq 0 ]]; then
    set -- "${REPO_ROOT}/tests" "${RTC_DIR}/tests" "$@"
fi

echo "[e2e_local] running pytest: $*"
cd "${RTC_DIR}"
LIVEKIT_URL="ws://${LIVEKIT_BIND}:${LIVEKIT_PORT}" \
LIVEKIT_API_KEY="${DEV_API_KEY}" \
LIVEKIT_API_SECRET="${DEV_API_SECRET}" \
    "${VENV_DIR}/bin/python" -m pytest -v "$@"
