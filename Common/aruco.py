import cv2
from dataclasses import dataclass
from typing import List
from Camera.calibration import CameraCalibration
from Camera.frame_capture import (
    FrameCaptureThread,
    RES_2560x1920,
)
from Common.frame_supplier import FrameSupplier
from Camera.undistorted import UndistortedFrameSupplierThread
from Common.web_interface import StreamConfiguration, WebInterfaceThread
import numpy as np
from Common.frame_consumer import FrameConsumerThread


@dataclass
class ArucoCode:
    corners: List
    id: int


class ArucoTrackerThread(FrameSupplier, FrameConsumerThread):
    # This threaded class detects and stores arucos codes, as well as supplies the frame for which
    # the codes were detected.
    # Why supply the frame as well ? Sometimes you will need to have the detected codes as well as
    # the frame that was used, if for example you want to overlay the data on the frame.

    def __init__(self, frame_supplier: FrameSupplier, daemon=True):
        FrameConsumerThread.__init__(self, frame_supplier, self.on_frame, daemon=daemon)
        FrameSupplier.__init__(self)

        self.frame_codes_tuple = (None, [])
        self._aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
        self._aruco_params = cv2.aruco.DetectorParameters_create()

    def on_frame(self, frame):
        aruco_dict = self._aruco_dict
        aruco_params = self._aruco_params

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        all_corners, ids, _ = cv2.aruco.detectMarkers(
            gray, aruco_dict, parameters=aruco_params
        )
        
        codes = []
        if ids is not None: 
            all_corners = np.array(all_corners).squeeze(1)
            codes = [ArucoCode(corners, id[0]) for corners, id in zip(all_corners, ids)]

        self.frame_codes_tuple = (frame, codes)
        self.set_new_frame_available()

    def get_frame(self):
        return self.frame_codes_tuple[0]

    def get_codes(self):
        return self.frame_codes_tuple[1]

    def get_frame_and_codes(self):
        return self.frame_codes_tuple


if __name__ == "__main__":
    config = CameraCalibration.load_from_file("config.json")
    frame_capture_thread = FrameCaptureThread(RES_2560x1920)
    frame_capture_thread.start()

    undistorted_frame_supplier_thread = UndistortedFrameSupplierThread(frame_capture_thread, config)
    undistorted_frame_supplier_thread.start()

    aruco = ArucoTrackerThread(undistorted_frame_supplier_thread)
    aruco.start()

    output_frame_supplier = FrameSupplier()

    web_interface = WebInterfaceThread(daemon=True)
    web_interface.create_video_stream(
        "/output", StreamConfiguration(output_frame_supplier)
    )
    web_interface.start()


    frame = None
    while True:
        frame, codes = aruco.get_frame_and_codes(frame)
        
        if len(codes) == 0:
            output_frame_supplier.set_current_frame(frame)
            continue

        draw_frame = frame.copy()
        for c in codes:
            print(c.corners)
            topLeft, topRight, bottomRight, bottomLeft = c.corners
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))

            # cv2.line(draw_frame, topLeft, topRight, (0, 255, 0), 2)
            # cv2.line(draw_frame, topRight, bottomRight, (0, 255, 0), 2)
            # cv2.line(draw_frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            # cv2.line(draw_frame, bottomLeft, topLeft, (0, 255, 0), 2)
            print(c.id)
            cv2.putText(draw_frame, "1", topLeft, cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
            cv2.putText(draw_frame, "2", topRight, cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
            cv2.putText(draw_frame, "3", bottomRight, cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
            cv2.putText(draw_frame, "4", bottomLeft, cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)

        output_frame_supplier.set_current_frame(draw_frame)



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
