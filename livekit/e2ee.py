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

import asyncio
from dataclasses import dataclass
import enum
import logging

from ._ffi_client import FfiHandle, ffi_client
from ._proto import e2ee_pb2
from ._proto import ffi_pb2 as proto_ffi

DEFAULT_RATCHET_SALT = b"LKFrameEncryptionKey"
DEFAULT_MAGIC_BYTES = b"LK-ROCKS"
DEFAULT_RATCHET_WINDOW_SIZE = 16

class EncryptionType(enum.Enum):
    NONE = 0
    GCM = 1
    CUSTOM = 2

class FrameCryptorState(enum.Enum):
    NEW = 0
    OK = 1
    ENCRYPTION_FAILED = 2
    DECRYPTION_FAILED = 3
    MISSING_KEY = 4
    KEY_RATCHETED = 5
    INTERNAL_ERROR = 6

@dataclass
class KeyProviderOptions:
    shared_key: bool = True
    ratchet_salt: bytes = DEFAULT_RATCHET_SALT
    uncrypted_magic_bytes: bytes = DEFAULT_MAGIC_BYTES
    ratchet_window_size: int = DEFAULT_RATCHET_WINDOW_SIZE

@dataclass
class E2EEOptions:
    key_provider_options: KeyProviderOptions = KeyProviderOptions()
    encryption_type: EncryptionType = EncryptionType.GCM

class KeyProvider:
    def __init__(self, ffi_handle: FfiHandle, options: KeyProviderOptions):
        self._options = options
        self._ffi_handle = ffi_handle
    
    @property
    def options(self) -> KeyProviderOptions:
        return self._options
    
    def set_shared_key(self, key: bytes, key_index: int) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.key_provider_set_shared_key.room_handle = self._ffi_handle.handle
        req.e2ee.key_provider_set_shared_key.key_index = key_index
        req.e2ee.key_provider_set_shared_key.shared_key = key

        ffi_client.request(req)

    def export_shared_key(self, key_index: int) -> bytes:
        req = proto_ffi.FfiRequest()
        req.e2ee.key_provider_export_shared_key.room_handle = self._ffi_handle.handle
        req.e2ee.key_provider_export_shared_key.key_index = key_index
        resp = ffi_client.request(req)
        key =  resp.e2ee.key_provider_export_shared_key.key
        return key

    def rachet_shared_key(self, key_index: int) -> bytes:
        req = proto_ffi.FfiRequest()
        req.e2ee.key_provider_rachet_shared_key.room_handle = self._ffi_handle.handle
        req.e2ee.key_provider_rachet_shared_key.key_index = key_index

        resp = ffi_client.request(req)

        new_key = resp.e2ee.key_provider_rachet_shared_key.new_key
        return new_key

    def set_key(self, partcipant_id: str, key: bytes, key_index: int) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.key_provider_set_key.room_handle = self._ffi_handle.handle
        req.e2ee.key_provider_set_key.participant_id = partcipant_id
        req.e2ee.key_provider_set_key.key_index = key_index
        req.e2ee.key_provider_set_key.key = key

        self.key_index = key_index
        ffi_client.request(req)

    def export_key(self, partcipant_id: str, key_index: int) -> bytes:
        req = proto_ffi.FfiRequest()
        req.e2ee.key_provider_export_key.room_handle = self._ffi_handle.handle
        req.e2ee.key_provider_export_key.participant_id = partcipant_id
        req.e2ee.key_provider_export_key.key_index = key_index
        resp = ffi_client.request(req)
        key =  resp.e2ee.key_provider_export_key.key
        return key

    def rachet_key(self, partcipant_id: str, key_index: int) -> bytes:
        req = proto_ffi.FfiRequest()
        req.e2ee.key_provider_rachet_key.room_handle = self._ffi_handle.handle
        req.e2ee.key_provider_rachet_key.participant_id = partcipant_id
        req.e2ee.key_provider_rachet_key.key_index = key_index

        resp = ffi_client.request(req)

        new_key = resp.e2ee.key_provider_rachet_key.new_key
        return new_key


class FrameCryptor:
    def __init__(self, ffi_handle: FfiHandle, partcipant_id: str, key_index: int, enabled: bool):
        self._ffi_handle = ffi_handle
        self.partcipant_id = partcipant_id
        self.key_index = key_index
        self._enabled = enabled

    @property
    def partcipant_id(self) -> str:
        return self.partcipant_id
    
    @property
    def key_index(self) -> int:
        return self.key_index
    
    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.frame_cryptor_set_enabled.room_handle = self._ffi_handle.handle
        req.e2ee.frame_cryptor_set_enabled.participant_id = self.partcipant_id
        req.e2ee.frame_cryptor_set_enabled.enabled = enabled

        ffi_client.request(req)
        self._enabled = enabled

    def set_key_index(self, key_index: int) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.frame_cryptor_set_key_index.room_handle = self._ffi_handle.handle
        req.e2ee.frame_cryptor_set_key_index.participant_id = self.partcipant_id
        req.e2ee.frame_cryptor_set_key_index.key_index = key_index

        ffi_client.request(req)
        self.key_index = key_index

class E2EEManager:
    def __init__(self, ffi_handle: FfiHandle, options: E2EEOptions):
        self.options = options
        self._ffi_handle = ffi_handle
        self._enabled = True
        self._key_provider = KeyProvider(self._ffi_handle, options.key_provider_options)

    @property
    def key_provider(self) -> KeyProvider:
        return self._key_provider

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.e2ee_manager_set_enabled.room_handle = self._ffi_handle.handle
        req.e2ee.e2ee_manager_set_enabled.enabled = enabled

        resp = ffi_client.request(req)

        self._enabled = resp.e2ee_manager_set_enabled.enabled

    def frame_cryptors(self) -> []:
        req = proto_ffi.FfiRequest()
        req.e2ee.e2ee_manager_get_frame_cryptors.room_handle = self._ffi_handle.handle

        resp = ffi_client.request(req)

        frame_cryptors = []
        for frame_cryptor in resp.e2ee.e2ee_manager_get_frame_cryptors.frame_cryptors:
            frame_cryptors.append(FrameCryptor(
                ffi_handle=self._ffi_handle,
                partcipant_id=frame_cryptor.participant_id,
                key_index=frame_cryptor.key_index,
                enabled=frame_cryptor.enabled
            ))
        return frame_cryptors