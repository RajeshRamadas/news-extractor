"""
main.py — News Extraction Bot entry point.
Run: python main.py

Fetches news from 14 RSS feeds every 5–30 min, deduplicates headlines,
identifies first breakers, and stores everything in news.db + news_feed.csv.
No posting, no external API keys required.
"""

import logging
import signal
import sys
import time

import storage
from logger import setup_logger
from scheduler import NewsScheduler

setup_logger()
log = logging.getLogger("main")


def _handle_shutdown(sig, frame):
    try:
        stats = storage.get_stats()
        log.info("Shutdown signal received — stopping bot.")
        log.info(f"Session summary: {stats['total']} articles saved | "
                 f"{stats['breakers']} breakers | "
                 f"{stats['duplicates']} duplicates")
        log.info(f"By category: {stats['by_category']}")
    except Exception:
        pass
    sys.exit(0)


signal.signal(signal.SIGINT,  _handle_shutdown)
signal.signal(signal.SIGTERM, _handle_shutdown)


if __name__ == "__main__":
    log.info("=" * 55)
    log.info("  News Extraction Bot — 24/7 Mode")
    log.info("  Outputs: news.db  +  news_feed.csv  +  logs/")
    log.info("=" * 55)

    storage.init_db()
    storage.init_csv()

    scheduler = NewsScheduler()
    scheduler.start()

    # Keep main thread alive; workers are daemon threads
    while True:
        time.sleep(60)
