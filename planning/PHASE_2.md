---
type: reference
tags: [repo/AptBot]
up: "[[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]"
---
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

## 2. Craigslist poller → `src/fetch_craigslist.py`

> **Deviation from plan:** Craigslist RSS is dead (`format=rss` → 403,
> verified 2026-07-03), so the poller instead hits the unofficial
> `sapi.craigslist.org/web/v8/postings/search/full` JSON endpoint the search
> SPA uses, decoding its compact item format (offsets in `data.decode`,
> typed sub-arrays for slug/images/beds). Verified live: 360/360 Boston items
> parsed; listing URLs and image URLs resolve. Pure stdlib — no `feedparser`.
> If the endpoint changes, `docs/playbooks/craigslist.md` is the browser-mode
> fallback.

- Reads the `craigslist` source (site, `area_id`, price params) from the
  profile's `sources.yaml`; emits `Listing` JSON to stdout; unparseable items
  are skipped and counted on stderr. No browser, no login — cheap enough to
  run every cycle.

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

- [x] Write `src/schema.py` with `Listing` + `fingerprint()` (+ `fuzzy_key()`, JSON I/O helpers; `src/config.py` profile loader)
- [x] Write `src/fetch_craigslist.py`; verified live against sapi (360/360 parsed, URLs + images resolve)
- [x] Write playbook: Zillow
- [x] Write playbook: Apartments.com
- [x] Write playbook: Facebook Marketplace
- [x] Write playbook: Craigslist browser fallback (sapi contingency)
- [ ] Playbook(s) for local sources — blocked on Phase 1 follow-up (none confirmed by Cameron yet)
- [ ] Manual smoke test: one agent-driven browse of each browser source → valid `Listing` JSON (folded into the Phase 5 dry run — needs the Chrome session)

## Related

- [[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]
- [[Repos/AptBot/planning/PHASE_1|PHASE_1]]
- [[Repos/AptBot/planning/PHASE_3|PHASE_3]]
- [[Repos/AptBot/docs/playbooks/zillow|zillow playbook]]
