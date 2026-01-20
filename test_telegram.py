import sys
import os

# Add current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from common_modules.notification.telegram_bot import TelegramNotifier

def test_telegram():
    print("Initializing TelegramNotifier...")
    notifier = TelegramNotifier()
    
    if not notifier.token:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    if not notifier.chat_id:
        print("Error: TELEGRAM_CHAT_ID not found in environment variables.")
        return

    print(f"Token: {notifier.token[:5]}... (masked)")
    print(f"Chat ID: {notifier.chat_id}")

    message = "🔔 [TEST] Deep Value Bot: Telegram configuration test message."
    print("Sending test message...")
    notifier.send_message(message)
    print("Done.")

if __name__ == "__main__":
    test_telegram()
