# ScrapeCreators CLI — Full Platform Reference

Scrape 27+ social media platforms via CLI. The killer feature for cold email: **Facebook Ad Library company search** — find businesses actively spending on ads by keyword/industry.

## Installation

```bash
npm install -g @scrapecreators/cli
```

**Pitfall:** Global install may fail with `EACCES: permission denied, mkdir '/usr/local/lib/node_modules'`. Fix by setting a user-level prefix:

```bash
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
export PATH=~/.npm-global/bin:$PATH  # for current session
```

Then retry the install. Remember to prefix all subsequent commands with `export PATH=~/.npm-global/bin:$PATH &&` if `~/.bashrc` hasn't been re-sourced.

## Authentication

**Pitfall:** `scrapecreators auth login` is interactive and prompts for the key — it does NOT accept `--api-key`. Use config instead:

```bash
scrapecreators config set apiKey 90c2ca64   # note: camelCase, not api_key
```

Verify:
```bash
scrapecreators balance
# or check: scrapecreators config get apiKey
```

## Key Commands for Cold Email Lead Sourcing

### Facebook Ad Library — Search Companies Running Ads

```bash
scrapecreators facebook adlibrary-search-companies --query "HVAC" --pretty
```

Returns: company name, page_id, category, likes, IG username/followers, verification status, page_alias.

### Get a Company's Active Ads

```bash
scrapecreators facebook adlibrary-company-ads --page-id 124580071063221 --pretty
```

Shows what ads a company is currently running — useful for personalization research.

### More Targeted Searches

Use longer, more specific queries for local service businesses:
```bash
scrapecreators facebook adlibrary-search-companies --query "HVAC repair Florida" --pretty
scrapecreators facebook adlibrary-search-companies --query "AC installation Phoenix" --pretty
```

### Google Ad Library — Search Advertisers

```bash
scrapecreators google adlibrary-advertisers-search --query "HVAC Florida" --pretty
```

Returns: advertiser name, advertiser_id, region, number_of_ads_estimate, and associated website domains.

**Sparse yield:** Google returns 0-5 advertisers per query — 10-20x fewer than Facebook. "air conditioning {city}" is the most productive keyword pattern. "HVAC {city}" yields 1-2. "AC repair", "furnace repair", and "HVAC contractor" return zero. The term "AC" alone matches false positives (academies, barber academies, pavers) — always post-filter by name.

**Get a company's ads (25 credits with details, 1 credit without):**
```bash
scrapecreators google company-ads --advertiser-id AR02669822194556600321 --get-ad-details true
```

Without `--get-ad-details true`, only advertiserId and creativeId are returned.

### Other Platforms Worth Using

```bash
scrapecreators list                    # list all platforms
scrapecreators instagram --help        # explore Instagram endpoints
scrapecreators tiktok --help           # explore TikTok endpoints
```

## Output Formats

```bash
--pretty       # pretty-printed JSON (default is compact JSON)
--format csv   # CSV output
--output hvac-leads.json  # save to file
--clean        # strip noisy fields
```

## Integration with Cold Email Pipeline

This tool feeds the top-of-funnel for `cold-email-personalized-agent`: use `adlibrary-search-companies` to find prospects actively running ads, then `adlibrary-company-ads` to research their messaging before writing personalized sequences.

**⚠️ Verification required:** Leads from ScrapeCreators (including the leads database) are NOT pre-verified. In testing (June 2026), only 1.5% had any verification status and 28% failed real verification. Always verify through ScraperCity `email-validate` — note that ScraperCity is a **separate platform** from ScrapeCreators (different CLI, different API base, different auth mechanism), but both use the same account. See `scrapercity.md` reference.

## Enrichment: Turning Leads into Contacts

### PRIMARY METHOD — Profile Enrichment via `facebook profile`

**This is the correct, reliable path.** The `facebook profile` endpoint pulls website, email, phone, and business description directly from Facebook — bypassing the login wall:

```bash
scrapecreators facebook profile --url "https://facebook.com/FloridaFederalFHVAC" --pretty
```

Returns: `website`, `email`, `phone`, `pageIntro` (business description), `rating`, `ratingCount`, `adLibrary.adStatus` (whether currently running ads), `creationDate`.

**Cost: 1 credit per profile.** A 300-company list costs ~300 credits. At 25,000 credits per $top-up, this is pennies per lead.

**URL format:** Use the `page_alias` from search results (e.g. `FloridaFederalFHVAC` → `https://facebook.com/FloridaFederalFHVAC`). Fall back to `https://facebook.com/{page_id}` if no alias.

**Batch enrichment:** Loop through all companies in your list, call profile endpoint for each, extract `website`/`email`/`phone`. See `references/profile-enrich.py` for the Python script.

**Expected yield:** ~60-80% of HVAC contractors have a website listed on their Facebook page. ~20-40% have a public email. ~50-70% have a phone.

### FALLBACK — Domain Guessing + Anymail Finder

When profile enrichment comes back empty, fall back to these approaches:

**Domain guessing** from company names has a **0-10% hit rate** for small local contractors (tested on 30 HVAC companies — 0 resolved). Most small contractors don't own `companyname.com`. Only use this as a last resort.

**Anymail Finder API** — `POST /v5.1/find-email/person` (see `references/enrichment.md` for full API details). Requires both domain AND full_name. Auth: `Authorization: Bearer {key}`. Pitfall: `v4.0` and `v5.0` both 404; only `v5.1` works.

### Blockers (Context)

Facebook `/about` pages and mbasic subdomain are login-walled. DDG Lite and Google search from VPS are CAPTCHA-blocked. Bing via browser doesn't surface small local businesses. The profile endpoint is the only reliable free path — everything else is a dead end for small contractors.

See `references/browser-scraping.md` for the browser-based alternative when the API's geo-spraying technique doesn't work (clinical/medical keywords).

## Scale Strategy: Building Large Lead Lists

The API returns **max 15 results per query** — no pagination, no `--limit` flag. This is a hard API cap, not a CLI limitation. To build lists of 200–300+ companies:

1. **Spray keyword × geo combos** — use ~4 keyword variants across 15–20 states
2. **⚠️ This only works for LOCAL service businesses** (HVAC, roofing, plumbing, contractors) where companies have geographic page tags. For clinical, medical, national-brand, and ecommerce keywords (TRT, botox, medspa, semaglutide, drug rehab), the API returns the same global 15 results for every state — spraying is a waste of credits. Use the browser approach instead: `references/meta-ad-library-browser.md`.
3. **Keywords that work**: `"HVAC {state}"`, `"air conditioning {state}"`, `"heating and cooling {state}"` — rich results. `"AC repair {state}"` returns fewer but different companies. `"furnace repair {state}"`, `"duct cleaning {state}"`, `"heat pump {state}"` for niche coverage.
4. **Deduplicate by `page_id`** — same company appears across multiple queries
5. **Credit economics**: Each search costs 1 credit. 100 credits ≈ 95–100 API calls ≈ 250–350 unique companies (after dedup). Budget ~$1 earned per batch of 100 credits.
6. **Rate limit**: 0.15s delay between calls is safe. No observed throttling.

### MCA / Business Lending Keywords (tested June 2026)

For financial services verticals, geographic spraying may not multiply volume (these are often national brands, not local service businesses). Keywords tested:

| Keyword | Results | Quality |
|---------|---------|---------|
| "merchant cash advance" | 15 | Cash Advance Service, Loan Service, Financial Service |
| "business funding" | 15 | Loan Service, Finance, Business Consultant |
| "MCA funding" | 4 | Financial Service — thin yield |
| "business loans" | 15 | Loan Service, Financial Service, Internet Company |
| "small business loans" | 15 | Loan Service, Financial Service |
| "working capital advance" | 1 | Internet Company — too narrow |

Categories to target: "Loan Service", "Financial Service", "Cash Advance Service", "Finance". Filter out: "Internet Company", "Website", "Brand", "Fan page", "Digital creator".

See `references/batch-search.md` for the Python script that does parallel state×keyword spraying with dedup.

## Browser-Based Meta Ad Library Scraping (API Fallback)

When the API's 15-result cap is fatal — clinical/medical/national-brand keywords where geographic spraying returns zero new after the first state — use direct browser scraping. The public Ad Library shows real volumes: 3,500–50,000+ results per keyword.

### Approach Priority (by cost)

1. **Browser Use Cloud** ($29/mo Dev plan) — hardened Chromium with anti-detect fingerprinting, US residential proxies. Consistently bypasses Facebook detection. Primary for scale. See `references/browser-scraping-advanced.md` for SDK code.
2. **Browserbase** (free tier) — fragile, blocks after 1-2 keywords. Fallback for quick single-keyword lookups.
3. **❌ NEVER Apify** — `facebook-ads-scraper` actor burned $165 in 7 minutes with zero saved results (June 2026).

### Batch Extraction with Exhaustion Detection

For production-grade multi-keyword scraping, use batch extraction with state tracking. Each batch scrolls 3 times then extracts. When 2 consecutive batches return the same count, the page is exhausted — move to the next keyword.

### In-Session Keyword Cycling

Instead of re-navigating for each keyword, reuse the same browser session: `browser_type` into search box, `browser_press Enter`, scroll to trigger, begin extraction. ~3x faster than per-keyword navigation.

### Keywords That Work (Non-Local Verticals)

| Vertical | Good Keywords | Bad Keywords (noisy) |
|---|---|---|
| Men's Health | "TRT clinic", "testosterone replacement clinic" | "TRT" (matches Turkish media) |
| Med Spas | "medspa", "botox clinic", "CoolSculpting clinic" | "botox" (cosmetic products, international) |
| Weight Loss | "semaglutide clinic", "weight loss clinic" | "GLP-1", "Ozempic" (pharma news) |
| Behavioral Health | "addiction treatment center", "drug rehab center" | "drug rehab" (political ads) |
| Home Improvement | "bath remodel contractor", "kitchen remodel contractor" | "bath remodel", "new roof" (generic) |

### Known Result Volumes

| Keyword | Claimed Results | Keyword | Claimed Results |
|---|---|---|---|
| TRT clinic | ~3,500 | botox | ~50,000+ |
| medspa | ~15,000 | semaglutide | ~10,000 |
| weight loss clinic | ~5,000 | drug rehab | ~36,000 |
| addiction treatment | ~20,000 | kitchen remodel | ~23,000 |
| solar installation | ~15,000 | window replacement | ~8,000 |

Full extraction JS, batch state tracker, Browser Use Cloud SDK patterns, and advanced pitfalls in `references/browser-scraping-advanced.md`. Basic scroll/extraction recipes in `references/meta-ad-library-browser.md` and `references/browser-scraping.md`.

## Direct API Access

When the CLI is insufficient, call the API directly:

```python
import urllib.request, json

url = f"https://api.scrapecreators.com/v1/facebook/adLibrary/search/companies?query={urllib.request.quote(query)}"
req = urllib.request.Request(url, headers={
    "x-api-key": api_key,
    "accept": "application/json"
})
with urllib.request.urlopen(req, timeout=20) as resp:
    data = json.loads(resp.read().decode())
```

No curl on this VPS — use `urllib.request` from Python.

## Full Pitfalls Reference

1. **npm global install fails with EACCES** — use the prefix workaround above.
2. **Config key is `apiKey` (camelCase)** — `api_key` will be rejected.
3. **`auth login` is interactive** — can't pipe the key. Use `config set apiKey` instead.
4. **Facebook results skew toward manufacturers/brands** with generic queries — use geographic or service-specific keywords (e.g., "AC repair Dallas" not just "HVAC") to surface local service companies.
5. **Credits are limited** — check `scrapecreators balance` before heavy usage. Each search consumes 1 credit. 402 Payment Required = out of credits.
6. **15-result hard cap per query** — no pagination in API or CLI. Must spray many combos to build volume. Plan for ~250–350 unique leads per 100 credits.
7. **Residential proxies + headless Chrome = blocked by Facebook.** Even with working residential proxies (Decodo/Smartproxy), Facebook detects and blocks headless Chrome, returning empty pages. Only Browserbase's stealth browser reliably loads the Meta Ad Library. Direct urllib through proxies works for API calls but Playwright/Puppeteer headless browsers are detected. See `references/browser-scraping.md`.
8. **Some geo+keyword combos return 0** — North Carolina and Ohio returned sparse results. Florida, Texas, California, Arizona, Alabama are richest. Certain keywords like "AC repair" return fewer hits than "HVAC" or "air conditioning".
9. **Google Ad Library API path has capital `L`** — it's `/v1/google/adLibrary/advertisers/search`, NOT `/v1/google/adlibrary/advertisers/search`. The lowercase variant returns 404 for every call. Always verify the exact path in the CLI source (`api-config/apis.js`) before writing direct API scripts.
10. **Google Ad Library yields 10-20x fewer results than Facebook** — expect 0-5 advertisers per query (not 15). Spraying 50+ queries may only produce 15-25 unique companies after dedup. For volume, Facebook remains the primary source; Google is supplemental for high-intent prospects.
11. **"AC" keyword matches false positives on Google** — "AC Florida" matched aviation academies, piano academies, barber academies, flooring, and pavers alongside HVAC companies. Post-filter results by checking company names against HVAC-specific terms: `["hvac", "air condition", "heating", "heat pump", "duct", "cooling"]`. Exclude names containing: `["academy", "flooring", "barber", "pavers", "aviation", "piano", "lifts"]`.
12. **⚠️ ScrapeCreators lead database emails are NOT pre-verified** — Only ~1.5% of leads from the ScrapeCreators database have any verification status. When 12,939 "verified" database leads were double-checked through ScraperCity (June 2026), **32.3% were invalid**. Always run every lead through ScraperCity `email-validate` before uploading to Instantly.
13. **⚠️ Google Ad Library returns same company under different advertiser IDs** — Deduplicate by case-insensitive company name in addition to `advertiser_id`, merging ad counts. GREEN SOLUTIONS SOLAR appeared under two IDs (31 and 22 ads). See `references/comprehensive-sweep.md`.
14. **For bulk sequential API calls, execute_code is faster than delegate_task** — A 133-query Google sweep timed out at 600s in a subagent but completed in 193s via direct execute_code. Subagent overhead is significant for workloads with sleep delays. Keep per-subagent workloads under ~100 queries. See `references/comprehensive-sweep.md`.
15. **Geographic spraying FAILS for non-local verticals** — The keyword×state spraying strategy ONLY works for LOCAL service businesses (HVAC, roofing, plumbing) where companies are geo-tagged. For clinical/medical/national-brand keywords (TRT, botox, medspa, semaglutide, drug rehab, CoolSculpting), the API returns the **same global 15 results regardless of state**. In testing (June 2026): 300 queries across 6 keywords × 50 states for "medspa" returned only 89 unique companies. After the first state query per keyword, all 49 subsequent states returned zero new. For these verticals, use browser-based scraping — it scrapes the Meta Ad Library directly via browser, bypassing the 15-result API cap entirely.
16. **Residential proxies + headless Chrome = blocked.** Facebook detects headless Chrome even through working residential proxies, returning empty pages. Only Browserbase's stealth browser reliably loads the Meta Ad Library.
17. **API response field is `searchResults`, not `data`** — Direct API calls to `/v1/facebook/adLibrary/search/companies` return `{"success": true, "credits_remaining": N, "searchResults": [...]}`. Each result has `page_id`, `page_name`, `category`, `image_uri`, `likes`, `page_alias`. Do not access `data.results` — that path returns empty.
18. **⚠️ NEVER use Apify for Meta Ad Library scraping** — The `apify/facebook-ads-scraper` actor is a documented cost trap (June 2026). The `startUrls` field is required, but the rate-limiting parameter (`maxAds`, `maxResults`) is silently ignored. The scraper pulls thousands of ads per keyword at $3.40/1,000 ads. A 4-vertical batch with 37 keywords burned $165 in 7 minutes with zero saved results. User explicitly forbids Apify. Always use ScrapeCreators API first (free), then Browserbase (free), never Apify.