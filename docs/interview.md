# AptBot instantiation interview

AptBot is instantiable: each renter gets a **profile** under `profiles/<slug>/`
(three files: `criteria.yaml`, `sources.yaml`, `notify.yaml`). This document is
the script for creating one. The `apartment-hunt` skill runs it when invoked in
setup mode; a human can also follow it by hand, copying `profiles/_template/`.

Rules of the interview:

- Distinguish **hard** constraints (gate listings out) from **soft** ones
  (affect score only). When the renter is unsure, record it as soft.
- Don't skip the "common answers" prompts — renters forget to mention
  dealbreakers like laundry or parking until a bad listing reminds them.
- Anything assumed rather than answered gets an `# ASSUMPTION` comment in the
  YAML so it's easy to revisit.

## Part 1 — Criteria (fills `criteria.yaml`)

Ask, in order:

1. **Who's moving?** Name; total group size (renter + roommates); whether they
   want a whole unit for the group, a room in an existing shared household, or
   both. → `renter`, `group`
2. **Budget.** "What's the most *you* would pay per month, all-in?" (hard
   ceiling, their own share) and "what would feel like a good deal?" (target).
   For groups, confirm the whole-unit ceiling: share × group size. → `budget`
3. **Anchor & commute.** Where do they commute to (work/school, exact address
   or landmark)? By what mode? What's the longest acceptable commute in
   minutes? → `location.anchor`, `commute_mode`, `max_commute_min`
4. **Areas.** Any neighborhoods/towns explicitly in or out? (Empty in-list is
   fine — the judge scores by commute.) → `areas_ok`, `areas_no`
5. **Unit.** Minimum beds (usually ≥ group size) and baths; furnished
   required/avoided/indifferent? → `unit`
6. **Move-in window.** Earliest and latest acceptable start date. → `move_in`
7. **Lease.** Minimum term; are sublets acceptable? → `lease`
8. **Dealbreakers.** Prompt each of these explicitly — "would you reject an
   otherwise-perfect place over…": no in-unit laundry? no dishwasher? shared
   bathroom? no parking? ground floor / basement? window-AC-only or baseboard
   heat (no central heating/cooling)? pets not allowed (do they have one)?
   → `dealbreakers`
9. **Nice-to-haves.** Same list plus: private bath (for shared housing),
   central air/heat, outdoor space, gym, utilities included. Ranked top-3 if
   they name many. → `nice_to_haves`
10. **Anything else the judge should know?** Free text. → `renter.notes`

## Part 2 — Sources (fills `sources.yaml`)

1. **Craigslist**: find the site subdomain for their metro
   (`<site>.craigslist.org`) and its numeric `area_id` — fetch
   `https://sapi.craigslist.org/web/v8/postings/search/full?batch=<id>-0-360-0-0&cc=US&lang=en&searchPath=apa`
   and check `data.areas` names until it matches (boston=4). Set
   `min_price`/`max_price` from budget (unit ceiling + ~10% slack; floor ~$800
   to cut scam posts).
2. **Zillow / Apartments.com / FB Marketplace**: build one rentals URL per
   in-scope area (see each playbook's URL pattern). These are `browser` mode —
   the agent applies fine filters in the UI.
3. **Local sources the renter already uses**: ask "any local listing sites,
   university off-campus boards, or housing listservs/groups you already
   use?" These go straight into the corpus (part 2b) as `active`.

## Part 2b — Source discovery (fills `corpus.yaml`)

The defaults in `sources.yaml` exist in every metro; the localized long tail
does not. At instantiation, populate `profiles/<slug>/corpus.yaml` — later
cycles then just poll corpus + defaults. Procedure:

1. **Search the metro** (a handful of web searches, not an odyssey):
   - `<city/neighborhoods> apartment rental listings local realtors`
   - `<university> off-campus housing board` for every nearby university
   - `<city> housing facebook group / subreddit / listserv`
   - `<city> property management companies rentals` for the anchor's
     immediate neighborhoods
2. **Vet each candidate**: does it list rentals in the target areas and price
   band? Is it updated (listings from this month)? Is it reachable without an
   account the renter doesn't have?
3. **Record every candidate** in `corpus.yaml` (schema in
   `profiles/_template/corpus.yaml`) — vetted ones as `active`, unverified as
   `candidate`, login-walled as `needs-login`, junk as `dead` (dead entries
   prevent rediscovery). Big-brokerage sites whose inventory echoes the
   portals default to `candidate` with a "verify dedup overlap" note.
4. **Refresh**: re-run discovery on demand ("refresh the source corpus") or
   when several corpus sources go dead — not every cycle.

## Part 3 — Push channel (fills `notify.yaml` + `secrets.yaml`)

1. Generate a topic: `aptbot-<slug>-<14 random chars>` (unguessable — the topic
   name is the secret).
2. `curl -d "AptBot test" ntfy.sh/<topic>` to create traffic on it.
3. Have the renter install the **ntfy** app (iOS/Android) and subscribe to the
   topic; confirm the test push arrived (re-send if it predates subscribing).
4. Record the server + `push` thresholds in `notify.yaml`; record the topic in
   `profiles/<slug>/secrets.yaml` — that file is gitignored and must never be
   committed (this repo's remote is public).

## Part 4 — Wire-up

1. `mkdir profiles/<slug>` and write the three YAMLs (start from
   `profiles/_template/`).
2. Smoke test retrieval: `python src/fetch_craigslist.py --profile <slug>`
   should emit Listing JSON.
3. Schedule (or reuse) the scouting routine pointing at the new profile.
