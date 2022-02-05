from Camera.frame_capture import FrameCaptureThread
from Common.web_interface import StreamConfiguration, WebInterfaceThread

capture = FrameCaptureThread()
capture.start()

web_interface = WebInterfaceThread(daemon=False)
web_interface.start()
web_interface.create_video_stream("/output", StreamConfiguration(capture))