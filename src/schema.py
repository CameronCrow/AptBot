"""Listing — the contract between retrieval, judging, dedup, and notify.

Retrieval (scripts and browser playbooks) normalizes every source into this
shape. Dedup keys off `fingerprint()` (exact) and `fuzzy_key()` (cross-posting
collapse: the same unit posted on Zillow *and* Craigslist).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field


@dataclass
class Listing:
    source: str                      # "zillow" | "craigslist" | "fb_marketplace" | ...
    source_id: str                   # stable per-site id (url slug / post id)
    url: str
    title: str
    price: int | None = None         # $/mo
    beds: float | None = None
    baths: float | None = None
    address: str | None = None       # or approximate area
    available: str | None = None     # ISO date if stated
    posted: str | None = None        # ISO datetime if known
    description: str = ""
    images: list[str] = field(default_factory=list)   # urls (for the alert card)
    raw: dict = field(default_factory=dict)           # anything else site-specific

    def fingerprint(self) -> str:
        """Exact dedup key: normalized (source, source_id)."""
        return f"{self.source.strip().lower()}:{str(self.source_id).strip().lower()}"

    def fuzzy_key(self) -> str | None:
        """Cross-posting key: (price, beds, normalized address).

        None when any component is missing — an absent fuzzy key never
        collapses two listings together.
        """
        if self.price is None or self.beds is None or not self.address:
            return None
        return f"{self.price}|{self.beds:g}|{normalize_address(self.address)}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Listing":
        known = {f: d.get(f) for f in cls.__dataclass_fields__ if f in d}
        known.setdefault("description", "")
        known["description"] = known.get("description") or ""
        known["images"] = list(d.get("images") or [])
        known["raw"] = dict(d.get("raw") or {})
        return cls(**known)


_UNIT_RE = re.compile(r"\b(?:apt|apartment|unit|ste|suite|fl|floor|#)\s*\.?\s*\w{1,6}\b")
_SUFFIXES = {
    "street": "st", "avenue": "ave", "boulevard": "blvd", "road": "rd",
    "drive": "dr", "lane": "ln", "place": "pl", "court": "ct",
    "square": "sq", "terrace": "ter", "parkway": "pkwy", "circle": "cir",
}


def normalize_address(addr: str) -> str:
    """Lowercase, drop unit designators and punctuation, normalize suffixes."""
    s = addr.lower()
    s = _UNIT_RE.sub(" ", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    words = [_SUFFIXES.get(w, w) for w in s.split()]
    return " ".join(words)


def read_listings(fp) -> list[Listing]:
    """Read listings from a file object holding a JSON array or JSON lines.
    Tolerates a UTF-8 BOM (PowerShell 5.1's `Out-File -Encoding utf8`)."""
    text = fp.read().lstrip("﻿").strip()
    if not text:
        return []
    if text.startswith("["):
        rows = json.loads(text)
    else:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [Listing.from_dict(r) for r in rows]


def write_listings(listings: list[Listing], fp) -> None:
    json.dump([l.to_dict() for l in listings], fp, indent=1, ensure_ascii=False)
    fp.write("\n")
