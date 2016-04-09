import socket, sys
from _thread import *

HOST = socket.gethostname()
PORT = 4594

def clientthread(conn):
    msg = "Welcome to the server.\n"
    conn.send(msg.encode())
    while True:
        data = conn.recv(1024).decode()
        print(data)
        reply = "Poop" + data
        if not data:
            break

        conn.sendall(reply.encode())

    conn.close()

s = socket.socket()
s.bind((HOST, PORT))
print("Socket Bind Complete")

s.listen(1)
print("Socket now listening")

while True:
    conn, addr = s.accept()
    print("Connected with " + addr[0] + ":" + str(addr[1]))
    start_new_thread(clientthread,(conn,))

s.close()
