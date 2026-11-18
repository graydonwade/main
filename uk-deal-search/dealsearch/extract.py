"""Extract price / availability / condition from a product page.

Strategy (most to least reliable):
1. schema.org Product in JSON-LD  (used by nearly every UK appliance retailer)
2. schema.org microdata / OpenGraph product meta tags
3. Retailer-specific CSS selector from retailers.yaml (last resort)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup


@dataclass
class Offer:
    price: Decimal | None = None
    currency: str | None = None
    availability: str | None = None   # e.g. InStock / OutOfStock / PreOrder
    condition: str | None = None      # NewCondition / UsedCondition / RefurbishedCondition
    name: str | None = None
    sku: str | None = None
    mpn: str | None = None
    seller: str | None = None
    source: str = ""                  # which extractor found it
    raw: dict = field(default_factory=dict, repr=False)


def _to_decimal(v) -> Decimal | None:
    if v is None:
        return None
    s = re.sub(r"[^\d.]", "", str(v).replace(",", ""))
    try:
        return Decimal(s) if s else None
    except InvalidOperation:
        return None


def _short(schema_url: str | None) -> str | None:
    if not schema_url:
        return None
    return str(schema_url).rstrip("/").rsplit("/", 1)[-1]


def _iter_jsonld(obj):
    if isinstance(obj, list):
        for o in obj:
            yield from _iter_jsonld(o)
    elif isinstance(obj, dict):
        yield obj
        for key in ("@graph", "mainEntity", "itemListElement", "item"):
            if key in obj:
                yield from _iter_jsonld(obj[key])


def _is_type(node: dict, t: str) -> bool:
    nt = node.get("@type")
    return t in (nt if isinstance(nt, list) else [nt])


def _offers_from_product(p: dict) -> list[Offer]:
    offers = p.get("offers") or []
    if isinstance(offers, dict):
        offers = [offers]
    out = []
    for o in offers:
        if _is_type(o, "AggregateOffer"):
            price = o.get("lowPrice") or o.get("price")
        else:
            price = o.get("price")
            if price is None and isinstance(o.get("priceSpecification"), dict):
                price = o["priceSpecification"].get("price")
        seller = o.get("seller")
        out.append(Offer(
            price=_to_decimal(price),
            currency=o.get("priceCurrency"),
            availability=_short(o.get("availability")),
            condition=_short(o.get("itemCondition") or p.get("itemCondition")),
            name=p.get("name"),
            sku=p.get("sku"),
            mpn=p.get("mpn") or (p.get("model") if isinstance(p.get("model"), str) else None),
            seller=seller.get("name") if isinstance(seller, dict) else seller,
            source="json-ld",
            raw=o,
        ))
    return out


def from_jsonld(soup: BeautifulSoup) -> list[Offer]:
    found: list[Offer] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or tag.get_text() or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for node in _iter_jsonld(data):
            if _is_type(node, "Product") or _is_type(node, "ProductGroup"):
                found.extend(_offers_from_product(node))
    return [o for o in found if o.price is not None]


def from_meta(soup: BeautifulSoup) -> list[Offer]:
    def meta(*names):
        for n in names:
            t = soup.find("meta", attrs={"property": n}) or soup.find("meta", attrs={"itemprop": n}) \
                or soup.find("meta", attrs={"name": n})
            if t and t.get("content"):
                return t["content"]
        return None

    price = meta("product:price:amount", "og:price:amount", "price")
    if not price:
        el = soup.find(attrs={"itemprop": "price"})
        price = el.get("content") or el.get_text() if el else None
    if not price:
        return []
    return [Offer(
        price=_to_decimal(price),
        currency=meta("product:price:currency", "og:price:currency", "priceCurrency"),
        availability=_short(meta("product:availability", "og:availability", "availability")),
        condition=_short(meta("product:condition", "itemCondition")),
        name=meta("og:title"),
        source="meta",
    )]


def from_selector(soup: BeautifulSoup, selector: str) -> list[Offer]:
    el = soup.select_one(selector)
    if not el:
        return []
    return [Offer(price=_to_decimal(el.get("content") or el.get_text()), currency="GBP", source="css")]


def extract_offers(html: str, selector: str | None = None) -> list[Offer]:
    soup = BeautifulSoup(html, "lxml")
    for fn in (from_jsonld, from_meta):
        offers = fn(soup)
        if offers:
            return offers
    return from_selector(soup, selector) if selector else []
