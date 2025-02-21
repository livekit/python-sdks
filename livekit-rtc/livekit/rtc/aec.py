from __future__ import annotations

from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._utils import get_address
from .audio_frame import AudioFrame


class Aec:
    """
    Acoustic Echo Cancellation (AEC) module for removing echo from audio data using
    the AEC3 implementation from libwebrtc.

    Note: Frames must be processed in chunks of exactly 10 ms. 
    The length of the provided buffers must correspond to 10 ms of audio at the 
    given sample rate and number of channels.
    Only the capture data buffer is modified (in-place). The render data
    buffer is used as a reference and is not changed by this process.
    """

    def __init__(
        self,
        sample_rate: int,
        num_channels: int,
    ) -> None:
        """
        Initialize a new acoustic echo cancellation (AEC) instance.

        Parameters:
        - sample_rate (int): The sample rate (in Hz) of the audio to process.
        - num_channels (int): The number of channels in the audio stream.

        Ensure that each processed chunk represents exactly 10 ms of audio for
        reliable echo cancellation.

        Example:
            aec = Aec(sample_rate=48000, num_channels=2)
        """
        self._sample_rate = sample_rate
        self._mum_channels = num_channels

        req = proto_ffi.FfiRequest()
        req.new_aec.sample_rate = sample_rate
        req.new_aec.num_channels = num_channels

        resp = FfiClient.instance.request(req)
        self._ffi_handle = FfiHandle(resp.new_aec.aec.handle.id)

    def cancel_echo(
        self,
        capture_data: bytearray | AudioFrame,
        render_data: bytearray | AudioFrame
    ) -> None:
        """
        Perform in-place echo cancellation on the capture data based on the render data.

        This method processes two separate audio buffers:
        1. capture_data (modified in-place)
        2. render_data (read-only, not modified)

        Parameters:
        - capture_data (bytearray | AudioFrame): The capture audio buffer or frame.
          This buffer will be edited in-place to remove the echo.
        - render_data (bytearray | AudioFrame): The render audio buffer or frame.
          This buffer is read-only and provides the reference signal used to
          remove echo from capture_data.

        Important:
        - Each buffer must represent exactly 10 ms of audio (based on the
          sample rate and number of channels used to initialize Aec).

        Raises:
        - Exception: If the AEC processing fails internally.

        Example:
            # Assuming capture_data and render_data each hold exactly 10 ms of audio:
            aec.cancel_echo(capture_data=capture_data, render_data=render_data)
        """
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

