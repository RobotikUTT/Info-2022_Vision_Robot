import cv2
from aruco import ArucoTrackerThread
from Camera.calibration import CameraCalibration
from Camera.frame_capture import FrameCaptureThread, RES_2560x1920
from Camera.undistorted import UndistortedFrameSupplierThread
from web_interface import StreamConfiguration, WebInterfaceThread
import numpy as np


known_marker_position = {
    42: [(0, 0, 0), (0, 67, 0), (67, 67, 0), (67, 0, 0)],
    7 : [(762, 508, 0), (762, 575, 0), (829, 575, 0), (829, 508, 0)],
    51: [(0, 508, 0), (0, 575, 0), (67, 575, 0), (67, 508, 0)]
}

config = CameraCalibration.load_from_file("config.json")
frame_capture_thread = FrameCaptureThread(RES_2560x1920)
frame_capture_thread.start()

undistorted_frame_supplier_thread = UndistortedFrameSupplierThread(frame_capture_thread, config)
undistorted_frame_supplier_thread.start()

aruco = ArucoTrackerThread(undistorted_frame_supplier_thread)
aruco.start()

web_interface = WebInterfaceThread(daemon=True)
web_interface.create_video_stream(
    "/output", StreamConfiguration(undistorted_frame_supplier_thread)
)
web_interface.start()

invMtx = np.linalg.inv(config.K)

frame = None
while True:
    frame, codes = aruco.get_frame_and_codes(frame)
    
    objpoints = []
    imgpoints = []

    unknown = []

    for c in codes:
        if not c.id in known_marker_position:
            unknown.append(c)
            continue

        objpoints += known_marker_position[c.id]
        imgpoints += c.corners.tolist()

    if len(objpoints) < 4: continue   

    objpoints = np.array(objpoints, dtype=float)
    imgpoints = np.array(imgpoints, dtype=float)

    ret, rvec, tvec, *_ = cv2.solvePnP(objpoints, imgpoints, config.K, None)

    # print(ret, rvec, tvec)
    # print(tvec)
    rvec = rvec.squeeze()
    tvec = tvec.squeeze()

    rMat = cv2.Rodrigues(rvec)[0]
    
    camera_pos = -rMat.T.dot(np.array(tvec))

    for code in unknown:
        c = code.corners[0]
        screenPos = np.empty(3)
        screenPos[:2] = c
        screenPos[2] = 1

        pos_on_screen = np.array( rMat.T.dot( (invMtx.dot(screenPos) - tvec)) )

        
        direction = pos_on_screen - camera_pos

        s = (0 - camera_pos[2])/direction[2]

        print(camera_pos + s * direction)
        
        
    
    