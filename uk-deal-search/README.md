# uk-deal-search

Find the cheapest **new** price for a product across UK retailers, then stack the best coupon code and cashback on top.

- Reads prices from `schema.org` Product JSON-LD and meta tags. Most UK appliance retailers publish these, so there's no per-site scraper to maintain. A per-listing CSS `selector` covers the rest.
- Rejects eBay and marketplace resellers, outlet storefronts, and anything marked used, refurbished, graded, ex-display or open-box (`dealsearch/filters.py`).
- Uses Playwright for bot-protected sites that render prices with JavaScript (Currys, AO, John Lewis, Costco, LG).
- Coupons carry a confidence level (`verified` / `likely` / `unverified`). The ranking uses one checkout code plus one cashback offer, and applies only `likely`+ codes unless you pass `--include-unverified`.

## Use

```bash
pip install -e '.[browser,dev]' && playwright install chromium
dealsearch search WT1210WWF                       # retailer + comparison-site search URLs, to discover listings
dealsearch check  projects/lg-washtower-2026-11/products.yaml   # fetch live prices into the file
dealsearch report projects/lg-washtower-2026-11/products.yaml \
       --coupons projects/lg-washtower-2026-11/coupons.yaml     # ranked markdown table
```

## Adding a project
Make `projects/<name>/products.yaml`, listing each model and its retailer URLs, and `coupons.yaml`. Copy the LG WashTower project as a template.
Retailers, comparison sites and suspect domains are in `dealsearch/retailers.yaml`.

## Prior art
These were looked at rather than vendored. Structured-data extraction makes per-site scrapers unnecessary for this use.
- [extruct](https://github.com/scrapinghub/extruct): a fuller JSON-LD/microdata/RDFa extractor and a drop-in upgrade for `extract.py`.
- [price-parser](https://github.com/scrapinghub/price-parser): robust price-string parsing.
- PriceSpy / PriceRunner / idealo: used to discover retailers, not as a price source of truth.

## Projects
- `projects/lg-washtower-2026-11`: LG WT1210BBTN1 / WT1210NBTN1 / WT1210WWF, Black Friday 2026. See its `RESULTS.md`.
