from threading import Thread
from typing import Tuple
import numpy as np
import cv2
from Camera.frames import FrameSupplier
from Common.types import Frame
from typing import cast

# Weird resolutions:
# https://raspberrypi.stackexchange.com/questions/107161/picamera-exe-picameraioerror-failed-to-write-291840-bytes-from-buffer-to-output

# Some Posibles resolutions
RES_640x480 = (640, 480)
RES_1280x960 = (1280, 960)
RES_1600x1200 = (1600, 1200)
RES_2240x1680 = (2240, 1680)
RES_1296x736 = (1296, 736)
RES_1296x976 = (1296, 976)
RES_2592x1936 = (2592, 1936)
RES_2560x1920 = (2560, 1920)


class FrameCaptureThread(Thread, FrameSupplier):
    def __init__(self, daemon: bool = True, capture_resolution: Tuple[int, int]=RES_2560x1920) -> None:
        Thread.__init__(self, daemon=daemon)
        FrameSupplier.__init__(self)

        res = capture_resolution

        # Create a blank frame whilst waiting for the first frame to be captured
        self._frame = cast(Frame, np.empty((res[1], res[0], 3), dtype=np.uint8)) # type: Frame

    def set_frame(self, frame: Frame) -> None:
        self._frame = frame
        self.notify()

    def get_frame(self) -> Frame:
        return self._frame

    # Target of the capture thread
    def run(self) -> None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_EXPOSURE, 100)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("couldn't capture frame")
                continue
            
            self.set_frame(frame)
