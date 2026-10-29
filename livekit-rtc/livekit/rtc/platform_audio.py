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

"""
PlatformAudio - Platform audio device management via WebRTC's ADM

PlatformAudio provides access to the platform's audio devices (microphones and
speakers) via WebRTC's Audio Device Module (ADM). This is the recommended way
to handle audio in most applications because:

- Built-in echo cancellation (AEC), noise suppression (NS), and auto gain control (AGC)
- Automatic device enumeration and selection
- Efficient hardware-accelerated audio processing on supported platforms
- No need for external audio libraries

For custom audio processing pipelines where you need direct access to audio frames,
use the synthetic mode with AudioSource instead. See AudioSource for more details.

# Usage

```python
from livekit import rtc

# Create PlatformAudio instance (enables ADM)
platform_audio = rtc.PlatformAudio()

# List available devices
print("Microphones:")
for device in platform_audio.recording_devices():
    print(f"  [{device.index}] {device.name} (ID: {device.id})")

print("Speakers:")
for device in platform_audio.playout_devices():
    print(f"  [{device.index}] {device.name} (ID: {device.id})")

# Select specific devices (optional - uses default if not called)
platform_audio.set_recording_device(mic_device.id)
platform_audio.set_playout_device(speaker_device.id)

# Create audio source for publishing
audio_source = platform_audio.create_audio_source()

# Create and publish track
track = rtc.LocalAudioTrack.create_audio_track("microphone", audio_source)
await room.local_participant.publish_track(track)
```

# Limitations

- No direct access to captured audio frames (ADM sends directly to WebRTC)
- For frame-level processing, use synthetic mode with AudioSource.capture_frame()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ._ffi_client import FfiHandle, FfiClient
from ._proto import audio_frame_pb2 as proto_audio_frame
from ._proto import ffi_pb2 as proto_ffi


class PlatformAudioError(Exception):
    """Exception raised when PlatformAudio operations fail."""

    pass


@dataclass
class AudioDeviceInfo:
    """Information about an audio device.

    Attributes:
        index: Device index (0-based). Note: indices can change when devices are
            added/removed, so prefer using `id` for device selection.
        name: Device name as reported by the operating system.
        id: Platform-specific unique device identifier (GUID). This is stable across
            device additions/removals and should be preferred over index for device
            selection.
    """

    index: int
    name: str
    id: str

    @classmethod
    def _from_proto(cls, proto: proto_audio_frame.AudioDeviceInfo) -> "AudioDeviceInfo":
        return cls(index=proto.index, name=proto.name, id=proto.guid)


@dataclass
class PlatformAudioOptions:
    """Audio processing options for PlatformAudio.

    These options configure WebRTC's audio processing pipeline when using
    PlatformAudio for microphone capture.

    Attributes:
        echo_cancellation: Enable acoustic echo cancellation (AEC) to remove
            echo from speaker playback. Default: True.
        noise_suppression: Enable noise suppression to remove background noise.
            Default: True.
        auto_gain_control: Enable automatic gain control to normalize audio levels.
            Default: True.
        prefer_hardware: Prefer hardware audio processing when available.
            - iOS: Uses Voice Processing I/O (VPIO) for low-latency processing
            - Android: Hardware support varies by device
            - Desktop: Generally not available
            Default: True on iOS, False on other platforms.
    """

    echo_cancellation: bool = True
    noise_suppression: bool = True
    auto_gain_control: bool = True
    prefer_hardware: bool = False

    def _to_proto(self) -> proto_audio_frame.AudioSourceOptions:
        return proto_audio_frame.AudioSourceOptions(
            echo_cancellation=self.echo_cancellation,
            noise_suppression=self.noise_suppression,
            auto_gain_control=self.auto_gain_control,
            prefer_hardware=self.prefer_hardware,
        )


class PlatformAudioSource:
    """Audio source backed by PlatformAudio (WebRTC ADM).

    This source captures audio from the selected microphone via the platform's
    Audio Device Module. Unlike AudioSource (synthetic mode), frames are captured
    and sent directly by the ADM - there is no `capture_frame()` method.

    Use this with LocalAudioTrack.create_audio_track() to publish microphone audio.

    Note: This class is created via PlatformAudio.create_audio_source() and should
    not be instantiated directly.

    Resource Management:
        Call `close()` when done to immediately release native resources. If not
        called, resources are released when the object is garbage collected, but
        GC timing is non-deterministic and may cause issues on some platforms
        (especially Windows) where audio device handles must be released promptly.
    """

    def __init__(self, ffi_handle: FfiHandle, info: proto_audio_frame.AudioSourceInfo):
        self._ffi_handle = ffi_handle
        self._info = info

    @property
    def _handle(self) -> int:
        """Internal FFI handle for use with LocalAudioTrack.create_audio_track()."""
        return self._ffi_handle.handle

    def close(self) -> None:
        """Release the native audio source resources.

        Call this method when you are done using the audio source to immediately
        release the underlying native handle. This is especially important on
        Windows where audio device handles must be released promptly to avoid
        interfering with other audio operations.

        If `close()` is not called, resources will be released when the object
        is garbage collected. However, Python's garbage collection timing is
        non-deterministic, which can lead to:
        - Audio device contention if creating new audio sources before old ones
          are collected
        - Test failures when running multiple audio tests in sequence
        - Resource leaks in long-running applications that frequently create
          and discard audio sources

        It is safe to call `close()` multiple times; subsequent calls are no-ops.
        """
        self._ffi_handle.dispose()


class PlatformAudio:
    """Platform audio device management via WebRTC's Audio Device Module (ADM).

    PlatformAudio provides the recommended way to handle audio capture and playback
    in LiveKit applications. It uses WebRTC's ADM for efficient, hardware-accelerated
    audio processing with built-in echo cancellation, noise suppression, and
    automatic gain control.

    Key features:
    - Device enumeration: List available microphones and speakers
    - Device selection: Choose specific input/output devices
    - Audio processing: Built-in AEC, NS, and AGC
    - Automatic playout: Received audio is automatically played through speakers

    Example:
        ```python
        # Create PlatformAudio (keeps ADM alive)
        platform_audio = rtc.PlatformAudio()

        # Enumerate and select devices
        mics = platform_audio.recording_devices()
        platform_audio.set_recording_device(mics[0].id)

        # Create source and publish track
        source = platform_audio.create_audio_source()
        track = rtc.LocalAudioTrack.create_audio_track("mic", source)
        await room.local_participant.publish_track(track)

        # When done, close resources
        source.close()
        platform_audio.close()
        ```

    Resource Management:
        Call `close()` when done to immediately release native ADM resources.
        If not called, resources are released via garbage collection, but GC
        timing is non-deterministic. On Windows especially, failing to promptly
        release ADM resources can cause audio device contention and interfere
        with subsequent audio operations (including synthetic AudioSource usage).
    """

    def __init__(self) -> None:
        """Initialize PlatformAudio and enable the Audio Device Module.

        Raises:
            PlatformAudioError: If ADM initialization fails.
        """
        req = proto_ffi.FfiRequest()
        req.new_platform_audio.SetInParent()

        resp = FfiClient.instance.request(req)

        if resp.new_platform_audio.HasField("error"):
            raise PlatformAudioError(
                f"Failed to initialize PlatformAudio: {resp.new_platform_audio.error}"
            )

        self._info = resp.new_platform_audio.platform_audio.info
        self._ffi_handle = FfiHandle(resp.new_platform_audio.platform_audio.handle.id)

    def recording_devices(self) -> List[AudioDeviceInfo]:
        """Get available recording devices (microphones).

        Returns:
            List of AudioDeviceInfo for each available microphone.

        Raises:
            PlatformAudioError: If device enumeration fails.
        """
        req = proto_ffi.FfiRequest()
        req.get_audio_devices.platform_audio_handle = self._ffi_handle.handle

        resp = FfiClient.instance.request(req)

        if resp.get_audio_devices.HasField("error") and resp.get_audio_devices.error:
            raise PlatformAudioError(
                f"Failed to enumerate recording devices: {resp.get_audio_devices.error}"
            )

        return [AudioDeviceInfo._from_proto(d) for d in resp.get_audio_devices.recording_devices]

    def playout_devices(self) -> List[AudioDeviceInfo]:
        """Get available playout devices (speakers/headphones).

        Returns:
            List of AudioDeviceInfo for each available speaker.

        Raises:
            PlatformAudioError: If device enumeration fails.
        """
        req = proto_ffi.FfiRequest()
        req.get_audio_devices.platform_audio_handle = self._ffi_handle.handle

        resp = FfiClient.instance.request(req)

        if resp.get_audio_devices.HasField("error") and resp.get_audio_devices.error:
            raise PlatformAudioError(
                f"Failed to enumerate playout devices: {resp.get_audio_devices.error}"
            )

        return [AudioDeviceInfo._from_proto(d) for d in resp.get_audio_devices.playout_devices]

    def set_recording_device(self, device_id: str) -> None:
        """Select the recording device (microphone) to use.

        Call this before creating audio tracks to select which microphone to use.
        If not called, the system default microphone is used.

        Args:
            device_id: The device ID (GUID) from AudioDeviceInfo.id. Use the ID
                rather than index for stable device selection across hot-plug events.

        Raises:
            PlatformAudioError: If device selection fails.
        """
        req = proto_ffi.FfiRequest()
        req.set_recording_device.platform_audio_handle = self._ffi_handle.handle
        req.set_recording_device.device_id = device_id

        resp = FfiClient.instance.request(req)

        if resp.set_recording_device.HasField("error") and resp.set_recording_device.error:
            raise PlatformAudioError(
                f"Failed to set recording device: {resp.set_recording_device.error}"
            )

    def set_playout_device(self, device_id: str) -> None:
        """Select the playout device (speaker) to use.

        Call this before connecting to a room to select which speaker to use
        for audio output. If not called, the system default speaker is used.

        Args:
            device_id: The device ID (GUID) from AudioDeviceInfo.id. Use the ID
                rather than index for stable device selection across hot-plug events.

        Raises:
            PlatformAudioError: If device selection fails.
        """
        req = proto_ffi.FfiRequest()
        req.set_playout_device.platform_audio_handle = self._ffi_handle.handle
        req.set_playout_device.device_id = device_id

        resp = FfiClient.instance.request(req)

        if resp.set_playout_device.HasField("error") and resp.set_playout_device.error:
            raise PlatformAudioError(
                f"Failed to set playout device: {resp.set_playout_device.error}"
            )

    def create_audio_source(
        self, options: Optional[PlatformAudioOptions] = None
    ) -> PlatformAudioSource:
        """Create an audio source for publishing microphone audio.

        The returned source captures audio from the selected microphone (or system
        default) and can be used with LocalAudioTrack.create_audio_track() to
        publish audio.

        Args:
            options: Audio processing options (AEC, NS, AGC, prefer_hardware).
                If None, defaults are used (all processing enabled).

        Returns:
            PlatformAudioSource that can be passed to LocalAudioTrack.create_audio_track().

        Raises:
            PlatformAudioError: If source creation fails.

        Example:
            ```python
            source = platform_audio.create_audio_source(
                PlatformAudioOptions(
                    echo_cancellation=True,
                    noise_suppression=True,
                    auto_gain_control=True,
                )
            )
            track = rtc.LocalAudioTrack.create_audio_track("microphone", source)
            ```
        """
        if options is None:
            options = PlatformAudioOptions()

        req = proto_ffi.FfiRequest()
        req.new_audio_source.type = proto_audio_frame.AudioSourceType.AUDIO_SOURCE_PLATFORM
        req.new_audio_source.platform_audio_handle = self._ffi_handle.handle
        req.new_audio_source.options.CopyFrom(options._to_proto())
        # For platform audio, the ADM determines the actual sample rate and channels.
        # These fields are ignored but required by older proto versions (will be optional
        # in livekit-ffi >= 0.12.58). Use standard WebRTC defaults.
        req.new_audio_source.sample_rate = 48000
        req.new_audio_source.num_channels = 1

        resp = FfiClient.instance.request(req)
        source_info = resp.new_audio_source.source

        return PlatformAudioSource(
            FfiHandle(source_info.handle.id),
            source_info,
        )

    def close(self) -> None:
        """Release the native Audio Device Module resources.

        Call this method when you are done using PlatformAudio to immediately
        release the underlying ADM handle and associated native resources.

        Why call close() explicitly?
            Python's garbage collection is non-deterministic. If you rely on GC
            to clean up PlatformAudio, the ADM may remain active longer than
            expected. This can cause problems on some platforms (especially
            Windows) where:

            - Audio device handles are held longer than necessary, preventing
              other applications or audio subsystems from accessing the devices
            - Subsequent audio operations (including synthetic AudioSource) may
              fail or behave unexpectedly due to ADM still being active
            - Tests running in sequence may interfere with each other if the
              previous test's ADM resources haven't been collected yet

        What happens if close() is not called?
            Resources will eventually be released when the PlatformAudio object
            is garbage collected. This works fine in simple applications where
            the object goes out of scope and is collected promptly. However, in
            these scenarios you should call close() explicitly:

            - Running multiple tests that use audio
            - Switching between PlatformAudio and synthetic AudioSource
            - Long-running applications that create/destroy audio resources
            - Applications where prompt device release is important

        It is safe to call `close()` multiple times; subsequent calls are no-ops.

        Note:
            Always close PlatformAudioSource instances before closing the parent
            PlatformAudio instance.
        """
        self._ffi_handle.dispose()
