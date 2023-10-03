import asyncio
import ctypes
import logging
import pathlib
import platform
from signal import SIGINT, SIGTERM

import numpy as np
from livekit import rtc

os = platform.system().lower()
if os == "windows":
    lib_file = 'whisper.dll'
elif os == "darwin":
    lib_file = 'libwhisper.dylib'
else:
    lib_file = 'libwhisper.so'

whisper_dir = pathlib.Path(__file__).parent.absolute() / "whisper.cpp"
libname = str(whisper_dir / lib_file)
fname_model = str(whisper_dir / "models/ggml-tiny.en.bin")

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'  # noqa


# declare the Whisper C API  (Only what we need, keep things simple)
# also see this issue: https://github.com/ggerganov/whisper.cpp/issues/9
# structure must match https://github.com/ggerganov/whisper.cpp/blob/master/whisper.h


class WhisperSamplingStrategy(ctypes.c_int):
    WHISPER_SAMPLING_GREEDY = 0
    WHISPER_SAMPLING_BEAM_SEARCH = 1


class WhisperFullParams(ctypes.Structure):
    _fields_ = [
        ('strategy', ctypes.c_int),
        ('n_threads',  ctypes.c_int),
        ('n_max_text_ctx', ctypes.c_int),
        ('offset_ms', ctypes.c_int),
        ('duration_ms', ctypes.c_int),
        ('translate', ctypes.c_bool),
        ('no_context', ctypes.c_bool),
        ('single_segment', ctypes.c_bool),
        ('print_special', ctypes.c_bool),
        ('print_progress', ctypes.c_bool),
        ('print_realtime', ctypes.c_bool),
        ('print_timestamps', ctypes.c_bool),
        ('token_timestamps', ctypes.c_bool),
        ('thold_pt', ctypes.c_float),
        ('thold_ptsum', ctypes.c_float),
        ('max_len', ctypes.c_int),
        ('split_on_word', ctypes.c_bool),
        ('max_tokens', ctypes.c_int),
        ('speed_up', ctypes. c_bool),
        ('audio_ctx', ctypes. c_int),
        ('tdrz_enable', ctypes. c_bool),
        ('initial_prompt', ctypes.c_char_p),
        ('prompt_tokens', ctypes.c_void_p),
        ('prompt_n_tokens', ctypes.c_int),
        ('language', ctypes.c_char_p),
        ('detect_language', ctypes.c_bool),
        ('suppress_blank', ctypes.c_bool),
        ('suppress_non_speech_tokens', ctypes.c_bool),
        ('temperature', ctypes.c_float),
        ('max_initial_ts', ctypes.c_float),
        ('length_penalty', ctypes.c_float),
        ('temperature_inc', ctypes. c_float),
        ('entropy_thold', ctypes. c_float),
        ('logprob_thold', ctypes. c_float),
        ('no_speech_thold', ctypes. c_float),
        ('greedy', ctypes.c_int),
        ('beam_size', ctypes.c_int),
        ('patience', ctypes.c_float),
        ('new_segment_callback', ctypes.c_void_p),
        ('new_segment_callback_user_data', ctypes.c_void_p),
        ('progress_callback', ctypes.c_void_p),
        ('progress_callback_user_data', ctypes.c_void_p),
        ('encoder_begin_callback', ctypes.c_void_p),
        ('encoder_begin_callback_user_data', ctypes.c_void_p),
        ('logits_filter_callback', ctypes.c_void_p),
        ('logits_filter_callback_user_data', ctypes.c_void_p),
    ]


WHISPER_SAMPLE_RATE = 16000
SAMPLES_30_SECS = WHISPER_SAMPLE_RATE * 30
SAMPLES_KEEP = WHISPER_SAMPLE_RATE * 1  # data to keep from the old inference
SAMPLES_STEP = WHISPER_SAMPLE_RATE * 3  # 3 seconds of new data

whisper = ctypes.CDLL(libname)
whisper.whisper_init_from_file.argtypes = [ctypes.c_char_p]
whisper.whisper_init_from_file.restype = ctypes.c_void_p
whisper.whisper_full_default_params.restype = WhisperFullParams
whisper.whisper_full_get_segment_text.restype = ctypes.c_char_p
ctx = whisper.whisper_init_from_file(fname_model.encode('utf-8'))


async def whisper_task(stream: rtc.AudioStream):
    data_30_secs = np.zeros(SAMPLES_30_SECS, dtype=np.float32)
    written_samples = 0  # nb. of samples written to data_30_secs for the cur. inference

    async for frame in stream:
        # whisper requires 16kHz mono, so resample the data
        # also convert the samples from int16 to float32
        frame = frame.remix_and_resample(
            WHISPER_SAMPLE_RATE, 1)

        data = np.array(frame.data, dtype=np.float32) / 32768.0

        # write the data inside data_30_secs at written_samples
        data_start = SAMPLES_KEEP + written_samples
        data_30_secs[data_start:data_start+len(data)] = data
        written_samples += len(data)

        if written_samples >= SAMPLES_STEP:
            params = whisper.whisper_full_default_params(
                WhisperSamplingStrategy.WHISPER_SAMPLING_GREEDY)
            params.print_realtime = False
            params.print_progress = False

            ctx_ptr = ctypes.c_void_p(ctx)
            data_ptr = data_30_secs.ctypes.data_as(
                ctypes.POINTER(ctypes.c_float))
            res = whisper.whisper_full(ctx_ptr,
                                       params,
                                       data_ptr,
                                       written_samples + SAMPLES_KEEP)

            if res != 0:
                logging.error("error while running inference: %s", res)
                return

            n_segments = whisper.whisper_full_n_segments(ctx_ptr)
            for i in range(n_segments):
                t0 = whisper.whisper_full_get_segment_t0(ctx_ptr, i)
                t1 = whisper.whisper_full_get_segment_t1(ctx_ptr, i)
                txt = whisper.whisper_full_get_segment_text(ctx_ptr, i)

                logging.info(
                    f"{t0/1000.0:.3f} - {t1/1000.0:.3f} : {txt.decode('utf-8')}")

            # write old data to the beginning of the buffer (SAMPLES_KEEP)
            data_30_secs[:SAMPLES_KEEP] = data_30_secs[data_start +
                                                       written_samples - SAMPLES_KEEP:
                                                       data_start + written_samples]
            written_samples = 0


async def main(room: rtc.Room):
    @room.listens_to("track_published")
    def on_track_published(publication: rtc.RemoteTrackPublication,
                           participant: rtc.RemoteParticipant):
        # Only subscribe to the audio tracks coming from the microphone
        if publication.kind == rtc.TrackKind.KIND_AUDIO \
                and publication.source == rtc.TrackSource.SOURCE_MICROPHONE:
            logging.info("track published: %s from participant %s (%s), subscribing...",
                         publication.sid, participant.sid, participant.identity)

            publication.set_subscribed(True)

    @room.listens_to("track_subscribed")
    def on_track_subscribed(track: rtc.Track,
                            publication: rtc.RemoteTrackPublication,
                            participant: rtc.RemoteParticipant):
        logging.info("starting listening to: %s", participant.identity)
        audio_stream = rtc.AudioStream(track)
        asyncio.create_task(whisper_task(audio_stream))

    await room.connect(URL, TOKEN, rtc.RoomOptions(auto_subscribe=False))
    logging.info("connected to room %s", room.name)

    # check if there are already published audio tracks
    for participant in room.participants.values():
        for track in participant.tracks.values():
            if track.kind == rtc.TrackKind.KIND_AUDIO \
                    and track.source == rtc.TrackSource.SOURCE_MICROPHONE:
                track.set_subscribed(True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("whisper.log"),
                        logging.StreamHandler()])

    loop = asyncio.get_event_loop()
    room = rtc.Room(loop=loop)

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
