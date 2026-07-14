---
type: reference
tags: [repo/AptBot]
up: "[[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]"
---
# Phase 1 — Criteria & source inventory

> **Pivot (2026-07-03):** during criteria collection Cameron redirected the
> design — AptBot must be **instantiable** for any renter, not hardcoded to one
> search. Instantiation = an interview that produces a **profile**:
> `profiles/<slug>/{criteria,sources,notify}.yaml`. The interview script lives
> in [`docs/interview.md`](../docs/interview.md); blank templates in
> `profiles/_template/`. All code takes `--profile <slug>`. The first instance
> is `profiles/boston` (Cameron's own search — Boston, not Princeton).

The whole "judge" step hinges on a precise spec. A vague spec makes the bot
noisy (pushes junk) or silent (over-filters). This phase produces the profile
system, the interview, and the first profile.

## 1. Interview → `docs/interview.md` + `profiles/_template/`

Four parts: criteria (budget/group/commute/dealbreakers/nice-to-haves —
including private bath, dishwasher, in-unit laundry, central heat/AC prompts),
sources (craigslist area id + portal URLs + local boards), push channel (ntfy
topic), wire-up. Hard vs. soft constraints kept distinct; unanswered items are
recorded with `# ASSUMPTION` comments rather than silently defaulted.

## 2. First instance → `profiles/boston/`

From Cameron's interview answers (2026-07-03):

- **Budget**: $2,000/mo hard ceiling for his share; group of 3 (2 roommates)
  → whole-unit ceiling $6,000.
- **Shapes**: whole 3BR+ for the group, or rooms in a shared household.
- **Anchor**: One Kendall Square, Cambridge, MA (his work).
- **Move-in**: 2026-08-01 → 2026-09-01.
- Commute mode/limit, dealbreakers, lease terms not yet answered — recorded as
  `# ASSUMPTION` in `criteria.yaml` (transit ≤ 30 min; no dealbreakers;
  nice-to-haves seeded from his interview-topic examples). **Follow up.**

## 3. Sources (boston instance)

| Source | Mode | Notes |
|--------|------|-------|
| Craigslist | script | **RSS is dead** (403, verified 2026-07-03) — poller uses the unofficial `sapi.craigslist.org` JSON endpoint instead (boston `area_id=4`, verified live). Browser playbook kept as fallback. |
| Zillow | browser | Cambridge / Somerville / Charlestown rentals URLs; agent applies filters in UI |
| Apartments.com | browser | path-encoded filters: `/cambridge-ma/3-bedrooms-under-6000/` |
| FB Marketplace | browser | most scam-prone; judge applies stricter prior |
| Local boards | — | superseded by the **discovered-source corpus** (2026-07-03): discovery pass seeded `profiles/boston/corpus.yaml` with 11 localized sources — 7 active (Boston Pads, 4 local realtors, Harvard off-campus board, r/bostonhousing), 3 candidate (Coldwell Banker, 2 FB housing groups — need membership/vetting), 1 needs-login (MIT board, Kerberos-walled) |

## 4. Push channel

Topic created (`aptbot-boston-…`); test push delivered 2026-07-03. The topic
name is the secret and the GitHub remote is **public**, so the topic lives only
in gitignored `profiles/boston/secrets.yaml`. Cameron still needs to install
the ntfy app and subscribe (topic name is in that file).

## Checklist

- [x] Collect criteria from Cameron (budget, anchor, group, move-in; commute limit + dealbreakers still assumed — follow up)
- [x] Design instantiable profile system: `profiles/_template/` + `docs/interview.md`
- [x] Write `profiles/boston/criteria.yaml`
- [x] Enumerate sources; verify craigslist retrieval path (RSS dead → sapi JSON)
- [x] Write `profiles/boston/sources.yaml`
- [x] Create ntfy topic, send test push
- [x] Write `profiles/boston/notify.yaml`
- [ ] Cameron: install ntfy app, subscribe to topic, confirm push arrives
- [ ] Cameron: confirm the `# ASSUMPTION` lines in `criteria.yaml`

## Related

- [[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]
- [[Repos/AptBot/planning/PHASE_2|PHASE_2]]
- [[Repos/AptBot/docs/interview|interview]]
- [[Repos/AptBot/planning/TODO|TODO]]
