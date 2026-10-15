import requests
import json

url = "https://fcbayern.com/graphql"

query = """
query {
  article(
    channelId: "fcbayern.com-de-de"
    id: "d2d3bd0a-129a-40b5-adf6-32ce0ec1d0b8"
  ) {
    id
    pageTitle
    lastModificationDate
    contentBlocks {
      __typename
      ... on History {
        id
        title
        subtitle
        entries {
          header
          title
          content {
            __typename
            ... on MarkdownText {
              id
              contentBlockType
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

print("TESTING FC BAYERN LIVETICKER ENTRIES")

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

    data = response.json()

    if "errors" in data:
        print(json.dumps(data["errors"], indent=2, ensure_ascii=False))
    else:
        article = data["data"]["article"]

        print("TITLE:", article["pageTitle"])
        print("LAST MODIFIED:", article["lastModificationDate"])
        print()

        for block in article["contentBlocks"]:
            if block.get("__typename") == "History":
                print("HISTORY BLOCK:", block["id"])
                print("HISTORY TITLE:", block["title"])
                print()

                for i, entry in enumerate(block["entries"], 1):
                    print("ENTRY", i)
                    print("HEADER:", entry["header"])
                    print("TITLE:", entry["title"])

                    for content in entry["content"]:
                        if content.get("__typename") == "MarkdownText":
                            html = content.get("contentHtml")

                            if html:
                                print("HTML:", html["html"])

                    print("------------------------------")

except Exception as e:
    print("ERROR:", str(e))
