---
type: reference
tags: [repo/AptBot]
up: "[[Repos/AptBot/docs/DOCS_MAIN|DOCS_MAIN]]"
---
# Playbook: Craigslist (fallback only)

Craigslist is normally **script-mode** — `src/fetch_craigslist.py` hits the
unofficial `sapi.craigslist.org` JSON endpoint (RSS is dead; 403 since ~2023).
Use this playbook **only when the script fails** (endpoint changed, blocked,
schema drift): mark the script errored in the run summary and fall back here,
and flag that the parser needs updating.

## Open

`https://<site>.craigslist.org/search/apa?min_price=<..>&max_price=<..>#search=1~list~0`
with the site/params from the profile's `sources.yaml` craigslist entry.
Force **list view** and sort **newest**.

## New-since-last-run

Newest-first; the post id is the digits at the end of each result URL
(`/apa/d/<slug>/<id>.html`). Stop at first already-seen id.

## Extract → Listing

| Field | Where |
|-------|-------|
| `source` | `"craigslist"` (same as the script — fingerprints stay compatible) |
| `source_id` | post id digits |
| `url` | result link |
| `title` | result title |
| `price` | card price |
| `beds` | "3br" chip when present |
| `baths` | detail page only ("2Ba") |
| `address` | detail page map address / neighborhood tag |
| `available` | detail "available <date>" banner |
| `posted` | card timestamp |
| `description` | detail post body — needed for the scam pass |
| `images` | gallery URLs (`images.craigslist.org/..._600x450.jpg`) |

## Quirks

- Heavy repost culture: identical post re-listed with new id every few days —
  fuzzy fingerprint catches these when price/beds/area are filled.
- Ghost listings from brokers ("1000s of apartments — call us!") — extract
  anyway; the judge's scam/junk pass drops them.
- If a CAPTCHA appears, stop the source and report; don't retry.

## Related

- [[Repos/AptBot/docs/DOCS_MAIN|DOCS_MAIN]]
- [[Repos/AptBot/docs/playbooks/zillow|zillow]]
- [[Repos/AptBot/docs/playbooks/apartments-com|apartments-com]]
- [[Repos/AptBot/docs/playbooks/fb-marketplace|fb-marketplace]]
