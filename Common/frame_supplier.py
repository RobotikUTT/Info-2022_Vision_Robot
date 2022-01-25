import threading


class FrameSupplier:
    # The purpose of this class is to hold a reference to a frame, and allow access to said frame.
    # To optimize threaded access and to avoid threads doing work twice on the same frame
    # (if say another thread can process frames faster that they can be supplied),
    # a "locking" system is used when requesting the current frame.
    # If the frame is the same as the previous one,
    # execution will be blocked using an instance of theading.Thread.event.

    def __init__(self):
        # This "threading.Event" object is used to comunicate
        # with others threads waiting for a new frame.
        self.new_frame_available_event = threading.Event()
        self._current_frame = None

    def _get_current_frame(self):
        return self._current_frame

    def set_current_frame(self, frame):
        self._current_frame = frame
        self._set_new_frame_available()

    # This method returns the current frame.
    # It can take the previous frame
    def get_frame(self, previous_frame=None):
        # Grab a reference to the current incase it gets updated after the comparison
        current_frame = self._get_current_frame()

        # If the previous frame isn't the same as the current one, return the current frame
        # (using "is" to compare identity)
        if previous_frame is not current_frame and current_frame is not None:
            return current_frame

        # Clear the new frame available event.
        # A thread already has the current frame and is asking for a new one,
        # which means the currentFrame is out of date.
        self.new_frame_available_event.clear()

        # Wait until a new frame becomes available.
        # This will be done in the capture thread after a frame has been read.
        self.new_frame_available_event.wait()

        new_frame = self._get_current_frame()
        return new_frame

    def _set_new_frame_available(self):
        self.new_frame_available_event.set()
