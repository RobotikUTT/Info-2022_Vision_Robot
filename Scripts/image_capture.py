import cv2
from Camera.frame_capture import FrameCaptureThread, RES_1600x1200, RES_2560x1920, RES_640x480
from Common.utils import find_chessboard, scale_image
from Common.web_interface import StreamConfiguration, WebInterfaceThread
import os

def begin_image_capture(preview_url, path):
    if not os.path.isdir(path): os.mkdir(path)
    print(f"capturing images to {path}")

    frame_capture = FrameCaptureThread(RES_2560x1920)
    frame_capture.start()

    web_interface = WebInterfaceThread()
    web_interface.create_video_stream(
        preview_url, StreamConfiguration(frame_capture)
    )
    print("after")
    web_interface.start()
    print(f"starting stream at '{preview_url}'")

    print("Press enter to captures frames...")
    nb_frame = 0

    while True:
        while os.path.isfile(f"{path}/img_{nb_frame}.jpg"): nb_frame += 1
        input(f"frame {nb_frame}")
        frame = frame_capture.get_frame()
        resized = scale_image(frame, 0.5)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        ret, _ = find_chessboard(gray, fast=False)
        
        if not ret:
            print("chessboard not found")
            continue

        cv2.imwrite(f"{path}/img_{nb_frame}.jpg", frame)

        nb_frame += 1