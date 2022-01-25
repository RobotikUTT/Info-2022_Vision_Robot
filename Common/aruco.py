import cv2
from dataclasses import dataclass
from threading import Thread, Event
from typing import List
from camera_calibration import CameraCalibration
from frame_capture import (
    FrameCaptureThread,
    RES_1280x960,
    RES_1600x1200,
    RES_2240x1680,
    RES_2560x1920,
    RES_640x480,
)
from frame_supplier import FrameSupplier
from undistorted_frame_supplier import UndistortedFrameSupplierThread
from web_interface import StreamConfiguration, WebInterfaceThread
import time


@dataclass
class ArucoCode:
    corners: List
    id: int


class ArucoTrackerThread(FrameSupplier, Thread):
    # This threaded class detects and stores arucos codes, as well as supplies the frame for which
    # the codes were detected.
    # Why supply the frame as well ? Sometimes you will need to have the detected codes as well as
    # the frame that was used, if for example you want to overlay the data on the frame.

    def __init__(self, frame_supplier: FrameSupplier, daemon=True):
        FrameSupplier.__init__(self)
        Thread.__init__(self, daemon=daemon)
        self.frame_supplier = frame_supplier
        self.frame_codes_tuple = (None, [])

    def _get_current_frame(self):
        return self.frame_codes_tuple[0]

    def run(self):
        arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
        arucoParams = cv2.aruco.DetectorParameters_create()

        previous_frame = None
        while True:
            frame = self.frame_supplier.get_frame(previous_frame)
            previous_frame = frame

            corners, ids, rejected = cv2.aruco.detectMarkers(
                frame, arucoDict, parameters=arucoParams
            )

            codes = (
                [ArucoCode(c, id[0]) for c, id in zip(corners, ids)]
                if ids is not None
                else []
            )
            self.frame_codes_tuple = (frame, codes)
            self._set_new_frame_available()

    def get_codes(self):
        return self.frame_codes_tuple[1]

    def get_frame_and_codes(self, previous_frame=None):
        frame_codes_tuple = self.frame_codes_tuple
        current_frame = frame_codes_tuple[0]

        if previous_frame is not current_frame and current_frame is not None:
            return frame_codes_tuple

        self.new_frame_available_event.clear()
        self.new_frame_available_event.wait()

        return self.frame_codes_tuple


if __name__ == "__main__":
    config = CameraCalibration.load_from_file("config.json")
    frame_capture = FrameCaptureThread(RES_1280x960)
    frame_capture.start()

    frame_supplier_thread = UndistortedFrameSupplierThread(frame_capture, config)
    frame_supplier_thread.start()

    aruco = ArucoTrackerThread(frame_supplier_thread)
    aruco.start()

    web_interface = WebInterfaceThread(daemon=True)
    web_interface.create_video_stream(
        "/output", StreamConfiguration(frame_supplier_thread)
    )
    web_interface.start()

    frame = None
    while True:
        frame, codes = aruco.get_frame_and_codes(frame)
        print([c.id for c in codes])
        # time.sleep(0.5)


# while True:
#     ret, frame = cap.read()
#     frame = calibration.undistort(frame, calib)
#     corners, ids, rejected = cv2.aruco.detectMarkers(
#         frame, arucoDict, parameters=arucoParams
#     )

#     if not ids is None:
#         for (markerCorner, markerID) in zip(corners, ids):
#             arucoCorners = markerCorner.reshape((4, 2))
#             topLeft, topRight, bottomRight, bottomLeft = arucoCorners

#             topRight = (int(topRight[0]), int(topRight[1]))
#             bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
#             bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
#             topLeft = (int(topLeft[0]), int(topLeft[1]))

#             cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
#             cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
#             cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
#             cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

#             cv2.putText(
#                 frame,
#                 str(markerID),
#                 (topLeft[0], topLeft[1] - 15),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.5,
#                 (0, 255, 0),
#                 2,
#             )

#     stream.checkConnections()
#     stream.sendFrame(frame)

#     # sleep(1)
