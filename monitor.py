import requests

url = "https://www.kicker.de/fc-bayern-muenchen/team-news"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

print("STATUS:", response.status_code)
print("LENGTH:", len(response.text))

print("\nFIRST 1000 CHARACTERS:")
print(response.text[:1000])
