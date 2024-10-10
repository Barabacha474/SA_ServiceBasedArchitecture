import socket

HOST = "localhost"  # The server's hostname or IP address
PORT = 5000        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        data = s.recv(1024).decode("utf-8")
        print(data)
        message = input("Enter command: ")
        s.sendall(message.encode("utf-8"))