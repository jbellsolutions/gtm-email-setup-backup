---
name: b2b-lead-generation-platforms
description: "B2B lead generation platforms: ScrapeCreators (Facebook/Google Ad Library, Instagram, TikTok) for top-of-funnel discovery + ScraperCity (Google Maps, Yelp, email validation, Zillow, enrichment) for verification and enrichment. Both npm CLI tools under the same account. Core of the AI Integraterz cold email pipeline."
category: sales
tags: [lead-generation, cold-email, scrapecreators, scrapercity, ad-library, email-validation, b2b]
related_skills: [cold-email-personalized-agent, Instantly-cold-email, cold-email-weekly-rhythm]
triggers:
  - scrapecreators
  - scrapercity
  - scraper city
  - facebook ad library
  - google ad library
  - companies running ads
  - ad library search
  - lead generation
  - email validation
  - google maps scraper
  - zillow agents
  - yelp scraper
  - b2b leads
  - find companies running facebook ads
  - cold email lead sourcing
---

# B2B Lead Generation Platforms

Two complementary platforms for the AI Integraterz cold email pipeline. Both are npm CLI tools, both under `jbellsolutions@gmail.com`, both used in the same workflow — but they are **different platforms with different API keys**.

## Quick Decision: Which Tool When?

| Task | Tool | Why |
|------|------|-----|
| Find companies running Facebook ads by keyword/industry | **ScrapeCreators** | Only platform with Facebook Ad Library search |
| Find Google advertisers by keyword | **ScrapeCreators** | Google Ad Library advertiser search |
| Scrape Google Maps businesses by category + location | **Playwright headless** (fastest, free) or **Browser (built-in)** | Playwright: 7-10 results/search, runs in parallel. Browser: 5-8 results. ⛔ ScraperCity Maps is UNAVAILABLE (account cancelled, -$3.00 balance as of July 2026). |
| Validate email addresses (batch) | **ScraperCity** | $0.0036/email, batch up to 500. ⚠️ ScraperCity account cancelled — requires reactivation. |
| Find emails from company domain | **ScraperCity** | Website Finder, $0.05/domain. ⚠️ Account cancelled. |
| Find contacts from LinkedIn profile URLs | **ScraperCity** | Mobile/People/Email finders. ⚠️ Account cancelled. |
| Look up property owner data | **ScraperCity** | Property Lookup, $0.15/address. ⚠️ Account cancelled. |
| Scrape Yelp listings | ❌ Broken | ScraperCity Yelp scraper broken June 2026. No working alternative. |
| Scrape Zillow agents | ❌ Broken | ScraperCity Zillow scraper broken June 2026. No working alternative. |
| Get a company's active Facebook ads for personalization | **ScrapeCreators** | `facebook adlibrary-company-ads` |
| Enrich Facebook leads with website/email/phone | **ScrapeCreators** | `facebook profile` endpoint, 1 credit/profile |
| Scrape TikTok, Instagram, 25+ other platforms | **ScrapeCreators** | `scrapecreators list` for full platform list |
| Large-scale local business lead lists (1,000+) | **Browser Browser Use Cloud** | See [Browser-Based Google Maps](#browser-based-google-maps-scraping). For scale, use Browser Use Cloud SDK with parallel sessions. |

**Pipeline flow (current, July 2026):** ScrapeCreators (top-of-funnel discovery) → Browser Google Maps (local business scraping) → Instantly (outreach). ScraperCity is down — verification/enrichment unavailable until account reactivated.

---

## Shared Environment

Both tools are global npm packages installed under the same prefix:

```bash
# Binary location
/opt/data/home/.npm-global/bin/scrapecreators
/opt/data/home/.npm-global/bin/scrapercity

# Ensure PATH includes the global prefix
export PATH=/opt/data/home/.npm-global/bin:$PATH
```

### PATH Trap (critical — affects both tools)

Python `subprocess`, `xargs`, and `execute_code` do NOT inherit the npm global path. Always set PATH explicitly:

```python
import os, subprocess
env = {**os.environ, 'PATH': '/opt/data/home/.npm-global/bin:' + os.environ.get('PATH', '')}
subprocess.run(['scrapecreators', 'balance'], env=env)
```

Or use full binary paths: `/opt/data/home/.npm-global/bin/scrapecreators`.

### npm Global Install Failure

Both tools may fail global install with `EACCES: permission denied`. Fix:

```bash
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
export PATH=~/.npm-global/bin:$PATH
```

### Config is camelCase (both tools)

```
scrapecreators config set apiKey YOUR_KEY     # NOT api_key
scrapercity login YOUR_KEY                    # saves apiKey to ~/.scrapercityrc
```

---

## ⚠️ KEY CONFUSION TRAP (Critical — Read First)

**ScrapeCreators and ScraperCity use DIFFERENT API keys that look similar:**

| Platform | Key Format | Auth Header |
|----------|-----------|-------------|
| ScrapeCreators | `90c2ca64` (8-char short key) | `x-api-key` |
| ScraperCity | `90c2ca64-81bc-48ab-a6b2-980abfaea898` (UUID) | `Authorization: Bearer` |

**The trap:** Running `scrapercity login 90c2ca64` (the ScrapeCreators key) silently overwrites `~/.scrapercityrc` and breaks ALL ScraperCity operations with 401 errors. If ScraperCity auth suddenly fails, check the rc file — it probably got the wrong key.

**Canary:** `scrapercity wallet` failing with 401 = wrong key in `~/.scrapercityrc`. Re-login with the full UUID key.

---

## ScrapeCreators — Ad Library Search (Top of Funnel)

Discover companies actively running ads on Facebook, Google, Instagram, TikTok, and 25+ other platforms. The killer feature for cold email: **Facebook Ad Library company search** — find businesses spending on ads by keyword/industry.

### Authentication

```bash
scrapecreators config set apiKey 90c2ca64   # camelCase: apiKey (NOT api_key)
scrapecreators balance                       # verify
```

`scrapecreators auth login` is interactive — use `config set` instead.

### Core Commands

```bash
# Facebook Ad Library — find companies running ads
scrapecreators facebook adlibrary-search-companies --query "HVAC Florida" --pretty

# Get a company's active ads (for personalization research)
scrapecreators facebook adlibrary-company-ads --page-id 124580071063221 --pretty

# Google Ad Library — find advertisers (10-20x fewer results than Facebook)
scrapecreators google adlibrary-advertisers-search --query "HVAC Florida" --pretty

# List all platforms
scrapecreators list
```

### Facebook Ad Library: 15-Result Hard Cap

The API returns **max 15 results per query** — no pagination. To build lists of 200–300+ companies:
1. **Spray keyword × geo combos** — ~4 keyword variants across 15–20 states
2. **This ONLY works for LOCAL service businesses** (HVAC, roofing, plumbing) where companies have geographic page tags. For clinical/medical/national-brand keywords (TRT, botox, medspa), geographic spraying returns zero new after the first state — use [browser-based scraping](#browser-based-meta-ad-library-scraping-api-fallback).
3. **Deduplicate by `page_id`** — same company appears across multiple queries
4. **Credit economics**: ~100 credits = 250–350 unique companies after dedup

### Keywords That Work

| Vertical | Good Keywords | Bad (noisy) |
|----------|--------------|-------------|
| HVAC | `"HVAC {state}"`, `"air conditioning {state}"` | — |
| Men's Health | `"TRT clinic"` | `"TRT"` (Turkish media) |
| Med Spas | `"medspa"`, `"botox clinic"` | `"botox"` (cosmetics) |
| Weight Loss | `"semaglutide clinic"` | `"GLP-1"`, `"Ozempic"` (pharma news) |
| Behavioral Health | `"addiction treatment center"` | `"drug rehab"` (political ads) |

### Lead Enrichment via Profile Endpoint

The `facebook profile` endpoint pulls website, email, phone, and business description from Facebook — bypassing the login wall. **1 credit per profile. This is the primary enrichment path.**

```bash
scrapecreators facebook profile --url "https://facebook.com/FloridaFederalFHVAC" --pretty
```

Expected yield: ~60-80% have websites, ~20-40% have public email, ~50-70% have phone. See `references/profile-enrich.py` for batch enrichment.

### Direct API Access (Python, no curl on this VPS)

```python
import urllib.request, json

url = f"https://api.scrapecreators.com/v1/facebook/adLibrary/search/companies?query={urllib.request.quote(query)}"
req = urllib.request.Request(url, headers={
    "x-api-key": "90c2ca64",
    "accept": "application/json"
})
with urllib.request.urlopen(req, timeout=20) as resp:
    data = json.loads(resp.read().decode())
# Response: {"success": true, "searchResults": [...]}
# Field is searchResults, NOT data or results
```

### Google Ad Library Notes

- Capital `L` in API path: `/v1/google/adLibrary/advertisers/search` (not `adlibrary`)
- Yields 10-20x fewer than Facebook — expect 0-5 advertisers per query
- `"AC"` matches false positives (academies, barbers) — post-filter by HVAC terms
- Same company appears under different advertiser IDs — deduplicate by case-insensitive name

### Browser-Based Meta Ad Library Scraping (API Fallback)

When the API's 15-result cap is fatal (clinical/medical/national-brand keywords), use direct browser scraping. The public Ad Library shows real volumes: 3,500–50,000+ results per keyword.

**Approach priority (by cost):**
1. **Browser Use Cloud** ($29/mo) — hardened Chromium with anti-detect. Consistently bypasses Facebook detection. Primary for scale.
2. **Browserbase** (free tier) — fragile, blocks after 1-2 keywords. Fallback.
3. **❌ NEVER Apify** — `facebook-ads-scraper` burned $165 in 7 minutes with zero results (June 2026). User forbids it.

See `references/browser-scraping-advanced.md` for SDK code, batch extraction with exhaustion detection, and in-session keyword cycling. See `references/meta-ad-library-browser.md` for basic scroll/extraction recipes.

### Key Pitfalls

1. **15-result hard cap** — no pagination. Must spray keyword×geo combos for volume.
2. **Geographic spraying FAILS for non-local verticals** — clinical/medical keywords return same global 15 results regardless of state. Use browser scraping instead.
3. **API response field is `searchResults`, not `data`**.
4. **Residential proxies + headless Chrome = blocked by Facebook.** Only Browserbase's stealth browser reliably loads Meta Ad Library.
5. **Google Ad Library: capital `L`** — `/adLibrary/` not `/adlibrary/`.
6. **ScrapeCreators leads are NOT pre-verified** — only ~1.5% have any verification status. 32.3% were invalid when checked through ScraperCity. Always verify through ScraperCity `email-validate` before uploading to Instantly.
7. **For bulk sequential API calls, `execute_code` is faster than `delegate_task`** — 133-query sweep: 193s via execute_code vs 600s timeout in subagent.
8. **ScraperCity account CANCELLED (July 2026)** — balance -$3.00, plan "Cancelled". Maps, email validation, and all scrapers are unavailable. Use browser-based Google Maps scraping (see section above) for local business discovery.
9. **Google Maps browser scraping: 5-result "limited view"** — without Google sign-in, Maps shows only 5-8 results per search. Each click into a detail listing reveals full phone/website/address. To get 1,000+ leads, plan for 150-200 searches across category×location combos.
10. **Playwright headless WORKS on Google Maps** — returns 7-10 results per search with correct anti-detection config. See [Playwright Headless Google Maps Scraping](#playwright-headless-google-maps-scraping). The old wisdom that "Playwright fails" was from an incomplete config (missing `--disable-blink-features=AutomationControlled` and `navigator.webdriver` suppression).
11. **`read_file` corrupts Python source when writing back** — `read_file` prepends line numbers with `|` (e.g., `123|#!/usr/bin/env`). When content is then patched or written back, the prefixes merge into the source, producing SyntaxErrors like `1|     1|#!/usr/bin/env python3`. Fix: strip `^\s*\d+\|` with sed or use `write_file` with clean content. When editing Python scripts, prefer `execute_code` to write fresh content.
12. **`patch` with `replace_all=false` garbles variable names when the match is ambiguous** — if the old_string appears elsewhere in the file with different surrounding context, the replacement can produce corrupted code like `json.dump({...},esults}, f)`. Always use enough surrounding context for a unique match, and verify the diff after applying.
13. **Shell heredocs (`<< 'EOF'`) break on `&`** — the shell interprets unescaped `&` in heredoc content as background operators even inside quoted delimiters on some shells. When writing Python scripts inline via terminal, avoid category strings containing `&` (like `"Wellness & Recovery"`). Use commas or write files via `write_file` instead.

Full platform reference, scaling strategies, MCA/business lending keywords

---

## ScraperCity — Enrichment, Verification & Additional Scraping

B2B lead gen platform with 15+ scrapers: Google Maps, email validation, Yelp, Zillow agents, Airbnb, property lookup, and more.

### Authentication

```bash
# Option 1: env var (preferred for subprocess/scripts)
export SCRAPERCITY_API_KEY=90c2ca64-81bc-48ab-a6b2-980abfaea898

# Option 2: login (saves to ~/.scrapercityrc)
scrapercity login 90c2ca64-81bc-48ab-a6b2-980abfaea898

# Verify
scrapercity wallet    # Plan: Growth ($149.00/cycle)
```

### Core Pattern (all scrapers)

Every scraper follows: **submit → poll status → download CSV**

```
POST /api/v1/scrape/{slug}        → { runId }
GET  /api/v1/scrape/status/{runId} → { status, handled, outputUrl }
GET  /api/downloads/{runId}        → CSV file
```

**API base:** `https://app.scrapercity.com` | **Auth:** `Authorization: Bearer {key}` (NOT `x-api-key`)

### Key Scrapers (working)

| Scraper | CLI Example | Cost | Speed |
|---------|------------|------|-------|
| Google Maps | `scrapercity maps -q "plumbers" -l "Miami, FL"` | $0.01/place | 5-30 min |
| Email Validator | `scrapercity email-validate a@b.com c@d.com` | $0.0036/email | 1-10 min |
| Email Finder | `scrapercity email-find --first X --last Y --domain Z` | $0.05/contact | 1-10 min |
| Mobile Finder | `scrapercity mobile-find <linkedin/email>` | $0.25/input | 1-5 min |
| People Finder | `scrapercity people-find --name "X"` | $0.02/result | 2-10 min |
| Store Leads | `scrapercity store-leads --platform shopify` | $0.0039/lead | Instant |
| Website Finder | `scrapercity website-finder acme.com` | Per domain | 5-15 min |

### ⛔ Broken Endpoints (June 2026)

- **Zillow Agents** — all submissions: HTTP 500 `{"error":"Launch failed"}`
- **Yelp Scraper** — same 500 error
- **Download 502** — when `handled: 0`, download returns 502 instead of empty CSV

Server-side issues — not auth or credits. See `references/zillow-agents-outage.md`.

### Google Maps — Email Limitation (Critical)

**Maps returns ZERO emails. Always.** Confirmed across HVAC (200+), MCA/lending (350+), and legal verticals. Maps provides: name, address, phone, website, category, rating, reviews — but no email. Plan for downstream enrichment: Maps → extract domains → ScraperCity Website Finder → email-validate.

### Email Validation at Scale

- Cost: $0.0036/email
- Batch size: 500 emails (reliable), ~90s per batch
- `--file` flag is BROKEN — use `cat file | xargs` or direct args
- Company enrichment included at no extra cost
- Output: `valid`/`invalid` binary (no "risky" tier)

### Polling Pattern (do NOT use `scrapercity poll`)

The `poll` command hangs. Use manual status loop:

```python
import time, subprocess, os

env = {**os.environ, 'PATH': '/opt/data/home/.npm-global/bin:' + os.environ.get('PATH','')}

for i in range(40):  # 10 min max
    r = subprocess.run(['scrapercity', 'status', run_id], capture_output=True, text=True, env=env)
    if 'SUCCEEDED' in r.stdout:
        break
    if 'FAILED' in r.stdout or 'CANCELLED' in r.stdout:
        raise Exception(f"Run failed: {r.stdout}")
    time.sleep(15)
```

### Direct API (Python)

```python
import urllib.request, json

BASE = "https://app.scrapercity.com"
KEY = "90c2ca64-81bc-48ab-a6b2-980abfaea898"

def scrapercity_post(endpoint, body):
    url = f"{BASE}{endpoint}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "User-Agent": "scrapercity-cli/1.0"
    }, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())
```

### Key Pitfalls

1. **PATH trap** — `subprocess`/`xargs` don't inherit `/opt/data/home/.npm-global/bin`.
2. **`poll` hangs** — use manual status loop instead.
3. **`--file` flag broken** for `email-validate`.
4. **Auth is `Bearer`, not `x-api-key`** — different from ScrapeCreators.
5. **⚠️ KEY CONFUSION** — using ScrapeCreators key for ScraperCity silently breaks auth.
6. **Maps returns ZERO emails** — always needs separate enrichment.
7. **BuiltWith fails on niche tech** (Centrex CRM, etc.) — verify on builtwith.com first.
8. **Download 502 ≠ transient error** — means the data doesn't exist.

Full platform reference, all scrapers, error codes, MCP config, and batch Maps strategy in `references/scrapercity.md`.

---

## Pipeline Integration

The cold email lead generation flow:

```
ScrapeCreators (discovery)          ScraperCity (verification/enrichment)
─────────────────────────           ─────────────────────────────────────
adlibrary-search-companies ─┐
adlibrary-company-ads ──────┤       email-validate ────────┐
facebook profile ───────────┘       website-finder ────────┤
google adlibrary-search ────┐       maps (for directories) ┤
                              ├──→   email-find ────────────┤
                              │      mobile-find ───────────┤
                              │      people-find ───────────┘
                              │
                              └──→ Instantly (outreach)
```

**Critical workflow:** ScrapeCreators discovers leads → ScraperCity verifies emails → only verified leads go to Instantly. ScrapeCreators leads are **not pre-verified** (32.3% invalid in testing). Do NOT skip verification.

---

## Browser-Based Google Maps Scraping (ScraperCity Fallback)

**When ScraperCity Maps is unavailable (cancelled account, API issues), use the built-in browser** for Google Maps business scraping. This is the ONLY working approach for local business lead generation as of July 2026 — curl, Playwright headless, Apify, and DuckDuckGo ALL fail against Google's anti-bot measures.

### The Pattern That Works

```
browser_navigate → Google Maps search URL → browser_snapshot → parse sidebar results
```

**Search URL format:** `https://www.google.com/maps/search/<keyword>+<city>+<state>`

Each search returns **5-8 results** in the "limited view" sidebar (no sign-in required). The snapshot text is machine-readable with consistent structure:

```
- article
  - link "BUSINESS_NAME" [ref=eXX]
  - StaticText "BUSINESS_NAME"
  - image "4.9 stars"
  - generic
    - StaticText "CATEGORY  ADDRESS"
  - generic
    - StaticText "HOURS"
```

### Extractable Data (sidebar list view)

| Field | Source | Reliability |
|-------|--------|-------------|
| Business name | Link text | ✅ Always present |
| Rating | Image alt text ("4.9 stars") | ✅ Always present |
| Category | StaticText before address | ✅ Always present |
| Address (partial) | StaticText after category | ⚠️ Often truncated |
| Hours | StaticText ("Open · Closes 8 PM") | ⚠️ Sometimes missing |

### Getting Full Contact Data (detail view)

Click into a listing to open the detail panel, which reveals:

| Field | Example |
|-------|---------|
| Full address | "9616 Reisterstown Rd Ste 114, Owings Mills, MD 21117" |
| Phone | "(410) 363-2282" (from button aria-label or `tel:` link) |
| Website | "4lifecutzz03.booksy.com" (from "Website:" link) |
| Located in | "Phenix Salon Suites" (shopping center context) |
| Full hours | "Closed · Opens 11 AM · See more hours" |

### Scaling to Volume (1,000+ leads)

For large campaigns (100+ category×location combos):

1. **Sequential browser scraping:** ~20s per search = 30+ minutes for 100 combos. Viable for up to ~300 leads. Does NOT need any paid APIs.

2. **Browser Use Cloud SDK (recommended for 1,000+):** Use parallel sessions via the v3 SDK. Each session scrapes one category. 5 concurrent sessions × 20 searches each = ~8 minutes for 100 combos. Cost: ~$0.02/hr browser time + $5/GB proxy bandwidth.

3. **Apify Google Maps Scraper (if API key valid):** Actor `WnMxbsRLNbPeYL6ge` (google-maps-with-contact-details). One search string = 20+ results with full contact details. ⚠️ Requires valid Apify token — the env key was invalid as of July 2026.

### What Does NOT Work (July 2026)
| Approach | Result | Why |
|----------|--------|-----|
| curl + Google Maps | Zero results | JS-rendered, returns skeleton HTML (~50KB) |
| curl + Google Search local pack | Zero results | Bot detection, blocks all curl requests |
| curl + YellowPages | Cloudflare block | "Sorry, you have been blocked" |
| curl + DuckDuckGo local | Rate-limited after 1 query | Aggressive rate limiting |
| Playwright headless | ✅ Works | 7-10 results/search with anti-detection config. See [Playwright Headless](#playwright-headless-google-maps-scraping). |
| Apify API | Invalid token | Key `apify_api_7IYoLx...` returns "user-or-token-not-found" |
| ScraperCity Maps | Account cancelled | -$3.00 balance, plan "Cancelled" |
| Delegate subagents for scraping | Timeout | 18 API calls in 600s = too slow per search |

### Playwright Headless Google Maps Scraping

**Playwright headless WORKS** for Google Maps business scraping — 7-10 results per search — and is the fastest free approach for bulk lead generation (100+ category×location combos). The key is anti-detection config:

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(
        headless=True,
        executable_path='/opt/data/home/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome',
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
    )
    ctx = await browser.new_context(
        viewport={'width': 1280, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    )
    page = await ctx.new_page()
    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Search URL: https://www.google.com/maps/search/{query with + for spaces}
    await page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}", wait_until='domcontentloaded', timeout=30000)
    await page.wait_for_timeout(4000)  # Let results render

    # Extract from sidebar feed
    articles = await page.query_selector_all('[role="feed"] > div > div > a[href*="/maps/place/"]')
    if not articles:
        articles = await page.query_selector_all('a[href*="/maps/place/"][aria-label]')

    for a in articles[:20]:
        aria_label = await a.get_attribute('aria-label')
        text = (await a.text_content() or '').strip()
        parent_text = await a.evaluate('el => el.closest("[role=\\"article\\"], article")?.textContent || ""')
        full = parent_text if parent_text else text
        # Parse name, rating (regex: \d+\.?\d*\s*stars?), address, phone from `full`
```

**CSV fields extracted:** name, rating, category (empty — search query used instead), address, phone, link, source_search.

**Performance:** ~4-5 seconds per search. 88 searches = ~6 minutes for ~600-900 leads. Two instances can run in parallel on the same VPS without conflicts (separate state files).

**Resilience:** Save CSV + JSON state file after EACH search to survive interruptions. Resume by loading state file and skipping completed search keys.

**Pitfall:** `read_file` adds line-number prefixes that corrupt Python source when written back. Always strip `^\s*\d+\|` before writing. Use `write_file` with fresh content or sed to fix corrupted files.

Full working script: `scripts/gmaps_batch_scraper.py` (91 searches across 3 degrees of separation).

### Phone Number Extraction (browser_console)

Google's obfuscated DOM makes JS querySelector extraction unreliable. Instead, use regex on the snapshot text or the detail panel's text content:

```javascript
// From browser_console, extract phone from detail panel
const text = document.querySelector('[role="main"]')?.textContent || '';
const phoneMatch = text.match(/(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/);
// Returns: "(410) 363-2282"
```

### Data Extraction Efficiency Tips

1. **Parse snapshots in execute_code, not browser_console.** The snapshot text is reliable; DOM queries are not.
2. **Batch snapshot parsing.** Collect 10+ snapshots, then batch-parse all at once in execute_code with regex.
3. **Skip JS extraction for sidebar.** The snapshot already contains structured text — the article → link → StaticText pattern is consistent.
4. **Click into detail only for priority leads.** The detail view (phone, website, full address) requires a click per listing. Reserve this for Tier 1 prospects.

Full scraping script, search query lists by category, and snapshot parsing patterns in `references/google-maps-browser-scraping.md`.

---

## References

- `references/scrapecreators-cli.md` — Full ScrapeCreators platform reference: all commands, scaling strategies, MCA keywords, enrichment fallback chain, batch search patterns
- `references/scrapercity.md` — Full ScraperCity platform reference: all scrapers, error codes, MCP config, BuiltWith limitations
- `references/batch-search.md` — Python script for spraying keyword×geo combos, dedup strategy
- `references/comprehensive-sweep.md` — Two-tier nationwide sweep to bust 15-result API cap
- `references/enrichment.md` — Anymail Finder API and enrichment blockers
- `references/profile-enrich.py` — Batch profile enrichment script
- `references/meta-ad-library-browser.md` — Direct browser-based Meta Ad Library scraping
- `references/browser-scraping.md` — Browser scraping basics and blocking patterns
- `references/browser-scraping-advanced.md` — Browser Use Cloud SDK, batch extraction, keyword cycling
- `references/browserbase-blocking-pattern.md` — Browserbase blocking diagnosis
- `references/filter-noise-patterns.md` — Post-filtering noise from ad library results
- `references/batch-state-tracker.py` — Batch extraction state tracker
- `references/meta-extraction.js` — JavaScript extraction patterns for Meta Ad Library
- `references/playwright-stealth-failure-log.md` — Playwright stealth failure documentation
- `references/zillow-agents-outage.md` — Zillow agents outage debugging (June 2026)
- `references/google-maps-browser-scraping.md` — Browser-based Google Maps scraping: working patterns, failed approaches, scaling strategies for local business lead generation

## Scripts

- `scripts/gmaps_batch_scraper.py` — Batch 1: 91 searches across Degree 1-3 categories
- `scripts/gmaps_batch2_scraper.py` — Batch 2: 42 additional searches (home services, retail)
- `scripts/gmaps_batch3_scraper.py` — Batch 3: 25 supplemental searches (pharmacies, grocery, etc.)
- `scripts/google-batch-advertisers.py` — Batch Google Ad Library advertiser search
- `scripts/batch-maps-submit.mjs` — Batch Maps submission via Node.js module import
- `scripts/batch-maps-poll-merge.mjs` — Poll and merge batch Maps results