import asyncio
import logging
from signal import SIGINT, SIGTERM

import numpy as np

import livekit

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'  # noqa

SAMPLE_RATE = 48000
NUM_CHANNELS = 1


async def publish_sine(source: livekit.AudioSource):
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


async def publish_pulse(source: livekit.AudioSource):
    frequency = 440
    modulation_frequency = 1.0  # 1Hz for beep once every second
    beep_duration = 0.5  # Beep for half a second, then silence for half a second
    amplitude = 32767  # for 16-bit audio
    samples_per_channel = 480  # 10ms at 48kHz
    total_samples = 0

    audio_frame = livekit.AudioFrame.create(
        SAMPLE_RATE, NUM_CHANNELS, samples_per_channel)

    audio_data = np.ctypeslib.as_array(audio_frame.data)

    while True:
        time = (total_samples + np.arange(samples_per_channel)) / SAMPLE_RATE

        sine_wave = amplitude * np.sin(2 * np.pi * frequency * time)

        # Square wave for clear beep effect
        square_wave = (
            np.sign(np.sin(2 * np.pi * modulation_frequency * time)) + 1) / 2
        # Zero out the sine wave where the square wave is zero (during the "off" portion of the beep)
        beeping_sine = sine_wave * square_wave

        # Limit beep duration
        beeping_sine[time % (1/modulation_frequency) > beep_duration] = 0

        np.copyto(audio_data, beeping_sine.astype(np.int16))

        await source.capture_frame(audio_frame)

        total_samples += samples_per_channel


async def main(room: livekit.Room) -> None:
    logging.info("connecting to %s", URL)
    try:
        e2ee_options = livekit.E2EEOptions()
        e2ee_options.key_provider_options.shared_key = b'livekitrocks'

        await room.connect(URL, TOKEN, options=livekit.RoomOptions(
            e2ee=e2ee_options
        ))
        logging.info("connected to room %s", room.name)
    except livekit.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
        return

    @room.on('e2ee_state_changed')
    def e2ee_changed(participant, state):
        logging.info("decryption changed %s: %s", participant.identity, state)

    # publish a track
    source = livekit.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
    track = livekit.LocalAudioTrack.create_audio_track("sinewave", source)
    options = livekit.TrackPublishOptions(
        source=livekit.TrackSource.SOURCE_MICROPHONE,
    )
    publication = await room.local_participant.publish_track(track, options)
    logging.info("published track %s", publication.sid)
    asyncio.ensure_future(publish_sine(source))

    await asyncio.sleep(1)

    source2 = livekit.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
    track2 = livekit.LocalAudioTrack.create_audio_track("sinewave2", source2)
    publication = await room.local_participant.publish_track(track2, options)
    logging.info("published track 2 %s", publication.sid)
    asyncio.ensure_future(publish_sine(source2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("publish_wave.log"),
                        logging.StreamHandler()])

    loop = asyncio.get_event_loop()
    room = livekit.Room(loop=loop)

    async def cleanup():
        await room.disconnect()
        loop.stop()

    asyncio.ensure_future(main(room))
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(
            signal, lambda: asyncio.ensure_future(cleanup()))

    try:
        loop.run_forever()
    finally:
        loop.close()
