import cv2
import numpy as np


def findChessboard(frame, boardSize=(6, 9), convertToGray=False, fast=False):
    if convertToGray:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if fast:
        return cv2.findChessboardCorners(frame, boardSize, flags=cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    else:
        return cv2.findChessboardCorners(frame, boardSize, flags=cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE)
