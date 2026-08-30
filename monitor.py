import json
import requests
from bs4 import BeautifulSoup

WEBSITES_FILE = "websites.json"

def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()
    return response.text


def find_headlines(html):
    soup = BeautifulSoup(html, "html.parser")

    headlines = []

    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(" ", strip=True)

        if len(text) >= 15:
            headlines.append(text)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(headlines))


def main():

    websites = json.loads(
        open(WEBSITES_FILE, encoding="utf-8").read()
    )

    for site in websites:

        print("\n==============================")
        print(site["name"])
        print("==============================")

        try:

            html = get_page(site["url"])
            headlines = find_headlines(html)

            print("Headlines found:", len(headlines))

            for headline in headlines[:20]:
                print("-", headline)

        except Exception as e:

            print("ERROR:", e)


if __name__ == "__main__":
    main()
