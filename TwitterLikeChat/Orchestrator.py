import queue
import threading
import time
from UserService import UserService
from FeedService import FeedService
from ConnectionService import ConnectionService


class Orchestrator:
    def __init__(self):
        self.user_service = UserService()
        self.feed_service = FeedService()
        self.command_queue = queue.Queue()
        self.connection_service = ConnectionService(orchestrator_queue=self.command_queue)
        self.feed_updated = False

    def start(self):
        print("[*] Orchestrator started.")
        connection_service_thread = threading.Thread(target=self.connection_service.start, args=())
        connection_service_thread.start()
        self.process_commands()

    def process_commands(self):
        print("[*] Processing commands started.")
        print(self.command_queue.unfinished_tasks)
        while True:

            try:
                client_address, command = self.command_queue.get(block=False)
                self.handle_command(client_address, command)
            except queue.Empty:
                if self.feed_updated:
                    self.send_feed_update()
                    self.feed_updated = False
                time.sleep(0.1)

    def handle_command(self, client_address, command):
        print(f"[+] Received {command} from {client_address}")
        if command == "/help":
            self.send_message(client_address, "/help - Show this help message")
            self.send_message(client_address, "/login: <NAME> - Login with username")
            self.send_message(client_address, "/reg: <NAME> - Register a new user")
            self.send_message(client_address, "/logout - Logout")
            self.send_message(client_address, "/send: <MSG> - Send a message")
            self.send_message(client_address, "/like: <NAME> <TIMESTAMP> - Like a message")
        elif command.startswith("/login:"):
            username = command.split(":")[1].strip()
            success, message = self.user_service.login_user(username)
            if success:
                self.connection_service.set_registered_status(client_address, True, username)
                self.send_message(client_address, message)
            else:
                self.send_message(client_address, message)
        elif command.startswith("/reg:"):
            username = command.split(":")[1].strip()
            success, message = self.user_service.register_user(username)
            if success:
                self.send_message(client_address, message)
                self.send_message(client_address, "Please login now.")
            else:
                self.send_message(client_address, message)
        elif command == "/logout":
            if self.connection_service.is_registered(client_address):

                username = self.connection_service.get_registered_username(client_address)

                success, message = self.user_service.logout_user(username)
                self.connection_service.set_registered_status(client_address, False)
                self.send_message(client_address, message)
            else:
                self.send_message(client_address, "You are not logged in.")
        elif command.startswith("/send:"):
            if self.connection_service.is_registered(client_address):
                message = command.split(":")[1].strip()

                username = self.connection_service.get_registered_username(client_address)

                self.feed_service.add_message(username, message)
            else:
                self.send_message(client_address, "Please register or log in.")
        elif command.startswith("/like:"):
            if self.connection_service.is_registered(client_address):
                parts = command.split(":")[1].strip().split(" ")
                if len(parts) == 2:
                    username, timestamp = parts
                    try:
                        timestamp = float(timestamp)
                        success, message = self.feed_service.like_message(username, timestamp)
                        self.send_message(client_address, message)
                    except ValueError:
                        self.send_message(client_address, "[!] Invalid timestamp format.")
                else:
                    self.send_message(client_address, "[!] Invalid command format.")
            else:
                self.send_message(client_address, "[!] Please register or log in.")
        else:
            self.send_message(client_address, "[!] Invalid command. Use /help for available commands.")

    def send_feed_update(self):
        feed = self.feed_service.get_feed()
        for client_address in self.connection_service.connections:
            self.send_message(client_address, "[*] Feed Update")
            for message in feed:
                msg = f"[*] {message['username']}, {message['timestamp']} : {message['message']}"
                msg += f"\n[*] Liked by: {', '.join(message['likes'])}"
                msg += "\n-------------------------------------------------------------------------"
                self.send_message(client_address, msg)

    def send_message(self, client_address, message):
        socket = self.connection_service.getSocketByAddress(client_address)
        self.connection_service.send_message(socket, message)

    def stop(self):
        self.connection_service.stop()
        print("Orchestrator stopped.")


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.start()
