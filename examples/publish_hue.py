import asyncio
import colorsys
import logging
from pathlib import Path
from signal import SIGINT, SIGTERM

import numpy as np
import os
import sys

# Get the parent directory for debug only
parent_dir = os.path.dirname(os.path.realpath(__file__))
import_dir = os.path.normpath(os.path.join(parent_dir, os.pardir)) 
# Add the parent directory to sys.path
sys.path.append(import_dir)


import livekit

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTUxNzA2OTEsImlzcyI6IkFQSXJramtRYVZRSjVERSIsIm5hbWUiOiJweWUyZWUiLCJuYmYiOjE2OTMzNzA2OTEsInN1YiI6InB5ZTJlZSIsInZpZGVvIjp7InJvb20iOiJsaXZlIiwicm9vbUpvaW4iOnRydWV9fQ.CZnT4fOBjUTxrTlkijxb_D_4HAbZoxljNRjDlCRHNBY'  # noqa


async def publish_frames(source: livekit.VideoSource):
    argb_frame = livekit.ArgbFrame(
        livekit.VideoFormatType.FORMAT_ARGB, 1280, 720)

    arr = np.ctypeslib.as_array(argb_frame.data)

    framerate = 1 / 30
    hue = 0.0

    while True:
        frame = livekit.VideoFrame(
            0, livekit.VideoRotation.VIDEO_ROTATION_0, argb_frame.to_i420())

        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        rgb = [(x * 255) for x in rgb] # type: ignore

        argb_color = np.array(rgb + [255], dtype=np.uint8)
        arr.flat[::4] = argb_color[0]
        arr.flat[1::4] = argb_color[1]
        arr.flat[2::4] = argb_color[2]
        arr.flat[3::4] = argb_color[3]

        source.capture_frame(frame)

        hue += framerate/3  # 3s for a full cycle
        if hue >= 1.0:
            hue = 0.0

        try:
            await asyncio.sleep(framerate)
        except asyncio.CancelledError:
            break


def do_e2ee_test(room: livekit.Room):
        room.e2ee_manager.key_provider.set_shared_key(b"87654321", 1)
        key0 = room.e2ee_manager.key_provider.export_key("shared", 0)

        if key0 != b"12345678":
            logging.info("key0 is not 12345678")
        
        key1 = room.e2ee_manager.key_provider.export_key("shared", 1)

        if key1 != b"87654321":
            logging.info("key1 is not 87654321")

        room.e2ee_manager.key_provider.set_shared_key(b"88888888", 3)
        key3 = room.e2ee_manager.key_provider.export_key("shared", 3)
        room.e2ee_manager.key_provider.rachet_key("shared", 3)
        key4 = room.e2ee_manager.key_provider.export_key("shared", 3)

        room.e2ee_manager.key_provider.set_key("participant1", b"11111111", 0)
        key5 = room.e2ee_manager.key_provider.export_key("participant1", 0)

        room.e2ee_manager.key_provider.set_key("shared", b"22222222", 0)
        key6 = room.e2ee_manager.key_provider.export_key("shared", 0)


        room.e2ee_manager.key_provider.set_key("shared", b"12345678", 0)

async def main():
    room = livekit.Room()

    logging.info("connecting to %s", URL)
    try:
        await room.connect(URL, TOKEN, options= livekit.RoomOptions(
            auto_subscribe= True,
            dynacast= True,
            e2ee_options= livekit.e2ee.E2EEOptions(
                encryption_type= livekit.e2ee.EncryptionType.GCM,
                key_provider_options= livekit.e2ee.KeyProviderOptions()
            ),
        ))
        room.e2ee_manager.key_provider.set_shared_key(b"12345678", 0)
        
        #do_e2ee_test(room)

        logging.info("connected to room %s", room.name)
    except livekit.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
        return False

    @room.listens_to("e2ee_state_changed")
    def on_e2ee_state_changed(participant: livekit.Participant, publication: livekit.TrackPublication, participant_id: str, state: any) -> None:
        logging.info(
            "e2ee state changed for %s %s, track %s, state: %s, e2ee participant_id %s", participant.sid, participant.identity, publication.sid, state, participant_id)
    

    # publish a track
    source = livekit.VideoSource()
    source_task = asyncio.create_task(publish_frames(source))

    track = livekit.LocalVideoTrack.create_video_track("hue", source)
    options = livekit.TrackPublishOptions()
    options.source = livekit.TrackSource.SOURCE_CAMERA
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
                        logging.FileHandler("publish_hue.log"), logging.StreamHandler()])

    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main())
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
