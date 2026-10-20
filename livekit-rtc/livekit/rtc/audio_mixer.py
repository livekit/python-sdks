import asyncio
import numpy as np
import contextlib
from dataclasses import dataclass
from typing import AsyncIterator, Optional
from .audio_frame import AudioFrame
from .log import logger

_Stream = AsyncIterator[AudioFrame]

# consecutive timeouts after which a stream is dropped once end_input() was called
_MAX_STALLED_ROUNDS = 10


@dataclass
class _Contribution:
    stream: _Stream
    data: np.ndarray
    buffer: np.ndarray
    had_data: bool
    exhausted: bool


class AudioMixer:
    def __init__(
        self,
        sample_rate: int,
        num_channels: int,
        *,
        blocksize: int = 0,
        stream_timeout_ms: int = 100,
        capacity: int = 100,
    ) -> None:
        """
        Initialize the AudioMixer.

        The mixer accepts multiple async audio streams and mixes them into a single output stream.
        Each output frame is generated with a fixed chunk size determined by the blocksize (in samples).
        If blocksize is not provided (or 0), it defaults to 100ms.

        Each input stream is processed in parallel, accumulating audio data until at least one chunk
        of samples is available. If an input stream does not provide data within the specified timeout,
        a warning is logged. The mixer can be closed immediately
        (dropping unconsumed frames) or allowed to flush remaining data using end_input().

        Args:
            sample_rate (int): The audio sample rate in Hz.
            num_channels (int): The number of audio channels.
            blocksize (int, optional): The size of the audio block (in samples) for mixing. If not provided,
                defaults to sample_rate // 10.
            stream_timeout_ms (int, optional): The maximum wait time in milliseconds for each stream to provide
                audio data before timing out. Defaults to 100 ms.
            capacity (int, optional): The maximum number of mixed frames to store in the output queue.
                Defaults to 100.
        """
        self._streams: set[_Stream] = set()
        self._buffers: dict[_Stream, np.ndarray] = {}
        # A read that timed out is kept for the next round: cancelling it would close an
        # async generator stream for good.
        self._pending_reads: dict[_Stream, asyncio.Future[AudioFrame]] = {}
        self._stalled_rounds: dict[_Stream, int] = {}
        self._sample_rate: int = sample_rate
        self._num_channels: int = num_channels
        self._chunk_size: int = blocksize if blocksize > 0 else int(sample_rate // 10)
        self._stream_timeout_ms: int = stream_timeout_ms
        self._queue: asyncio.Queue[Optional[AudioFrame]] = asyncio.Queue(maxsize=capacity)
        # _ending signals that no new streams will be added,
        # but we continue processing until all streams are exhausted.
        self._ending: bool = False
        self._closed: bool = False
        self._mixer_task: asyncio.Task = asyncio.create_task(self._mixer())

    def add_stream(self, stream: AsyncIterator[AudioFrame]) -> None:
        """
        Add an audio stream to the mixer.

        The stream is added to the internal set of streams and an empty buffer is initialized for it,
        if not already present.

        Args:
            stream (AsyncIterator[AudioFrame]): An async iterator that produces AudioFrame objects.
        """
        if self._ending:
            raise RuntimeError("Cannot add stream after mixer has been closed")

        self._streams.add(stream)
        if stream not in self._buffers:
            self._buffers[stream] = np.empty((0, self._num_channels), dtype=np.int16)

    def remove_stream(self, stream: AsyncIterator[AudioFrame]) -> None:
        """
        Remove an audio stream from the mixer.

        This method removes the specified stream and its associated buffer from the mixer.

        Args:
            stream (AsyncIterator[AudioFrame]): The audio stream to remove.
        """
        self._streams.discard(stream)
        self._buffers.pop(stream, None)
        self._stalled_rounds.pop(stream, None)
        pending = self._pending_reads.pop(stream, None)
        if pending is not None:
            _discard_read(pending)

    def __aiter__(self) -> "AudioMixer":
        return self

    async def __anext__(self) -> AudioFrame:
        if self._closed:
            raise StopAsyncIteration
        item = await self._queue.get()
        if item is None:
            self._closed = True
            raise StopAsyncIteration
        return item

    async def aclose(self) -> None:
        """
        Immediately stop mixing and close the mixer.

        This cancels the mixing task and drops any unconsumed output in the queue.
        An iterator waiting for output is released, and subsequent iteration stops.
        Pending stream reads are cancelled and awaited, so a stream must let
        asyncio.CancelledError propagate once its cleanup is done.
        """
        self._ending = True
        self._closed = True
        try:
            self._mixer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._mixer_task
            pending = list(self._pending_reads.values())
            self._pending_reads.clear()
            for read in pending:
                _discard_read(read)
            # let the streams finish their cleanup before the mixer counts as closed
            await asyncio.gather(*pending, return_exceptions=True)
        finally:
            while not self._queue.empty():
                self._queue.get_nowait()
            self._queue.put_nowait(None)

    def end_input(self) -> None:
        """
        Signal that no more streams will be added.

        This method marks the mixer as closed so that it flushes any remaining buffered output before ending.
        Note that existing streams will still be processed until exhausted.
        """
        self._ending = True

    async def _mixer(self) -> None:
        while True:
            # If we're in ending mode and there are no more streams, exit.
            if self._ending and not self._streams:
                break

            if not self._streams:
                await asyncio.sleep(0.01)
                continue

            tasks = [
                self._get_contribution(
                    stream,
                    self._buffers.get(stream, np.empty((0, self._num_channels), dtype=np.int16)),
                )
                for stream in list(self._streams)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            contributions = []
            any_data = False
            removals = []
            for contrib in results:
                if not isinstance(contrib, _Contribution):
                    continue

                contributions.append(contrib.data.astype(np.float32))
                self._buffers[contrib.stream] = contrib.buffer
                if contrib.had_data:
                    any_data = True
                if contrib.exhausted and contrib.buffer.shape[0] == 0:
                    removals.append(contrib.stream)

            for stream in removals:
                self.remove_stream(stream)

            if not any_data:
                await asyncio.sleep(0.001)
                continue

            mixed = np.sum(np.stack(contributions, axis=0), axis=0)
            mixed = np.clip(mixed, -32768, 32767).astype(np.int16)
            frame = AudioFrame(
                mixed.tobytes(), self._sample_rate, self._num_channels, self._chunk_size
            )
            await self._queue.put(frame)

        await self._queue.put(None)

    async def _get_contribution(
        self, stream: AsyncIterator[AudioFrame], buf: np.ndarray
    ) -> _Contribution:
        had_data = buf.shape[0] > 0
        exhausted = False
        # a round scheduled before remove_stream() must not start a new read on that stream
        while buf.shape[0] < self._chunk_size and not exhausted and stream in self._streams:
            # The read stays in _pending_reads until it completes, so remove_stream()
            # and aclose() can always cancel it.
            read = self._pending_reads.get(stream)
            if read is None:
                read = asyncio.ensure_future(stream.__anext__())
                self._pending_reads[stream] = read
            done, _ = await asyncio.wait({read}, timeout=self._stream_timeout_ms / 1000)
            if not done:
                logger.warning(f"AudioMixer: stream {stream} timeout, ignoring")
                stalled = self._stalled_rounds.get(stream, 0) + 1
                self._stalled_rounds[stream] = stalled
                # after end_input() a stream that keeps stalling is dropped, so the drain ends
                exhausted = self._ending and stalled >= _MAX_STALLED_ROUNDS
                break
            self._stalled_rounds.pop(stream, None)
            if self._pending_reads.get(stream) is read:
                del self._pending_reads[stream]
            try:
                frame = read.result()
            except StopAsyncIteration:
                exhausted = True
                break
            except asyncio.TimeoutError:
                # raised by the stream itself: handled like the mixer's own timeout, as before
                logger.warning(f"AudioMixer: stream {stream} timeout, ignoring")
                break
            new_data = np.frombuffer(frame.data.tobytes(), dtype=np.int16).reshape(
                -1, self._num_channels
            )
            buf = np.concatenate((buf, new_data), axis=0) if buf.size else new_data
            had_data = True
        if buf.shape[0] >= self._chunk_size:
            contrib, buf = buf[: self._chunk_size], buf[self._chunk_size :]
        else:
            pad = np.zeros((self._chunk_size - buf.shape[0], self._num_channels), dtype=np.int16)
            contrib, buf = (
                np.concatenate((buf, pad), axis=0),
                np.empty((0, self._num_channels), dtype=np.int16),
            )
        return _Contribution(stream, contrib, buf, had_data, exhausted)


def _discard_read(read: "asyncio.Future[AudioFrame]") -> None:
    """Cancel a read that is no longer wanted and consume its outcome whenever it ends."""
    read.cancel()
    read.add_done_callback(_consume_outcome)


def _consume_outcome(read: "asyncio.Future[AudioFrame]") -> None:
    if not read.cancelled():
        read.exception()  # mark a failed read as handled
