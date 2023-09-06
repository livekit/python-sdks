import asyncio
import os
from queue import Queue
import signal
import threading

import cv2
import mediapipe as mp
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

URL = 'ws://localhost:7880'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjM1MTAzOTAsImlzcyI6IkFQSU1teGlMOHJxdUt6dFpFb1pKVjlGYiIsIm5hbWUiOiJ0aGlyZCIsIm5iZiI6MTY4NzUxMDM5MCwic3ViIjoidGhpcmQiLCJ2aWRlbyI6eyJyb29tIjoiZGF2aWRzLXJvb20iLCJyb29tSm9pbiI6dHJ1ZX19.QHw8R5rZVhJx9pWwnnriTc0hp_IvRuVQQWPaCeXt96Y'

frame_queue = Queue()
argb_frame = None

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


def draw_landmarks_on_image(rgb_image, detection_result):
    # from https://github.com/googlesamples/mediapipe/blob/main/examples/face_landmarker/python/%5BMediaPipe_Python_Tasks%5D_Face_Landmarker.ipynb
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


should_run = True
room = None  # type: livekit.Room


async def handle_room() -> None:
    # livekit must be imported in the same thread as the event loop
    import livekit
    global room
    room = livekit.Room()
    subscribed_track_id = None
    print("connecting to room")
    await room.connect(URL, TOKEN, livekit.RoomOptions(
        # Unncomment below to enable E2EE
        # e2ee=livekit.E2EEOptions(
        #     key_provider_options=livekit.KeyProviderOptions(
        #         shared_key=b"livekitrocks"
        #     )
        # ),
        auto_subscribe=False,
    ))
    print("connected to room: " + room.name)

    video_stream = None

    @room.on("track_published")
    def on_track_published(publication: livekit.RemoteTrackPublication,
                           participant: livekit.RemoteParticipant):
        nonlocal subscribed_track_id
        if publication.kind == livekit.TrackKind.KIND_VIDEO and (
            subscribed_track_id is None or subscribed_track_id == publication.sid
        ):
            publication.set_subscribed(True)
            subscribed_track_id = publication.sid

    @room.on("track_subscribed")
    def on_track_subscribed(track: livekit.Track,
                            publication: livekit.RemoteTrackPublication,
                            participant: livekit.RemoteParticipant):
        print("track subscribed: " + publication.sid)
        if track.kind == livekit.TrackKind.KIND_VIDEO:
            nonlocal video_stream
            video_stream = livekit.VideoStream(track)

            @video_stream.on("frame_received")
            def on_video_frame(frame: livekit.VideoFrame):
                frame_queue.put(frame)

    @room.on("track_unsubscribed")
    def on_track_unsubscribed(publication: livekit.RemoteTrackPublication,
                              participant: livekit.RemoteParticipant):
        print("track unsubscribed: " + publication.sid)
        nonlocal subscribed_track_id
        if publication.sid == subscribed_track_id:
            subscribed_track_id = None

    @room.on("disconnected")
    def on_disconnected():
        print("disconnected from room")
        global should_run
        should_run = False
        loop.stop()


def display_frames() -> None:
    cv2.namedWindow('livekit_video', cv2.WINDOW_AUTOSIZE)
    cv2.startWindowThread()

    global argb_frame, should_run
    import livekit

    with FaceLandmarker.create_from_options(options) as landmarker:
        while should_run:
            try:
                frame = frame_queue.get(False, 0.1)
            except:
                continue
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
                mp_image, frame.timestamp_us)

            draw_landmarks_on_image(arr, detection_result)

            arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

            cv2.imshow('livekit_video', arr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    should_run = False


loop = asyncio.new_event_loop()


def run_loop() -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


def main() -> None:
    room_thread = threading.Thread(target=run_loop)
    room_thread.start()

    future = asyncio.run_coroutine_threadsafe(handle_room(), loop)

    def on_stop(sig=None, frame=None):
        global should_run
        should_run = False
        future.cancel()
        if room is not None:
            asyncio.run_coroutine_threadsafe(room.disconnect(), loop)

    signal.signal(signal.SIGINT, on_stop)
    signal.signal(signal.SIGTERM, on_stop)

    display_frames()
    on_stop()
    loop.stop()


if __name__ == "__main__":
    main()
