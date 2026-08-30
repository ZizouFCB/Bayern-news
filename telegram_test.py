import os
import requests

token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]

url = f"api.telegram.org/bot{token}/sendMessage"

response = requests.post(
url,
data={
"chat_id": chat_id,
"text": "✅ GitHub → Telegram connection works!"
},
timeout=30
)

print(response.text)
