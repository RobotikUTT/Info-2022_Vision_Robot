import numpy as np
import cv2 as cv
import glob
import calibration

boardSize = (6, 9)
bx, by = boardSize

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((by*bx,3), np.float32)
objp[:,:2] = np.mgrid[0:bx,0:by].T.reshape(-1,2) * 34
axis = np.float32([[1,0,0], [0,1,0], [0,0,-1]]).reshape(-1,3) * 170


def draw(img, corners, imgpts):
    corner = corners[0].ravel()

    corner = tuple(int(v) for v in corner)
    
    int_imgpts = []
    for point in imgpts:
        int_imgpts.append([int(v) for v in point.ravel()])

    print(int_imgpts)

    img = cv.line(img, corner, int_imgpts[0], (255,0,0), 5)
    img = cv.line(img, corner, int_imgpts[1], (0,255,0), 5)
    img = cv.line(img, corner, int_imgpts[2], (0,0,255), 5)
    return img



data = calibration.CameraCalibration.load("config.json")
mtx = data.mtx
dist = data.dist



for fname in glob.glob(".images/*"):
    img = cv.imread(fname)

    img = calibration.undistort(img, data)

    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, (bx,by),None)
    if ret == True:
        corners2 = cv.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)

        img = cv.drawChessboardCorners(img, (6, 9), corners2, True)

        # Find the rotation and translation vectors.
        # ret,rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)
        ret,rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, None)

        print(rvecs, tvecs)

        # project 3D points to image plane
        # imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, None)


        print("rvecs: ")
        print(rvecs)
        print("tvecs")
        print(tvecs)
        print('----------------')

        img = draw(img,corners2,imgpts)
        cv.imshow('img',img)
        k = cv.waitKey(0) & 0xFF
        if k == ord('s'):
            cv.imwrite(fname[:6]+'.png', img)

cv.destroyAllWindows()