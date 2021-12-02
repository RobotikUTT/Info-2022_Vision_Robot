# https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0

import yaml
import cv2
assert cv2.__version__[0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'
import numpy as np
import glob
import json
from dataclasses import dataclass
import detection


@dataclass()
class CameraCalibration():
    DIM: list
    mtx: np.matrix
    dist: list

    def save(self, dataPath):
        data = {
            "DIM": self.DIM,
            "mtx": np.asarray(self.mtx).tolist(),
            "dist": np.asarray(self.dist).tolist()
            }
        with open(dataPath, 'w') as fp:
            json.dump(data, fp, indent=4)

    def load(dataPath):
        with open(dataPath, 'r') as fp:
            data = json.load(fp)
            return CameraCalibration(
                data['DIM'],
                np.array(data['mtx']),
                np.array(data['dist'])
            )

def getCameraCalibration(imagesPath : str, checkerboardSize = (6, 9)):

    subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_FIX_SKEW

    # objp gives the positions of all the points on a checkerboard
    objp = np.zeros((1, checkerboardSize[0]*checkerboardSize[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:checkerboardSize[0], 0:checkerboardSize[1]].T.reshape(-1, 2)*34

    _img_shape = None

    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    images = glob.glob(f"{imagesPath}/*")

    for fname in images:
        img = cv2.imread(fname)
        if _img_shape == None:
            _img_shape = img.shape[:2]
        else:
            assert _img_shape == img.shape[:2], "All images must share the same size."
            
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = detection.findChessboard(img)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),subpix_criteria)
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

    DIM =_img_shape[::-1]

    cameraCalib = CameraCalibration(DIM, K, D)

    return cameraCalib

def undistort(img, calibrationData: CameraCalibration, balance=1, dim2=None, dim3=None):

    DIM = calibrationData.DIM
    K = calibrationData.mtx
    D = calibrationData.dist

    dim1 = img.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort    
    
    assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    
    if not dim2:
        dim2 = dim1    

    if not dim3:
        dim3 = dim1    
        
    scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.

    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0    
    
    # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3), balance=balance)

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    return undistorted_img


if __name__ == "__main__":
    data = getCameraCalibration(".images")
    data.save("config.json")
    data = CameraCalibration.load("config.json")
    img = cv2.imread(".images/3.jpg")

    m = np.mat(data.mtx)

    undistorted_img = undistort(img, data)

    cv2.imshow("test", undistorted_img)
    cv2.waitKey(100000)

