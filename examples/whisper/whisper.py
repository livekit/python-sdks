import asyncio
import logging
from signal import SIGINT, SIGTERM

import livekit

import numpy as np
from whispercpp import Whisper

tasks = set()


URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'  # noqa


WHISPER_SAMPLE_RATE = 16000
SAMPLES_STEP = WHISPER_SAMPLE_RATE * 3  # 3 seconds of new data


async def audio_frame_loop(stream: livekit.AudioStream):
    whisper = Whisper.from_pretrained("tiny.en")
    data = np.zeros(SAMPLES_STEP, dtype=np.float32)
    written_samples = 0

    async for frame_coro in stream:
        raw_frame = await frame_coro
        # whisper requires 16kHz mono, so resample the data
        # also convert the samples from int16 to float32
        frame = raw_frame.remix_and_resample(WHISPER_SAMPLE_RATE, 1)
        frame_data = np.array(frame.data, dtype=np.float32) / 32768.0

        # write the data inside data_30_secs at written_samples
        data[written_samples:written_samples + len(data)] = frame_data
        written_samples += len(data)

        if written_samples >= SAMPLES_STEP:
            res = whisper.transcribe(data)
            written_samples = 0
            print(res)


async def main():
    room = livekit.Room()
    audio_stream = None

    @room.listens_to("track_published")
    def on_track_published(publication: livekit.RemoteTrackPublication,
                           participant: livekit.RemoteParticipant):
        # Only subscribe to the audio tracks coming from the microphone
        if publication.kind == livekit.TrackKind.KIND_AUDIO \
                and publication.source == livekit.TrackSource.SOURCE_MICROPHONE:
            logging.info("track published: %s from participant %s (%s), subscribing...",
                         publication.sid, participant.sid, participant.identity)

            publication.set_subscribed(True)

    @room.listens_to("track_subscribed")
    def on_track_subscribed(track: livekit.Track,
                            publication: livekit.RemoteTrackPublication,
                            participant: livekit.RemoteParticipant):
        logging.info("starting listening to: %s", participant.identity)
        nonlocal audio_stream
        audio_stream = livekit.AudioStream(track)
        task = asyncio.create_task(audio_frame_loop(audio_stream))
        tasks.add(task)
        task.add_done_callback(tasks.remove)

    try:
        logging.info("connecting to %s", URL)
        await room.connect(URL, TOKEN, livekit.RoomOptions(auto_subscribe=False))
        logging.info("connected to room %s", room.name)

        # check if there are already published audio tracks
        for participant in room.participants.values():
            for track in participant.tracks.values():
                if track.kind == livekit.TrackKind.KIND_AUDIO \
                        and track.source == livekit.TrackSource.SOURCE_MICROPHONE:
                    track.set_subscribed(True)

        await room.run()
    except livekit.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
    except asyncio.CancelledError:
        logging.info("closing the room")
        await room.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

