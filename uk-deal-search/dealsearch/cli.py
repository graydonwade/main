"""dealsearch CLI.

  dealsearch check  projects/<p>/products.yaml          # scrape every known product URL
  dealsearch report projects/<p>/products.yaml --coupons projects/<p>/coupons.yaml
  dealsearch search WT1210WWF                          # print retailer search URLs to discover listings

`check` writes observed prices back into the products file (observed: block) so
`report` can rank them with the best coupon/cashback stack applied.
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging
import sys
from decimal import Decimal
from importlib import resources
from urllib.parse import quote_plus

import yaml

from . import coupons as cp
from .extract import extract_offers
from .fetch import FetchError, fetch
from .filters import domain, rejection_reason


def _retailers() -> dict:
    return yaml.safe_load(resources.files("dealsearch").joinpath("retailers.yaml").read_text())


def cmd_search(args) -> int:
    cfg = _retailers()
    for r in cfg["retailers"] + cfg["aggregators"]:
        print(f"{r['name']:<20} {r['search'].format(q=quote_plus(args.query))}")
    return 0


def cmd_check(args) -> int:
    cfg = _retailers()
    suspect = set(cfg.get("suspect_domains", []))
    browser_domains = {r["domain"] for r in cfg["retailers"] if r.get("browser")}
    with open(args.products) as f:
        data = yaml.safe_load(f)
    today = dt.date.today().isoformat()
    for prod in data["products"]:
        for lst in prod.get("listings", []):
            url = lst["url"]
            why = rejection_reason(url, lst.get("title", ""), extra_blocked=suspect)
            if why:
                lst["observed"] = {"date": today, "rejected": why}
                print(f"SKIP {prod['model']} {domain(url)}: {why}")
                continue
            mode = "always" if domain(url) in browser_domains else args.browser
            try:
                offers = extract_offers(fetch(url, use_browser=mode), lst.get("selector"))
            except FetchError as e:
                lst["observed"] = {"date": today, "error": str(e)[:200]}
                print(f"FAIL {prod['model']} {domain(url)}: {e}")
                continue
            new = [o for o in offers if not rejection_reason(url, o.name or "", o.condition)]
            if not new:
                lst["observed"] = {"date": today, "error": "no new-condition price found"}
                print(f"NONE {prod['model']} {domain(url)}")
                continue
            o = min(new, key=lambda o: o.price)
            lst["observed"] = {"date": today, "price": float(o.price),
                               "availability": o.availability, "via": o.source}
            print(f"OK   {prod['model']} {domain(url)}: £{o.price} {o.availability or ''}")
    with open(args.products, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    return 0


def _price(lst: dict) -> Decimal | None:
    obs = lst.get("observed") or {}
    p = obs.get("price", lst.get("price"))
    return Decimal(str(p)) if p is not None else None


def cmd_report(args) -> int:
    with open(args.products) as f:
        data = yaml.safe_load(f)
    coupons = cp.load(args.coupons) if args.coupons else []
    for prod in data["products"]:
        rows = []
        for lst in prod.get("listings", []):
            if lst.get("exclude"):
                continue
            price = _price(lst)
            if price is None:
                continue
            total = price + Decimal(str(lst.get("delivery", 0) or 0))
            eff, used = cp.best_stack(lst["retailer"], total, coupons, args.include_unverified)
            rows.append((eff, total, lst, used))
        rows.sort(key=lambda r: r[0])
        print(f"\n## {prod['model']} — {prod.get('name', '')}\n")
        print("| Retailer | Listed + delivery | After codes/cashback | Applied | Price source |")
        print("|---|---|---|---|---|")
        for eff, total, lst, used in rows:
            applied = "; ".join(f"{c.code or c.kind} ({c.status})" for c in used) or "—"
            src = lst.get("price_source", "observed" if lst.get("observed") else "manual")
            print(f"| [{lst['retailer']}]({lst['url']}) | £{total:,.2f} | £{eff:,.2f} | {applied} | {src} |")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="dealsearch")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.set_defaults(fn=cmd_search)
    c = sub.add_parser("check"); c.add_argument("products")
    c.add_argument("--browser", choices=["never", "auto", "always"], default="auto")
    c.set_defaults(fn=cmd_check)
    r = sub.add_parser("report"); r.add_argument("products"); r.add_argument("--coupons")
    r.add_argument("--include-unverified", action="store_true",
                   help="also apply aggregator codes nobody has confirmed")
    r.set_defaults(fn=cmd_report)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
