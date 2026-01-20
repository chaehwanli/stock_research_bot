import os
import telebot
from dotenv import load_dotenv

# Load .env from project root
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(env_path)

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = None
        
        if self.token:
            self.bot = telebot.TeleBot(self.token)
        else:
            print("Warning: TELEGRAM_BOT_TOKEN not found.")

    def send_message(self, message):
        """
        Sends a text message to the configured chat ID.
        """
        if not self.bot or not self.chat_id:
            print("Telegram not configured. Message not sent.")
            print(f"Content: {message[:50]}...")
            return

        try:
            # Telegram has a message length limit (4096 chars). Split if needed.
            if len(message) > 4000:
                chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
                for chunk in chunks:
                    self.bot.send_message(self.chat_id, chunk)
            else:
                self.bot.send_message(self.chat_id, message)
            print("Telegram message sent.")
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

    def send_file(self, file_path):
        if not self.bot or not self.chat_id:
            return
        
        try:
            with open(file_path, 'rb') as f:
                self.bot.send_document(self.chat_id, f)
            print("File sent via Telegram.")
        except Exception as e:
            print(f"Failed to send file: {e}")
