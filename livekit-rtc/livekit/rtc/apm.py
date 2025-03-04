from __future__ import annotations

from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._utils import get_address
from .audio_frame import AudioFrame


class AudioProcessingModule:
    def __init__(
        self,
        *,
        echo_canceller_enabled: bool = False,
        noise_suppression_enabled: bool = False,
        high_pass_filter_enabled: bool = False,
        gain_controller_enabled: bool = False,
    ) -> None:
        req = proto_ffi.FfiRequest()
        req.new_apm.echo_canceller_enabled = echo_canceller_enabled
        req.new_apm.noise_suppression_enabled = noise_suppression_enabled
        req.new_apm.high_pass_filter_enabled = high_pass_filter_enabled
        req.new_apm.gain_controller_enabled = gain_controller_enabled

        resp = FfiClient.instance.request(req)
        self._ffi_handle = FfiHandle(resp.new_apm.apm.handle.id)

    def process_stream(self, data: AudioFrame) -> None:
        bdata = data.data.cast("b")

        req = proto_ffi.FfiRequest()
        req.apm_process_stream.apm_handle = self._ffi_handle.handle
        req.apm_process_stream.data_ptr = get_address(memoryview(bdata))
        req.apm_process_stream.size = len(bdata)
        req.apm_process_stream.sample_rate = data.sample_rate
        req.apm_process_stream.num_channels = data.num_channels

        resp = FfiClient.instance.request(req)

        if resp.apm_process_stream.error:
            raise Exception(resp.apm_process_stream.error)

    def process_reverse_stream(self, data: AudioFrame) -> None:
        bdata = data.data.cast("b")

        req = proto_ffi.FfiRequest()
        req.apm_process_reverse_stream.apm_handle = self._ffi_handle.handle
        req.apm_process_reverse_stream.data_ptr = get_address(memoryview(bdata))
        req.apm_process_reverse_stream.size = len(bdata)
        req.apm_process_reverse_stream.sample_rate = data.sample_rate
        req.apm_process_reverse_stream.num_channels = data.num_channels

        resp = FfiClient.instance.request(req)

        if resp.apm_process_stream.error:
            raise Exception(resp.apm_process_stream.error)
