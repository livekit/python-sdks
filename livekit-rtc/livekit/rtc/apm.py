from __future__ import annotations

from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._utils import get_address
from .audio_frame import AudioFrame


class AudioProcessingModule:
    """
    Provides WebRTC audio processing capabilities including echo cancellation, noise suppression,
    high-pass filtering, and gain control.
    """

    def __init__(
        self,
        *,
        echo_canceller_enabled: bool = False,
        noise_suppression_enabled: bool = False,
        high_pass_filter_enabled: bool = False,
        gain_controller_enabled: bool = False,
    ) -> None:
        """
        Initialize an AudioProcessingModule instance with the specified audio processing features.

        Args:
            echo_canceller_enabled (bool, optional): Whether to enable echo cancellation.
            noise_suppression_enabled (bool, optional): Whether to enable noise suppression.
            high_pass_filter_enabled (bool, optional): Whether to enable a high-pass filter.
            gain_controller_enabled (bool, optional): Whether to enable a gain controller.
        """
        req = proto_ffi.FfiRequest()
        req.new_apm.echo_canceller_enabled = echo_canceller_enabled
        req.new_apm.noise_suppression_enabled = noise_suppression_enabled
        req.new_apm.high_pass_filter_enabled = high_pass_filter_enabled
        req.new_apm.gain_controller_enabled = gain_controller_enabled

        resp = FfiClient.instance.request(req)
        self._ffi_handle = FfiHandle(resp.new_apm.apm.handle.id)

    def process_stream(self, data: AudioFrame) -> None:
        """
        Process the provided audio frame using the configured audio processing features.

        The input audio frame is modified in-place (if applicable) by the underlying audio
        processing module (e.g., echo cancellation, noise suppression, etc.).

        Important:
            Audio frames must be exactly 10 ms in duration.
        """
        bdata = data.data.cast("b")

        req = proto_ffi.FfiRequest()
        req.apm_process_stream.apm_handle = self._ffi_handle.handle
        req.apm_process_stream.data_ptr = get_address(memoryview(bdata))
        req.apm_process_stream.size = len(bdata)
        req.apm_process_stream.sample_rate = data.sample_rate
        req.apm_process_stream.num_channels = data.num_channels

        resp = FfiClient.instance.request(req)

        if resp.apm_process_stream.error:
            raise RuntimeError(resp.apm_process_stream.error)

    def process_reverse_stream(self, data: AudioFrame) -> None:
        """
        Process the reverse audio frame (typically used for echo cancellation in a full-duplex setup).

        In an echo cancellation scenario, this method is used to process the "far-end" audio
        prior to mixing or feeding it into the echo canceller. Like `process_stream`, the
        input audio frame is modified in-place by the underlying processing module.

        Important:
            Audio frames must be exactly 10 ms in duration.
        """
        bdata = data.data.cast("b")

        req = proto_ffi.FfiRequest()
        req.apm_process_reverse_stream.apm_handle = self._ffi_handle.handle
        req.apm_process_reverse_stream.data_ptr = get_address(memoryview(bdata))
        req.apm_process_reverse_stream.size = len(bdata)
        req.apm_process_reverse_stream.sample_rate = data.sample_rate
        req.apm_process_reverse_stream.num_channels = data.num_channels

        resp = FfiClient.instance.request(req)

        if resp.apm_process_stream.error:
            raise RuntimeError(resp.apm_process_stream.error)
