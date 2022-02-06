from typing import Tuple
from Camera.calibration import CameraCalibration
from Common.frame_consumer import FrameConsumerThread
from Common.frame_supplier import FrameSupplier


class UndistortedFrameSupplierThread(FrameConsumerThread, FrameSupplier):
    # A frame supplier that will fetch new frames on its own thread so as to supply
    # an undistorted version of the latest frame.

    def __init__(self, frame_supplier: FrameSupplier, camera_calibration: CameraCalibration, daemon=True):
        FrameConsumerThread.__init__(self, frame_supplier, self.on_frame, daemon)
        FrameSupplier.__init__(self)
        self.camera_calibration = camera_calibration

        self._frame_size = None
        self.maps = None

    def on_frame(self, frame):
        frame_size = frame.shape[1::-1]
        if self._frame_size == None or self._frame_size != frame_size:
            self._frame_size = frame_size
            self.maps = self.camera_calibration.get_undistortion_maps(frame_size)
    
        undistorted_frame = self.camera_calibration.undistort(frame, *self.maps)
        self.set_frame(undistorted_frame)