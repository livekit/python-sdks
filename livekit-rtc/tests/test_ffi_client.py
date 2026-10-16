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

"""FfiClient.request tests against the native library."""

import subprocess
import sys

# Runs in a fresh interpreter: ctypes reuses a `c_ubyte * n` type that another
# live object still holds, which would hide a new one made per request.
_COUNT_ARRAY_TYPES_IN_GARBAGE = """
import ctypes
import gc

from livekit import rtc

gc.collect()
gc.set_debug(gc.DEBUG_SAVEALL)
for _ in range(50):
    rtc.AudioProcessingModule()
gc.collect()
print(sum(isinstance(o, type(ctypes.Array)) for o in gc.garbage))
"""


def test_request_leaves_no_ctypes_array_type_in_garbage() -> None:
    result = subprocess.run(
        [sys.executable, "-c", _COUNT_ARRAY_TYPES_IN_GARBAGE],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "0"
