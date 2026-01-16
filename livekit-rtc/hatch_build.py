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

"""Custom build hook for platform-specific wheel tagging.

This hook generates py3-none-{platform} wheels because the native FFI libraries
(.so/.dylib/.dll) don't use the Python C API - they're loaded via ctypes at
runtime. This makes them compatible with any Python 3.x version.

Why not use sysconfig.get_platform()?
  - On macOS, it returns the Python interpreter's compile-time deployment target,
    not the MACOSX_DEPLOYMENT_TARGET from the environment that cibuildwheel sets.

Why not let hatchling infer the tag?
  - hatchling doesn't recognize bundled .so/.dylib/.dll as platform-specific
    unless we explicitly set pure_python=False and provide the tag.
"""

import os
import platform
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        build_data["pure_python"] = False
        build_data["infer_tag"] = False
        build_data["tag"] = f"py3-none-{self._get_platform_tag()}"

    def _get_platform_tag(self):
        """Get the wheel platform tag for the current/target platform."""
        if sys.platform == "darwin":
            return self._get_macos_tag()
        elif sys.platform == "linux":
            # Return linux tag; cibuildwheel's auditwheel converts to manylinux
            return f"linux_{platform.machine()}"
        elif sys.platform == "win32":
            return f"win_{self._normalize_arch(platform.machine())}"
        else:
            return f"{platform.system().lower()}_{platform.machine()}"

    def _get_macos_tag(self):
        """Build macOS platform tag respecting cross-compilation settings.

        cibuildwheel sets MACOSX_DEPLOYMENT_TARGET and ARCHFLAGS when building.
        We must use these rather than the host machine's values.
        """
        target = os.environ.get("MACOSX_DEPLOYMENT_TARGET")
        if not target:
            # Fall back to current macOS version (for local dev builds)
            target = platform.mac_ver()[0]
            parts = target.split(".")
            target = f"{parts[0]}.{parts[1] if len(parts) > 1 else '0'}"

        version_tag = target.replace(".", "_")
        arch = self._get_target_arch()
        return f"macosx_{version_tag}_{arch}"

    def _get_target_arch(self):
        """Detect target architecture, respecting ARCHFLAGS for cross-compilation.

        cibuildwheel sets ARCHFLAGS="-arch arm64" or "-arch x86_64" when
        cross-compiling on macOS.
        """
        archflags = os.environ.get("ARCHFLAGS", "")
        if "-arch arm64" in archflags:
            return "arm64"
        if "-arch x86_64" in archflags:
            return "x86_64"
        return self._normalize_arch(platform.machine())

    def _normalize_arch(self, arch):
        """Normalize architecture names to wheel tag format."""
        return {
            "AMD64": "amd64",
            "x86_64": "x86_64",
            "arm64": "arm64",
            "aarch64": "aarch64",
        }.get(arch, arch.lower())
