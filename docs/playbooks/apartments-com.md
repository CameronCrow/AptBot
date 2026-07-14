---
type: reference
tags: [repo/AptBot]
up: "[[Repos/AptBot/docs/DOCS_MAIN|DOCS_MAIN]]"
---
# Playbook: Apartments.com

Browser-mode source. Filters are path-encoded, so the `urls:` in the profile's
`sources.yaml` already carry beds/price (e.g.
`https://www.apartments.com/cambridge-ma/3-bedrooms-under-6000/`).

## Open

Open each URL. Then:

- Sort: **Newest** (dropdown top-right of results).
- If the profile seeks `room_in_shared`, also check the same city path without
  the beds segment plus the "Rooms" filter under Lifestyle, if present —
  otherwise rooms mostly won't appear on this site.

## New-since-last-run

Newest-first walk; stop at the first already-seen id. First-ever run: first ~2
pages. Note: Apartments.com mixes "featured/sponsored" cards at the top that
ignore sort order — skip cards labeled *Sponsored* when detecting "new".

## Extract → Listing

| Field | Where |
|-------|-------|
| `source` | `"apartments_com"` |
| `source_id` | property slug — last path segment of the card URL (e.g. `.../the-eddy-boston-ma/abc123/` → `abc123`, else the slug) |
| `url` | card link |
| `title` | property name |
| `price` | card price; ranges ("$5,700 – 7,200") → low end |
| `beds` / `baths` | card facts; ranges → the qualifying floorplan's value |
| `address` | card address line |
| `available` | card "Available Now / Aug 15" when shown |
| `posted` | rarely shown; leave null |
| `description` | detail-page blurb when opened |
| `images` | first 1–3 carousel image URLs |
| `raw` | amenity chips (in-unit W/D, dishwasher, AC, parking) — feed the judge |

## Quirks

- Mostly professionally-managed buildings: scam risk is low, but prices are
  often "starting at" teasers — the judge should treat range prices skeptically.
- One property card = many floorplans; qualify on the cheapest floorplan that
  meets `beds_min`, and record that plan's price/beds.
- Pagination resets sort occasionally — re-check the sort dropdown on page 2.
- Phone-number interstitials and tour-scheduling modals: close, never submit.

## Related

- [[Repos/AptBot/docs/DOCS_MAIN|DOCS_MAIN]]
- [[Repos/AptBot/docs/playbooks/zillow|zillow]]
- [[Repos/AptBot/docs/playbooks/fb-marketplace|fb-marketplace]]
- [[Repos/AptBot/docs/playbooks/generic-local|generic-local]]
