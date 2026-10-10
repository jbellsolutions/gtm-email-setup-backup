# MCA / ISO Lead Generation — Business Lending Broker Market

Lead generation for the merchant cash advance (MCA) and business lending vertical. Primary ICP: ISOs, super-ISOs, and MCA brokers — the sales organizations that buy leads, run sales floors, hire reps, and originate deals to funders. Secondary ICP: direct funders/lenders who recruit ISOs.

## ICP Definition

### Target A: ISOs, Super-ISOs & MCA Brokers (PRIMARY)
Sales organizations that buy leads, put reps on phones calling merchants, run sales floors/call centers, hire and train salespeople, originate and syndicate deals.

**Their pain:** Lead costs eat margins ($50-150/lead, 5-10% conversion). Reps spend more time dialing dead numbers than closing.

**Keywords:** "merchant cash advance," "business loans," "business funding," "MCA lender," "small business financing," "revenue based financing"

### Target B: Direct Funders & Lenders (SECONDARY)
Have capital and recruit ISOs via "ISO partner programs." Different pitch — setting appointments with potential ISOs for them to recruit.

**Signal:** Websites with `/partners`, `/iso`, `/broker-program`, `/partner-with-us` paths.

## Proven Sources

### Tier 1: deBanked Funder Directory (HIGHEST QUALITY)
**URL:** `https://debanked.com/funder-lender-directory/`

Curated directory with company name, phone, website URL (often linking to partner/ISO signup pages), years on deBanked (quality signal), event badges. Yield: ~40-45 funders. $0 cost.

Browser console extraction:
```javascript
Array.from(document.querySelectorAll('article')).map(a => ({
  company: a.querySelector('h3')?.textContent?.trim() || '',
  phone: a.querySelector('p')?.textContent?.trim() || '',
  website: a.querySelector('a[href*="http"]')?.href || ''
}))
```

**⚠️ Dead deBanked pages:** `/brokers/`, `/lead-sources/`, `/smb-finance-rankings/`, `/mca-software-and-crms/` are all 404 or blog post redirects. Only `/funder-lender-directory/` is active.

### Tier 2: Google Maps by Hotspot ZIP (MEDIUM QUALITY, NO EMAILS)
Search for "merchant cash advance" or "business loans" in hotspot cities via ScraperCity Maps scraper ($0.01/listing).

**Confirmed yields (June 2026):** NY: 35, Miami: 43, LA: 34, Dallas: 50, Phoenix: 50, Chicago: ~30, Atlanta: ~28.

**⚠️ Maps returns ZERO emails** — always plan for separate enrichment. Vary query per city to avoid duplicates.

### Tier 3: Funder ISO Partner Pages (BROWSER MINING)
deBanked funder websites typically have `/partners`, `/iso`, or `/partner-with-us` pages listing their ISO network. High-effort manual browser work but yields Tier-1-target ISOs.

### Tier 4: Apify PipelineLabs — Keyword-Based (SCALE PLAY)
Actor `kVYdvNOefemtiDXO5` with `companyKeywordIncludes`. **$1 per 1,000 leads** — NOT the expensive Meta Ads actor.

MCA-optimized payload:
```python
{
    "companyKeywordIncludes": [
        "merchant cash advance", "business funding", "MCA",
        "revenue based financing", "business loans", "small business lending",
        "merchant funding", "business capital", "working capital"
    ],
    "hasEmail": True,
    "emailStatusIncludes": ["verified"],
    "personLocationCountryIncludes": ["United States"],
    "companySizeIncludes": ["1-10", "11-50", "51-200", "201-500"],
    "seniorityIncludes": ["owner", "c_suite", "partner", "director"],
    "totalResults": 10000
}
```

Post-filter: ~50% MCA relevance from keyword-based scraping. Each batch returns ~100 leads / ~20 unique companies. Rotate keyword combos across 5-10 batches for coverage (10 batches yielded 704 leads / 156 companies on June 15, 2026).

**⚠️ PipelineLabs emails are 90%+ INVALID.** Tested June 15: 10 "verified" PipelineLabs emails → 1 valid, 6 invalid, 3 unknown via ScraperCity. The `emailStatus: verified` field is cosmetic. PipelineLabs is a COMPANY DISCOVERY tool, not an email source. For emails, use ScraperCity Website Finder (when wallet allows) or direct website scraping. For phone numbers, use the direct scraping technique above (Tier 0).

**⚠️ PipelineLabs phone numbers are MASKED** (e.g., `+177****9822`) — compliance restriction. Do not rely on PipelineLabs for phone.

### Tier 5: SBA Lender Lists
`https://www.sba.gov/partners/lenders/microloan-program/list-lenders` — downloadable CSVs of authorized lenders.

### Tier 5: Meta Ad Library (BUDGET SIGNAL)

Companies running Facebook ads for MCA/business lending — signals ad budget + active marketing motion. Uses ScrapeCreators `facebook adlibrary-search-companies`.

**Keywords that work:** "merchant cash advance" → 15 results (Cash Advance Service, Loan Service categories). "business funding" → 15 results. "business loans" → 15 results. "small business loans" → 15 results. "MCA funding" → 4 results. "working capital advance" → 1 result.

**Limitation:** 15-result hard cap per query (API limitation). MCA is closer to a national vertical than local (like medspa) — geo-spraying by state may not multiply volume the way it does for HVAC. For volume, pair with PipelineLabs and direct website scraping.

**Profile enrichment:** `scrapecreators facebook profile` can pull website, email, and phone from Facebook pages at 1 credit each. Yield: ~20-30% for phone numbers, ~30-40% for emails. Example: Fundwise Capital Funding returned (509) 761-9097 and fundwisecapital7@gmail.com. Inconsistent — some pages return no contact data.

**Credit cost:** 1 credit per search + 1 credit per profile enrichment. 21,789 credit pool available as of June 2026.

## Blocked / Dead Sources

| Source | Issue | Workaround |
|--------|-------|-----------|
| **Daily Funder** | Cloudflare bot detection | None found |
| **SBFA** | "Not available yet" | No public member list |
| **ILPA** | ModSecurity block | Try browser with residential proxy |
| **Broker Fair sponsors** | JS-rendered in iframe | Try direct curl on iframe source |
| **BuiltWith Centrex** | Not in BuiltWith database | Skip ALL BuiltWith for MCA |
| **Bright Data** | Catalog not downloaded | Download catalog first |

## Tech Signals (Limited)

Centrex CRM (60%+ of established broker shops) is NOT tracked by BuiltWith. Other potential tech signals (LendSaaS, Velocity, FundKite, TurnKey Lender, LoanPro) are unverified. **Skip BuiltWith for MCA entirely.**

## Collection Pipeline

The most reliable path for phone numbers in this vertical is direct website scraping — not Maps, not PipelineLabs, not profile enrichment.

### TIER 0: Direct Website Phone Scraping (HIGHEST YIELD FOR PHONES)

**Finding (June 15, 2026):** 51% of MCA/business lending company websites have a phone number extractable via simple regex on the homepage or contact page. This outperforms every enrichment tool.

**Method:**
```python
import urllib.request, re, concurrent.futures

phone_re = re.compile(r'(?:(?:\+|00)1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}')

def extract_phone(domain):
    paths = ['', '/contact', '/contact-us', '/about', '/about-us']
    for path in paths:
        for proto in ['https', 'http']:
            try:
                url = f"{proto}://{domain}{path}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5, context=ssl_ctx) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')[:80000]
                text = re.sub(r'<[^>]+>', ' ', html)
                phones = phone_re.findall(text)
                real = [p for p in phones if len(re.sub(r'\D','',p)) == 10]
                for p in real:
                    idx = text.find(p)
                    ctx = text[max(0,idx-80):idx+len(p)+80].lower()
                    if not any(w in ctx for w in ['fax','tty','tdd']):
                        return p.strip()
            except: continue
    return None

# Run with ThreadPoolExecutor(max_workers=20) for 400+ domains in ~3 minutes
```

**Results (June 15, 2026):** 498 domains → 257 phone numbers (51%) in 3 minutes. Filter out obviously fake numbers (all-same-digit like 6666666667, leading 0 or 1 in area code).

**Context filtering:** Skip numbers near "fax", "tty", "tdd". Prefer numbers near "call", "phone", "contact", "sales", "support".

**Fallback paths:** Try `/contact`, `/contact-us`, `/about`, `/about-us`, `/contactus` if homepage yields nothing. Accept first valid phone on contact pages regardless of context words.

### Tier 1: deBanked Funder Directory (BEST QUALITY, CURATED)

## Pitfalls

1. **BuiltWith is useless for MCA.** Centrex and other industry CRMs aren't tracked. Confirmed June 15: "Centrex" → "Lookup failed".
2. **Maps returns no emails.** Always plan for a separate enrichment step.
3. **deBanked has many dead pages.** `/brokers/`, `/lead-sources/`, `/smb-finance-rankings/`, `/mca-software-and-crms/` are all 404 or blog redirects.
4. **Industry forums are heavily bot-protected.** Daily Funder (Cloudflare), ILPA (ModSecurity).
5. **SBFA has no public member list.** ("Not available yet")
6. **Funder partner pages are signup forms, not ISO directories.** Most funder `/partners` pages don't list existing ISOs publicly.
7. **PipelineLabs emails are 90%+ INVALID** even with `emailStatus: verified`. Do not trust. Confirmed June 15.
8. **PipelineLabs phone numbers are MASKED.** Don't rely on PipelineLabs for phone — use direct website scraping.
9. **Direct website phone scraping yields ~50%, not 100%.** Accept the hit rate; don't iterate endlessly on misses.
10. **Some scraped phone numbers are fake.** Factor funding returned 6666666667. Filter: reject all-same-digit numbers.
11. **Don't confuse Target A (ISOs/brokers) with Target B (funders).** Different pitches.
12. **Meta Ad Library 15-result cap applies to MCA.** Geographic spraying doesn't help — treat MCA as a national vertical.

## References

- `references/debanked-funder-directory.md` — Complete 41-funder extraction from deBanked (June 15, 2026): company names, phones, websites, partner page URLs, and year-joined data.