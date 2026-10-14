import requests

url = "https://fcbayern.com/graphql"

query = """
query {
  __schema {
    queryType {
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

print("TESTING FC BAYERN CHANNEL TYPE")

try:
    response = requests.post(
        url,
        json={"query": query},
        headers=headers,
        timeout=30
    )

    print("HTTP STATUS:", response.status_code)

    data = response.json()

    for field in data["data"]["__schema"]["queryType"]["fields"]:
        if field["name"] in ["channels", "newsOverview", "newsSearch", "articles"]:
            print()
            print("FIELD:", field["name"])
            print("TYPE:", field["type"])

except Exception as e:
    print("ERROR:", str(e))
