#!/usr/bin/env python3
"""Single shared site footer used by every generated page and mirrored on the homepage."""

from __future__ import annotations

import re
from pathlib import Path


def render_site_footer(*, root_href: str = "", note_extra: str = "") -> str:
    """Return the canonical footer markup.

    root_href: path prefix back to the site root ('' on homepage, '../' on city pages,
    '../../' on nested listing/condo pages).
    note_extra: optional sentence appended after the TRESA line (e.g. condo disclaimer).
    """
    _ = root_href  # reserved for future root-relative footer links
    note = "Advertising follows Ontario RECO rules under TRESA."
    if note_extra:
        note = f"{note} {note_extra.strip()}"

    return f"""  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-meta">
        <div>© <span id="year">2026</span> Josh Schwartz</div>
        <div>Sales Representative · Snobar Realty Group Inc., Brokerage</div>
      </div>
      <p class="footer-note">
        {note}
      </p>
    </div>
  </footer>"""


def site_footer_script_tag(*, root_href: str = "") -> str:
    """Script tag that fills the copyright year on every page."""
    root = root_href or ""
    if root in {"", "."}:
        src = "assets/site-footer.js?v=20261014footer"
    else:
        if not root.endswith("/"):
            root = f"{root}/"
        src = f"{root}assets/site-footer.js?v=20261014footer"
    return f'  <script src="{src}" defer></script>'


def sync_homepage_footer(index_path: Path) -> bool:
    """Replace the homepage <footer class="site-footer">…</footer> with the shared markup."""
    html = index_path.read_text(encoding="utf-8")
    footer = render_site_footer(root_href="").strip()
    new_html, count = re.subn(
        r'<footer class="site-footer">.*?</footer>',
        footer,
        html,
        count=1,
        flags=re.S,
    )
    if count != 1:
        return False
    if new_html != html:
        index_path.write_text(new_html, encoding="utf-8")
    return True
