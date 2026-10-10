# Domain-to-Email Extraction Options

When a Google Maps or ScrapeCreators CSV has zero emails (common — maps data returns business name, phone, address, website, but no email), you need to extract emails from the domains/websites before verification and personalization can begin.

## The Problem Pattern

Google Maps data: 5,579 rows → 0 emails. 5,070 have websites (90.9%). 5,554 have phone numbers (99.6%). The `emails` column is empty for 100% of rows.

**Before proceeding to verification, always check:** does the CSV actually have an `emails` field with data? Run a quick count:
```python
import csv
with open('file.csv') as f:
    reader = csv.DictReader(f)
    with_email = sum(1 for row in reader if row.get('emails', '').strip())
print(f"{with_email}/{total} have emails")
```
If 0, switch to domain-to-email extraction.

---

## Option 1: Firecrawl

**Python SDK:** Installed on VPS (v4.23.0). No API key configured (commented out in `.env`).

### Key Methods
- `scrape_url(url)` — single page scrape (markdown, HTML, or structured)
- `extract(urls, schema)` — AI-powered structured extraction (find emails with a schema)
- `batch_scrape_urls(urls)` — batch processing for many domains
- `map_url(url)` — discover all URLs on a site (find contact pages)

### Pricing

| Plan | Pages/Credits | Monthly Cost | Fits 4,390 Domains? |
|------|--------------|--------------|---------------------|
| Free | 1,000 | $0 | No (~225 domains @ 2 pages each) |
| Hobby | 5,000 | $16/mo | No (~1,100 domains) |
| **Standard** | **100,000** | **$83/mo** | **Yes** (covers all ~8,780 pages) |
| Growth | 500,000 | $333/mo | Overkill |
| Scale | 1,000,000 | $599/mo | Overkill |

### Approach
Use `extract()` with a JSON schema targeting email addresses:
```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc_...")

result = app.extract(
    urls=["https://bendlawgroup.com", "https://shermanbusinesslaw.com"],
    prompt="Find all email addresses on these pages. Look for contact@, info@, attorney names with emails.",
    schema={
        "type": "object",
        "properties": {
            "emails": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All email addresses found"
            }
        }
    }
)
```

### Pros/Cons
- + AI-powered, handles obfuscated emails
- + Batch processing supported
- - LLM cost overlay on top of page credits
- - Requires signup + $83/mo commitment
- - Overkill for simple static law firm sites

---

## Option 2: Apify

**API key:** Configured in `.env` (`APIFY_API_KEY`). Several email-finder actors available.

### Top Actors for Domain → Email

| Actor | What It Does | Known Pricing |
|-------|-------------|---------------|
| `scraper-mind/website-email-phone-finder` | Takes website URLs, scrapes, returns emails + phones | Per-request |
| `snipercoder/bulk-decision-makers-email-finder` | Bulk B2B email finder by domain | **$0.80/1K emails** |
| `renzomacar/website-contact-finder` | Email & Contact Finder from websites | Per-request |
| `makework36/email-finder-scraper` | Website Email & Contact Finder | Per-request |

### Apify Platform Pricing
- Free: $5 credits/month
- Starter: $49/mo (100 compute units)
- Scale: $199/mo
- Plus actor-specific per-result fees

### Approach
Feed website URLs to a domain-scraper actor:
```python
import urllib.request, json

APIFY_KEY = "apify_api_..."
actor_id = "scraper-mind/website-email-phone-finder"

payload = {
    "startUrls": [
        {"url": "https://bendlawgroup.com"},
        {"url": "https://shermanbusinesslaw.com"}
    ]
}

url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_KEY}"
req = urllib.request.Request(url, data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"}, method='POST')
```

### Pros/Cons
- + API key already configured
- + Purpose-built scrapers (not AI overkill)
- + $0.80/1K emails for bulk actor is cheap (~$3.50 total for 4,390)
- + Pay-per-use, no monthly commitment
- - Actor quality varies by maintainer
- - Need to test individual actors for reliability

---

## Option 3: ScraperCity Website Finder

**CLI:** `scrapercity website-finder <domain>` | **MCP:** `mcp_scrapercity_scrape_website_finder`

### Cost
Per-domain (exact cost not yet verified — need test run). Same account as email validation ($149/mo Growth plan, 99% usage as of June 2026).

### Pros/Cons
- + Same account as email verification
- + Single-vendor pipeline (find + verify in one account)
- - Account nearly maxed out ($148/$149 used)
- - Per-domain costs add up fast at 4,390 domains

---

## Decision Guide

| Situation | Use |
|-----------|-----|
| Small batch (under 100 domains) | Firecrawl Free tier |
| Medium batch (100-1,000) | Apify `snipercoder` at $0.80/1K |
| Large batch (1,000+) | Apify `scraper-mind/website-email-phone-finder` |
| Budget-sensitive at scale | Apify at ~$3.50 for full 4,390 list |

**Recommendation:** Apify `scraper-mind/website-email-phone-finder`. Cheapest, purpose-built, no monthly commitment. Test with 10 domains first.

---

## Post-Extraction: Always Verify

After extracting emails from any source, run them through ScraperCity `email-validate` before uploading to Instantly. Domain-extracted emails have ~15-30% invalidity rate (generic inboxes, catch-alls, typos). Never upload unverified emails.
