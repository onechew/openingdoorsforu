#!/usr/bin/env python3
"""Generate city pages, listing detail pages, and sitemap for SEO."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))
# Sitemap lastmod: ISO 8601 with timezone (W3C Datetime / sitemaps.org)
LASTMOD = (
    datetime.now(timezone.utc)
    .replace(hour=0, minute=0, second=0, microsecond=0)
    .isoformat()
)
ORIGIN = "https://openingdoorsforu.com"

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
            "Downtown and midtown towers trade on walkability; west and east pockets often balance transit with parking.",
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
        "title": "Etobicoke Realtor | Homes for Sale, Sold & Lease | Josh Schwartz",
        "description": "Etobicoke realtor Josh Schwartz with Thapar Team, #1 Team in Etobicoke. Current listings, recently sold and leased homes in Mimico, Islington, lake shore condos, and family neighbourhoods across Etobicoke.",
        "lead": "Etobicoke is Toronto’s west side: lake shore living, family neighbourhoods, and easy access to downtown and Pearson. Josh works with Thapar Team, #1 Team in Etobicoke.",
        "about": "Etobicoke is a primary focus for Josh Schwartz and Opening Doors For U. From Mimico and the lake shore to Islington and inland family streets, he helps clients buy, sell, and lease with practical guidance, backed by Thapar Team, #1 Team in Etobicoke.",
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
            "angle": "Thapar Team · #1 in Etobicoke",
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
    css = asset_href("assets/seo-pages.css", depth) + "?v=20260803bq"
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
        <a href="{home}#listings">Listings</a>
        <a href="{home}#condo-guide">Condo Guide</a>
        <a href="{home}#services">Services</a>
      </nav>
      <div class="header-utils">
        <div class="header-contact">
          <a class="call-phone" href="tel:+16473608179" aria-label="Call Josh">
            <span class="flag" aria-hidden="true">🇨🇦</span>
            <span class="phone-text">647-360-8179</span>
          </a>
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
  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-meta">
        <div>© {date.today().year} Josh Schwartz</div>
        <div>Sales Representative · Snobar Realty Group Inc., Brokerage</div>
      </div>
      <p class="footer-note">Advertising follows Ontario RECO rules under TRESA.</p>
    </div>
  </footer>
  <button class="back-to-top" id="backToTop" type="button" aria-label="Back to top" hidden>
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 18V7"></path>
      <path d="m6 11 6-6 6 6"></path>
    </svg>
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
</body>
</html>
"""


def cards_html(items: list[dict], depth: int, link_prefix: str) -> str:
    if not items:
        home = asset_href("", depth) or "./"
        thapar = "https://www.thaparteam.ca/property-search/results/?searchid=3952868"
        return (
            f'<p class="empty">Josh can help you buy, sell, or lease here. '
            f'<a href="{home}#contact">text Josh</a> or '
            f'<a href="{thapar}" target="_blank" rel="noopener noreferrer">browse live inventory</a>.</p>'
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
        img = asset_href(item.get("image", "assets/JS.jpg"), depth)
        if str(item.get("image") or "").startswith("http"):
            img = item["image"]
        loc = item.get("location") or item.get("area") or ""
        attr = ""
        if item.get("kind") == "team" or item.get("source") == "thapar":
            note = item.get("attribution") or "Listed with Snobar Realty Group Inc. · Thapar Team"
            attr = f'<p class="card-meta card-attr">{esc(note)}</p>'
        bits.append(
            f"""
      <a class="card" href="{esc(href)}"{target}>
        <div class="card-media"><img src="{esc(img)}" alt="{esc(item.get('alt') or item['title'])}" loading="lazy" width="800" height="600" /></div>
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


def write_city_pages():
    urls = []
    for key, meta in CITIES.items():
        current, past = city_items(key)
        sold, leased = split_past(past)
        depth = 1
        out_dir = ROOT / key
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"{ORIGIN}/{key}/"
        condo_cta = (
            '<a class="btn btn-primary" href="south-etobicoke-condo-guide/">Condo guide</a>'
            if key == "etobicoke"
            else ""
        )
        listings_btn = "btn-secondary" if key == "etobicoke" else "btn-primary"
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
        <a class="btn {listings_btn}" href="{asset_href('', depth)}#listings">View all listings</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Current Listings in {esc(meta['name'])}</h2>
      <p class="section-copy">Live inventory Josh can help you buy or lease in and around {esc(meta['name'])}. Team listings are with Snobar Realty Group / Thapar Team. Not all are personally listed by Josh.</p>
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
        <div class="stat"><strong>{esc(meta['snapshot']['metric'])}</strong><span>{esc(meta['snapshot']['metric_label'])}</span></div>
        <div class="stat"><strong>{esc(meta['snapshot']['angle'])}</strong><span>{esc(meta['snapshot']['angle_label'])}</span></div>
      </div>
      <p class="section-copy snapshot-note">{esc(meta['snapshot']['note'])} <span class="snapshot-cta">Ask Josh for a current {esc(meta['name'])} brief.</span></p>
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


ICON_BED = (
    '<svg class="fact-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M3 11V19M21 11V19M3 14H21M5 14V9.5C5 8.1 6.1 7 7.5 7H11C12.1 7 13 7.6 13.5 8.5C14 7.6 14.9 7 16 7H16.5C17.9 7 19 8.1 19 9.5V14M3 19H21" '
    'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)
ICON_BATH = (
    '<svg class="fact-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M5 12V7.5C5 6.1 6.1 5 7.5 5H9M5 12H20C20.6 12 21 12.4 21 13V15C21 17.2 19.2 19 17 19H7C4.8 19 3 17.2 3 15V13C3 12.4 3.4 12 4 12H5ZM8 19V21M16 19V21" '
    'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)
ICON_PARKING = (
    '<svg class="fact-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<circle cx="12" cy="12" r="8.25" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    '<path d="M10 16.5V7.5h3.2c1.7 0 2.8 1 2.8 2.5S14.9 12.5 13.2 12.5H10" '
    'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)
ICON_SIZE = (
    '<svg class="fact-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M5 9V5H9M15 5H19V9M19 15V19H15M9 19H5V15" '
    'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)
ICON_CONDO = (
    '<svg class="fact-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M4 20V9l5-3v14M9 20V6l7 4v10M13 10h2M13 13h2M13 16h2M6.5 12H7.5M6.5 15H7.5M4 20h16" '
    'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)


def infer_property_type(item: dict) -> str:
    if item.get("type"):
        return str(item["type"])
    blob = f"{item.get('title', '')} {item.get('alt', '')}"
    if re.search(r"triplex", blob, re.I):
        return "Triplex"
    if re.search(r"duplex", blob, re.I):
        return "Duplex"
    if re.search(r"townhouse|townhome|freehold town", blob, re.I):
        return "Townhouse"
    if re.search(r"\b(bsmt|basement|lower|upper)\b", blob, re.I):
        return "Apartment"
    if re.search(r"condo|apartment|apt", blob, re.I) or re.search(
        r"#\s*\d+|\d+\s*-\s*\d+", item.get("title", "")
    ):
        return "Condo Apt"
    return "Home"


def listing_facts_html(item: dict) -> str:
    facts = []
    if item.get("beds"):
        facts.append(
            f'<div class="fact">{ICON_BED}<span>{esc(count_label(item["beds"], "bed"))}</span></div>'
        )
    if item.get("baths"):
        facts.append(
            f'<div class="fact">{ICON_BATH}<span>{esc(count_label(item["baths"], "bath"))}</span></div>'
        )
    if item.get("parking") is not None and str(item.get("parking")).strip() != "":
        facts.append(
            f'<div class="fact">{ICON_PARKING}<span>{esc(count_label(item["parking"], "parking", "parking"))}</span></div>'
        )
    if item.get("size"):
        size = re.sub(r"\s*SQ\.?\s*FT\.?", " sqft", str(item["size"]), flags=re.I)
        size = size.replace("-", "–")
        facts.append(f'<div class="fact">{ICON_SIZE}<span>{esc(size)}</span></div>')
    # Always show property type (condo / home / etc.) on every listing page
    facts.append(
        f'<div class="fact">{ICON_CONDO}<span>{esc(infer_property_type(item))}</span></div>'
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
        img = asset_href(item.get("image", "assets/JS.jpg"), depth)
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
        <div class="card-media"><img src="{esc(asset_href(s.get('image','assets/JS.jpg'), depth))}" alt="{esc(s['title'])}" loading="lazy" /></div>
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
        facts_html = listing_facts_html(item)
        status = item.get("status") or ""
        location = item.get("location") or item.get("area") or ""

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
        area_section = neighbourhood_section_html(item, depth)

        body = f"""
  <section class="section">
    <div class="container">
      <p class="breadcrumb"><a href="{asset_href('', depth)}">Home</a> / <a href="{asset_href('', depth)}?tab=sold#listings">Sold &amp; Leased</a> / {esc(item['title'])}</p>
      <div class="listing-hero">
        <div class="listing-hero-media"><img src="{esc(img)}" alt="{esc(item.get('alt') or item['title'])}" width="1200" height="900" /></div>
        <div>
          <p class="eyebrow">{esc(status)}</p>
          <h1>{esc(item['title'])}</h1>
          <p class="lead">{esc(location)}</p>
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
    """Write a standards-compliant XML sitemap (UTF-8, ISO 8601 lastmod).

    Served from GitHub Pages as application/xml via the .xml extension.
    """
    city_urls = [(f"{ORIGIN}/{k}/", "weekly", "0.9") for k in CITIES]
    base = [
        (f"{ORIGIN}/", "weekly", "1.0"),
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


def main():
    city_urls = write_city_pages()
    listing_urls = write_listing_pages()
    write_sitemap(city_urls + listing_urls)


if __name__ == "__main__":
    main()
