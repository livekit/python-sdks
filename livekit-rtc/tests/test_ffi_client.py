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

import ctypes
import gc

from livekit import rtc


def test_request_leaves_no_cyclic_garbage() -> None:
    gc.collect()
    gc.set_debug(gc.DEBUG_SAVEALL)
    try:
        for _ in range(50):
            rtc.AudioProcessingModule()
        gc.collect()
        array_types = [o for o in gc.garbage if isinstance(o, type(ctypes.Array))]
    finally:
        gc.set_debug(0)
        gc.garbage.clear()
    assert array_types == []
