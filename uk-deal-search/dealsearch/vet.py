"""Retailer legitimacy vetting — run before trusting any price.

Automated signals (each is cheap and catches the usual clone-store pattern of a
months-old domain, no company details, and prices far below market):

  * domain age           RDAP (Nominet for .uk, rdap.org otherwise)
  * company details      company number / VAT number / UK postcode on the site's own pages
  * Companies House      status, age, overdue accounts, insolvency history
                         (needs a free API key in $CH_API_KEY:
                          https://developer.company-information.service.gov.uk/)
  * Trustpilot           AggregateRating from trustpilot.com/review/<domain>
  * price outlier        listing >20% below the median of other vetted listings (in report)

Human-researched verdicts live in retailers.yaml under `trust:` and always win;
the automated score is for retailers nobody has vetted yet.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

from .fetch import HEADERS, FetchError, fetch

VERDICTS = ("LEGIT", "LEGIT-WITH-CAVEATS", "UNVERIFIED", "AVOID")

COMPANY_NO = re.compile(r"compan(?:y|ies)\s*(?:registration\s*)?(?:no\.?|number|reg\.?)\s*[:.]?\s*((?:SC|NI|OC)?\d{6,8})", re.I)
VAT_NO = re.compile(r"\bGB\s?\d{3}\s?\d{4}\s?\d{2}\b")
UK_POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b")
INFO_PATHS = ("", "/about-us", "/about", "/terms-and-conditions", "/terms", "/contact-us", "/contact")


@dataclass
class Vetting:
    domain: str
    domain_registered: str | None = None
    company_number: str | None = None
    vat_number: str | None = None
    has_uk_address: bool = False
    ch_status: str | None = None
    ch_incorporated: str | None = None
    ch_flags: list[str] = field(default_factory=list)
    trustpilot_score: float | None = None
    trustpilot_reviews: int | None = None
    red_flags: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    verdict: str = "UNVERIFIED"


def _years_since(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        d = dt.date.fromisoformat(iso[:10])
    except ValueError:
        return None
    return (dt.date.today() - d).days / 365.25


def domain_registered(domain: str) -> str | None:
    url = (f"https://rdap.nominet.uk/uk/domain/{domain}" if domain.endswith(".uk")
           else f"https://rdap.org/domain/{domain}")
    r = requests.get(url, headers={"Accept": "application/rdap+json"}, timeout=15)
    r.raise_for_status()
    for ev in r.json().get("events", []):
        if ev.get("eventAction") == "registration":
            return ev.get("eventDate", "")[:10]
    return None


def scan_site(domain: str, v: Vetting) -> None:
    text = ""
    for path in INFO_PATHS:
        try:
            html = fetch(f"https://{domain}{path}", use_browser="never")
        except FetchError:
            continue
        text += " " + BeautifulSoup(html, "lxml").get_text(" ")
        if COMPANY_NO.search(text) and VAT_NO.search(text):
            break
    if not text:
        v.errors.append("site unreachable")
        return
    if m := COMPANY_NO.search(text):
        v.company_number = m.group(1).upper().zfill(8)
    if m := VAT_NO.search(text):
        v.vat_number = m.group(0).replace(" ", "")
    v.has_uk_address = bool(UK_POSTCODE.search(text))


def companies_house(v: Vetting) -> None:
    key = os.environ.get("CH_API_KEY")
    if not key or not v.company_number:
        return
    r = requests.get(f"https://api.company-information.service.gov.uk/company/{v.company_number}",
                     auth=(key, ""), timeout=15)
    if r.status_code == 404:
        v.ch_flags.append("company number not found at Companies House")
        return
    r.raise_for_status()
    c = r.json()
    v.ch_status = c.get("company_status")
    v.ch_incorporated = c.get("date_of_creation")
    if c.get("accounts", {}).get("overdue"):
        v.ch_flags.append("accounts overdue")
    if c.get("has_insolvency_history"):
        v.ch_flags.append("insolvency history")
    if c.get("company_status") != "active":
        v.ch_flags.append(f"status={c.get('company_status')}")


def trustpilot(v: Vetting) -> None:
    html = fetch(f"https://uk.trustpilot.com/review/{v.domain}", use_browser="never")
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for node in data.get("@graph", [data]) if isinstance(data, dict) else data:
            ar = node.get("aggregateRating") if isinstance(node, dict) else None
            if ar:
                v.trustpilot_score = float(ar.get("ratingValue"))
                v.trustpilot_reviews = int(ar.get("reviewCount"))
                return


def score(v: Vetting) -> str:
    age = _years_since(v.domain_registered)
    if age is not None and age < 1:
        v.red_flags.append(f"domain only {age:.1f} years old")
    if not v.company_number and "site unreachable" not in v.errors:
        v.red_flags.append("no company number on site (UK law requires it for Ltd companies)")
    if v.company_number and not v.vat_number:
        v.red_flags.append("no VAT number on site")
    v.red_flags += v.ch_flags
    ch_age = _years_since(v.ch_incorporated)
    if ch_age is not None and ch_age < 1:
        v.red_flags.append(f"company incorporated {ch_age:.1f} years ago")
    if v.trustpilot_score is not None and v.trustpilot_score < 3:
        v.red_flags.append(f"Trustpilot {v.trustpilot_score}")

    hard = [f for f in v.red_flags if f.startswith(("domain only", "no company number", "company number not found",
                                                   "status=", "insolvency"))]
    if len(hard) >= 2:
        return "AVOID"
    established = (age or 0) >= 3 and v.company_number and (v.trustpilot_reviews or 0) >= 100
    if established and not v.red_flags:
        return "LEGIT"
    if established or (v.company_number and not hard):
        return "LEGIT-WITH-CAVEATS"
    return "UNVERIFIED"


def vet(domain: str) -> Vetting:
    v = Vetting(domain=domain)
    for name, fn in (("rdap", lambda: setattr(v, "domain_registered", domain_registered(domain))),
                     ("site", lambda: scan_site(domain, v)),
                     ("companies-house", lambda: companies_house(v)),
                     ("trustpilot", lambda: trustpilot(v))):
        try:
            fn()
        except Exception as e:  # noqa: BLE001 - every check is best-effort
            v.errors.append(f"{name}: {str(e)[:120]}")
    v.verdict = score(v)
    return v
