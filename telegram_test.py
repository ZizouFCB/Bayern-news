import os
import requests

token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if not token or not chat_id:
    raise SystemExit("Telegram credentials are missing.")

response = requests.post(
    "https://api.telegram.org/bot" + token + "/sendMessage",
    data={
        "chat_id": chat_id,
        "text": "✅ GitHub → Telegram connection works!"
    },
    timeout=30
)

print(response.text)
