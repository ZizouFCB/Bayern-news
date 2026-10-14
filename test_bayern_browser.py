import requests
import json

url = "https://fcbayern.com/graphql"

query = """
query ContentList($channelId: String!, $id: ID!, $filter: [String]) {
  contentlist(
    channelId: $channelId
    id: $id
    filterTags: $filter
    count: 10
    offset: 0
  ) {
    __typename
    count
    offset
    total
    results {
      __typename
      channelId
      id
      publicationDate
      teaserTitle
      teaserSubtitle
      teaserText
      teaserLink {
        __typename
        title
        target {
          __typename
          ... on InternalLink {
            channelId
            channelPath
            id
            locale
            pageType
            path
          }
          ... on ExternalLink {
            url
          }
        }
      }
    }
  }
}
"""

payload = {
    "operationName": "ContentList",
    "variables": {
        "channelId": "allianz-arena-en-gb",
        "id": "bd7202b0-dd86-4c2e-aab4-e631b613874f"
    },
    "query": query
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "ArenaAppAndroid"
}

print("TESTING FC BAYERN GRAPHQL")
print("URL:", url)

try:
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30
    )

    print("HTTP STATUS:", response.status_code)
    print("RESPONSE LENGTH:", len(response.text))
    print("RESPONSE START:")
    print(response.text[:2000])

except Exception as e:
    print("GRAPHQL ERROR:", str(e))
