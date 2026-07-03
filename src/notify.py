"""Push notifications via ntfy.sh, with flood guard and an alert trail.

Every alert (instant or summary) is appended to data/<profile>/alerts.log as a
JSON line, so there's always a reviewable record of what was pushed and why.

CLI:
    python src/notify.py --profile X push [--dry-run] < judged.json
    python src/notify.py --profile X test          # manual channel check

judged.json: array of {"listing": {...Listing...}, "score": int,
"reasons": [str, ...]} — the merge of retrieval output and judge verdicts.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone

from config import data_dir, load_profile
from schema import Listing


def _post(server: str, topic: str, body: str, headers: dict) -> None:
    req = urllib.request.Request(
        f"{server.rstrip('/')}/{topic}",
        data=body.encode("utf-8"),
        headers={k: v for k, v in headers.items() if v},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def _h(value: str) -> str:
    """HTTP headers are latin-1; strip emoji etc. from titles."""
    return value.encode("latin-1", "replace").decode("latin-1")


def _title(listing: Listing, score: int) -> str:
    parts = []
    if listing.price is not None:
        parts.append(f"${listing.price:,}")
    if listing.beds is not None:
        bb = f"{listing.beds:g}bd"
        if listing.baths is not None:
            bb += f"/{listing.baths:g}ba"
        parts.append(bb)
    where = listing.address or listing.title
    if where:
        parts.append(where[:60])
    return f"{' · '.join(parts)} (score {score})"


def _log_alert(slug: str, kind: str, listing: Listing, score: int | None,
               reasons: list[str], dry_run: bool) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": kind,                     # "instant" | "summary_item" | "test"
        "fingerprint": listing.fingerprint() if listing.source_id else None,
        "source": listing.source,
        "url": listing.url,
        "title": listing.title,
        "price": listing.price,
        "score": score,
        "reasons": reasons,
        "dry_run": dry_run,
    }
    with open(data_dir(slug) / "alerts.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def push(listing: Listing, score: int, reasons: list[str], notify_cfg: dict,
         slug: str, dry_run: bool = False) -> None:
    """One instant push for one qualifying listing."""
    ntfy = notify_cfg.get("ntfy", {})
    pol = notify_cfg.get("push", {})
    tags = "house,moneybag" if listing.raw.get("price_drop_from") else "house"
    body_lines = list(reasons[:3])
    if listing.raw.get("price_drop_from"):
        body_lines.insert(0, f"PRICE DROP: was ${listing.raw['price_drop_from']:,}")
    headers = {
        "Title": _h(_title(listing, score)),
        "Priority": "high" if score >= pol.get("high_priority_score", 90) else "default",
        "Click": listing.url,
        "Attach": listing.images[0] if listing.images else None,
        "Tags": tags,
    }
    if not dry_run:
        _post(ntfy["server"], ntfy["topic"], "\n".join(body_lines) or listing.title,
              headers)
    _log_alert(slug, "instant", listing, score, reasons, dry_run)


def push_summary(overflow: list[tuple[Listing, int, list[str]]], notify_cfg: dict,
                 slug: str, dry_run: bool = False) -> None:
    """One digest push for qualifying listings beyond the flood-guard cap."""
    ntfy = notify_cfg.get("ntfy", {})
    lines = [
        f"{_title(l, s)}\n{l.url}"
        for l, s, _ in overflow
    ]
    headers = {"Title": _h(f"+{len(overflow)} more matches"), "Tags": "house"}
    if not dry_run:
        _post(ntfy["server"], ntfy["topic"], "\n\n".join(lines), headers)
    for l, s, r in overflow:
        _log_alert(slug, "summary_item", l, s, r, dry_run)


def push_all(qualifying: list[tuple[Listing, int, list[str]]], notify_cfg: dict,
             slug: str, dry_run: bool = False) -> dict:
    """Flood guard: top-N instant pushes, the rest as one summary push."""
    cap = (notify_cfg.get("push", {}).get("flood_guard", {}) or {}).get("max_instant", 3)
    ranked = sorted(qualifying, key=lambda t: t[1], reverse=True)
    instant, overflow = ranked[:cap], ranked[cap:]
    for listing, score, reasons in instant:
        push(listing, score, reasons, notify_cfg, slug, dry_run)
    if overflow:
        push_summary(overflow, notify_cfg, slug, dry_run)
    return {"instant": len(instant), "summarized": len(overflow)}


def main() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="ntfy push helper")
    ap.add_argument("--profile")
    ap.add_argument("command", choices=["push", "test"])
    ap.add_argument("--dry-run", action="store_true",
                    help="log to alerts.log but send nothing")
    args = ap.parse_args()

    profile = load_profile(args.profile)
    notify_cfg = profile["notify"]
    if not (notify_cfg.get("ntfy") or {}).get("topic"):
        raise SystemExit("no ntfy topic — is profiles/<slug>/secrets.yaml in place?")

    if args.command == "test":
        l = Listing(source="test", source_id="", url="https://example.com",
                    title="AptBot channel test")
        _post(notify_cfg["ntfy"]["server"], notify_cfg["ntfy"]["topic"],
              "If you can read this, the push channel works.",
              {"Title": "AptBot: channel test", "Tags": "white_check_mark"})
        _log_alert(profile["slug"], "test", l, None, [], False)
        print("test push sent", file=sys.stderr)
        return

    rows = json.loads(sys.stdin.read().lstrip("﻿") or "[]")
    qualifying = [
        (Listing.from_dict(r["listing"]), int(r["score"]), list(r.get("reasons") or []))
        for r in rows
    ]
    result = push_all(qualifying, notify_cfg, profile["slug"], args.dry_run)
    print(f"notify: {result['instant']} instant, {result['summarized']} summarized"
          + (" (dry-run)" if args.dry_run else ""), file=sys.stderr)


if __name__ == "__main__":
    main()
