"""Rules for rejecting listings that aren't a plain NEW unit from a real retailer."""
from __future__ import annotations

import re
from urllib.parse import urlparse

BLOCKED_DOMAINS = {
    "ebay.co.uk", "ebay.com", "amazon.co.uk/gp/offer-listing",  # marketplace resellers
    "onbuy.com", "fruugo.co.uk", "gumtree.com", "facebook.com", "preloved.co.uk",
    "backmarket.co.uk", "musicmagpie.co.uk", "cex.co.uk",
}

# Words in a title/URL that mean "not a brand-new, sealed unit".
NOT_NEW = re.compile(
    r"\b(used|refurb(ished)?|renewed|pre[- ]?owned|second[- ]?hand|graded|grade [a-d]|"
    r"b[- ]?grade|ex[- ]?display|open[- ]?box|returned|clearance outlet|scratch(ed)? (and|&) dent|"
    r"cosmetic(ally)? (damaged|imperfect)|seconds)\b",
    re.I,
)

# Known outlet-only storefronts that sell graded stock under the same model number.
OUTLET_DOMAINS = {"awoutlet.co.uk", "ao.com/outlet", "currys.co.uk/clearance"}


def domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def rejection_reason(url: str, title: str = "", condition: str | None = None,
                     extra_blocked: set[str] | None = None) -> str | None:
    d = domain(url)
    blocked = BLOCKED_DOMAINS | (extra_blocked or set())
    for b in blocked:
        if d == b or d.endswith("." + b) or (("/" in b) and b in (d + urlparse(url).path)):
            return f"blocked domain ({b})"
    for o in OUTLET_DOMAINS:
        if o in d + urlparse(url).path:
            return f"outlet/graded storefront ({o})"
    if condition and condition not in ("NewCondition", "New", "new"):
        return f"condition={condition}"
    m = NOT_NEW.search(f"{title} {urlparse(url).path.replace('-', ' ')}")
    if m:
        return f"not-new keyword '{m.group(0)}'"
    return None
