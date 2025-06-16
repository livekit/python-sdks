# Copyright 2023 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ctypes
from ._ffi_client import FfiHandle
from ._proto import audio_frame_pb2 as proto_audio
from ._utils import get_address
from typing import Any, Union


class AudioFrame:
    """
    A class that represents a frame of audio data with specific properties such as sample rate,
    number of channels, and samples per channel.

    The format of the audio data is 16-bit signed integers (int16) interleaved by channel.
    """

    def __init__(
        self,
        data: Union[bytes, bytearray, memoryview],
        sample_rate: int,
        num_channels: int,
        samples_per_channel: int,
    ) -> None:
        """
        Initialize an AudioFrame instance.

        Args:
            data (Union[bytes, bytearray, memoryview]): The raw audio data, which must be at least
                `num_channels * samples_per_channel * sizeof(int16)` bytes long.
            sample_rate (int): The sample rate of the audio in Hz.
            num_channels (int): The number of audio channels (e.g., 1 for mono, 2 for stereo).
            samples_per_channel (int): The number of samples per channel.

        Raises:
            ValueError: If the length of `data` is smaller than the required size.
        """
        data = memoryview(data).cast("B")

        if len(data) < num_channels * samples_per_channel * ctypes.sizeof(ctypes.c_int16):
            raise ValueError(
                "data length must be >= num_channels * samples_per_channel * sizeof(int16)"
            )

        if len(data) % ctypes.sizeof(ctypes.c_int16) != 0:
            # can happen if data is bigger than needed
            raise ValueError("data length must be a multiple of sizeof(int16)")

        n = len(data) // ctypes.sizeof(ctypes.c_int16)
        self._data = (ctypes.c_int16 * n).from_buffer_copy(data)

        self._sample_rate = sample_rate
        self._num_channels = num_channels
        self._samples_per_channel = samples_per_channel
        self._userdata: dict[str, Any] = {}

    @staticmethod
    def create(sample_rate: int, num_channels: int, samples_per_channel: int) -> "AudioFrame":
        """
        Create a new empty AudioFrame instance with specified sample rate, number of channels,
        and samples per channel.

        Args:
            sample_rate (int): The sample rate of the audio in Hz.
            num_channels (int): The number of audio channels (e.g., 1 for mono, 2 for stereo).
            samples_per_channel (int): The number of samples per channel.

        Returns:
            AudioFrame: A new AudioFrame instance with uninitialized (zeroed) data.
        """
        size = num_channels * samples_per_channel * ctypes.sizeof(ctypes.c_int16)
        data = bytearray(size)
        return AudioFrame(data, sample_rate, num_channels, samples_per_channel)

    @staticmethod
    def _from_owned_info(owned_info: proto_audio.OwnedAudioFrameBuffer) -> "AudioFrame":
        info = owned_info.info
        size = info.num_channels * info.samples_per_channel
        cdata = (ctypes.c_int16 * size).from_address(info.data_ptr)
        data = bytearray(cdata)
        FfiHandle(owned_info.handle.id)
        return AudioFrame(data, info.sample_rate, info.num_channels, info.samples_per_channel)

    def _proto_info(self) -> proto_audio.AudioFrameBufferInfo:
        audio_info = proto_audio.AudioFrameBufferInfo()
        audio_info.data_ptr = get_address(memoryview(self._data))
        audio_info.sample_rate = self.sample_rate
        audio_info.num_channels = self.num_channels
        audio_info.samples_per_channel = self.samples_per_channel
        return audio_info

    @property
    def userdata(self) -> dict[str, Any]:
        """
        Returns the user data associated with the audio frame.
        """
        return self._userdata

    @property
    def data(self) -> memoryview:
        """
        Returns a memory view of the audio data as 16-bit signed integers.

        Returns:
            memoryview: A memory view of the audio data.
        """
        return memoryview(self._data).cast("B").cast("h")

    @property
    def sample_rate(self) -> int:
        """
        Returns the sample rate of the audio frame.

        Returns:
            int: The sample rate in Hz.
        """
        return self._sample_rate

    @property
    def num_channels(self) -> int:
        """
        Returns the number of channels in the audio frame.

        Returns:
            int: The number of audio channels (e.g., 1 for mono, 2 for stereo).
        """
        return self._num_channels

    @property
    def samples_per_channel(self) -> int:
        """
        Returns the number of samples per channel.

        Returns:
            int: The number of samples per channel.
        """
        return self._samples_per_channel

    @property
    def duration(self) -> float:
        """
        Returns the duration of the audio frame in seconds.

        Returns:
            float: The duration in seconds.
        """
        return self.samples_per_channel / self.sample_rate

    def to_wav_bytes(self) -> bytes:
        """
        Convert the audio frame data to a WAV-formatted byte stream.

        Returns:
            bytes: The audio data encoded in WAV format.
        """
        import wave
        import io

        with io.BytesIO() as wav_file:
            with wave.open(wav_file, "wb") as wav:
                wav.setnchannels(self.num_channels)
                wav.setsampwidth(2)
                wav.setframerate(self.sample_rate)
                wav.writeframes(self._data)

            return wav_file.getvalue()

    def __repr__(self) -> str:
        return (
            f"rtc.AudioFrame(sample_rate={self.sample_rate}, "
            f"num_channels={self.num_channels}, "
            f"samples_per_channel={self.samples_per_channel}, "
            f"duration={self.duration:.3f})"
        )

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any):
        from pydantic_core import core_schema
        import base64

        def validate_audio_frame(value: Any) -> "AudioFrame":
            if isinstance(value, AudioFrame):
                return value

            if isinstance(value, tuple):
                value = value[0]

            if isinstance(value, dict):
                return AudioFrame(
                    data=base64.b64decode(value["data"]),
                    sample_rate=value["sample_rate"],
                    num_channels=value["num_channels"],
                    samples_per_channel=value["samples_per_channel"],
                )

            raise TypeError("Invalid type for AudioFrame")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.model_fields_schema(
                        {
                            "data": core_schema.model_field(core_schema.str_schema()),
                            "sample_rate": core_schema.model_field(core_schema.int_schema()),
                            "num_channels": core_schema.model_field(core_schema.int_schema()),
                            "samples_per_channel": core_schema.model_field(
                                core_schema.int_schema()
                            ),
                        },
                    ),
                    core_schema.no_info_plain_validator_function(validate_audio_frame),
                ]
            ),
            python_schema=core_schema.no_info_plain_validator_function(validate_audio_frame),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: {
                    "data": base64.b64encode(instance.data).decode("utf-8"),
                    "sample_rate": instance.sample_rate,
                    "num_channels": instance.num_channels,
                    "samples_per_channel": instance.samples_per_channel,
                }
            ),
        )
