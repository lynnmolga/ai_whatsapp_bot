import time
import requests
from whatsapp_connect import open_whatsapp, get_last_message, send_message

API_URL = "http://localhost:8000/draft"
CHAT_NAME = "Mom"

def main():
    open_whatsapp()
    last_seen = None
    print("Bot started...")
    while True:
        msg = get_last_message(CHAT_NAME)
        if msg and msg != last_seen:
            last_seen = msg
            print("New message:", msg)
            print("Sending to AI...")
            response = requests.post(
                API_URL,
                json={
                    "sender": CHAT_NAME,
                    "message": msg,
                },
                timeout=300,
            )
            data = response.json()
            print("AI response:", data)
            if data.get("should_reply"):
                reply = data.get("best_reply") or data.get("draft")
                print("Suggested reply:", reply)
                confirm = input("Send? (y/n): ")
                if confirm.lower() == "y":
                    send_message(reply)
        time.sleep(5)


if __name__ == "__main__":
    main()