# Phase 4 — Notify

## 1. Push helper → `src/notify.py`

- Single function `push(listing, score, reasons)` → HTTP POST to
  `ntfy.sh/<topic>` from `notify.yaml`.
- Use ntfy features: title = `$1,850 · 2bd/1ba · Nassau St area (score 82)`,
  body = top 2–3 reasons, `Click` action = listing URL, `Attach` = first image
  URL so the notification shows a photo.
- Priority mapping: score ≥ 90 → `high`, else `default`.

## 2. Alert policy

- **Instant** push per qualifying listing — apartments move fast, digests lose
  races. Rate-guard: if one run yields > 5 qualifying listings, send the top 3
  instantly + 1 summary push for the rest (prevents first-run flood and
  criteria-too-loose flood).
- Every alert also appended to `data/alerts.log` (JSON lines) so there's a
  reviewable trail of what was pushed and why.

## Checklist

- [x] Write `src/notify.py` + test against the live topic (channel test sent 2026-07-03)
- [x] Implement flood guard (top-3 + summary; cap from `notify.yaml`)
- [x] Implement `data/<profile>/alerts.log` trail (also records dry-runs and summary items)
- [x] End-to-end: fake listing → formatted push sent to the topic with photo attach + click-through (verified in ntfy's response; on-phone confirmation pending Cameron subscribing to the topic)
