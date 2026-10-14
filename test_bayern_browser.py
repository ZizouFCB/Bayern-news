import requests

url = "https://fcbayern.com/graphql"

query = """
query {
  article(
    channelId: "fcbayern.com-de-de"
    id: "d2d3bd0a-129a-40b5-adf6-32ce0ec1d0b8"
  ) {
    id
    path
    pageTitle
    publicationDate
    lastModificationDate
    shortUrl
    contentBlocks {
      __typename
    }
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "ArenaAppAndroid"
}

print("TESTING FC BAYERN LIVETICKER CONTENT")

try:
    response = requests.post(
        url,
        json={"query": query},
        headers=headers,
        timeout=30
    )

    print("HTTP STATUS:", response.status_code)
    print("RESPONSE LENGTH:", len(response.text))
    print("RESPONSE:")
    print(response.text[:15000])

except Exception as e:
    print("ERROR:", str(e))
