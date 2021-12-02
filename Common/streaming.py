import cv2
import socket
import pickle
import struct
import simplejpeg

HOST = ''
PORT = 8089

cap = cv2.VideoCapture(0)

payload_size = struct.calcsize("L") ### CHANGED

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST, PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn, addr = s.accept()

data = b'' ### CHANGED


while True:
    ret,frame = cap.read()
    frame = cv2.resize(frame, (720, 480))

    # Serialize frame
    data = simplejpeg.encode_jpeg(frame, 1)
    data = pickle.dumps(data)

    # Send message length first
    message_size = struct.pack("L", len(data)) ### CHANGED

    # Then data
    conn.sendall(message_size + data)

    