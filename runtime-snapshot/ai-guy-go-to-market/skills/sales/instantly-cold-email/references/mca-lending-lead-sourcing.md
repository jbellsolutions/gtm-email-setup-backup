# MCA & Business Lending Lead Sourcing Methodology

Proven multi-source approach for finding MCA funders, ISO shops, and business lenders who buy leads and staff sales floors.

## Target ICP (Two Distinct Segments)

### Primary: ISO Shops & MCA Brokers
- Buy leads and put reps on phones to close merchants
- Run sales floors / call centers
- Pain point: lead costs eating margins, rep productivity

### Secondary: Direct Funders & Lenders
- Have the capital, underwrite and fund deals
- Recruit ISOs to originate for them
- Pain point: ISO recruitment and retention

## Source Stack (Ranked by ROI)

### 1. deBanked Funder Directory (Tab 3 in Claude framework)
**URL:** https://debanked.com/funder-lender-directory/
**Yield:** ~40 curated funders with phone numbers + partner URLs
**Method:** Browser console extraction — `Array.from(document.querySelectorAll('article')).map(...)`
**Quality:** Highest — every listing is vetted by deBanked. Most link directly to ISO partner signup pages.

### 2. Apify PipelineLabs — Company Discovery (Tab 2/3)
**Actor:** `kVYdvNOefemtiDXO5`
**Cost:** $1 per 1,000 leads
**Method:** Use `companyKeywordIncludes` (NOT `companyIndustryIncludes` — MCA isn't a standard industry code):
```json
{
  "companyKeywordIncludes": [
    "merchant cash advance", "business funding", "MCA lending",
    "business loans", "revenue based financing", "working capital"
  ],
  "hasEmail": true,
  "emailStatusIncludes": ["verified"],
  "personLocationCountryIncludes": ["United States"],
  "totalResults": 5000
}
```
**Critical:** PipelineLabs emails are ~90% invalid. Use ONLY for company/title discovery.
**Pipeline:** PipelineLabs → extract domains → ScraperCity Website Finder → email-validate.

### 3. Google Maps by Hotspot City (Tab 4)
**Tool:** ScraperCity Maps
**Cost:** $0.01/listing (~$0.50 per city at 50 results)
**Queries that work:** "merchant cash advance", "business loans", "business funding"
**Cities tested (June 2026 yields):**
| City | "merchant cash advance" | "business loans" | "business funding" |
|------|------------------------|-------------------|-------------------|
| New York, NY | 38 domains | — | — |
| Los Angeles, CA | — | 34 domains | — |
| Miami, FL | 35 domains | — | — |
| Dallas, TX | — | 38 domains | — |
| Phoenix, AZ | — | — | 38 domains |
| Denver, CO | — | 42 domains | — |
| Long Island, NY | — | — | 34 domains |
| Chicago, IL | 17 domains | — | — |
| Atlanta, GA | 17 domains | — | — |
| Charlotte, NC | 11 domains | — | — |
| Las Vegas, NV | 8 domains | — | — |
| Newark, NJ | 3 domains | — | — |
**Pattern:** Large metros yield 30-42, smaller markets 3-17. Zero emails returned — domains only.
**Scale strategy:** 12 cities × 2 query variations = ~500-800 unique domains.

### 4. Meta Ad Library via ScrapeCreators (Tab 6)
**Tool:** `scrapecreators facebook adlibrary-search-companies`
**Cost:** 1 credit per query (free from 21K+ credit balance)
**Keywords tested:**
- "merchant cash advance" → 15 results (Cash Advance Service, Loan Service)
- "business funding" → 15 results (Loan Service, Finance)
- "MCA funding" → 4 results (Financial Service)
- "business loans" → 15 results
- "small business loans" → 15 results (Loan Service, Financial Service)
**Limitation:** 15-result hard cap per query. MCA is not a hyper-local vertical (like HVAC) so geographic spraying by state may not multiply volume significantly.
**Signal value:** Companies actively spending on ads = budget + marketing motion. Gold for ICP qualification.

### 5. Niche Directories (Tab 3)
**Accessible:** deBanked Funder Directory (41 funders)
**Blocked/Failed:**
- Daily Funder — Cloudflare
- SBFA (sbfassociation.org) — members page empty ("Not available yet")
- ILPA (innovativelending.org) — ModSecurity
- Broker Fair sponsors (brokerfair.org) — iframe JS rendering
- deBanked MCA Software & CRMs — 404 / blog post only

### 6. Tech Signals (Tab 8)
**BuiltWith "Centrex"** — FAILED. ScraperCity BuiltWith scraper returned "Lookup failed." Centrex CRM is not in BuiltWith's technology database (too niche/industry-specific).
**BuiltWith direct search** — FAILED. Searching "merchant cash advance" on BuiltWith.com matched generic terms (Miva Merchant, etc.), not MCA-specific tech.
**Alternative:** No viable tech detection signal found for MCA companies. Skip this tab.

## Verification Pipeline (Mandatory)
```
Raw leads → ScraperCity email-validate ($0.0036/email) → valid only → qualify_leads.py → upload
```
Expect 40-90% invalidity depending on source. PipelineLabs worst (90%), Maps needs Website Finder first.

## Copy Angles (for campaign build)
- Phones Are Quiet: Brokers living on inbound ISO submissions
- Ads Are Broken: MCA brokers burning ad spend on lead gen
- Competitors' Phones: "Your competitors have an AI-SDR calling merchants you're bidding against"
- Go Direct: "You're paying ISOs 10-15 points. Keep the spread."