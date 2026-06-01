"""
storage.py — Saves extracted articles to SQLite and optionally CSV.
Tags are stored as a comma-separated string in both outputs.
"""

import csv
import logging
import os
import sqlite3
from datetime import datetime, timezone

import config

log = logging.getLogger("storage")


def _tags_to_str(tags) -> str:
    """Convert list ['market','stocks','india'] → 'market,stocks,india'"""
    if isinstance(tags, list):
        return ",".join(tags)
    return str(tags) if tags else ""


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and indexes if they don't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                saved_at       TEXT NOT NULL,
                pub_date       TEXT,
                category       TEXT NOT NULL,
                source         TEXT NOT NULL,
                tags           TEXT,
                title          TEXT NOT NULL,
                link           TEXT,
                guid           TEXT UNIQUE,
                is_breaker     INTEGER DEFAULT 0,
                is_duplicate   INTEGER DEFAULT 0,
                dup_of_source  TEXT,
                similarity     REAL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON articles(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_source   ON articles(source)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tags     ON articles(tags)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_at ON articles(saved_at)")
        conn.commit()
    log.info(f"Database ready: {config.DB_FILE}")


def _save_one_db(article: dict, category: str):
    pub_date = article.get("fetched_at", "")
    if hasattr(pub_date, "isoformat"):
        pub_date = pub_date.isoformat()

    try:
        with _get_conn() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO articles
                    (saved_at, pub_date, category, source, tags, title, link, guid,
                     is_breaker, is_duplicate, dup_of_source, similarity)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                datetime.now(timezone.utc).isoformat(),
                str(pub_date),
                category,
                article.get("source", ""),
                _tags_to_str(article.get("tags", [])),
                article.get("title", ""),
                article.get("link", ""),
                article.get("guid", article.get("title", "")),
                1 if article.get("is_breaker") else 0,
                1 if article.get("is_duplicate") else 0,
                article.get("duplicate_of_source"),
                article.get("similarity_score"),
            ))
            conn.commit()
    except Exception as e:
        log.error(f"  DB save error: {e}")


_CSV_HEADER = [
    "saved_at", "pub_date", "category", "source", "tags", "title",
    "link", "is_breaker", "is_duplicate", "dup_of_source", "similarity"
]


def init_csv():
    if not config.CSV_ENABLED:
        return
    if not os.path.exists(config.CSV_FILE):
        with open(config.CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(_CSV_HEADER)
    log.info(f"CSV ready: {config.CSV_FILE}")


def _save_one_csv(article: dict, category: str):
    if not config.CSV_ENABLED:
        return
    pub_date = article.get("fetched_at", "")
    if hasattr(pub_date, "isoformat"):
        pub_date = pub_date.isoformat()
    try:
        with open(config.CSV_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now(timezone.utc).isoformat(),
                str(pub_date),
                category,
                article.get("source", ""),
                _tags_to_str(article.get("tags", [])),
                article.get("title", ""),
                article.get("link", ""),
                1 if article.get("is_breaker") else 0,
                1 if article.get("is_duplicate") else 0,
                article.get("duplicate_of_source", ""),
                article.get("similarity_score", ""),
            ])
    except Exception as e:
        log.error(f"  CSV save error: {e}")


def store(articles: list, category: str) -> int:
    for art in articles:
        _save_one_db(art, category)
        _save_one_csv(art, category)
    log.info(f"  Stored {len(articles)} articles [{category}]")
    return len(articles)


def _make_like_clauses(column: str, terms: list[str], params: list) -> str:
    clauses = []
    for term in terms:
        clauses.append(f"lower({column}) LIKE ?")
        params.append(f"%{term}%")
    return " OR ".join(clauses)

def get_latest(limit: int = 20, category: str = None, tag: str = None, keyword_terms: list = None) -> list:
    params = []
    where = "WHERE 1=1"
    if category:
        where += " AND category = ?"
        params.append(category)
    if tag:
        where += " AND (',' || tags || ',' LIKE ?)"
        params.append(f"%,{tag},%")
    if keyword_terms:
        kw_clause = " OR ".join("lower(title) LIKE ?" for _ in keyword_terms)
        where += f" AND ({kw_clause})"
        params.extend(f"%{kw.lower()}%" for kw in keyword_terms)
    params.append(limit)
    with _get_conn() as conn:
        return [dict(r) for r in conn.execute(f"SELECT * FROM articles {where} ORDER BY saved_at DESC LIMIT ?", params).fetchall()]


def get_stats() -> dict:
    with _get_conn() as conn:
        total    = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        breakers = conn.execute("SELECT COUNT(*) FROM articles WHERE is_breaker=1").fetchone()[0]
        dups     = conn.execute("SELECT COUNT(*) FROM articles WHERE is_duplicate=1").fetchone()[0]
        by_cat   = conn.execute("SELECT category, COUNT(*) n FROM articles GROUP BY category").fetchall()
        by_src   = conn.execute("SELECT source, COUNT(*) n FROM articles GROUP BY source ORDER BY n DESC LIMIT 10").fetchall()
    return {
        "total":       total,
        "breakers":    breakers,
        "duplicates":  dups,
        "by_category": {r["category"]: r["n"] for r in by_cat},
        "top_sources": [(r["source"], r["n"]) for r in by_src],
    }


def get_tag_stats() -> list:
    """Returns [(tag, count), ...] sorted by count descending."""
    with _get_conn() as conn:
        rows = conn.execute("SELECT tags FROM articles WHERE tags != ''").fetchall()
    counts = {}
    for row in rows:
        for tag in row["tags"].split(","):
            tag = tag.strip()
            if tag:
                counts[tag] = counts.get(tag, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)
