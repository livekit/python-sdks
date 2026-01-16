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

from sysconfig import get_platform

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """Force platform-specific wheel with py3-none tag.

        The native libraries (.so, .dylib, .dll) are not Python C extensions -
        they're standalone FFI libraries loaded at runtime. This means they
        don't depend on a specific Python version's ABI, so we use py3-none
        to indicate compatibility with any Python 3.x version.
        """
        build_data["pure_python"] = False
        build_data["infer_tag"] = False
        build_data["tag"] = f"py3-none-{get_platform().replace('-', '_').replace('.', '_')}"
