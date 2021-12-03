#!/bin/python3
import cv2
import socket
import pickle
import struct
from time import sleep

import simplejpeg


while True:
    clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    while True:
        try:
            clientsocket.connect(('192.168.43.184',1234))
            break
        except ConnectionRefusedError:
            print("waiting for server")
            sleep(1)


    payload_size = struct.calcsize("=L") ### CHANGED

    data = b'' ### CHANGED

    while True:
        # Retrieve message size
        while len(data) < payload_size:
            data += clientsocket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("=L", packed_msg_size)[0] ### CHANGED

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += clientsocket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Extract frame
        frame = pickle.loads(frame_data)
        frame = simplejpeg.decode_jpeg(frame)

        frame = cv2.resize(frame, (1080, 720))

        # Display
        cv2.imshow('frame', frame)
        cv2.waitKey(1)