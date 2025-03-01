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

from dataclasses import dataclass, field
from typing import List, Optional

from ._ffi_client import FfiClient
from ._proto import e2ee_pb2 as proto_e2ee
from ._proto import ffi_pb2 as proto_ffi

DEFAULT_RATCHET_SALT = b"LKFrameEncryptionKey"
DEFAULT_RATCHET_WINDOW_SIZE = 16
DEFAULT_FAILURE_TOLERANCE = -1


@dataclass
class KeyProviderOptions:
    shared_key: Optional[bytes] = None
    ratchet_salt: bytes = DEFAULT_RATCHET_SALT
    ratchet_window_size: int = DEFAULT_RATCHET_WINDOW_SIZE
    failure_tolerance: int = DEFAULT_FAILURE_TOLERANCE


@dataclass
class E2EEOptions:
    key_provider_options: KeyProviderOptions = field(default_factory=KeyProviderOptions)
    encryption_type: proto_e2ee.EncryptionType.ValueType = proto_e2ee.EncryptionType.GCM


class KeyProvider:
    def __init__(self, room_handle: int, options: KeyProviderOptions):
        self._options = options
        self._room_handle = room_handle

    @property
    def options(self) -> KeyProviderOptions:
        return self._options

    def set_shared_key(self, key: bytes, key_index: int) -> None:
        """Sets the shared encryption key.

        Parameters:
            key (bytes): The new shared key.
            key_index (int): The index of the key.

        Example:
            ```python
            key_provider.set_shared_key(b"my_shared_key", key_index=1)
            ```
        """
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.set_shared_key.key_index = key_index
        req.e2ee.set_shared_key.shared_key = key
        FfiClient.instance.request(req)

    def export_shared_key(self, key_index: int) -> bytes:
        """Exports the shared encryption key.

        Parameters:
            key_index (int): The index of the key to export.

        Returns:
            bytes: The exported shared key.

        Example:
            ```python
            key = key_provider.export_shared_key(key_index=1)
            ```
        """
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.get_shared_key.key_index = key_index
        resp = FfiClient.instance.request(req)
        key = resp.e2ee.get_shared_key.key
        return key

    def ratchet_shared_key(self, key_index: int) -> bytes:
        """Ratchets the shared encryption key to a new key.

        Parameters:
            key_index (int): The index of the key to ratchet.

        Returns:
            bytes: The new ratcheted shared key.

        Example:
            ```python
            new_key = key_provider.ratchet_shared_key(key_index=1)
            ```
        """
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.ratchet_shared_key.key_index = key_index

        resp = FfiClient.instance.request(req)

        new_key = resp.e2ee.ratchet_shared_key.new_key
        return new_key

    def set_key(self, participant_identity: str, key: bytes, key_index: int) -> None:
        """Sets the encryption key for a specific participant.

        Parameters:
            participant_identity (str): The identity of the participant.
            key (bytes): The encryption key to set.
            key_index (int): The index of the key.

        Example:
            ```python
            key_provider.set_key("participant123", b"participant_key", key_index=2)
            ```
        """
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.set_key.participant_identity = participant_identity
        req.e2ee.set_key.key_index = key_index
        req.e2ee.set_key.key = key

        self.key_index = key_index
        FfiClient.instance.request(req)

    def export_key(self, participant_identity: str, key_index: int) -> bytes:
        """Exports the encryption key for a specific participant.

        Parameters:
            participant_identity (str): The identity of the participant.
            key_index (int): The index of the key to export.

        Returns:
            bytes: The exported key.

        Example:
            ```python
            key = key_provider.export_key("participant123", key_index=2)
            ```
        """
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.get_key.participant_identity = participant_identity
        req.e2ee.get_key.key_index = key_index
        resp = FfiClient.instance.request(req)
        key = resp.e2ee.get_key.key
        return key

    def ratchet_key(self, participant_identity: str, key_index: int) -> bytes:
        """Ratchets the encryption key for a specific participant to a new key.

        Parameters:
            participant_identity (str): The identity of the participant.
            key_index (int): The index of the key to ratchet.

        Returns:
            bytes: The new ratcheted key.

        Example:
            ```python
            new_key = key_provider.ratchet_key("participant123", key_index=2)
            ```
        """
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.ratchet_key.participant_identity = participant_identity
        req.e2ee.ratchet_key.key_index = key_index

        resp = FfiClient.instance.request(req)
        new_key = resp.e2ee.ratchet_key.new_key
        return new_key


class FrameCryptor:
    def __init__(self, room_handle: int, participant_identity: str, key_index: int, enabled: bool):
        self._room_handle = room_handle
        self._enabled = enabled
        self._participant_identity = participant_identity
        self._key_index = key_index

    @property
    def participant_identity(self) -> str:
        return self._participant_identity

    @property
    def key_index(self) -> int:
        return self._key_index

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enables or disables frame encryption.

        Parameters:
            enabled (bool): True to enable, False to disable.

        Example:
            ```python
            frame_cryptor.set_enabled(True)
            ```
        """
        self._enabled = enabled
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.cryptor_set_enabled.participant_identity = self._participant_identity
        req.e2ee.cryptor_set_enabled.enabled = enabled
        FfiClient.instance.request(req)

    def set_key_index(self, key_index: int) -> None:
        """Sets the key index for encryption/decryption.

        Parameters:
            key_index (int): The new key index.

        Example:
            ```python
            frame_cryptor.set_key_index(3)
            ```
        """
        self._key_index = key_index
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.cryptor_set_key_index.participant_identity = self._participant_identity
        req.e2ee.cryptor_set_key_index.key_index = key_index
        FfiClient.instance.request(req)


class E2EEManager:
    def __init__(self, room_handle: int, options: Optional[E2EEOptions]):
        self.options = options
        self._room_handle = room_handle
        self._enabled = options is not None

        if options is not None:
            self._key_provider = KeyProvider(self._room_handle, options.key_provider_options)

    @property
    def key_provider(self) -> Optional[KeyProvider]:
        return self._key_provider

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enables or disables end-to-end encryption.

        Parameters:
            enabled (bool): True to enable, False to disable.

        Example:
            ```python
            e2ee_manager.set_enabled(True)
            ```
        """
        self._enabled = enabled
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle
        req.e2ee.manager_set_enabled.enabled = enabled
        FfiClient.instance.request(req)

    def frame_cryptors(self) -> List[FrameCryptor]:
        """Retrieves the list of frame cryptors for participants.

        Returns:
            List[FrameCryptor]: A list of FrameCryptor instances.

        Example:
            ```python
            cryptors = e2ee_manager.frame_cryptors()
            for cryptor in cryptors:
                print(cryptor.participant_identity)
            ```
        """
        req = proto_ffi.FfiRequest()
        req.e2ee.room_handle = self._room_handle

        resp = FfiClient.instance.request(req)
        frame_cryptors = []
        for frame_cryptor in resp.e2ee.manager_get_frame_cryptors.frame_cryptors:
            frame_cryptors.append(
                FrameCryptor(
                    self._room_handle,
                    frame_cryptor.participant_identity,
                    frame_cryptor.key_index,
                    frame_cryptor.enabled,
                )
            )
        return frame_cryptors
