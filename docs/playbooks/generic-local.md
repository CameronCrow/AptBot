# Playbook: generic local source (realtors, property managers, boards)

For corpus entries (`profiles/<slug>/corpus.yaml`) that don't have a
dedicated playbook. These sites are small and heterogeneous — this playbook
is a procedure, not a DOM map.

## Open

Open the entry's `url`. Find the rentals/listings view if the URL landed on a
homepage (nav labels: "Rentals", "Listings", "Apartments", "Available").
Apply whatever filters exist toward the profile's criteria (price ceiling,
beds, area); many small sites have none — that's fine, the gates handle it.

## New-since-last-run

Prefer a "newest" / "recently added" sort if one exists. These sites are
low-volume: walk the first ~20 cards and rely on the seen-store to drop
already-seen ones (fingerprint = this source's `name` + the listing's URL
slug or MLS/listing id). Stop early at the first already-seen id only when
the site clearly sorts newest-first.

## Extract → Listing

Fill what the site shows; missing fields pass to the judge:

- `source` = the corpus entry's `name`; `source_id` = listing id / URL slug
- `url`, `title`, `price`, `beds`, `baths`, `address`
- `available` when stated (realtor sites usually state it — valuable)
- `description` — first ~500 chars; `images` — first 1–3
- `raw.fee` — note broker fee vs no-fee if shown (Boston-relevant; the judge
  treats a broker fee as ~1 month of effective extra rent)

## Quirks & rules

- **Realtor/PM sites**: inventory often *also* appears on the big portals —
  the fuzzy fingerprint collapses echoes, so don't skip a listing just
  because it looks familiar; extract it and let dedup decide.
- **Boards/groups (Reddit, Facebook groups)**: posts are unstructured — parse
  price/beds/area out of the post text; the poster is a private party, so
  apply the same strict scam prior as FB Marketplace. Never reply, DM, or
  join-request with a message.
- **IDX-widget sites** (embedded MLS search iframes): if the widget resists
  extraction, grab whatever the card view shows and let the judge open the
  detail page for finalists.
- Site broken / empty / redirects to a portal → note it and suggest demoting
  the corpus entry (`status: dead`) in the run summary.
- **A corpus source failing never aborts the run** — same failure policy as
  every other source.
