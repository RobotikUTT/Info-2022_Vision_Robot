import cv2
import numpy as np
import socket
import pickle
import struct

import simplejpeg

# cap=cv2.VideoCapture(0)
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('192.168.43.210',8089))

payload_size = struct.calcsize("L") ### CHANGED

data = b'' ### CHANGED

while True:
    # Retrieve message size
    while len(data) < payload_size:
        data += clientsocket.recv(4096)

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED

    # Retrieve all data based on message size
    while len(data) < msg_size:
        data += clientsocket.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    # Extract frame
    frame = pickle.loads(frame_data)

    frame = simplejpeg.decode_jpeg(frame)

    # Display
    cv2.imshow('frame', frame)
    cv2.waitKey(1)