"""
deduplicator.py — Jaccard-based duplicate detection with TTL headline memory.
Identifies the first source to break each story.
"""

import re
import logging
from collections import defaultdict, OrderedDict
from datetime import datetime, timezone, timedelta

import config

log = logging.getLogger("deduplicator")

STOPWORDS = {
    "the", "and", "for", "are", "was", "with", "that", "this", "from", "has",
    "its", "after", "amid", "on", "in", "at", "to", "of", "a", "an", "by",
    "as", "is", "it", "be", "or", "up", "over", "into", "out", "about", "per",
    "says", "say", "said", "new", "year", "two", "one", "first", "last",
    "will", "could", "would", "also", "just", "more", "than", "his", "her",
}


def _tokenize(title: str) -> frozenset:
    words = re.sub(r"[^a-z0-9\s]", "", title.lower()).split()
    return frozenset(w for w in words if len(w) > 2 and w not in STOPWORDS)


def _jaccard(a: frozenset, b: frozenset) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


class HeadlineMemory:
    """
    Rolling TTL cache of seen headlines.
    Evicts entries older than SEEN_HEADLINES_TTL_HRS automatically.
    Caps at SEEN_HEADLINES_MAX entries (oldest first).
    """

    def __init__(self):
        self._store: OrderedDict = OrderedDict()

    def _evict_expired(self):
        cutoff = datetime.now(timezone.utc) - timedelta(hours=config.SEEN_HEADLINES_TTL_HRS)
        expired = [k for k, v in self._store.items() if v["seen_at"] < cutoff]
        for k in expired:
            del self._store[k]

    def _evict_overflow(self):
        while len(self._store) >= config.SEEN_HEADLINES_MAX:
            self._store.popitem(last=False)

    def add(self, guid: str, tokens: frozenset, source: str):
        self._evict_expired()
        self._evict_overflow()
        self._store[guid] = {
            "tokens":  tokens,
            "source":  source,
            "seen_at": datetime.now(timezone.utc),
        }

    def find_duplicate(self, tokens: frozenset, threshold: float):
        """Returns best matching entry dict if similarity >= threshold, else None."""
        self._evict_expired()
        best_score = 0.0
        best_match = None
        for guid, entry in self._store.items():
            score = _jaccard(tokens, entry["tokens"])
            if score >= threshold and score > best_score:
                best_score = score
                best_match = {**entry, "guid": guid, "score": score}
        return best_match

    def __len__(self):
        return len(self._store)


# Module-level singletons — persist across all fetch cycles
_memory         = HeadlineMemory()
_breaker_counts = defaultdict(int)


def process_articles(articles: list) -> dict:
    """
    Deduplicate a batch of articles and tag each one.

    Returns:
        {
            "to_publish":  [...]  new / unique articles
            "duplicates":  [...]  suppressed duplicates
            "stats":       {...}
        }
    """
    to_publish = []
    duplicates = []

    # Sort by pub date so the earliest article in this batch wins breaker status
    sorted_articles = sorted(
        articles,
        key=lambda x: x.get("fetched_at", datetime.now(timezone.utc))
    )

    for art in sorted_articles:
        tokens = _tokenize(art["title"])
        match  = _memory.find_duplicate(tokens, config.SIMILARITY_THRESHOLD)

        if match:
            art["is_breaker"]          = False
            art["is_duplicate"]        = True
            art["duplicate_of_source"] = match["source"]
            art["similarity_score"]    = round(match["score"] * 100, 1)
            duplicates.append(art)
            log.debug(
                f"  DUP ({art['similarity_score']}%) "
                f"[{art['source']}] '{art['title'][:55]}' "
                f"← [{match['source']}]"
            )
        else:
            art["is_breaker"]   = True
            art["is_duplicate"] = False
            _memory.add(art.get("guid", art["title"]), tokens, art["source"])
            _breaker_counts[art["source"]] += 1
            to_publish.append(art)
            log.debug(f"  NEW [{art['source']}] '{art['title'][:55]}'")

    stats = {
        "total":       len(sorted_articles),
        "to_publish":  len(to_publish),
        "duplicates":  len(duplicates),
        "memory_size": len(_memory),
    }
    log.info(
        f"  Dedup: {stats['total']} in → "
        f"{stats['to_publish']} new, "
        f"{stats['duplicates']} dups "
        f"(memory: {stats['memory_size']} headlines)"
    )
    return {"to_publish": to_publish, "duplicates": duplicates, "stats": stats}


def get_breaker_leaderboard() -> list:
    """Returns [(source, count), ...] sorted by break count descending."""
    return sorted(_breaker_counts.items(), key=lambda x: x[1], reverse=True)
