"""
fetcher.py — Robust RSS fetcher with retries, timeouts, and tag passthrough.

NOTE: This file is intentionally NOT named inspect.py.
      Naming any project file inspect.py shadows Python's built-in
      inspect module and breaks the requests library.
"""

import time
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import config

log = logging.getLogger("fetcher")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"}


def _parse_pub_date(item) -> datetime:
    pub_el = item.find("pubDate")
    if pub_el is not None and pub_el.text:
        try:
            return parsedate_to_datetime(pub_el.text.strip()).astimezone(timezone.utc)
        except Exception:
            pass
    return datetime.now(timezone.utc)


def _parse_items(root, source_name: str, tags: list) -> list:
    """Extract article dicts from parsed XML root. Attaches feed tags to every article."""
    articles = []
    items = root.findall(".//item")[: config.ARTICLES_PER_FEED]
    for item in items:
        title_el = item.find("title")
        link_el  = item.find("link")
        guid_el  = item.find("guid")

        title = (title_el.text or "").strip() if title_el is not None else ""
        link  = (link_el.text  or "").strip() if link_el  is not None else ""
        guid  = (guid_el.text  or link).strip() if guid_el is not None else link

        if not title:
            continue

        articles.append({
            "title":      title,
            "link":       link,
            "guid":       guid,
            "source":     source_name,
            "tags":       tags,          # list e.g. ["market", "stocks", "india"]
            "fetched_at": _parse_pub_date(item),
        })
    return articles


def fetch_feed(feed: dict) -> list:
    """
    Fetch one RSS feed with exponential-backoff retry.
    Returns list of article dicts on success, [] on failure.
    """
    name = feed["name"]
    url  = feed["url"]
    tags = feed.get("tags", [])

    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=config.REQUEST_TIMEOUT_SEC)
            resp.raise_for_status()
            root     = ET.fromstring(resp.content)
            articles = _parse_items(root, name, tags)
            log.info(f"  [{name}] {len(articles)} articles | tags: {tags}")
            return articles

        except requests.exceptions.Timeout:
            log.warning(f"  [{name}] Timeout (attempt {attempt}/{config.MAX_RETRIES})")
        except requests.exceptions.ConnectionError:
            log.warning(f"  [{name}] Connection error (attempt {attempt}/{config.MAX_RETRIES})")
        except requests.exceptions.HTTPError as e:
            log.warning(f"  [{name}] HTTP {e.response.status_code} — skipping")
            return []
        except ET.ParseError:
            log.warning(f"  [{name}] XML parse error — skipping")
            return []
        except Exception as e:
            log.warning(f"  [{name}] Error: {e} (attempt {attempt}/{config.MAX_RETRIES})")

        if attempt < config.MAX_RETRIES:
            time.sleep(2 ** attempt)

    log.error(f"  [{name}] All {config.MAX_RETRIES} attempts failed. Skipping.")
    return []


def fetch_category(category: str) -> list:
    """Fetch every feed in a category. Returns merged article list."""
    feeds = config.FEEDS.get(category, [])
    all_articles = []
    for feed in feeds:
        all_articles.extend(fetch_feed(feed))
    return all_articles
