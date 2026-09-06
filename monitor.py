import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

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

    if "fcbayern.com" in url:
        headers["Accept-Language"] = "de-DE,de;q=0.9"
        headers["Referer"] = "https://www.google.com/"
        
    if "sport.sky.de" in url:
        headers["Accept-Language"] = "de-DE,de;q=0.9"
        headers["Referer"] = "https://www.google.com/"
    
    request_url = url

    if "sport.sky.de" in url:
        request_url = f"https://r.jina.ai/{url}"

    if "sport.sky.de" in url:
        headers["X-No-Cache"] = "true"

    response = requests.get(
        request_url,
        headers=headers,
        timeout=60
)

    response.raise_for_status()
    return response.text


def is_bayern_article(title, url):
    text = (title + " " + url).lower()

    keywords = [
        "bayern",
        "fc bayern",
        "fcb",
        "münchen",
        "munich",
        "kompany",
        "eberl",
        "kane",
        "neuer",
        "upamecano",
        "kim min-jae",
        "olise",
        "musiala",
        "gnabry",
        "sane",
        "sané",
        "goretzka",
        "kimmich",
        "pavlovic",
        "pavlović",
        "davies",
        "laimer",
        "stanišić",
        "díaz",
        "diaz",
        "saibari",
        "brown",
        "tah",
        "jackson",
        "bischof"
    ]

    return any(keyword in text for keyword in keywords)


def get_articles(html, site):
    if site["name"] == "FC Bayern Official":
        print("LINES CONTAINING FC BAYERN NEWS:")

        for line in html.splitlines():
            if "fcbayern.com/de/news/" in line:
                print(line[:1000])

        return []

    if site["name"] == "Sky Bayern":
        import re

        articles = []
        seen = set()

        pattern = r'\[([^\]]+)\]\((https://sport\.sky\.de/fussball/artikel/[^)]+)\)'

        for match in re.finditer(pattern, html, re.DOTALL):
            title = match.group(1).strip()
            url = match.group(2).strip()

            if len(title) < 20:
                continue

            if url in seen:
                continue

            seen.add(url)

            articles.append({
                "title": title,
                "url": url
            })

        return articles
        
    soup = BeautifulSoup(html, "html.parser")

    articles = []
    seen = set()

    for link in soup.find_all("a", href=True):

        title = link.get_text(" ", strip=True)

        if len(title) < 25:
            continue

        href = link.get("href", "").strip()

        if not href or href.startswith("#"):
            continue

        url = urljoin(site["url"], href)

        name = site["name"]

        # BILD Bayern
        if name == "BILD Bayern":
            if "/sport/fussball/" not in url:
                continue
            if "fc-bayern" not in url.lower() and "bayern-muenchen" not in url.lower():
                continue

        # BILD FUSSBALL
        elif name == "BILD FUSSBALL":
            if "/sport/fussball/" not in url.lower():
                continue

        # SPORT1 Bayern
        elif name == "SPORT1 Bayern":
            pass

        # SPORT2
        elif name == "SPORT2":
            path = urlparse(url).path.lower()

            if "/news/fussball/" not in path and "/tv-video/video/" not in path:
                continue

        # TZ Bayern
        elif name == "tz Bayern":
            if "/sport/fc-bayern/" not in url:
                continue

        # Abendzeitung Bayern
        elif name == "Abendzeitung Bayern":
            if "/sport/fcbayern/" not in url:
                continue

        # SZ Bayern
        elif name == "SZ Bayern":
            path = urlparse(url).path.lower()

            if "/gutscheine/" in path:
                continue

        if url in seen:
            continue

        # T-Online Bayern
        elif name == "T-Online Bayern":
            path = urlparse(url).path.lower()

            if "/sport/fussball/bundesliga/fc-bayern-muenchen/" not in path:
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
            Path(STATE_FILE).read_text(
                encoding="utf-8"
            )
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

    with open(
        WEBSITES_FILE,
        encoding="utf-8"
    ) as file:
        websites = json.load(file)

    state = load_state()

    notified_urls = set()

    for site_state in state.values():
        if isinstance(site_state, dict):
            notified_urls.update(site_state.keys())

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

            print(
                "Articles found:",
                len(articles)
            )

            current_articles = {
                article["url"]: article["title"]
                for article in articles
            }

            old_articles = state.get(
                name,
                {}
            )

            if not old_articles:

                print("Creating baseline.")

                state[name] = current_articles
                continue

            new_articles = []

            for article_url, title in current_articles.items():

                if article_url not in old_articles and article_url not in notified_urls:
               
                new_articles.append({
                "title": title,
                "url": article_url
                })

            print(
                "New articles:",
                len(new_articles)
            )

            for article in reversed(new_articles):

                message = (
                    "🆕 NEW BAYERN ARTICLE\n\n"
                    f"{name}\n\n"
                    f"{article['title']}\n\n"
                    f"{article['url']}"
                )

                send_telegram(message)

                notified_urls.add(article["url"])

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
