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

from __future__ import annotations

import gc
import subprocess
import sys

import pytest

from livekit.rtc._ffi_client import FfiClient, FfiHandle
from livekit.rtc._proto import audio_frame_pb2, ffi_pb2


def _allocate_real_handle() -> int:
    req = ffi_pb2.FfiRequest()
    req.new_audio_source.type = audio_frame_pb2.AUDIO_SOURCE_NATIVE
    req.new_audio_source.sample_rate = 48000
    req.new_audio_source.num_channels = 1
    req.new_audio_source.queue_size_ms = 100
    resp = FfiClient.instance.request(req)
    handle_id = resp.new_audio_source.source.handle.id
    assert handle_id != 0
    return int(handle_id)


def test_active_runtime_invalid_handle_asserts() -> None:
    FfiClient.instance
    with pytest.raises(AssertionError):
        FfiHandle(999999).dispose()


def test_live_handles_marked_consumed_and_no_assert_after_dispose() -> None:
    handle_id = _allocate_real_handle()
    handle = FfiHandle(handle_id)
    assert not handle.disposed

    # Global dispose marks all live handles consumed and sets _ffi_disposed
    FfiClient.instance._dispose()
    assert handle.disposed

    # Explicit dispose or __del__ after global dispose should be a no-op and not assert
    handle.dispose()
    handle.__del__()

    # Newly instantiated handle after global dispose also safely no-ops without assert
    late_handle = FfiHandle(12345)
    late_handle.dispose()

    del handle
    del late_handle
    gc.collect()


def test_subprocess_exit_with_undisposed_handle_has_no_assertion_error() -> None:
    code = """
import sys
from livekit.rtc._proto import audio_frame_pb2, ffi_pb2
from livekit.rtc._ffi_client import FfiClient, FfiHandle

req = ffi_pb2.FfiRequest()
req.new_audio_source.type = audio_frame_pb2.AUDIO_SOURCE_NATIVE
req.new_audio_source.sample_rate = 48000
req.new_audio_source.num_channels = 1
req.new_audio_source.queue_size_ms = 100
resp = FfiClient.instance.request(req)
handle_id = resp.new_audio_source.source.handle.id
# Leave handle alive at process shutdown
global_handle = FfiHandle(handle_id)
sys.exit(0)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "AssertionError" not in result.stderr
    assert "Exception ignored" not in result.stderr
