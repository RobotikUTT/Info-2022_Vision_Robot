from typing import Tuple
import cv2
import numpy as np
from Camera.calibration import CameraCalibration
from Camera.frame_capture import FrameCaptureThread
from Camera.undistorted import UndistortedFrameSupplierThread

from Common.frame_supplier import FrameSupplier

# Shorthand for cv2.findChessboardCorners with some default flags
# Can take a "fast" boolean to indicate whether to use the "cv2.CALIB_CB_FAST_CHECK" flag,
# in which case the function will just call "find_chessboard_fast"
def find_chessboard(frame, board_size=(6, 9), fast=False):
    if fast:
        return find_chessboard_fast(frame, board_size)

    return cv2.findChessboardCorners(
        frame,
        board_size,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )


def find_chessboard_fast(frame, board_size=(6, 9)):
    return cv2.findChessboardCorners(
        frame,
        board_size,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_FAST_CHECK
        + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )


def scale_image(frame, scale_factor):
    width = int(frame.shape[1] * scale_factor)
    height = int(frame.shape[0] * scale_factor)
    dim = (width, height)

    return cv2.resize(frame, dim, interpolation=cv2.INTER_NEAREST)


def corner_sub_pix(frame, corners):
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    return cv2.cornerSubPix(frame, corners, (11, 11), (-1, -1), criteria)

# Start the camera capture thread as well as the undistortion thread and return both.
def camera_setup(calib_file: CameraCalibration) -> FrameSupplier:
    camera_calibration = CameraCalibration.load_from_file(calib_file)

    frame_capture = FrameCaptureThread()
    frame_capture.start()

    undistorted_supplier = UndistortedFrameSupplierThread(frame_capture, camera_calibration)
    undistorted_supplier.start()

    return frame_capture, undistorted_supplier