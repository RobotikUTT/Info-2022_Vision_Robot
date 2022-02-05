import numpy as np
import calibration
import detection
import cv2
import streaming
from time import sleep

def getCameraRay(invMtx, rvec, tvec, screenPos):

    rvec = np.array(rvec).reshape(3)
    tvec = np.array(tvec).reshape(3)

    screenPos = np.append(np.array(screenPos)[:2], 1)

    rMat = cv2.Rodrigues(rvec)[0]

    cameraPosition = -rMat.T.dot(np.array(tvec)).reshape(3)
    posOnScreen = np.array( rMat.T.dot( (invMtx.dot(screenPos) - tvec)) )

    # print(cameraPosition)
    # print( invMtx.dot(screenPos))

    # s = (0 - cameraPosition.item(2)) / (posOnScreen.item(2) - cameraPosition.item(2))

    return cameraPosition, posOnScreen - cameraPosition

def getWorldPosition(ray, z = 0):
    rayOrigin = ray[0].reshape(3)
    direction = ray[1].reshape(3)

    s = (z-rayOrigin[2])/direction[2]
    
    return rayOrigin + s * direction


if __name__ == "__main__":

    stream = streaming.VideoStreamer(1234)
    stream.start()

    calib = calibration.CameraCalibration.load("config.json")
    invMtx = np.linalg.inv(calib.mtx)

    cap = cv2.VideoCapture(0)
    ret, referenceFrame = cap.read()
    referenceFrame = calibration.undistort(referenceFrame, calib)

    bx, by = (6, 9)
    squareSize = 1
    objp = np.zeros((by*bx,3), np.float32)
    objp[:,:2] = np.mgrid[0:bx,0:by].T.reshape(-1,2) * squareSize

    ret, corners = detection.findChessboard(referenceFrame, convertToGray=True, fast=False)
    
    stream.checkConnections()
    stream.sendFrame(referenceFrame)

    ret, rvec, tvec, *_ = cv2.solvePnP(objp, corners, calib.mtx, None)

    screenPos = [269, 247]

    ray = getCameraRay(invMtx, rvec, tvec, screenPos)
    pos = getWorldPosition(ray)
    print(pos)

    referenceFrame = cv2.circle(referenceFrame, screenPos, 10, (255, 0, 0))

    while True:
        stream.checkConnections()
        stream.sendFrame(referenceFrame)
        sleep(0.5)

    # while True:
        # ret, frame = cap.read()
        # frame = calibration.undistort(frame, calib)

        # ray = getCameraRay(invMtx, rvec, tvec, [228, 176])

        # pos = getWorldPosition(ray, 0)
        # print(pos)