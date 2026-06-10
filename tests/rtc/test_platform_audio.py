"""
Tests for PlatformAudio functionality.

These tests require audio hardware to be available. On CI environments without
audio devices, tests will be skipped automatically.
"""

import pytest
from typing import Optional

from livekit import rtc


# Global to cache PlatformAudio availability check
_platform_audio_available: Optional[bool] = None
_platform_audio_error: Optional[str] = None


def _check_platform_audio_available() -> tuple[bool, Optional[str]]:
    """Check if PlatformAudio can be initialized on this system."""
    global _platform_audio_available, _platform_audio_error

    if _platform_audio_available is not None:
        return _platform_audio_available, _platform_audio_error

    try:
        pa = rtc.PlatformAudio()
        _platform_audio_available = True
        _platform_audio_error = None
        # Keep reference to avoid cleanup issues
        del pa
    except rtc.PlatformAudioError as e:
        _platform_audio_available = False
        _platform_audio_error = str(e)

    return _platform_audio_available, _platform_audio_error


def requires_platform_audio(func):
    """Decorator to skip tests if PlatformAudio is not available."""

    @pytest.mark.skipif(
        not _check_platform_audio_available()[0],
        reason=f"PlatformAudio not available: {_check_platform_audio_available()[1]}",
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# Use a module-scoped fixture to avoid creating multiple PlatformAudio instances
@pytest.fixture(scope="module")
def platform_audio():
    """Create a PlatformAudio instance for testing."""
    available, error = _check_platform_audio_available()
    if not available:
        pytest.skip(f"PlatformAudio not available: {error}")

    pa = rtc.PlatformAudio()
    yield pa
    # Cleanup handled by garbage collection


class TestPlatformAudioCreation:
    """Tests for PlatformAudio initialization."""

    def test_platform_audio_creation(self, platform_audio):
        """Test that PlatformAudio can be created successfully."""
        assert platform_audio is not None

    def test_platform_audio_multiple_instances(self, platform_audio):
        """Test that multiple PlatformAudio instances can coexist."""
        # Creating another instance should reuse the same underlying ADM
        available, error = _check_platform_audio_available()
        if not available:
            pytest.skip(f"PlatformAudio not available: {error}")

        pa2 = rtc.PlatformAudio()
        assert pa2 is not None
        # Both should work
        assert platform_audio is not None


class TestDeviceEnumeration:
    """Tests for audio device enumeration."""

    def test_recording_devices_returns_list(self, platform_audio):
        """Test that recording_devices() returns a list."""
        devices = platform_audio.recording_devices()
        assert isinstance(devices, list)

    def test_playout_devices_returns_list(self, platform_audio):
        """Test that playout_devices() returns a list."""
        devices = platform_audio.playout_devices()
        assert isinstance(devices, list)

    def test_recording_device_info_structure(self, platform_audio):
        """Test that recording devices have correct structure."""
        devices = platform_audio.recording_devices()
        if not devices:
            pytest.skip("No recording devices available")

        device = devices[0]
        assert isinstance(device, rtc.AudioDeviceInfo)
        assert isinstance(device.index, int)
        assert isinstance(device.name, str)
        assert isinstance(device.id, str)
        assert device.index >= 0
        assert len(device.name) > 0

    def test_playout_device_info_structure(self, platform_audio):
        """Test that playout devices have correct structure."""
        devices = platform_audio.playout_devices()
        if not devices:
            pytest.skip("No playout devices available")

        device = devices[0]
        assert isinstance(device, rtc.AudioDeviceInfo)
        assert isinstance(device.index, int)
        assert isinstance(device.name, str)
        assert isinstance(device.id, str)
        assert device.index >= 0
        assert len(device.name) > 0

    def test_device_indices_are_sequential(self, platform_audio):
        """Test that device indices start at 0 and are sequential."""
        recording = platform_audio.recording_devices()
        playout = platform_audio.playout_devices()

        for i, device in enumerate(recording):
            assert device.index == i, f"Recording device index mismatch: {device.index} != {i}"

        for i, device in enumerate(playout):
            assert device.index == i, f"Playout device index mismatch: {device.index} != {i}"


class TestDeviceSelection:
    """Tests for audio device selection."""

    def test_set_recording_device_valid(self, platform_audio):
        """Test setting a valid recording device."""
        devices = platform_audio.recording_devices()
        if not devices:
            pytest.skip("No recording devices available")

        # Should not raise
        platform_audio.set_recording_device(devices[0].id)

    def test_set_playout_device_valid(self, platform_audio):
        """Test setting a valid playout device."""
        devices = platform_audio.playout_devices()
        if not devices:
            pytest.skip("No playout devices available")

        # Should not raise
        platform_audio.set_playout_device(devices[0].id)

    def test_set_recording_device_invalid_falls_back_to_default(self, platform_audio):
        """Test that setting an invalid recording device falls back to default (no error).

        When a device GUID is invalid (e.g., device was unplugged), the system
        gracefully falls back to the default device instead of raising an error.
        This is intentional behavior for better UX - a saved device preference
        shouldn't crash the app if the device is removed.
        """
        # Should not raise - falls back to default device
        platform_audio.set_recording_device("invalid-device-id-that-does-not-exist")

    def test_set_playout_device_invalid_falls_back_to_default(self, platform_audio):
        """Test that setting an invalid playout device falls back to default (no error).

        When a device GUID is invalid (e.g., device was unplugged), the system
        gracefully falls back to the default device instead of raising an error.
        This is intentional behavior for better UX - a saved device preference
        shouldn't crash the app if the device is removed.
        """
        # Should not raise - falls back to default device
        platform_audio.set_playout_device("invalid-device-id-that-does-not-exist")


class TestAudioSourceCreation:
    """Tests for PlatformAudioSource creation."""

    def test_create_audio_source_default_options(self, platform_audio):
        """Test creating an audio source with default options."""
        source = platform_audio.create_audio_source()
        assert source is not None
        assert isinstance(source, rtc.PlatformAudioSource)

    def test_create_audio_source_custom_options(self, platform_audio):
        """Test creating an audio source with custom options."""
        options = rtc.PlatformAudioOptions(
            echo_cancellation=True,
            noise_suppression=True,
            auto_gain_control=True,
            prefer_hardware=False,
        )
        source = platform_audio.create_audio_source(options)
        assert source is not None
        assert isinstance(source, rtc.PlatformAudioSource)

    def test_create_audio_source_all_processing_disabled(self, platform_audio):
        """Test creating an audio source with all processing disabled."""
        options = rtc.PlatformAudioOptions(
            echo_cancellation=False,
            noise_suppression=False,
            auto_gain_control=False,
        )
        source = platform_audio.create_audio_source(options)
        assert source is not None

    def test_audio_source_has_handle(self, platform_audio):
        """Test that created audio source has a valid internal handle."""
        source = platform_audio.create_audio_source()
        # The _handle property is used internally for track creation
        assert hasattr(source, "_handle")
        assert source._handle > 0

    def test_create_multiple_audio_sources(self, platform_audio):
        """Test creating multiple audio sources from the same PlatformAudio."""
        source1 = platform_audio.create_audio_source()
        source2 = platform_audio.create_audio_source()

        assert source1 is not None
        assert source2 is not None
        # Each source should have a unique handle
        assert source1._handle != source2._handle


class TestPlatformAudioOptions:
    """Tests for PlatformAudioOptions dataclass."""

    def test_default_options(self):
        """Test default PlatformAudioOptions values."""
        options = rtc.PlatformAudioOptions()
        assert options.echo_cancellation is True
        assert options.noise_suppression is True
        assert options.auto_gain_control is True
        assert options.prefer_hardware is False

    def test_custom_options(self):
        """Test custom PlatformAudioOptions values."""
        options = rtc.PlatformAudioOptions(
            echo_cancellation=False,
            noise_suppression=False,
            auto_gain_control=False,
            prefer_hardware=True,
        )
        assert options.echo_cancellation is False
        assert options.noise_suppression is False
        assert options.auto_gain_control is False
        assert options.prefer_hardware is True


class TestAudioDeviceInfo:
    """Tests for AudioDeviceInfo dataclass."""

    def test_audio_device_info_creation(self):
        """Test creating AudioDeviceInfo manually."""
        info = rtc.AudioDeviceInfo(index=0, name="Test Mic", id="test-guid-123")
        assert info.index == 0
        assert info.name == "Test Mic"
        assert info.id == "test-guid-123"

    def test_audio_device_info_equality(self):
        """Test AudioDeviceInfo equality comparison."""
        info1 = rtc.AudioDeviceInfo(index=0, name="Test Mic", id="guid-1")
        info2 = rtc.AudioDeviceInfo(index=0, name="Test Mic", id="guid-1")
        info3 = rtc.AudioDeviceInfo(index=1, name="Other Mic", id="guid-2")

        assert info1 == info2
        assert info1 != info3


class TestIntegrationWithTrack:
    """Integration tests with LocalAudioTrack."""

    def test_create_track_from_platform_audio_source(self, platform_audio):
        """Test creating a LocalAudioTrack from PlatformAudioSource."""
        source = platform_audio.create_audio_source()
        track = rtc.LocalAudioTrack.create_audio_track("test-mic", source)

        assert track is not None
        assert track.name == "test-mic"
        assert track.kind == rtc.TrackKind.KIND_AUDIO
