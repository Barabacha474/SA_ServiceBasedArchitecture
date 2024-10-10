import json
import socket
import threading
import time

class ConnectionService:
    def __init__(self, host="localhost", port=5000, orchestrator_queue=None):
        self.host = host
        self.port = port
        self.orchestrator_queue = orchestrator_queue
        self.connections = {}

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        self.running = True
        self.connection_threads = []

    def start(self):
        print(f"[*] Connection service started on {self.host}:{self.port}")
        while self.running:
            client_socket, client_address = self.server_socket.accept()
            print(f"[+] Connection from {client_address}")
            connection_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            self.connection_threads.append(connection_thread)
            connection_thread.start()

    def handle_client(self, client_socket, client_address):
        self.connections[client_address] = {"registered": False}
        self.send_message(client_socket, "Welcome to Twitter-like chat!")
        self.send_message(client_socket, "Please enter your username:")
        while True:
            try:
                data = client_socket.recv(1024).decode("utf-8").strip()
                if data == "/exit":
                    self.disconnect_client(client_socket, client_address)
                    break
                self.orchestrator_queue.put((client_address, data))
            except ConnectionResetError:
                print(f"[-] Connection with {client_address} lost.")
                self.disconnect_client(client_socket, client_address)
                break

    def send_message(self, client_socket, message):
        client_socket.sendall(message.encode("utf-8"))

    def disconnect_client(self, client_socket, client_address):
        client_socket.close()
        if client_address in self.connections:
            del self.connections[client_address]
            self.orchestrator_queue.put((client_address, "/logout"))
        print(f"Disconnected from {client_address}")

    def set_registered_status(self, client_address, status):
        if client_address in self.connections:
            self.connections[client_address]["registered"] = status

    def is_registered(self, client_address):
        if client_address in self.connections:
            return self.connections[client_address]["registered"]
        return False

    def stop(self):
        self.running = False
        self.server_socket.close()
        for thread in self.connection_threads:
            thread.join()
        print("[!] Connection service stopped.")