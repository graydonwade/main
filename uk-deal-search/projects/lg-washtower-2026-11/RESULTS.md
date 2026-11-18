# LG WashTower: cheapest NEW UK prices (live check 2026-11-14)

Prices marked **live** were read from the retailer's own product page on 2026-11-14.
Rows marked *snippet (live check failed)* belong to sites that block automated access (AO, Currys, Argos, Very, Hughes, Harvey Norman); their figures are older search-snippet prices and need checking by hand.
Coupon codes were batch-tested in real baskets on 2026-11-15 (`dealsearch coupons`); see *Coupon testing* below.

## Cheapest per model (live prices, legitimate retailers)

| Model | Cheapest | Runner-up | Notes |
|---|---|---|---|
| **WT1210WWF** (white) | **£1,299**: [Mark's Electrical](https://markselectrical.co.uk/wt1210wwf_lg-washer-dryer) (free delivery and recycling) or [Sonic Direct](https://www.sonicdirect.co.uk/prod/Washer-Dryers/LG-WT1210WWF-Washer-Dryer-in-White-1400-Spin-12kg10kg-A-Rated-WashTower-with-Dual-Inverter-Heat-Pump) (RRP £1,899, in stock) | [Paul Davies](https://www.pauldavieskitchensandappliances.co.uk/lg-wt1210wwf-12kg-10kg-1400-spin-washer-dryer-white.html) £1,299.99 ("only 3 left"); Harvey Norman UK £1,299 (user-seen) | **£1,244** at Mark's with Marks+ (£19.99/yr, so £1,263.99 net). Appliance City £1,399 − SALE50 = £1,349 |
| **WT1210BBTN1** (black) | **£1,459**: [Webbs](https://www.webbs.tv/lg-washtower-wt1210bbtn1-heat-pump-12-10kg-washer-dryer-platinum-black.html) (was £1,699, 5-yr warranty) or [Donaghy Bros](https://donaghybros.co.uk/lg-washtower-wt1210bbtn1-12kg-10kg-1400rpm-washer-dryer-black.html) (in stock) | [Paul Davies](https://www.pauldavieskitchensandappliances.co.uk/lg-wt1210bbtn1-12kg-10kg-1400-spin-washer-dryer-black.html) £1,479.99 | Costco £1,499.98 (members; page shows out-of-stock text). **Sonic Direct £1,999 − code VPV5DS500 = £1,499** (verified in basket). Appliance City £1,599 − SALE50 = £1,549. Mark's £1,599 / £1,544 Marks+ |
| **WT1210NBTN1** (green/beige) | **£1,199**: [Harvey Norman UK](https://www.harveynorman.co.uk/products/lg-washtower-12kg-washer-10kg-dryer-freestanding-washer-dryer-wt1210nbtn1-green-beige) (Black Friday, was £1,499; seen by user 2026-11-15; Harvey Norman blocks our checks, so delivery and stock need confirming) | £1,449: [Appliance City](https://www.appliancecity.co.uk/laundry/washer-dryers/freestanding-washer-dryers/lg-wt1210nbtn1-12kg-10kg-washtower-turbowash-washer-dryer-green-beige/) £1,499 − code **SALE50** (in stock, free delivery, free 5-yr warranty to claim) | [LG UK](https://www.lg.com/uk/laundry/washtowers/wt1210nbtn1/) £1,599 − 5% member = £1,519 | If LG's 10% refer-a-friend code stacks with the member discount, LG comes to about **£1,367**, with free installation. Unconfirmed: you need someone's referral code. Costco's £1,299.99 listing is gone |

Changes since the snippet-based pass: Sonic Direct white dropped to £1,299; Paul Davies is £1,299.99 white and £1,479.99 black; Costco black is £1,499.98, not £1,449.99; John Lewis black is £1,999; LG UK is £1,599 white (out of stock), £1,999 black and £1,599 green.

## Coupon testing (real baskets, 2026-11-15)
Codes were added to an anonymous basket through each shop's own basket API or storefront. Nothing was ordered.
Candidates were codes published on the retailer's own pages and on coupon sites, the same prefix with other common amounts (e.g. SALE10–SALE250), and 24 common seasonal codes.

| Retailer | Method | Codes tried | Result |
|---|---|---|---|
| Appliance City | WooCommerce Store API | ~35 per model | **SALE50 works on all three** (−£50). SALE10/25/30/75/100/150/200/250 exist but are locked to other products |
| Sonic Direct | browser | product voucher + list | **VPV5DS500: −£500 on black** (£1,999 → £1,499). No voucher on white (already £1,299) |
| Mark's Electrical | basket XML endpoint | 37 | **MEMULTIBUY: 10% off when the WashTower is bought with another eligible item of £249+** (white: £1,299 → £1,169.10). LGSAVE50/100/200 and QUOSAVE10 are valid but for other products; OUTLET10/OUTLET5 are outlet stock only; HUKD5/HUKD10, MARKS5/MARKS10 and 9 generic codes are expired |
| Paul Davies | Magento REST | 24 per model | none |
| Donaghy Bros | Magento REST | 24 | none |
| Carters Direct | Magento REST | 24 | none |
| Webbs | browser (REST blocked) | 24 | none |
| Currys / AO / Argos / Very | — | — | not testable: these sites block data-centre IPs (see `docs/residential-ip.md`) |

## Other savings
- **Appliance City `SALE50`**: verified in a real basket on all three WashTowers.
- **Sonic Direct `VPV5DS500`**: verified, −£500 on the black WT1210BBTN1.
- **LG UK**: free membership gives 5% off the first order, a refer-a-friend code gives 10% (reported to stack), and WashTowers come with free installation. Trade-in saves up to £100. TopCashback was advertising 10% on LG appliances (8 Nov newsletter), but it usually won't pay out alongside a non-affiliate code.
- **Price beat**: Sonic Direct ("We Price Beat") and Richer Sounds; quote the cheapest live price above.
- **Blue Light Card**: AO £15 off, Currys up to £25 off.
- Mark's Electrical shows a "10% Multibuy Discount" if you buy more than one appliance.

## Retailer legitimacy (standard step: `dealsearch vet`, verdicts in `dealsearch/retailers.yaml`)
Every shortlisted retailer is an established UK business with a Companies House record, a physical shop or warehouse, and a large Trustpilot history. Most are Euronics member stores, which is a strong sign of UK-channel stock with a UK LG warranty.

| Retailer | Verdict | Evidence |
|---|---|---|
| Mark's Electrical | LEGIT | Marks Electrical Ltd 04463433, AIM-listed group; est. 2002; Trustpilot 4.8 / ~116k |
| Appliance City | LEGIT | Bunny Appliance Warehouse Ltd 03027841 (1995), Nottingham; Trustpilot 4.5 / ~45k. *Not* the similarly named Appliance City Ltd 05839129, which is in liquidation |
| Webbs | LEGIT | Webbs of Cannock Ltd 08002533, trading since 1958, Euronics; Trustpilot 4.8 / ~950 |
| Carters Direct | LEGIT | Sussex firm since 1987, ~7 showrooms, Euronics; Trustpilot 4.9 / ~2.4k (company no. not confirmed) |
| Costco UK | LEGIT, with caveats | Costco Wholesale UK Ltd 02635489. Membership needed. Costco covers 2 years; the extra LG years must be registered with LG within 90 days |
| Sonic Direct, DB Domestics, RDO, Paul Davies, Stellisons, Genesis | LEGIT | Established independents, mostly Euronics members, Trustpilot 4.5–4.9 |
| Harvey Norman UK | LEGIT | Genuine Harvey Norman group, 4 UK stores (UK company formed 2024) |
| Donaghy Bros | LEGIT, with caveats | NI030598, trading since 1964. Its pages are mirrored on a `duckdns.org` domain, so buy only at donaghybros.co.uk and confirm UK (not ROI) stock |
| Appliances Direct | LEGIT | Buy It Direct Ltd 04171412. Also sells graded WashTowers (6-month cover), so make sure the listing is *new* |
| Currys, John Lewis, AO, Very, Euronics, Hughes | LEGIT | Major UK chains |
| **Lifestyle Home Appliance Warehouse** | **AVOID** | Domain registered 10 Jul 2026; shows the £1,317 'Typical UK price' in both £ and €; no company found; Trustpilot 2.5 from 5 reviews reporting non-delivery and "scam"; matches a known clone-store pattern. **Don't pay; if you already have, contact your card issuer** |
| Yellow Electronics | Real business, wrong stock | Sells customer returns, surplus and box-damaged stock, so the £999 listing is almost certainly not new |
| TieDex | Real but not recommended | General reseller, not LG-authorised; complaints about import charges and stock that isn't actually in stock |

These facts come from search snippets of Companies House, Endole, Trustpilot and euronics.co.uk; the registers themselves were blocked from this environment. Check the company number on Companies House before paying.

## Excluded
eBay; AW Outlet (graded stock); John Lewis Outlet listing; TieDex (reseller with poor reviews, dearer anyway);
Yellow Electronics (£999, out of stock, implausible); Fortuna Jersey (Jersey only).
Lifestyle Home Appliance Warehouse (AVOID, see above).

## Full ranking (generated by `dealsearch report`)

## WT1210WWF — LG WashTower 12kg/10kg washer dryer, white

| Retailer | Trust | Listed + delivery | After codes/cashback | Applied | Price source |
|---|---|---|---|---|---|
| [Sonic Direct](https://www.sonicdirect.co.uk/prod/Washer-Dryers/LG-WT1210WWF-Washer-Dryer-in-White-1400-Spin-12kg10kg-A-Rated-WashTower-with-Dual-Inverter-Heat-Pump) | LEGIT | £1,299.00 | £799.00 | VPV5DS500 (verified) | live 2026-11-14 |
| [Mark's Electrical](https://markselectrical.co.uk/wt1210wwf_lg-washer-dryer) | LEGIT | £1,299.00 | £1,299.00 | — | live 2026-11-14 |
| [Harvey Norman UK](https://www.harveynorman.co.uk/products/lg-washtower-12kg-washer-10kg-dryer-freestanding-washer-dryer-wt1210wwf-white) | LEGIT | £1,299.00 | £1,299.00 | — | user screenshot 2026-11-15 |
| [Paul Davies](https://www.pauldavieskitchensandappliances.co.uk/lg-wt1210wwf-12kg-10kg-1400-spin-washer-dryer-white.html) | LEGIT | £1,299.99 | £1,299.99 | — | live 2026-11-14 |
| [Appliance City](https://www.appliancecity.co.uk/laundry/lg-wt1210wwf-12kg-10kg-washtower-turbowash-washer-dryer-white/) | LEGIT | £1,399.00 | £1,349.00 | SALE50 (verified) | live 2026-11-14 |
| [John Lewis](https://www.johnlewis.com/lg-wt1210bbtn1-wt1210wwf-washtower-freestanding-heat-pump-washer-dryer-12kg-10kg-load-1400rpm-spin/white/p112485759) | LEGIT | £1,499.00 | £1,499.00 | — | snippet (live check failed) |
| [DB Domestics](https://www.dbdomestics.com/search?q=WT1210WWF) | LEGIT | £1,499.00 | £1,499.00 | — | snippet (live check failed) |
| [LG UK](https://www.lg.com/uk/laundry/washtowers/wt1210wwf/) | LEGIT | £1,599.00 | £1,519.05 | (member welcome) (likely) | live 2026-11-14 |
| [Currys](https://www.currys.co.uk/products/lg-washtower-wt1210wwf-wifienabled-12-kg-washer-dryer-white-10301982.html) | LEGIT | £1,599.00 | £1,599.00 | — | snippet (live check failed) |
| [Euronics](https://www.euronics.co.uk/catalogue/laundry/washing-machines/freestanding-washing-machines/front-loading-washing-machines/lg-wt1210wwf-12kg-wash-10kg-dry-1400rpm-washer-dryer-tower-white/p/LGEWT1210WWF) | LEGIT | £1,599.00 | £1,599.00 | — | live 2026-11-14 |
| [Webbs](https://www.webbs.tv/catalogsearch/result/?q=WT1210WWF) | LEGIT | £1,599.00 | £1,599.00 | — | snippet (live check failed) |
| [RDO](https://www.rdo.co.uk/products/l-g-free-standing-washer-dryer-wt1210wwf-white) | LEGIT | £1,599.00 | £1,599.00 | — | live 2026-11-14 |

## WT1210BBTN1 — LG WashTower 12kg/10kg washer dryer, platinum black

| Retailer | Trust | Listed + delivery | After codes/cashback | Applied | Price source |
|---|---|---|---|---|---|
| [Webbs](https://www.webbs.tv/lg-washtower-wt1210bbtn1-heat-pump-12-10kg-washer-dryer-platinum-black.html) | LEGIT | £1,459.00 | £1,459.00 | — | live 2026-11-14 |
| [Donaghy Bros](https://donaghybros.co.uk/lg-washtower-wt1210bbtn1-12kg-10kg-1400rpm-washer-dryer-black.html) | LEGIT-WITH-CAVEATS | £1,459.00 | £1,459.00 | — | live 2026-11-14 |
| [Paul Davies](https://www.pauldavieskitchensandappliances.co.uk/lg-wt1210bbtn1-12kg-10kg-1400-spin-washer-dryer-black.html) | LEGIT | £1,479.99 | £1,479.99 | — | live 2026-11-14 |
| [Sonic Direct](https://www.sonicdirect.co.uk/prod/Washer-Dryers/LG-WT1210BBTN1-Washer-Dryer-in-Platinum-Black-1400-Spin-12kg10kg-A-Rated-WashTower-with-Dual-Inverter-Heat-Pump) | LEGIT | £1,999.00 | £1,499.00 | VPV5DS500 (verified) | live 2026-11-14 |
| [Costco UK](https://www.costco.co.uk/p/464003) | LEGIT-WITH-CAVEATS | £1,499.98 | £1,499.98 | — | live 2026-11-14 |
| [Appliance City](https://www.appliancecity.co.uk/laundry/washer-dryers/freestanding-washer-dryers/lg-wt1210bbtn1-12kg-10kg-washtower-washer-dryer-black-steel/) | LEGIT | £1,599.00 | £1,549.00 | SALE50 (verified) | live 2026-11-14 |
| [Mark's Electrical](https://markselectrical.co.uk/wt1210bbtn1_lg-washer-dryer) | LEGIT | £1,599.00 | £1,599.00 | — | live 2026-11-14 |
| [Appliances Direct](https://www.appliancesdirect.co.uk/search?q=WT1210BBTN1) | LEGIT | £1,599.00 | £1,599.00 | — | snippet (live check failed) |
| [Very](https://www.very.co.uk/search/WT1210BBTN1) | LEGIT | £1,599.00 | £1,599.00 | — | snippet (live check failed) |
| [Euronics](https://www.euronics.co.uk/catalogue/laundry/washer-dryers/freestanding-washer-dryers/lg-wt1210bbtn1-12kg10kg-1400-spin-washer-dryer-platinum-black/p/LGEWT1210BBTN1) | LEGIT | £1,599.99 | £1,599.99 | — | live 2026-11-14 |
| [Currys](https://www.currys.co.uk/search?q=WT1210BBTN1) | LEGIT | £1,699.00 | £1,699.00 | — | snippet (live check failed) |
| [RDO](https://www.rdo.co.uk/products/l-g-free-standing-washer-dryer-wt1210bbtn1-platinum-black) | LEGIT | £1,699.00 | £1,699.00 | — | live 2026-11-14 |
| [LG UK](https://www.lg.com/uk/laundry/washtowers/wt1210bbtn1/) | LEGIT | £1,999.00 | £1,899.05 | (member welcome) (likely) | live 2026-11-14 |
| [John Lewis](https://www.johnlewis.com/lg-wt1210bbtn1-wt1210wwf-washtower-freestanding-heat-pump-washer-dryer-12kg-10kg-load-1400rpm-spin/black/p112485759) | LEGIT | £1,999.00 | £1,999.00 | — | live 2026-11-14 (page text) |
| [Genesis](https://www.genesishomeappliances.co.uk/lg-wt1210bbtn1-black-100102308.html) | LEGIT | £1,999.00 | £1,999.00 | — | snippet (live check failed) |

## WT1210NBTN1 — LG WashTower 12kg/10kg washer dryer, green & beige

| Retailer | Trust | Listed + delivery | After codes/cashback | Applied | Price source |
|---|---|---|---|---|---|
| [Harvey Norman UK](https://www.harveynorman.co.uk/products/lg-washtower-12kg-washer-10kg-dryer-freestanding-washer-dryer-wt1210nbtn1-green-beige) | LEGIT ⚠️ >20% below median | £1,199.00 | £1,199.00 | — | user screenshot 2026-11-15 |
| [Sonic Direct](https://www.sonicdirect.co.uk/prod/Washer-Dryers/LG-WT1210NBTN1-Washer-Dryer-in-Green--Beige-1400-Spin-12kg10kg-A-Rated-WashTower) | LEGIT | £1,699.00 | £1,199.00 | VPV5DS500 (verified) | snippet (live check failed) |
| [Appliance City](https://www.appliancecity.co.uk/laundry/washer-dryers/freestanding-washer-dryers/lg-wt1210nbtn1-12kg-10kg-washtower-turbowash-washer-dryer-green-beige/) | LEGIT | £1,499.00 | £1,449.00 | SALE50 (verified) | live 2026-11-14 |
| [LG UK](https://www.lg.com/uk/laundry/washtowers/wt1210nbtn1/) | LEGIT | £1,599.00 | £1,519.05 | (member welcome) (likely) | live 2026-11-14 |
| [Currys Business](https://business.currys.co.uk/catalogue/domestic-appliances/laundry/washer-dryers-free-standing/lg-washtower-ai-direct-drive-wt1210nbtn1-wifi-enabled-12-kg-washer-dryer-green-beige/B598238B) | LEGIT | £1,698.96 | £1,698.96 | — | snippet (live check failed) |
| [Carters Direct](https://www.cartersdirect.co.uk/lg-wt1210nbtn1.html) | LEGIT | £1,699.00 | £1,699.00 | — | live 2026-11-14 |
| [Stellisons](https://www.stellisonselectrical.co.uk/lg-wt1210nbtn1-abgqpuk-1000083760.html) | LEGIT | £1,699.00 | £1,699.00 | — | snippet (live check failed) |
| [Currys](https://www.currys.co.uk/products/lg-washtower-ai-direct-drive-wt1210nbtn1-wifienabled-12-kg-washer-dryer-green-and-beige-10272687.html) | LEGIT | £1,798.97 | £1,798.97 | — | snippet (live check failed) |
