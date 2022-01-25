from threading import Thread
import time
from frame_capture import FrameCaptureThread, RES_640x480
from web_interface import StreamConfiguration, WebInterfaceThread
from camera_calibration import CameraCalibration
from frame_supplier import FrameSupplier


class UndistortedFrameSupplierThread(FrameSupplier, Thread):
    # A frame supplier that will fetch new frames on its own thread so as to supply
    # an undistorted version of the latest frame.

    def __init__(
        self,
        distorted_frame_supplier: FrameSupplier,
        camera_calibration: CameraCalibration,
        daemon=True,
    ):
        FrameSupplier.__init__(self)
        Thread.__init__(self, daemon=daemon)
        self.frame_supplier = distorted_frame_supplier
        self.camera_calibration = camera_calibration

    def run(self):
        previous_frame = self.frame_supplier.get_frame()
        map1, map2 = self.camera_calibration.get_undistortion_maps(
            previous_frame.shape[1::-1]
        )
        while True:
            frame = self.frame_supplier.get_frame(previous_frame)
            previous_frame = frame
            undistorted = self.camera_calibration.undistort(frame, map1, map2)

            self.set_current_frame(undistorted)


if __name__ == "__main__":
    config = CameraCalibration.load_from_file("config.json")
    frame_capture = FrameCaptureThread(RES_640x480)
    frame_capture.start()

    frame_supplier_thread = UndistortedFrameSupplierThread(frame_capture, config)
    frame_supplier_thread.start()

    web_interface = WebInterfaceThread(daemon=False)
    web_interface.create_video_stream(
        "/output", StreamConfiguration(frame_supplier_thread)
    )
    web_interface.start()

    while True:
        time.sleep(1)
