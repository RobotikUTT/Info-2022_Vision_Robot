from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import cv2
import numpy as np
import json

class CameraCalibration:
    def __init__(self, DIM: Tuple(int, int), K: np.array, D: np.array):
        self.DIM = DIM
        self.K = K
        self.D = D

    def save_to_file(self, path):
        data = {"DIM": self.DIM, "K": self.K.tolist(), "D": self.D.tolist()}

        with open(path, "w") as fp:
            json.dump(data, fp, indent=2)

    @staticmethod
    def load_from_file(path) -> CameraCalibration:
        with open(path, "r") as fp:
            data = json.load(fp)

        return CameraCalibration(
            tuple(data["DIM"]),
            np.array(data["K"]),
            np.array(data["D"]),
        )

    @staticmethod
    def generate_camera_calibration(
        image_size, objpoints, imgpoints
    ) -> CameraCalibration:
        DIM = image_size
        K = np.zeros((3, 3))
        D = np.zeros((4, 1))

        calibration_flags = (
            cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC
            + cv2.fisheye.CALIB_CHECK_COND
            + cv2.fisheye.CALIB_FIX_SKEW
        )

        cv2.fisheye.calibrate(
            objpoints,
            imgpoints,
            DIM,
            K,
            D,
            None,
            None,
            calibration_flags,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6),
        )

        return CameraCalibration(DIM, K, D)

    def get_undistortion_maps(self, dim1, dim2=None, dim3=None):
        if not dim2:
            dim2 = dim1
        if not dim3:
            dim3 = dim2

        scaled_K = (
            self.K * dim1[0] / self.DIM[0]
        )  # The values of K is to scale with image dimension.
        scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0

        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
            scaled_K, self.D, dim2, np.eye(3), balance=1
        )

        map1, map2 = cv2.fisheye.initUndistortRectifyMap(
            scaled_K, self.D, np.eye(3), new_K, dim3, cv2.CV_16SC2
        )

        return map1, map2

    @staticmethod
    def undistort(frame, map1, map2):
        undistorted_img = cv2.remap(
            frame,
            map1,
            map2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
        )
        return undistorted_img