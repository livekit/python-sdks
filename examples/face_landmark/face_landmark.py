import asyncio
import logging
import os
from signal import SIGINT, SIGTERM

import cv2
import mediapipe as mp
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

from livekit import rtc

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'  # noqa

tasks = set()

# You can download a face landmark model file from https://developers.google.com/mediapipe/solutions/vision/face_landmarker#models
model_file = 'face_landmarker.task'
model_path = os.path.dirname(os.path.realpath(__file__)) + '/' + model_file

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO)

# from https://github.com/googlesamples/mediapipe/blob/main/examples/face_landmarker/python/%5BMediaPipe_Python_Tasks%5D_Face_Landmarker.ipynb


def draw_landmarks_on_image(rgb_image, detection_result):
    face_landmarks_list = detection_result.face_landmarks

    # Loop through the detected faces to visualize.
    for face_landmarks in face_landmarks_list:

        # Draw the face landmarks.
        face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        face_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(
                x=landmark.x, y=landmark.y, z=landmark.z)
            for landmark in face_landmarks
        ])

        solutions.drawing_utils.draw_landmarks(
            image=rgb_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_tesselation_style())
        solutions.drawing_utils.draw_landmarks(
            image=rgb_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_contours_style())
        solutions.drawing_utils.draw_landmarks(
            image=rgb_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_iris_connections_style())


async def frame_loop(video_stream: rtc.VideoStream) -> None:
    landmarker = FaceLandmarker.create_from_options(options)
    argb_frame = None
    cv2.namedWindow('livekit_video', cv2.WINDOW_AUTOSIZE)
    cv2.startWindowThread()
    async for frame in video_stream:
        buffer = frame.buffer

        if argb_frame is None or argb_frame.width != buffer.width \
                or argb_frame.height != buffer.height:
            argb_frame = rtc.ArgbFrame.create(
                rtc.VideoFormatType.FORMAT_ABGR, buffer.width, buffer.height)

        buffer.to_argb(argb_frame)

        arr = np.frombuffer(argb_frame.data, dtype=np.uint8)
        arr = arr.reshape((argb_frame.height, argb_frame.width, 4))
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB, data=arr)

        detection_result = landmarker.detect_for_video(
            mp_image, frame.timestamp_us)

        draw_landmarks_on_image(arr, detection_result)

        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

        cv2.imshow('livekit_video', arr)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    landmarker.close()
    cv2.destroyAllWindows()


async def main(room: rtc.Room) -> None:
    video_stream = None

    @room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, *_):
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            nonlocal video_stream
            if video_stream is not None:
                # only process the first stream received
                return

            print("subscribed to track: " + track.name)
            video_stream = rtc.VideoStream(track)
            task = asyncio.create_task(frame_loop(video_stream))
            tasks.add(task)
            task.add_done_callback(tasks.remove)

    await room.connect(URL, TOKEN)
    print("connected to room: " + room.name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[
                        logging.FileHandler("face_landmark.log"),
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
