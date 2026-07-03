"""Craigslist poller. Emits Listing JSON (array) to stdout.

Craigslist killed RSS (403 as of 2026-07), so this hits the unofficial JSON
endpoint the search SPA itself uses:

    https://sapi.craigslist.org/web/v8/postings/search/full
        ?batch={area_id}-0-360-0-0&cc=US&lang=en&searchPath=apa&{params}

Response decoding (reverse-engineered, verified live 2026-07-03):
    data.decode.minPostingId / minPostedDate — offsets for compact ints
    data.decode.locations[i] = [4, site, subarea] — URL construction
    each item: [idOffset, postedOffset, ?, price, "locIdx:nbhd~lat~lon",
                <token>, [tag, ...]..., "TITLE", ...]
    tagged arrays: 4=image ids, 5=[beds, sqft], 6=url slug, 10=price string

Being unofficial, the endpoint may change — the parser skips (and counts)
items it can't decode, and docs/playbooks/craigslist.md is the browser-mode
fallback if it breaks entirely.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from config import load_profile
from schema import Listing, write_listings

SAPI = "https://sapi.craigslist.org/web/v8/postings/search/full"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# tags for the typed sub-arrays inside an item
TAG_IMAGES, TAG_BEDS_SQFT, TAG_SLUG, TAG_PRICE_STR = 4, 5, 6, 10

_LOC_RE = re.compile(r"^(\d+):\S*~(-?\d+(?:\.\d+)?)~(-?\d+(?:\.\d+)?)")


def fetch_json(area_id: int, params: dict, batch_size: int = 360) -> dict:
    q = {
        "batch": f"{area_id}-0-{batch_size}-0-0",
        "cc": "US",
        "lang": "en",
        "searchPath": "apa",
        **{k: str(v) for k, v in (params or {}).items()},
    }
    url = f"{SAPI}?{urllib.parse.urlencode(q)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _image_urls(entries: list, limit: int = 3) -> list[str]:
    """"3:00J0J_abc_TOKEN" -> https://images.craigslist.org/00J0J_abc_TOKEN_600x450.jpg
    (verified live: the whole post-colon string is the image id)."""
    urls = []
    for e in entries[:limit]:
        if not isinstance(e, str) or ":" not in e:
            continue
        img_id = e.split(":", 1)[1]
        if img_id:
            urls.append(f"https://images.craigslist.org/{img_id}_600x450.jpg")
    return urls


def parse_item(item: list, decode: dict, category: str = "apa") -> Listing:
    posting_id = decode["minPostingId"] + item[0]
    posted = datetime.fromtimestamp(
        decode["minPostedDate"] + item[1], tz=timezone.utc
    ).isoformat()
    price = item[3] if isinstance(item[3], (int, float)) and item[3] > 0 else None

    slug = title = None
    beds = sqft = None
    images: list[str] = []
    loc_idx = lat = lon = None
    strings: list[str] = []

    for el in item:
        if isinstance(el, list) and el and isinstance(el[0], int):
            tag = el[0]
            if tag == TAG_SLUG and len(el) > 1:
                slug = el[1]
            elif tag == TAG_IMAGES:
                images = _image_urls(el[1:])
            elif tag == TAG_BEDS_SQFT:
                if len(el) > 1 and isinstance(el[1], (int, float)):
                    beds = float(el[1])
                if len(el) > 2 and isinstance(el[2], (int, float)):
                    sqft = el[2]
        elif isinstance(el, str):
            m = _LOC_RE.match(el)
            if m and "~" in el:
                loc_idx, lat, lon = int(m.group(1)), float(m.group(2)), float(m.group(3))
            else:
                strings.append(el)

    # the title is the longest bare string (others are short internal tokens)
    if strings:
        title = max(strings, key=len)
    if not slug or not title:
        raise ValueError(f"item {posting_id}: missing slug/title")

    site, subarea = "www", ""
    locations = decode.get("locations") or []
    if loc_idx is not None and 0 < loc_idx < len(locations):
        loc = locations[loc_idx]
        if isinstance(loc, list) and len(loc) >= 3:
            site, subarea = loc[1], loc[2]
    url = f"https://{site}.craigslist.org/{subarea}/{category}/d/{slug}/{posting_id}.html"

    return Listing(
        source="craigslist",
        source_id=str(posting_id),
        url=url,
        title=title,
        price=int(price) if price is not None else None,
        beds=beds,
        baths=None,                      # not present in search results
        address=None,                    # only lat/lon at search level
        available=None,
        posted=posted,
        description="",                  # judge opens the URL when needed
        images=images,
        raw={k: v for k, v in {"lat": lat, "lon": lon, "sqft": sqft}.items() if v is not None},
    )


def fetch_listings(source_cfg: dict) -> tuple[list[Listing], int]:
    data = fetch_json(int(source_cfg["area_id"]), source_cfg.get("params") or {})["data"]
    decode = data["decode"]
    listings, skipped = [], 0
    for item in data.get("items", []):
        try:
            listings.append(parse_item(item, decode))
        except Exception:
            skipped += 1
    return listings, skipped


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")   # emoji titles vs. Windows cp1252
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--profile", help="profile slug under profiles/")
    ap.add_argument("--limit", type=int, help="emit at most N listings")
    args = ap.parse_args()

    profile = load_profile(args.profile)
    sources = [
        s for s in profile["sources"].get("sources", [])
        if s.get("name") == "craigslist" and s.get("mode") == "script" and s.get("enabled", True)
    ]
    if not sources:
        print("no enabled script-mode craigslist source in profile", file=sys.stderr)
        write_listings([], sys.stdout)
        return

    all_listings: list[Listing] = []
    for src in sources:
        listings, skipped = fetch_listings(src)
        all_listings.extend(listings)
        print(
            f"craigslist[{src.get('site', '?')}]: {len(listings)} listings"
            + (f", {skipped} unparseable (skipped)" if skipped else ""),
            file=sys.stderr,
        )
    if args.limit:
        all_listings = all_listings[: args.limit]
    write_listings(all_listings, sys.stdout)


if __name__ == "__main__":
    main()
