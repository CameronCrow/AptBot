"""Hard gates — cheap deterministic filters run before the LLM judge.

Only certain misses are dropped; anything ambiguous (missing price, beds,
address, availability) passes through to the judge. A listing survives if it
could plausibly satisfy ANY listing shape the profile seeks (whole_unit for
the group, and/or room_in_shared).

CLI: python src/gates.py --profile X < listings.json > survivors.json
     (reject counts by reason on stderr)
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date

from config import load_profile
from schema import Listing, read_listings, write_listings


def _iso(d) -> date | None:
    if d is None:
        return None
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d)[:10])
    except ValueError:
        return None


def gate(listing: Listing, criteria: dict) -> tuple[bool, list[str]]:
    """(passes, reasons-it-failed). Missing fields never fail a check."""
    budget = criteria.get("budget", {})
    group = criteria.get("group", {})
    unit = criteria.get("unit", {})
    location = criteria.get("location", {})
    move_in = criteria.get("move_in", {})

    shapes = group.get("seeking") or ["whole_unit"]
    size = int(group.get("size") or 1)
    max_share = budget.get("max_rent")
    unit_ceiling = max_share * size if max_share else None
    room_ceiling = max_share
    beds_min = unit.get("beds_min")

    reasons: list[str] = []

    # ---- shape/budget/beds: survive if any sought shape is plausible ----
    plausible = []
    if "whole_unit" in shapes:
        ok = True
        if beds_min is not None and listing.beds is not None and listing.beds < beds_min:
            ok = False
        if unit_ceiling is not None and listing.price is not None and listing.price > unit_ceiling:
            ok = False
        plausible.append(("whole_unit", ok))
    if "room_in_shared" in shapes:
        # rooms often report the house's total beds, so beds never disqualify;
        # a room just can't cost more than the renter's own ceiling
        ok = not (room_ceiling is not None and listing.price is not None
                  and listing.price > room_ceiling)
        plausible.append(("room_in_shared", ok))
    if plausible and not any(ok for _, ok in plausible):
        if listing.price is not None and unit_ceiling is not None and listing.price > unit_ceiling:
            reasons.append(f"over_budget:{listing.price}>{unit_ceiling}")
        else:
            reasons.append("no_sought_shape_fits")

    # ---- excluded areas (hard) ----
    areas_no = [a.lower() for a in (location.get("areas_no") or [])]
    haystack = " ".join(filter(None, [listing.address, listing.title])).lower()
    for area in areas_no:
        if area and area in haystack:
            reasons.append(f"excluded_area:{area}")
            break

    # ---- availability past the move-in window (hard) ----
    latest = _iso(move_in.get("latest"))
    available = _iso(listing.available)
    if latest and available and available > latest:
        reasons.append(f"available_too_late:{available.isoformat()}")

    return (not reasons, reasons)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="hard gates (pre-LLM filters)")
    ap.add_argument("--profile")
    args = ap.parse_args()

    criteria = load_profile(args.profile)["criteria"]
    listings = read_listings(sys.stdin)

    survivors: list[Listing] = []
    rejects: Counter[str] = Counter()
    for l in listings:
        ok, reasons = gate(l, criteria)
        if ok:
            survivors.append(l)
        else:
            rejects[reasons[0].split(":")[0]] += 1

    write_listings(survivors, sys.stdout)
    summary = ", ".join(f"{k}={v}" for k, v in rejects.most_common()) or "none"
    print(f"gates: {len(survivors)}/{len(listings)} passed; rejects: {summary}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
