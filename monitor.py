import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

WEBSITES_FILE = "websites.json"
STATE_FILE = "state.json"


def get_page(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        )
    }

    if "fcbayern.com" in url:
        headers["Accept-Language"] = "de-DE,de;q=0.9"
        headers["Referer"] = "https://www.google.com/"
        
    if "sport.sky.de" in url:
        headers["Accept-Language"] = "de-DE,de;q=0.9"
        headers["Referer"] = "https://www.google.com/"
    
    request_url = url

    if "sport.sky.de" in url:
        request_url = f"https://r.jina.ai/{url}"

    if "sport.sky.de" in url:
        headers["X-No-Cache"] = "true"

    print("TESTING FC BAYERN DIRECT:", request_url)
    
    response = requests.get(
        request_url,
        headers=headers,
        timeout=60
)

    response.raise_for_status()
    return response.text

def get_fcbayern_german_articles():
    url = "https://fcbayern.com/graphql"

    query = """
    query {
      articles(
        channelId: "fcbayern.com-de-de"
        count: 20
        offset: 0
      ) {
        results {
          id
          path
          pageTitle
          publicationDate
          lastModificationDate
        }
      }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "ArenaAppAndroid"
    }

    response = requests.post(
        url,
        json={"query": query},
        headers=headers,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(
            f"FC Bayern GraphQL error: {data['errors']}"
        )

    results = data["data"]["articles"]["results"]

    articles = []

    for article in results:

        article_id = article.get("id")
        title = article.get("pageTitle")
        path = article.get("path")
        publication_date = article.get("publicationDate")

        if not article_id or not title or not path:
            continue

        # The permanent Liveticker is handled separately.
        if path == "/de/news/fc-bayern-liveticker-alle-infos-rund-um-unsere-profis":
            continue

        if not publication_date:
            continue

        article_url = urljoin(
            "https://fcbayern.com",
            path
        )

        articles.append({
            "id": article_id,
            "title": title,
            "url": article_url,
            "publicationDate": publication_date
        })

    return articles

def get_fcbayern_liveticker():
    url = "https://fcbayern.com/graphql"

    query = """
    query {
      article(
        channelId: "fcbayern.com-de-de"
        id: "d2d3bd0a-129a-40b5-adf6-32ce0ec1d0b8"
      ) {
        pageTitle
        lastModificationDate
        contentBlocks {
          __typename

          ... on History {
            entries {
              header
              title

              content {
                __typename

                ... on MarkdownText {
                  contentHtml {
                    html
                  }
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

    response = requests.post(
        url,
        json={"query": query},
        headers=headers,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(
            f"FC Bayern Liveticker GraphQL error: {data['errors']}"
        )

    article = data["data"]["article"]

    if not article:
        return None

    for block in article.get("contentBlocks", []):

        if block.get("__typename") != "History":
            continue

        entries = block.get("entries", [])

        if not entries:
            return None

        newest = entries[0]

        title = newest.get("title") or ""
        header = newest.get("header") or ""

        text_parts = []

        for content in newest.get("content", []):

            if content.get("__typename") != "MarkdownText":
                continue

            content_html = content.get("contentHtml")

            if not content_html:
                continue

            html = content_html.get("html", "")

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            text = soup.get_text(
                " ",
                strip=True
            )

            if text:
                text_parts.append(text)

        text = " ".join(text_parts).strip()

        fingerprint = (
            f"{header}|{title}|{text}"
        )

        return {
            "header": header,
            "title": title,
            "text": text,
            "fingerprint": fingerprint,
            "url": (
                "https://fcbayern.com"
                "/de/news/"
                "fc-bayern-liveticker-"
                "alle-infos-rund-um-unsere-profis"
            )
        }

    return None


def is_bayern_article(title, url):
    text = (title + " " + url).lower()

    keywords = [
        "bayern",
        "fc bayern",
        "fcb",
        "münchen",
        "munich",
        "kompany",
        "eberl",
        "kane",
        "neuer",
        "upamecano",
        "kim min-jae",
        "olise",
        "musiala",
        "gnabry",
        "sane",
        "sané",
        "goretzka",
        "kimmich",
        "pavlovic",
        "pavlović",
        "davies",
        "laimer",
        "stanišić",
        "díaz",
        "diaz",
        "saibari",
        "brown",
        "tah",
        "jackson",
        "bischof"
    ]

    return any(keyword in text for keyword in keywords)


def get_articles(html, site):
    
    if site["name"] == "FC Bayern Official":
        articles = []
        print("FC BAYERN RAW SAMPLE:")
        print(html[:5000])
        seen = set()

        pattern = r'\[([^\]]+)\]\((https://fcbayern\.com/de/[^)\s]+)'

        excluded_paths = [
            "/de",
            "/de/",
            "/de/kontakt",
            "/de/tickets",
            "/de/shop",
            "/de/club",
            "/de/fans",
            "/de/teams",
            "/de/match-center",
            "/de/leichte-sprache",
        ]

        for match in re.finditer(pattern, html):
            title = match.group(1).strip()
            url = match.group(2).strip()

            if url in seen:
                continue

            if len(title) < 15:
                continue

            path = urlparse(url).path.lower()

            if any(path == excluded or path.startswith(excluded + "/")
                   for excluded in excluded_paths):
                continue

            if (
                "/de/news/" not in path
                and "/fcbayerntv/" not in path
            ):
                continue

            seen.add(url)

            articles.append({
                "title": title,
                "url": url
            })

        return articles

    if site["name"] == "Kicker Bayern":
        import xml.etree.ElementTree as ET

        articles = []
        seen = set()

        root = ET.fromstring(html)

        for item in root.findall(".//item"):
            title_tag = item.find("title")
            link_tag = item.find("link")

            if title_tag is None or link_tag is None:
                continue

            title = title_tag.text or ""
            article_url = link_tag.text or ""

            title = title.strip()
            article_url = article_url.strip()

            if not title or not article_url:
                continue

            if article_url in seen:
                continue

            seen.add(article_url)

            articles.append({
                "title": title,
                "url": article_url
            })

        print("Kicker items found:", len(articles))

        for article in articles:
            print("KICKER ITEM:", article["title"], "=>", article["url"])

        return articles

    if site["name"] == "NewsNow Bayern":
        articles = []
        seen = set()

        soup = BeautifulSoup(html, "html.parser")

        articles = []
        seen = set()

        for link in soup.find_all("a", href=True):
            href = link.get("href", "").strip()
            title = link.get_text(" ", strip=True)

            if "c.newsnow.co.uk" not in href.lower():
                continue

            if len(title) < 20:
                continue

            if href in seen:
                continue

            seen.add(href)

            articles.append({
                "title": title,
                "url": href
            })

        print("NewsNow Latest articles found:", len(articles))

        return articles
                
        latest_heading = soup.find(
            lambda tag:
            tag.name in ["h1", "h2", "h3", "h4", "div", "span"]
            and tag.get_text(" ", strip=True).lower() == "latest"
        )

        if latest_heading:
            latest_section = latest_heading

            for _ in range(5):
                latest_section = latest_section.parent
                if latest_section is None:
                    break

                links = latest_section.find_all("a", href=True)

                valid_links = []
                for link in links:
                    title = link.get_text(" ", strip=True)
                    href = link.get("href", "").strip()

                    if len(title) < 20:
                        continue

                    if not href:
                        continue

                    if href.startswith("/"):
                        href = urljoin(
                            "https://www.newsnow.co.uk",
                            href
                        )

                    if href in seen:
                        continue

                    if "/h/" in href:
                        continue

                    if "newsnow.co.uk" not in href.lower():
                        continue

                    valid_links.append((title, href))

                if len(valid_links) >= 2:
                    for title, href in valid_links:
                        seen.add(href)

                        articles.append({
                            "title": title,
                            "url": href
                        })

                    break

        print("NewsNow Latest articles found:", len(articles))

        return articles  

    if site["name"] == "Sky Bayern":
    
        articles = []
        seen = set()

        pattern = r'\[([^\]]+)\]\((https://sport\.sky\.de/fussball/artikel/[^)]+)\)'

        for match in re.finditer(pattern, html, re.DOTALL):
            title = match.group(1).strip()
            url = match.group(2).strip()

            if len(title) < 20:
                continue

            if url in seen:
                continue

            seen.add(url)

            articles.append({
                "title": title,
                "url": url
            })

        return articles
        
    soup = BeautifulSoup(html, "html.parser")

    articles = []
    seen = set()

    for link in soup.find_all("a", href=True):

        title = link.get_text(" ", strip=True)

        if len(title) < 25:
            continue

        href = link.get("href", "").strip()

        if not href or href.startswith("#"):
            continue

        url = urljoin(site["url"], href)

        name = site["name"]

        # Footy Headlines Germany
        if name == "Footy Headlines Germany":
            path = urlparse(url).path

            if not re.match(r"^/\d+/.+\.html$", path):
                continue

        # Footy Headlines Bayern
        if name == "Footy Headlines Bayern":
            path = urlparse(url).path

            if not re.match(r"^/\d+/.+\.html$", path):
                continue

        # BILD Bayern
        if name == "BILD Bayern":
            if "/sport/fussball/" not in url:
                continue
            if "fc-bayern" not in url.lower() and "bayern-muenchen" not in url.lower():
                continue

        # BILD FUSSBALL
        elif name == "BILD FUSSBALL":
            if "/sport/fussball/" not in url.lower():
                continue

        # SPORT1 Bayern
        elif name == "SPORT1 Bayern":
            pass

        # SPORT2
        elif name == "SPORT2":
            path = urlparse(url).path.lower()

            if "/news/fussball/" not in path and "/tv-video/video/" not in path:
                continue

        # SPORT DE
        elif name == "SPORT DE":
            path = urlparse(url).path.lower()
            if "/news/" not in path:
                continue

        # TZ Bayern
        elif name == "tz Bayern":
            if "/sport/fc-bayern/" not in url:
                continue

        # Abendzeitung Bayern
        elif name == "Abendzeitung Bayern":
            if "/sport/fcbayern/" not in url:
                continue

        # SZ Bayern
        elif name == "SZ Bayern":
            path = urlparse(url).path.lower()

            if "/gutscheine/" in path:
                continue

        if url in seen:
            continue

        # T-Online Bayern
        elif name == "T-Online Bayern":
            path = urlparse(url).path.lower()

            if "/sport/fussball/bundesliga/fc-bayern-muenchen/" not in path:
                continue

        seen.add(url)

        articles.append({
            "title": title,
            "url": url
        })

    return articles


def load_state():
    if not Path(STATE_FILE).exists():
        return {}

    try:
        return json.loads(
            Path(STATE_FILE).read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return {}


def save_state(state):
    Path(STATE_FILE).write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": message
        },
        timeout=30
    )

    response.raise_for_status()


def main():

    with open(
        WEBSITES_FILE,
        encoding="utf-8"
    ) as file:
        websites = json.load(file)

    state = load_state()

    notified_urls = set(state.get("_notified_urls", []))

    # FC Bayern German website - GraphQL monitor
    try:
        print()
        print("==============================")
        print("FC Bayern Official - German")
        print("==============================")

        fcb_articles = get_fcbayern_german_articles()

        print(
            "FC Bayern articles found:",
            len(fcb_articles)
        )

        old_fcb = state.get(
            "FC Bayern Official",
            {}
        )

        if not old_fcb:
            print("Creating FC Bayern baseline.")

            state["FC Bayern Official"] = {
                article["url"]: article["title"]
                for article in fcb_articles
            }

        else:
            new_fcb_articles = []

            for article in fcb_articles:

                article_url = article["url"]

                if (
                    article_url not in old_fcb
                    and article_url not in notified_urls
                ):
                    new_fcb_articles.append(article)

            print(
                "New FC Bayern articles:",
                len(new_fcb_articles)
            )

            for article in reversed(new_fcb_articles):

                article_url = article["url"]

                # Mark URL as notified BEFORE sending.
                # This prevents the same URL from being sent again
                # if another workflow run starts unexpectedly.
                notified_urls.add(article_url)

                state["_notified_urls"] = list(notified_urls)
                save_state(state)

                message = (
                    "🆕 NEW BAYERN ARTICLE\n\n"
                    f"{name}\n\n"
                    f"{article['title']}\n\n"
                    f"{article_url}"
                )

                send_telegram(message)

                print(
                    "Telegram notification sent:",
                    article["title"]
                )

            state["FC Bayern Official"] = {
                article["url"]: article["title"]
                for article in fcb_articles
            }

    except Exception as e:

        print(
            f"ERROR: FC Bayern Official: {e}"
        )

    # FC Bayern permanent Liveticker monitor
    try:
        print()
        print("==============================")
        print("FC Bayern Liveticker")
        print("==============================")

        liveticker = get_fcbayern_liveticker()

        if not liveticker:
            print("No Liveticker entry found.")

        else:
            old_liveticker = state.get(
                "_fcbayern_liveticker",
                {}
            )

            fingerprint = liveticker["fingerprint"]

            if not old_liveticker:

                print(
                    "Creating Liveticker baseline."
                )

                state["_fcbayern_liveticker"] = {
                    "fingerprint": fingerprint
                }

            elif (
                fingerprint
                != old_liveticker.get("fingerprint")
            ):

                message = (
                    "🆕 FC BAYERN LIVETICKER UPDATE\n\n"
                    f"{liveticker['header']}\n"
                    f"{liveticker['title']}\n\n"
                    f"{liveticker['text']}\n\n"
                    f"{liveticker['url']}"
                )

                send_telegram(message)

                print(
                    "Telegram Liveticker notification sent:",
                    liveticker["title"]
                )

                state["_fcbayern_liveticker"] = {
                    "fingerprint": fingerprint
                }

            else:

                print(
                    "No new Liveticker update."
                )

    except Exception as e:

        print(
            f"ERROR: FC Bayern Liveticker: {e}"
        )

    for site_state in state.values():
        if isinstance(site_state, dict):
            notified_urls.update(site_state.keys())

    for site in websites:

        name = site["name"]
        url = site["url"]

        print()
        print("==============================")
        print(name)
        print("==============================")

        try:

            html = get_page(url)

            articles = get_articles(
                html,
                site
            )

            print(
                "Articles found:",
                len(articles)
            )

            current_articles = {
                article["url"]: article["title"]
                for article in articles
            }

            old_articles = state.get(
                name,
                {}
            )

            if not old_articles:

                print("Creating baseline.")

                state[name] = current_articles
                continue

            new_articles = []

            for article_url, title in current_articles.items():

                if article_url not in old_articles and article_url not in notified_urls:
               
                    new_articles.append({
                    "title": title,
                    "url": article_url
                })

            print(
                "New articles:",
                len(new_articles)
            )

            for article in reversed(new_articles):

                message = (
                    "🆕 NEW BAYERN ARTICLE\n\n"
                    f"{name}\n\n"
                    f"{article['title']}\n\n"
                    f"{article['url']}"
                )

                send_telegram(message)

                notified_urls.add(article["url"])

                print(
                    "Telegram notification sent:",
                    article["title"]
                )

            state[name] = current_articles

        except Exception as e:

            print(
                f"ERROR: {name}: {e}"
            )

    state["_notified_urls"] = list(notified_urls)

    save_state(state)


if __name__ == "__main__":
    main()
