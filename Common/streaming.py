import cv2
import socket
import pickle
import struct
import simplejpeg
import calibration
import detection

from time import sleep

payload_size = struct.calcsize("L") ### CHANGED

cap = cv2.VideoCapture(0)

class VideoStreamer():
    def __init__(self, port, quality=None):
        self.port = port

        self.quality = quality

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(0)
        
        
        self.connections = []

    def start(self, keepTrying=True):
        while True:
            try:
                self.socket.bind(('', self.port))
                self.socket.listen(10)
                break
            except OSError:
                if not keepTrying: break
                sleep(1)
        

    def checkConnections(self):
        try:
            conn, addr = self.socket.accept()
            self.connections.append(conn)
            print(f"new connection. now {len(self.connections)} connections")
            print(conn)

        except BlockingIOError:
            pass

    def sendFrame(self, frame=None):
        if self.quality != None:
            frame = cv2.resize(frame, self.quality)

        # Serialize frame
        data = simplejpeg.encode_jpeg(frame, 50)
        data = pickle.dumps(data)

        # Send message length first
        message_size = struct.pack("L", len(data)) ### CHANGED

        for conn in self.connections.copy():
            try:
                conn.sendall(message_size + data)
            except (ConnectionResetError, BrokenPipeError):
                conn.close()
                self.connections.remove(conn)

    def closeAll(self):
        for c in self.connections:
            c.shutdown(2)
            c.close()

if __name__ == "__main__":
    calib = calibration.CameraCalibration.load("config.json")

    v = VideoStreamer(8089, calib.DIM)
    v.start()

    try:
        while True:
            v.checkConnections()
            ret, frame = cap.read() 
            frame = cv2.resize(frame, calib.DIM)
            # frame = calibration.undistort(frame, calib)

            # ret, corners = detection.findChessboard(frame, convertToGray=True, fast=True)
            # frame = cv2.drawChessboardCorners(frame, (6, 9), corners, ret)


            v.sendFrame(frame)

    except KeyboardInterrupt:
        print("quitting")
        v.closeAll()