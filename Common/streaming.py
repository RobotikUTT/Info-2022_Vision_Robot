import cv2
import socket
import pickle
import struct
import simplejpeg
import calibration

from time import sleep

payload_size = struct.calcsize("L") ### CHANGED

cap = cv2.VideoCapture(0)

class VideoStreamer():
    def __init__(self, port):
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)
        self.socket.bind(('', self.port))
        self.socket.listen(10)
        
        self.connections = []

    def checkConnections(self):
        try:
            conn, addr = self.socket.accept()
            self.connections.append(conn)
            print(f"new connection. now {len(self.connections)} connections")
            print(conn)

        except BlockingIOError:
            pass

    def sendFrame(self, frame=None):
        frame = cv2.resize(frame, (720, 480))

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

while True:
    try:
        v = VideoStreamer(8089)
        print("ready")
        break
    except OSError:
        print(".", end="")
        sleep(1)


calib = calibration.CameraCalibration.load("config.json")



try:
    while True:
        v.checkConnections()
        ret, frame = cap.read() 
        frame = cv2.resize(frame, calib.DIM)
        frame = calibration.undistort(frame, calib)

        v.sendFrame(frame)

except KeyboardInterrupt:
    print("quitting")
    v.closeAll()