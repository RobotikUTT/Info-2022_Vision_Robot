import cv2
from threading import Thread

class VideoGetter:

    RES_640x480   = (640, 480)
    RES_2595x1936 = (2595, 1936)
    RES_2592x1944 = (2592, 1944)

    def __init__(self, src=0, captureResolution=None):
        if captureResolution is None: captureResolution = VideoGetter.RES_2592x1944

        self.running = False

        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, captureResolution[0])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, captureResolution[1])

        self.grabFrame()

    def grabFrame(self):
        self.grabbed, self.frame = self.stream.read()

    def start(self):
        if self.running: return

        self.running = True
        Thread(target=self.get, args=(), daemon=True).start()

    def get(self):
        while self.running:
             # If the previous frame was succesfully grabbed, grab another one
            if not self.grabbed:
                print("failed to get frame")
                self.stop()
            else: 
                self.grabFrame()
            
    def stop(self):
        self.running = False