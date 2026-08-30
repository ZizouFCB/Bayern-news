import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

WEBSITES_FILE = "websites.json"


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


def find_articles(html, base_url):

    soup = BeautifulSoup(html, "html.parser")

    articles = []

    for link in soup.find_all("a", href=True):

        text = link.get_text(" ", strip=True)

        if len(text) < 20:
            continue

        href = link["href"]

        if href.startswith("#"):
            continue

        full_url = urljoin(base_url, href)

        articles.append({
            "title": text,
            "url": full_url
        })

    # Remove duplicates
    unique = {}

    for article in articles:
        key = article["url"]

        if key not in unique:
            unique[key] = article

    return list(unique.values())


def main():

    with open(WEBSITES_FILE, encoding="utf-8") as file:
        websites = json.load(file)

    for site in websites:

        print("\n==============================")
        print(site["name"])
        print("==============================")

        try:

            html = get_page(site["url"])

            articles = find_articles(
                html,
                site["url"]
            )

            print("Possible articles:", len(articles))

            for article in articles[:30]:

                print(
                    "-",
                    article["title"],
                    "→",
                    article["url"]
                )

        except Exception as e:

            print("ERROR:", e)


if __name__ == "__main__":
    main()
