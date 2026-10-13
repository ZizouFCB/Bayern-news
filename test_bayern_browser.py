from playwright.sync_api import sync_playwright

print("TESTING FC BAYERN GERMAN WEBSITE")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(locale="de-DE")

    try:
        response = page.goto(
            "https://fcbayern.com/de",
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("HTTP STATUS:", response.status if response else "No response")
        print("PAGE TITLE:", page.title())
        print("NEWS LINKS:", page.locator("a[href*='/de/news/']").count())

    except Exception as e:
        print("BROWSER ERROR:", str(e))

    finally:
        browser.close()
