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

"""Custom setup.py for platform-specific wheel tagging.

This file exists solely to customize the wheel platform tag. All package metadata
is defined in pyproject.toml.

The native FFI libraries (.so/.dylib/.dll) require specific platform tags that
respect MACOSX_DEPLOYMENT_TARGET and ARCHFLAGS environment variables set by
cibuildwheel, rather than using sysconfig.get_platform() which returns Python's
compile-time values.
"""

import os
import platform
import sys

import setuptools  # type: ignore
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel  # type: ignore


def get_platform_tag():
    """Get the wheel platform tag for the current/target platform."""
    if sys.platform == "darwin":
        # Get deployment target from environment (set by cibuildwheel) or fall back
        target = os.environ.get("MACOSX_DEPLOYMENT_TARGET")
        if not target:
            target = platform.mac_ver()[0]
            parts = target.split(".")
            target = f"{parts[0]}.{parts[1] if len(parts) > 1 else '0'}"

        version_tag = target.replace(".", "_")

        # Check ARCHFLAGS for cross-compilation (cibuildwheel sets this)
        archflags = os.environ.get("ARCHFLAGS", "")
        if "-arch arm64" in archflags:
            arch = "arm64"
        elif "-arch x86_64" in archflags:
            arch = "x86_64"
        else:
            arch = platform.machine()

        return f"macosx_{version_tag}_{arch}"
    elif sys.platform == "linux":
        return f"linux_{platform.machine()}"
    elif sys.platform == "win32":
        arch = platform.machine()
        if arch == "AMD64":
            arch = "amd64"
        return f"win_{arch}"
    else:
        return f"{platform.system().lower()}_{platform.machine()}"


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        self.plat_name = get_platform_tag()
        _bdist_wheel.finalize_options(self)


setuptools.setup(
    cmdclass={
        "bdist_wheel": bdist_wheel,
    },
)
