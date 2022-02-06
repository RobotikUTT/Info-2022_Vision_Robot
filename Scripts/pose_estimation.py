from Camera.calibration import CameraCalibration
from Common.aruco import ArucoTrackerThread
from Common.frame_consumer import FrameConsumerThread
from Common.pose_estimation import PoseEstimation
from Common.utils import camera_setup

def pose_estimation(preview_url, calib_file, known_codes_file):
    _, undistorted_supplier = camera_setup(calib_file)

    aruco_tracker = ArucoTrackerThread(undistorted_supplier)
    aruco_tracker.start()

    def on_aruco(frame):
        codes = aruco_tracker.get_codes()
        print(codes)

    aruco_tracker_consumer = FrameConsumerThread(aruco_tracker, on_aruco, daemon=False)
    aruco_tracker_consumer.start()

    calib = CameraCalibration.load_from_file(calib_file)
    
    p_estim = PoseEstimation(calib)
    p_estim.solve_new_position()
    