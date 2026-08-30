import json
import hashlib
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

WEBSITES_FILE = "websites.json"
STATE_FILE = "state.json"


def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()
    return response.text


def clean_page(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)

    return text


def make_hash(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def load_state():
    if not Path(STATE_FILE).exists():
        return {}

    return json.loads(
        Path(STATE_FILE).read_text()
    )


def save_state(state):
    Path(STATE_FILE).write_text(
        json.dumps(
            state,
            indent=2
        )
    )


def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": message
        },
        timeout=30
    )


def main():

    websites = json.loads(
        Path(WEBSITES_FILE).read_text()
    )

    state = load_state()

    for site in websites:

        name = site["name"]
        url = site["url"]

        print(f"Checking {name}...")

        try:

            html = get_page(url)
            text = clean_page(html)
            current_hash = make_hash(text)

            old_hash = state.get(url)

            if old_hash is None:

                print(f"Creating baseline for {name}")

                state[url] = current_hash

            elif old_hash != current_hash:

                print(f"CHANGE DETECTED: {name}")

                send_telegram(
                    f"🔴 CHANGE DETECTED\n\n"
                    f"{name}\n\n"
                    f"{url}"
                )

                state[url] = current_hash

            else:

                print(f"No change: {name}")

        except Exception as e:

            print(f"ERROR: {name}: {e}")

    save_state(state)


if __name__ == "__main__":
    main()
