from decimal import Decimal

from dealsearch.coupons import Coupon, best_stack
from dealsearch.extract import extract_offers
from dealsearch.filters import rejection_reason

JSONLD = """<html><head><script type="application/ld+json">
{"@context":"https://schema.org","@graph":[{"@type":"Product","name":"LG WT1210WWF WashTower",
"mpn":"WT1210WWF","offers":{"@type":"Offer","price":"1,499.00","priceCurrency":"GBP",
"availability":"https://schema.org/InStock","itemCondition":"https://schema.org/NewCondition"}}]}
</script></head><body></body></html>"""


def test_jsonld_extraction():
    (o,) = extract_offers(JSONLD)
    assert o.price == Decimal("1499.00")
    assert o.availability == "InStock" and o.condition == "NewCondition"
    assert o.mpn == "WT1210WWF"


def test_meta_fallback():
    html = '<meta property="product:price:amount" content="1599"><meta property="product:price:currency" content="GBP">'
    (o,) = extract_offers(html)
    assert o.price == Decimal("1599") and o.source == "meta"


def test_filters():
    assert rejection_reason("https://www.ebay.co.uk/itm/1")
    assert rejection_reason("https://awoutlet.co.uk/lg-wt1210bbtn1-black-3654.html")
    assert rejection_reason("https://x.co.uk/p", "LG WashTower - Graded B")
    assert rejection_reason("https://x.co.uk/p", "", "RefurbishedCondition")
    assert rejection_reason("https://ao.com/product/wt1210wwf") is None


def test_best_stack_one_code_plus_cashback():
    cs = [
        Coupon("AC", "SALE50", "fixed", Decimal(50), status="likely"),
        Coupon("AC", "PCT5", "percent", Decimal(5), cap=Decimal(40), status="likely"),
        Coupon("AC", None, "cashback_percent", Decimal(2), status="likely"),
        Coupon("AC", "JUNK", "fixed", Decimal(500), status="unverified"),
    ]
    eff, used = best_stack("AC", Decimal(1500), cs)
    assert [c.code for c in used] == ["SALE50", None]
    assert eff == Decimal(1450) - Decimal("29.00")
