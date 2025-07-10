import asyncio
import os
import numpy as np
import sounddevice as sd

from livekit import rtc, api
from livekit.plugins import noise_cancellation

SAMPLERATE = 48000
BLOCKSIZE = 480  # 10ms chunks at 48kHz
CHANNELS = 1


class AudioBuffer:
    def __init__(self, blocksize=BLOCKSIZE):
        self.blocksize = blocksize
        self.buffer = np.array([], dtype=np.int16)

    def add_frame(self, frame_data):
        self.buffer = np.concatenate([self.buffer, frame_data])

    def get_chunk(self):
        if len(self.buffer) >= self.blocksize:
            chunk = self.buffer[: self.blocksize]
            self.buffer = self.buffer[self.blocksize :]
            return chunk
        return None

    def get_padded_chunk(self):
        if len(self.buffer) > 0:
            chunk = np.zeros(self.blocksize, dtype=np.int16)
            available = min(len(self.buffer), self.blocksize)
            chunk[:available] = self.buffer[:available]
            self.buffer = self.buffer[available:]
            return chunk
        return np.zeros(self.blocksize, dtype=np.int16)


async def audio_player(queue: asyncio.Queue):
    """Pull from the queue and stream audio using sounddevice."""
    buffer = AudioBuffer(BLOCKSIZE)

    def callback(outdata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")

        # Try to fill buffer from queue
        while not queue.empty():
            try:
                data = queue.get_nowait()
                buffer.add_frame(data)
            except asyncio.QueueEmpty:
                break

        # Get exactly the right amount of data
        chunk = buffer.get_chunk()
        if chunk is not None:
            outdata[:] = chunk.reshape(-1, 1)
        else:
            # Not enough data, use what we have padded with zeros
            outdata[:] = buffer.get_padded_chunk().reshape(-1, 1)

    stream = sd.OutputStream(
        samplerate=SAMPLERATE,
        channels=CHANNELS,
        blocksize=BLOCKSIZE,
        dtype="int16",
        callback=callback,
        latency="low",
    )
    with stream:
        while True:
            await asyncio.sleep(0.1)  # keep the loop alive


async def rtc_session(room, queue: asyncio.Queue):
    track: rtc.RemoteAudioTrack | None = None
    while not track:
        for participant in room.remote_participants.values():
            for t in participant.track_publications.values():
                if t.kind == rtc.TrackKind.KIND_AUDIO and t.subscribed:
                    track = t.track
                    break
            if track:
                break
        if not track:
            print("waiting for audio track")
            await asyncio.sleep(2)

    stream = rtc.AudioStream.from_track(
        track=track,
        sample_rate=SAMPLERATE,
        num_channels=1,
        noise_cancellation=noise_cancellation.BVC(),  # or NC()
    )

    print("playing stream")
    try:
        # Process audio frames from the stream
        async for audio_frame_event in stream:
            frame = audio_frame_event.frame

            audio_data = np.frombuffer(frame.data, dtype=np.int16)

            try:
                await queue.put(audio_data)
            except asyncio.QueueFull:
                # Skip this frame if queue is full
                print("Warning: Audio queue full, dropping frame")
                continue

    finally:
        # Clean up the stream when done
        await stream.aclose()


async def main():
    queue = asyncio.Queue(maxsize=50)
    player_task = asyncio.create_task(audio_player(queue))

    token = (
        api.AccessToken()
        .with_identity("python-bot")
        .with_name("Python Bot")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room="my-room",
                agent=True,
            )
        )
        .to_jwt()
    )
    url = os.getenv("LIVEKIT_URL")

    room = rtc.Room()
    await room.connect(
        url,
        token,
        options=rtc.RoomOptions(
            auto_subscribe=True,
        ),
    )
    print(f"Connected to room: {room.name}")

    try:
        await rtc_session(room, queue)
    finally:
        # Clean up
        await room.disconnect()
        player_task.cancel()
        try:
            await player_task
        except asyncio.CancelledError:
            pass


asyncio.run(main())
