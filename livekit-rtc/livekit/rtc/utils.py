from __future__ import annotations

from .audio_frame import AudioFrame


__all__ = ["combine_audio_frames"]


def combine_audio_frames(buffer: AudioFrame | list[AudioFrame]) -> AudioFrame:
    """
    Combines one or more `rtc.AudioFrame` objects into a single `rtc.AudioFrame`.

    This function concatenates the audio data from multiple frames, ensuring that
    all frames have the same sample rate and number of channels. It efficiently
    merges the data by preallocating the necessary memory and copying the frame
    data without unnecessary reallocations.

    Args:
        buffer: A single `rtc.AudioFrame` or a list of `rtc.AudioFrame`
            objects to be combined.

    Returns:
        rtc.AudioFrame: A new `rtc.AudioFrame` containing the combined audio data.

    Raises:
        ValueError: If the buffer is empty.
        ValueError: If frames have differing sample rates.
        ValueError: If frames have differing numbers of channels.

    Example:
        >>> frame1 = rtc.AudioFrame(
        ...     data=b"\x01\x02", sample_rate=48000, num_channels=2, samples_per_channel=1
        ... )
        >>> frame2 = rtc.AudioFrame(
        ...     data=b"\x03\x04", sample_rate=48000, num_channels=2, samples_per_channel=1
        ... )
        >>> combined_frame = combine_audio_frames([frame1, frame2])
        >>> combined_frame.data
        b'\x01\x02\x03\x04'
        >>> combined_frame.sample_rate
        48000
        >>> combined_frame.num_channels
        2
        >>> combined_frame.samples_per_channel
        2
    """
    if not isinstance(buffer, list):
        return buffer

    if not buffer:
        raise ValueError("buffer is empty")

    sample_rate = buffer[0].sample_rate
    num_channels = buffer[0].num_channels

    total_data_length = 0
    total_samples_per_channel = 0

    for frame in buffer:
        if frame.sample_rate != sample_rate:
            raise ValueError(
                f"Sample rate mismatch: expected {sample_rate}, got {frame.sample_rate}"
            )

        if frame.num_channels != num_channels:
            raise ValueError(
                f"Channel count mismatch: expected {num_channels}, got {frame.num_channels}"
            )

        total_data_length += len(frame.data)
        total_samples_per_channel += frame.samples_per_channel

    data = bytearray(total_data_length)
    offset = 0
    for frame in buffer:
        frame_data = frame.data.cast("b")
        data[offset : offset + len(frame_data)] = frame_data
        offset += len(frame_data)

    return AudioFrame(
        data=data,
        sample_rate=sample_rate,
        num_channels=num_channels,
        samples_per_channel=total_samples_per_channel,
    )
