from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi

class AudioFilter:
    def __init__(
        self,
        path: str,
    ) -> None:
        self._path = path

        req = proto_ffi.FfiRequest()
        req.load_audio_filter_plugin.plugin_path = path

        resp = FfiClient.instance.request(req)

        self._ffi_handle_id = resp.load_audio_filter_plugin.handle.id
        self._ffi_handle = FfiHandle(resp.load_audio_filter_plugin.handle.id)

    def handle(self) -> int:
        return self._ffi_handle_id
