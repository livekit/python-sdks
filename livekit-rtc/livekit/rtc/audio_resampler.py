from __future__ import annotations

import ctypes
from enum import Enum, unique

from ._proto import audio_frame_pb2 as proto_audio_frame
from ._ffi_client import FfiClient, FfiHandle
from ._proto import ffi_pb2 as proto_ffi
from ._utils import get_address
from .audio_frame import AudioFrame


@unique
class AudioResamplerQuality(str, Enum):
    QUICK = "quick"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AudioResampler:
    """
    A class for resampling audio data from one sample rate to another.

    `AudioResampler` provides functionality to resample audio data from an input sample rate to an output
    sample rate using the Sox resampling library. It supports multiple channels and configurable resampling quality.
    """

    def __init__(
        self,
        input_rate: int,
        output_rate: int,
        *,
        num_channels: int = 1,
        quality: AudioResamplerQuality = AudioResamplerQuality.MEDIUM,
    ) -> None:
        """
        Initialize an `AudioResampler` instance for resampling audio data.

        Args:
            input_rate (int): The sample rate of the input audio data (in Hz).
            output_rate (int): The desired sample rate of the output audio data (in Hz).
            num_channels (int, optional): The number of audio channels (e.g., 1 for mono, 2 for stereo). Defaults to 1.
            quality (AudioResamplerQuality, optional): The quality setting for the resampler. Can be one of the
                `AudioResamplerQuality` enum values: `QUICK`, `LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`. Higher quality settings
                result in better audio quality but require more processing power. Defaults to `AudioResamplerQuality.MEDIUM`.

        Raises:
            Exception: If there is an error creating the resampler.
        """
        self._input_rate = input_rate
        self._output_rate = output_rate
        self._num_channels = num_channels

        req = proto_ffi.FfiRequest()
        req.new_sox_resampler.input_rate = input_rate
        req.new_sox_resampler.output_rate = output_rate
        req.new_sox_resampler.num_channels = num_channels
        req.new_sox_resampler.quality_recipe = _to_proto_quality(quality)

        # not exposed for now
        req.new_sox_resampler.input_data_type = (
            proto_audio_frame.SoxResamplerDataType.SOXR_DATATYPE_INT16I
        )
        req.new_sox_resampler.output_data_type = (
            proto_audio_frame.SoxResamplerDataType.SOXR_DATATYPE_INT16I
        )
        req.new_sox_resampler.flags = 0  # default

        resp = FfiClient.instance.request(req)

        if resp.new_sox_resampler.error:
            raise Exception(resp.new_sox_resampler.error)

        self._ffi_handle = FfiHandle(resp.new_sox_resampler.resampler.handle.id)

    def push(self, data: bytearray | AudioFrame) -> list[AudioFrame]:
        """
        Push audio data into the resampler and retrieve any available resampled data.

        This method accepts audio data, resamples it according to the configured input and output rates,
        and returns any resampled data that is available after processing the input.

        Args:
            data (bytearray | AudioFrame): The audio data to resample. This can be a `bytearray` containing
                raw audio bytes in int16le format or an `AudioFrame` object.

        Returns:
            list[AudioFrame]: A list of `AudioFrame` objects containing the resampled audio data.
                The list may be empty if no output data is available yet.

        Raises:
            Exception: If there is an error during resampling.
        """
        bdata = data if isinstance(data, bytearray) else data.data.cast("b")

        req = proto_ffi.FfiRequest()
        req.push_sox_resampler.resampler_handle = self._ffi_handle.handle
        req.push_sox_resampler.data_ptr = get_address(memoryview(bdata))
        req.push_sox_resampler.size = len(bdata)

        resp = FfiClient.instance.request(req)

        if resp.push_sox_resampler.error:
            raise Exception(resp.push_sox_resampler.error)

        if not resp.push_sox_resampler.output_ptr:
            return []

        cdata = (ctypes.c_int8 * resp.push_sox_resampler.size).from_address(
            resp.push_sox_resampler.output_ptr
        )
        output_data = bytearray(cdata)
        return [
            AudioFrame(
                output_data,
                self._output_rate,
                self._num_channels,
                len(output_data)
                // (self._num_channels * ctypes.sizeof(ctypes.c_int16)),
            )
        ]

    def flush(self) -> list[AudioFrame]:
        """
        Flush any remaining audio data through the resampler and retrieve the resampled data.

        This method should be called when no more input data will be provided to ensure that all internal
        buffers are processed and all resampled data is output.

        Returns:
            list[AudioFrame]: A list of `AudioFrame` objects containing the remaining resampled audio data after flushing.
                The list may be empty if no output data remains.

        Raises:
            Exception: If there is an error during flushing.
        """
        req = proto_ffi.FfiRequest()
        req.flush_sox_resampler.resampler_handle = self._ffi_handle.handle

        resp = FfiClient.instance.request(req)

        if not resp.flush_sox_resampler.output_ptr:
            return []

        cdata = (ctypes.c_int8 * resp.flush_sox_resampler.size).from_address(
            resp.flush_sox_resampler.output_ptr
        )
        output_data = bytearray(cdata)
        return [
            AudioFrame(
                output_data,
                self._output_rate,
                self._num_channels,
                len(output_data)
                // (self._num_channels * ctypes.sizeof(ctypes.c_int16)),
            )
        ]


def _to_proto_quality(
    quality: AudioResamplerQuality,
) -> proto_audio_frame.SoxQualityRecipe.ValueType:
    if quality == AudioResamplerQuality.QUICK:
        return proto_audio_frame.SoxQualityRecipe.SOXR_QUALITY_QUICK
    elif quality == AudioResamplerQuality.LOW:
        return proto_audio_frame.SoxQualityRecipe.SOXR_QUALITY_LOW
    elif quality == AudioResamplerQuality.MEDIUM:
        return proto_audio_frame.SoxQualityRecipe.SOXR_QUALITY_MEDIUM
    elif quality == AudioResamplerQuality.HIGH:
        return proto_audio_frame.SoxQualityRecipe.SOXR_QUALITY_HIGH
    elif quality == AudioResamplerQuality.VERY_HIGH:
        return proto_audio_frame.SoxQualityRecipe.SOXR_QUALITY_VERYHIGH
