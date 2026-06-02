# Run the e2e_local_test.sh suite inside a container.
#
# Build:
#   docker build -t livekit-py-e2e .
# Run:
#   docker run --rm livekit-py-e2e                 # full run (build FFI + tests)
#   docker run --rm livekit-py-e2e -k server_leave # pass args through to pytest
#
# The image bundles livekit-server, the Rust toolchain, uv, and the system
# libraries needed to build livekit-ffi. The repo is copied to /workspace and
# e2e_local_test.sh is the entrypoint.

FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/root/.cargo/bin:/root/.local/bin:${PATH} \
    CARGO_HOME=/root/.cargo \
    RUSTUP_HOME=/root/.rustup

# System deps: build toolchain for livekit-ffi, lsof for port probing in the
# script, curl/ca-certificates/git for fetching toolchains and sources.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        clang \
        cmake \
        curl \
        git \
        libasound2-dev \
        libclang-dev \
        libdbus-1-dev \
        libgbm-dev \
        libgl1-mesa-dev \
        libglib2.0-dev \
        libpulse-dev \
        libssl-dev \
        libudev-dev \
        libx11-dev \
        libxcomposite-dev \
        libxcursor-dev \
        libxdamage-dev \
        libxext-dev \
        libxfixes-dev \
        libxi-dev \
        libxinerama-dev \
        libxrandr-dev \
        libxrender-dev \
        libxss-dev \
        libxtst-dev \
        lld \
        lsof \
        nasm \
        ninja-build \
        pkg-config \
        procps \
        protobuf-compiler \
        python3-dev \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Rust toolchain (livekit-ffi build).
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --default-toolchain stable --profile minimal

# uv (used by the script to create / populate .test-venv).
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# livekit-server (dev-mode binary; arch-aware). The release filename includes
# the version, so we look up the latest tag via the GitHub API first.
RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "${arch}" in \
        amd64|arm64|armv7) ;; \
        *) echo "unsupported arch: ${arch}" >&2; exit 1 ;; \
    esac; \
    version="$(curl -fsSL https://api.github.com/repos/livekit/livekit/releases/latest \
        | sed -n 's/.*\"tag_name\": *\"v\([^\"]*\)\".*/\1/p')"; \
    test -n "${version}"; \
    url="https://github.com/livekit/livekit/releases/download/v${version}/livekit_${version}_linux_${arch}.tar.gz"; \
    echo "fetching ${url}"; \
    curl -fsSL "${url}" -o /tmp/livekit.tgz; \
    tar -xzf /tmp/livekit.tgz -C /usr/local/bin livekit-server; \
    rm /tmp/livekit.tgz; \
    livekit-server --version

WORKDIR /workspace

# Copy the repo. .dockerignore should keep .test-venv, target/, node_modules
# etc. out of the build context (see the file next to this Dockerfile).
COPY . /workspace

RUN chmod +x /workspace/e2e_local_test.sh

ENTRYPOINT ["/workspace/e2e_local_test.sh"]
CMD []
