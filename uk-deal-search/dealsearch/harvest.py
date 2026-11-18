"""Collect candidate coupon codes that are actually published somewhere.

Sources: the retailer's own pages (many show 'Save £50 with voucher code: SALE50'),
coupon/deal sites that print codes in the page, and a short list of common
seasonal codes. No random generation.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .fetch import FetchError, fetch_http

CODE_CONTEXT = re.compile(
    r"(?:voucher|promo|discount|coupon)?\s*code\s*[:\-–]?\s*['\"“]?([A-Z][A-Z0-9]{3,19})\b"
    r"|(?:use|enter|apply|with)\s+(?:the\s+)?(?:code\s+)?['\"“]([A-Z][A-Z0-9]{3,19})['\"”]", re.I)
STOP = {"CODE", "CODES", "HERE", "BELOW", "ABOVE", "TERMS", "APPLY", "COPY", "CHECKOUT", "BASKET", "VALID",
        "WHEN", "THIS", "THAT", "YOUR", "WITH", "FROM", "OFFER", "DETAILS", "REVEAL", "NONE", "REQUIRED",
        "NEEDED", "SHOW", "COPIED", "UNLOCK", "POSTCODE", "VOUCHER", "DISCOUNT", "PROMO", "COUPON", "BEFORE"}

SEASONAL = ["BLACKFRIDAY", "BLACKFRIDAY10", "BF10", "BF2026", "BLACKFRIDAY2026", "CYBER", "CYBERMONDAY",
            "WELCOME10", "WELCOME5", "NEWSLETTER", "NEWSLETTER10", "SAVE10", "SAVE5", "EXTRA10", "EXTRA20",
            "XMAS20", "XMAS10", "CHRISTMAS", "NHS", "NHS10", "BLUELIGHT", "STUDENT", "LG10", "LAUNDRY"]

DEAL_SITES = [
    "https://www.hotukdeals.com/vouchers/{domain}",
    "https://www.vouchercodes.co.uk/{domain}",
]


def _text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["style", "noscript"]):
        t.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" "))


def codes_in(text: str) -> set[str]:
    out = set()
    for m in CODE_CONTEXT.finditer(text):
        if m.group(2):                       # quoted after use/enter/apply: trust it
            out.add(m.group(2).upper())
        elif m.group(1) and any(ch.isdigit() for ch in m.group(1)) and m.group(1)[0].isupper():
            out.add(m.group(1).upper())      # bare "code: X" must look like a code (has a digit)
    return {c for c in out if c not in STOP}


PREFILLED = re.compile(r'<input[^>]*(?:voucher|coupon|promo)[^>]*value="([A-Z0-9]{4,20})"', re.I)


def prefilled(html: str) -> set[str]:
    """Codes a shop pre-fills in a voucher box on the product page (e.g. Sonic Direct)."""
    return {c.upper() for c in PREFILLED.findall(html) if any(ch.isdigit() for ch in c)}


def family(codes: set[str], amounts=(10, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250)) -> set[str]:
    """If a retailer publishes PREFIX<amount> codes (SALE30, SALE50...), the same prefix with the
    other common amounts is worth one try each."""
    prefixes = {m.group(1) for c in codes if (m := re.fullmatch(r"([A-Z]{3,10})(\d{1,3})", c))}
    return {f"{p}{a}" for p in prefixes for a in amounts} - set(codes)


def harvest(domain: str, extra_urls: list[str] = (), seasonal: bool = True, log=print) -> dict[str, str]:
    """Return {code: where it was seen}."""
    found: dict[str, str] = {}
    urls = [f"https://{domain}/", f"https://www.{domain}/"] + list(extra_urls)
    urls += [t.format(domain=domain) for t in DEAL_SITES]
    for u in dict.fromkeys(urls):
        try:
            html = fetch_http(u, retries=0)
        except FetchError:
            continue
        for c in codes_in(_text(html)) | prefilled(html):
            found.setdefault(c, urlparse(u).netloc)
    n_seen = len(found)
    for c in family(set(found)):
        found.setdefault(c, "same family as a published code")
    if seasonal:
        for c in SEASONAL:
            found.setdefault(c, "seasonal guess list")
    log(f"  harvested {n_seen} published codes for {domain} (+{len(found) - n_seen} seasonal)")
    return found
