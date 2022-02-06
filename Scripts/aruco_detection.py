from Common.aruco import ArucoTrackerThread
from Common.frame_consumer import FrameConsumerThread
from Common.utils import camera_setup


def aruco_detection(url, calib_file):

    _, undistorted_supplier = camera_setup(calib_file)

    aruco_tracker = ArucoTrackerThread(undistorted_supplier)
    aruco_tracker.start()

    def on_aruco(frame):
        codes = aruco_tracker.get_codes()
        print(codes)

    aruco_tracker_consumer = FrameConsumerThread(aruco_tracker, on_aruco, daemon=False)
    aruco_tracker_consumer.start()