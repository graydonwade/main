"""HTTP fetching: curl_cffi/requests first, a (stealth) browser as fallback.

Big UK retailers sit behind Cloudflare (Currys, AO, Harvey Norman) or Akamai
(Argos, Very). Both hard-block data-centre IPs, whatever the client looks like,
so for those you need a UK residential exit: set DEALSEARCH_PROXY, e.g.

  DEALSEARCH_PROXY=socks5://127.0.0.1:1055      # Tailscale exit node at home (see docs/residential-ip.md)
  DEALSEARCH_PROXY=http://user:pass@host:port   # residential proxy provider

From a good IP, these engines make the client itself look like a normal browser:
  curl_cffi   - real Chrome TLS/HTTP2 fingerprint for plain HTTP  (pip install curl_cffi)
  patchright  - Playwright patched to hide automation signals     (pip install patchright)
Both are optional; we fall back to requests / stock Playwright.
"""
from __future__ import annotations

import logging
import os
import random
import time
from urllib.parse import urlparse

log = logging.getLogger(__name__)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

_last_hit: dict[str, float] = {}


class FetchError(RuntimeError):
    pass


def proxy() -> str | None:
    return os.environ.get("DEALSEARCH_PROXY") or None


def _polite(url: str) -> None:
    """Space out requests to the same host (default 4-8s; DEALSEARCH_DELAY=min,max)."""
    lo, hi = (float(x) for x in os.environ.get("DEALSEARCH_DELAY", "4,8").split(","))
    host = urlparse(url).netloc
    wait = _last_hit.get(host, 0) + random.uniform(lo, hi) - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.time()


def _get_curl_cffi(url: str, timeout: float):
    from curl_cffi import requests as cr
    px = proxy()
    return cr.get(url, impersonate="chrome", timeout=timeout,
                  proxies={"http": px, "https": px} if px else None,
                  headers={"Accept-Language": HEADERS["Accept-Language"]})


def _get_requests(url: str, timeout: float):
    import requests
    px = proxy()
    return requests.get(url, headers=HEADERS, timeout=timeout,
                        proxies={"http": px, "https": px} if px else None)


def fetch_http(url: str, timeout: float = 20.0, retries: int = 2) -> str:
    try:
        import curl_cffi  # noqa: F401
        getter = _get_curl_cffi
    except ImportError:
        getter = _get_requests
    last: Exception | None = None
    for attempt in range(retries + 1):
        _polite(url)
        try:
            r = getter(url, timeout)
            if r.status_code == 200 and len(r.text) > 2000:
                return r.text
            last = FetchError(f"HTTP {r.status_code}, {len(r.text)} bytes")
            if r.status_code in (403, 404, 410):
                break  # retrying a block or a missing page won't help
        except Exception as e:  # network / TLS / proxy
            last = e
        time.sleep(1.5 * (attempt + 1))
    raise FetchError(f"{url}: {last}")


fetch_requests = fetch_http  # backwards-compatible name


def _browser_proxy() -> dict | None:
    px = proxy()
    if not px:
        return None
    u = urlparse(px)
    cfg = {"server": f"{u.scheme}://{u.hostname}:{u.port}"}
    if u.username:
        cfg |= {"username": u.username, "password": u.password or ""}
    return cfg


def fetch_browser(url: str, timeout_ms: int = 40000) -> str:
    try:
        from patchright.sync_api import sync_playwright
    except ImportError:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:  # pragma: no cover - optional dependency
            raise FetchError("no browser engine: pip install patchright (or playwright)") from e
    headless = os.environ.get("DEALSEARCH_HEADFUL") != "1"
    exe = os.environ.get("DEALSEARCH_CHROMIUM") or (
        "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None)
    _polite(url)
    with sync_playwright() as p:
        kw = {"headless": headless, "proxy": _browser_proxy()}
        try:
            browser = p.chromium.launch(**kw)
        except Exception:
            if not exe:
                raise
            browser = p.chromium.launch(executable_path=exe, **kw)
        try:
            page = browser.new_page(locale="en-GB", timezone_id="Europe/London")
            if os.environ.get("DEALSEARCH_SAVE_DATA", "1") == "1":
                # Prices are in the HTML/JSON; skip heavy assets (matters on mobile data).
                page.route("**/*", lambda route: route.abort()
                           if route.request.resource_type in ("image", "media", "font")
                           else route.continue_())
            try:
                resp = page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)  # client-side prices; lets a JS challenge clear
                if "Just a moment" in page.title():  # Cloudflare interstitial: give it time
                    page.wait_for_timeout(12000)
                html, title = page.content(), page.title()
            except Exception as e:  # playwright.Error, timeouts
                raise FetchError(f"browser: {str(e).splitlines()[0][:150]}") from e
            if any(t in title for t in ("Attention Required", "Access Denied", "Just a moment")):
                raise FetchError(f"browser: blocked ({title.strip()[:40]}) - needs a residential IP "
                                 "(DEALSEARCH_PROXY)")
            if resp is not None and resp.status >= 400 and len(html) < 20000:
                raise FetchError(f"browser: HTTP {resp.status}")
            return html
        finally:
            browser.close()


def fetch(url: str, use_browser: str = "auto") -> str:
    """use_browser: 'never' | 'auto' (fallback on failure) | 'always'."""
    if use_browser == "always":
        return fetch_browser(url)
    try:
        return fetch_http(url)
    except FetchError as e:
        if use_browser == "never":
            raise
        log.info("http failed (%s); retrying with browser", e)
        return fetch_browser(url)
