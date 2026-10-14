import requests

urls = [
    "https://fcbayern.com/de/page-data.json",
    "https://fcbayern.com/page-data/de/page-data.json",
]

for url in urls:
    print("\nTESTING:", url)

    try:
        response = requests.get(url, timeout=20)
        print("STATUS:", response.status_code)
        print("CONTENT TYPE:", response.headers.get("content-type"))
        print("RESPONSE:", response.text[:300].replace("\n", " "))
    except Exception as e:
        print("ERROR:", str(e))
