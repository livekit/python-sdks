import asyncio
import os
from queue import Queue

import cv2
import mediapipe as mp
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

import livekit

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MDY2MTMyODgsImlzcyI6IkFQSVRzRWZpZFpqclFvWSIsIm5hbWUiOiJuYXRpdmUiLCJuYmYiOjE2NzI2MTMyODgsInN1YiI6Im5hdGl2ZSIsInZpZGVvIjp7InJvb20iOiJ0ZXN0Iiwicm9vbUFkbWluIjp0cnVlLCJyb29tQ3JlYXRlIjp0cnVlLCJyb29tSm9pbiI6dHJ1ZSwicm9vbUxpc3QiOnRydWV9fQ.uSNIangMRu8jZD5mnRYoCHjcsQWCrJXgHCs0aNIgBFY'

frame_queue = Queue()
argb_frame = None

# You can downlo9ad a face landmark model file from https://developers.google.com/mediapipe/solutions/vision/face_landmarker#models
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
    for idx in range(len(face_landmarks_list)):
        face_landmarks = face_landmarks_list[idx]

        # Draw the face landmarks.
        face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        face_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
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


async def room() -> None:
    room = livekit.Room()
    await room.connect(URL, TOKEN)
    print("connected to room: " + room.name)

    video_stream = None

    @room.on("track_subscribed")
    def on_track_subscribed(track: livekit.Track, publication: livekit.RemoteTrackPublication, participant: livekit.RemoteParticipant):
        if track.kind == livekit.TrackKind.KIND_VIDEO:
            nonlocal video_stream
            video_stream = livekit.VideoStream(track)

            @video_stream.on("frame_received")
            def on_video_frame(frame: livekit.VideoFrame):
                frame_queue.put(frame)

    await room.run()


def display_frames() -> None:
    cv2.namedWindow('livekit_video', cv2.WINDOW_AUTOSIZE)
    cv2.startWindowThread()

    global argb_frame

    with FaceLandmarker.create_from_options(options) as landmarker:
        while True:
            frame = frame_queue.get()
            buffer = frame.buffer

            if argb_frame is None or argb_frame.width != buffer.width or argb_frame.height != buffer.height:
                argb_frame = livekit.ArgbFrame(
                    livekit.VideoFormatType.FORMAT_ABGR, buffer.width, buffer.height)

            buffer.to_argb(argb_frame)

            arr = np.ctypeslib.as_array(argb_frame.data)
            arr = arr.reshape((argb_frame.height, argb_frame.width, 4))
            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB, data=arr)

            detection_result = landmarker.detect_for_video(
                mp_image, frame.timestamp)

            draw_landmarks_on_image(arr, detection_result)

            arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

            cv2.imshow('livekit_video', arr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()


async def main() -> None:
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, asyncio.run, room())

    display_frames()
    await future

if __name__ == "__main__":
    asyncio.run(main())
