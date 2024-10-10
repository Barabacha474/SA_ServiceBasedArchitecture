import socket

HOST = "localhost"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        data = s.recv(1024).decode("utf-8")
        print(data)
        message = input("Enter command: ")
        s.sendall(message.encode("utf-8"))