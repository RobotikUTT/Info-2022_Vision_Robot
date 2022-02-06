from Camera.calibration import CameraCalibration
import numpy as np
import cv2

class PoseEstimation:
    def __init__(self, camera_calibration: CameraCalibration):
        self.cam_mtx = camera_calibration.K
        self.inv_cam_mtx = np.linalg.inv(self.cam_mtx)
        self.camera_pos = None

    def get_camera_pos(self):
        return self.camera_pos
    
    def solve_new_position(self, objpoints, imgpoints):
        objpoints = np.array(objpoints, dtype=float)
        imgpoints = np.array(imgpoints, dtype=float)

        ret, rvec, tvec, *_ = cv2.solvePnP(objpoints, imgpoints, self.cam_mtx, None)

        rvec = rvec.squeeze()
        tvec = tvec.squeeze()
        
        self.r_mat = cv2.Rodrigues(rvec)[0]
        self.tvec = tvec

        self.camera_pos = -self.r_mat.T.dot(tvec)

    def get_direction(self, screen_pos):
        pos_on_screen = np.array( self.r_mat.T.dot((self.inv_mtx.dot(screen_pos) - self.tvec)) )
        return pos_on_screen - self.camera_pos

    def get_world_pos(self, screen_pos, height=0):
        direction = self.get_direction(screen_pos)

        s = (height - self.camera_pos[2])/direction[2]

        return self.camera_pos + s * direction