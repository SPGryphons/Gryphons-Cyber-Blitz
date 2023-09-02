import threading
import time

import requests


class WebHookLogger:
    def __init__(self, url: str, username: str):
        self.url = url
        self.username = username
        self.running = False
        self._thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()


    def warning(self, message: str):
        """
        Sends a warning message to the webhook
        """
        self.send_message(message, "Warning", 0xFEE75C)


    def error(self, message: str):
        """
        Sends an error message to the webhook
        """
        self.send_message(message, "Error", 0xED4245)


    def info(self, message: str):
        """
        Sends an info message to the webhook
        """
        self.send_message(message, "Info", 0x57F287)


    def send_message(self, message: str, title: str, color: int):
        """
        Tries to send a message to the webhook, if it fails, it will try again with an exponential backoff
        """
        if not self.running:
            print("Webhook logger is not running")
            return

        data = {
            "username": self.username,
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": color,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                }
            ]
        }

        attempts = 0

        while attempts < 5:
            try:
                res = requests.post(self.url, json=data)
                res.raise_for_status()
                break
            except Exception as e:
                print("Error sending telemetry")
                print(e)
                attempts += 1
            time.sleep(2 ** attempts)
        else:
            print("Failed to send message")


    def run(self):
        try:
            while True:
                try:
                    self.info(f"{self.username} is still running")
                    print("Regular telemetry message sent")
                except Exception as e:
                    print("Error sending telemetry")
                    print(e)

                time.sleep(5 * 60)
        finally:
            self.running = False
