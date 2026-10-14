import requests
import json

url = "https://fcbayern.com/graphql"

query = """
query {
  __typename
}
"""

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "ArenaAppAndroid"
}

print("TESTING FC BAYERN GRAPHQL DISCOVERY")

try:
    response = requests.post(
        url,
        json={
            "operationName": "Discovery",
            "variables": {},
            "query": query
        },
        headers=headers,
        timeout=30
    )

    print("HTTP STATUS:", response.status_code)
    print("RESPONSE:")
    print(response.text[:1000])

except Exception as e:
    print("ERROR:", str(e))
