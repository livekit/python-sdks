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

"""Unit tests for E2EE functionality."""

import pytest


class TestKeyProviderOptions:
    """Tests for KeyProviderOptions dataclass."""

    def test_default_values(self):
        """Test that KeyProviderOptions has correct default values."""
        from livekit.rtc.e2ee import (
            KeyProviderOptions,
            DEFAULT_RATCHET_SALT,
            DEFAULT_RATCHET_WINDOW_SIZE,
            DEFAULT_FAILURE_TOLERANCE,
            DEFAULT_KEY_RING_SIZE,
        )
        from livekit.rtc._proto import e2ee_pb2 as proto_e2ee

        options = KeyProviderOptions()

        assert options.shared_key is None
        assert options.ratchet_salt == DEFAULT_RATCHET_SALT
        assert options.ratchet_window_size == DEFAULT_RATCHET_WINDOW_SIZE
        assert options.failure_tolerance == DEFAULT_FAILURE_TOLERANCE
        assert options.key_ring_size == DEFAULT_KEY_RING_SIZE
        assert options.key_derivation_function == proto_e2ee.KeyDerivationFunction.PBKDF2

    def test_custom_values(self):
        """Test KeyProviderOptions with custom values."""
        from livekit.rtc.e2ee import KeyProviderOptions
        from livekit.rtc._proto import e2ee_pb2 as proto_e2ee

        options = KeyProviderOptions(
            shared_key=b"my-secret-key",
            ratchet_salt=b"custom-salt",
            ratchet_window_size=32,
            failure_tolerance=5,
            key_ring_size=8,
            key_derivation_function=proto_e2ee.KeyDerivationFunction.HKDF,
        )

        assert options.shared_key == b"my-secret-key"
        assert options.ratchet_salt == b"custom-salt"
        assert options.ratchet_window_size == 32
        assert options.failure_tolerance == 5
        assert options.key_ring_size == 8
        assert options.key_derivation_function == proto_e2ee.KeyDerivationFunction.HKDF

    def test_various_key_lengths(self):
        """Test that shared_key accepts various lengths."""
        from livekit.rtc.e2ee import KeyProviderOptions

        # Short key
        options_short = KeyProviderOptions(shared_key=b"short")
        assert options_short.shared_key == b"short"

        # Medium key
        options_medium = KeyProviderOptions(shared_key=b"medium-length-key-here")
        assert options_medium.shared_key == b"medium-length-key-here"

        # Long key
        long_key = b"a" * 256
        options_long = KeyProviderOptions(shared_key=long_key)
        assert options_long.shared_key == long_key

        # Binary key
        binary_key = bytes(range(256))
        options_binary = KeyProviderOptions(shared_key=binary_key)
        assert options_binary.shared_key == binary_key


class TestE2EEOptions:
    """Tests for E2EEOptions dataclass."""

    def test_default_values(self):
        """Test E2EEOptions default values."""
        from livekit.rtc.e2ee import E2EEOptions, KeyProviderOptions
        from livekit.rtc._proto import e2ee_pb2 as proto_e2ee

        options = E2EEOptions()

        assert isinstance(options.key_provider_options, KeyProviderOptions)
        assert options.encryption_type == proto_e2ee.EncryptionType.GCM

    def test_with_shared_key(self):
        """Test E2EEOptions with a shared key."""
        from livekit.rtc.e2ee import E2EEOptions, KeyProviderOptions

        key_options = KeyProviderOptions(shared_key=b"test-key")
        options = E2EEOptions(key_provider_options=key_options)

        assert options.key_provider_options.shared_key == b"test-key"


class TestProtoMessageBuilding:
    """Tests for proto message building with E2EE options."""

    def test_proto_key_provider_options_fields(self):
        """Test that proto KeyProviderOptions has all required fields."""
        from livekit.rtc._proto import e2ee_pb2 as proto_e2ee

        proto_options = proto_e2ee.KeyProviderOptions()

        # Set all fields that should be present
        proto_options.shared_key = b"test-key"
        proto_options.ratchet_window_size = 16
        proto_options.ratchet_salt = b"LKFrameEncryptionKey"
        proto_options.failure_tolerance = -1
        proto_options.key_ring_size = 16
        proto_options.key_derivation_function = proto_e2ee.KeyDerivationFunction.PBKDF2

        # Verify fields are set correctly
        assert proto_options.shared_key == b"test-key"
        assert proto_options.ratchet_window_size == 16
        assert proto_options.ratchet_salt == b"LKFrameEncryptionKey"
        assert proto_options.failure_tolerance == -1
        assert proto_options.key_ring_size == 16
        assert proto_options.key_derivation_function == proto_e2ee.KeyDerivationFunction.PBKDF2

    def test_proto_serialization(self):
        """Test that proto message can be serialized without errors."""
        from livekit.rtc._proto import e2ee_pb2 as proto_e2ee

        proto_options = proto_e2ee.KeyProviderOptions()
        proto_options.ratchet_window_size = 16
        proto_options.ratchet_salt = b"LKFrameEncryptionKey"
        proto_options.failure_tolerance = -1
        proto_options.key_ring_size = 16
        proto_options.key_derivation_function = proto_e2ee.KeyDerivationFunction.PBKDF2

        # This should not raise an EncodeError
        serialized = proto_options.SerializeToString()
        assert len(serialized) > 0

        # Verify we can deserialize it back
        parsed = proto_e2ee.KeyProviderOptions()
        parsed.ParseFromString(serialized)
        assert parsed.key_ring_size == 16
        assert parsed.key_derivation_function == proto_e2ee.KeyDerivationFunction.PBKDF2

    def test_e2ee_options_proto_serialization(self):
        """Test full E2eeOptions proto serialization."""
        from livekit.rtc._proto import e2ee_pb2 as proto_e2ee

        e2ee_opts = proto_e2ee.E2eeOptions()
        e2ee_opts.encryption_type = proto_e2ee.EncryptionType.GCM
        e2ee_opts.key_provider_options.shared_key = b"my-shared-key"
        e2ee_opts.key_provider_options.ratchet_window_size = 16
        e2ee_opts.key_provider_options.ratchet_salt = b"LKFrameEncryptionKey"
        e2ee_opts.key_provider_options.failure_tolerance = -1
        e2ee_opts.key_provider_options.key_ring_size = 16
        e2ee_opts.key_provider_options.key_derivation_function = (
            proto_e2ee.KeyDerivationFunction.PBKDF2
        )

        # This should not raise an EncodeError
        serialized = e2ee_opts.SerializeToString()
        assert len(serialized) > 0


class TestPublicExports:
    """Tests for public API exports."""

    def test_key_derivation_function_exported(self):
        """Test that KeyDerivationFunction is exported from the package."""
        from livekit.rtc import KeyDerivationFunction

        # Verify enum values are accessible
        assert KeyDerivationFunction.PBKDF2 == 0
        assert KeyDerivationFunction.HKDF == 1

    def test_encryption_type_exported(self):
        """Test that EncryptionType is exported from the package."""
        from livekit.rtc import EncryptionType

        assert EncryptionType.NONE == 0
        assert EncryptionType.GCM == 1
        assert EncryptionType.CUSTOM == 2

    def test_e2ee_classes_exported(self):
        """Test that E2EE classes are exported from the package."""
        from livekit.rtc import E2EEOptions, KeyProviderOptions

        # Should be able to instantiate without errors
        key_opts = KeyProviderOptions()
        e2ee_opts = E2EEOptions()

        assert key_opts is not None
        assert e2ee_opts is not None
