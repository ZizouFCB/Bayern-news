from playwright.sync_api import sync_playwright

url = "https://www.kicker.de/fc-bayern-muenchen/team-news"

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    )

    print("Opening Kicker...")

    response = page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000
    )

    print("HTTP STATUS:", response.status if response else "NONE")

    page.wait_for_timeout(5000)

    print("PAGE TITLE:", page.title())

    text = page.locator("body").inner_text()

    print("TEXT LENGTH:", len(text))

    print("\nFIRST 3000 CHARACTERS:")
    print(text[:3000])

    browser.close()
