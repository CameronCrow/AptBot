# AptBot — Main Plan

An apartment-hunting bot that searches **all** major listing sources, judges each
listing against a renter's criteria, deduplicates against what they've already seen,
and pushes only genuinely new + good matches to their phone.

**Instantiable (pivot 2026-07-03):** the bot is not hardcoded to one search.
Each renter gets a *profile* (`profiles/<slug>/{criteria,sources,notify}.yaml`)
created by an instantiation interview (`docs/interview.md`) covering rent,
roommates, commute anchor, private bath, dishwasher, in-unit laundry, central
heat/cooling, and the rest. All code and playbooks are profile-parameterized
(`--profile <slug>`). First instance: `profiles/boston` — Cameron's own search
(anchor: One Kendall Square, Cambridge; group of 3; move-in Aug 1–Sep 1 2026).

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
- **Craigslist via script** — planned as RSS, but RSS is dead (403, verified
  2026-07-03); the poller now uses Craigslist's unofficial `sapi` JSON search
  endpoint (verified working). Still no browser and cheap enough to run every
  cycle; the browser playbook is the fallback if `sapi` changes.
- **This repo holds**: the plan, the Listing schema, the RSS poller, the dedup
  store, the notify helper, per-site search playbooks, and the criteria spec.
  The *agent definition + skill + schedule* live in Cameron's Claude workforce
  and reference this repo.
- **Push via ntfy.sh** — zero-account push to phone via a single HTTP POST to a
  private topic. Twilio SMS is a stretch goal, not the v1 path.
- **Discovered-source corpus (added 2026-07-03)** — `sources.yaml` holds only
  the metro-independent defaults; at instantiation a discovery pass
  web-searches the metro for local realtors, property managers, boards, and
  university off-campus lists and writes `profiles/<slug>/corpus.yaml`
  (active/candidate/needs-login/dead). Cycles poll corpus + defaults; a
  generic playbook (`docs/playbooks/generic-local.md`) covers small sites.

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

- **Phases 1–5 implemented** (2026-07-03). Code + config in this repo (26
  tests passing; craigslist pipeline verified live end-to-end); the
  `apartment-scout` agent and `apartment-hunt` skill live in the Workforce
  repo's new Housing Dept and are wired into `~/.claude/`.
- Open with Cameron before arming:
  1. Install the ntfy app and subscribe to the topic in
     `profiles/boston/secrets.yaml`.
  2. Confirm the `# ASSUMPTION` lines in `profiles/boston/criteria.yaml`
     (commute limit 30 min transit, dealbreakers, lease terms, target rent).
  3. Supervised dry run with his Chrome session (browser sources + judge
     calibration over ~20 listings).
  4. Register the schedule (resolve cloud-vs-local Chrome) → arm.
- Phase 6 (hardening) waits for ~2 weeks of live runs.
