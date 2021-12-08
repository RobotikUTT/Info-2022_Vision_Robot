#!/bin/python3
# https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0

import pickle
import streaming
import detection
from dataclasses import dataclass
import json
import glob
import numpy as np
import cv2
assert cv2.__version__[
    0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'

global test_map1
# global test2_map1


@dataclass()
class CameraCalibration():
    """A dataclass to hold the calibration data for a specific camera.

    Args:
        DIM : The dimmension of the images used during calibration.
    """
    DIM: list
    mtx: np.matrix
    dist: list
    map1: np.ndarray
    map2: np.ndarray

    def save(self, dataPath):
        with open(dataPath, 'wb') as fp:
            pickle.dump(self, fp)

    def load(dataPath):
        with open(dataPath, 'rb') as fp:
            return pickle.load(fp)


def getCameraCalibration(imagesPath: str, checkerboardSize=(6, 9)) -> CameraCalibration:

    subpix_criteria = (cv2.TERM_CRITERIA_EPS +
                       cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + \
        cv2.fisheye.CALIB_FIX_SKEW+cv2.CALIB_RATIONAL_MODEL

    # objp gives the positions of all the points on a checkerboard
    objp = np.zeros(
        (1, checkerboardSize[0]*checkerboardSize[1], 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:checkerboardSize[0],
                              0:checkerboardSize[1]].T.reshape(-1, 2)*34

    _img_shape = None

    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    images = glob.glob(f"{imagesPath}/*")

    for fname in images:
        img = cv2.imread(fname)
        if _img_shape == None:
            _img_shape = img.shape[:2]
        else:
            assert _img_shape == img.shape[:2], "All images must share the same size."

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = detection.findChessboard(img)

        # If found, add object points, image points (after refining them)
        if ret == True:
            print(f"Found: {fname}")
            objpoints.append(objp)
            cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), subpix_criteria)
            imgpoints.append(corners)

    N_OK = len(objpoints)

    K = np.zeros((3, 3))
    D = np.zeros((4, 1))

    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]

    rms, K, D, rvecs, tvecs = \
        cv2.fisheye.calibrate(
            objpoints,
            imgpoints,
            gray.shape[::-1],
            K,
            D,
            rvecs,
            tvecs,
            calibration_flags,
            (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
        )

    DIM = _img_shape[::-1]

    # scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.
    scaled_K = K
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0

    # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        scaled_K, D, DIM, np.eye(3), balance=1)
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        scaled_K, D, np.eye(3), new_K, DIM, cv2.CV_16SC2)

    cameraCalib = CameraCalibration(DIM, K, D, map1, map2)

    return cameraCalib


def undistort(img, calibrationData: CameraCalibration):

    DIM = calibrationData.DIM
    map1 = calibrationData.map1
    map2 = calibrationData.map2

    # dim1 is the dimension of input image to un-distort
    dim1 = img.shape[:2][::-1]
    assert list(dim1) == list(
        DIM), "Image to undistort needs to have the same dimmensions as the ones used in calibration"

    return cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

    # data = getCameraCalibration(".images")
    # data.save("config.json")

    data = CameraCalibration.load("config.json")

    stream = streaming.VideoStreamer(1234)
    stream.start()

    while True:
        ret, frame = cap.read()
        frame = undistort(frame, data)
        stream.checkConnections()
        stream.sendFrame(frame)
