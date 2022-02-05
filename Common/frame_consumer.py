from threading import Thread, Event
from typing import Callable
import numpy

from Common.frame_supplier import FrameSupplier

class FrameConsumerThread(Thread):
    
    def __init__(self, frame_supplier: FrameSupplier, on_frame: Callable[[numpy.array], None], daemon=True):
        Thread.__init__(self, daemon=daemon)
        self._frame_event = Event()
        self._frame_event.clear()

        self.frame_supplier = frame_supplier
        frame_supplier.subscribe(lambda: self._frame_event.set())

        self.on_frame = on_frame

    def run(self):
        while True:
            self._frame_event.wait()
            self._frame_event.clear()
            frame = self.frame_supplier.get_frame()
            self.on_frame(frame)