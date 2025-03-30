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
        echo_cancellation: bool = False,
        noise_suppression: bool = False,
        high_pass_filter: bool = False,
        auto_gain_control: bool = False,
    ) -> None:
        """
        Initialize an AudioProcessingModule instance with the specified audio processing features.

        Args:
            echo_cancellation (bool, optional): Whether to enable echo cancellation.
            noise_suppression (bool, optional): Whether to enable noise suppression.
            high_pass_filter (bool, optional): Whether to enable a high-pass filter.
            auto_gain_control (bool, optional): Whether to enable auto gain control.
        """
        req = proto_ffi.FfiRequest()
        req.new_apm.echo_canceller_enabled = echo_cancellation
        req.new_apm.noise_suppression_enabled = noise_suppression
        req.new_apm.high_pass_filter_enabled = high_pass_filter
        req.new_apm.gain_controller_enabled = auto_gain_control

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

    def set_stream_delay_ms(self, delay_ms: int) -> None:
        """
        This must be called if and only if echo processing is enabled.

        Sets the `delay` in ms between `process_reverse_stream()` receiving a far-end
        frame and `process_stream()` receiving a near-end frame containing the
        corresponding echo. On the client-side this can be expressed as
            delay = (t_render - t_analyze) + (t_process - t_capture)
        where,
            - t_analyze is the time a frame is passed to `process_reverse_stream()` and
            t_render is the time the first sample of the same frame is rendered by
            the audio hardware.
            - t_capture is the time the first sample of a frame is captured by the
            audio hardware and t_process is the time the same frame is passed to
            `process_stream()`.
        """
        req = proto_ffi.FfiRequest()
        req.apm_set_stream_delay.apm_handle = self._ffi_handle.handle
        req.apm_set_stream_delay.delay_ms = delay_ms

        resp = FfiClient.instance.request(req)

        if resp.apm_set_stream_delay.error:
            raise RuntimeError(resp.apm_set_stream_delay.error)
