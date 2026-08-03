#!/usr/bin/env python3
"""Generate South Etobicoke condo guide index + per-building pages."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "condo-guide.json").read_text(encoding="utf-8"))
ORIGIN = "https://openingdoorsforu.com"
LASTMOD = (
    datetime.now(timezone.utc)
    .replace(hour=0, minute=0, second=0, microsecond=0)
    .isoformat()
)

GUIDE_DIR = ROOT / "etobicoke" / "south-etobicoke-condo-guide"
CONDO_DIR = ROOT / "etobicoke" / "condo"


def esc(text: object) -> str:
    return xml_escape(str(text))


def area_chip(area: object) -> str:
    """Condo chips only classify Mimico vs Humber Bay."""
    raw = str(area or "").strip().lower()
    if "mimico" in raw or "mystic" in raw:
        return "Mimico"
    return "Humber Bay"


def maps_url(address: object, area: object = "") -> str:
    query = f"{address}, {area}, Toronto, ON".replace("  ", " ").strip(", ")
    return f"https://www.google.com/maps/search/?api=1&query={quote(query)}"


def asset(path: str, depth: int) -> str:
    if not path:
        return ""
    return ("../" * depth) + path.lstrip("/")


def page_shell(
    *,
    title: str,
    description: str,
    canonical: str,
    depth: int,
    body: str,
    json_ld: dict | None = None,
    og_image: str | None = None,
) -> str:
    prefix = "../" * depth
    image = og_image or f"{ORIGIN}/assets/JS.jpg"
    ld = ""
    if json_ld:
        ld = f'\n  <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>'
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
  <meta property="og:image" content="{esc(image)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{esc(image)}" />
  <link rel="icon" href="{prefix}favicon.ico" sizes="any" />
  <link rel="icon" href="{prefix}assets/js.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png" sizes="180x180" />
  <link rel="preload" href="{prefix}assets/fonts/plus-jakarta-sans-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="{prefix}assets/fonts/cormorant-garamond-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0..1,0&display=swap" />
  <link rel="stylesheet" href="{prefix}assets/seo-pages.css?v=20260803bx" />{ld}
</head>
<body>
  <header class="site-header">
    <div class="container nav">
      <a class="brand" href="{prefix}" aria-label="Josh Schwartz home">
        <div class="brand-mark" aria-hidden="true">
          <img src="{prefix}assets/js-on-light.svg" alt="Josh Schwartz Opening Doors For U logo" />
        </div>
        <div class="brand-lockup">
          <span class="brand-name">Josh Schwartz</span>
          <img class="brand-snobar" src="{prefix}assets/snobar-dark.svg" alt="Snobar Realty Group Inc., Brokerage" />
        </div>
      </a>
      <nav class="nav-links" aria-label="Primary navigation">
        <a href="{prefix}#listings">Listings</a>
        <a href="{prefix}#condo-guide">Condo Guide</a>
        <a href="{prefix}#services">Services</a>
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
        <div>© 2026 Josh Schwartz</div>
        <div>Sales Representative · Snobar Realty Group Inc., Brokerage</div>
      </div>
      <p class="footer-note">Advertising follows Ontario RECO rules under TRESA. Building facts are for guidance and may change.</p>
    </div>
  </footer>
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

    document.querySelectorAll("video[data-autoplay-loop]").forEach((video) => {{
      const tryPlay = () => video.play().catch(() => {{}});
      video.addEventListener("loadeddata", tryPlay, {{ once: true }});
      const io = new IntersectionObserver((entries) => {{
        entries.forEach((entry) => {{
          if (entry.isIntersecting) tryPlay();
          else video.pause();
        }});
      }}, {{ threshold: 0.35 }});
      io.observe(video);
    }});

    document.querySelectorAll("[data-photo-rail]").forEach((rail) => {{
      const slides = Array.from(rail.querySelectorAll(".condo-photo-rail-slide"));
      if (slides.length < 2) return;
      let index = 0;
      let timer = 0;
      const show = (next) => {{
        index = (next + slides.length) % slides.length;
        slides.forEach((slide, i) => {{
          slide.classList.toggle("is-active", i === index);
        }});
      }};
      const play = () => {{
        window.clearInterval(timer);
        timer = window.setInterval(() => show(index + 1), 3800);
      }};
      slides.forEach((slide, i) => {{
        slide.addEventListener("click", () => {{
          show(i);
          play();
        }});
      }});
      rail.addEventListener("mouseenter", () => window.clearInterval(timer));
      rail.addEventListener("mouseleave", play);
      show(0);
      play();
    }});

    (function initCondoGuideSort() {{
      const grid = document.querySelector("[data-condo-guide-grid]");
      const controls = document.querySelector("[data-condo-sort]");
      if (!grid || !controls) return;
      const cards = Array.from(grid.querySelectorAll(".condo-guide-tile"));
      const buttons = Array.from(controls.querySelectorAll("[data-sort]"));
      const apply = (mode) => {{
        const sorted = cards.slice().sort((a, b) => {{
          if (mode === "built") {{
            const yb = Number(b.dataset.year || 0) - Number(a.dataset.year || 0);
            if (yb !== 0) return yb;
          }}
          return String(a.dataset.name || "").localeCompare(String(b.dataset.name || ""), "en", {{ sensitivity: "base" }});
        }});
        sorted.forEach((card) => grid.appendChild(card));
        buttons.forEach((btn) => {{
          const active = btn.getAttribute("data-sort") === mode;
          btn.classList.toggle("is-active", active);
          btn.setAttribute("aria-pressed", active ? "true" : "false");
        }});
      }};
      controls.addEventListener("click", (event) => {{
        const btn = event.target.closest("[data-sort]");
        if (!btn) return;
        apply(btn.getAttribute("data-sort") || "az");
      }});
      apply("az");
    }})();
  </script>
</body>
</html>
"""


FACT_ICONS = {
    "Complex": "apartment",
    "Neighbourhood": "location_on",
    "Completed": "calendar_month",
    "Status": "check",
    "Buildings": "apartment",
    "Storeys": "floor",
    "Height": "height",
    "Units": "grid_view",
    "Suite sizes": "square_foot",
    "Developer": "home_work",
    "Architect": "architecture",
    "Condo corp.": "description",
    "Management": "badge",
    "Interior design": "design_services",
    "Security": "security",
    "Water views": "waves",
    "Pets": "pet_supplies",
    "Website": "language",
    "HoodQ": "home",
}

AMENITY_ICONS = {
    "Air Conditioning": "ac_unit",
    "Building Insurance": "shield",
    "Common Element Maintenance": "build",
    "Heat": "mode_heat",
    "Hydro": "bolt",
    "Water": "water_drop",
    "Parking": "directions_car",
    "Cable TV": "tv",
    "Car Wash Bay": "local_car_wash",
    "Community BBQ": "outdoor_grill",
    "Concierge": "concierge",
    "Enter Phone System": "dialpad",
    "Games / Recreation Room": "sports_esports",
    "Gym / Exercise": "fitness_center",
    "Hot Tub / Jacuzzi": "hot_tub",
    "Media Room / Cinema": "theaters",
    "Meeting / Function Room": "meeting_room",
    "Party Room": "liquor",
    "Pet Wash": "pet_supplies",
    "Playground": "person_play",
    "Pool - Indoor": "pool",
    "Pool - Outdoor": "pool",
    "Sauna": "sauna",
    "Security Guard": "security",
    "Visitor Lounge": "weekend",
    "Visitor Parking": "directions_car",
    "Yoga Studio": "sports_gymnastics",
    "Guest Suites": "bed",
    "Golf Simulator": "golf_course",
    "Putting Green": "golf_course",
    "Squash Court": "sports_tennis",
    "Tennis Court": "sports_tennis",
    "Business Centre": "laptop_mac",
    "Bike Storage": "pedal_bike",
    "Library": "menu_book",
    "Private Shuttle": "airport_shuttle",
    "Valet Parking": "garage",
    "Spa": "spa",
    "Steam Room": "humidity_low",
    "Rooftop Terrace": "deck",
    "Basketball Court": "sports_basketball",
}


# Material Security uses the checkered `security` glyph (filled, not outline `shield`).
FILLED_ICON_LABELS = frozenset({"Security", "Security Guard"})


def material_icon(name: str, css_class: str, *, filled: bool = False) -> str:
    """Google Material Symbols Outlined icon (https://fonts.google.com/icons)."""
    fill_class = " is-filled" if filled else ""
    return (
        f'<span class="material-symbols-outlined {css_class}{fill_class}" aria-hidden="true">'
        f"{name}</span>"
    )


def fact_icon(label: str) -> str:
    return material_icon(
        FACT_ICONS.get(label) or FACT_ICONS["Complex"],
        "condo-fact-icon",
        filled=label in FILLED_ICON_LABELS,
    )


def icon_markup(label: str) -> str:
    return material_icon(
        AMENITY_ICONS.get(label) or "support_agent",
        "condo-icon",
        filled=label in FILLED_ICON_LABELS,
    )



def website_host(url: str) -> str:
    host = (url or "").replace("https://", "").replace("http://", "").split("/")[0]
    return host[4:] if host.startswith("www.") else host


def overview_facts(b: dict) -> str:
    """Compact icon facts for the hero media column (beside video/cover)."""
    size = b.get("sizeRange")
    if b.get("sizeMin") and b.get("sizeMax"):
        size = f"{b['sizeMin']} – {b['sizeMax']}"
    towers = b.get("towers") or []
    storeys_value: object = b.get("floors")
    if towers:
        storeys_value = "__TOWERS__"
    rows = [
        # Location
        ("Neighbourhood", area_chip(b.get("area"))),
        # Timeline
        ("Completed", b.get("yearBuilt")),
        ("Status", b.get("status")),
        # Building form
        ("Buildings", b.get("buildings")),
        ("Storeys", storeys_value),
        ("Height", b.get("height")),
        ("Units", b.get("units")),
        ("Suite sizes", size),
        # Design team + operations (Architect | Management share a row in 2-col)
        ("Developer", b.get("builder")),
        ("Interior design", b.get("designer")),
        ("Architect", b.get("architect")),
        ("Management", b.get("management")),
        ("Condo corp.", b.get("condoCorp")),
        ("Security", b.get("security")),
        # Living
        ("Water views", b.get("waterViews")),
        ("Pets", b.get("pets")),
    ]
    items = []
    for label, value in rows:
        if value in ("", None):
            continue
        if label == "Pets":
            primary, note = split_primary_note(value)
            detail = (
                f'<span class="condo-fact-note">{esc(note)}</span>' if note else ""
            )
            body = f'<span class="condo-fact-main">{esc(primary)}</span>{detail}'
        elif label == "Storeys" and towers:
            floors = " & ".join(str(t["floors"]) for t in towers)
            body = f'<span class="condo-fact-main">{esc(floors)}</span>'
        else:
            body = f'<span class="condo-fact-main">{esc(value)}</span>'
        items.append(
            f'<li class="condo-fact-item">'
            f"{fact_icon(label)}"
            f'<div class="condo-fact-copy">'
            f'<span class="condo-fact-label">{esc(label)}</span>'
            f'<div class="condo-fact-value">{body}</div>'
            f"</div></li>"
        )
    if not items:
        return ""
    return f'<ul class="condo-fact-list">{"".join(items)}</ul>'


def title_block(b: dict) -> str:
    """Building name with optional official website beside it."""
    website = b.get("website") or ""
    site_html = ""
    if website:
        host = website_host(website)
        ext = material_icon("open_in_new", "condo-title-website-icon")
        site_html = (
            f'<a class="condo-title-website" href="{esc(website)}" '
            f'target="_blank" rel="noopener noreferrer">'
            f'<span>{esc(host)}</span>{ext}</a>'
        )
    return f"""
            <div class="condo-title-row">
              <h1>{esc(b["name"])}</h1>
              {site_html}
            </div>"""


def location_block(b: dict) -> str:
    """Address with building icon and Google Maps."""
    area = area_chip(b.get("area", ""))
    building_icon = material_icon("apartment", "condo-location-icon")
    maps_icon = material_icon("location_on", "condo-location-maps-icon")

    def maps_link(address: str) -> str:
        return (
            f'<a class="condo-location-directions" href="{esc(maps_url(address, area))}" '
            f'target="_blank" rel="noopener noreferrer">{maps_icon}Google Maps</a>'
        )

    towers = b.get("towers") or []
    if towers:
        lines = "".join(
            f'<li>'
            f'{building_icon}'
            f'<div class="condo-location-body">'
            f'<div class="condo-location-row">'
            f'<span class="condo-location-line">{esc(t["address"])}</span>'
            f'{maps_link(t["address"])}'
            f"</div>"
            f'<span class="condo-location-meta">{esc(t["name"])} · {esc(t["floors"])} storeys</span>'
            f"</div>"
            f"</li>"
            for t in towers
        )
        return f'<ul class="condo-location-list">{lines}</ul>'

    return f"""
        <div class="condo-location-single">
          {building_icon}
          <div class="condo-location-body">
            <div class="condo-location-row">
              <span class="condo-location-line">{esc(b["address"])}</span>
              {maps_link(b["address"])}
            </div>
          </div>
        </div>"""


def media_block(b: dict, depth: int) -> str:
    """Hero right column: video when available, otherwise building cover."""
    poster = asset(b.get("poster", ""), depth)
    video_src = b.get("video") or ""
    video = asset(video_src, depth) if video_src else ""
    ig = b.get("instagram") or "https://www.instagram.com/openingdoorsforu/reels/"
    avatar = asset("assets/J_S.png", depth)
    if video:
        return f"""
        <div class="condo-media has-video">
          <video data-autoplay-loop muted loop playsinline preload="metadata" poster="{esc(poster)}" src="{esc(video)}"></video>
          <div class="ig-reel-id" aria-hidden="true">
            <div class="ig-reel-avatar">
              <img src="{esc(avatar)}" alt="" loading="lazy" decoding="async" />
            </div>
            <div class="ig-reel-copy">
              <span class="ig-reel-handle">openingdoorsforu</span>
            </div>
          </div>
          <a class="condo-media-link" href="{esc(ig)}" target="_blank" rel="noopener noreferrer" aria-label="Watch {esc(b['name'])} amenity tour on Instagram"></a>
        </div>"""
    return f"""
        <div class="condo-media condo-cover">
          <img src="{esc(poster)}" alt="{esc(b['name'])} at {esc(b['address'])}" loading="eager" width="900" height="1200" />
        </div>"""


def building_photo_block(b: dict, depth: int) -> str:
    """Place cover photo in the body when hero already shows a tour video."""
    if not b.get("video"):
        return ""
    poster = asset(b.get("poster", ""), depth)
    if not poster:
        return ""
    gallery = [g for g in (b.get("gallery") or []) if g][:3]
    rail = ""
    if len(gallery) >= 2:
        slides = "".join(
            f'<figure class="condo-photo-rail-slide{" is-active" if i == 0 else ""}" data-rail-index="{i}">'
            f'<img src="{esc(asset(src, depth))}" alt="{esc(b["name"])} detail {i + 1}" '
            f'loading="lazy" width="960" height="640" />'
            f"</figure>"
            for i, src in enumerate(gallery)
        )
        rail = f"""
        <div class="condo-photo-rail" data-photo-rail aria-label="{esc(b['name'])} photo carousel">
          {slides}
        </div>"""
    return f"""
  <section class="section condo-building-photo-section">
    <div class="container">
      <div class="condo-photo-layout{" has-rail" if rail else ""}">
        <div class="condo-building-photo">
          <img src="{esc(poster)}" alt="{esc(b['name'])} at {esc(b['address'])}" loading="lazy" width="1400" height="900" />
        </div>
        {rail}
      </div>
      <p class="condo-building-photo-caption">{esc(b['name'])} · {esc(b['address'])}</p>
    </div>
  </section>"""


def split_primary_note(value: object) -> tuple[str, str]:
    """Split 'Primary · secondary detail' into hierarchy parts."""
    text = str(value).strip()
    for sep in (" · ", " — ", " – ", " - "):
        if sep in text:
            primary, note = text.split(sep, 1)
            return primary.strip(), note.strip()
    return text, ""


def icon_grid(items: list, empty_message: str = "") -> str:
    if not items:
        return f'<p class="condo-icon-empty">{esc(empty_message)}</p>' if empty_message else ""
    cells = "".join(
        f'<li class="condo-icon-item">{icon_markup(item)}<span>{esc(item)}</span></li>'
        for item in items
    )
    return f'<ul class="condo-icon-grid">{cells}</ul>'


def tel_href(phone: object) -> str:
    digits = "".join(ch for ch in str(phone or "") if ch.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    return f"tel:+{digits}" if digits else ""


def contacts_section(b: dict) -> str:
    """Concierge + management contact strip for residents and buyers."""
    concierge = b.get("conciergePhone") or ""
    management_phone = b.get("managementPhone") or ""
    management = b.get("management") or ""
    if not concierge and not management_phone:
        return ""
    rows = []
    if concierge:
        rows.append(
            f'<div class="condo-contact-row">'
            f'<span class="condo-contact-label">Concierge</span>'
            f'<a class="condo-contact-value" href="{esc(tel_href(concierge))}">{esc(concierge)}</a>'
            f"</div>"
        )
    if management_phone or management:
        mgmt_bits = []
        if management:
            mgmt_bits.append(f'<span class="condo-contact-company">{esc(management)}</span>')
        if management_phone:
            mgmt_bits.append(
                f'<a class="condo-contact-value" href="{esc(tel_href(management_phone))}">'
                f"{esc(management_phone)}</a>"
            )
        rows.append(
            f'<div class="condo-contact-row">'
            f'<span class="condo-contact-label">Management</span>'
            f'<div class="condo-contact-mgmt">{"".join(mgmt_bits)}</div>'
            f"</div>"
        )
    return f"""
  <section class="section condo-contact-section">
    <div class="container">
      <div class="condo-contact-band">
        <p class="condo-contact-kicker">Building contacts</p>
        <div class="condo-contact-rows">{"".join(rows)}</div>
        <p class="condo-contact-note">Numbers can change. Confirm with the building or Josh before you rely on them.</p>
      </div>
    </div>
  </section>
"""


def story_section(b: dict) -> str:
    """Richer building narrative: history, topical sections, suite notes."""
    history = (b.get("history") or "").strip()
    sections = b.get("sections") or []
    suite_notes = (b.get("suiteNotes") or "").strip()
    if not history and not sections and not suite_notes:
        return ""
    blocks = []
    if history:
        blocks.append(
            f'<div class="condo-story-block">'
            f"<h2>About {esc(b['name'])}</h2>"
            f"<p>{esc(history)}</p>"
            f"</div>"
        )
    for section in sections:
        title = (section.get("title") or "").strip()
        body = (section.get("body") or "").strip()
        if not title or not body:
            continue
        blocks.append(
            f'<div class="condo-story-block">'
            f"<h3>{esc(title)}</h3>"
            f"<p>{esc(body)}</p>"
            f"</div>"
        )
    if suite_notes:
        blocks.append(
            f'<div class="condo-story-block">'
            f"<h3>Suite features &amp; layouts</h3>"
            f"<p>{esc(suite_notes)}</p>"
            f"</div>"
        )
    return f"""
  <section class="section condo-story-section">
    <div class="container condo-story-grid">
      {"".join(blocks)}
    </div>
  </section>
"""


def school_groups_html(b: dict) -> str:
    ws = b.get("walkScore") or {}
    schools = ws.get("nearbySchools") or {}
    public_schools = schools.get("public") or []
    catholic_schools = schools.get("catholic") or []
    if not public_schools and not catholic_schools:
        return ""
    groups = []
    if public_schools:
        items = "".join(f"<li>{esc(s)}</li>" for s in public_schools)
        groups.append(
            f'<div class="condo-walk-school-group">'
            f'<p class="condo-walk-school-label">Public</p><ul>{items}</ul></div>'
        )
    if catholic_schools:
        items = "".join(f"<li>{esc(s)}</li>" for s in catholic_schools)
        groups.append(
            f'<div class="condo-walk-school-group">'
            f'<p class="condo-walk-school-label">Catholic</p><ul>{items}</ul></div>'
        )
    return f'<div class="condo-walk-school-cols">{"".join(groups)}</div>'


def about_neighbourhood_section(b: dict) -> str:
    """Neighbourhood context with schools + HoodQ guide."""
    nb = b.get("neighbourhood") or {}
    intro = (nb.get("intro") or "").strip()
    highlights = nb.get("highlights") or []
    schools = school_groups_html(b)
    hoodq = b.get("hoodq") or ""
    parks = ""
    ws = b.get("walkScore") or {}
    if ws.get("nearbyParks"):
        parks = f'<p class="condo-neighbourhood-parks">Nearby parks: {esc(ws["nearbyParks"])}.</p>'
    if not intro and not highlights and not schools and not hoodq:
        return ""

    highlight_html = ""
    if highlights:
        bits = []
        for item in highlights:
            title = (item.get("title") or "").strip()
            body = (item.get("body") or "").strip()
            if not title or not body:
                continue
            bits.append(
                f'<div class="condo-neighbourhood-highlight">'
                f"<h3>{esc(title)}</h3>"
                f"<p>{esc(body)}</p>"
                f"</div>"
            )
        if bits:
            highlight_html = f'<div class="condo-neighbourhood-highlights">{"".join(bits)}</div>'

    schools_block = ""
    if schools or hoodq:
        hoodq_html = ""
        if hoodq:
            hoodq_html = (
                f'<p class="condo-neighbourhood-hoodq">'
                f'<a href="{esc(hoodq)}" target="_blank" rel="noopener noreferrer">'
                f"HoodQ Mimico–Humber Bay Shores neighbourhood guide</a>"
                f"<span>Schools, transit, and local context for this pocket.</span>"
                f"</p>"
            )
        schools_title = (
            '<p class="condo-walk-schools-title">Nearby schools</p>' if schools else ""
        )
        schools_block = f"""
        <div class="condo-neighbourhood-schools">
          {schools_title}
          {schools}
          {hoodq_html}
        </div>"""

    intro_html = f"<p class=\"condo-neighbourhood-intro\">{esc(intro)}</p>" if intro else ""
    return f"""
  <section class="section condo-neighbourhood-section">
    <div class="container">
      <h2>About the neighbourhood</h2>
      {intro_html}
      {parks}
      {highlight_html}
      {schools_block}
    </div>
  </section>
"""


def fees_amenities_sections(b: dict) -> str:
    fees = b.get("feesCover") or []
    amenities = b.get("amenities") or []
    fees_html = icon_grid(fees, "Fee inclusions vary. Confirm with the status certificate.")
    amenities_html = icon_grid(amenities, "Ask Josh for the current amenity roster.")
    return f"""
  <section class="section condo-fees-section">
    <div class="container">
      <h2>Maintenance fees cover</h2>
      {fees_html}
    </div>
  </section>

  <section class="section condo-amenities-section">
    <div class="container">
      <h2>Amenities</h2>
      {amenities_html}
    </div>
  </section>
"""


def walkscore_section(b: dict) -> str:
    """Neighbourhood Walk / Transit / Bike scores + commute + map."""
    ws = b.get("walkScore") or {}
    if not ws.get("walk"):
        return ""
    lat = float(ws["lat"])
    lng = float(ws["lng"])
    map_query = quote(f"{lat},{lng}")
    map_src = (
        f"https://www.google.com/maps?q={map_query}&z=15&hl=en&output=embed"
    )
    display_address = ws.get("displayAddress") or b["address"]
    city_line = ws.get("cityLine") or "Toronto, Ontario"
    maps_link = (
        "https://www.google.com/maps/search/?api=1&query="
        f"{quote(f'{display_address}, {city_line}')}"
    )
    commute = ws.get("commute") or {}
    commute_icons = {
        "drive": "directions_car",
        "transit": "directions_subway",
        "bike": "directions_bike",
        "walk": "directions_walk",
    }
    commute_bits = []
    for mode, label in (
        ("drive", "Drive"),
        ("transit", "Transit"),
        ("bike", "Bike"),
        ("walk", "Walk"),
    ):
        if commute.get(mode):
            icon = material_icon(commute_icons[mode], f"condo-commute-icon is-{mode}")
            commute_bits.append(
                f'<li>{icon}<span class="condo-commute-mode">{label}</span>'
                f'<span class="condo-commute-time">{esc(commute[mode])}</span></li>'
            )
    commute_html = ""
    if commute_bits:
        commute_html = f"""
        <div class="condo-commute">
          <p class="condo-commute-label">Commute to {esc(ws.get("commuteTo", "Downtown Toronto"))}</p>
          <ul class="condo-commute-list">{"".join(commute_bits)}</ul>
        </div>"""

    def score_row(kind: str, score, label, desc) -> str:
        return f"""
        <div class="condo-score-row">
          <img
            class="condo-score-badge"
            src="https://pp.walk.sc/badge/{kind}/score/{int(score)}.svg"
            alt="{int(score)} {kind.title()} Score"
            width="72"
            height="72"
            loading="lazy"
          />
          <div class="condo-score-copy">
            <p class="condo-score-label">{esc(label)}</p>
            <p class="condo-score-desc">{esc(desc)}</p>
          </div>
        </div>"""

    scores = "".join(
        [
            score_row("walk", ws["walk"], ws.get("walkLabel", "Walk Score"), ws.get("walkDesc", "")),
            score_row(
                "transit",
                ws["transit"],
                ws.get("transitLabel", "Transit Score"),
                ws.get("transitDesc", ""),
            ),
            score_row("bike", ws["bike"], ws.get("bikeLabel", "Bike Score"), ws.get("bikeDesc", "")),
        ]
    )
    return f"""
  <section class="section condo-walk-section">
    <div class="container">
      <div class="condo-walk-head">
        <h2>Getting around</h2>
        <p>
          <strong>{esc(ws.get("displayAddress", b["address"]))}</strong>
          <span>{esc(ws.get("cityLine", "Toronto, Ontario"))}</span>
        </p>
      </div>
      <div class="condo-walk-grid">
        <div class="condo-walk-scores">
          {commute_html}
          {scores}
          <p class="condo-walk-credit">
            Scores by
            <a href="{esc(ws["url"])}" target="_blank" rel="noopener noreferrer">Walk Score®</a>
          </p>
        </div>
        <div class="condo-walk-map">
          <iframe
            title="Map of {esc(b["name"])}"
            src="{esc(map_src)}"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
          ></iframe>
          <a class="condo-walk-map-link" href="{esc(maps_link)}" target="_blank" rel="noopener noreferrer">Open larger map</a>
        </div>
      </div>
    </div>
  </section>
"""


def related_cards(current_slug: str, depth: int, limit: int = 3) -> str:
    others = [b for b in DATA if b["slug"] != current_slug][:limit]
    cards = []
    for b in others:
        href = asset(f"etobicoke/condo/{b['slug']}/", depth)
        poster = asset(b.get("poster", ""), depth)
        year = b.get("yearBuilt")
        year_html = (
            f'<span class="card-year-chip">Built {esc(year)}</span>' if year else ""
        )
        cards.append(
            f"""
        <a class="card condo-guide-tile" href="{href}">
          <div class="card-media"><img src="{esc(poster)}" alt="" loading="lazy" /></div>
          <div class="card-body">
            <div class="card-chip-row">
              <span class="card-status">{esc(area_chip(b.get('area')))}</span>
              {year_html}
            </div>
            <p class="card-title">{esc(b['name'])}</p>
            <p class="card-meta">{esc(b['address'])}</p>
          </div>
        </a>"""
        )
    return "".join(cards)


def write_index() -> None:
    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    tiles = []
    for b in DATA:
        href = f"../condo/{b['slug']}/"
        poster = asset(b.get("poster", ""), 2)
        year = b.get("yearBuilt") or 0
        year_html = (
            f'<span class="card-year-chip">Built {esc(year)}</span>' if year else ""
        )
        tiles.append(
            f"""
        <a class="card condo-guide-tile" href="{href}" data-name="{esc(b['name'])}" data-year="{esc(year)}">
          <div class="card-media"><img src="{esc(poster)}" alt="{esc(b['name'])}" loading="lazy" /></div>
          <div class="card-body">
            <div class="card-chip-row">
              <span class="card-status">{esc(area_chip(b.get('area')))}</span>
              {year_html}
            </div>
            <p class="card-title">{esc(b['name'])}</p>
            <p class="card-meta">{esc(b['address'])}</p>
          </div>
        </a>"""
        )

    body = f"""
  <section class="hero-band">
    <div class="container">
      <p class="breadcrumb"><a href="../../">Home</a> / <a href="../">Etobicoke</a> / Condo Guide</p>
      <p class="eyebrow">Etobicoke Condo Guide</p>
      <h1>Explore Etobicoke Condos</h1>
      <p class="lead">Building guides for Humber Bay Shores &amp; Mimico.</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="sms:+16473608179?body=Hi%20Josh%2C%20I%27d%20like%20help%20comparing%20Etobicoke%20condos.">Text Josh</a>
        <a class="btn btn-secondary" href="../">Etobicoke listings</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="condo-guide-heading">
        <div>
          <h2>Condo buildings</h2>
          <p class="section-copy">Tap a building for facts, amenities, and who it tends to fit.</p>
        </div>
        <div class="condo-guide-sort" data-condo-sort role="group" aria-label="Sort buildings">
          <span class="condo-guide-sort-label">Sort</span>
          <button type="button" class="condo-guide-sort-btn is-active" data-sort="az" aria-pressed="true">A–Z</button>
          <button type="button" class="condo-guide-sort-btn" data-sort="built" aria-pressed="false">Newest built</button>
        </div>
      </div>
      <div class="grid condo-guide-index" data-condo-guide-grid>
        {"".join(tiles)}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container prose">
      <h2>Buying in South Etobicoke?</h2>
      <p>Comparing fees, views, amenities, and resale patterns building-by-building is the difference between a good condo and the right condo. Josh works with Thapar Team, #1 Team in Etobicoke, and can pull live inventory for any of these addresses.</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="../../#service-buy">Buy with Josh</a>
        <a class="btn btn-secondary" href="../../#service-sell">Sell with Josh</a>
      </div>
    </div>
  </section>
"""
    html = page_shell(
        title="Etobicoke Condo Guide | Josh Schwartz",
        description="Josh’s Etobicoke condo guide: Humber Bay Shores and Mimico buildings with facts, amenities, and amenity tours.",
        canonical=f"{ORIGIN}/etobicoke/south-etobicoke-condo-guide/",
        depth=2,
        body=body,
        json_ld={
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Etobicoke Condo Guide",
            "url": f"{ORIGIN}/etobicoke/south-etobicoke-condo-guide/",
            "about": {"@type": "Place", "name": "South Etobicoke"},
        },
    )
    (GUIDE_DIR / "index.html").write_text(html, encoding="utf-8")


def write_building(b: dict) -> None:
    out = CONDO_DIR / b["slug"]
    out.mkdir(parents=True, exist_ok=True)
    depth = 3
    summary = b.get("summary") or ""
    hero_summary = (
        f'<p class="condo-hero-summary">{esc(summary)}</p>' if summary else ""
    )
    why_items = "".join(
        f'<li class="condo-fit-item">'
        f'{material_icon("check", "condo-fit-icon")}'
        f"<span>{esc(item)}</span></li>"
        for item in b.get("why", [])
    )
    ideal_items = "".join(
        f'<li class="condo-fit-item">'
        f'{material_icon("person", "condo-fit-icon")}'
        f"<span>{esc(item)}</span></li>"
        for item in b.get("idealFor", [])
    )
    media_items = [
        m
        for m in (b.get("media") or [])
        if m.get("url")
        and m.get("title")
        and "humberbayliving" not in str(m.get("url", "")).lower()
        and "humber bay living" not in str(m.get("source", "")).lower()
    ]
    media_html = ""
    if media_items:
        ext = material_icon("open_in_new", "condo-press-ext")
        links = "".join(
            f'<li><a href="{esc(m["url"])}" target="_blank" rel="noopener noreferrer">'
            f'<span class="condo-press-source">{esc(m.get("source", "Article"))}</span>'
            f'<span class="condo-press-title">{esc(m["title"])}</span>'
            f"{ext}"
            f"</a></li>"
            for m in media_items
        )
        media_html = f"""
  <section class="section condo-press-section">
    <div class="container">
      <h2>In the media</h2>
      <ul class="condo-press-list">{links}</ul>
    </div>
  </section>"""

    has_tour = " has-tour" if b.get("video") else ""
    facts = overview_facts(b)
    sms_body = quote(f"Hi Josh, I want to know more about {b['name']} at {b['address']}.")
    sms_href = f"sms:+16473608179?body={sms_body}"
    body = f"""
  <section class="hero-band condo-hero">
    <div class="container">
      <p class="breadcrumb"><a href="../../../">Home</a> / <a href="../../">Etobicoke</a> / <a href="../../south-etobicoke-condo-guide/">Condo Guide</a> / {esc(b["name"])}</p>
      <div class="condo-hero-grid{has_tour}">
          <div class="condo-hero-copy">
            <p class="condo-area-chip-wrap"><span class="condo-area-chip">{esc(area_chip(b.get("area", "Etobicoke")))}</span></p>
            {title_block(b)}
            {location_block(b)}
            {hero_summary}
          </div>
          {media_block(b, depth)}
          {facts}
      </div>
    </div>
  </section>

  {contacts_section(b)}

  {building_photo_block(b, depth)}

  {story_section(b)}

  {fees_amenities_sections(b)}

  {about_neighbourhood_section(b)}

  {walkscore_section(b)}

  <section class="section condo-fit-section">
    <div class="container condo-fit-grid">
      <div>
        <h2>Why consider {esc(b["name"])}</h2>
        <ul class="condo-fit-list">{why_items}</ul>
      </div>
      <div>
        <h2>Who it fits</h2>
        <ul class="condo-fit-list">{ideal_items}</ul>
      </div>
    </div>
  </section>

  {media_html}

  <section class="section condo-action">
    <div class="container condo-action-inner">
      <div class="condo-action-copy">
        <h2>Buying or selling here?</h2>
        <p>Josh can pull live inventory, fee schedules, and recent comps for {esc(b["name"])}.</p>
      </div>
      <div class="cta-row">
        <a class="btn btn-primary" href="{esc(sms_href)}">Text Josh for more</a>
        <a class="btn btn-secondary" href="../../south-etobicoke-condo-guide/">All condo guides</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <h2>See more condo guides</h2>
      <div class="grid">{related_cards(b["slug"], depth)}</div>
    </div>
  </section>
"""
    poster = (b.get("poster") or "").strip()
    og_image = f"{ORIGIN}/{poster}" if poster else None
    json_ld = {
            "@context": "https://schema.org",
            "@type": "Residence",
            "name": b["name"],
            "url": f"{ORIGIN}/etobicoke/condo/{b['slug']}/",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": b["address"],
                "addressLocality": "Toronto",
                "addressRegion": "ON",
                "addressCountry": "CA",
            },
        }
    if og_image:
        json_ld["image"] = og_image
    html = page_shell(
        title=f"{b['name']} | Etobicoke Condo Guide | Josh Schwartz",
        description=f"{b['name']} at {b['address']} in {b.get('area', 'Etobicoke')}: history, amenities, and local guidance from Josh Schwartz.",
        canonical=f"{ORIGIN}/etobicoke/condo/{b['slug']}/",
        depth=depth,
        body=body,
        json_ld=json_ld,
        og_image=og_image,
    )
    (out / "index.html").write_text(html, encoding="utf-8")


def update_sitemap() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    urls = [
        f"{ORIGIN}/etobicoke/south-etobicoke-condo-guide/",
        *[f"{ORIGIN}/etobicoke/condo/{b['slug']}/" for b in DATA],
    ]
    for url in urls:
        entry = (
            f"  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{LASTMOD}</lastmod>\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>0.8</priority>\n"
            f"  </url>\n"
        )
        if f"<loc>{url}</loc>" not in text:
            text = text.replace("</urlset>", entry + "</urlset>")
    sitemap.write_text(text, encoding="utf-8")


def main() -> None:
    write_index()
    for building in DATA:
        write_building(building)
    update_sitemap()
    print(f"Generated guide + {len(DATA)} condo pages")


if __name__ == "__main__":
    main()
