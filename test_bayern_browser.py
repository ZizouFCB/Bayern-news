import requests

url = "https://fcbayern.com/graphql"

query = """
query {
  articles(
    channelId: "fcbayern.com-de-de"
    count: 20
    offset: 0
  ) {
    results {
      id
      path
      pageTitle
      publicationDate
      lastModificationDate
      shortUrl
    }
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "ArenaAppAndroid"
}

print("FINDING FC BAYERN LIVETICKER ID")

try:
    response = requests.post(
        url,
        json={"query": query},
        headers=headers,
        timeout=30
    )

    print("HTTP STATUS:", response.status_code)

    data = response.json()

    if "errors" in data:
        print("GRAPHQL ERRORS:", data["errors"])
    else:
        for article in data["data"]["articles"]["results"]:
            if "Liveticker" in (article.get("pageTitle") or ""):
                print()
                print("FOUND LIVETICKER")
                print("ID:", article["id"])
                print("TITLE:", article["pageTitle"])
                print("PATH:", article["path"])
                print("DATE:", article["publicationDate"])
                print("LAST MODIFIED:", article["lastModificationDate"])
                print("SHORT URL:", article["shortUrl"])

except Exception as e:
    print("ERROR:", str(e))
