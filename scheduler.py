"""
scheduler.py — Launches one background worker thread per feed category.
All categories (market, national, global) run 24/7 with no time restrictions.
"""

import logging
import threading
import time
from datetime import datetime, timezone, timedelta

import config
import fetcher
import deduplicator
import storage

log = logging.getLogger("scheduler")

IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist() -> datetime:
    return datetime.now(IST)


def _run_cycle(category: str):
    """One complete fetch → deduplicate → store cycle for a category."""
    log.info(f"\n[{category.upper()}] Extraction cycle — {_now_ist().strftime('%H:%M:%S IST')}")

    # 1. Fetch raw articles
    articles = fetcher.fetch_category(category)
    if not articles:
        log.info("  No articles fetched.")
        return

    log.info(f"  Fetched {len(articles)} raw articles")

    # 2. Deduplicate + tag breakers
    result = deduplicator.process_articles(articles)

    # 3. Store new + duplicates (full audit trail)
    all_tagged = result["to_publish"] + result["duplicates"]
    storage.store(all_tagged, category)

    # 4. Log breaker leaderboard on market cycles
    if category == "market":
        board = deduplicator.get_breaker_leaderboard()
        if board:
            log.info("  Breaker leaderboard (session):")
            for rank, (src, cnt) in enumerate(board[:5], 1):
                log.info(f"    #{rank} {src}: {cnt} first breaks")

    # 5. DB summary
    stats = storage.get_stats()
    log.info(
        f"  DB: {stats['total']} total | "
        f"{stats['breakers']} breakers | "
        f"{stats['duplicates']} duplicates"
    )
    log.info(f"[{category.upper()}] Done.")


def _loop(category: str, interval_minutes: int):
    """Infinite loop: run one cycle, sleep, repeat."""
    log.info(f"  Worker [{category}] ready — every {interval_minutes} min")
    while True:
        try:
            _run_cycle(category)
        except Exception as e:
            log.error(f"  [{category}] Unhandled error in cycle: {e}", exc_info=True)
        time.sleep(interval_minutes * 60)


class NewsScheduler:
    """Starts one daemon thread per feed category."""

    WORKERS = [
        ("market",   config.FETCH_INTERVAL_MARKET),
        ("national", config.FETCH_INTERVAL_NATIONAL),
        ("global",   config.FETCH_INTERVAL_GLOBAL),
    ]

    def start(self):
        log.info("Starting extraction workers...")
        for category, interval in self.WORKERS:
            t = threading.Thread(
                target=_loop,
                args=(category, interval),
                name=f"worker-{category}",
                daemon=True,
            )
            t.start()
        log.info("All workers running.")
