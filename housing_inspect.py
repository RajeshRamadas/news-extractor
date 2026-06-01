"""
housing_inspect.py — Browse the collected housing market news.

IMPORTANT: Named housing_inspect.py NOT inspect.py — naming it inspect.py
           shadows Python's built-in and breaks the requests library.

Usage:
    python housing_inspect.py stats
    python housing_inspect.py tags
    python housing_inspect.py latest
    python housing_inspect.py latest <category>     (us|global|india|mortgage)
    python housing_inspect.py tag <tagname>          (housing|mortgage|luxury|reit|...)
    python housing_inspect.py dups
    python housing_inspect.py breakers
    python housing_inspect.py search <keyword>
"""

import sqlite3
import sys

import config


def _conn():
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_stats():
    with _conn() as conn:
        total    = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        breakers = conn.execute("SELECT COUNT(*) FROM articles WHERE is_breaker=1").fetchone()[0]
        dups     = conn.execute("SELECT COUNT(*) FROM articles WHERE is_duplicate=1").fetchone()[0]

        print(f"\n{'='*62}")
        print(f"  HOUSING NEWS DB: {config.DB_FILE}")
        print(f"{'='*62}")
        print(f"  Total articles : {total}")
        print(f"  Breakers       : {breakers}")
        print(f"  Duplicates     : {dups}")

        print(f"\n  By category:")
        for r in conn.execute("SELECT category, COUNT(*) n FROM articles GROUP BY category ORDER BY n DESC"):
            print(f"    {r['category']:<16} {r['n']}")

        print(f"\n  Top sources:")
        for r in conn.execute(
            "SELECT source, COUNT(*) n FROM articles GROUP BY source ORDER BY n DESC LIMIT 12"
        ):
            print(f"    {r['source']:<30} {r['n']}")

        print(f"\n  Breaker leaderboard:")
        for r in conn.execute(
            "SELECT source, COUNT(*) n FROM articles WHERE is_breaker=1 "
            "GROUP BY source ORDER BY n DESC LIMIT 10"
        ):
            print(f"    {r['source']:<30} {r['n']} first breaks")
    print()


def cmd_tags():
    with _conn() as conn:
        rows = conn.execute("SELECT tags FROM articles WHERE tags != ''").fetchall()

    counts = {}
    for row in rows:
        for tag in row["tags"].split(","):
            tag = tag.strip()
            if tag:
                counts[tag] = counts.get(tag, 0) + 1

    print(f"\n  {'TAG':<22} {'COUNT':>6}   BAR")
    print(f"  {'-'*60}")
    max_c = max(counts.values(), default=1)
    for tag, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        bar = "█" * int(cnt / max_c * 28)
        print(f"  {tag:<22} {cnt:>6}   {bar}")
    print()


def cmd_latest(category: str = None, limit: int = 30):
    query  = "SELECT * FROM articles"
    params = []
    if category:
        query += " WHERE category=?"
        params.append(category)
    query += " ORDER BY saved_at DESC LIMIT ?"
    params.append(limit)

    label = f"[{category}]" if category else "[all]"
    print(f"\n  Latest {limit} articles {label}")
    print(f"  {'#':<4} {'Source':<24} {'Tags':<32} {'T':<3} {'Title'}")
    print(f"  {'-'*105}")
    with _conn() as conn:
        rows = conn.execute(query, params).fetchall()
        if not rows:
            print("  No articles found.")
            return
        for i, r in enumerate(rows, 1):
            tag  = "B" if r["is_breaker"] else ("D" if r["is_duplicate"] else "-")
            tags = (r["tags"] or "")[:30]
            print(f"  {i:<4} {r['source']:<24} {tags:<32} {tag:<3} {r['title'][:40]}")
    print()


def cmd_tag(tagname: str, limit: int = 30):
    query = (
        "SELECT * FROM articles "
        "WHERE (',' || tags || ',') LIKE ? "
        "ORDER BY saved_at DESC LIMIT ?"
    )
    print(f"\n  Articles tagged [{tagname}] — latest {limit}")
    print(f"  {'#':<4} {'Cat':<10} {'Source':<24} {'Tags':<28} {'Title'}")
    print(f"  {'-'*105}")
    with _conn() as conn:
        rows = conn.execute(query, (f"%,{tagname},%", limit)).fetchall()
        if not rows:
            print(f"  No articles with tag '{tagname}'.")
            print(f"  Run: python housing_inspect.py tags")
            return
        for i, r in enumerate(rows, 1):
            tags = (r["tags"] or "")[:26]
            print(f"  {i:<4} {r['category']:<10} {r['source']:<24} {tags:<28} {r['title'][:38]}")
    print()


def cmd_search(keyword: str, limit: int = 30):
    """Full-text search across titles."""
    query = (
        "SELECT * FROM articles "
        "WHERE title LIKE ? "
        "ORDER BY saved_at DESC LIMIT ?"
    )
    print(f"\n  Search results for '{keyword}' — latest {limit}")
    print(f"  {'#':<4} {'Cat':<10} {'Source':<24} {'Tags':<24} {'Title'}")
    print(f"  {'-'*100}")
    with _conn() as conn:
        rows = conn.execute(query, (f"%{keyword}%", limit)).fetchall()
        if not rows:
            print(f"  No articles found containing '{keyword}'.")
            return
        for i, r in enumerate(rows, 1):
            tags = (r["tags"] or "")[:22]
            print(f"  {i:<4} {r['category']:<10} {r['source']:<24} {tags:<24} {r['title'][:40]}")
    print()


def cmd_dups(limit: int = 30):
    print(f"\n  Latest {limit} duplicate detections")
    print(f"  {'Source':<24} {'Dup of':<22} {'Sim%':<6} {'Title'}")
    print(f"  {'-'*95}")
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM articles WHERE is_duplicate=1 ORDER BY saved_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        if not rows:
            print("  No duplicates recorded yet.")
            return
        for r in rows:
            sim = f"{r['similarity']:.0f}%" if r["similarity"] else "—"
            print(f"  {r['source']:<24} {(r['dup_of_source'] or ''):<22} {sim:<6} {r['title'][:42]}")
    print()


def cmd_breakers(limit: int = 15):
    print(f"\n  Breaker leaderboard — top {limit} sources")
    print(f"  {'Rank':<6} {'Source':<30} {'First Breaks'}")
    print(f"  {'-'*52}")
    with _conn() as conn:
        rows = conn.execute(
            "SELECT source, COUNT(*) n FROM articles WHERE is_breaker=1 "
            "GROUP BY source ORDER BY n DESC LIMIT ?",
            (limit,)
        ).fetchall()
        if not rows:
            print("  No data yet.")
            return
        for i, r in enumerate(rows, 1):
            print(f"  #{i:<5} {r['source']:<30} {r['n']}")
    print()


HELP = """
Usage:
  python housing_inspect.py stats
  python housing_inspect.py tags
  python housing_inspect.py latest
  python housing_inspect.py latest <category>    (us | global | india | mortgage)
  python housing_inspect.py tag <tagname>        (housing | mortgage | luxury | reit | ...)
  python housing_inspect.py search <keyword>     (mortgage | RBI | Dubai | bubble | ...)
  python housing_inspect.py dups
  python housing_inspect.py breakers
"""

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"

    if cmd == "stats":
        cmd_stats()
    elif cmd == "tags":
        cmd_tags()
    elif cmd == "latest":
        cat = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_latest(cat)
    elif cmd == "tag":
        if len(sys.argv) < 3:
            print("Usage: python housing_inspect.py tag <tagname>")
        else:
            cmd_tag(sys.argv[2])
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: python housing_inspect.py search <keyword>")
        else:
            cmd_search(sys.argv[2])
    elif cmd == "dups":
        cmd_dups()
    elif cmd == "breakers":
        cmd_breakers()
    else:
        print(HELP)
