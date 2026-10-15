import requests
from bs4 import BeautifulSoup

url = "https://fcbayern.com/graphql"

query = """
query {
  article(
    channelId: "fcbayern.com-de-de"
    id: "d2d3bd0a-129a-40b5-adf6-32ce0ec1d0b8"
  ) {
    lastModificationDate
    contentBlocks {
      __typename
      ... on History {
        entries {
          header
          title
          content {
            __typename
            ... on MarkdownText {
              contentHtml {
                html
              }
            }
          }
        }
      }
    }
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "ArenaAppAndroid"
}

print("TESTING FC BAYERN LIVETICKER NEWEST ENTRY")

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
        article = data["data"]["article"]

        for block in article["contentBlocks"]:
            if block.get("__typename") == "History":

                entries = block["entries"]

                if not entries:
                    print("NO ENTRIES FOUND")
                else:
                    newest = entries[0]

                    print()
                    print("NEWEST ENTRY")
                    print("HEADER:", newest["header"])
                    print("TITLE:", newest["title"])

                    for content in newest["content"]:
                        if content.get("__typename") == "MarkdownText":
                            html = content["contentHtml"]["html"]

                            soup = BeautifulSoup(
                                html,
                                "html.parser"
                            )

                            text = soup.get_text(
                                " ",
                                strip=True
                            )

                            print("TEXT:", text)

                    print()
                    print("TOTAL ENTRIES:", len(entries))
                    print("LAST MODIFIED:", article["lastModificationDate"])

except Exception as e:
    print("ERROR:", str(e))
