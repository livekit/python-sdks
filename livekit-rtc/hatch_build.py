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

        # Get the platform tag using hatchling's logic (handles MACOSX_DEPLOYMENT_TARGET, etc.)
        from packaging.tags import sys_tags

        tag = next(
            t for t in sys_tags() if "manylinux" not in t.platform and "musllinux" not in t.platform
        )
        platform = tag.platform

        if sys.platform == "darwin":
            from hatchling.builders.macos import process_macos_plat_tag

            platform = process_macos_plat_tag(platform, compat=True)

        build_data["tag"] = f"py3-none-{platform}"
