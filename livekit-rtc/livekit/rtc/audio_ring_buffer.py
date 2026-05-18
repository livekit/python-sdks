from __future__ import annotations

import threading

from .audio_frame import AudioFrame


class AudioRingBuffer:
    """Pre-allocated circular buffer for raw PCM audio data.

    Stores int16 PCM samples in a fixed-size bytearray. Push is zero-allocation.
    """

    def __init__(self, max_duration: float, sample_rate: int, num_channels: int) -> None:
        self._sample_rate = sample_rate
        self._num_channels = num_channels
        self._bytes_per_second = sample_rate * num_channels * 2  # int16
        self._max_bytes = int(max_duration * self._bytes_per_second)
        if self._max_bytes <= 0:
            raise ValueError("max_duration must be positive")

        self._buf = bytearray(self._max_bytes)
        self._write_pos = 0
        self._size = 0
        self._lock = threading.Lock()

    @property
    def duration(self) -> float:
        with self._lock:
            return self._size / self._bytes_per_second

    @property
    def max_duration(self) -> float:
        return self._max_bytes / self._bytes_per_second

    def push(self, frame: AudioFrame) -> None:
        data = frame.data.cast("b")
        n = len(data)
        if n == 0:
            return

        with self._lock:
            if n >= self._max_bytes:
                # frame larger than buffer — keep only the tail
                self._buf[:] = data[n - self._max_bytes :]
                self._write_pos = 0
                self._size = self._max_bytes
                return

            end = self._write_pos + n
            if end <= self._max_bytes:
                self._buf[self._write_pos : end] = data
            else:
                first = self._max_bytes - self._write_pos
                self._buf[self._write_pos : self._max_bytes] = data[:first]
                self._buf[: n - first] = data[first:]

            self._write_pos = end % self._max_bytes
            self._size = min(self._size + n, self._max_bytes)

    def capture(self) -> bytes:
        """Snapshot the buffer contents and reset. Returns raw PCM bytes."""
        with self._lock:
            if self._size == 0:
                return b""

            read_pos = (self._write_pos - self._size) % self._max_bytes
            if read_pos + self._size <= self._max_bytes:
                data = bytes(self._buf[read_pos : read_pos + self._size])
            else:
                first = self._max_bytes - read_pos
                data = bytes(self._buf[read_pos:]) + bytes(self._buf[: self._size - first])

            self._write_pos = 0
            self._size = 0
            return data

    def clear(self) -> None:
        with self._lock:
            self._write_pos = 0
            self._size = 0
