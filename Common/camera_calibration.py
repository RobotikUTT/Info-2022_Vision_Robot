from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import json
from web_interface import WebInterfaceThread, StreamConfiguration
import frame_capture as f_cap
from utils import (
    corner_sub_pix,
    find_chessboard,
    scale_image,
)
from frame_supplier import FrameSupplier
import cv2
import numpy as np


class CameraCalibration:
    def __init__(self, DIM: Tuple(int, int), K: np.array, D: np.array):
        self.DIM = DIM
        self.K = K
        self.D = D

    def save_to_file(self, path):
        data = {"DIM": self.DIM, "K": self.K.tolist(), "D": self.D.tolist()}

        with open(path, "w") as fp:
            json.dump(data, fp, indent=2)

    def load_from_file(path) -> CameraCalibration:
        with open(path, "r") as fp:
            data = json.load(fp)

        return CameraCalibration(
            tuple(data["DIM"]),
            np.array(data["K"]),
            np.array(data["D"]),
        )

    def generate_camera_calibration(
        image_size, objpoints, imgpoints
    ) -> CameraCalibration:
        DIM = image_size
        K = np.zeros((3, 3))
        D = np.zeros((4, 1))

        calibration_flags = (
            cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC
            # + cv2.fisheye.CALIB_CHECK_COND
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

    def undistort(self, frame, map1, map2):
        undistorted_img = cv2.remap(
            frame,
            map1,
            map2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
        )
        return undistorted_img


def live_calibration(
    frame_capture: f_cap.FrameCaptureThread,
    frame_output: FrameSupplier,
    board_size=(6, 9),
    nb_frames=50,
    low_res_scale_factor=1,
) -> CameraCalibration:
    print("starting live calibration")

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    # The positions of the corners on a chessbaord
    # Everytime a chessboard is detected, we can add these points to objpoints
    objp = np.zeros((1, board_size[0] * board_size[1], 3), np.float32)
    objp[0, :, :2] = np.mgrid[0 : board_size[0], 0 : board_size[1]].T.reshape(-1, 2)

    nb_frames_collected = 0
    previous_frame = None
    while nb_frames_collected < nb_frames:
        full_frame = frame_capture.get_frame(previous_frame)
        previous_frame = full_frame

        resized = scale_image(full_frame, low_res_scale_factor)

        resized_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        ret, low_res_corners = find_chessboard(resized_gray, board_size, fast=False)

        if not ret:
            continue

        # Get the four corners of the chessboard
        quad_corners = low_res_corners[[0, 5, -1, -6]]

        x, y, w, h = cv2.boundingRect(quad_corners)
        x -= w // 4
        y -= h // 4
        w += w // 2
        h += h // 2

        x = int(x / low_res_scale_factor)
        y = int(y / low_res_scale_factor)
        w = int(w / low_res_scale_factor)
        h = int(h / low_res_scale_factor)

        x = max(0, x)
        y = max(0, y)

        cropped = full_frame[y : y + h, x : x + w]
        cropped = np.ascontiguousarray(cropped)
        cropped_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

        ret, cropped_corners = find_chessboard(cropped_gray, board_size, fast=True)

        if not ret:
            continue

        nb_frames_collected += 1

        cropped_corners = corner_sub_pix(cropped_gray, cropped_corners)
        corners = np.array(cropped_corners + (x, y), dtype="f")

        objpoints.append(objp)
        imgpoints.append(corners)

        cv2.drawChessboardCorners(full_frame, board_size, corners, True)
        frame_output.set_new_frame(full_frame)

        print(f"got {nb_frames_collected} frames")

    frame = frame_capture.get_frame()
    DIM = frame.shape[1::-1]

    config = CameraCalibration.generate_camera_calibration(DIM, objpoints, imgpoints)

    return config


if __name__ == "__main__":

    frame_capture = f_cap.FrameCaptureThread()
    frame_capture.start()

    output_frame_supplier = FrameSupplier()

    web_interface = WebInterfaceThread()
    web_interface.start()
    web_interface.create_video_stream(
        "/raw", StreamConfiguration(frame_capture, f_cap.RES_640x480)
    )
    web_interface.create_video_stream("/output", StreamConfiguration(output_frame_supplier))

    config = live_calibration(
        frame_capture, output_frame_supplier, low_res_scale_factor=0.25
    )
    config.save_to_file("config.json")

    config = CameraCalibration.load_from_file("config.json")
    dim1 = frame_capture.get_resolution()

    map1, map2 = config.get_undistortion_maps(dim1)

    previous_frame = None
    while True:
        frame = frame_capture.get_frame(previous_frame)
        previous_frame = frame
        undistorted_img = config.undistort(frame, map1, map2)
        output_frame_supplier.set_new_frame(undistorted_img)
