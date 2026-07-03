"""Seen-listings store — SQLite at data/<profile>/seen.db (gitignored).

Dedup happens on two keys: the exact fingerprint (source:source_id) and the
fuzzy key (price|beds|normalized-address) that collapses cross-postings of the
same unit on different sites. Price-change detection is recorded here as the
Phase 6 re-alert hook.

CLI (all read Listing JSON on stdin):
    python src/store.py --profile X filter-new   > new.json   # drop seen; tag price drops
    python src/store.py --profile X mark-seen                 # upsert everything
    python src/store.py --profile X mark-alerted --score 80 --verdict push
    python src/store.py --profile X stats
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from config import data_dir
from schema import Listing, read_listings, write_listings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (
    fingerprint TEXT PRIMARY KEY,
    source      TEXT NOT NULL,
    url         TEXT NOT NULL,
    price       INTEGER,
    beds        REAL,
    fuzzy_key   TEXT,
    first_seen  TEXT NOT NULL,
    last_seen   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_seen_fuzzy ON seen(fuzzy_key) WHERE fuzzy_key IS NOT NULL;
CREATE TABLE IF NOT EXISTS alerted (
    fingerprint TEXT PRIMARY KEY,
    alerted_at  TEXT NOT NULL,
    score       INTEGER,
    verdict     TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, db_path: str | Path):
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(_SCHEMA)

    @classmethod
    def for_profile(cls, slug: str) -> "Store":
        return cls(data_dir(slug) / "seen.db")

    def close(self) -> None:
        self.db.close()

    def _lookup(self, listing: Listing) -> sqlite3.Row | None:
        """The seen row for this listing, by exact then fuzzy key."""
        row = self.db.execute(
            "SELECT * FROM seen WHERE fingerprint = ?", (listing.fingerprint(),)
        ).fetchone()
        if row:
            return row
        fuzzy = listing.fuzzy_key()
        if fuzzy:
            return self.db.execute(
                "SELECT * FROM seen WHERE fuzzy_key = ?", (fuzzy,)
            ).fetchone()
        return None

    def is_new(self, listing: Listing) -> bool:
        return self._lookup(listing) is None

    def price_drop(self, listing: Listing) -> int | None:
        """Previous price if this listing was seen before at a higher price.
        (Phase 6 hook: re-alert on meaningful drops.)"""
        row = self._lookup(listing)
        if row and listing.price is not None and row["price"] is not None \
                and listing.price < row["price"]:
            return row["price"]
        return None

    def mark_seen(self, listing: Listing) -> None:
        now = _now()
        self.db.execute(
            """INSERT INTO seen (fingerprint, source, url, price, beds, fuzzy_key,
                                 first_seen, last_seen)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(fingerprint) DO UPDATE SET
                 last_seen = excluded.last_seen,
                 price     = excluded.price,
                 url       = excluded.url""",
            (listing.fingerprint(), listing.source, listing.url, listing.price,
             listing.beds, listing.fuzzy_key(), now, now),
        )
        self.db.commit()

    def mark_alerted(self, listing: Listing, score: int | None,
                     verdict: str = "push") -> None:
        self.db.execute(
            """INSERT INTO alerted (fingerprint, alerted_at, score, verdict)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(fingerprint) DO UPDATE SET
                 alerted_at = excluded.alerted_at,
                 score      = excluded.score,
                 verdict    = excluded.verdict""",
            (listing.fingerprint(), _now(), score, verdict),
        )
        self.db.commit()

    def recent_comps(self, beds: float | None = None, days: int = 14) -> list[int]:
        """Recent prices for the judge's value context."""
        q = ("SELECT price FROM seen WHERE price IS NOT NULL "
             "AND last_seen >= datetime('now', ?)")
        params: list = [f"-{int(days)} days"]
        if beds is not None:
            q += " AND beds = ?"
            params.append(beds)
        return [r["price"] for r in self.db.execute(q, params)]

    def stats(self) -> dict:
        seen = self.db.execute("SELECT COUNT(*) c FROM seen").fetchone()["c"]
        alerted = self.db.execute("SELECT COUNT(*) c FROM alerted").fetchone()["c"]
        return {"seen": seen, "alerted": alerted}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="seen-listings store")
    ap.add_argument("--profile")
    ap.add_argument("command", choices=["filter-new", "mark-seen", "mark-alerted", "stats"])
    ap.add_argument("--score", type=int)
    ap.add_argument("--verdict", default="push")
    args = ap.parse_args()

    from config import resolve_slug
    store = Store.for_profile(resolve_slug(args.profile))

    if args.command == "stats":
        print(store.stats())
        return

    listings = read_listings(sys.stdin)
    if args.command == "filter-new":
        out = []
        for l in listings:
            drop_from = store.price_drop(l)
            if store.is_new(l):
                out.append(l)
            elif drop_from is not None:
                l.raw["price_drop_from"] = drop_from
                out.append(l)
        write_listings(out, sys.stdout)
        print(f"filter-new: {len(out)}/{len(listings)} new or price-dropped",
              file=sys.stderr)
    elif args.command == "mark-seen":
        for l in listings:
            store.mark_seen(l)
        print(f"mark-seen: {len(listings)}", file=sys.stderr)
    elif args.command == "mark-alerted":
        for l in listings:
            store.mark_alerted(l, args.score, args.verdict)
        print(f"mark-alerted: {len(listings)}", file=sys.stderr)


if __name__ == "__main__":
    main()
