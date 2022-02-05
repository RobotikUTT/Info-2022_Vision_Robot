from glob import glob
import cv2
import numpy as np
from Camera.calibration import CameraCalibration

from Common.utils import find_chessboard, corner_sub_pix

def generate_calibration(image_folder, output_file_path, board_size=(6, 9)):
    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    # The positions of the corners on a chessbaord
    # Everytime a chessboard is detected, we can add these points to objpoints
    objp = np.zeros((1, board_size[0] * board_size[1], 3), np.float32)
    objp[0, :, :2] = np.mgrid[0 : board_size[0], 0 : board_size[1]].T.reshape(-1, 2)

    size = None

    print(f"Analysing images in '{image_folder}':")
    files = sorted(glob(f"{image_folder}/*.jpg"))
    for image_path in files:
        print(f"- {image_path}")
        frame = cv2.imread(image_path)
        if size == None:
            size = frame.shape[:2][::-1]

        if size != frame.shape[:2][::-1]:
            print("image sizes not all same")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = find_chessboard(gray, board_size, fast=True)

        if not ret:
            print(f"couldn't find chessboard for image '{image_path}'")
            continue

        corners = corner_sub_pix(gray, corners)

        objpoints.append(objp)
        imgpoints.append(corners)

        try:
            calibration = CameraCalibration.generate_camera_calibration(size, objpoints, imgpoints)
            calibration.save_to_file(output_file_path)
        except cv2.error:
            objpoints.pop()
            imgpoints.pop()
            print(f"bad image: {image_path}")

        
    # for i, f in enumerate(files):
    #     print(i, f)
    calibration = CameraCalibration.generate_camera_calibration(size, objpoints, imgpoints)

    calibration.save_to_file(output_file_path)
    