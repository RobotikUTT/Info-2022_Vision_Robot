#!/bin/python3
import cv2
import socket
import pickle
import struct
import simplejpeg
import calibration
import os

from time import sleep

payload_size = struct.calcsize("L") ### CHANGED


class VideoStreamer():
    """This class is responsible for keeping several streaming sockets open, and allows frames to be sent to all clients."""
    
    def __init__(self, port, quality=None):
        """Constructor for VideoStreamer.

        Args:
            port (int): The port on which to supply the video stream.
            quality (tuple(int, int), optional): The dimmensions to which each will be resized before being sent. If left as None, the frames will not be resized.
        """

        self.port = port

        self.quality = quality

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(0)
        
        
        self.connections = []

    def start(self, keepTrying=True):
        """Starts the stream, as in opens the port given to the constructor.

        Args:
            keepTrying (bool, optional): Whether this function will hang/loop until the server can be opened (say if the port was already open). Defaults to True.
        """
        while True:
            try:
                self.socket.bind(('', self.port))
                self.socket.listen(10)
                break
            except OSError:
                if not keepTrying: break
                sleep(1)
        

    def checkConnections(self):
        """Check to see if there are new clients. Should be run regularly (like every time you send a frame).
        """
        try:
            conn, addr = self.socket.accept()
            self.connections.append(conn)
            print(f"new connection. now {len(self.connections)} connections")
            print(conn)

        except BlockingIOError:
            pass

    def sendFrame(self, frame=None):
        """Sends a frame to all clients. The server must have been previously started (see :func:`VideoStreamer.start`)

        Args:
            frame ([type], optional): [description]. Defaults to None.
        """
        if self.quality != None:
            frame = cv2.resize(frame, self.quality)

        # Serialize frame
        data = simplejpeg.encode_jpeg(frame, 90)
        data = pickle.dumps(data)

        # Send message length first
        message_size = struct.pack("L", len(data)) ### CHANGED

        for conn in self.connections.copy():
            try:
                conn.sendall(message_size + data)
            except (ConnectionResetError, BrokenPipeError):
                print(f"closing: {conn}")
                conn.close()
                self.connections.remove(conn)

    def closeAll(self):
        """Close all client connections.
        """
        for c in self.connections:
            c.shutdown(2)
            c.close()

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    # A test configuration file exists in the same folder as this script. 
    # Because relative paths are weird (depending from where you called the script), 
    # we need to get the current script's path and add the name of the configuration file.
    dirname = os.path.dirname(__file__)
    configFilePath = os.path.join(dirname, "testConfig.json")

    calib = calibration.CameraCalibration.load(configFilePath)

    v = VideoStreamer(1234, calib.DIM)
    v.start()

    try:
        while True:
            v.checkConnections()
            ret, frame = cap.read() 
            # frame = cv2.resize(frame, calib.DIM)

            v.sendFrame(frame)

    except KeyboardInterrupt:
        print("quitting")
        v.closeAll()