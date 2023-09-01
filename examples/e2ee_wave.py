import asyncio
import logging
from signal import SIGINT, SIGTERM

import numpy as np

# get livekit module path, FOR TESTING ONLY
# import os
# import sys
# parent_dir = os.path.dirname(os.path.realpath(__file__))
# import_dir = os.path.normpath(os.path.join(parent_dir, os.pardir)) 
# sys.path.append(import_dir)

import livekit

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTUxNzA2OTEsImlzcyI6IkFQSXJramtRYVZRSjVERSIsIm5hbWUiOiJweWUyZWUiLCJuYmYiOjE2OTMzNzA2OTEsInN1YiI6InB5ZTJlZSIsInZpZGVvIjp7InJvb20iOiJsaXZlIiwicm9vbUpvaW4iOnRydWV9fQ.CZnT4fOBjUTxrTlkijxb_D_4HAbZoxljNRjDlCRHNBY'


def on_audio_frame(frame: livekit.AudioFrame):
    logging.info("received audio frame rate %d samples %d channel %d", frame.sample_rate, frame.samples_per_channel, frame.num_channels)
    pass

async def publish_frames(source: livekit.AudioSource):
    sample_rate = 48000
    frequency = 440
    amplitude = 32767  # for 16-bit audio
    num_channels = 1
    samples_per_channel = 480  # 10ms at 48kHz
    time = np.arange(samples_per_channel) / sample_rate
    total_samples = 0

    audio_frame = livekit.AudioFrame.create(
        sample_rate, num_channels, samples_per_channel)

    audio_data = np.ctypeslib.as_array(audio_frame.data)

    while True:
        time = (total_samples + np.arange(samples_per_channel)) / sample_rate

        sine_wave = (amplitude * np.sin(2 * np.pi *
                     frequency * time)).astype(np.int16)
        np.copyto(audio_data, sine_wave)

        source.capture_frame(audio_frame)

        total_samples += samples_per_channel

        try:
            await asyncio.sleep(1 / 100)  # 10m
        except asyncio.CancelledError:
            break


async def main() -> None:
    room = livekit.Room()
    logging.info("connecting to %s", URL)
    
    # listen to e2ee_state_changed event
    @room.listens_to("e2ee_state_changed")
    def on_e2ee_state_changed(participant: livekit.Participant, publication: livekit.TrackPublication, participant_id: str, state: any) -> None:
        logging.info(
            "e2ee state changed for %s %s, track %s, state: %s, e2ee participant_id %s", participant.sid, participant.identity, publication.sid, state, participant_id)
    try:
        await room.connect(URL, TOKEN, options= livekit.RoomOptions(
            auto_subscribe= True,
            dynacast= True,
            e2ee_options= livekit.e2ee.E2EEOptions(),
        ))

        # set shared key for room
        room.e2ee_manager.key_provider.set_shared_key(b"12345678", 0)

        logging.info("connected to room %s", room.name)
    except livekit.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
        return

    # publish a track
    source = livekit.AudioSource()
    source_task = asyncio.create_task(publish_frames(source))

    track = livekit.LocalAudioTrack.create_audio_track("sinewave", source)
    options = livekit.TrackPublishOptions()
    options.source = livekit.TrackSource.SOURCE_MICROPHONE
    publication = await room.local_participant.publish_track(track, options)
    logging.info("published track %s", publication.sid)
    
    try:
        await room.run()
    except asyncio.CancelledError:
        logging.info("closing the room")
        source_task.cancel()
        await source_task
        await room.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("publish_wave.log"), logging.StreamHandler()])

    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main())
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
