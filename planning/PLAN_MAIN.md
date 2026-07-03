# AptBot — Main Plan

An apartment-hunting bot that searches **all** major listing sources, judges each
listing against Cameron's criteria, deduplicates against what he's already seen,
and pushes only genuinely new + good matches to his phone.

## Architecture (decided)

The bot is a **hybrid**: an agent-driven workflow (Claude Code) for the fragile,
judgment-heavy parts, and a small amount of durable code in this repo for the
deterministic parts.

```
scheduled routine (2–3×/day)
        │
        ▼
apartment-scout agent ──drives Chrome (logged-in)──▶ Zillow, Apartments.com,
        │                                             FB Marketplace, local sites
        │           └────RSS fetch (script)─────────▶ Craigslist
        ▼
judge each listing (fit? scam? commute? overpriced?)   ← LLM value-add
        │
        ▼
dedup vs. local seen-listings store ──▶ only genuinely new + good survive
        │
        ▼
ntfy.sh POST ──▶ 📱 push notification
```

Key decisions and their rationale:

- **Browser-driving agent, not a headless scraper**, for the big portals
  (Zillow, Apartments.com, FB Marketplace). These sites have no clean public
  API and actively block headless scrapers; driving Cameron's logged-in Chrome
  session is human-paced, authenticated, and far less brittle.
- **Craigslist via RSS** — the one source with a cheap machine-readable feed;
  poll it with a small script instead of burning agent time.
- **This repo holds**: the plan, the Listing schema, the RSS poller, the dedup
  store, the notify helper, per-site search playbooks, and the criteria spec.
  The *agent definition + skill + schedule* live in Cameron's Claude workforce
  and reference this repo.
- **Push via ntfy.sh** — zero-account push to phone via a single HTTP POST to a
  private topic. Twilio SMS is a stretch goal, not the v1 path.

## Phase index

| Phase | File | Summary |
|-------|------|---------|
| 1 | [PHASE_1.md](PHASE_1.md) | **Criteria & source inventory** — define search criteria (`criteria.yaml`), enumerate concrete sources/URLs, set up the ntfy topic. The spec that makes the bot good vs. noisy. |
| 2 | [PHASE_2.md](PHASE_2.md) | **Retrieval** — Listing schema, Craigslist RSS poller, per-site browser playbooks for the agent to follow. |
| 3 | [PHASE_3.md](PHASE_3.md) | **Judge & dedup** — scoring rubric, scam heuristics, SQLite seen-listings store. |
| 4 | [PHASE_4.md](PHASE_4.md) | **Notify** — ntfy push helper, alert formatting, instant-vs-digest policy. |
| 5 | [PHASE_5.md](PHASE_5.md) | **Orchestration** — `apartment-scout` agent + skill, scheduled routine, end-to-end dry run. |
| 6 | [PHASE_6.md](PHASE_6.md) | **Hardening (stretch)** — Twilio SMS, feedback loop on scores, price-drop tracking. |

## Current State

- Repo scaffolded from PROJECT_TEMPLATE; full plan written (all phase files +
  TODO). No implementation yet.
- Next action: Phase 1 — Cameron supplies search criteria (budget, location /
  commute anchor, beds/baths, move-in date, dealbreakers) so `criteria.yaml`
  can be filled in.
