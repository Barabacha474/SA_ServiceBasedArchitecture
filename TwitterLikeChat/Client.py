import socket
import threading

HOST = "localhost"
PORT = 5000

def receive_data(s):
    while True:
        try:
            data = s.recv(1024).decode("utf-8")
            print(data)
        except ConnectionResetError:
            print("[!] Connection lost. Exiting.")
            break

def send_commands(s):
    while True:
        message = input("")
        s.sendall(message.encode("utf-8"))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    receive_thread = threading.Thread(target=receive_data, args=(s,))
    send_thread = threading.Thread(target=send_commands, args=(s,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()