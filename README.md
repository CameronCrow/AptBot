# AptBot

An apartment-hunting bot: an `apartment-scout` Claude agent drives a logged-in
browser (Zillow, Apartments.com, FB Marketplace, local sites) and a small
Craigslist RSS poller, judges each listing against Cameron's criteria
(fit / commute / value / scam risk), dedupes against a local seen-store, and
pushes only new + good matches to his phone via ntfy.sh.

Hybrid design: judgment-heavy, fragile parts live in the agent; deterministic
parts (schema, RSS poller, dedup store, gates, notify helper) live in `src/`.

See `planning/PLAN_MAIN.md` for the full plan and current state.
