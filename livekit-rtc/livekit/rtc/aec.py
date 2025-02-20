from __future__ import annotations

from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._utils import get_address
from .audio_frame import AudioFrame


class Aec:
    """
    Acoustic Echo Cancellation (AEC) module for removing echo from audio data.
    (It uses the AEC3 implementation from libwebrtc).
    """

    def __init__(
        self,
        sample_rate: int,
        num_channels: int,
    ) -> None:
        self._sample_rate = sample_rate
        self._mum_channels = num_channels

        req = proto_ffi.FfiRequest()
        req.new_aec.sample_rate = sample_rate
        req.new_aec.num_channels = num_channels

        resp = FfiClient.instance.request(req)
        self._ffi_handle = FfiHandle(resp.new_aec.aec.handle.id)

    def cancel_echo(self, capture_data: bytearray | AudioFrame, render_data: bytearray | AudioFrame) -> None:
        cap_data = capture_data if isinstance(capture_data, bytearray) else capture_data.data.cast("b")
        rend_data = render_data if isinstance(render_data, bytearray) else render_data.data.cast("b")

        req = proto_ffi.FfiRequest()
        req.cancel_echo.aec_handle = self._ffi_handle.handle
        req.cancel_echo.cap_ptr = get_address(memoryview(cap_data))
        req.cancel_echo.cap_size = len(cap_data)
        req.cancel_echo.rend_ptr = get_address(memoryview(rend_data))
        req.cancel_echo.rend_size = len(rend_data)

        resp = FfiClient.instance.request(req)

        if resp.cancel_echo.error:
            raise Exception(resp.cancel_echo.error)
