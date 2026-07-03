# Playbook: Facebook Marketplace (property rentals)

Browser-mode source, and the reason it must be Cameron's logged-in Chrome —
Marketplace is invisible without a Facebook session. Highest scam density of
any source; the judge applies a stricter prior (see docs/judge-rubric.md).
Also the best source for private-landlord units and rooms in shared houses.

## Open

Open the `urls:` from the profile's `sources.yaml`
(e.g. `https://www.facebook.com/marketplace/boston/propertyrentals`). Apply UI
filters:

- Price max = whole-unit ceiling; leave min at the profile's `min_price` floor.
- Location radius: the anchor city, ~8 km / 5 mi (Marketplace radii are coarse).
- If whole-unit-only: Bedrooms min. If the profile seeks `room_in_shared`,
  leave beds unfiltered — rooms post as 1-bed "Private room for rent".
- Sort: **Date listed: Newest first** (re-apply — it silently resets).

## New-since-last-run

Newest-first walk; stop at first already-seen id. Marketplace re-bumps posts
("Listed 3 weeks ago" appearing among fresh ones) — rely on the seen-store,
not the displayed age. First-ever run: first ~30 cards.

## Extract → Listing

Card grid is thin; open the detail panel (click, stays on-page) for each new card.

| Field | Where |
|-------|-------|
| `source` | `"fb_marketplace"` |
| `source_id` | item id — digits in `/marketplace/item/<id>/` |
| `url` | `https://www.facebook.com/marketplace/item/<id>/` |
| `title` | listing title |
| `price` | headline price |
| `beds` / `baths` | detail "3 beds · 1 bath" line when present |
| `address` | approximate area shown ("Cambridge, MA — 2 miles away"); exact addresses are rare |
| `available` | "Available from" field when present |
| `posted` | "Listed X ago" → ISO date (approximate) |
| `description` | full description text — **critical for the judge's scam pass** |
| `images` | first 1–3 photo URLs |
| `raw` | seller name + profile age hints if visible ("Joined Facebook in 2026" is a flag) |

## Quirks

- Infinite scroll; cards render in batches — scroll then wait before reading.
- The same unit is often re-posted every few days with a new item id: the
  fuzzy fingerprint (price+beds+area) is what catches these, so fill
  `price`/`beds`/`address` as completely as possible.
- Messenger popups and "Is this still available?" prompts: close, never send.
- Never message sellers, never mark "interested" — read-only.
- Scam tells to capture verbatim in `description`/`raw` for the judge:
  price far below area rate, stock/watermarked photos, "text me at …",
  landlord abroad, deposit-before-viewing.
