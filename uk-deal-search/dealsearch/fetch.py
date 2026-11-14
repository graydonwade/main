"""HTTP fetching with a plain-requests path and an optional Playwright fallback.

Many big UK retailers (Currys, AO, John Lewis, Argos) sit behind Akamai/Cloudflare
bot protection and render prices client-side, so plain requests often gets a 403
or an empty shell. If Playwright is installed we retry those in a real browser.
"""
from __future__ import annotations

import logging
import os
import time

import requests

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


class FetchError(RuntimeError):
    pass


def fetch_requests(url: str, timeout: float = 20.0, retries: int = 2) -> str:
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200 and len(r.text) > 2000:
                return r.text
            last = FetchError(f"HTTP {r.status_code}, {len(r.text)} bytes")
        except requests.RequestException as e:  # network / TLS / proxy
            last = e
        time.sleep(1.5 * (attempt + 1))
    raise FetchError(f"{url}: {last}")


def fetch_browser(url: str, timeout_ms: int = 30000) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:  # pragma: no cover - optional dependency
        raise FetchError("playwright not installed (pip install '.[browser]')") from e
    with sync_playwright() as p:
        # Use a pre-installed Chromium if the bundled one isn't downloaded.
        exe = os.environ.get("DEALSEARCH_CHROMIUM") or (
            "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None)
        try:
            browser = p.chromium.launch()
        except Exception:
            if not exe:
                raise
            browser = p.chromium.launch(executable_path=exe)
        try:
            page = browser.new_page(user_agent=UA, locale="en-GB")
            try:
                resp = page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)  # let client-side price widgets render
                html = page.content()
            except Exception as e:  # playwright.Error, timeouts
                raise FetchError(f"browser: {str(e).splitlines()[0][:150]}") from e
            if resp is not None and resp.status >= 400:
                raise FetchError(f"browser: HTTP {resp.status}")
            return html
        finally:
            browser.close()


def fetch(url: str, use_browser: str = "auto") -> str:
    """use_browser: 'never' | 'auto' (fallback on failure) | 'always'."""
    if use_browser == "always":
        return fetch_browser(url)
    try:
        return fetch_requests(url)
    except FetchError as e:
        if use_browser == "never":
            raise
        log.info("requests failed (%s); retrying with browser", e)
        return fetch_browser(url)
