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
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()
    return response.text


def get_articles(html, site):
    soup = BeautifulSoup(html, "html.parser")

    articles = []
    seen = set()

    for link in soup.find_all("a", href=True):

        title = link.get_text(" ", strip=True)

        if len(title) < 25:
            continue

        href = link.get("href", "")

        if href.startswith("#"):
            continue

        if href.startswith("/"):
            from urllib.parse import urljoin
            url = urljoin(site["url"], href)
        else:
            url = href

        # BILD: Bayern football articles
        if site["name"] == "BILD Bayern":
            if "/sport/fussball/" not in url:
                continue
            if "fc-bayern" not in url.lower():
                continue

        # SPORT1: articles mentioning Bayern in the title
        # or articles specifically under the FC Bayern URL pattern
        elif site["name"] == "SPORT1 Bayern":
            if "/news/fussball/" not in url:
                continue

            combined = (title + " " + url).lower()

            if not any(word in combined for word in [
                "bayern",
                "fc-bayern",
                "münchen",
                "munich"
            ]):
                continue

        # TZ: entire FC Bayern section
        elif site["name"] == "tz Bayern":
            if "/sport/fc-bayern/" not in url:
                continue

        # Abendzeitung: Bayern sports section
        elif site["name"] == "Abendzeitung Bayern":
            if "/sport/fcbayern/" not in url:
                continue

        if url in seen:
            continue

        seen.add(url)

        articles.append({
            "title": title,
            "url": url
        })

    return articles


def load_state():
    if not Path(STATE_FILE).exists():
        return {}

    try:
        return json.loads(
            Path(STATE_FILE).read_text(encoding="utf-8")
        )
    except Exception:
        return {}


def save_state(state):
    Path(STATE_FILE).write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": message
        },
        timeout=30
    )

    response.raise_for_status()


def main():

    with open(WEBSITES_FILE, encoding="utf-8") as file:
        websites = json.load(file)

    state = load_state()

    for site in websites:

        name = site["name"]
        url = site["url"]

        print()
        print("==============================")
        print(name)
        print("==============================")

        try:

            html = get_page(url)

            articles = get_articles(
                html,
                site
            )

            print("Articles found:", len(articles))

            current_articles = {
                article["url"]: article["title"]
                for article in articles
            }

            old_articles = state.get(name, {})

            if not old_articles:

                print("Creating baseline.")

                state[name] = current_articles
                continue

            new_articles = []

            for article_url, title in current_articles.items():

                if article_url not in old_articles:
                    new_articles.append({
                        "title": title,
                        "url": article_url
                    })

            print("New articles:", len(new_articles))

            for article in reversed(new_articles):

                message = (
                    f"🆕 NEW BAYERN ARTICLE\n\n"
                    f"{name}\n\n"
                    f"{article['title']}\n\n"
                    f"{article['url']}"
                )

                send_telegram(message)

                print(
                    "Telegram notification sent:",
                    article["title"]
                )

            state[name] = current_articles

        except Exception as e:

            print(
                f"ERROR: {name}: {e}"
            )

    save_state(state)


if __name__ == "__main__":
    main()
