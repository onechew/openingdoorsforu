#!/usr/bin/env python3
"""Fetch Thapar Team featured listings (searchid=3952868) into data/listings.json."""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.parse
from pathlib import Path


class CloudflareBlockedError(RuntimeError):
    """Raised when thaparteam.ca returns a Cloudflare bot challenge HTML page."""

ROOT = Path(__file__).resolve().parents[1]
LISTINGS_PATH = ROOT / "data" / "listings.json"
ACTIVE_JS = ROOT / "assets" / "active-listings.js"
SEARCH_PARAMS_PATH = ROOT / "data" / "thapar-search-params.json"
SEARCH_URL = "https://www.thaparteam.ca/property-search/results/?searchid=3952868"
API_URL = (
    "https://www.thaparteam.ca/property-search/res/includes/"
    "search_application/get_listings.asp"
)
ORIGIN_THAPAR = "https://www.thaparteam.ca"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
SEARCH_PARAMS_RE = re.compile(
    r"var\s+searchParams\s*=\s*(\{.*?\})\s*;\s*var\s+regionParams",
    re.S,
)

# Neighbourhoods that sit in Etobicoke even when city says Toronto
ETOBICOKE_HOODS = {
    "mimico",
    "islington",
    "islington-city centre west",
    "stonegate-queensway",
    "long branch",
    "alderwood",
    "new toronto",
    "sunnylea",
    "the kingsway",
    "edenbridge-humber valley",
    "humber heights",
    "kingsview village-the westway",
    "willowridge-martingrove-richview",
    "west humber-clairville",
    "elms-old rexdale",
    "rexdale-kipling",
    "mount olive-silverstone-jamestown",
    "thistletown-beaumonde heights",
    "humbermede",
    "humberlea-pelmo park w5",
    # note: "weston" is NOT Etobicoke (former City of York)
}


def _curl_get(url: str) -> str:
    return subprocess.check_output(
        [
            "curl",
            "-sL",
            "--max-time",
            "45",
            "-A",
            BROWSER_UA,
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "-H",
            "Accept-Language: en-CA,en;q=0.9",
            url,
        ],
        text=True,
    )


def _looks_like_cloudflare(raw: str) -> bool:
    head = (raw or "")[:4000].lower()
    return (
        "just a moment..." in head
        or "/cdn-cgi/challenge-platform" in head
        or "cf-chl" in head
        or "cf-browser-verification" in head
    )


def _parse_search_params(html: str) -> dict | None:
    m = SEARCH_PARAMS_RE.search(html or "")
    if not m:
        return None
    return json.loads(m.group(1))


def _load_cached_search_params() -> dict | None:
    if not SEARCH_PARAMS_PATH.is_file():
        return None
    try:
        data = json.loads(SEARCH_PARAMS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) and data.get("searchId") else None


def _save_search_params(params: dict) -> None:
    SEARCH_PARAMS_PATH.write_text(
        json.dumps(params, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def fetch_search_params() -> dict:
    """Load live Thapar searchParams; fall back to cached JSON for CI/bot blocks."""
    html = ""
    try:
        html = _curl_get(SEARCH_URL)
        if _looks_like_cloudflare(html):
            raise CloudflareBlockedError(
                "Thapar search page blocked by Cloudflare bot challenge "
                f"(len={len(html)}). GitHub Actions IPs cannot scrape thaparteam.ca."
            )
        live = _parse_search_params(html)
        if live:
            _save_search_params(live)
            return live
    except CloudflareBlockedError:
        raise
    except subprocess.CalledProcessError as err:
        print(f"  Live search page fetch failed ({err.returncode}); trying cache…")
    else:
        snippet = re.sub(r"\s+", " ", (html or "")[:240]).strip()
        print(
            "  Live search page missing searchParams "
            f"(len={len(html or '')}, head={snippet!r}); trying cache…"
        )

    cached = _load_cached_search_params()
    if cached:
        print(f"  Using cached searchParams (searchId={cached.get('searchId')})")
        return cached
    raise RuntimeError("Could not find searchParams on Thapar search page (no cache)")


def post_listings(base: dict, page: int, page_size: int = 12) -> dict:
    sp = json.loads(json.dumps(base))
    sp["search"]["offset"] = {
        "pageSize": page_size,
        "pageNumber": page,
        "listingId": "",
    }
    body = urllib.parse.urlencode(
        {
            "searchParameters": json.dumps(sp, separators=(",", ":")),
            "pageSize": str(page_size),
            "pageNumber": str(page),
        }
    )
    tmp = ROOT / ".tmp-thapar-body.txt"
    out = ROOT / ".tmp-thapar-out.json"
    tmp.write_text(body, encoding="utf-8")
    try:
        subprocess.check_call(
            [
                "curl",
                "-sL",
                "--max-time",
                "45",
                API_URL,
                "-H",
                f"User-Agent: {BROWSER_UA}",
                "-H",
                "Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
                "-H",
                "X-Requested-With: XMLHttpRequest",
                "-H",
                "Accept: application/json, text/javascript, */*; q=0.01",
                "-H",
                "Origin: https://www.thaparteam.ca",
                "-H",
                f"Referer: {SEARCH_URL}",
                "--data-binary",
                f"@{tmp}",
                "-o",
                str(out),
            ]
        )
        raw = out.read_text(encoding="utf-8")
        if _looks_like_cloudflare(raw):
            raise CloudflareBlockedError(
                "Thapar listings API blocked by Cloudflare bot challenge "
                f"(len={len(raw)}). GitHub Actions IPs cannot scrape thaparteam.ca."
            )
        try:
            return json.loads(raw)
        except json.JSONDecodeError as err:
            raise RuntimeError(
                f"Thapar listings API returned non-JSON (len={len(raw)}): {raw[:200]!r}"
            ) from err
    finally:
        tmp.unlink(missing_ok=True)
        out.unlink(missing_ok=True)


def fetch_all_properties(base: dict) -> list[dict]:
    """Pull every page from the Thapar featured search (typically 12/page, 4 pages)."""
    first = post_listings(base, page=1, page_size=12)
    total_records = int(first.get("totalRecords") or 0)
    total_pages = int(first.get("totalPages") or 1)
    if total_pages < 1:
        total_pages = 1
    # Prefer totalRecords when totalPages looks stale
    if total_records > 0:
        total_pages = max(total_pages, (total_records + 11) // 12)

    all_props: list[dict] = []
    seen: set = set()
    for page in range(1, total_pages + 1):
        data = first if page == 1 else post_listings(base, page=page, page_size=12)
        chunk = data.get("properties") or []
        print(f"  Thapar page {page}/{total_pages}: {len(chunk)} listings")
        for p in chunk:
            mid = str(p.get("mls") or p.get("mlsId") or "")
            if not mid or mid in seen:
                continue
            seen.add(mid)
            all_props.append(p)

    if total_records and len(all_props) < total_records:
        raise RuntimeError(
            f"Incomplete Thapar sync: got {len(all_props)} of {total_records}"
        )
    return all_props


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s


def map_area(city: str, hood: str) -> str:
    city_l = (city or "").strip().lower()
    hood_l = (hood or "").strip().lower()
    if hood_l in ETOBICOKE_HOODS or "etobicoke" in hood_l:
        return "Etobicoke"
    if city_l == "toronto":
        if any(x in hood_l for x in ("willowdale", "north york", "yorkdale")):
            return "North York"
        if any(x in hood_l for x in ("waterfront", "church-yonge", "bay street")):
            return "Downtown Toronto"
        return "West Toronto" if hood_l else "Toronto"
    if city_l == "mississauga":
        return "Mississauga"
    if city_l == "vaughan":
        return "Vaughan"
    if city_l in {"markham"}:
        return "Markham"
    if city_l in {"richmond hill"}:
        return "Richmond Hill"
    if city_l:
        return city.title()
    return "GTA"


def clean_hood(hood: str) -> str:
    """Strip TRREB municipal codes like '981 - Lincoln Lake' → 'Lincoln Lake'."""
    raw = (hood or "").strip()
    raw = re.sub(r"^\d+\s*-\s*", "", raw)
    return raw.strip()


def format_title(address1: str) -> str:
    # Feed sometimes inserts "N/A" as a placeholder unit token
    title = re.sub(r"\s+", " ", (address1 or "").strip())
    title = re.sub(r"\s+N/A\b", "", title, flags=re.I)
    title = re.sub(r"\s{2,}", " ", title).strip()
    return title


def photo_url(prop: dict) -> str:
    photos = prop.get("photos") or {}
    if isinstance(photos, dict):
        for key in ("primary", "url", "main"):
            if photos.get(key):
                return str(photos[key]).strip()
        imgs = photos.get("images") or photos.get("items") or []
        if imgs and isinstance(imgs[0], dict):
            return str(imgs[0].get("url") or imgs[0].get("src") or "").strip()
        if imgs and isinstance(imgs[0], str):
            return imgs[0].strip()
    if isinstance(photos, list) and photos:
        p0 = photos[0]
        return str(p0.get("url") if isinstance(p0, dict) else p0).strip()
    return ""


def convert(prop: dict) -> dict:
    address = format_title(prop.get("address1") or "")
    if not address:
        raise ValueError(f"Missing address for MLS {prop.get('mls')}")
    city = (prop.get("city") or "").strip()
    hood_raw = (
        (prop.get("neighborhood") or {}).get("value")
        or prop.get("subDivision")
        or ""
    ).strip()
    hood = clean_hood(hood_raw)
    area = map_area(city, hood_raw)  # map on raw/cleaned-insensitive set
    # Remap using cleaned hood too
    if area == "West Toronto" or area == "Toronto":
        area = map_area(city, hood)
    location = " · ".join(x for x in [hood or None, city or None] if x)
    beds = prop.get("beds") or {}
    baths = prop.get("baths") or {}
    bed_n = beds.get("count") if isinstance(beds, dict) else beds
    bath_n = baths.get("count") if isinstance(baths, dict) else baths
    typ = re.sub(r"\s+", " ", (prop.get("listTypeDescrip") or "Home").strip())
    mls = (prop.get("mls") or "").strip()
    if not mls:
        raise ValueError(f"Missing MLS for {address}")
    detail = (prop.get("detailUrl") or "").strip()
    if detail.startswith("/"):
        detail = ORIGIN_THAPAR + detail
    if not detail.startswith("http"):
        raise ValueError(f"Bad detail URL for {mls}: {detail!r}")
    price = (prop.get("price") or "").strip()
    if not price:
        raise ValueError(f"Missing price for {mls}")
    # These are active sale listings from the featured office search — never invent lease/sold.
    status_raw = (prop.get("status") or "").strip()
    if status_raw and status_raw.lower() not in {"active", "new", "price change"}:
        # Skip non-active inventory rather than mislabel
        raise ValueError(f"Non-active status for {mls}: {status_raw}")
    office = ((prop.get("office") or {}).get("name") or "Snobar Realty Group Inc.").strip()
    img = photo_url(prop)
    if not img:
        raise ValueError(f"Missing photo for {mls}")
    slug = slugify(f"{address}-{mls}")

    item = {
        "title": address,
        "location": location,
        "area": area,
        "status": "For Sale",
        "tagClass": "sale",
        "price": price,
        "mls": mls,
        "type": typ,
        "image": img,
        "alt": f"{address} · {location} · listed with {office} · available via Thapar Team",
        "url": detail,
        "slug": slug,
        "kind": "team",
        "source": "thapar",
        "office": office,
        "attribution": f"Listed with {office}",
    }
    if bed_n not in (None, "", 0, "0"):
        item["beds"] = str(int(bed_n) if isinstance(bed_n, float) and bed_n == int(bed_n) else bed_n)
    if bath_n not in (None, "", 0, "0"):
        item["baths"] = str(int(bath_n) if isinstance(bath_n, float) and bath_n == int(bath_n) else bath_n)
    return item


def verify_against_source(team: list[dict], props: list[dict]) -> None:
    """Hard fail if any displayed field drifts from the live feed."""
    by_mls = {str(p.get("mls")): p for p in props}
    if len(team) != len(by_mls):
        # allow josh-overlap filtering only smaller
        pass
    errors = []
    for item in team:
        mls = item["mls"]
        p = by_mls.get(mls)
        if not p:
            errors.append(f"{mls}: not in source feed")
            continue
        src_title = format_title(p.get("address1") or "")
        if item["title"] != src_title:
            errors.append(f"{mls}: title {item['title']!r} != {src_title!r}")
        src_price = (p.get("price") or "").strip()
        if item["price"] != src_price:
            errors.append(f"{mls}: price {item['price']!r} != {src_price!r}")
        src_type = re.sub(r"\s+", " ", (p.get("listTypeDescrip") or "").strip())
        if item.get("type") != src_type:
            errors.append(f"{mls}: type {item.get('type')!r} != {src_type!r}")
        beds = (p.get("beds") or {}).get("count")
        baths = (p.get("baths") or {}).get("count")
        if beds not in (None, "", 0, "0") and item.get("beds") != str(int(beds) if isinstance(beds, float) and beds == int(beds) else beds):
            errors.append(f"{mls}: beds {item.get('beds')!r} != {beds!r}")
        if baths not in (None, "", 0, "0") and item.get("baths") != str(int(baths) if isinstance(baths, float) and baths == int(baths) else baths):
            errors.append(f"{mls}: baths {item.get('baths')!r} != {baths!r}")
        detail = (p.get("detailUrl") or "").strip()
        if detail.startswith("/"):
            detail = ORIGIN_THAPAR + detail
        if item.get("url") != detail:
            errors.append(f"{mls}: url mismatch")
        if item.get("kind") != "team" or item.get("source") != "thapar":
            errors.append(f"{mls}: missing team attribution flags")
        if "josh" in (item.get("alt") or "").lower() and "listed" in (item.get("alt") or "").lower():
            errors.append(f"{mls}: alt implies Josh listed this home")
        if item.get("status") != "For Sale":
            errors.append(f"{mls}: status must be For Sale for this feed")
    if errors:
        raise SystemExit("Team listing verification failed:\n- " + "\n- ".join(errors))


def write_active_js(josh: list[dict], team: list[dict], synced_at: str) -> None:
    """Homepage loads this file for Active Listings cards."""
    combined = list(josh) + list(team)
    slim = []
    for item in combined:
        row = {
            "title": item["title"],
            "location": item.get("location") or "",
            "status": item.get("status") or "For Sale",
            "tagClass": item.get("tagClass") or "sale",
            "price": item.get("price") or "",
            "image": item.get("image") or "assets/JS.jpg",
            "alt": item.get("alt") or item["title"],
            "url": item.get("url") or "",
            "kind": item.get("kind") or "active",
            "source": item.get("source") or "",
        }
        for key in ("beds", "baths", "parking", "size", "type", "mls", "area", "office", "attribution"):
            if item.get(key) not in (None, ""):
                row[key] = item[key]
        slim.append(row)
    stamp = re.sub(r"[^\d]", "", synced_at)[:14] or "1"
    ACTIVE_JS.write_text(
        "window.__ACTIVE_LISTINGS_META__ = "
        + json.dumps(
            {
                "syncedAt": synced_at,
                "teamCount": len(team),
                "joshCount": len(josh),
                "source": SEARCH_URL,
            },
            ensure_ascii=False,
        )
        + ";\n"
        + "window.__ACTIVE_LISTINGS__ = "
        + json.dumps(slim, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    bump_active_listings_cache(stamp)


def bump_active_listings_cache(stamp: str) -> None:
    index = ROOT / "index.html"
    html = index.read_text(encoding="utf-8")
    updated = re.sub(
        r'src="assets/active-listings\.js(?:\?v=[^"]*)?"',
        f'src="assets/active-listings.js?v={stamp}"',
        html,
        count=1,
    )
    if updated != html:
        index.write_text(updated, encoding="utf-8")


def main() -> None:
    from datetime import datetime, timezone

    synced_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    print("Fetching Thapar featured search…")
    try:
        base = fetch_search_params()
        props = fetch_all_properties(base)
    except CloudflareBlockedError as err:
        print(f"ERROR: {err}")
        # Cron soft-skip: exit 0 so a re-enabled schedule stays green and keeps
        # the last committed inventory. Manual workflow_dispatch / local runs fail.
        if os.environ.get("GITHUB_EVENT_NAME") == "schedule":
            print(
                "Scheduled sync skipped; keeping last committed listings. "
                "Refresh by running `python3 scripts/sync-team-listings.py` locally "
                "(or from a self-hosted runner / proxy that is not Cloudflare-blocked)."
            )
            return
        raise SystemExit(2) from err

    if len(props) < 1:
        raise SystemExit("Thapar feed returned 0 listings")

    team = []
    skipped = []
    for p in props:
        try:
            team.append(convert(p))
        except ValueError as err:
            skipped.append(str(err))

    data = json.loads(LISTINGS_PATH.read_text(encoding="utf-8"))
    josh = data.get("current") or []
    josh_mls = {str(i.get("mls") or "") for i in josh if i.get("mls")}
    team = [t for t in team if str(t.get("mls") or "") not in josh_mls]

    verify_against_source(team, props)

    data["team"] = team
    data["teamSyncedAt"] = synced_at
    LISTINGS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_active_js(josh, team, synced_at)
    subprocess.check_call(["python3", str(ROOT / "scripts" / "generate-seo-pages.py")])
    print(f"Synced {len(team)} team listings (+ {len(josh)} Josh current) at {synced_at}")
    if skipped:
        print(f"Skipped {len(skipped)}:")
        for s in skipped:
            print(" -", s)


if __name__ == "__main__":
    main()
