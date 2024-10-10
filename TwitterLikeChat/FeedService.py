import json
import time

class FeedService:
    def __init__(self, feed_db_path="feed.json"):
        self.feed_db_path = feed_db_path
        try:
            with open(self.feed_db_path, "r") as f:
                self.feed = json.load(f)
        except FileNotFoundError:
            self.feed = []
        self.feed_updated = False

    def save_feed(self):
        with open(self.feed_db_path, "w") as f:
            json.dump(self.feed, f)
        self.feed_updated = True

    def add_message(self, username, message, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        new_message = {
            "message": message,
            "username": username,
            "likes": [],
            "timestamp": timestamp
        }
        self.feed.insert(0, new_message)
        self.delete_last_message()

    def delete_last_message(self):
        if self.feed:
            self.feed.pop()
            self.save_feed()

    def like_message(self, username, timestamp):
        for message in self.feed:
            if message["timestamp"] == timestamp:
                if username not in message["likes"]:
                    message["likes"].append(username)
                    self.save_feed()
                    return True, "[*] Message liked."
                else:
                    return False, "[!] You have already liked this message."
        return False, "[!] Message not found."

    def get_feed(self):
        return self.feed