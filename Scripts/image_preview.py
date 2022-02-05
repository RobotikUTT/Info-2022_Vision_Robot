from Camera.frame_capture import FrameCaptureThread
from Common.web_interface import StreamConfiguration, WebInterfaceThread

def image_preview(url):
    capture = FrameCaptureThread()
    capture.start()

    web_interface = WebInterfaceThread(daemon=False)
    web_interface.create_video_stream(url, StreamConfiguration(capture))
    web_interface.start()