import requests

url = "https://fcbayern.com/graphql"

query = """
query {
  articles(
    channelId: "fcbayern.com-de-de"
    count: 20
    offset: 0
  ) {
    total
    count
    offset
    results {
      id
      path
      channelId
      channelPath
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

print("TESTING FC BAYERN GERMAN LATEST ARTICLES")

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
        articles = data["data"]["articles"]

        print("TOTAL:", articles["total"])
        print("COUNT:", articles["count"])
        print()

        for i, article in enumerate(articles["results"], 1):
            print("ARTICLE", i)
            print("TITLE:", article["pageTitle"])
            print("DATE:", article["publicationDate"])
            print("URL:", "https://fcbayern.com" + article["path"])
            print("SHORT URL:", article["shortUrl"])
            print("------------------------------")

except Exception as e:
    print("ERROR:", str(e))
