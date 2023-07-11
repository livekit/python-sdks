import sys
import livekit
import logging
import asyncio
from signal import SIGINT, SIGTERM

from livekit import ArgbFrame
from livekit._proto.video_frame_pb2 import FORMAT_BGRA, FORMAT_ABGR, FORMAT_ARGB, FORMAT_RGBA

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'

import cv2
import numpy as np

import time

async def main():
    room = livekit.Room()

    audio_stream = None
    video_stream = None

    @room.on("participant_connected")
    def on_participant_connected(participant: livekit.RemoteParticipant):
        logging.info(
            "SNAP: participant connected: %s %s", participant.sid, participant.identity)

    @room.on("participant_disconnected")
    def on_participant_disconnected(participant: livekit.RemoteParticipant):
        logging.info("SNAP: participant disconnected: %s %s",
                     participant.sid, participant.identity)

    @room.on("track_published")
    def on_track_published(publication: livekit.LocalTrackPublication, participant: livekit.RemoteParticipant):
        logging.info("SNAP: track published: %s from participant %s (%s)",
                     publication.sid, participant.sid, participant.identity)

    @room.on("track_unpublished")
    def on_track_unpublished(publication: livekit.LocalTrackPublication, participant: livekit.RemoteParticipant):
        logging.info("SNAP: track unpublished: %s", publication.sid)

    @room.on("track_subscribed")
    def on_track_subscribed(track: livekit.Track, publication: livekit.RemoteTrackPublication, participant: livekit.RemoteParticipant):
        logging.info("SNAP: track subscribed: %s %s", publication.sid, track.kind)
        start_time = time.time()
        if track.kind == livekit.TrackKind.KIND_VIDEO:
            logging.debug(f"SNAP: on_track_subscribed setting track event on {track.sid} {track.name}")
            nonlocal video_stream
            video_stream = livekit.VideoStream(track)

            frame_num = 0

            @video_stream.on("frame_received")
            def on_video_frame(frame: livekit.VideoFrame):
                nonlocal frame_num
                nonlocal start_time
                # get a snapshot every 2 seconds
                if time.time() - start_time < 2:
                    return
                start_time = time.time()
                logging.debug(f"SNAP: on_video_frame received video frame on {track.sid} {frame.buffer}")

                size = frame.buffer.width * frame.buffer.height
                yuv = frame.buffer.to_i420()
                logging.debug(f"SNAP: on_video_frame INFO: chroma:{yuv.chroma_width}x{yuv.chroma_height} size: {size}/{yuv.width*yuv.height} ({yuv.width}x{yuv.height}) strides: {yuv.stride_y}/{yuv.stride_u}/{yuv.stride_v}")

                argb_frame = ArgbFrame(format=FORMAT_ARGB, width=frame.buffer.width, height=frame.buffer.height)
                frame.buffer.to_argb(argb_frame)
                logging.debug(f"SNAP: on_video_frame argb_frame: {argb_frame.width}x{argb_frame.height} data: {argb_frame.data}")

                image = np.array(argb_frame.data, dtype=np.uint8).reshape((argb_frame.height, argb_frame.width, 4))
                # write image to file
                #cv2.imwrite(f"{track.sid}-{frame_num:04d}.jpg", image)
                cv2.imwrite(f"{track.sid}.png", image)
                frame_num += 1
                # display image
                #cv2.imshow(track.sid, image)
        elif track.kind == livekit.TrackKind.KIND_AUDIO:
            logging.debug("SNAP: Subscribed to an Audio Track")
            nonlocal audio_stream
            audio_stream = livekit.AudioStream(track)

            @audio_stream.on('frame_received')
            def on_audio_frame(frame: livekit.AudioFrame):
                # received an audio frame from the track
                pass


    @room.on("track_unsubscribed")
    def on_track_unsubscribed(track: livekit.Track, publication: livekit.RemoteTrackPublication, participant: livekit.RemoteParticipant):
        logging.info("SNAP: track unsubscribed: %s", publication.sid)

    @room.on("data_received")
    def on_data_received(data: bytes, kind: livekit.DataPacketKind, participant: livekit.Participant):
        logging.info("SNAP: received data from %s: %s", participant.identity, data)

    try:
        logging.info("SNAP: connecting to %s", URL)
        await room.connect(URL, TOKEN)
        logging.info("SNAP: connected to room %s", room.name)

        await room.local_participant.publish_data("hello world")

        await room.run()
    except livekit.ConnectError as e:
        logging.error("SNAP: failed to connect to the room: %s", e)
    except asyncio.CancelledError:
        logging.info("SNAP: closing the room")
        await room.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("basic_room.log"), logging.StreamHandler()])

    #if '--help' in sys.argv:
    #    print(f"Usage: python3 {sys.argv[0]} --token <token>")
    #    print(f"Usage: python3 {sys.argv[0]} --key <key> --secret <secret> --room <room> --identity <identity>")
    #    sys.exit(0)

    # get token parameters from command line
    if len(sys.argv) > 1:
        import optparse
        parser = optparse.OptionParser()
        parser.add_option('--url', dest='url', help='url      (default: ws://localhost:7880)', default='ws://localhost:7880')
        parser.add_option('--token', dest='token', help='token    (no default)', default=None)
        parser.add_option('--key', dest='key', help='key      (default: devkey)', default="devkey")
        parser.add_option('--secret', dest='secret', help='secret   (default: secret)', default="secret")
        parser.add_option('--room', dest='room', help='room     (no default)')
        parser.add_option('--identity', dest='identity', help='identity (default: basic_snapshot)', default="basic_snapshot")
        (options, args) = parser.parse_args()
        if options.token:
            TOKEN = options.token
        else:
            TOKEN = livekit.create_access_token(options.key, options.secret, options.room, options.identity)
    URL = options.url
    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main(URL, TOKEN))
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()

