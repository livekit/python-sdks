import asyncio
import logging
from signal import SIGINT, SIGTERM

import numpy as np

import livekit

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'  # noqa

SAMPLE_RATE = 48000
NUM_CHANNELS = 1


async def publish_frames(source: livekit.AudioSource):
    frequency = 440
    amplitude = 32767  # for 16-bit audio
    samples_per_channel = 480  # 10ms at 48kHz
    time = np.arange(samples_per_channel) / SAMPLE_RATE
    total_samples = 0

    audio_frame = livekit.AudioFrame.create(
        SAMPLE_RATE, NUM_CHANNELS, samples_per_channel)

    audio_data = np.ctypeslib.as_array(audio_frame.data)

    while True:
        time = (total_samples + np.arange(samples_per_channel)) / SAMPLE_RATE

        sine_wave = (amplitude * np.sin(2 * np.pi *
                     frequency * time)).astype(np.int16)
        np.copyto(audio_data, sine_wave)

        await source.capture_frame(audio_frame)

        total_samples += samples_per_channel


async def main() -> None:
    room = livekit.Room()

    logging.info("connecting to %s", URL)
    try:
        await room.connect(URL, TOKEN)
        logging.info("connected to room %s", room.name)
    except livekit.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
        return

    # publish a track
    source = livekit.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
    track = livekit.LocalAudioTrack.create_audio_track("sinewave", source)
    options = livekit.TrackPublishOptions()
    options.source = livekit.TrackSource.SOURCE_MICROPHONE
    publication = await room.local_participant.publish_track(track, options)
    logging.info("published track %s", publication.sid)

    asyncio.ensure_future(publish_frames(source))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("publish_wave.log"),
                        logging.StreamHandler()])

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, loop.stop)
    try:
        loop.run_forever()
    finally:
        loop.close()
