from livekit import AudioFrame

from ._ffi_client import FfiClient, FfiHandle
from ._proto import audio_frame_pb2 as proto_audio_frame
from ._proto import ffi_pb2 as proto_ffi


class AudioSource:
    def __init__(self) -> None:
        req = proto_ffi.FfiRequest()
        req.new_audio_source.type = proto_audio_frame.AudioSourceType.AUDIO_SOURCE_NATIVE

        ffi_client = FfiClient()
        resp = ffi_client.request(req)
        self._info = resp.new_audio_source.source
        self._ffi_handle = FfiHandle(self._info.handle.id)

    def capture_frame(self, frame: AudioFrame) -> None:
        req = proto_ffi.FfiRequest()

        req.capture_audio_frame.source_handle.id = self._ffi_handle.handle
        req.capture_audio_frame.buffer_handle.id = frame._ffi_handle.handle

        ffi_client = FfiClient()
        ffi_client.request(req)
