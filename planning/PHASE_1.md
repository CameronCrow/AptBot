# Phase 1 — Criteria & source inventory

The whole "judge" step hinges on a precise spec. A vague spec makes the bot
noisy (pushes junk) or silent (over-filters). This phase produces the two
config files everything else consumes, plus the push channel.

## 1. Search criteria → `src/config/criteria.yaml`

Fields to capture from Cameron (hard vs. soft constraints kept distinct):

```yaml
budget:
  max_rent: ???          # hard ceiling, $/mo
  target_rent: ???       # soft — score bonus below this
location:
  anchor: ???            # commute anchor (e.g. Princeton campus)
  max_commute_min: ???   # by which mode? (walk / bike / transit / drive)
  areas_ok: []           # neighborhoods / towns explicitly in-scope
  areas_no: []           # explicitly out
unit:
  beds_min: ???
  baths_min: ???
  furnished: any | required | avoid
move_in:
  earliest: ???          # ISO date
  latest: ???
lease:
  min_months: ???
  sublets_ok: ???
dealbreakers: []         # e.g. no in-unit laundry, ground floor, no parking
nice_to_haves: []        # each adds score, never gates
```

## 2. Source inventory → `src/config/sources.yaml`

For each source: name, concrete search URL(s) pre-filtered to the criteria,
retrieval mode (`browser` | `rss`), and polling notes.

| Source | Mode | Notes |
|--------|------|-------|
| Zillow (rentals) | browser | saved-search URL; logged-in session |
| Apartments.com | browser | saved-search URL |
| Facebook Marketplace | browser | most scam-prone; judge phase must be strict |
| Craigslist | rss | `.../search/apa?format=rss&...` pre-filtered feed |
| Local / university housing | browser or rss | e.g. Princeton off-campus housing site, local listservs — enumerate during this phase |

## 3. Push channel

- Pick a private, unguessable ntfy topic name (e.g. `aptbot-<random-suffix>`);
  record it in `src/config/notify.yaml` (topic name only — it *is* the secret,
  so keep the repo private / don't push the repo publicly with it).
- Install the ntfy app on phone, subscribe to the topic.
- Verify with a manual `curl -d "test" ntfy.sh/<topic>`.

## Checklist

- [ ] Collect criteria from Cameron (budget, anchor+commute, beds/baths, move-in, dealbreakers, nice-to-haves)
- [ ] Write `src/config/criteria.yaml`
- [ ] Enumerate concrete sources incl. local/Princeton ones; build pre-filtered search URLs
- [ ] Write `src/config/sources.yaml`
- [ ] Create ntfy topic, subscribe on phone, send test push
- [ ] Write `src/config/notify.yaml`
