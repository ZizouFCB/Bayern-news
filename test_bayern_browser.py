import requests

url = "https://fcbayern.com/graphql"

query = """
query {
  __schema {
    queryType {
      fields {
        name
        args {
          name
          type {
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

print("TESTING FC BAYERN GRAPHQL ARGUMENTS")

try:
    response = requests.post(
        url,
        json={"query": query},
        headers=headers,
        timeout=30
    )

    print("HTTP STATUS:", response.status_code)
    print("RESPONSE LENGTH:", len(response.text))

    data = response.json()

    for field in data["data"]["__schema"]["queryType"]["fields"]:
        if field["name"] in [
            "newsOverview",
            "newsSearch",
            "contentlist",
            "articles",
            "updates"
        ]:
            print()
            print("FIELD:", field["name"])

            for arg in field["args"]:
                print("  ARG:", arg["name"], "TYPE:", arg["type"])

except Exception as e:
    print("ERROR:", str(e))
