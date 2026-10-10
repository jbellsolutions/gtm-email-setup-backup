# Book Author Scraping — Session Provenance

**Date**: June 7, 2026
**Goal**: Scrape 5,000+ recently published book authors for podcast booking outreach (Business, Health, Law, Self-Help categories). $10 Decodo budget max.

## Results Summary

| Source | Authors | Cost | Notes |
|--------|---------|------|-------|
| **OpenLibrary API** | 5,889 | $0 | Direct HTTP, no proxy. Hit 5K in 3 subjects. |
| PRLog RSS | ~5-10 | $0.01 | Via Decodo proxy. Low volume, high quality. |
| Google Books API | 0 | $0 | 429 rate limited without API key |
| Amazon New Releases | 0 | $0 | Bot-protected through residential proxy |
| Goodreads | ~10 | $0 | Intermittent results, fragile |

## What Was Tried and Failed

### Google Books API
- Query: `subject:X`, `orderBy=newest`, `langRestrict=en`
- Result: 429 rate limit on ALL requests through Decodo residential proxy
- Retried with 2.5s delays — still 429
- Needs: Google API key for quota, OR direct HTTP without proxy

### Amazon New Releases
- URL: `https://www.amazon.com/gp/new-releases/books/{category_id}`
- Selectors: `div[data-asin]`, `.zg-item-immersion`, `a[href*="/dp/"]`
- Result: All selectors return 0 items through Decodo proxy (200 status, empty DOM)
- Amazon detects residential proxies and serves stripped pages
- Needs: Browser Use Cloud (Tier 1) with hardened Chromium

### Goodreads Genre Pages
- URL: `https://www.goodreads.com/genres/{genre}`
- Sometimes works (returned 3-6 books), sometimes empty page
- Decodo proxy: intermittent. Browserbase browser tool: works but fragile.
- Best selectors: `a.bookTitle` + `a.authorName`

### PRLog HTML Detail Pages
- Works but too slow — 1 request per author, ~30% yield of actual individual authors
- Most PRLog book releases are from publishers/companies, not individual authors
- RSS feed is faster but very limited (1 item in books tag)

## What Works (Production-Ready)

### OpenLibrary API
- Endpoint: `https://openlibrary.org/search.json`
- No auth, no rate limits, clean JSON
- 25 subjects × 10 pages × 100 books = massive scale
- Script: `sales/book-author-lead-scraping/scripts/openlibrary_mega_scrape.py`

### Decodo Proxy: What It's Good For
- Public RSS feeds (PRLog)
- Government databases, Craigslist, public directories
- Anything with NO anti-bot protection
- $2/GB, negligible cost for text-based scraping

### Decodo Proxy: What It's NOT Good For
- Google APIs (429)
- Amazon (empty responses)
- Goodreads (intermittent)
- Any site with even basic bot detection
