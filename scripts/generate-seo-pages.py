#!/usr/bin/env python3
"""Generate city pages, listing detail pages, and sitemap for SEO."""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from site_footer import (  # noqa: E402
    render_site_footer,
    site_footer_script_tag,
    sync_homepage_footer,
)
DATA = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))
# Sitemap lastmod: ISO 8601 with timezone (W3C Datetime / sitemaps.org)
LASTMOD = (
    datetime.now(timezone.utc)
    .replace(hour=0, minute=0, second=0, microsecond=0)
    .isoformat()
)
ORIGIN = "https://openingdoorsforu.com"

# Thin outline SVGs (stroke) so icons stay light — no Google font dependency.
_SVG_PATHS = {
    "school": (
        '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/>'
        '<path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5"/>'
    ),
    "subway": (
        '<rect x="5" y="3" width="14" height="14" rx="2"/>'
        '<path d="M5 11h14M9 17l-1.5 3M15 17l1.5 3M9 14h.01M15 14h.01"/>'
    ),
    "bus": (
        '<path d="M4 6c0-1.5 3.6-2 8-2s8 .5 8 2v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6z"/>'
        '<path d="M4 11h16M8 18v2M16 18v2M8 14h.01M16 14h.01"/>'
    ),
    "chart": '<path d="M3 17l5-5 4 4 8-9"/>',
    "city": (
        '<path d="M3 21h18M5 21V8l7-4 7 4v13"/>'
        '<path d="M9 21v-5h6v5M9 10h.01M15 10h.01M9 14h.01M15 14h.01"/>'
    ),
    "group": (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="3.5"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "near": '<path d="M3 11l19-8-8 19-2.5-8.5z"/>',
    "analytics": (
        '<path d="M4 19V5M4 19h16"/>'
        '<path d="M8 16v-5M12 16V8M16 16v-3"/>'
    ),
}


def city_svg(name: str, tone: str, size: str = "lg") -> str:
    """Self-contained thin outline icon badge (no webfont)."""
    path = _SVG_PATHS[name]
    return (
        f'<span class="city-icon-badge city-icon-badge--{size} is-{tone}" aria-hidden="true">'
        f'<svg viewBox="0 0 24 24" width="24" height="24" fill="none" focusable="false">{path}</svg>'
        f"</span>"
    )


# Tile index on /etobicoke/. Full guides: /etobicoke/neighbourhoods/{slug}/
ETOBICOKE_NEIGHBOURHOODS = [
    {
        "slug": "mimico",
        "name": "Mimico",
        "chip": "South Etobicoke",
        "image": "assets/neighbourhoods/mimico.jpg",
    },
    {
        "slug": "long-branch",
        "name": "Long Branch",
        "chip": "South Etobicoke",
        "image": "assets/neighbourhoods/long-branch.jpg",
    },
    {
        "slug": "alderwood",
        "name": "Alderwood",
        "chip": "South Etobicoke",
        "image": "assets/neighbourhoods/alderwood.jpg",
    },
    {
        "slug": "new-toronto",
        "name": "New Toronto",
        "chip": "South Etobicoke",
        "image": "assets/neighbourhoods/new-toronto.jpg",
    },
    {
        "slug": "humber-bay-shores",
        "name": "Humber Bay Shores",
        "chip": "South Etobicoke",
        "image": "assets/neighbourhoods/humber-bay.jpg",
    },
    {
        "slug": "stonegate-queensway",
        "name": "Stonegate-Queensway",
        "chip": "Etobicoke",
        "image": "assets/neighbourhoods/stonegate-queensway.jpg",
    },
]

CITIES = {
    "toronto": {
        "name": "Toronto",
        "areas": ["Downtown Toronto", "Midtown Toronto", "East Toronto", "West Toronto"],
        "title": "Toronto Realtor | Homes for Sale, Sold & Lease | Josh Schwartz",
        "description": "Buy, sell, or lease in Toronto with Josh Schwartz. Browse current listings, recently sold and leased homes across Downtown, Midtown, East Toronto, and West Toronto.",
        "lead": "From downtown condos to midtown apartments and west-end houses, Josh helps buyers, sellers, and renters find the right Toronto fit with clear local guidance.",
        "about": "Toronto is the core of the GTA market: waterfront towers, midtown apartments, and established west- and east-end streets. Josh Schwartz helps clients weigh neighbourhood fit, pricing, and timing without the noise.",
        "schools": [
            "University of Toronto and nearby college campuses shape strong rental demand downtown.",
            "Families often weigh school catchments in midtown and the east/west ends alongside commute time.",
            "Ask Josh for catchment context before you write an offer. School boundaries change buyer pools.",
        ],
        "transit": [
            "TTC subway, streetcar, and GO connections make many Toronto neighbourhoods workable without a long drive.",
            "Downtown and midtown towers trade on walkability. West and east pockets often balance transit with parking.",
            "Commute patterns to the Financial District, hospitals, and campuses still drive absorption for leases and sales.",
        ],
        "snapshot": {
            "focus": "Condos & urban homes",
            "buyer": "First-time, downsizers, investors",
            "metric": "Downtown · Midtown · East · West",
            "metric_label": "Key pockets",
            "angle": "Buy · Sell · Lease",
            "angle_label": "How Josh helps",
            "note": "Inventory and days-on-market shift by pocket. Downtown lease velocity differs from midtown sales.",
        },
    },
    "etobicoke": {
        "name": "Etobicoke",
        "areas": ["Etobicoke"],
        "title": "Etobicoke Realtor | South Etobicoke & Humber Bay | Josh Schwartz",
        "description": "Josh Schwartz for South Etobicoke, Humber Bay Shores, Mimico, and wider Etobicoke. Current listings plus recently sold and leased homes across lake shore condos and family neighbourhoods.",
        "lead": "Etobicoke is Toronto’s west side, with primary focus on South Etobicoke, Humber Bay Shores, and Mimico lake shore living, plus family neighbourhoods inland. Josh Schwartz helps clients buy, sell, and lease with clear local guidance.",
        "about": "Etobicoke is a primary focus for Josh Schwartz and Opening Doors For U. From Mimico and the lake shore to Islington and inland family streets, he helps clients buy, sell, and lease with practical guidance. He works with Thapar Team through Snobar Realty Group Inc., Brokerage.",
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
            "metric": "Mimico · Islington · Queensway",
            "metric_label": "Key pockets",
            "angle": "Josh · backed by Thapar Team",
            "angle_label": "Local strength",
            "note": "Mimico and Queensway pockets can move quickly on well-priced suites.",
        },
    },
    "north-york": {
        "name": "North York",
        "areas": ["North York"],
        "title": "North York Realtor | Condos & Homes | Josh Schwartz",
        "description": "North York real estate with Josh Schwartz: current listings plus recently sold and leased homes around Willowdale, Yonge corridor, and surrounding North York communities.",
        "lead": "North York mixes Yonge-corridor condos with quieter residential streets. Josh helps buyers and renters weigh amenities, subway access, and value against downtown pricing.",
        "about": "North York blends high-rise living along Yonge with calmer residential pockets. Josh helps clients read the trade-offs clearly (building amenities, transit, and price) without overselling any one corridor.",
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
            "metric": "Line 1 · Willowdale · nearby pockets",
            "metric_label": "Key pockets",
            "angle": "Building-level comps",
            "angle_label": "How we price",
            "note": "Building-level comps matter more than broad North York averages.",
        },
    },
    "markham": {
        "name": "Markham",
        "areas": ["Markham"],
        "title": "Markham Realtor | Homes for Sale & Sold | Josh Schwartz",
        "description": "Markham homes with Josh Schwartz. See current opportunities and recently sold or leased properties across Markham and nearby York Region communities.",
        "lead": "Markham is known for family homes, newer communities, and strong employment nodes. Josh helps buyers compare schools, commute, and house-versus-condo options across York Region.",
        "about": "Markham is a key York Region market. Buyers often weigh it against Richmond Hill and Vaughan on schools, commute, and product type. Josh keeps those comparisons practical and local.",
        "schools": [
            "School quality and catchments are frequent decision drivers for Markham family buyers.",
            "New-build and resale pockets can feed different school boundaries. Verify before you offer.",
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
            "metric": "Detached · towns · newer communities",
            "metric_label": "Common product",
            "angle": "Schools · commute · value",
            "angle_label": "Decision drivers",
            "note": "Detached and townhome demand often leads condo volume in buyer conversations.",
        },
    },
    "richmond-hill": {
        "name": "Richmond Hill",
        "areas": ["Richmond Hill"],
        "title": "Richmond Hill Realtor | Sold Homes & Local Guidance | Josh Schwartz",
        "description": "Richmond Hill real estate guidance from Josh Schwartz: recently sold and leased highlights, plus help buying or selling across Richmond Hill.",
        "lead": "Richmond Hill sits between Toronto and northern York Region, with established streets and newer housing. Josh helps families weigh lifestyle and value against Markham and Aurora.",
        "about": "Richmond Hill mixes quieter residential neighbourhoods with newer stock. Clients often compare it with Markham and Aurora. Josh helps match product type to school and commute needs.",
        "schools": [
            "Family buyers commonly shortlist Richmond Hill for school options and quieter residential streets.",
            "Confirm boundaries early. They influence both pricing and days on market.",
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
            "metric": "Established · newer communities",
            "metric_label": "Neighbourhood mix",
            "angle": "Condition · lot · commute",
            "angle_label": "What separates offers",
            "note": "Condition and lot utility often separate similar list prices.",
        },
    },
    "vaughan": {
        "name": "Vaughan",
        "areas": ["Vaughan"],
        "title": "Vaughan Realtor | Homes Sold & for Lease | Josh Schwartz",
        "description": "Vaughan real estate with Josh Schwartz. Browse sold and leased results and get clear guidance for buying or selling in Vaughan.",
        "lead": "Vaughan draws buyers looking for newer homes, highway access, and more space than Toronto proper. Josh helps compare Vaughan pockets with clear pricing context.",
        "about": "Vaughan continues to attract families and relocators seeking newer housing stock and highway access. Josh compares Vaughan pockets against neighbouring York Region cities with straightforward, local comps.",
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
            "metric": "Highway 400 / 407 access",
            "metric_label": "Lifestyle factor",
            "angle": "Builder era · product type",
            "angle_label": "What drives comps",
            "note": "Product type and builder era drive comps more than city-wide averages.",
        },
    },
    "mississauga": {
        "name": "Mississauga",
        "areas": ["Mississauga"],
        "title": "Mississauga Realtor | GTA Homes | Josh Schwartz",
        "description": "Mississauga and west-GTA guidance from Josh Schwartz: sold and leased highlights plus help buying, selling, or leasing across Mississauga.",
        "lead": "Mississauga spans condo nodes, townhomes, and detached streets across the west GTA. Josh helps clients compare commute, schools, and value against Etobicoke and Oakville.",
        "about": "Mississauga is one of the GTA’s largest markets, and many micro-markets in one. Josh helps buyers, sellers, and renters narrow the map so neighbourhood comps stay relevant.",
        "schools": [
            "School choice varies widely by neighbourhood. Treat Mississauga as many micro-markets, not one.",
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
            "metric": "Condo · town · detached nodes",
            "metric_label": "Market mix",
            "angle": "Neighbourhood-level comps",
            "angle_label": "How we advise",
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
    css = asset_href("assets/seo-pages.css", depth) + "?v=20261025thin"
    icon_svg = asset_href("assets/js.svg", depth)
    icon_png = asset_href("assets/favicon-48.png", depth)
    icon_apple = asset_href("apple-touch-icon.png", depth)
    icon_ico = asset_href("favicon.ico", depth)
    home = asset_href("", depth) or "./"
    if not home.endswith("/") and home != "./":
        home += "/"
    brand_home = "/"
    logo_js = asset_href("assets/js-on-light.svg", depth)
    logo_snobar = asset_href("assets/snobar-dark.svg", depth)
    fonts = """
  <link rel="preload" href="{jakarta}" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="{cormorant}" as="font" type="font/woff2" crossorigin />
""".format(
        jakarta=asset_href("assets/fonts/plus-jakarta-sans-latin.woff2", depth),
        cormorant=asset_href("assets/fonts/cormorant-garamond-latin.woff2", depth),
    )
    ld = ""
    if json_ld:
        ld = f'<script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>'
    root_href = "../" * depth
    footer = render_site_footer(root_href=root_href)
    footer_js = site_footer_script_tag(root_href=root_href)
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
  <link rel="icon" href="{icon_ico}" sizes="any" />
  <link rel="icon" href="{icon_svg}" type="image/svg+xml" />
  <link rel="icon" href="{icon_png}" type="image/png" sizes="48x48" />
  <link rel="apple-touch-icon" href="{icon_apple}" sizes="180x180" />
  {fonts}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0..1,0&display=swap" />
  <link rel="stylesheet" href="{css}" />
  {ld}
</head>
<body>
  <header class="site-header">
    <div class="container nav">
      <a class="brand" href="{brand_home}" aria-label="Josh Schwartz home">
        <div class="brand-mark" aria-hidden="true">
          <img src="{logo_js}" alt="Josh Schwartz Opening Doors For U logo" />
        </div>
        <div class="brand-lockup">
          <span class="brand-name">Josh Schwartz</span>
          <img
            class="brand-snobar"
            src="{logo_snobar}"
            alt="Snobar Realty Group Inc., Brokerage"
          />
        </div>
      </a>
      <nav class="nav-links" aria-label="Primary navigation">
        <div class="nav-drop" data-nav-drop>
          <button class="nav-drop-toggle" type="button" aria-expanded="false" aria-haspopup="true" aria-controls="navListingsMenu">
            Listings
            <span class="nav-drop-caret" aria-hidden="true"></span>
          </button>
          <div class="nav-drop-menu" id="navListingsMenu" role="menu">
            <a href="{home}?tab=active#listings" role="menuitem">Active</a>
            <a href="{home}?tab=sold#listings" role="menuitem">Sold &amp; Leased</a>
          </div>
        </div>
        <div class="nav-drop" data-nav-drop>
          <button class="nav-drop-toggle" type="button" aria-expanded="false" aria-haspopup="true" aria-controls="navGuidesMenu">
            Guides
            <span class="nav-drop-caret" aria-hidden="true"></span>
          </button>
          <div class="nav-drop-menu" id="navGuidesMenu" role="menu">
            <a href="{home}#areas" role="menuitem">Areas</a>
            <a href="{home}etobicoke/neighbourhoods/" role="menuitem">Neighbourhoods</a>
            <a href="{home}#condo-guide" role="menuitem">Condo</a>
          </div>
        </div>
        <div class="nav-drop" data-nav-drop>
          <button class="nav-drop-toggle" type="button" aria-expanded="false" aria-haspopup="true" aria-controls="navServicesMenu">
            Services
            <span class="nav-drop-caret" aria-hidden="true"></span>
          </button>
          <div class="nav-drop-menu" id="navServicesMenu" role="menu">
            <a href="{home}#service-buy" role="menuitem">Buy</a>
            <a href="{home}#service-sell" role="menuitem">Sell</a>
            <a href="{home}#service-lease" role="menuitem">Lease</a>
          </div>
        </div>
        <div class="nav-drop" data-nav-drop>
          <button class="nav-drop-toggle" type="button" aria-expanded="false" aria-haspopup="true" aria-controls="navAboutMenu">
            About
            <span class="nav-drop-caret" aria-hidden="true"></span>
          </button>
          <div class="nav-drop-menu" id="navAboutMenu" role="menu">
            <a href="{home}about/" role="menuitem">About</a>
            <a href="{home}#reviews" role="menuitem">Reviews</a>
            <a href="{home}#reels" role="menuitem">Latest</a>
            <a href="{home}#faq" role="menuitem">FAQ</a>
          </div>
        </div>
      </nav>
      <div class="header-utils">
        <div class="header-contact">
          <a class="call-phone" href="tel:+16473608179" aria-label="Call Josh">
            <span class="flag" aria-hidden="true">🇨🇦</span>
            <span class="phone-text">647-360-8179</span>
          </a>
          <button
            class="copy-email email-text"
            type="button"
            data-email="josh@thaparteam.ca"
            data-tip="Copy Josh's email"
            aria-label="Copy Josh's email"
          >
            <span class="copy-email-text">josh@thaparteam.ca</span>
          </button>
        </div>
        <div class="header-social" aria-label="Social links">
          <a class="fill-icon icon-threads" href="https://www.threads.com/@openingdoorsforu" target="_blank" rel="noopener noreferrer" aria-label="Threads">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.263 11.097c-.03-3.486-1.92-5.586-5.111-5.586-2.13 0-3.922.963-4.863 2.499l2.062 1.438c.535-.843 1.272-1.543 2.628-1.543 1.528 0 2.318.85 2.544 2.431a15 15 0 0 0-2.236-.173c-4.125 0-6.068 1.867-6.068 4.336s1.943 3.99 4.804 3.99c3.139 0 5.013-2.115 5.781-4.735.798.361 1.348 1.204 1.348 2.47 0 3.387-3.907 5.232-7.22 5.232-4.885 0-8.077-3.207-8.077-8.424 0-6.392 4.223-10.487 9.9-10.487 3.808 0 5.69 1.671 6.97 3.914l2.108-1.475C21.44 2.078 18.331 0 13.663 0 6.227 0 1.168 5.277 1.168 12.934c0 7 4.953 11.066 10.856 11.066 4.878 0 9.809-2.846 9.809-7.716 0-2.545-1.46-4.231-3.569-5.187m-6.33 4.855c-1.077 0-2.026-.512-2.026-1.453 0-1.483 1.822-1.934 3.606-1.934.678 0 1.34.045 1.927.173-.422 1.927-1.671 3.215-3.508 3.214Z"/></svg>
          </a>
          <a class="fill-icon icon-tiktok" href="https://www.tiktok.com/@openingdoorsforu" target="_blank" rel="noopener noreferrer" aria-label="TikTok">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 0 0-.79-.05A6.34 6.34 0 0 0 3.15 15.3a6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.34-6.34V8.69a8.19 8.19 0 0 0 4.76 1.52V6.75a4.85 4.85 0 0 1-.999-.06z"/></svg>
          </a>
          <a class="fill-icon icon-fb" href="https://www.facebook.com/OpeningdoorsforU/" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 13.5h2.5l1-4H14v-2c0-1.03 0-2 2-2h1.5V2.14c-.326-.043-1.557-.14-2.857-.14C11.928 2 10 3.657 10 6.7v2.8H7v4h3V22h4z"/></svg>
          </a>
          <a class="icon-ig" href="https://www.instagram.com/openingdoorsforu/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="2.4" y="2.4" width="19.2" height="19.2" rx="5.4" stroke="currentColor" stroke-width="2.35"/><circle cx="12" cy="12" r="4.15" stroke="currentColor" stroke-width="2.35"/><circle cx="17.55" cy="6.45" r="1.35" fill="currentColor" stroke="none"/></svg>
          </a>
        </div>
      </div>
    </div>
  </header>
  {body}
{footer}
  <button class="back-to-top" id="backToTop" type="button" aria-label="Back to top" hidden>
    <span class="material-symbols-outlined" aria-hidden="true">arrow_upward</span>
  </button>
  <script>
    (function initBackToTop() {{
      const btn = document.getElementById("backToTop");
      if (!btn) return;
      const threshold = window.matchMedia("(max-width: 720px)").matches ? 280 : 480;
      const update = () => {{
        const show = window.scrollY > threshold;
        btn.classList.toggle("is-visible", show);
        btn.hidden = !show;
        if (!show) btn.classList.remove("is-settled");
      }};
      window.addEventListener("scroll", update, {{ passive: true }});
      update();
      btn.addEventListener("animationend", (event) => {{
        if (event.animationName === "back-to-top-enter") {{
          btn.classList.add("is-settled");
        }}
      }});
      btn.addEventListener("click", () => {{
        const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({{ top: 0, behavior: reduce ? "auto" : "smooth" }});
      }});
    }})();

    async function copyText(text) {{
      if (navigator.clipboard && window.isSecureContext) {{
        await navigator.clipboard.writeText(text);
        return;
      }}
      const input = document.createElement("textarea");
      input.value = text;
      input.setAttribute("readonly", "");
      input.style.position = "absolute";
      input.style.left = "-9999px";
      document.body.appendChild(input);
      input.select();
      document.execCommand("copy");
      document.body.removeChild(input);
    }}

    document.querySelectorAll(".copy-email").forEach(button => {{
      const defaultTip = button.getAttribute("data-tip") || "Copy Josh's email";
      const label = button.querySelector(".copy-email-text");
      const defaultLabel = label ? label.textContent : "";
      const swapLabel = button.classList.contains("btn") && label;
      let copiedTimer;
      button.addEventListener("click", async () => {{
        const email = button.dataset.email;
        if (!email) return;
        try {{
          await copyText(email);
          if (swapLabel) {{
            label.textContent = "Copied!";
            button.classList.add("is-copied");
          }} else {{
            button.setAttribute("data-tip", "Copied!");
            button.classList.add("is-copied");
          }}
          window.clearTimeout(copiedTimer);
          copiedTimer = window.setTimeout(() => {{
            if (swapLabel) label.textContent = defaultLabel;
            else button.setAttribute("data-tip", defaultTip);
            button.classList.remove("is-copied");
          }}, 2000);
        }} catch (error) {{
          window.prompt("Copy email address:", email);
        }}
      }});
    }});

    (function initCopyMls() {{
      const defaultTip = "Copy MLS#";
      let copiedTimer;
      let activeButton = null;

      function clearCopiedState(button) {{
        if (!button) return;
        button.setAttribute("data-tip", defaultTip);
        button.classList.remove("is-copied");
      }}

      document.addEventListener("mousedown", event => {{
        const button = event.target.closest(".listing-mls");
        if (!button) return;
        event.preventDefault();
      }});

      document.addEventListener("click", async event => {{
        const button = event.target.closest(".listing-mls");
        if (!button) return;
        event.preventDefault();
        const mls = button.dataset.mls;
        if (!mls) return;
        window.clearTimeout(copiedTimer);
        if (activeButton && activeButton !== button) clearCopiedState(activeButton);
        try {{
          await copyText(mls);
          activeButton = button;
          button.setAttribute("data-tip", "Copied!");
          button.classList.add("is-copied");
          button.blur();
          copiedTimer = window.setTimeout(() => {{
            clearCopiedState(button);
            if (activeButton === button) activeButton = null;
          }}, 1600);
        }} catch (error) {{
          clearCopiedState(button);
          activeButton = null;
          window.prompt("Copy MLS#:", mls);
        }}
      }});
    }})();
  </script>
{footer_js}
</body>
</html>
"""


def cards_html(items: list[dict], depth: int, link_prefix: str) -> str:
    if not items:
        home = asset_href("", depth) or "./"
        thapar = "https://www.thaparteam.ca/property-search/results/?searchid=3952868"
        return (
            '<div class="empty-cta">'
            "<p>No closed results in this section right now. Josh can still help you buy, sell, or lease here.</p>"
            '<div class="cta-row empty-cta-actions">'
            f'<a class="btn btn-secondary" href="{home}#contact">Text Josh</a>'
            f'<a class="btn btn-secondary" href="{thapar}" target="_blank" rel="noopener noreferrer">Browse live inventory</a>'
            "</div></div>"
        )
    bits = []
    for item in items:
        status = item.get("status") or ""
        status_class = (
            "lease"
            if re.search(r"lease", status, re.I)
            else "sold"
            if re.search(r"sold", status, re.I)
            else "sale"
            if re.search(r"sale", status, re.I)
            else ""
        )
        external = item.get("url") if str(item.get("url") or "").startswith("http") else ""
        href = external or f"{link_prefix}{item['slug']}/"
        target = ' target="_blank" rel="noopener noreferrer"' if external else ""
        img = asset_href(item.get("image", "assets/listing-placeholder.svg"), depth)
        if str(item.get("image") or "").startswith("http"):
            img = item["image"]
        fallback = asset_href("assets/listing-placeholder.svg", depth)
        loc = item.get("location") or item.get("area") or ""
        attr = ""
        if item.get("kind") == "team" or item.get("source") == "thapar":
            note = item.get("attribution") or "Listed with Snobar Realty Group Inc. · Thapar Team"
            attr = f'<p class="card-meta card-attr">{esc(note)}</p>'
        bits.append(
            f"""
      <a class="card" href="{esc(href)}"{target}>
        <div class="card-media"><img src="{esc(img)}" alt="{esc(item.get('alt') or item['title'])}" loading="lazy" width="800" height="600" onerror="this.onerror=null;this.src='{esc(fallback)}';" /></div>
        <div class="card-body">
          <span class="card-status {status_class}">{esc(status)}</span>
          <p class="card-title">{esc(item['title'])}</p>
          <p class="card-meta">{esc(loc)}</p>
          {attr}
        </div>
      </a>"""
        )
    return '<div class="grid">' + "".join(bits) + "</div>"


def all_current() -> list[dict]:
    return list(DATA.get("current") or []) + list(DATA.get("team") or [])


def split_past(items: list[dict]):
    sold = [i for i in items if re.search(r"sold", i.get("status", ""), re.I)]
    leased = [i for i in items if re.search(r"lease", i.get("status", ""), re.I)]
    return sold, leased


def city_items(city_key: str):
    areas = set(CITIES[city_key]["areas"])
    current_all = all_current()
    current = [
        i
        for i in current_all
        if i.get("area") in areas
        or any(a.replace(" Toronto", "") in (i.get("location") or "") for a in areas)
    ]
    if city_key == "etobicoke":
        current = [
            i
            for i in current_all
            if i.get("area") == "Etobicoke"
            or re.search(
                r"mimico|etobicoke|islington|queensway|long branch|alderwood|humber|rexdale|kingsview|willowridge|clairville|kipling|thistletown",
                f"{i.get('location','')} {i.get('title','')} {i.get('area','')}",
                re.I,
            )
        ]
    elif city_key == "toronto":
        current = [
            i
            for i in current_all
            if i.get("area") in areas
            or (
                re.search(r"toronto", f"{i.get('location','')} {i.get('area','')}", re.I)
                and not re.search(
                    r"mimico|north york|scarborough|etobicoke|mississauga|vaughan|markham",
                    f"{i.get('location','')} {i.get('area','')}",
                    re.I,
                )
            )
        ]
    elif city_key == "mississauga":
        current = [i for i in current_all if i.get("area") == "Mississauga" or re.search(r"mississauga", i.get("location", ""), re.I)]
    elif city_key == "vaughan":
        current = [i for i in current_all if i.get("area") == "Vaughan" or re.search(r"vaughan|concord", i.get("location", ""), re.I)]
    elif city_key == "north-york":
        current = [i for i in current_all if i.get("area") == "North York" or re.search(r"north york|willowdale|yorkdale", i.get("location", ""), re.I)]
    past = [i for i in DATA["sold"] if i.get("area") in areas]
    return current, past


def etobicoke_neighbourhoods_html(depth: int) -> str:
    """McDadi-style tile index on the Etobicoke city page. Full guides live under /etobicoke/neighbourhoods/."""
    tiles = []
    for n in ETOBICOKE_NEIGHBOURHOODS:
        img = asset_href(n["image"], depth)
        href = asset_href(f"etobicoke/neighbourhoods/{n['slug']}/", depth)
        tiles.append(
            f"""
      <a class="hood-tile" href="{esc(href)}" aria-label="{esc(n['name'])} neighbourhood guide">
        <img src="{esc(img)}" alt="" loading="lazy" width="1600" height="1000" />
        <span class="hood-tile-label">
          <span class="hood-tile-name">{esc(n['name'])}</span>
          <span class="hood-tile-meta">{esc(n['chip'])}</span>
        </span>
      </a>"""
        )
    return f"""
  <section class="section" id="neighbourhoods">
    <div class="container">
      <h2>Neighbourhoods</h2>
      <p class="section-copy">South Etobicoke communities Josh serves. Open a guide for lifestyle, housing mix, transit context, and who it tends to fit.</p>
      <div class="hood-grid">{''.join(tiles)}
      </div>
    </div>
  </section>
"""


def write_city_pages():
    urls = []
    for key, meta in CITIES.items():
        current, past = city_items(key)
        sold, leased = split_past(past)
        depth = 1
        out_dir = ROOT / key
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"{ORIGIN}/{key}/"
        if key == "etobicoke":
            condo_cta = (
                f'<a class="btn btn-primary" href="{asset_href("", depth)}#service-buy">Buy with Josh</a>\n'
                f'        <a class="btn btn-secondary" href="{asset_href("", depth)}#service-sell">Sell with Josh</a>\n'
                '        <a class="btn btn-secondary" href="south-etobicoke-condo-guide/">Condo guide</a>'
            )
            hood_section = etobicoke_neighbourhoods_html(depth)
        else:
            condo_cta = (
                f'<a class="btn btn-primary" href="{asset_href("", depth)}#listings">View all listings</a>'
            )
            hood_section = ""
        other_city_links = "".join(
            f'<a href="{asset_href(k + "/", depth)}">{esc(CITIES[k]["name"])}</a>'
            for k in CITIES
            if k != key
        )
        body = f"""
  <section class="hero-band">
    <div class="container">
      <p class="breadcrumb"><a href="{asset_href('', depth)}">Home</a> / {esc(meta['name'])}</p>
      <p class="eyebrow">Opening Doors For U</p>
      <h1>{esc(meta['name'])} Real Estate</h1>
      <p class="lead">{esc(meta.get('lead', meta['about']))}</p>
      <div class="cta-row">
        {condo_cta}
      </div>
    </div>
  </section>
{hood_section}
  <section class="section">
    <div class="container">
      <h2>Current Listings in {esc(meta['name'])}</h2>
      <p class="section-copy">Live inventory Josh Schwartz can help you buy or lease in and around {esc(meta['name'])}. Some homes are listed with Snobar Realty Group / Thapar Team (Josh’s credential network). Not all are personally listed by Josh.</p>
      {cards_html(current, depth, asset_href('listings/', depth))}
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Recently Sold in {esc(meta['name'])}</h2>
      <p class="section-copy">Closed sales Josh helped bring across the finish line.</p>
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
      <div class="hood-panel-head">
        {city_svg("school", "school")}
        <h2>Schools</h2>
      </div>
      <ul class="city-note-list">
        {''.join(f'<li>{city_svg("school", "school", "sm")}<span>{esc(x)}</span></li>' for x in meta['schools'])}
      </ul>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="hood-panel-head">
        {city_svg("subway", "transit")}
        <h2>Transit</h2>
      </div>
      <ul class="city-note-list">
        {''.join(f'<li>{city_svg("bus", "transit", "sm")}<span>{esc(x)}</span></li>' for x in meta['transit'])}
      </ul>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="hood-panel-head">
        {city_svg("chart", "market")}
        <h2>Market Snapshot</h2>
      </div>
      <div class="stat-row stat-row--open">
        <div class="stat stat--open">{city_svg("city", "housing")}<div><strong>{esc(meta['snapshot']['focus'])}</strong><span>Local focus</span></div></div>
        <div class="stat stat--open">{city_svg("group", "clients")}<div><strong>{esc(meta['snapshot']['buyer'])}</strong><span>Typical clients</span></div></div>
        <div class="stat stat--open">{city_svg("near", "transit")}<div><strong>{esc(meta['snapshot']['metric'])}</strong><span>{esc(meta['snapshot']['metric_label'])}</span></div></div>
        <div class="stat stat--open">{city_svg("analytics", "market")}<div><strong>{esc(meta['snapshot']['angle'])}</strong><span>{esc(meta['snapshot']['angle_label'])}</span></div></div>
      </div>
      <div class="city-links" style="margin-top:18px">
        {other_city_links}
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
        crumbs = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": f"{ORIGIN}/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": meta["name"],
                    "item": canonical,
                },
            ],
        }
        html = html.replace(
            "</head>",
            f'<script type="application/ld+json">{json.dumps(crumbs, ensure_ascii=False)}</script>\n</head>',
            1,
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


def count_label(value, singular: str, plural: str | None = None) -> str:
    plural = plural or f"{singular}s"
    raw = str(value).strip()
    try:
        n = float(raw.replace("+", ""))
        label = singular if n == 1 else plural
    except ValueError:
        label = plural
    return f"{raw} {label}"


ICON_BED = "bed"
ICON_BATH = "shower"
ICON_PARKING = "directions_car"
ICON_SIZE = "square_foot"

PROPERTY_TYPE_ICONS = {
    "Condo Apt": "apartment",
    "Apartment": "apartment",
    "Triplex": "apartment",
    "Duplex": "apartment",
    "Townhouse": "home",
    "Home": "home",
}


def material_icon(name: str, css_class: str = "fact-icon") -> str:
    """Google Material Symbols Outlined — match condo guide weight/fill."""
    return (
        f'<span class="material-symbols-outlined {css_class}" aria-hidden="true">'
        f"{name}</span>"
    )


def property_type_icon(label: str) -> str:
    return material_icon(PROPERTY_TYPE_ICONS.get(label, "home"))


def infer_property_type(item: dict) -> str:
    """Prefer an explicit type. Never treat a lone low unit number (#3) as condo —
    freehold multiplexes use those too. Verify ambiguous addresses before labeling."""
    if item.get("type"):
        return str(item["type"])
    blob = f"{item.get('title', '')} {item.get('alt', '')}"
    title = item.get("title", "")
    if re.search(r"triplex", blob, re.I):
        return "Triplex"
    if re.search(r"duplex", blob, re.I):
        return "Duplex"
    if re.search(r"townhouse|townhome|freehold town", blob, re.I):
        return "Townhouse"
    if re.search(r"\b(bsmt|basement|lower|upper)\b", blob, re.I):
        return "Apartment"
    # Explicit condo wording, or high-rise style suite numbers (#2203 / 1209-…)
    if re.search(r"\bcondo\b", blob, re.I):
        return "Condo Apt"
    if re.search(r"\b(apartment|apt)\b", blob, re.I):
        return "Condo Apt"
    if re.search(r"#\s*\d{3,}\b", title) or re.search(r"\b\d{3,}\s*-\s*\d+", title):
        return "Condo Apt"
    return "Home"


# City → broader region label (factual geography only; no invented stats).
CITY_REGION = {
    "whitby": "Durham Region",
    "oshawa": "Durham Region",
    "ajax": "Durham Region",
    "pickering": "Durham Region",
    "barrie": "Simcoe County",
    "newmarket": "York Region",
    "richmond hill": "York Region",
    "markham": "York Region",
    "vaughan": "York Region",
    "mississauga": "Peel Region",
    "brampton": "Peel Region",
    "toronto": "Toronto",
    "etobicoke": "Toronto",
    "north york": "Toronto",
    "scarborough": "Toronto",
}


def format_past_location(item: dict) -> str:
    """Human-readable place line: pocket · city · region, Ontario when useful."""
    loc = (item.get("location") or "").strip()
    area = (item.get("area") or "").strip()
    if loc and "·" in loc:
        parts = [p.strip() for p in loc.split("·") if p.strip()]
    elif loc:
        parts = [loc]
    elif area:
        parts = [area]
    else:
        parts = []

    city_key = (parts[-1] if parts else area or "").casefold()
    region = CITY_REGION.get(city_key)
    if region and region.casefold() not in {p.casefold() for p in parts}:
        # e.g. Whitby → Whitby · Durham Region
        if not parts:
            parts = [region]
        elif parts[-1].casefold() != region.casefold():
            parts.append(region)

    base = " · ".join(parts) if parts else "Ontario"
    if re.search(r"\bON\b|\bOntario\b", base, re.I):
        return base
    return f"{base}, Ontario"


def format_closed_date(item: dict) -> str:
    raw = str(item.get("date") or "").strip()
    if not raw:
        return ""
    try:
        from datetime import datetime

        dt = datetime.strptime(raw[:10], "%Y-%m-%d")
        return dt.strftime("%B %Y")
    except ValueError:
        return raw


def past_listing_meta_html(item: dict) -> str:
    """Closed date + property type for sold/leased detail pages."""
    bits = []
    closed = format_closed_date(item)
    if closed:
        bits.append(
            f'<div class="fact">{material_icon("event")}<span>Closed {esc(closed)}</span></div>'
        )
    prop_type = infer_property_type(item)
    bits.append(
        f'<div class="fact">{property_type_icon(prop_type)}'
        f'<span>{esc(prop_type)}</span></div>'
    )
    if not bits:
        return ""
    return f'<div class="listing-facts listing-facts--past"><div class="listing-facts-main">{"".join(bits)}</div></div>'


def listing_facts_html(item: dict) -> str:
    facts = []
    if item.get("beds"):
        facts.append(
            f'<div class="fact">{material_icon(ICON_BED)}'
            f'<span>{esc(count_label(item["beds"], "bed"))}</span></div>'
        )
    if item.get("baths"):
        facts.append(
            f'<div class="fact">{material_icon(ICON_BATH)}'
            f'<span>{esc(count_label(item["baths"], "bath"))}</span></div>'
        )
    if item.get("parking") is not None and str(item.get("parking")).strip() != "":
        facts.append(
            f'<div class="fact">{material_icon(ICON_PARKING)}'
            f'<span>{esc(count_label(item["parking"], "parking", "parking"))}</span></div>'
        )
    if item.get("size"):
        size = re.sub(r"\s*SQ\.?\s*FT\.?", " sqft", str(item["size"]), flags=re.I)
        size = size.replace("-", "–")
        facts.append(
            f'<div class="fact">{material_icon(ICON_SIZE)}<span>{esc(size)}</span></div>'
        )
    # Property type on active pages; past sold/leased pages use past_listing_meta_html instead.
    if item.get("kind") != "past":
        prop_type = infer_property_type(item)
        facts.append(
            f'<div class="fact">{property_type_icon(prop_type)}'
            f'<span>{esc(prop_type)}</span></div>'
        )

    price = item.get("price") or ""
    mls = item.get("mls") or ""
    price_html = ""
    if price and not re.search(r"^(sold|leased)$", price, re.I):
        # Split "$2,600/mo" into value + unit when possible
        m = re.match(r"^(\$[\d,]+)(/mo|/month)?(.*)$", price.strip(), re.I)
        if m:
            unit = m.group(2) or ""
            rest = (m.group(3) or "").strip()
            unit_html = f'<span class="listing-price-unit">{esc(unit)}</span>' if unit else ""
            extra = f' <span class="listing-price-extra">{esc(rest)}</span>' if rest else ""
            price_html = f'<p class="listing-price">{esc(m.group(1))}{unit_html}{extra}</p>'
        else:
            price_html = f'<p class="listing-price">{esc(price)}</p>'
    mls_html = (
        f'<button type="button" class="listing-mls" data-mls="{esc(mls)}" data-tip="Copy MLS#" aria-label="Copy MLS# {esc(mls)}">MLS# {esc(mls)}</button>'
        if mls
        else ""
    )

    if not facts and not price_html and not mls_html:
        return ""

    main = f'<div class="listing-facts-main">{"".join(facts)}</div>' if facts else ""
    side = ""
    if price_html or mls_html:
        side = f'<div class="listing-facts-side">{price_html}{mls_html}</div>'

    return f'<div class="listing-facts">{side}{main}</div>'


def resolve_city_slug(item: dict) -> str | None:
    for key, meta in CITIES.items():
        if item.get("area") in meta["areas"] or (
            key == "etobicoke" and re.search(r"mimico|etobicoke", item.get("location", ""), re.I)
        ):
            return key
    if re.search(r"toronto", item.get("location", "") or "", re.I):
        return "toronto"
    return None


def neighbourhood_section_html(item: dict, depth: int) -> str:
    """Real area context + city CTA, not a restatement of the address."""
    city_slug = resolve_city_slug(item)
    pocket = (item.get("location") or "").split("·")[0].strip() or item.get("area") or "This area"
    if not city_slug or city_slug not in CITIES:
        return ""
    meta = CITIES[city_slug]
    city_name = meta["name"]
    # Prefer a local transit note when available; else the city about line.
    notes = meta.get("transit") or []
    body = notes[0] if notes else meta.get("about") or meta.get("lead") or ""
    href = asset_href(f"{city_slug}/", depth)
    return f"""
  <section class="section">
    <div class="container">
      <h2>{esc(pocket)}</h2>
      <div class="prose">
        <p>{esc(body)}</p>
        <p><a href="{esc(href)}">Explore homes in {esc(city_name)}</a></p>
      </div>
    </div>
  </section>"""


def similar_items(item: dict, pool: list[dict], limit: int = 3) -> list[dict]:
    current_slug = item.get("slug")
    seen: set[str] = set()
    unique: list[dict] = []
    for x in pool:
        slug = x.get("slug")
        if not slug or slug == current_slug or slug in seen:
            continue
        seen.add(slug)
        unique.append(x)
    area = item.get("area")
    same = [x for x in unique if x.get("area") == area]
    rest = [x for x in unique if x.get("area") != area]
    return (same + rest)[:limit]


def write_listing_pages():
    urls = []
    # Active
    # Josh-listed detail pages only (team listings link out to Thapar)
    for item in DATA["current"]:
        depth = 2
        out_dir = ROOT / "listings" / item["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"{ORIGIN}/listings/{item['slug']}/"
        title = listing_title(item)
        description = listing_description(item)
        img = asset_href(item.get("image", "assets/listing-placeholder.svg"), depth)
        facts_html = listing_facts_html(item)
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
        <div class="card-media"><img src="{esc(asset_href(s.get('image','assets/listing-placeholder.svg'), depth))}" alt="{esc(s['title'])}" loading="lazy" /></div>
        <div class="card-body">
          <span class="card-status {status_class}">{esc(status)}</span>
          <p class="card-title">{esc(s['title'])}</p>
          <p class="card-meta">{esc(s.get('location') or s.get('area') or '')}</p>
        </div>
      </a>"""
            )
        sim_html = '<div class="grid">' + "".join(sim_bits) + "</div>" if sim_bits else '<p class="empty">More homes coming soon.</p>'

        cta = ""
        if item.get("url"):
            cta = f'<a class="btn btn-primary" href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">View full listing</a>'

        sms_body = quote(f"Hi Josh, I am interested in {item['title']}.")
        sms_href = f"sms:+16473608179?body={sms_body}"
        area_section = neighbourhood_section_html(item, depth)

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
          {facts_html}
          <div class="cta-row">
            {cta}
            <a class="btn btn-secondary" href="{esc(sms_href)}">Text Josh</a>
          </div>
        </div>
      </div>
    </div>
  </section>
  {area_section}
  <section class="section"><div class="container"><h2>Similar Homes</h2>{sim_html}</div></section>
"""
        json_ld = {
            "@context": "https://schema.org",
            "@type": "RealEstateListing",
            "name": item["title"],
            "description": description,
            "url": canonical,
            "image": f"{ORIGIN}/{item.get('image', 'assets/listing-placeholder.svg')}",
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
        img = asset_href(item.get("image", "assets/listing-placeholder.svg"), depth)
        facts_html = listing_facts_html(item)
        status = item.get("status") or ""
        location_line = format_past_location(item)

        similar = similar_items(item, DATA["sold"])
        sim_bits = []
        for s in similar:
            sim_bits.append(
                f"""
      <a class="card" href="{esc(asset_href('sold/' + s['slug'] + '/', depth))}">
        <div class="card-media"><img src="{esc(asset_href(s.get('image','assets/listing-placeholder.svg'), depth))}" alt="{esc(s['title'])}" loading="lazy" /></div>
        <div class="card-body">
          <span class="card-status {'lease' if 'lease' in (s.get('status') or '').lower() else 'sold'}">{esc(s.get('status') or '')}</span>
          <p class="card-title">{esc(s['title'])}</p>
          <p class="card-meta">{esc(format_past_location(s))}</p>
        </div>
      </a>"""
            )
        sim_html = '<div class="grid">' + "".join(sim_bits) + "</div>" if sim_bits else '<p class="empty">More results coming soon.</p>'
        area_section = neighbourhood_section_html(item, depth)
        past_facts = past_listing_meta_html(item)
        eyebrow = f'<p class="eyebrow">{esc(status)}</p>' if status else ""

        body = f"""
  <section class="section">
    <div class="container">
      <p class="breadcrumb"><a href="{asset_href('', depth)}">Home</a> / <a href="{asset_href('', depth)}?tab=sold#listings">Sold &amp; Leased</a> / {esc(item['title'])}</p>
      <div class="listing-hero">
        <div class="listing-hero-media"><img src="{esc(img)}" alt="{esc(item.get('alt') or item['title'])}" width="1200" height="900" /></div>
        <div>
          {eyebrow}
          <h1>{esc(item['title'])}</h1>
          <p class="listing-place-label">Location</p>
          <p class="lead listing-location">{esc(location_line)}</p>
          {past_facts}
          {facts_html}
          <div class="cta-row">
            <a class="btn btn-primary" href="{asset_href('', depth)}#contact">Get a home valuation</a>
            <a class="btn btn-secondary" href="{asset_href('', depth)}?tab=sold#listings">Browse more results</a>
          </div>
        </div>
      </div>
    </div>
  </section>
  {area_section}
  <section class="section"><div class="container"><h2>Similar Homes</h2>{sim_html}</div></section>
"""
        locality = (item.get("area") or item.get("location") or "Ontario").split("·")[-1].strip()
        json_ld = {
            "@context": "https://schema.org",
            "@type": "Residence",
            "name": item["title"],
            "description": description,
            "url": canonical,
            "image": f"{ORIGIN}/{item.get('image', 'assets/listing-placeholder.svg')}",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": item["title"],
                "addressLocality": locality,
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
    """Write a standards-compliant XML sitemap (UTF-8, ISO 8601 lastmod).

    Served from GitHub Pages as application/xml via the .xml extension.
    """
    city_urls = [(f"{ORIGIN}/{k}/", "weekly", "0.9") for k in CITIES]
    base = [
        (f"{ORIGIN}/", "weekly", "1.0"),
        (f"{ORIGIN}/about/", "monthly", "0.85"),
        (f"{ORIGIN}/privacy/", "yearly", "0.3"),
        *city_urls,
        *extra_urls,
    ]
    # dedupe (preserve order; do not alter URL strings)
    seen = set()
    urls = []
    for loc, freq, pri in base:
        if loc in seen:
            continue
        seen.add(loc)
        urls.append((loc, freq, pri))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, freq, pri in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(loc)}</loc>")
        lines.append(f"    <lastmod>{LASTMOD}</lastmod>")
        lines.append(f"    <changefreq>{xml_escape(freq)}</changefreq>")
        lines.append(f"    <priority>{xml_escape(pri)}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    sitemap_path = ROOT / "sitemap.xml"
    sitemap_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"sitemap urls: {len(urls)}")


def write_neighbourhood_guide_pages() -> list[tuple[str, str, str]]:
    """Hub + per-neighbourhood guides under /etobicoke/neighbourhoods/."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "neighbourhood_pages",
        Path(__file__).resolve().parent / "generate-neighbourhood-pages.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.write_neighbourhood_pages()


def condo_guide_urls() -> list[tuple[str, str, str]]:
    """Indexable condo hub + building URLs (generated by generate-condo-guide.py)."""
    urls: list[tuple[str, str, str]] = [
        (f"{ORIGIN}/etobicoke/south-etobicoke-condo-guide/", "monthly", "0.85"),
    ]
    condo_root = ROOT / "etobicoke" / "condo"
    if condo_root.is_dir():
        for child in sorted(condo_root.iterdir()):
            if child.is_dir() and (child / "index.html").is_file():
                urls.append((f"{ORIGIN}/etobicoke/condo/{child.name}/", "monthly", "0.8"))
    return urls


def main():
    city_urls = write_city_pages()
    listing_urls = write_listing_pages()
    neighbourhood_urls = write_neighbourhood_guide_pages()
    write_sitemap(city_urls + listing_urls + neighbourhood_urls + condo_guide_urls())
    if sync_homepage_footer(ROOT / "index.html"):
        print("synced homepage footer")
    else:
        print("warning: homepage footer sync failed")


if __name__ == "__main__":
    main()
