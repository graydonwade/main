"""Batch-test coupon codes against a real basket, like a browser coupon extension does.

Adapters talk to the shop platform's own basket API (fast, exact totals):
  woocommerce  - Store API  /wp-json/wc/store/v1/cart/...
  magento2     - REST guest carts  /rest/V1/guest-carts/...
The basket is anonymous and abandoned afterwards: nothing is ordered or paid.

Only codes from a candidate list are tried (public codes, retailer promo patterns), with a
delay between attempts. This is not a random code generator.
"""
from __future__ import annotations

import json
import os
import random
import re
import time
from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urlparse

from .fetch import HEADERS, proxy


@dataclass
class CodeResult:
    code: str
    ok: bool
    discount: Decimal = Decimal(0)
    total: Decimal | None = None
    message: str = ""


def _session():
    try:
        from curl_cffi import requests as cr
        s = cr.Session(impersonate="chrome")
    except ImportError:
        import requests
        s = requests.Session()
        s.headers.update(HEADERS)
    if proxy():
        s.proxies = {"http": proxy(), "https": proxy()}
    return s


def _pause():
    lo, hi = (float(x) for x in os.environ.get("DEALSEARCH_COUPON_DELAY", "2,4").split(","))
    time.sleep(random.uniform(lo, hi))


class WooCommerce:
    def __init__(self, product_url: str):
        u = urlparse(product_url)
        self.base = f"{u.scheme}://{u.netloc}/wp-json/wc/store/v1"
        self.product_url = product_url
        self.s = _session()
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def _req(self, method, path, body=None):
        r = self.s.request(method, self.base + path, headers=self.headers,
                           data=json.dumps(body) if body is not None else None, timeout=30)
        for h in ("Nonce", "X-WC-Store-API-Nonce"):
            if r.headers.get(h):
                self.headers["Nonce"] = r.headers[h]
        if r.headers.get("Cart-Token"):
            self.headers["Cart-Token"] = r.headers["Cart-Token"]
        return r

    def _product_id(self) -> int:
        html = self.s.get(self.product_url, timeout=30).text
        for pat in (r'name="add-to-cart"\s+value="(\d+)"', r'data-product_id="(\d+)"',
                    r'"product_id"\s*:\s*"?(\d+)', r'postid-(\d+)'):
            if m := re.search(pat, html):
                return int(m.group(1))
        raise RuntimeError("could not find WooCommerce product id on page")

    @staticmethod
    def _money(totals: dict, key: str) -> Decimal:
        minor = int(totals.get("currency_minor_unit", 2))
        return Decimal(totals.get(key, "0")) / (10 ** minor)

    def setup(self) -> Decimal:
        self._req("GET", "/cart")
        pid = self._product_id()
        r = self._req("POST", "/cart/add-item", {"id": pid, "quantity": 1})
        if r.status_code >= 400:
            raise RuntimeError(f"add-item failed: {r.status_code} {r.text[:150]}")
        return self._money(r.json()["totals"], "total_price")

    def try_code(self, code: str) -> CodeResult:
        r = self._req("POST", "/cart/apply-coupon", {"code": code})
        if r.status_code >= 400:
            msg = re.sub("<[^>]+>", "", r.json().get("message", r.text[:120]))
            return CodeResult(code, False, message=msg)
        t = r.json()["totals"]
        res = CodeResult(code, True, self._money(t, "total_discount") + self._money(t, "total_discount_tax"),
                         self._money(t, "total_price"))
        self._req("POST", "/cart/remove-coupon", {"code": code})
        return res


class Magento2:
    def __init__(self, product_url: str, sku: str | None = None):
        u = urlparse(product_url)
        self.base = f"{u.scheme}://{u.netloc}/rest/V1/guest-carts"
        self.product_url = product_url
        self.sku = sku
        self.s = _session()
        self.cart = None

    def _sku(self) -> str:
        html = self.s.get(self.product_url, timeout=30).text
        from .extract import extract_offers
        for o in extract_offers(html):
            for part in (o.sku or "").split(","):
                if part.strip() and "TRUSTPILOT" not in part.upper():
                    return part.strip()
        for pat in (r'"sku"\s*:\s*"([^"]+)"', r'itemprop="sku"[^>]*content="([^"]+)"',
                    r'data-product-sku="([^"]+)"', r'"product_sku"\s*:\s*"([^"]+)"'):
            if m := re.search(pat, html):
                return m.group(1)
        raise RuntimeError("could not find Magento SKU on page")

    def _req(self, method, path="", body=None):
        return self.s.request(method, self.base + path, timeout=30,
                              headers={"Content-Type": "application/json", "Accept": "application/json"},
                              data=json.dumps(body) if body is not None else None)

    def _totals(self) -> dict:
        return self._req("GET", f"/{self.cart}/totals").json()

    def setup(self) -> Decimal:
        self.cart = self._req("POST").json()
        sku = self.sku or self._sku()
        r = self._req("POST", f"/{self.cart}/items", {"cartItem": {"sku": sku, "qty": 1, "quote_id": self.cart}})
        if r.status_code >= 400:
            raise RuntimeError(f"add item (sku {sku}) failed: {r.status_code} {r.text[:150]}")
        return Decimal(str(self._totals().get("grand_total", 0)))

    def try_code(self, code: str) -> CodeResult:
        r = self._req("PUT", f"/{self.cart}/coupons/{code}")
        if r.status_code >= 400:
            try:
                msg = r.json().get("message", "")
                for i, p in enumerate(r.json().get("parameters", []) or []):
                    msg = msg.replace(f"%{i + 1}", str(p))
            except ValueError:
                msg = r.text[:120]
            return CodeResult(code, False, message=msg)
        t = self._totals()
        res = CodeResult(code, True, abs(Decimal(str(t.get("discount_amount", 0)))),
                         Decimal(str(t.get("grand_total", 0))))
        self._req("DELETE", f"/{self.cart}/coupons")
        return res


class Magento2Form:
    """Magento 2 via the storefront forms (for shops that block the REST API, e.g. Webbs)."""

    def __init__(self, product_url: str, sku: str | None = None):
        u = urlparse(product_url)
        self.root = f"{u.scheme}://{u.netloc}"
        self.product_url = product_url
        self.s = _session()

    def _form_key(self, html: str) -> str:
        m = re.search(r'name="form_key"[^>]*value="([^"]+)"', html) or re.search(r'"formKey"\s*:\s*"([^"]+)"', html)
        fk = m.group(1) if m else None
        return fk or self.s.cookies.get("form_key") or ""

    def _cart_state(self) -> tuple[Decimal, Decimal, str]:
        html = self.s.get(f"{self.root}/checkout/cart/", timeout=30).text
        j = self.s.get(f"{self.root}/customer/section/load/?sections=cart,messages&force_new_section_timestamp=true",
                       timeout=30, headers={"X-Requested-With": "XMLHttpRequest"})
        msgs = ""
        try:
            data = j.json()
            msgs = " ".join(re.sub("<[^>]+>", "", m.get("text", "")) for m in data.get("messages", {}).get("messages", []))
        except ValueError:
            pass
        if not msgs:
            msgs = " ".join(re.sub(r"\s+", " ", re.sub("<[^>]+>", "", m)) for m in
                            re.findall(r'<div[^>]*message-(?:error|success|notice)[^>]*>(.*?)</div>', html, re.S))
        grand = re.search(r'"grand_total"\s*:\s*"?([\d.]+)', html)
        sub = re.search(r'"subtotal"\s*:\s*"?([\d.]+)', html)
        disc = re.search(r'"discount_amount"\s*:\s*"?(-?[\d.]+)', html)
        total = Decimal(grand.group(1) if grand else (sub.group(1) if sub else "0"))
        return total, abs(Decimal(disc.group(1))) if disc else Decimal(0), msgs.strip()

    def setup(self) -> Decimal:
        html = self.s.get(self.product_url, timeout=30).text
        pid = re.search(r'name="product"\s+value="(\d+)"', html) or re.search(r'data-product-id="(\d+)"', html)
        if not pid:
            raise RuntimeError("no Magento product id on page")
        fk = self._form_key(html)
        r = self.s.post(f"{self.root}/checkout/cart/add/", timeout=30,
                        data={"product": pid.group(1), "qty": 1, "form_key": fk},
                        headers={"X-Requested-With": "XMLHttpRequest", "Referer": self.product_url})
        if r.status_code >= 400:
            raise RuntimeError(f"add to cart failed: HTTP {r.status_code}")
        self.form_key = fk
        self.base, _, _ = self._cart_state()
        if not self.base:
            raise RuntimeError("cart is empty after add")
        return self.base

    def try_code(self, code: str) -> CodeResult:
        self.s.post(f"{self.root}/checkout/cart/couponPost/", timeout=30,
                    data={"coupon_code": code, "remove": 0, "form_key": self.form_key},
                    headers={"Referer": f"{self.root}/checkout/cart/"})
        total, disc, msg = self._cart_state()
        if disc > 0 or total < self.base:
            res = CodeResult(code, True, disc or self.base - total, total, msg)
            self.s.post(f"{self.root}/checkout/cart/couponPost/", timeout=30,
                        data={"coupon_code": code, "remove": 1, "form_key": self.form_key})
            return res
        return CodeResult(code, False, message=msg or "no discount")


class MarksElectrical:
    """markselectrical.co.uk: custom basket with an XML AJAX endpoint."""
    root = "https://markselectrical.co.uk"

    def __init__(self, product_url: str, sku: str | None = None):
        self.product_url = product_url
        self.sku = sku or re.search(r"/([a-z0-9]+)_", urlparse(product_url).path, re.I).group(1).upper()

    @staticmethod
    def _tag(xml: str, tag: str) -> str | None:
        m = re.search(rf"<{tag}>(.*?)</{tag}>", xml, re.S)
        return m.group(1) if m else None

    def setup(self) -> Decimal:
        self.s = _session()  # fresh basket each time, so an applied code never carries over
        self.s.get(f"{self.root}/basket/add/item/{self.sku}", timeout=30)
        xml = self.s.get(f"{self.root}/basket/promo/mode/ajax/promocode/X", timeout=30).text
        if self.sku not in xml:
            raise RuntimeError("item did not reach the basket")
        self.base = Decimal(self._tag(xml, "total"))
        return self.base

    def try_code(self, code: str) -> CodeResult:
        xml = self.s.get(f"{self.root}/basket/promo/mode/ajax/promocode/{code}", timeout=30).text
        total = Decimal(self._tag(xml, "total") or "0")
        disc = Decimal(self._tag(xml, "discount-total") or "0")
        msg = re.sub(r"\s+", " ", self._tag(xml, "text") or "")
        action = self._tag(xml, "action") or ""
        if action in ("INVALID", "EXPIRED") or (disc == 0 and total >= self.base):
            return CodeResult(code, False, Decimal(0), total, (msg or action).replace("code  ", f"code {code} "))
        res = CodeResult(code, True, disc or self.base - total, total, msg)
        self.setup()
        return res


KILL_OVERLAYS = ("document.querySelectorAll('#CybotCookiebotDialog,#CybotCookiebotDialogBodyUnderlay,"
                 "#onetrust-consent-sdk,[class*=cookie-banner],[id*=cookie-notice]').forEach(e=>e.remove())")

# Browser checkout profiles for shops without a usable basket API.
BROWSER_PROFILES = {
    "webbs.tv": {
        "pre_add_text": r"delivery only, I.ll do it myself",
        "add": "#product-addtocart-button",
        "cart_url": "https://www.webbs.tv/checkout/cart/",
        "open_text": r"Apply Discount Code",
        "code_input": "#coupon_code",
        "apply": "#discount-coupon-form button.action.apply, #discount-coupon-form button",
        "remove": "#discount-coupon-form button.action.cancel",
        "total": r"Order Total Incl\. VAT\s*£([\d,]+\.\d\d)",
        "message": r"(The coupon code[^.]*\.|You used coupon code[^.]*\.)",
    },
    "sonicdirect.co.uk": {
        "code_on_product_page": True,          # code goes in #DetailVoucher before adding
        "code_input": "#DetailVoucher",
        "apply": ".btn-voucher",
        "add": "#AddToBasket",
        "cart_url": "https://www.sonicdirect.co.uk/viewbasket.asp",
        "total": r"Subtotal\s*£([\d,]+\.\d\d)",
        "applied_code": r"Voucher \(([A-Z0-9]+)\)",
        "message": r"(Voucher \([A-Z0-9]+\)[^£]*£[\d,.]+|[^.]*voucher[^.]*(?:invalid|not valid|expired)[^.]*\.)",
    },
}


class BrowserCheckout:
    """Drives the real storefront in a (stealth) browser, one fresh session per code."""

    def __init__(self, product_url: str, sku: str | None = None):
        self.url = product_url
        host = urlparse(product_url).netloc.removeprefix("www.")
        if host not in BROWSER_PROFILES:
            raise RuntimeError(f"no browser checkout profile for {host}")
        self.p = BROWSER_PROFILES[host]

    def _run(self, code: str | None) -> tuple[Decimal, str]:
        try:
            from patchright.sync_api import sync_playwright
        except ImportError:
            from playwright.sync_api import sync_playwright
        exe = "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None
        p = self.p
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=os.environ.get("DEALSEARCH_HEADFUL") != "1",
                                   executable_path=exe, proxy=None)
            try:
                pg = b.new_page(locale="en-GB", timezone_id="Europe/London")
                pg.goto(self.url, wait_until="domcontentloaded", timeout=45000)
                pg.wait_for_timeout(2500)
                pg.evaluate(KILL_OVERLAYS)
                if p.get("code_on_product_page"):
                    pg.fill(p["code_input"], code or "")  # empty = true baseline (box is pre-filled)
                    if code:
                        with pg.expect_navigation(timeout=30000):
                            pg.click(p["apply"])
                        pg.wait_for_timeout(1500)
                        pg.evaluate(KILL_OVERLAYS)
                if p.get("pre_add_text"):
                    pg.get_by_text(re.compile(p["pre_add_text"], re.I)).first.click()
                pg.click(p["add"])
                pg.wait_for_timeout(4000)
                pg.goto(p["cart_url"], wait_until="domcontentloaded")
                pg.wait_for_timeout(3000)
                pg.evaluate(KILL_OVERLAYS)
                if code and not p.get("code_on_product_page"):
                    if p.get("open_text") and not pg.locator(p["code_input"]).first.is_visible():
                        pg.get_by_text(re.compile(p["open_text"], re.I)).first.click()
                        pg.wait_for_timeout(800)
                    pg.fill(p["code_input"], code)
                    pg.click(p["apply"])
                    pg.wait_for_timeout(5000)
                text = re.sub(r"\s+", " ", pg.inner_text("body"))
            finally:
                b.close()
        m = re.search(p["total"], text, re.I)
        if not m:
            raise RuntimeError("could not read basket total")
        msg = re.search(p["message"], text, re.I)
        applied = re.search(p["applied_code"], text) if p.get("applied_code") else None
        self.applied = applied.group(1) if applied else None
        return Decimal(m.group(1).replace(",", "")), (msg.group(1) if msg else "")

    def setup(self) -> Decimal:
        self.base, _ = self._run(None)
        return self.base

    def try_code(self, code: str) -> CodeResult:
        total, msg = self._run(code)
        if self.p.get("applied_code") and self.applied and self.applied != code:
            return CodeResult(code, False, message=f"rejected; shop applied its own voucher {self.applied} instead")
        if total < self.base:
            return CodeResult(code, True, self.base - total, total, msg)
        return CodeResult(code, False, message=msg or "no discount")


ADAPTERS = {"woocommerce": WooCommerce, "magento2": Magento2, "magento2-form": Magento2Form,
            "marks": MarksElectrical, "browser": BrowserCheckout}


def detect_platform(product_url: str) -> str | None:
    s = _session()
    u = urlparse(product_url)
    root = f"{u.scheme}://{u.netloc}"
    if u.netloc.endswith("markselectrical.co.uk"):
        return "marks"
    if u.netloc.removeprefix("www.") in BROWSER_PROFILES:
        return "browser"
    try:
        if s.get(root + "/wp-json/wc/store/v1/cart", timeout=20).status_code == 200:
            return "woocommerce"
        r = s.get(root + "/rest/V1/directory/currency", timeout=20)
        if r.status_code == 200 and "base_currency_code" in r.text:
            return "magento2"
    except Exception:  # noqa: BLE001
        pass
    return None


def test_codes(product_url: str, codes: list[str], platform: str | None = None,
               sku: str | None = None, log=print) -> tuple[Decimal, list[CodeResult]]:
    platform = platform or detect_platform(product_url)
    if platform not in ADAPTERS:
        raise RuntimeError(f"no basket adapter for {urlparse(product_url).netloc} (platform={platform})")
    a = ADAPTERS[platform](product_url, sku) if platform != "woocommerce" else ADAPTERS[platform](product_url)
    try:
        base = a.setup()
    except Exception as e:  # noqa: BLE001
        if platform != "magento2":
            raise
        log(f"  REST basket refused ({str(e)[:60]}...); using storefront forms")
        platform, a = "magento2-form", Magento2Form(product_url)
        base = a.setup()
    log(f"  basket total before codes: £{base:,.2f} ({platform})")
    results = []
    for code in dict.fromkeys(c.strip().upper() for c in codes if c.strip()):
        _pause()
        try:
            r = a.try_code(code)
        except Exception as e:  # noqa: BLE001
            r = CodeResult(code, False, message=f"error: {str(e)[:80]}")
        results.append(r)
        log(f"  {'✅' if r.ok and r.discount else ('➖' if r.ok else '❌')} {code:<16} "
            + (f"-£{r.discount:,.2f} → £{r.total:,.2f}" if r.ok else r.message[:70]))
    return base, results
