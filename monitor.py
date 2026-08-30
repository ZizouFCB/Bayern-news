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
    seen = set()

    for link in soup.find_all("a", href=True):

        title = link.get_text(" ", strip=True)

        if len(title) < 25:
            continue

        url = urljoin(base_url, link["href"])

        if url in seen:
            continue

        seen.add(url)

        articles.append({
            "title": title,
            "url": url
        })

    return articles


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

            # Show only the first 15.
            for article in articles[:15]:

                print()
                print("TITLE:", article["title"])
                print("URL:", article["url"])

        except Exception as e:

            print("ERROR:", e)


if __name__ == "__main__":
    main()
