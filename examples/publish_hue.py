import asyncio
import colorsys
import logging
from signal import SIGINT, SIGTERM

import numpy as np
from livekit import rtc

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'  # noqa


async def draw_color_cycle(source: rtc.VideoSource):
    argb_frame = rtc.ArgbFrame.create(
        rtc.VideoFormatType.FORMAT_ARGB, 1280, 720)
    arr = np.frombuffer(argb_frame.data, dtype=np.uint8)

    framerate = 1 / 30
    hue = 0.0

    while True:
        start_time = asyncio.get_event_loop().time()

        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        rgb = [(x * 255) for x in rgb]  # type: ignore

        argb_color = np.array(rgb + [255], dtype=np.uint8)
        arr.flat[::4] = argb_color[0]
        arr.flat[1::4] = argb_color[1]
        arr.flat[2::4] = argb_color[2]
        arr.flat[3::4] = argb_color[3]

        frame = rtc.VideoFrame(
            0, rtc.VideoRotation.VIDEO_ROTATION_0, argb_frame.to_i420())

        source.capture_frame(frame)
        hue = (hue + framerate / 3) % 1.0

        code_duration = asyncio.get_event_loop().time() - start_time
        await asyncio.sleep(1 / 30 - code_duration)


async def main(room: rtc.Room):
    logging.info("connecting to %s", URL)
    try:
        await room.connect(URL, TOKEN)
        logging.info("connected to room %s", room.name)
    except rtc.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
        return

    # publish a track
    source = rtc.VideoSource()
    track = rtc.LocalVideoTrack.create_video_track("hue", source)
    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_CAMERA
    publication = await room.local_participant.publish_track(track, options)
    logging.info("published track %s", publication.sid)

    asyncio.ensure_future(draw_color_cycle(source))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("publish_hue.log"),
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
