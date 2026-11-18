"""Coupon / cashback stacking.

Codes can't be tested at checkout headlessly without an account+basket on most
sites, so each coupon carries a `status`:
  verified    - confirmed applied at checkout by a human
  likely      - official retailer/brand promo or recent hotukdeals confirmation
  unverified  - from a coupon aggregator; may be expired or exclude LG/laundry
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

import yaml


@dataclass
class Coupon:
    retailer: str            # retailer name or "*" for any
    code: str | None         # None for automatic promos / cashback
    kind: str                # percent | fixed | cashback_percent | cashback_fixed
    value: Decimal
    min_spend: Decimal = Decimal(0)
    cap: Decimal | None = None
    status: str = "unverified"
    applies_to: str = ""     # free text: brands/categories
    excludes: str = ""
    source: str = ""
    note: str = ""

    def saving(self, price: Decimal) -> Decimal:
        if price < self.min_spend:
            return Decimal(0)
        if self.kind in ("percent", "cashback_percent"):
            s = price * self.value / 100
        else:
            s = self.value
        if self.cap is not None:
            s = min(s, self.cap)
        return s.quantize(Decimal("0.01"), ROUND_HALF_UP)

    @property
    def is_cashback(self) -> bool:
        return self.kind.startswith("cashback")


def load(path: str) -> list[Coupon]:
    with open(path) as f:
        rows = yaml.safe_load(f).get("coupons", [])
    out = []
    for r in rows:
        for k in ("value", "min_spend", "cap"):
            if r.get(k) is not None:
                r[k] = Decimal(str(r[k]))
        out.append(Coupon(**r))
    return out


def best_stack(retailer: str, price: Decimal, coupons: list[Coupon],
               include_unverified: bool = False) -> tuple[Decimal, list[Coupon]]:
    """Best checkout code (only one code usually allowed) + best cashback, which
    normally stack. Returns (effective price, coupons used)."""
    ok = {"verified", "likely"} | ({"unverified"} if include_unverified else set())
    mine = [c for c in coupons if c.retailer in (retailer, "*") and c.status in ok]
    codes = [c for c in mine if not c.is_cashback]
    cash = [c for c in mine if c.is_cashback]
    used = []
    eff = price
    if codes:
        best = max(codes, key=lambda c: c.saving(price))
        if best.saving(price) > 0:
            eff -= best.saving(price)
            used.append(best)
    if cash:
        best = max(cash, key=lambda c: c.saving(eff))
        if best.saving(eff) > 0:
            eff -= best.saving(eff)
            used.append(best)
    return eff, used
