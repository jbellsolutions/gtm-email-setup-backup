# Prospector Coverage Limits & Fallback Strategy

Instantly Prospector's email database coverage is extremely uneven by sub-industry. Some niches have excellent coverage; others have near-zero.

## When to Use Prospector

Prospector works well for well-categorized B2B niches with high database penetration:

- **Staffing & Recruiting** — 73% verified (1,047/1,434), July 2026
- **Law Practice** — ~50-60% verified
- **Public Relations** — ~50% verified
- **Any sub-industry where a prior fetch shows >20% email rate**

## When Prospector Fails

Prospector fails for niche local businesses and industries with poor database coverage:

- **Solar / Renewables** — 0% (0 emails out of 50), July 2026
- **Men's Health Clinics** — loose keyword matching, mixed results
- **Med Spas / Aesthetics** — loose keyword matching, pool company false positives
- **Any sub-industry where the free search returns irrelevant leads AND prior fetches show <10% email rate**

## The Keyword Matching Problem

Prospector's `companyKeyword` filter matches broadly against company names and descriptions. Multi-word phrases don't help much:

- `"men's health"` → pharma companies, software firms, wellness apps
- `"med spa"` → pool & spa companies, bath product retailers
- `"solar installation"` → flooring companies, electrical manufacturers

**Fix:** Always combine `companyKeyword` with `companySubIndustry` to narrow results. Even then, results may be mixed for niche local businesses.

## Fallback Strategy: ScraperCity Maps Scraping

When Prospector can't deliver, use Google Maps scraping. Maps data returns real businesses with names, addresses, phones, and websites — then enrich emails separately.

### Workflow

1. **Scrape Google Maps** for the niche + location via ScraperCity or Apify
2. **Extract domains** from business websites
3. **Find emails** via domain-to-email tools (Hunter.io, Apify, or DIY scraping)
4. **Verify emails** via Reacher gateway
5. **Proceed to research + email creation** as normal

### ScraperCity Maps
```
# Search for businesses on Google Maps
scrapercity maps-search --query "solar installation companies" --location "Austin, TX" --limit 100
```

### Apify Google Maps
Use `compass/crawler-google-places` actor — returns addresses, phones, websites. No emails returned by default; needs separate email enrichment step.

### Domain-to-Email Pipeline
Once you have websites, use one of:
- Apify email finder actors
- Hunter.io API
- DIY scraping (low accuracy: ~4.3% valid rate in law firm test — use only as last resort)

## Decision Tree

```
User requests a niche from Prospector
          ↓
Run free search (Step 1b)
          ↓
    Results relevant?
    ├── YES → Check prior fetches for this sub-industry
    │           ├── >20% email rate → Proceed with fetch
    │           └── <20% or unknown → Fetch 10 as test batch
    │                                    ├── >2 emails → Scale up
    │                                    └── 0-2 emails → SWITCH TO MAPS
    └── NO → Check if better keywords/sub-industry combo exists
              ├── Found → Re-search
              └── Not found → SWITCH TO MAPS
```

## Recovery Example

**Solar Campaign (July 2026):** Prospector free search found 10 relevant solar companies (CitiGreen, New England Clean Energy, Grape Solar). Fetch of 50 contacts returned **0 emails** because the Renewables & Environment sub-industry has zero email coverage in Prospector's database. Next step: switch to ScraperCity Google Maps scraping for solar installers by state.