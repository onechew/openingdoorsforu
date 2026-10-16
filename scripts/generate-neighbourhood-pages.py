#!/usr/bin/env python3
"""South Etobicoke neighbourhood guides nested under /etobicoke/neighbourhoods/.

IA follows broker best practice (McDadi-style hub + one page per neighbourhood):
  /etobicoke/neighbourhoods/           hub with wide photo tiles
  /etobicoke/neighbourhoods/{slug}/    dedicated guide page

Qualitative copy only. No invented prices, DOM, school rankings, or commute minutes.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "seo_pages", ROOT / "scripts" / "generate-seo-pages.py"
)
_seo = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_seo)

esc = _seo.esc
page_shell = _seo.page_shell
asset_href = _seo.asset_href
ORIGIN = _seo.ORIGIN

NEIGHBOURHOODS = [
    {
        "slug": "mimico",
        "name": "Mimico",
        "chip": "South Etobicoke",
        "blurb": "Waterfront living with village amenities, lake shore condos, and established residential streets.",
        "image": "assets/neighbourhoods/mimico.jpg",
        "about": [
            "Mimico sits on Toronto’s west waterfront in South Etobicoke, with a mix of lake shore condos, low-rise living, and established residential streets.",
            "GO, TTC, and highway access connect the community to downtown and the wider GTA, so buyers often weigh village amenities against commute convenience.",
        ],
        "lifestyle": "Parks, Mimico Village amenities, and waterfront access shape day-to-day living, with a calmer west-end rhythm than downtown condo corridors.",
        "housing": "Lake shore towers sit alongside low-rise and freehold pockets, so buyers often compare condo living with nearby residential streets before they write an offer.",
        "transit": "GO, TTC, Gardiner, and the 427 keep downtown and the wider GTA reachable without treating Mimico like a one-size-fits-all west waterfront market.",
        "why": [
            "Waterfront parks and village amenities in one South Etobicoke pocket",
            "Housing mix that spans lake shore condos and established streets",
            "Transit and highway access toward downtown and the GTA",
            "Clear local comps versus blanket west-end waterfront pricing",
        ],
        "fits": [
            "Professionals who want waterfront-adjacent living without downtown density",
            "Downsizers comparing Mimico condo buildings with nearby low-rise streets",
            "Households weighing GO and TTC convenience against neighbourhood feel",
            "Buyers, sellers, and renters who need Mimico-specific comps",
        ],
        "highlights": [
            {
                "icon": "park",
                "title": "Parks & waterfront",
                "detail": "Waterfront parks and lake access shape everyday outdoor routines.",
            },
            {
                "icon": "storefront",
                "title": "Village amenities",
                "detail": "Mimico Village shops and services support a local day-to-day rhythm.",
            },
            {
                "icon": "apartment",
                "title": "Mixed housing",
                "detail": "Lake shore condos sit beside low-rise and established residential streets.",
            },
            {
                "icon": "directions_subway",
                "title": "Transit friendly",
                "detail": "GO, TTC, and highway access keep downtown and the GTA reachable.",
            },
            {
                "icon": "volume_off",
                "title": "Calmer pace",
                "detail": "A west-end rhythm that feels quieter than downtown condo corridors.",
            },
        ],
        "adjacent": ["humber-bay", "new-toronto", "long-branch"],
        "condo_link": True,
    },
    {
        "slug": "long-branch",
        "name": "Long Branch",
        "chip": "South Etobicoke",
        "blurb": "Calmer lakeside streets, greenery, and parks such as Marie Curtis Park close at hand.",
        "image": "assets/neighbourhoods/long-branch.jpg",
        "about": [
            "Long Branch is one of South Etobicoke’s established lakeside communities. Expect a calm environment with tree-lined streets, greenery, and park space close at hand.",
            "Buyers and renters often weigh housing mix and neighbourhood feel against nearby Mimico, New Toronto, and Alderwood before they shortlist homes.",
        ],
        "lifestyle": "Quiet residential streetscapes, park space within everyday reach, and a calmer lakeside rhythm than downtown condo corridors.",
        "housing": "More grounded in low-rise and residential streets than high-rise lake shore towers, while still part of the broader west waterfront corridor.",
        "transit": "TTC, nearby GO options, and Gardiner access support commuting without forcing a downtown address.",
        "why": [
            "Established lakeside community character in South Etobicoke",
            "Residential streetscapes with a calmer pace than condo corridors",
            "Easy comparisons with Mimico, New Toronto, and Alderwood",
            "Parks and neighbourhood amenities within everyday reach",
        ],
        "fits": [
            "Buyers who prefer residential streets over high-rise condo corridors",
            "Renters and owners comparing Long Branch with nearby lakeside pockets",
            "Households who want parks and a quieter neighbourhood feel",
            "Anyone who needs clear South Etobicoke comps before offering",
        ],
        "highlights": [
            {
                "icon": "park",
                "title": "Parks",
                "detail": "Park space such as Marie Curtis Park sits within everyday reach.",
            },
            {
                "icon": "volume_off",
                "title": "Quiet",
                "detail": "Residential streetscapes with a calmer lakeside feel than condo corridors.",
            },
            {
                "icon": "home",
                "title": "Low-rise character",
                "detail": "More grounded in houses and residential streets than high-rise towers.",
            },
            {
                "icon": "directions_subway",
                "title": "Transit friendly",
                "detail": "TTC, nearby GO options, and Gardiner access support commuting.",
            },
            {
                "icon": "directions_bike",
                "title": "Cycling friendly",
                "detail": "Good for recreational cycling and bike-led trips along the west waterfront.",
            },
        ],
        "adjacent": ["new-toronto", "mimico", "alderwood"],
    },
    {
        "slug": "alderwood",
        "name": "Alderwood",
        "chip": "South Etobicoke",
        "blurb": "Established residential streets with a grounded, family-oriented feel.",
        "image": "assets/neighbourhoods/alderwood.jpg",
        "about": [
            "Alderwood is a South Etobicoke neighbourhood with established residential streets and a housing mix that often attracts families and long-term owners.",
            "Compared with high-rise lake shore living, Alderwood usually feels more grounded in low-rise homes, local amenities, and everyday neighbourhood routines.",
        ],
        "lifestyle": "Day-to-day life centres on residential streets, local amenities, and a steadier neighbourhood rhythm than the lake shore condo towers.",
        "housing": "Primarily low-rise and family homes, often compared with Long Branch, Mimico, and New Toronto when balancing lifestyle and commute.",
        "transit": "Local transit and highway access support cross-GTA routines without downtown density.",
        "why": [
            "Established residential streets with a family-oriented feel",
            "Low-rise housing mix versus high-rise lake shore living",
            "Practical comparisons with Long Branch, Mimico, and New Toronto",
            "Everyday neighbourhood amenities without downtown intensity",
        ],
        "fits": [
            "Families looking for established South Etobicoke streets",
            "Buyers comparing low-rise homes with nearby condo pockets",
            "Long-term owners planning a sale or next purchase",
            "Anyone who wants grounded neighbourhood comps before deciding",
        ],
        "highlights": [
            {
                "icon": "home",
                "title": "Residential streets",
                "detail": "Established low-rise streets with a grounded neighbourhood feel.",
            },
            {
                "icon": "family_restroom",
                "title": "Family oriented",
                "detail": "Housing mix and street character often attract long-term owners and families.",
            },
            {
                "icon": "storefront",
                "title": "Local amenities",
                "detail": "Day-to-day routines centre on nearby shops and neighbourhood services.",
            },
            {
                "icon": "directions_car",
                "title": "Practical access",
                "detail": "Transit and highway options support cross-GTA commuting without downtown density.",
            },
            {
                "icon": "volume_off",
                "title": "Steady pace",
                "detail": "Quieter than lake shore condo corridors, with a steadier residential rhythm.",
            },
        ],
        "adjacent": ["long-branch", "new-toronto", "stonegate-queensway"],
    },
    {
        "slug": "new-toronto",
        "name": "New Toronto",
        "chip": "South Etobicoke",
        "blurb": "Lakeside corridor between Mimico and Long Branch, with parks and quieter streets.",
        "image": "assets/neighbourhoods/new-toronto.jpg",
        "about": [
            "New Toronto sits on South Etobicoke’s lakeside corridor between Mimico and Long Branch. The feel is calmer than downtown condo strips.",
            "Tree-lined streets, greenery, and Colonel Samuel Smith Park shape day-to-day living, with Lake Shore transit and highway access keeping downtown reachable.",
        ],
        "lifestyle": "A quieter lakeside rhythm, with parks close by, greenery on residential streets, and a corridor character between Mimico’s village energy and Long Branch’s residential calm.",
        "housing": "Mixed housing styles across the corridor, so local comps matter more than treating the entire west-end waterfront as interchangeable.",
        "transit": "Lake Shore transit, nearby GO options, and Gardiner access support commuting without downtown density.",
        "why": [
            "Calm lakeside corridor with tree-lined streets and greenery",
            "Colonel Samuel Smith Park and waterfront green space close at hand",
            "Transit-friendly Lake Shore access without downtown density",
            "Mixed housing that needs New Toronto comps, not blanket waterfront pricing",
        ],
        "fits": [
            "Buyers comparing New Toronto with Mimico and Long Branch",
            "Households who want parks, quieter streets, and lakeside access",
            "Cyclists and transit riders who still want a calmer neighbourhood feel",
            "Sellers who need local comps rather than one-size-fits-all west-end pricing",
        ],
        "highlights": [
            {
                "icon": "park",
                "title": "Parks & greenery",
                "detail": "Colonel Samuel Smith Park and tree-lined streets shape day-to-day living.",
            },
            {
                "icon": "volume_off",
                "title": "Quiet corridor",
                "detail": "Calmer than downtown condo strips, between Mimico and Long Branch.",
            },
            {
                "icon": "home",
                "title": "Mixed housing",
                "detail": "Local comps matter more than treating the whole west waterfront as one market.",
            },
            {
                "icon": "directions_subway",
                "title": "Transit friendly",
                "detail": "Lake Shore transit, nearby GO options, and Gardiner access support commuting.",
            },
            {
                "icon": "directions_bike",
                "title": "Cycling friendly",
                "detail": "Lakeside paths and corridor streets support recreational and practical cycling.",
            },
        ],
        "adjacent": ["mimico", "long-branch", "alderwood"],
    },
    {
        "slug": "humber-bay",
        "name": "Humber Bay",
        "chip": "South Etobicoke",
        "blurb": "Lake shore condo living along Humber Bay Shores, with trails and amenity-forward towers.",
        "image": "assets/neighbourhoods/humber-bay.jpg",
        "about": [
            "Humber Bay, including Humber Bay Shores, is known for lake shore condo living, waterfront paths, and easy connections toward downtown along Toronto’s west waterfront.",
            "The housing mix skews toward condo buildings and amenity-focused living, which attracts professionals, downsizers, and relocators comparing lifestyle with other South Etobicoke pockets.",
        ],
        "lifestyle": "Waterfront trails, parkland, and amenity-forward condo living define the everyday rhythm along Lake Shore and Marine Parade.",
        "housing": "Primarily condo towers and suite living, where building choice, fees, and views matter as much as the neighbourhood label.",
        "transit": "Streetcar, Gardiner access, and bike paths support commuting and recreation along the west waterfront.",
        "why": [
            "Lake shore condo living with waterfront paths and parks",
            "Amenity-focused towers that trade on lifestyle and views",
            "Convenient connections toward downtown along the west waterfront",
            "Clear building-by-building comps across Humber Bay Shores",
        ],
        "fits": [
            "Buyers who want newer high-rise waterfront condo living",
            "Downsizers drawn to amenity programming and lake access",
            "Relocators comparing Humber Bay with Mimico and nearby pockets",
            "Anyone evaluating condo buildings systematically before offering",
        ],
        "highlights": [
            {
                "icon": "apartment",
                "title": "Condo living",
                "detail": "Amenity-forward towers define the housing mix along Humber Bay Shores.",
            },
            {
                "icon": "park",
                "title": "Waterfront paths",
                "detail": "Trails and parkland support lakeside walks and everyday outdoor time.",
            },
            {
                "icon": "pool",
                "title": "Amenity focused",
                "detail": "Building lifestyle and views matter as much as the neighbourhood label.",
            },
            {
                "icon": "directions_subway",
                "title": "Transit friendly",
                "detail": "Streetcar and Gardiner access support commuting along the west waterfront.",
            },
            {
                "icon": "directions_bike",
                "title": "Cycling friendly",
                "detail": "Bike paths along the lake shore support recreation and practical trips.",
            },
        ],
        "adjacent": ["mimico", "stonegate-queensway", "new-toronto"],
        "condo_link": True,
    },
    {
        "slug": "stonegate-queensway",
        "name": "Stonegate-Queensway",
        "chip": "Etobicoke",
        "blurb": "Established streets with Queensway corridor convenience toward the rest of Toronto.",
        "image": "assets/neighbourhoods/stonegate-queensway.jpg",
        "about": [
            "Stonegate-Queensway sits in South Etobicoke with a blend of residential streets and practical access along the Queensway corridor toward the rest of Toronto.",
            "Clients often compare its housing mix and lifestyle with Mimico, Alderwood, and nearby west-end pockets when deciding between condo and low-rise options.",
        ],
        "lifestyle": "Established neighbourhood living with convenient amenities along the Queensway corridor and practical access toward the wider city.",
        "housing": "A blend of residential streets and practical housing options, often weighed against Mimico and Alderwood condo-versus-low-rise tradeoffs.",
        "transit": "Queensway corridor access supports commuting across Etobicoke and into the broader GTA.",
        "why": [
            "Established residential feel with Queensway corridor convenience",
            "Practical access toward the rest of Toronto",
            "Useful comparisons with Mimico, Alderwood, and nearby west-end pockets",
            "Housing mix that supports condo and low-rise decision-making",
        ],
        "fits": [
            "Buyers comparing Stonegate-Queensway with Mimico and Alderwood",
            "Households who want established streets with corridor convenience",
            "Sellers and renters who need local comps before moving",
            "Anyone balancing lifestyle, amenities, and commute without downtown living",
        ],
        "highlights": [
            {
                "icon": "home",
                "title": "Established streets",
                "detail": "Residential character with a steadier pace than downtown condo corridors.",
            },
            {
                "icon": "storefront",
                "title": "Corridor amenities",
                "detail": "Everyday shops and services along the Queensway corridor.",
            },
            {
                "icon": "apartment",
                "title": "Housing mix",
                "detail": "Condo and low-rise options that need local comps, not blanket west-end pricing.",
            },
            {
                "icon": "directions_bus",
                "title": "Practical access",
                "detail": "Queensway corridor links support commuting across Etobicoke and the GTA.",
            },
            {
                "icon": "near_me",
                "title": "City convenient",
                "detail": "Useful comparisons with Mimico and Alderwood when balancing lifestyle and commute.",
            },
        ],
        "adjacent": ["mimico", "alderwood", "humber-bay"],
    },
]

BY_SLUG = {n["slug"]: n for n in NEIGHBOURHOODS}


def _faq_answer(name: str) -> str:
    return (
        f"Josh Schwartz is a Sales Representative with Snobar Realty Group Inc., Brokerage, "
        f"backed by Thapar Team (#1 team in Etobicoke). He helps buyers, sellers, and renters "
        f"in {name} and across South Etobicoke with clear market facts and no gimmicks. "
        f"Contact Josh at +1-647-360-8179."
    )


def _hood_tiles(depth: int, *, exclude: str | None = None) -> str:
    bits = []
    for n in NEIGHBOURHOODS:
        if exclude and n["slug"] == exclude:
            continue
        href = asset_href(f"etobicoke/neighbourhoods/{n['slug']}/", depth)
        img = asset_href(n["image"], depth)
        bits.append(
            f"""
      <a class="hood-tile" href="{esc(href)}" aria-label="{esc(n['name'])} neighbourhood guide">
        <img src="{esc(img)}" alt="" loading="lazy" width="1600" height="1000" />
        <span class="hood-tile-label">
          <span class="hood-tile-name">{esc(n['name'])}</span>
          <span class="hood-tile-meta">{esc(n['chip'])}</span>
        </span>
      </a>"""
        )
    return '<div class="hood-grid">' + "".join(bits) + "</div>"


def _icon(name: str, extra_class: str = "") -> str:
    cls = f"material-symbols-outlined {extra_class}".strip()
    return f'<span class="{cls}" aria-hidden="true">{esc(name)}</span>'


def _highlights_html(n: dict) -> str:
    items = []
    for h in n.get("highlights") or []:
        items.append(
            f"""
      <li class="hood-trait">
        {_icon(h["icon"], "hood-trait-icon")}
        <div class="hood-trait-copy">
          <span class="hood-trait-title">{esc(h["title"])}</span>
          <p class="hood-trait-detail">{esc(h["detail"])}</p>
        </div>
      </li>"""
        )
    return '<ul class="hood-trait-list">' + "".join(items) + "</ul>"


def _jump_nav_html() -> str:
    pills = [
        ("#highlights", "park", "is-nature", "Highlights"),
        ("#lifestyle", "local_activity", "is-character", "Lifestyle"),
        ("#housing", "home", "is-housing", "Housing"),
        ("#transit", "directions_subway", "is-transit", "Transit"),
        ("#fits", "person", "is-fit", "Who it fits"),
    ]
    bits = []
    for href, icon, tone, label in pills:
        bits.append(
            f'<a class="hood-jump-pill {tone}" href="{href}">'
            f"{_icon(icon, 'hood-jump-icon')}<span>{esc(label)}</span></a>"
        )
    return (
        '<nav class="hood-jump" aria-label="On this page">'
        + "".join(bits)
        + "</nav>"
    )


def _check_list_html(items: list[str], *, icon: str) -> str:
    bits = []
    for item in items:
        bits.append(
            f'<li class="hood-check-item">{_icon(icon, "hood-check-icon")}'
            f"<span>{esc(item)}</span></li>"
        )
    return '<ul class="hood-check-list">' + "".join(bits) + "</ul>"


def _panel(title: str, icon: str, body: str, *, section_id: str) -> str:
    return f"""
  <section class="section hood-panel" id="{esc(section_id)}">
    <div class="container">
      <div class="hood-panel-head">
        {_icon(icon, "hood-panel-icon")}
        <h2>{esc(title)}</h2>
      </div>
      {body}
    </div>
  </section>
"""


def build_hub() -> tuple[str, str]:
    depth = 2
    canonical = f"{ORIGIN}/etobicoke/neighbourhoods/"
    title = "Etobicoke Neighbourhoods | Josh Schwartz"
    description = (
        "Explore Mimico, Long Branch, Alderwood, New Toronto, Humber Bay, and Stonegate-Queensway "
        "with Josh Schwartz. South Etobicoke neighbourhood guides nested under the Etobicoke city page."
    )
    body = f"""
  <section class="hero-band">
    <div class="container">
      <p class="breadcrumb"><a href="{asset_href('', depth)}">Home</a> / <a href="{asset_href('etobicoke/', depth)}">Etobicoke</a> / Neighbourhoods</p>
      <h1>Etobicoke neighbourhoods</h1>
      <p class="lead">South Etobicoke communities with clear local guidance. Not one-size-fits-all advice.</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="tel:+16473608179">Call Josh</a>
        <a class="btn btn-secondary" href="{asset_href('etobicoke/', depth)}">Etobicoke listings</a>
        <a class="btn btn-secondary" href="{asset_href('etobicoke/south-etobicoke-condo-guide/', depth)}">Condo guide</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Areas of focus</h2>
      <p class="section-copy">Each guide covers lifestyle, housing mix, transit context, and who the neighbourhood tends to fit. Open a community for the full page.</p>
      {_hood_tiles(depth)}
    </div>
  </section>
"""
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Etobicoke Neighbourhoods",
        "url": canonical,
        "description": description,
        "isPartOf": {"@type": "WebSite", "url": f"{ORIGIN}/"},
        "about": {"@type": "Place", "name": "Etobicoke"},
    }
    html = page_shell(
        title=title,
        description=description,
        canonical=canonical,
        depth=depth,
        body=body,
        json_ld=json_ld,
    )
    return canonical, html


def build_page(n: dict) -> tuple[str, str]:
    depth = 3
    slug = n["slug"]
    name = n["name"]
    canonical = f"{ORIGIN}/etobicoke/neighbourhoods/{slug}/"
    title = f"{name} Neighbourhood Guide | Etobicoke | Josh Schwartz"
    description = (
        f"{name} in Etobicoke with Josh Schwartz. Lifestyle, housing mix, transit context, "
        f"and clear local guidance for buyers, sellers, and renters."
    )
    img = asset_href(n["image"], depth)
    about_html = "".join(f"<p>{esc(p)}</p>" for p in n["about"])
    adjacent_bits = []
    for adj in n.get("adjacent") or []:
        other = BY_SLUG.get(adj)
        if not other:
            continue
        href = asset_href(f"etobicoke/neighbourhoods/{other['slug']}/", depth)
        adjacent_bits.append(f'<a href="{esc(href)}">{esc(other["name"])}</a>')
    adjacent_html = " · ".join(adjacent_bits) if adjacent_bits else ""
    condo_cta = ""
    if n.get("condo_link"):
        condo_cta = (
            f'<a class="btn btn-secondary" href="{asset_href("etobicoke/south-etobicoke-condo-guide/", depth)}">'
            "Condo guide</a>"
        )
    faq_a = _faq_answer(name)
    body = f"""
  <section class="hero-band" id="overview">
    <div class="container">
      <p class="breadcrumb"><a href="{asset_href('', depth)}">Home</a> / <a href="{asset_href('etobicoke/', depth)}">Etobicoke</a> / <a href="{asset_href('etobicoke/neighbourhoods/', depth)}">Neighbourhoods</a> / {esc(name)}</p>
      <p class="condo-area-chip-wrap"><span class="condo-area-chip">{esc(n['chip'])}</span></p>
      <h1>{esc(name)}</h1>
      <p class="lead">{esc(n['blurb'])}</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="tel:+16473608179">Call Josh</a>
        <a class="btn btn-secondary" href="{asset_href('etobicoke/', depth)}">Etobicoke listings</a>
        {condo_cta}
      </div>
      <figure class="hood-cover">
        <img src="{esc(img)}" alt="{esc(name)}, Etobicoke neighbourhood" width="1920" height="844" />
      </figure>
    </div>
  </section>

  <section class="section hood-snapshot" id="about">
    <div class="container">
      <h2>About {esc(name)}</h2>
      <div class="prose hood-snapshot-prose">{about_html}</div>
      {_jump_nav_html()}
      <div class="hood-snapshot-overview" id="highlights">
        <p class="hood-snapshot-label">Overview</p>
        {_highlights_html(n)}
      </div>
    </div>
  </section>

{_panel("Lifestyle", "local_activity", f'<div class="prose"><p>{esc(n["lifestyle"])}</p></div>', section_id="lifestyle")}
{_panel("Housing mix", "home", f'<div class="prose"><p>{esc(n["housing"])}</p></div>', section_id="housing")}
{_panel("Getting around", "directions_subway", f'<div class="prose"><p>{esc(n["transit"])}</p></div>', section_id="transit")}
{_panel(f"Why buyers look at {name}", "check_circle", _check_list_html(n["why"], icon="check"), section_id="why")}
{_panel("Who it tends to fit", "person", _check_list_html(n["fits"], icon="person"), section_id="fits")}

  <section class="section" id="faq">
    <div class="container">
      <div class="hood-panel-head">
        {_icon("help", "hood-panel-icon")}
        <h2>FAQ</h2>
      </div>
      <div class="prose">
        <h3>Who is the best realtor in {esc(name)}?</h3>
        <p>{esc(faq_a)}</p>
        <h3>Should I buy a condo or a house?</h3>
        <p>It depends on your lifestyle, budget, maintenance preferences, and long term goals. Condos often require less maintenance, while freehold homes typically provide more space and flexibility.</p>
        <h3>How do I get started?</h3>
        <p>Reach out for a conversation. We will discuss your goals, answer your questions, and create a plan that fits your timeline whether you are buying, selling, investing, or leasing.</p>
      </div>
    </div>
  </section>

  <section class="section" id="nearby">
    <div class="container">
      <div class="hood-panel-head">
        {_icon("map", "hood-panel-icon")}
        <h2>Nearby neighbourhoods</h2>
      </div>
      <p class="section-copy">{adjacent_html}</p>
      {_hood_tiles(depth, exclude=slug)}
      <p class="section-copy" style="margin-top:24px">
        <a class="text-link" href="{asset_href('etobicoke/neighbourhoods/', depth)}">All Etobicoke neighbourhoods</a>
      </p>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>Work with Josh in {esc(name)}</h2>
      <p class="section-copy">Clear local comps, no gimmicks. Call or text for current inventory and neighbourhood fit.</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="tel:+16473608179">Call +1-647-360-8179</a>
        <button
          class="btn btn-secondary copy-email"
          type="button"
          data-email="josh@thaparteam.ca"
          aria-label="Copy Josh's email"
        >
          <span class="copy-email-text">Copy Josh's email</span>
        </button>
      </div>
    </div>
  </section>
"""
    agent_ld = {
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "@id": f"{ORIGIN}/#agent",
        "name": "Josh Schwartz",
        "telephone": "+1-647-360-8179",
        "email": "josh@thaparteam.ca",
        "url": f"{ORIGIN}/",
        "areaServed": [name, "South Etobicoke", "Etobicoke"],
        "parentOrganization": {
            "@type": "RealEstateAgency",
            "name": "Snobar Realty Group Inc., Brokerage",
        },
        "memberOf": {"@type": "Organization", "name": "Thapar Team"},
        "description": (
            f"Josh Schwartz is a Sales Representative serving {name} and South Etobicoke. "
            "15 years in real estate, backed by Thapar Team (#1 team in Etobicoke)."
        ),
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"Who is the best realtor in {name}?",
                "acceptedAnswer": {"@type": "Answer", "text": faq_a},
            }
        ],
    }
    html = page_shell(
        title=title,
        description=description,
        canonical=canonical,
        depth=depth,
        body=body,
        json_ld=agent_ld,
    )
    inject = f'<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>\n'
    html = html.replace("</head>", inject + "</head>", 1)
    return canonical, html


def write_neighbourhood_pages() -> list[tuple[str, str, str]]:
    urls: list[tuple[str, str, str]] = []
    hub_dir = ROOT / "etobicoke" / "neighbourhoods"
    hub_dir.mkdir(parents=True, exist_ok=True)
    hub_url, hub_html = build_hub()
    (hub_dir / "index.html").write_text(hub_html, encoding="utf-8")
    urls.append((hub_url, "weekly", "0.85"))
    print("wrote etobicoke/neighbourhoods/")

    for n in NEIGHBOURHOODS:
        out_dir = hub_dir / n["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        page_url, page_html = build_page(n)
        (out_dir / "index.html").write_text(page_html, encoding="utf-8")
        urls.append((page_url, "weekly", "0.8"))
        print(f"wrote etobicoke/neighbourhoods/{n['slug']}/")

    (ROOT / "data" / "neighbourhoods.json").write_text(
        json.dumps(
            [{"slug": n["slug"], "name": n["name"]} for n in NEIGHBOURHOODS],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return urls


def main() -> None:
    urls = write_neighbourhood_pages()
    print(f"neighbourhood pages: {len(urls)}")


if __name__ == "__main__":
    main()
