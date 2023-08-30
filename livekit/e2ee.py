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

class KeyProviderOptions:
    salt: bytes = DEFAULT_RATCHET_SALT
    magic_bytes: bytes = DEFAULT_MAGIC_BYTES
    ratchet_window_size: int = DEFAULT_RATCHET_WINDOW_SIZE

class E2EEOptions:
    is_shared_key: bool = True
    shared_key: str = True
    key_provider_options: KeyProviderOptions = KeyProviderOptions()

class FrameCryptor:
    partcipant_id: str
    key_index: int
    enabled: bool
    encryption_type: EncryptionType
    def __init__(self, ffi_handle: FfiHandle, partcipant_id: str, key_index: int, enabled: bool, encryption_type: EncryptionType):
        self.ffi_handle = ffi_handle
        self.partcipant_id = partcipant_id
        self.key_index = key_index
        self.enabled = enabled
        self.encryption_type = encryption_type

    async def set_enabled(self, enabled: bool) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.frame_cryptor_enable.room_handle = self.ffi_handle()
        req.e2ee.frame_cryptor_enable.participant_id = self.partcipant_id
        req.e2ee.frame_cryptor_enable.key_index = self.key_index
        req.e2ee.frame_cryptor_enable.enabled = enabled

        resp = ffi_client.request(req)
        future: asyncio.Future[e2ee_pb2.E2EEResponse] = asyncio.Future()

        @ffi_client.on('e2ee')
        def on_frame_cryptor_enabled_callback(cb: e2ee_pb2.E2EEResponse):
            if cb.async_id == resp.e2ee.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'e2ee', on_frame_cryptor_enabled_callback)

        await future
    
    async def set_key(self, key: bytes, key_index: int) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.frame_cryptor_set_key.room_handle = self.ffi_handle()
        req.e2ee.frame_cryptor_set_key.participant_id = self.partcipant_id
        req.e2ee.frame_cryptor_set_key.key_index = key_index
        req.e2ee.frame_cryptor_set_key.key = key

        self.key_index = key_index

        resp = ffi_client.request(req)
        future: asyncio.Future[e2ee_pb2.E2EEResponse] = asyncio.Future()

        @ffi_client.on('e2ee')
        def on_frame_cryptor_set_key_callback(cb: e2ee_pb2.E2EEResponse):
            if cb.async_id == resp.e2ee.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'e2ee', on_frame_cryptor_set_key_callback)

        await future

    async def export_key(self) -> bytes:
        req = proto_ffi.FfiRequest()
        req.e2ee.frame_cryptor_export_key.room_handle = self.ffi_handle()
        req.e2ee.frame_cryptor_export_key.participant_id = self.partcipant_id
        req.e2ee.frame_cryptor_export_key.key_index = self.key_index

        resp = ffi_client.request(req)
        future: asyncio.Future[e2ee_pb2.E2EEResponse] = asyncio.Future()

        @ffi_client.on('e2ee')
        def on_frame_cryptor_export_key_callback(cb: e2ee_pb2.E2EEResponse):
            if cb.async_id == resp.e2ee.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'e2ee', on_frame_cryptor_export_key_callback)

        await future
        return future.result().e2ee.frame_cryptor_export_key.key
    
    async def rachet_key(self) -> bytes:
        req = proto_ffi.FfiRequest()
        req.e2ee.frame_cryptor_rachet_key.room_handle = self.ffi_handle()
        req.e2ee.frame_cryptor_rachet_key.participant_id = self.partcipant_id
        req.e2ee.frame_cryptor_rachet_key.key_index = self.key_index

        resp = ffi_client.request(req)
        future: asyncio.Future[e2ee_pb2.E2EEResponse] = asyncio.Future()

        @ffi_client.on('e2ee')
        def on_frame_cryptor_rachet_key_callback(cb: e2ee_pb2.E2EEResponse):
            if cb.async_id == resp.e2ee.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'e2ee', on_frame_cryptor_rachet_key_callback)

        await future
        return future.result().e2ee.frame_cryptor_rachet_key.new_key

class E2EEManager:
    def __init__(self, ffi_handle: FfiHandle, options: E2EEOptions):
        self.options = options
        self.ffi_handle = ffi_handle
    
    async def set_enabled(self, enabled: bool) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.e2ee_manager_enable.room_handle = self.ffi_handle()
        req.e2ee.e2ee_manager_enable.enabled = enabled

        resp = ffi_client.request(req)
        future: asyncio.Future[e2ee_pb2.E2EEResponse] = asyncio.Future()

        @ffi_client.on('e2ee')
        def on_e2ee_manager_enabled_callback(cb: e2ee_pb2.E2EEResponse):
            if cb.async_id == resp.e2ee.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'e2ee', on_e2ee_manager_enabled_callback)

        await future
    
    async def set_shared_key(self, enabled_shared_key: bool, shared_key: str) -> None:
        req = proto_ffi.FfiRequest()
        req.e2ee.e2ee_manager_set_shared_key.room_handle = self.ffi_handle()
        req.e2ee.e2ee_manager_set_shared_key.shared_key = shared_key
        req.e2ee.e2ee_manager_set_shared_key.enabled_shared_key = enabled_shared_key

        resp = ffi_client.request(req)
        future: asyncio.Future[e2ee_pb2.E2EEResponse] = asyncio.Future()

        @ffi_client.on('e2ee')
        def on_e2ee_manager_set_shared_key_callback(cb: e2ee_pb2.E2EEResponse):
            if cb.async_id == resp.e2ee.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'e2ee', on_e2ee_manager_set_shared_key_callback)

        await future

    async def frame_cryptors(self) -> []:
        req = proto_ffi.FfiRequest()
        req.e2ee.e2ee_manager_get_frame_cryptors.room_handle = self.ffi_handle()

        resp = ffi_client.request(req)
        future: asyncio.Future[e2ee_pb2.E2EEResponse] = asyncio.Future()

        @ffi_client.on('e2ee')
        def on_e2ee_manager_get_frame_cryptors(cb: e2ee_pb2.E2EEResponse):
            if cb.async_id == resp.e2ee.async_id:
                future.set_result(cb)
                ffi_client.remove_listener(
                    'e2ee', on_e2ee_manager_get_frame_cryptors)

        await future
        res = future.result()
        frame_cryptors = []
        for frame_cryptor in res.e2ee.e2ee_manager_get_frame_cryptors.frame_cryptors:
            frame_cryptors.append(FrameCryptor(
                ffi_handle=self.ffi_handle,
                partcipant_id=frame_cryptor.participant_id,
                key_index=frame_cryptor.key_index,
                enabled=frame_cryptor.enabled,
                encryption_type=EncryptionType(frame_cryptor.encryption_type)
            ))
        return frame_cryptors