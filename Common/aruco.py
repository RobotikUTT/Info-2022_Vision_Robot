#!/bin/python3

# import the necessary packages
import argparse
import imutils
import cv2
import sys
import calibration
import streaming
from time import sleep

stream = streaming.VideoStreamer(1234)

stream.start()


cap = cv2.VideoCapture(0)


arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
arucoParams = cv2.aruco.DetectorParameters_create()

calib = calibration.CameraCalibration.load("config.json")

while True:
    ret, frame = cap.read()
    frame = calibration.undistort(frame, calib)
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)

    if not ids is None:
        for (markerCorner, markerID) in zip(corners, ids):
            arucoCorners = markerCorner.reshape((4, 2))
            topLeft, topRight, bottomRight, bottomLeft = arucoCorners

            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

            cv2.putText(frame, str(markerID), (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (0, 255, 0), 2)

    stream.checkConnections()
    stream.sendFrame(frame)

    # sleep(1)

