import json
import requests
from bs4 import BeautifulSoup

with open("websites.json", encoding="utf-8") as f:
    websites = json.load(f)

for site in websites:

    if site["name"] != "Abendzeitung Bayern":
        continue

    print("URL:", site["url"])

    response = requests.get(
        site["url"],
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    print("STATUS:", response.status_code)
    print("LENGTH:", len(response.text))

    soup = BeautifulSoup(response.text, "html.parser")

    print(
        "PAGE TITLE:",
        soup.title.get_text(strip=True)
        if soup.title
        else "NONE"
    )

    print("\nFIRST 20 LINKS:")

    for link in soup.find_all("a", href=True)[:20]:

        text = link.get_text(" ", strip=True)

        if text:
            print("TEXT:", text[:150])
            print("URL:", link["href"])
            print()
