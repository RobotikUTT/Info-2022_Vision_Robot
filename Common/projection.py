import numpy as np
import calibration
import cv2

if __name__ == "__main__":

    calib = calibration.CameraCalibration.load("config.json")

    print(calib.mtx)
    mtx = calib.mtx


    Lcam=mtx.dot(np.hstack((cv2.Rodrigues(rvecs[0])[0],tvecs[0])))