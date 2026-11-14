# Getting past retailer bot blocks

## What's actually blocking us (tested 2026-11-14)
| Retailers | Protection | Result from a cloud server |
|---|---|---|
| Currys, AO, Harvey Norman | Cloudflare | 403 "Attention Required" (hard block) |
| Argos, Very | Akamai Bot Manager | 403 "Access Denied" |

From a US data-centre IP these blocks hold whatever the client looks like. A real Chrome TLS fingerprint
(curl_cffi) and a stealth-patched browser (patchright) still get 403. **The IP is the problem.** A UK
residential IP is the fix. The stealth client (already built in) helps only once the IP is good.

## Options, best first

### 1. Your own home connection (free, genuinely residential)
- **Run it at home:** `pip install -e '.[browser]' && dealsearch check ...` on your own computer.
- **Run it here, routed through home:** make a home computer or Raspberry Pi a **Tailscale exit node**, then
  `source scripts/home-exit.sh`. This works in unprivileged containers via userspace networking + SOCKS5.
  Put `TS_AUTHKEY` in the cloud environment's secrets.
- Alternatives to Tailscale: WireGuard to your router, or [microsocks](https://github.com/rofl0r/microsocks)
  on a home machine exposed through a [cloudflared](https://github.com/cloudflare/cloudflared) /
  Tailscale tunnel.

### 1b. Your Android phone as the exit node (no home broadband needed)
Install Tailscale, enable **Run as exit node**, approve it in the admin console, and use `scripts/home-exit.sh` with `TS_EXIT_NODE=<phone name>`.
Traffic goes out over mobile data, and carrier IPs are rarely blocked. Keep the app in the foreground during a run.
iOS can't act as an exit node.

### 2. A UK mobile hotspot / 4G dongle
Mobile carrier IPs (CGNAT, shared by thousands of users) are almost never hard-blocked. A cheap SIM in a
Raspberry Pi 4G HAT, used as a Tailscale exit node, gives you a "mobile proxy" you own.

### 3. Commercial residential / ISP proxies
Set `DEALSEARCH_PROXY=http://user:pass@host:port` with a UK geo-target. Prefer providers whose
residential pool is **consent-based**: peers opt in and are paid, the SDK discloses it, the provider is
an EWDCI member, and it publishes a KYC policy. **Static ISP proxies** (residential-ASN IPs hosted in
data centres) are a cleaner, cheaper option for a handful of sites. Our volume (a few dozen pages per run)
costs pennies on pay-per-GB plans.

## Open-source tooling (GitHub)
| Project | What it does | Status here |
|---|---|---|
| [lexiforest/curl_cffi](https://github.com/lexiforest/curl_cffi) | Real Chrome/Safari TLS + HTTP/2 fingerprints for plain HTTP | **Used** (first fetch attempt) |
| [Kaliiiiiiiiii-Vinyzu/patchright-python](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python) | Drop-in Playwright with automation leaks patched | **Used** (browser fallback) |
| [daijro/camoufox](https://github.com/daijro/camoufox) | Stealth Firefox build with fingerprint rotation; strong against Cloudflare/Akamai | Good next step if patchright gets challenged from a residential IP |
| [ultrafunkamsterdam/nodriver](https://github.com/ultrafunkamsterdam/nodriver) | CDP-only Chrome automation (successor to undetected-chromedriver) | Alternative |
| [seleniumbase/SeleniumBase](https://github.com/seleniumbase/SeleniumBase) | UC/CDP mode, can click through Cloudflare Turnstile | Alternative |
| [FlareSolverr/FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) | Proxy server that solves Cloudflare challenges and returns cookies | Useful as a sidecar |
| [omkarcloud/botasaurus](https://github.com/omkarcloud/botasaurus) | Scraping framework with anti-detect browser built in | Alternative |
| [tailscale/tailscale](https://github.com/tailscale/tailscale) | Exit node used by `scripts/home-exit.sh` | **Used** |

## Knobs
- `DEALSEARCH_PROXY`: proxy for every request (http/https/socks5).
- `DEALSEARCH_HEADFUL=1`: visible browser (needs a display; it passes more checks than headless).
- `DEALSEARCH_SAVE_DATA=1` (default): the browser skips images, video and fonts, cutting data use several-fold. Set it to 0 if a site needs them to render prices.
- `DEALSEARCH_DELAY=4,8`: random gap in seconds between hits to the same site. Keep it, because burst traffic is what got Webbs, Donaghy and Hughes to start returning 403 mid-run.
