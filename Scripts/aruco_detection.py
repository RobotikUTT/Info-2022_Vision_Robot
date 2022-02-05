from Camera.calibration import CameraCalibration
from Camera.frame_capture import FrameCaptureThread
from Camera.undistorted import UndistortedFrameSupplierThread
from Common.aruco import ArucoTrackerThread
from Common.frame_consumer import FrameConsumerThread


def aruco_detection(url, calib_file):

    camera_calibration = CameraCalibration.load_from_file(calib_file)

    frame_capture = FrameCaptureThread()
    frame_capture.start()

    undistorted_supplier = UndistortedFrameSupplierThread(frame_capture, camera_calibration)
    undistorted_supplier.start()

    aruco_tracker = ArucoTrackerThread(undistorted_supplier)
    aruco_tracker.start()

    def on_aruco(frame):
        codes = aruco_tracker.get_codes()
        print(codes)

    aruco_tracker_consumer = FrameConsumerThread(aruco_tracker, on_aruco, daemon=False)
    aruco_tracker_consumer.start()