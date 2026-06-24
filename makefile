.PHONY: help bootstrap install format format-check lint lint-fix check type-check clean build \
        build-rtc build-wheel generate-proto download-ffi status doctor

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m
BOLD := \033[1m

# Paths (computed as absolute paths)
MAKEFILE_DIR := $(shell pwd)
PYTHON_RTC := $(MAKEFILE_DIR)/livekit-rtc
PYTHON_API := $(MAKEFILE_DIR)/livekit-api
PYTHON_PROTOCOL := $(MAKEFILE_DIR)/livekit-protocol
RUST_SUBMODULE := $(MAKEFILE_DIR)/livekit-rtc/rust-sdks

# Platform and architecture auto-detection
ARCH := $(shell uname -m)
OS := $(shell uname -s | tr A-Z a-z)

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BOLD)$(CYAN)Available targets:$(RESET)"
	@echo ""
	@echo "$(BOLD)Development Workflows:$(RESET)"
	@grep -E '^(bootstrap|build-rtc|build-wheel|download-ffi|status|doctor):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)Code Quality:$(RESET)"
	@grep -E '^(format|format-check|lint|lint-fix|type-check|check):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)Other:$(RESET)"
	@grep -E '^(install|clean|build):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'

install: ## Install all dependencies with dev extras
	@echo "$(BOLD)$(CYAN)Installing dependencies...$(RESET)"
	@uv sync --all-extras --dev
	@echo "$(BOLD)$(GREEN)✓ Dependencies installed$(RESET)"

format: ## Format code with ruff
	@echo "$(BOLD)$(CYAN)Formatting code...$(RESET)"
	@uv run ruff format .
	@echo "$(BOLD)$(GREEN)✓ Code formatted$(RESET)"

format-check: ## Check code formatting without making changes
	@echo "$(BOLD)$(CYAN)Checking code formatting...$(RESET)"
	@if uv run ruff format --check .; then \
		echo "$(BOLD)$(GREEN)✓ Code formatting is correct$(RESET)"; \
	else \
		echo "$(BOLD)$(RED)✗ Code formatting issues found. Run 'make format' to fix.$(RESET)"; \
		exit 1; \
	fi

lint: ## Run ruff linter
	@echo "$(BOLD)$(CYAN)Running linter...$(RESET)"
	@if uv run ruff check .; then \
		echo "$(BOLD)$(GREEN)✓ No linting issues found$(RESET)"; \
	else \
		echo "$(BOLD)$(RED)✗ Linting issues found$(RESET)"; \
		exit 1; \
	fi

lint-fix: ## Run ruff linter and fix issues automatically
	@echo "$(BOLD)$(CYAN)Running linter with auto-fix...$(RESET)"
	@uv run ruff check --fix .
	@echo "$(BOLD)$(GREEN)✓ Linting complete$(RESET)"

type-check: ## Run mypy type checker
	@echo "$(BOLD)$(CYAN)Running type checker...$(RESET)"
	@if uv run mypy livekit-protocol livekit-api livekit-rtc livekit-memory; then \
		echo "$(BOLD)$(GREEN)✓ Type checking passed$(RESET)"; \
	else \
		echo "$(BOLD)$(RED)✗ Type checking failed$(RESET)"; \
		exit 1; \
	fi

check: format-check lint type-check ## Run all checks (format, lint, type-check)
	@echo "$(BOLD)$(GREEN)✓ All checks passed!$(RESET)"

# ============================================
# Development Workflows
# ============================================

download-ffi: ## Download pre-built FFI artifacts for livekit-rtc
	@echo "$(BOLD)$(CYAN)📦 Downloading FFI artifacts...$(RESET)"
	@set -e; \
	DETECTED_ARCH="$(ARCH)"; \
	DETECTED_OS="$(OS)"; \
	if [ "$$DETECTED_ARCH" = "aarch64" ]; then \
		PLATFORM_ARCH="arm64"; \
	else \
		PLATFORM_ARCH="$$DETECTED_ARCH"; \
	fi; \
	if [ "$$DETECTED_OS" = "darwin" ]; then \
		PLATFORM_OS="macos"; \
	else \
		PLATFORM_OS="$$DETECTED_OS"; \
	fi; \
	echo "$(CYAN)   Platform: $$PLATFORM_OS-$$PLATFORM_ARCH$(RESET)"; \
	cd $(PYTHON_RTC) && python rust-sdks/download_ffi.py --platform "$$PLATFORM_OS" --arch "$$PLATFORM_ARCH" --output livekit/rtc/resources; \
	echo "$(BOLD)$(GREEN)✅ FFI artifacts downloaded$(RESET)"

build-rtc: ## Build livekit-ffi from local rust-sdks and generate proto
	@echo "$(BOLD)$(CYAN)🦀 Building livekit-ffi from source...$(RESET)"
	@set -e; \
	if [ ! -d "$(RUST_SUBMODULE)" ]; then \
		echo "$(BOLD)$(RED)✗ Error: rust-sdks submodule not found at $(RUST_SUBMODULE)$(RESET)"; \
		exit 1; \
	fi; \
	echo "$(CYAN)🦀 Building livekit-ffi...$(RESET)"; \
	cd $(RUST_SUBMODULE) && cargo build --release -p livekit-ffi; \
	echo "$(CYAN)📝 Generating protobuf FFI protocol...$(RESET)"; \
	cd $(PYTHON_RTC) && ./generate_proto.sh; \
	RUST_LIB_DIR="$$(cd $(RUST_SUBMODULE) && pwd)/target/release"; \
	if [ "$(OS)" = "darwin" ]; then \
		RUST_LIB_PATH="$$RUST_LIB_DIR/liblivekit_ffi.dylib"; \
	elif [ "$(OS)" = "linux" ]; then \
		RUST_LIB_PATH="$$RUST_LIB_DIR/liblivekit_ffi.so"; \
	else \
		RUST_LIB_PATH="$$RUST_LIB_DIR/livekit_ffi.dll"; \
	fi; \
	echo "$(BOLD)$(GREEN)✅ Built livekit-ffi from source$(RESET)"; \
	echo ""; \
	echo "$(BOLD)$(YELLOW)📋 To use the local rust lib, export the following:$(RESET)"; \
	echo "$(BOLD)   export LIVEKIT_LIB_PATH=$$RUST_LIB_PATH$(RESET)"

build-wheel: ## Build wheel for a package (usage: make build-wheel PACKAGE=livekit-rtc)
	@echo "$(BOLD)$(CYAN)📦 Building wheel...$(RESET)"
	@set -e; \
	if [ -z "$(PACKAGE)" ]; then \
		echo "$(BOLD)$(RED)✗ Error: PACKAGE parameter is required$(RESET)"; \
		echo "$(YELLOW)Usage: make build-wheel PACKAGE=<package-name>$(RESET)"; \
		echo "$(YELLOW)Available packages: livekit-rtc, livekit-api, livekit-protocol$(RESET)"; \
		exit 1; \
	fi; \
	PACKAGE_PATH="$(MAKEFILE_DIR)/$(PACKAGE)"; \
	if [ ! -d "$$PACKAGE_PATH" ]; then \
		echo "$(BOLD)$(RED)✗ Error: Package directory not found: $$PACKAGE_PATH$(RESET)"; \
		exit 1; \
	fi; \
	if [ ! -f "$$PACKAGE_PATH/pyproject.toml" ]; then \
		echo "$(BOLD)$(RED)✗ Error: pyproject.toml not found in $$PACKAGE_PATH$(RESET)"; \
		exit 1; \
	fi; \
	echo "$(CYAN)   Package: $(PACKAGE)$(RESET)"; \
	echo "$(CYAN)   Building in: $$PACKAGE_PATH$(RESET)"; \
	cd "$$PACKAGE_PATH" && uv build --out-dir ./dist; \
	echo "$(BOLD)$(GREEN)✅ Wheel built successfully$(RESET)"; \
	echo "$(CYAN)   Output: $$PACKAGE_PATH/dist/$(RESET)"

status: ## Show current development environment status
	@echo "$(BOLD)$(CYAN)📍 Current status:$(RESET)"
	@echo ""
	@set -e; \
	echo "$(BOLD)📦 Packages:$(RESET)"; \
	for pkg in livekit livekit-api livekit-protocol; do \
		SHOW_OUTPUT=$$(uv pip show $$pkg 2>/dev/null || echo ""); \
		if [ -z "$$SHOW_OUTPUT" ]; then \
			echo "   $$pkg: NOT INSTALLED"; \
		elif echo "$$SHOW_OUTPUT" | grep -q "Editable project location:"; then \
			VERSION=$$(echo "$$SHOW_OUTPUT" | grep "^Version:" | awk '{print $$2}'); \
			LOCATION=$$(echo "$$SHOW_OUTPUT" | grep "Editable project location:" | cut -d' ' -f4-); \
			echo "   $$pkg: LOCAL (editable) v$$VERSION"; \
			echo "      path: $$LOCATION"; \
		else \
			VERSION=$$(echo "$$SHOW_OUTPUT" | grep "^Version:" | awk '{print $$2}'); \
			echo "   $$pkg: PyPI v$$VERSION"; \
		fi; \
	done; \
	echo ""; \
	echo "$(BOLD)🦀 FFI Status:$(RESET)"; \
	if [ -n "$$LIVEKIT_LIB_PATH" ]; then \
		if [ -f "$$LIVEKIT_LIB_PATH" ]; then \
			echo "   FFI: CUSTOM (from LIVEKIT_LIB_PATH env var)"; \
			echo "   path: $$LIVEKIT_LIB_PATH"; \
		else \
			echo "   FFI: CUSTOM (LIVEKIT_LIB_PATH set but file not found)"; \
			echo "   path: $$LIVEKIT_LIB_PATH"; \
		fi; \
	else \
		FFI_PATH="$(PYTHON_RTC)/livekit/rtc/resources"; \
		if [ -d "$$FFI_PATH" ] && { [ -f "$$FFI_PATH/liblivekit_ffi.dylib" ] || [ -f "$$FFI_PATH/liblivekit_ffi.so" ] || [ -f "$$FFI_PATH/livekit_ffi.dll" ]; }; then \
			RUST_SUBMODULE_DIR="$$(cd $(RUST_SUBMODULE) 2>/dev/null && pwd || echo "")"; \
			CARGO_TOML_PATH="$$RUST_SUBMODULE_DIR/livekit-ffi/Cargo.toml"; \
			if [ -f "$$CARGO_TOML_PATH" ]; then \
				FFI_VERSION=$$(grep '^version = ' "$$CARGO_TOML_PATH" | head -1 | sed 's/.*"\(.*\)".*/\1/'); \
				echo "   FFI: PRE-BUILT ARTIFACTS (v$$FFI_VERSION)"; \
			else \
				echo "   FFI: PRE-BUILT ARTIFACTS"; \
			fi; \
		else \
			echo "   FFI: NOT AVAILABLE (run 'make download-ffi')"; \
		fi; \
	fi

doctor: ## Check development environment health
	@echo "$(BOLD)$(CYAN)🏥 Running diagnostics...$(RESET)"
	@echo ""
	@ISSUES=0; \
	echo "$(BOLD)📦 Required Tools:$(RESET)"; \
	if command -v uv &> /dev/null; then \
		UV_VERSION=$$(uv --version 2>&1 | head -1); \
		echo "   ✓ uv: $$UV_VERSION"; \
	else \
		echo "   ✗ uv: NOT FOUND"; \
		ISSUES=$$((ISSUES + 1)); \
	fi; \
	if command -v python &> /dev/null; then \
		PYTHON_VERSION=$$(python --version 2>&1); \
		echo "   ✓ python: $$PYTHON_VERSION"; \
	else \
		echo "   ✗ python: NOT FOUND"; \
		ISSUES=$$((ISSUES + 1)); \
	fi; \
	if command -v cargo &> /dev/null; then \
		CARGO_VERSION=$$(cargo --version 2>&1); \
		echo "   ✓ cargo: $$CARGO_VERSION"; \
	else \
		echo "   ⚠ cargo: NOT FOUND (required for 'make build-rtc')"; \
	fi; \
	if command -v git &> /dev/null; then \
		GIT_VERSION=$$(git --version 2>&1); \
		echo "   ✓ git: $$GIT_VERSION"; \
	else \
		echo "   ✗ git: NOT FOUND"; \
		ISSUES=$$((ISSUES + 1)); \
	fi; \
	echo ""; \
	echo "$(BOLD)📂 Repository Structure:$(RESET)"; \
	REPO_ROOT=$$(cd $(MAKEFILE_DIR) && git rev-parse --show-toplevel 2>/dev/null || echo ""); \
	if [ -n "$$REPO_ROOT" ]; then \
		BRANCH=$$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"); \
		COMMIT=$$(git rev-parse --short HEAD 2>/dev/null || echo "unknown"); \
		echo "   ✓ python-sdks: $$REPO_ROOT"; \
		echo "      Branch: $$BRANCH @ $$COMMIT"; \
	fi; \
	if [ -d "$(PYTHON_RTC)" ]; then \
		echo "   ✓ livekit-rtc: $(PYTHON_RTC)"; \
	else \
		echo "   ✗ livekit-rtc: NOT FOUND"; \
		ISSUES=$$((ISSUES + 1)); \
	fi; \
	if [ -d "$(PYTHON_API)" ]; then \
		echo "   ✓ livekit-api: $(PYTHON_API)"; \
	else \
		echo "   ✗ livekit-api: NOT FOUND"; \
		ISSUES=$$((ISSUES + 1)); \
	fi; \
	if [ -d "$(PYTHON_PROTOCOL)" ]; then \
		echo "   ✓ livekit-protocol: $(PYTHON_PROTOCOL)"; \
	else \
		echo "   ✗ livekit-protocol: NOT FOUND"; \
		ISSUES=$$((ISSUES + 1)); \
	fi; \
	if [ -d "$(RUST_SUBMODULE)" ]; then \
		echo "   ✓ rust-sdks: $(RUST_SUBMODULE)"; \
		if [ -e "$(RUST_SUBMODULE)/.git" ]; then \
			RUST_BRANCH=$$(cd $(RUST_SUBMODULE) && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"); \
			RUST_COMMIT=$$(cd $(RUST_SUBMODULE) && git rev-parse --short HEAD 2>/dev/null || echo "unknown"); \
			echo "      Branch: $$RUST_BRANCH @ $$RUST_COMMIT"; \
		fi; \
	else \
		echo "   ⚠ rust-sdks: NOT FOUND (needed for 'make build-rtc')"; \
	fi; \
	echo ""; \
	echo "$(BOLD)🔍 Current Configuration:$(RESET)"; \
	if [ -d ".venv" ]; then \
		echo "   ✓ Virtual environment: .venv exists"; \
	else \
		echo "   ⚠ Virtual environment: .venv not found (run 'make install')"; \
	fi; \
	for pkg in livekit livekit-api livekit-protocol; do \
		SHOW_OUTPUT=$$(uv pip show $$pkg 2>/dev/null || echo ""); \
		if [ -z "$$SHOW_OUTPUT" ]; then \
			echo "   ✗ $$pkg: NOT INSTALLED"; \
		elif echo "$$SHOW_OUTPUT" | grep -q "Editable project location:"; then \
			VERSION=$$(echo "$$SHOW_OUTPUT" | grep "^Version:" | awk '{print $$2}'); \
			echo "   ✓ $$pkg: LOCAL (editable) v$$VERSION"; \
		else \
			VERSION=$$(echo "$$SHOW_OUTPUT" | grep "^Version:" | awk '{print $$2}'); \
			echo "   ✓ $$pkg: PyPI v$$VERSION"; \
		fi; \
	done; \
	if [ -n "$$LIVEKIT_LIB_PATH" ]; then \
		if [ -f "$$LIVEKIT_LIB_PATH" ]; then \
			echo "   ✓ FFI: Custom build from LIVEKIT_LIB_PATH"; \
		else \
			echo "   ✗ FFI: LIVEKIT_LIB_PATH set but file not found: $$LIVEKIT_LIB_PATH"; \
			ISSUES=$$((ISSUES + 1)); \
		fi; \
	fi; \
	echo ""; \
	if [ $$ISSUES -eq 0 ]; then \
		echo "$(BOLD)$(GREEN)✅ All checks passed! Environment is healthy.$(RESET)"; \
	else \
		echo "$(BOLD)$(RED)⚠️  Found $$ISSUES issue(s). Please fix the errors above.$(RESET)"; \
		exit 1; \
	fi

bootstrap: ## Sync repo, deps, and assets to a working dev state (safe to re-run)
	@echo "$(BOLD)$(CYAN)🔄 Syncing development environment...$(RESET)"
	@git submodule update --init --recursive
	@git lfs install
	@git lfs pull
	@$(MAKE) install
	@$(MAKE) download-ffi
	@echo "$(BOLD)$(GREEN)✓ Sync complete$(RESET)"