# Phase 6 — Hardening (stretch)

Only after the v1 loop has run for a week or two. Candidates, in rough order
of value:

- **Score feedback loop** — Cameron reacts to pushes (👍/👎 via ntfy action
  buttons or a quick note); reactions logged and folded into the judge rubric
  as few-shot examples. Tune the push threshold from real data.
- **Price-drop tracking** — activate the store's price-change hook: re-alert
  when a previously-seen listing drops price meaningfully (≥ $50 or ≥ 3%).
- **Twilio SMS** — real texts instead of / in addition to ntfy, if push proves
  too easy to miss. Costs cents/msg + account setup; only if needed.
- **More frequent Craigslist polling** — RSS is cheap; a separate 15–30 min
  lightweight schedule for RSS-only, keeping browser runs at 2–3×/day.
- **Weekly digest** — Sunday summary push/email: market overview, price
  trends from the store, anything skipped that was borderline.

## Checklist

- [ ] Decide which hardening items are worth it after ~2 weeks of live runs
- [ ] Implement chosen items (each gets its own mini-checklist here)
