from typing import Optional, List

from ._ffi_client import FfiClient
from ._proto import ffi_pb2 as proto_ffi


class AudioFilter:
    def __init__(self, module_id: str, path: str, dependencies: Optional[List[str]] = None) -> None:
        self._path = path

        req = proto_ffi.FfiRequest()
        req.load_audio_filter_plugin.module_id = module_id
        req.load_audio_filter_plugin.plugin_path = path
        req.load_audio_filter_plugin.dependencies[:] = (
            dependencies if dependencies is not None else []
        )

        resp = FfiClient.instance.request(req)

        if resp.load_audio_filter_plugin.error:
            raise Exception(
                f"failed to initialize audio filter #{resp.load_audio_filter_plugin.error}"
            )
