class FrameSupplier:
    # The purpose of this class is to hold a reference to a frame, and allow access to said frame.

    def __init__(self):
        self._current_frame = None
        self._callbacks = []

    def subscribe(self, callback):
        if not callable(callback):
            raise TypeError("Callback must be a function with no arguments.")

        self._callbacks.append(callback)

    def unsubscribe(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def get_frame(self):
        return self._current_frame

    def set_new_frame_available(self):
        for callback in self._callbacks:
            callback()

    def set_frame(self, frame):
        self._current_frame = frame
        self.set_new_frame_available()
        
