import os
import glob
from pathlib import Path
import cv2
import detection
import streaming
import calibration

def startCalibration(camera: cv2.VideoCapture = None, imagesPath=".images", configPath="config.json", keepImages=True, boardSize=(6, 9), streamResults=True, streamPort=1234, nbImages=100):
    """
    camera: An opencv VideoCapture object (to avoid accidently creating multiple for the same camera). If None, will automaticaly create one.
    """

    # Make folder if it doesn't exist
    Path(imagesPath).mkdir(parents=True, exist_ok=True)

    if not keepImages:
        # Clear contents of the folder
        files = glob.glob(imagesPath)
        for f in files:
            os.remove(f)

    if camera == None: camera = cv2.VideoCapture(0)

    if streamResults:
        stream = streaming.VideoStreamer(streamPort)
        stream.start()

    i = 101
    while i < nbImages:
        ret, frame = camera.read()
        ret, corners = detection.findChessboard(frame, fast=True)
        
        if streamResults: 
            streamFrame = frame.copy()
            stream.checkConnections()

            streamFrame = cv2.drawChessboardCorners(streamFrame, boardSize, corners, ret)

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
            ret, frame = camera.read()
            frame = calibration.undistort(frame, calib)

            stream.checkConnections()
            stream.sendFrame(frame)


if __name__ == "__main__":
    startCalibration()
    
