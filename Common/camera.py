#!/bin/python3
import cv2


class Cam():
    # Static reference to an instance of cv2.VideoCapture()
    __cap = None

    RES_1024x768 = (1024, 768)
    RES_1024x1024 = (1280, 1024)

    def start():
        if Cam.__cap is None:
            Cam.__cap = cv2.VideoCapture(0)

    def getFrame():
        ret, frame = Cam.__cap.read()
        return frame

    def setResolution(res=RES_1024x768):
        Cam.start()
        Cam.__cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
        Cam.__cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])


# Possible resolutions
# 160.0 x 120.0
# 176.0 x 144.0
# 320.0 x 240.0
# 352.0 x 288.0
# 640.0 x 480.0
# 1024.0 x 768.0
# 1280.0 x 1024.0
