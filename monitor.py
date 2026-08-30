import requests

url = "https://www.sport1.de/team/fc-bayern-muenchen/opta_156"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)
print("Characters received:", len(response.text))
print(response.text[:500])
