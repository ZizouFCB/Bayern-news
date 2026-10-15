import requests

url = "https://fcbayern.com/graphql"

query = """
query {
  __type(name: "HistoryEntry") {
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

print("TESTING FC BAYERN HISTORY ENTRY FIELDS")

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
