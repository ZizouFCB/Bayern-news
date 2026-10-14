import requests

url = "https://fcbayern.com/graphql"

query = """
query {
  newsOverview(channelId: "fcbayern.com-de-de") {
    id
    path
    pageTitle
    widgetFeatures
    filterTags
    filterSections
    filterTypes
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "ArenaAppAndroid"
}

print("TESTING FC BAYERN GERMAN NEWS PAGE")

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
    print(response.text[:10000])

except Exception as e:
    print("ERROR:", str(e))
