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

import os
import platform
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """Force platform-specific wheel with py3-none tag.

        The native libraries (.so, .dylib, .dll) are not Python C extensions -
        they're standalone FFI libraries loaded at runtime. This means they
        don't depend on a specific CPython ABI, so we use py3-none to indicate
        compatibility with any Python 3.x version while keeping the platform tag.
        """
        build_data["pure_python"] = False
        build_data["infer_tag"] = False

        if sys.platform == "darwin":
            plat_tag = self._get_macos_platform_tag()
        else:
            from packaging.tags import sys_tags

            tag = next(
                t
                for t in sys_tags()
                if "manylinux" not in t.platform and "musllinux" not in t.platform
            )
            plat_tag = tag.platform

        build_data["tag"] = f"py3-none-{plat_tag}"

    def _get_macos_platform_tag(self):
        """Build macOS platform tag from MACOSX_DEPLOYMENT_TARGET env var."""
        deployment_target = os.environ.get("MACOSX_DEPLOYMENT_TARGET")
        if not deployment_target:
            # Fall back to current macOS version
            deployment_target = platform.mac_ver()[0]
            # Use only major.minor
            parts = deployment_target.split(".")
            deployment_target = f"{parts[0]}.{parts[1] if len(parts) > 1 else '0'}"

        # Convert version to wheel tag format (e.g., "11.0" -> "11_0")
        version_tag = deployment_target.replace(".", "_")

        # Get architecture
        machine = platform.machine()
        if machine == "x86_64":
            arch = "x86_64"
        elif machine == "arm64":
            arch = "arm64"
        else:
            arch = machine

        return f"macosx_{version_tag}_{arch}"
