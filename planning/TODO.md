---
type: reference
tags: [repo/AptBot]
up: "[[AptBot]]"
---
# TODO

- [x] **Phase 1 — Criteria & source inventory**: instantiable profiles (`profiles/_template/` + interview), `profiles/boston/*`, ntfy topic live
- [x] **Phase 2 — Retrieval**: Listing schema, Craigslist poller (sapi JSON — RSS is dead), browser playbooks per source
- [x] **Phase 3 — Judge & dedup**: SQLite seen-store, hard gates, judge rubric (+ tests; calibration pass pending Phase 5 dry run)
- [x] **Phase 4 — Notify**: ntfy push helper, flood guard, alert trail
- [x] **Phase 5 — Orchestration**: `apartment-scout` agent + `apartment-hunt` skill live; deterministic dry run done (supervised browser dry run + schedule registration → arm still pending with Cameron)
- [x] **Extension — Discovered-source corpus**: per-profile `corpus.yaml` (local realtors/boards/university lists) populated by a discovery pass at instantiation; cycles poll corpus + defaults; boston corpus seeded (11 sources)
- [ ] **Phase 6 — Hardening (stretch)**: feedback loop, price-drop alerts, Twilio, digest

## Related

- [[Repos/AptBot/planning/PLAN_MAIN|PLAN_MAIN]]
- [[Repos/AptBot/planning/PHASE_5|PHASE_5]]
- [[Repos/AptBot/planning/PHASE_6|PHASE_6]]
