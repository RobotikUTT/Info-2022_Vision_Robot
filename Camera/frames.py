from abc import ABC, abstractmethod
from threading import Thread, Event
from Camera.calibration import CameraCalibration
from Common.observer import Observer, Subject
from Common.types import Frame

from typing import Tuple

class FrameSupplier(Subject, ABC):

    def __init__(self) -> None:
        Subject.__init__(self)

    @abstractmethod
    def get_frame(self) -> Frame:
        pass
    
    @abstractmethod
    def set_frame(self, frame: Frame):
        pass

class FrameObserverThreaded(Thread, Observer, ABC):
    def __init__(self, frame_supplier: FrameSupplier, daemon: bool = True) -> None:
        super().__init__(daemon=daemon)

        self._new_frame_available_event = Event()

        self.frame_supplier = frame_supplier
        frame_supplier.attach(self)

    def update(self, _):
        self._new_frame_available_event.set()

    def run(self) -> None:
        while True:
            self._new_frame_available_event.wait()
            self._new_frame_available_event.clear()
            self.on_frame(self.frame_supplier.get_frame())

    @abstractmethod
    def on_frame(self, frame: Frame) -> None:
        pass

class UndistortFrameThread(FrameObserverThreaded, FrameSupplier):
    """This class derives from FrameSupplier so as to give an undistorted frame
    """    

    def __init__(self, frame_supplier: FrameSupplier, camera_calibration: CameraCalibration, daemon=True):
        """[summary]

        Args:
            frame_supplier (FrameSupplier): A FrameSupplier which gives 'distorted' frames.
            camera_calibration (CameraCalibration): The CameraCalibration for the given camera.
            daemon (bool, optional): Whether this thread should run as a daemon. Defaults to True.
        """        
        Thread.__init__(self, daemon=daemon)
        FrameObserverThreaded.__init__(self, frame_supplier)

        self._camera_calibration = camera_calibration

        self._frame_size = None
        self._maps = () # type: Tuple

    def on_frame(self, frame):
        if self._maps == ():
            frame_size = frame.shape[1::-1]
            self._maps = self._camera_calibration.get_undistortion_maps(frame_size)
            
        undistorted_frame = self._camera_calibration.undistort(frame, self._maps[0], self._maps[1])
        self.set_frame(undistorted_frame)