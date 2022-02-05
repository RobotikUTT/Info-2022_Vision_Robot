from Camera.calibration import CameraCalibration
from Camera.frame_capture import FrameCaptureThread
from Common.web_interface import StreamConfiguration, WebInterfaceThread
from Camera.undistorted import UndistortedFrameSupplierThread

def corrected_preview(config_file, preview_url):
    web_interface = WebInterfaceThread()
    web_interface.start()

    frame_capture = FrameCaptureThread(daemon=False)
    frame_capture.start()

    calibration = CameraCalibration.load_from_file(config_file)

    undistorted = UndistortedFrameSupplierThread(frame_capture, calibration)
    undistorted.start()

    web_interface.create_video_stream(preview_url, StreamConfiguration(undistorted))