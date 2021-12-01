import cv2
import socket
import pickle
import struct
import simplejpeg

cap=cv2.VideoCapture(0)
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('localhost',8089))

while True:
    ret,frame=cap.read()
    # Serialize frame

    frame = cv2.resize(frame, (1080, 720))

    data = simplejpeg.encode_jpeg(frame)
    data = pickle.dumps(frame)

    # Send message length first
    message_size = struct.pack("L", len(data)) ### CHANGED

    # Then data
    clientsocket.sendall(message_size + data)
