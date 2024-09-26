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
    def __init__(
        self,
        input_rate: int,
        output_rate: int,
        *,
        num_channels: int = 1,
        quality: AudioResamplerQuality = AudioResamplerQuality.HIGH,
    ) -> None:
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
        bdata = data if isinstance(data, bytearray) else data.data

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
        req = proto_ffi.FfiRequest()
        req.flush_sox_resampler.resampler_handle = self._ffi_handle.handle

        resp = FfiClient.instance.request(req)

        if not resp.flush_sox_resampler.output_ptr:
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
