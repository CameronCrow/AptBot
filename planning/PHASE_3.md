---
type: reference
tags: [repo/AptBot]
up: "[[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]"
---
# Phase 3 — Judge & dedup

The judge step is the reason this is an agent and not a scraper. Deterministic
parts (dedup, hard gates) are code; fuzzy parts (fit, scam, value) are the LLM.

## 1. Dedup store → `src/store.py`

- SQLite at `data/seen.db` (`data/` is gitignored).
- Tables:
  - `seen(fingerprint PK, source, url, first_seen, last_seen, price)`
  - `alerted(fingerprint PK, alerted_at, score, verdict)`
- API: `is_new(listing)`, `mark_seen(listing)`, `mark_alerted(listing, score)`.
- Price-change detection: same fingerprint, lower price → treat as new-ish
  (re-alert with a "price drop" tag) — hook for Phase 6.
- Cross-posting collapse via the fuzzy secondary key from `schema.py`.

## 2. Hard gates (code, pre-LLM) → `src/gates.py`

Cheap deterministic filters so the agent never wastes judgment on obvious
misses: over `max_rent`, under `beds_min`, outside `areas_ok`, availability
outside the move-in window. Everything ambiguous (missing fields) passes
through to the judge rather than being dropped.

## 3. LLM judge rubric → `docs/judge-rubric.md`

The agent scores each surviving listing 0–100 with a structured verdict:

- **Fit** — criteria match incl. soft constraints and nice-to-haves.
- **Commute** — estimate from address/area to the anchor; flag if unstated.
- **Value** — price vs. comparable listings seen recently (the store gives it
  recent price context for the same area/beds).
- **Scam risk** — too-cheap-for-area, wire-transfer/gift-card language, no
  interior photos or stock photos, urgency pressure, landlord "out of the
  country". FB Marketplace and Craigslist get a stricter prior.
- Output: `{score, verdict: push|skip, reasons[], scam_flags[]}`.
- Push threshold: start at score ≥ 70 and no scam flags; tune in Phase 6.

## Checklist

- [x] Write `src/store.py` + `tests/test_store.py` (dedup, cross-post collapse, price-drop)
- [x] Write `src/gates.py` + tests (ambiguous listings pass through) — gates are shape-aware: a listing survives if it plausibly fits *any* sought shape (whole_unit / room_in_shared)
- [x] Write `docs/judge-rubric.md`
- [x] Live smoke: fetch → gates → filter-new on real Boston data (360 → 161 gated survivors → 161 new on cold store)
- [ ] Calibration pass: run rubric over ~20 real listings, eyeball scores with Cameron, adjust (needs the Phase 5 browser run)

## Related

- [[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]
- [[Repos/AptBot/planning/PHASE_2|PHASE_2]]
- [[Repos/AptBot/planning/PHASE_4|PHASE_4]]
- [[Repos/AptBot/docs/judge-rubric|judge-rubric]]
