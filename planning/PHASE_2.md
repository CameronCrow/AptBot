# Phase 2 — Retrieval

Two retrieval modes normalize into one `Listing` schema.

## 1. Listing schema → `src/schema.py`

The contract between retrieval, judging, dedup, and notify:

```python
Listing:
  source: str            # "zillow" | "craigslist" | "fb" | ...
  source_id: str         # stable per-site id (url slug / post id)
  url: str
  title: str
  price: int | None      # $/mo
  beds: float | None
  baths: float | None
  address: str | None    # or approximate area
  available: str | None  # ISO date if stated
  posted: str | None
  description: str
  images: list[str]      # urls (for the alert card, not stored)
  raw: dict              # anything else site-specific
```

`fingerprint()` helper: normalized `(source, source_id)`, plus a fuzzy
secondary key `(price, beds, normalized-address)` to catch cross-postings
(same unit on Zillow *and* Craigslist).

## 2. Craigslist RSS poller → `src/fetch_craigslist.py`

- ~40 lines: fetch the pre-filtered RSS feed(s) from `sources.yaml`, parse
  entries → `Listing` objects, emit JSON to stdout.
- Pure stdlib + `feedparser`. No browser, no login. Cheap enough to run every
  agent cycle (and more often later if wanted).

## 3. Browser playbooks → `docs/playbooks/<source>.md`

For each `browser`-mode source, a short markdown playbook the agent follows
when driving Chrome (same pattern as the canvas-syncer agent):

- exact saved-search URL to open
- how to detect "new since last run" (sort by newest; stop at first seen id)
- which fields to extract into the `Listing` schema and where they live on the page
- site quirks (lazy-loading, login walls, "verified" badges, map vs list view)

Playbooks are docs, not code — when a site reshuffles its DOM, the agent
usually adapts on its own; the playbook just captures what's stable.

## Checklist

- [ ] Write `src/schema.py` with `Listing` + `fingerprint()`
- [ ] Write `src/fetch_craigslist.py`; verify against the live feed
- [ ] Write playbook: Zillow
- [ ] Write playbook: Apartments.com
- [ ] Write playbook: Facebook Marketplace
- [ ] Write playbook(s): local/university sources from Phase 1
- [ ] Manual smoke test: one agent-driven browse of each source produces valid `Listing` JSON
