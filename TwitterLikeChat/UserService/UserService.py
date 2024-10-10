import json

class UserService:
    def __init__(self, users_db_path="UserService/users.json", orchestrator_queue = None):
        self.orchestrator_queue = orchestrator_queue
        self.users_db_path = users_db_path
        try:
            with open(self.users_db_path, "r") as f:
                self.users = json.load(f)

                for username in self.users:
                    self.users[username]["online"] = False

        except FileNotFoundError:
            self.users = {}


    def save_users(self):
        with open(self.users_db_path, "w") as f:
            json.dump(self.users, f)

    def register_user(self, username):
        if username in self.users:
            return False, "[!] User already exists. Please log in."
        self.users[username] = {"online": False}
        self.save_users()
        return True, "[+] User registered successfully. Please log in."

    def login_user(self, username):
        if username not in self.users:
            return False, "[!] User not found. Please register."
        if self.users[username]["online"]:
            return False, "[!] User already logged in. Please use a different username."
        self.users[username]["online"] = True
        self.save_users()
        return True, "[+] Login successful."

    def logout_user(self, username):
        if username not in self.users:
            return False, "[!] User not found."
        if not self.users[username]["online"]:
            return False, "[!] User is not logged in."
        self.users[username]["online"] = False
        self.save_users()
        return True, "[-] Logout successful."

    def is_registered(self, username):
        return username in self.users

    def is_online(self, username):
        return self.users[username]["online"] if self.is_registered(username) else False

    def get_registered_users(self):
        return list(self.users.keys())

    def get_online_users(self):
        return [user for user, data in self.users.items() if data["online"]]