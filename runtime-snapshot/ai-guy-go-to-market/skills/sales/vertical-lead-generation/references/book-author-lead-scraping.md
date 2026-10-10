# Book Author Lead Scraping (Full Reference)

Scrape recently published book authors across Business, Health, Law, Self-Help, and adjacent categories. Target: authors who just launched a book and are actively seeking exposure — ideal for podcast/guest booking outreach.

## Source Strategy (ranked by effectiveness)

### Tier 1: OpenLibrary API (PRIMARY)
- **URL**: `https://openlibrary.org/search.json`
- **Params**: `subject=X`, `sort=new`, `limit=100`, `page=N`, `language=eng`
- **No auth required, no rate limits, clean JSON**
- Returns author_name[], title, first_publish_year, subjects
- 25+ subjects × 10 pages × 100 results = 25K potential authors
- **Always use this first** — it hit 5,889 unique authors in 3 subjects (business, management, leadership) in under 60 seconds

### Tier 2: PRLog RSS Feeds (via Decodo proxy)
- `https://www.prlog.org/news/tag/books/rss.xml`
- `https://www.prlog.org/news/tag/author/rss.xml`
- Parse XML with `xml.etree.ElementTree`, extract author via regex from title+description
- Low yield (~5-10 authors per feed) but high quality — these are active promoters
- Requires Decodo residential proxy ($2/GB)

### Tier 3: Goodreads Genre Pages
- `https://www.goodreads.com/genres/business` etc.
- Inconsistent — sometimes returns data, sometimes empty page
- Use BeautifulSoup with selectors: `a.bookTitle`, `a.authorName`
- Best when accessed via Browserbase browser tool, not raw requests

### Tier 4: PRLog HTML Pages (deprecated)
- Too slow (1 page per author), low yield of individual authors vs publishers

## Failed Sources (do not retry without new approach)

| Source | Issue |
|--------|-------|
| **Google Books API** | 429 rate limit without API key. Residential proxies make it worse. |
| **Amazon New Releases** | Bot-protected. Empty results through Decodo residential proxy. |
| **PRNewswire** | Search URL format changed — 404 on keyword searches |
| **Decodo → Google/Amazon/Goodreads** | Residential proxies trigger anti-bot on major platforms. |

## Extraction Pattern

```python
import requests, re

def add_author(all_results, seen, source, author, title, cat='', date='', url=''):
    if not author or not title: return False
    author = re.sub(r'\s+', ' ', str(author).strip())
    title = re.sub(r'\s+', ' ', str(title).strip())
    if len(author) < 3 or len(title) < 5: return False
    key = (author.lower()[:40], title.lower()[:60])
    if key in seen: return False
    seen.add(key)
    all_results.append({...})
    return True
```

## Output Schema

| Field | Description |
|-------|-------------|
| source | OpenLibrary, PRLog, Goodreads |
| author | Author name |
| book_title | Book title |
| category | Subject/genre tags |
| date | Publication year or press release date |
| url | Source URL |

## Pitfalls

1. **Google Books API 429** — API key gives 1,000 queries/day but without one, rate limit is brutal. Don't use without key.
2. **Amazon blocks residential proxies** — `div[data-asin]` selectors return zero items through Decodo.
3. **PRLog RSS is single-item** — The books RSS feed returns only 1 item. HTML listing is more comprehensive but slower.
4. **Goodreads intermittent** — Sometimes returns empty page through requests.
5. **OpenLibrary `sort=new` means recently added to catalog, not recently published** — cross-reference `first_publish_year`.
6. **Author name dedup is essential** — use (author[:40], title[:60]) as dedup key.

## Budget

Decodo proxy cost for PRLog RSS only: ~$0.01 per run (negligible). OpenLibrary is free and direct HTTP. Total author scraping budget is effectively $0 for any scale.

## Scripts

- `scripts/openlibrary_mega_scrape.py` — Proven standalone scraper. 5K+ authors in <60s. Run with `--limit 5000 --output /tmp/authors.csv`.