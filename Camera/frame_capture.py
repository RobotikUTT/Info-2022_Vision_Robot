from threading import Thread
import numpy as np
import cv2
from Common.frame_supplier import FrameSupplier

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
# RES_2560x1936 = (2560, 1936)


class FrameCaptureThread(Thread, FrameSupplier):
    # This class is responsible for grabbing the frames from the Pi Camera on its own thread.
    # If the thread hasn't been started, the frame will just be solid black.
    # It derives from FrameSupplier, a custom class desgined to supply a frame.

    def __init__(self, daemon=True, capture_resolution=RES_2560x1920):
        Thread.__init__(self, daemon=daemon)
        FrameSupplier.__init__(self)

        # Create a blank frame whilst waiting for the first frame to be captured
        res = capture_resolution
        self._current_frame = np.empty((res[1], res[0], 3), dtype=np.uint8)

        self.resolution_has_changed = False
        self.set_resolution(capture_resolution)

    def set_resolution(self, capture_resolution):
        self.capture_resolution = capture_resolution
        self.resolution_has_changed = True

    def get_resolution(self):
        return self.capture_resolution

    # Target of the capture thread
    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_EXPOSURE, 100)
        while True:
            if self.resolution_has_changed:
                self.resolution_has_changed = False
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.capture_resolution[1])
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.capture_resolution[0])

            ret, frame = cap.read()
            if not ret:
                print("couldn't capture frame")
                continue
            
            if not self.resolution_has_changed:
                self.set_frame(frame)
