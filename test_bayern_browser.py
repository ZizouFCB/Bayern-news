import requests

url = "https://fcbayern.com/graphql"

query = """
query {
  __type(name: "HistoryContent") {
    name
    kind
    possibleTypes {
      name
      fields {
        name
        type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
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

print("TESTING FC BAYERN HISTORY CONTENT")

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
