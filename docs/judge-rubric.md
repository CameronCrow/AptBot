---
type: reference
tags: [repo/AptBot]
up: "[[Repos/AptBot/docs/DOCS_MAIN|DOCS_MAIN]]"
---
# Judge rubric

The judge is the LLM step: the apartment-scout agent scores every listing that
survived the hard gates and dedup. Inputs per listing: the `Listing` JSON, the
profile's `criteria.yaml`, and recent price context from the store
(`Store.recent_comps(beds)`). Output per listing:

```json
{
  "fingerprint": "...",
  "score": 0-100,
  "verdict": "push" | "skip",
  "reasons": ["top 2-3 human-readable reasons, best first"],
  "scam_flags": []
}
```

`verdict: push` requires **score ≥ `push.min_score`** (from `notify.yaml`,
default 70) **and zero scam flags**. When unsure whether a flag is real,
include it — a missed great listing costs less than a scam push at 7am.

## Scoring: start at 50, then adjust

### Fit (±30)

- Shape match: qualifies cleanly as a sought shape (`whole_unit` with
  `beds_min`+ beds, or `room_in_shared` at ≤ the per-person ceiling). A listing
  that only *maybe* fits a shape (e.g. beds unknown) caps Fit at +10.
- `budget.target_rent`: at/below target (per-person share) → up to +10;
  between target and max → 0; there is no over-max case (gated).
- Availability inside `move_in` window → +5; more than ~1 month before
  `earliest` (dead rent) → −10; unstated → 0 and mention in reasons.
- Each `nice_to_have` clearly present → +3 (cap +12). Each `dealbreaker`
  clearly present → **verdict skip** regardless of score (it's a hard NO that
  the gates couldn't see from structured fields).
- `lease` mismatch (short sublet when `sublets_ok: false`) → −15.

### Commute (±20)

Estimate door-to-door minutes from the listing's address/area to
`location.anchor` by `location.commute_mode` (use knowledge of the metro's
transit/geography; be conservative when only a neighborhood is known).

- ≤ half of `max_commute_min` → +20
- within `max_commute_min` → +10 to 0 (sliding)
- over the limit → −20; *far* over (≥ 2×) → verdict skip
- Address too vague to estimate → 0, add "commute unverified" to reasons.

### Value (±15)

Compare price to `recent_comps(beds)` from the store (median of the last two
weeks of same-beds listings). No comps yet (cold store) → 0, don't guess hard.

- ≥ 10% below median → +15 (and check Scam — bargains are bait)
- around median → +5 to 0
- ≥ 10% above median → −10

### Scam risk (flags, not points)

Flag anything matching (record verbatim evidence in `scam_flags`):

- Price far below area rate (the +15 Value case *is* a scam signal — the two
  sections must be read together)
- Wire transfer, gift cards, crypto, Zelle-before-viewing, deposit to "hold"
- No interior photos, stock/watermarked photos, photos inconsistent with unit
- Urgency pressure ("many applicants, send deposit today")
- Landlord out of country / "traveling, my agent will mail keys"
- Contact redirection off-platform in the first message ("text me at…")
- **Stricter prior for `craigslist` and `fb_marketplace`**: on these sources,
  treat *one* strong tell as flag-worthy; on Zillow/Apartments.com verified
  listings, require more than one weak tell.

Any flag → `verdict: skip` (the alert trail still logs it, so nothing is
silently lost).

## Calibration

- [ ] Run the rubric over ~20 real Boston listings, eyeball scores with
      Cameron, and adjust the weights above (pending — needs the Phase 5
      browser run for a realistic sample).
- Tuning knobs live in `notify.yaml` (`min_score`, `high_priority_score`);
  weight changes belong here, in prose, so the judge and humans stay in sync.

## Related

- [[Repos/AptBot/docs/DOCS_MAIN|DOCS_MAIN]]
- [[Repos/AptBot/docs/interview|interview]]
- [[Repos/AptBot/planning/PHASE_3|PHASE_3]]
