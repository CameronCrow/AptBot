---
type: reference
tags: [repo/AptBot]
up: "[[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]"
---
# Phase 5 — Orchestration

Wire the pieces into Cameron's Claude workforce. The repo stays the source of
truth for config, code, and playbooks; the workforce provides the agent, the
skill, and the schedule.

## 1. `apartment-scout` agent (via add-employee flow)

- New employee, likely under a small "Housing" scope or standalone.
- System prompt: mission, points at this repo, follows the skill below.
- Browser access pattern copied from `canvas-syncer` (drives Cameron's
  logged-in Chrome).

## 2. `apartment-hunt` skill

The run loop, one cycle:

1. Read `criteria.yaml`, `sources.yaml`, `notify.yaml`.
2. Run `fetch_craigslist.py` (script) — collect Listings.
3. For each browser source: follow its playbook, extract new Listings; stop
   early at first already-seen id.
4. Pipe all Listings through `gates.py`, then the store's `is_new`.
5. Judge survivors per `docs/judge-rubric.md`.
6. `notify.push()` qualifying ones; `mark_seen` / `mark_alerted` everything.
7. Append a one-line run summary to `data/runs.log`
   (`checked N, new M, pushed K, errors []`).

Failure policy: one source failing (layout change, login wall) must not abort
the run — log it, continue, and include it in the run summary so it surfaces.

## 3. Scheduled routine

- `/schedule` cloud routine, 2–3×/day to start (e.g. 8:00 / 13:00 / 19:00) —
  browser sources are the bottleneck; Craigslist RSS could later poll more
  often via a separate lightweight schedule.
- Caveat to verify: scheduled cloud runs may not have the logged-in Chrome
  session available — if so, the routine falls back to RSS-only + a push
  nudging Cameron to trigger a full browser run locally. Resolve during dry
  runs.

## 4. End-to-end dry run

- Full cycle with `--dry-run` (judge + log, no push), review `runs.log` and
  would-have-pushed list with Cameron, then arm it.

## Status (2026-07-03)

- **Agent created**: `apartment-scout` in a new single-employee **Housing Dept**
  (`Workforce/agents/housing/apartment-scout/`, live via the `~/.claude/agents`
  junction). Browser posture copied from canvas-syncer (never logs in, never
  contacts sellers). Directors' org charts + workforce README updated.
- **Skill created**: `apartment-hunt` (`Workforce/skills/apartment-hunt/`) —
  cycle mode implements the 9-step run loop incl. failure policy and a
  first-run cap (~40 newest judged on a cold store); setup mode implements the
  instantiation interview from `docs/interview.md`.
- **Deterministic dry run done**: fetch → gates → filter-new → judged 10 newest
  per rubric → `notify --dry-run` (2 would-push: Belmont 4BR $3,950 score 74,
  Watertown 3BR $3,500 score 71) → `runs.log` + `alerts.log` written. Store
  deliberately left unmarked so the supervised run re-processes today's
  listings. Browser sources not exercised (needs Cameron's Chrome session).
- **Schedule deliberately not registered yet** (Cameron away when asked;
  defaulted to the plan's gate: supervised dry run first, then register + arm).
  Cloud caveat stands: scheduled cloud runs won't have logged-in Chrome —
  likely shape is RSS/sapi-only cloud runs + a push nudging a local browser
  run, or local scheduling. Decide at registration.

## Checklist

- [x] Create `apartment-scout` agent (housing dept, no director)
- [x] Write `apartment-hunt` skill implementing the run loop (+ setup/interview mode)
- [x] Failure policy encoded in skill + demonstrated in dry run (browser sources recorded as errored, run completed); full kill-a-source test during the supervised browser run
- [ ] Supervised dry run with Cameron: browser sources via his Chrome, review would-have-pushed list, calibrate judge (~20 listings)
- [ ] Register scheduled routine; resolve the cloud-vs-local-browser caveat → arm live pushes

## Related

- [[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]
- [[Repos/AptBot/planning/PHASE_4|PHASE_4]]
- [[Repos/AptBot/planning/PHASE_6|PHASE_6]]
- [[Repos/AptBot/docs/interview|interview]]
