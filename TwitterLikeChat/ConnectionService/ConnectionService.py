import json
import socket
import threading
import time

lock = threading.Lock()

class ConnectionService:
    def __init__(self, host="localhost", port=5000, orchestrator_queue=None):
        self.host = host
        self.port = port
        self.orchestrator_queue = orchestrator_queue
        self.connections = {}
        self.addressToSocket = {}

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
            with lock:
                self.addressToSocket[client_address] = client_socket
            connection_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            self.connection_threads.append(connection_thread)
            connection_thread.start()

    def handle_client(self, client_socket, client_address):
        self.connections[client_address] = {"registered": False, "username": None, "socket": client_socket}
        self.send_message(client_socket, "Welcome to Twitter-like chat!")
        while True:
            try:
                data = client_socket.recv(407).decode("utf-8").strip() #'/send '+ 400 symbols

                if data == "/exit":
                    with lock:
                        self.disconnect_client(client_socket, client_address)
                    break
                with lock:
                    self.orchestrator_queue.put((client_address, data))
            except ConnectionResetError:
                print(f"[-] Connection with {client_address} lost.")
                with lock:
                    self.disconnect_client(client_socket, client_address)
                break

    def send_message(self, client_socket, message):
        print(f"[+] Sending {message}")
        print(f"[+] Sending {client_socket}")
        client_socket.sendall(message.encode("utf-8"))

    def getSocketByAddress(self, address):
        return self.connections[address]["socket"]

    def disconnect_client(self, client_socket, client_address):
        client_socket.close()
        if client_address in self.connections:
            del self.connections[client_address]
            self.orchestrator_queue.put((client_address, "/logout"))
        print(f"[-] Disconnected from {client_address}")

    def set_registered_status(self, client_address, status, username = None):
        if client_address in self.connections:
            self.connections[client_address]["registered"] = status
            self.connections[client_address]["username"] = username

    def is_registered(self, client_address):
        if client_address in self.connections:
            return self.connections[client_address]["registered"]
        return False

    def get_username(self, client_address):
        if self.is_registered(client_address):
            return self.connections[client_address]["username"]
        else:
            return None

    def stop(self):
        self.running = False
        self.server_socket.close()
        for thread in self.connection_threads:
            thread.join()
        print("[!] Connection service stopped.")