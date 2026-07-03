# Playbook: Zillow (rentals)

Browser-mode source. The agent drives Cameron's logged-in Chrome; being logged
in keeps Zillow's anti-bot friction low and enables saved-search state.

## Open

Open each URL under the `zillow` source's `urls:` in the profile's
`sources.yaml` (one per in-scope area). On first visit, apply UI filters from
`criteria.yaml`:

- **For Rent** toggle (not For Sale)
- Price max = whole-unit ceiling (`budget.max_rent × group.size`)
- Beds min = `unit.beds_min` — *skip this filter if the profile also seeks
  `room_in_shared`* (rooms are posted as low-bed listings)
- Sort: **Newest**

Prefer **list view** over map view (stable ordering; map hides results).

## New-since-last-run

Results are newest-first: walk cards top-down, build the listing id from the
card link, and **stop at the first id the seen-store already has**
(`python src/store.py --profile <slug> seen <fingerprint>` or batch via
`filter-new`). First-ever run: take the first ~2 pages only.

## Extract → Listing

Per card (open the detail page only when card data is incomplete):

| Field | Where |
|-------|-------|
| `source` | `"zillow"` |
| `source_id` | zpid — the digits in the card URL `/homedetails/...-<zpid>_zpid/` |
| `url` | card link, stripped of query params |
| `title` | card headline (usually the address) |
| `price` | card price; take the low end of ranges like "$5,800+/mo" |
| `beds` / `baths` | card facts line ("3 bds 1 ba") |
| `address` | card address line |
| `available` | detail page "Date available" if shown |
| `posted` | card "X hours/days on Zillow" → ISO date (approximate is fine) |
| `description` | detail-page description, first ~500 chars, when opened |
| `images` | first 1–3 card/carousel image URLs |
| `raw` | anything else useful: sqft, pets policy, laundry/parking amenity chips |

## Quirks

- Cards lazy-load: scroll the results pane to materialize cards before reading.
- Interstitial sign-in/app modals: dismiss, never sign out.
- "Verified listing" badge → record `raw.verified: true` (judge trusts these more).
- Multi-unit buildings post as one card with floorplans: if a floorplan within
  budget exists, use the building page URL and the cheapest qualifying plan's
  price/beds; `source_id` stays the zpid.
- Zillow bundles Trulia/HotPads inventory — cross-posting dedup handles echoes.
- CAPTCHA / "Press & Hold" wall: stop this source, mark it errored in the run
  summary; do not retry in a loop.
