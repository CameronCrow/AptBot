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

## Checklist

- [ ] Create `apartment-scout` agent
- [ ] Write `apartment-hunt` skill implementing the run loop
- [ ] Failure policy verified (kill one source mid-run → run completes)
- [ ] Register scheduled routine; resolve the cloud-vs-local-browser caveat
- [ ] Dry run reviewed with Cameron → arm live pushes
