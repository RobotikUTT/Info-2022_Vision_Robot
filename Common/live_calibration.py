#!/bin/python3
import os
import glob
from pathlib import Path
import cv2
import detection
import streaming
import calibration
from camera import Cam


def startCalibration(imagesPath=".images", configPath="config.json", boardSize=(6, 9), streamResults=True, streamPort=1234, nbImages=100, resolution=Cam.RES_1024x1024):
    """
    camera: An opencv VideoCapture object (to avoid accidently creating multiple for the same camera). If None, will automaticaly create one.
    """

    # Make folder if it doesn't exist
    Path(imagesPath).mkdir(parents=True, exist_ok=True)

    # Clear contents of the folder
    files = glob.glob(f"{imagesPath}/*")
    for f in files:
        print(f)
        os.remove(f)

    if streamResults:
        stream = streaming.VideoStreamer(streamPort, quality=10)
        stream.start()

    Cam.setResolution(resolution)

    i = 0
    while i < nbImages:
        frame = Cam.getFrame()
        ret, corners = detection.findChessboard(frame, fast=True)

        if streamResults:
            streamFrame = frame.copy()
            stream.checkConnections()

            streamFrame = cv2.drawChessboardCorners(
                streamFrame, boardSize, corners, ret)

            stream.sendFrame(streamFrame)

        if ret:
            cv2.imwrite(f"{imagesPath}/{i}.jpg", frame)
            i += 1

    print("calibrating...")
    calib = calibration.getCameraCalibration(imagesPath)
    print("done calibrating !")

    calib.save(configPath)

    if streamResults:
        while True:
            frame = Cam.getFrame()
            frame = calibration.undistort(frame, calib)

            stream.checkConnections()
            stream.sendFrame(frame)


if __name__ == "__main__":
    startCalibration()
