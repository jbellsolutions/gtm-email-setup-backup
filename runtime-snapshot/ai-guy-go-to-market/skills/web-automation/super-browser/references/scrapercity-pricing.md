# ScraperCity Pricing Reference

## Pricing Model
- **$0.01 per lead** — NOT per scrape
- Maps scraper: 200 leads = $2.00 | 500 leads = $5.00
- `priceMicro` in API responses = per-lead, not total

## Plan Limits
- Growth plan: $149/mo with $149 usage cap
- Exceeding cap triggers auto-upgrade to $649/mo tier
- $649 charge failure = full account pause
- ALWAYS check wallet first: leads × $0.01 must fit within remaining balance

## Repercussions (June 2026)
- 29 scrapes (8×200 + 21×500) = $121
- Exceeded Growth cap → auto $649 upgrade → card declined → paused
- Downloaded leads persist on VPS regardless
