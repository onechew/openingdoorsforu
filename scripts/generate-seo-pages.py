#!/usr/bin/env python3
"""Generate city pages, listing detail pages, and sitemap for SEO."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "listings.json").read_text())
TODAY = date.today().isoformat()
ORIGIN = "https://openingdoorsforu.com"

CITIES = {
    "toronto": {
        "name": "Toronto",
        "areas": ["Downtown Toronto", "Midtown Toronto", "East Toronto", "West Toronto"],
        "title": "Toronto Realtor | Homes for Sale, Sold & Lease | Josh Schwartz",
        "description": "Buy, sell, or lease in Toronto with Josh Schwartz. Browse current listings, recently sold and leased homes across Downtown, Midtown, East Toronto, and West Toronto.",
        "about": "Toronto is the core of the GTA housing market — from waterfront condos and downtown suites to midtown apartments and west-end houses. Josh Schwartz helps buyers, sellers, and renters navigate neighbourhood fit, pricing, and timing with clear local guidance.",
        "schools": [
            "University of Toronto and nearby college campuses shape strong rental demand downtown.",
            "Families often weigh school catchments in midtown and the east/west ends alongside commute time.",
            "Ask Josh for catchment context before you write an offer — school boundaries change buyer pools.",
        ],
        "transit": [
            "TTC subway, streetcar, and GO connections make many Toronto neighbourhoods workable without a long drive.",
            "Downtown and midtown towers trade on walkability; west and east pockets often balance transit with parking.",
            "Commute patterns to the Financial District, hospitals, and campuses still drive absorption for leases and sales.",
        ],
        "snapshot": {
            "focus": "Condos & urban homes",
            "buyer": "First-time, downsizers, investors",
            "note": "Inventory and days-on-market shift by pocket — downtown lease velocity differs from midtown sales.",
        },
    },
    "etobicoke": {
        "name": "Etobicoke",
        "areas": ["Etobicoke"],
        "title": "Etobicoke Realtor | Homes for Sale, Sold & Lease | Josh Schwartz",
        "description": "Etobicoke realtor Josh Schwartz. Current listings, recently sold and leased homes in Mimico, Islington, lake shore condos, and family neighbourhoods across Etobicoke.",
        "about": "Etobicoke sits on Toronto’s west side with lake shore condo corridors, established family streets, and quick links to downtown and the airport. It is a primary focus for Josh Schwartz and Opening Doors For U — practical advice for buyers, sellers, and renters who want local clarity without gimmicks.",
        "schools": [
            "Families often compare schools across south Etobicoke and inland neighbourhoods when choosing between houses and condos.",
            "Proximity to parks, the waterfront trail, and community centres matters as much as classroom rankings for many buyers.",
            "Josh can help you weigh school options against budget and commute before you shortlist homes.",
        ],
        "transit": [
            "GO, TTC, and highway access (Gardiner / 427) connect Mimico and Islington-area living to the rest of the GTA.",
            "Lake shore condo living often pairs transit with bike and waterfront paths.",
            "Sellers benefit when staging and pricing reflect how buyers actually commute from Etobicoke.",
        ],
        "snapshot": {
            "focus": "Lake shore condos & family homes",
            "buyer": "End-users, relocators, lease clients",
            "note": "Mimico and Queensway pockets can move quickly on well-priced suites.",
        },
    },
    "north-york": {
        "name": "North York",
        "areas": ["North York"],
        "title": "North York Realtor | Condos & Homes | Josh Schwartz",
        "description": "North York real estate with Josh Schwartz — current listings plus recently sold and leased homes around Willowdale, Yonge corridor, and surrounding North York communities.",
        "about": "North York blends high-rise living along Yonge with quieter residential pockets. Buyers often compare condo amenities, subway access, and value against downtown Toronto pricing. Josh helps clients read the trade-offs clearly.",
        "schools": [
            "Yonge-corridor living attracts students and professionals tied to nearby colleges and tutoring hubs.",
            "Family buyers frequently check school options when choosing between condo and low-rise product.",
            "Local knowledge matters: two buildings a few blocks apart can serve very different buyer pools.",
        ],
        "transit": [
            "Line 1 subway access is a major pricing driver for North York condos.",
            "Highway 401 connectivity supports cross-GTA commuting.",
            "Lease demand often tracks transit convenience for professionals working downtown or midtown.",
        ],
        "snapshot": {
            "focus": "Yonge-corridor condos",
            "buyer": "Professionals, investors, relocators",
            "note": "Building-level comps matter more than broad North York averages.",
        },
    },
    "markham": {
        "name": "Markham",
        "areas": ["Markham"],
        "title": "Markham Realtor | Homes for Sale & Sold | Josh Schwartz",
        "description": "Markham homes with Josh Schwartz. See current opportunities and recently sold or leased properties across Markham and nearby York Region communities.",
        "about": "Markham is a key York Region market known for family homes, newer communities, and strong employment nodes. Buyers often compare Markham with Richmond Hill and Vaughan on schools, commute, and house-versus-condo trade-offs.",
        "schools": [
            "School quality and catchments are frequent decision drivers for Markham family buyers.",
            "New-build and resale pockets can feed different school boundaries — verify before you offer.",
            "Josh helps families map shortlists to the schools and routines that actually fit their day.",
        ],
        "transit": [
            "Highway 404 / 407 access and GO options shape Markham commute patterns.",
            "Many buyers balance Markham pricing against longer downtown trips.",
            "Local retail and employment hubs reduce the need for a daily downtown commute for some households.",
        ],
        "snapshot": {
            "focus": "Family homes & townhomes",
            "buyer": "Growing families, upsizers",
            "note": "Detached and townhome demand often leads condo volume in buyer conversations.",
        },
    },
    "richmond-hill": {
        "name": "Richmond Hill",
        "areas": ["Richmond Hill"],
        "title": "Richmond Hill Realtor | Sold Homes & Local Guidance | Josh Schwartz",
        "description": "Richmond Hill real estate guidance from Josh Schwartz — recently sold and leased highlights, plus help buying or selling across Richmond Hill.",
        "about": "Richmond Hill sits between Toronto and northern York Region communities, with a mix of established neighbourhoods and newer housing. Clients often weigh Richmond Hill against Markham and Aurora for lifestyle and value.",
        "schools": [
            "Family buyers commonly shortlist Richmond Hill for school options and quieter residential streets.",
            "Confirm boundaries early — they influence both pricing and days on market.",
            "Josh can connect housing product type to the school and commute profile you need.",
        ],
        "transit": [
            "Yonge Street corridor and highway links support commuting into Toronto and across York Region.",
            "GO and bus connections matter for households splitting work between downtown and 905 offices.",
            "Sellers should price to the commute story buyers are actually shopping.",
        ],
        "snapshot": {
            "focus": "Residential homes",
            "buyer": "Families and move-up buyers",
            "note": "Condition and lot utility often separate similar list prices.",
        },
    },
    "vaughan": {
        "name": "Vaughan",
        "areas": ["Vaughan"],
        "title": "Vaughan Realtor | Homes Sold & for Lease | Josh Schwartz",
        "description": "Vaughan real estate with Josh Schwartz. Browse sold and leased results and get clear guidance for buying or selling in Vaughan.",
        "about": "Vaughan continues to attract buyers seeking newer housing stock, highway access, and space relative to Toronto proper. Josh helps clients compare Vaughan pockets against neighbouring York Region cities with straightforward pricing context.",
        "schools": [
            "Growing communities mean school planning should sit beside floor-plan decisions.",
            "Buyers often ask about future development and how it may affect traffic and amenities.",
            "Josh keeps the advice practical: what matters for resale in this pocket, not generic slogans.",
        ],
        "transit": [
            "Highway 400 / 407 access is a major lifestyle factor for Vaughan households.",
            "Subway extension and bus connections improve access into Toronto for some corridors.",
            "Lease and sale demand can follow employment nodes and retail destinations in Vaughan.",
        ],
        "snapshot": {
            "focus": "Newer homes & townhomes",
            "buyer": "Families, relocators",
            "note": "Product type and builder era drive comps more than city-wide averages.",
        },
    },
    "mississauga": {
        "name": "Mississauga",
        "areas": ["Mississauga"],
        "title": "Mississauga Realtor | GTA Homes | Josh Schwartz",
        "description": "Mississauga and west-GTA guidance from Josh Schwartz — sold and leased highlights plus help buying, selling, or leasing across Mississauga.",
        "about": "Mississauga is one of the GTA’s largest housing markets, spanning condo nodes, townhomes, and detached streets. Clients often compare Mississauga with Etobicoke and Oakville on commute, schools, and value.",
        "schools": [
            "School choice varies widely by neighbourhood — treat Mississauga as many micro-markets, not one.",
            "Families should align budget, commute, and catchment before touring broadly.",
            "Josh helps narrow the map so you are not comparing unrelated pockets.",
        ],
        "transit": [
            "GO transit, MiWay, and highway corridors (QEW / 403 / 401) define many purchase decisions.",
            "Airport-adjacent living is a distinct buyer and renter pool.",
            "Pricing strategy should reflect how buyers weigh transit versus parking and driving.",
        ],
        "snapshot": {
            "focus": "West GTA homes & condos",
            "buyer": "Diverse end-users and investors",
            "note": "Neighbourhood-level comps beat city-wide averages every time.",
        },
    },
}


def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def asset_href(path: str, depth: int) -> str:
    if path.startswith("http"):
        return path
    prefix = "../" * depth
    return f"{prefix}{path.lstrip('/')}"


def page_shell(
    *,
    title: str,
    description: str,
    canonical: str,
    depth: int,
    body: str,
    json_ld: dict | None = None,
) -> str:
    css = asset_href("assets/seo-pages.css", depth)
    icon = asset_href("assets/js.svg", depth)
    home = asset_href("", depth) or "./"
    if not home.endswith("/") and home != "./":
        home += "/"
    fonts = """
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap" rel="stylesheet" />
"""
    ld = ""
    if json_ld:
        ld = f'<script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>'
    return f"""<!DOCTYPE html>
<html lang="en-CA">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <link rel="canonical" href="{esc(canonical)}" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:url" content="{esc(canonical)}" />
  <meta property="og:image" content="{ORIGIN}/assets/JS.jpg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />
  <link rel="icon" href="{icon}" type="image/svg+xml" />
  {fonts}
  <link rel="stylesheet" href="{css}" />
  {ld}
</head>
<body>
  <header class="site-header">
    <div class="container nav">
      <a class="brand" href="{home}">
        <img src="{asset_href('assets/js.svg', depth)}" alt="" />
        Josh Schwartz
      </a>
      <nav class="nav-links" aria-label="Primary">
        <a href="{home}#listings">Listings</a>
        <a href="{home}#services">Services</a>
        <a href="{home}#contact">Contact</a>
      </nav>
    </div>
  </header>
  {body}
  <footer class="site-footer">
    <div class="container">
      <p>© {date.today().year} Josh Schwartz · Sales Representative · Snobar Realty Group Inc., Brokerage</p>
      <p><a href="{home}">Opening Doors For U</a> · Etobicoke, Toronto &amp; GTA</p>
    </div>
  </footer>
</body>
</html>
"""


def cards_html(items: list[dict], depth: int, link_prefix: str) -> str:
    if not items:
        return '<p class="empty">No matching homes to show here yet — <a href="{}#contact">contact Josh</a> for a private search.</p>'.format(
            asset_href("", depth) or "./"
        )
    bits = []
    for item in items:
        status = item.get("status") or ""
        status_class = "lease" if re.search(r"lease", status, re.I) else "sold" if re.search(r"sold", status, re.I) else ""
        href = f"{link_prefix}{item['slug']}/"
        img = asset_href(item.get("image", "assets/JS.jpg"), depth)
        loc = item.get("location") or item.get("area") or ""
        bits.append(
            f"""
      <a class="card" href="{esc(href)}">
        <div class="card-media"><img src="{esc(img)}" alt="{esc(item.get('alt') or item['title'])}" loading="lazy" width="800" height="600" /></div>
        <div class="card-body">
          <span class="card-status {status_class}">{esc(status)}</span>
          <p class="card-title">{esc(item['title'])}</p>
          <p class="card-meta">{esc(loc)}</p>
        </div>
      </a>"""
        )
    return '<div class="grid">' + "".join(bits) + "</div>"


def split_past(items: list[dict]):
    sold = [i for i in items if re.search(r"sold", i.get("status", ""), re.I)]
    leased = [i for i in items if re.search(r"lease", i.get("status", ""), re.I)]
    return sold, leased


def city_items(city_key: str):
    areas = set(CITIES[city_key]["areas"])
    current = [i for i in DATA["current"] if i.get("area") in areas or any(a.replace(" Toronto", "") in (i.get("location") or "") for a in areas)]
    # Active listings use location like "Mimico · Toronto" without area field
    if city_key == "etobicoke":
        current = [
            i
            for i in DATA["current"]
            if re.search(r"mimico|etobicoke|islington|queensway", f"{i.get('location','')} {i.get('title','')}", re.I)
        ]
    elif city_key == "toronto":
        current = [
            i
            for i in DATA["current"]
            if re.search(r"toronto", i.get("location", ""), re.I)
            and not re.search(r"mimico|north york|scarborough|etobicoke", i.get("location", ""), re.I)
        ]
    past = [i for i in DATA["sold"] if i.get("area") in areas]
    if city_key == "toronto":
        past = [i for i in DATA["sold"] if i.get("area") in areas]
    return current, past


def write_city_pages():
    urls = []
    for key, meta in CITIES.items():
        current, past = city_items(key)
        sold, leased = split_past(past)
        depth = 1
        out_dir = ROOT / key
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"{ORIGIN}/{key}/"
        body = f"""
  <section class="hero-band">
    <div class="container">
      <p class="breadcrumb"><a href="{asset_href('', depth)}">Home</a> / {esc(meta['name'])}</p>
      <p class="eyebrow">Opening Doors For U</p>
      <h1>{esc(meta['name'])} Real Estate</h1>
      <p class="lead">{esc(meta['about'])}</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="{asset_href('', depth)}#contact">Work with Josh</a>
        <a class="btn btn-secondary" href="{asset_href('', depth)}#listings">View all listings</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Current Listings in {esc(meta['name'])}</h2>
      <p class="section-copy">Active homes for sale or lease that Josh is marketing in and around {esc(meta['name'])}.</p>
      {cards_html(current, depth, asset_href('listings/', depth))}
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Recently Sold in {esc(meta['name'])}</h2>
      <p class="section-copy">Closed sales Josh helped bring across the finish line. Prices are not shown, consistent with Ontario RECO / TRESA advertising rules.</p>
      {cards_html(sold, depth, asset_href('sold/', depth))}
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Recently Leased in {esc(meta['name'])}</h2>
      <p class="section-copy">Lease placements for renters and landlords across {esc(meta['name'])}.</p>
      {cards_html(leased, depth, asset_href('sold/', depth))}
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>About {esc(meta['name'])}</h2>
      <div class="prose"><p>{esc(meta['about'])}</p></div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Schools</h2>
      <div class="prose"><ul>{''.join(f'<li>{esc(x)}</li>' for x in meta['schools'])}</ul></div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Transit</h2>
      <div class="prose"><ul>{''.join(f'<li>{esc(x)}</li>' for x in meta['transit'])}</ul></div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Market Snapshot</h2>
      <div class="stat-row">
        <div class="stat"><strong>{esc(meta['snapshot']['focus'])}</strong><span>Local focus</span></div>
        <div class="stat"><strong>{esc(meta['snapshot']['buyer'])}</strong><span>Typical clients</span></div>
        <div class="stat"><strong>{len(sold)}</strong><span>Sold on site</span></div>
        <div class="stat"><strong>{len(leased)}</strong><span>Leased on site</span></div>
      </div>
      <p class="section-copy" style="margin-top:18px">{esc(meta['snapshot']['note'])} For live numbers, ask Josh for a current {esc(meta['name'])} brief.</p>
      <div class="city-links" style="margin-top:18px">
        {''.join(f'<a href="{asset_href(k + "/", depth)}">{esc(CITIES[k]["name"])}</a>' for k in CITIES if k != key)}
      </div>
    </div>
  </section>
"""
        json_ld = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": meta["title"],
            "description": meta["description"],
            "url": canonical,
            "isPartOf": {"@id": f"{ORIGIN}/#website"},
            "about": {"@type": "Place", "name": meta["name"]},
        }
        html = page_shell(
            title=meta["title"],
            description=meta["description"],
            canonical=canonical,
            depth=depth,
            body=body,
            json_ld=json_ld,
        )
        (out_dir / "index.html").write_text(html)
        urls.append((canonical, "weekly", "0.9"))
        print(f"city {key}: current={len(current)} sold={len(sold)} leased={len(leased)}")
    return urls


def listing_title(item: dict) -> str:
    status = item.get("status") or ""
    area = item.get("area") or ""
    loc = item.get("location") or area
    city = area or loc.split("·")[-1].strip()
    beds = item.get("beds")
    if re.search(r"sold", status, re.I):
        return f"Sold Home in {city} | {item['title']} | Opening Doors For U"
    if re.search(r"lease", status, re.I) and item.get("kind") == "past":
        return f"Leased Home in {city} | {item['title']} | Opening Doors For U"
    if beds:
        kind = "Condo" if re.search(r"#|condo|suite", item["title"], re.I) else "Home"
        action = "for Lease" if re.search(r"lease", status, re.I) else "for Sale"
        return f"{beds} Bedroom {kind} {action} in {city} | Opening Doors For U"
    return f"{item['title']} | {city} | Opening Doors For U"


def listing_description(item: dict) -> str:
    status = item.get("status") or ""
    area = item.get("area") or item.get("location") or "the GTA"
    if re.search(r"sold", status, re.I):
        return f"{item['title']} was sold in {area} with Josh Schwartz. See neighbourhood notes, property context, and similar homes across the GTA."
    if re.search(r"lease", status, re.I) and item.get("kind") == "past":
        return f"{item['title']} was leased in {area} with Josh Schwartz. Review the neighbourhood context and similar leased homes."
    bits = [item["title"], status, area]
    if item.get("beds"):
        bits.append(f"{item['beds']} beds")
    if item.get("price"):
        bits.append(item["price"])
    return f"{' · '.join(bits)}. Listed with Josh Schwartz, Opening Doors For U."


def neighbourhood_blurb(item: dict) -> str:
    area = item.get("area") or "this community"
    loc = item.get("location") or area
    return (
        f"{item['title']} sits in {loc}. Buyers and renters comparing options in {area} "
        f"usually weigh commute, building or lot utility, and nearby daily needs. "
        f"Josh Schwartz helps you read those trade-offs with clear local context — not hype."
    )


def why_blurb(item: dict) -> str:
    area = item.get("area") or "the area"
    return (
        f"People looking in {area} often want a practical mix of access, amenities, and long-term usability. "
        f"Whether you are buying, selling, or leasing next, Josh can map comparable homes and a realistic plan."
    )


def similar_items(item: dict, pool: list[dict], limit: int = 3) -> list[dict]:
    area = item.get("area")
    others = [x for x in pool if x.get("slug") != item.get("slug")]
    same = [x for x in others if x.get("area") == area]
    picks = (same + others)[:limit]
    return picks


def write_listing_pages():
    urls = []
    # Active
    for item in DATA["current"]:
        depth = 2
        out_dir = ROOT / "listings" / item["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"{ORIGIN}/listings/{item['slug']}/"
        title = listing_title(item)
        description = listing_description(item)
        img = asset_href(item.get("image", "assets/JS.jpg"), depth)
        features = []
        if item.get("beds"):
            features.append(f"{item['beds']} Bedrooms")
        if item.get("baths"):
            features.append(f"{item['baths']} Bathrooms")
        if item.get("size"):
            features.append(item["size"])
        if item.get("mls"):
            features.append(f"MLS# {item['mls']}")
        if item.get("price"):
            features.append(item["price"])
        feature_html = "".join(f"<li>{esc(f)}</li>" for f in features) or "<li>Details on request</li>"
        similar = similar_items(item, DATA["current"] + DATA["sold"])
        sim_html = cards_html(
            similar,
            depth,
            asset_href("listings/", depth)
            if similar and similar[0].get("kind") == "active"
            else asset_href("sold/", depth),
        )
        # Fix similar links individually
        sim_bits = []
        for s in similar:
            prefix = asset_href("listings/" if s.get("kind") == "active" else "sold/", depth)
            status = s.get("status") or ""
            status_class = "lease" if re.search(r"lease", status, re.I) else "sold" if re.search(r"sold", status, re.I) else ""
            sim_bits.append(
                f"""
      <a class="card" href="{esc(prefix + s['slug'] + '/')}">
        <div class="card-media"><img src="{esc(asset_href(s.get('image','assets/JS.jpg'), depth))}" alt="{esc(s['title'])}" loading="lazy" /></div>
        <div class="card-body">
          <span class="card-status {status_class}">{esc(status)}</span>
          <p class="card-title">{esc(s['title'])}</p>
          <p class="card-meta">{esc(s.get('location') or s.get('area') or '')}</p>
        </div>
      </a>"""
            )
        sim_html = '<div class="grid">' + "".join(sim_bits) + "</div>" if sim_bits else '<p class="empty">More homes coming soon.</p>'

        city_slug = None
        for key, meta in CITIES.items():
            if item.get("area") in meta["areas"] or (
                key == "etobicoke" and re.search(r"mimico|etobicoke", item.get("location", ""), re.I)
            ):
                city_slug = key
                break
        if not city_slug and re.search(r"toronto", item.get("location", ""), re.I):
            city_slug = "toronto"
        city_link = f'<a href="{asset_href(city_slug + "/", depth)}">{esc(CITIES[city_slug]["name"])}</a>' if city_slug else "GTA"

        cta = ""
        if item.get("url"):
            cta = f'<a class="btn btn-primary" href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">View full listing</a>'

        body = f"""
  <section class="section">
    <div class="container">
      <p class="breadcrumb"><a href="{asset_href('', depth)}">Home</a> / <a href="{asset_href('', depth)}#listings">Listings</a> / {esc(item['title'])}</p>
      <div class="listing-hero">
        <div class="listing-hero-media"><img src="{esc(img)}" alt="{esc(item.get('alt') or item['title'])}" width="1200" height="900" /></div>
        <div>
          <p class="eyebrow">{esc(item.get('status') or 'Listing')}</p>
          <h1>{esc(item['title'])}</h1>
          <p class="lead">{esc(item.get('location') or '')}</p>
          <ul class="feature-list">{feature_html}</ul>
          <div class="cta-row">
            {cta}
            <a class="btn btn-secondary" href="{asset_href('', depth)}#contact">Ask Josh about this home</a>
          </div>
        </div>
      </div>
    </div>
  </section>
  <section class="section"><div class="container"><h2>Property Features</h2><div class="prose"><p>{esc(item['title'])} is presented with clear specs so you can compare apples to apples. {('Size: ' + item['size'] + '.') if item.get('size') else ''} For showings, disclosures, and the newest status, contact Josh directly.</p><ul class="feature-list">{feature_html}</ul></div></div></section>
  <section class="section"><div class="container"><h2>Neighbourhood</h2><div class="prose"><p>{esc(neighbourhood_blurb(item))}</p><p>Explore more in {city_link}.</p></div></div></section>
  <section class="section"><div class="container"><h2>Nearby Schools</h2><div class="prose"><p>School fit depends on exact catchments and your household needs. Josh can share current local context for {esc(item.get('area') or item.get('location') or 'this pocket')} before you write an offer or sign a lease.</p></div></div></section>
  <section class="section"><div class="container"><h2>Why Buyers Love This Area</h2><div class="prose"><p>{esc(why_blurb(item))}</p></div></div></section>
  <section class="section"><div class="container"><h2>Similar Homes</h2>{sim_html}</div></section>
"""
        json_ld = {
            "@context": "https://schema.org",
            "@type": "RealEstateListing",
            "name": item["title"],
            "description": description,
            "url": canonical,
            "image": f"{ORIGIN}/{item.get('image', 'assets/JS.jpg')}",
        }
        html = page_shell(
            title=title,
            description=description,
            canonical=canonical,
            depth=depth,
            body=body,
            json_ld=json_ld,
        )
        (out_dir / "index.html").write_text(html)
        urls.append((canonical, "weekly", "0.8"))

    # Past sold/leased
    for item in DATA["sold"]:
        depth = 2
        out_dir = ROOT / "sold" / item["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"{ORIGIN}/sold/{item['slug']}/"
        title = listing_title(item)
        description = listing_description(item)
        img = asset_href(item.get("image", "assets/JS.jpg"), depth)
        status = item.get("status") or ""
        headline = (
            f"Detached Home Sold in {item.get('area')}"
            if re.search(r"sold", status, re.I) and not re.search(r"#", item["title"])
            else f"{status} in {item.get('area')}"
        )
        if re.search(r"#|condo|ave #|st #|rd #|dr #", item["title"], re.I):
            headline = f"{'Condo' if re.search(r'sold', status, re.I) else 'Suite'} {status} in {item.get('area')}"

        similar = similar_items(item, DATA["sold"])
        sim_bits = []
        for s in similar:
            sim_bits.append(
                f"""
      <a class="card" href="{esc(asset_href('sold/' + s['slug'] + '/', depth))}">
        <div class="card-media"><img src="{esc(asset_href(s.get('image','assets/JS.jpg'), depth))}" alt="{esc(s['title'])}" loading="lazy" /></div>
        <div class="card-body">
          <span class="card-status {'lease' if 'lease' in (s.get('status') or '').lower() else 'sold'}">{esc(s.get('status') or '')}</span>
          <p class="card-title">{esc(s['title'])}</p>
          <p class="card-meta">{esc(s.get('location') or s.get('area') or '')}</p>
        </div>
      </a>"""
            )
        sim_html = '<div class="grid">' + "".join(sim_bits) + "</div>" if sim_bits else '<p class="empty">More results coming soon.</p>'

        city_slug = None
        for key, meta in CITIES.items():
            if item.get("area") in meta["areas"]:
                city_slug = key
                break
        city_link = (
            f'<a href="{asset_href(city_slug + "/", depth)}">{esc(CITIES[city_slug]["name"])}</a>'
            if city_slug
            else esc(item.get("area") or "GTA")
        )

        body = f"""
  <section class="section">
    <div class="container">
      <p class="breadcrumb"><a href="{asset_href('', depth)}">Home</a> / <a href="{asset_href('', depth)}#listings">Sold &amp; Leased</a> / {esc(item['title'])}</p>
      <div class="listing-hero">
        <div class="listing-hero-media"><img src="{esc(img)}" alt="{esc(item.get('alt') or item['title'])}" width="1200" height="900" /></div>
        <div>
          <p class="eyebrow">{esc(status)}</p>
          <h1>{esc(item['title'])}</h1>
          <p class="lead">{esc(headline)} — {esc(item.get('location') or item.get('area') or '')}</p>
          <p class="section-copy">Closed with Josh Schwartz. Sale prices are not displayed here, consistent with Ontario RECO / TRESA advertising rules.</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="{asset_href('', depth)}#contact">Get a home valuation</a>
            <a class="btn btn-secondary" href="{asset_href('', depth)}#listings">Browse more results</a>
          </div>
        </div>
      </div>
    </div>
  </section>
  <section class="section"><div class="container"><h2>Property Features</h2><div class="prose"><p>{esc(item['title'])} is part of Josh’s {esc(status.lower())} track record in {esc(item.get('area') or 'the GTA')}. Use this page for neighbourhood context and comparable activity — then talk to Josh for a tailored brief on your next move.</p></div></div></section>
  <section class="section"><div class="container"><h2>Neighbourhood</h2><div class="prose"><p>{esc(neighbourhood_blurb(item))}</p><p>See more activity in {city_link}.</p></div></div></section>
  <section class="section"><div class="container"><h2>Nearby Schools</h2><div class="prose"><p>School preferences vary by household. If you are buying or leasing nearby, Josh can outline the local options that usually come up for {esc(item.get('area') or 'this neighbourhood')}.</p></div></div></section>
  <section class="section"><div class="container"><h2>Why Buyers Love This Area</h2><div class="prose"><p>{esc(why_blurb(item))}</p></div></div></section>
  <section class="section"><div class="container"><h2>Similar Homes</h2>{sim_html}</div></section>
"""
        json_ld = {
            "@context": "https://schema.org",
            "@type": "Residence",
            "name": item["title"],
            "description": description,
            "url": canonical,
            "image": f"{ORIGIN}/{item.get('image', 'assets/JS.jpg')}",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": item["title"],
                "addressLocality": item.get("area") or "Toronto",
                "addressRegion": "ON",
                "addressCountry": "CA",
            },
        }
        html = page_shell(
            title=title,
            description=description,
            canonical=canonical,
            depth=depth,
            body=body,
            json_ld=json_ld,
        )
        (out_dir / "index.html").write_text(html)
        urls.append((canonical, "monthly", "0.7"))

    return urls


def write_sitemap(extra_urls: list[tuple[str, str, str]]):
    city_urls = [(f"{ORIGIN}/{k}/", "weekly", "0.9") for k in CITIES]
    base = [
        (f"{ORIGIN}/", "weekly", "1.0"),
        *city_urls,
        *extra_urls,
    ]
    # dedupe
    seen = set()
    urls = []
    for loc, freq, pri in base:
        if loc in seen:
            continue
        seen.add(loc)
        urls.append((loc, freq, pri))
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, freq, pri in urls:
        body.append("  <url>")
        body.append(f"    <loc>{loc}</loc>")
        body.append(f"    <lastmod>{TODAY}</lastmod>")
        body.append(f"    <changefreq>{freq}</changefreq>")
        body.append(f"    <priority>{pri}</priority>")
        body.append("  </url>")
    body.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(body) + "\n")
    print(f"sitemap urls: {len(urls)}")


def main():
    city_urls = write_city_pages()
    listing_urls = write_listing_pages()
    write_sitemap(city_urls + listing_urls)


if __name__ == "__main__":
    main()
