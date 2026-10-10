# ScraperCity — Full Platform Reference

ScraperCity is a B2B lead generation platform with 15+ scrapers: Zillow agents, Google Maps businesses, Yelp listings, email validation, Airbnb hosts, and more. It is a **separate platform from ScrapeCreators** with different API keys and auth mechanisms.

## Installation & Setup

```bash
npm install -g scrapercity@1.0.4
# Binary: /opt/data/home/.npm-global/bin/scrapercity
```

**Auth — two options, either works:**
```bash
scrapercity login 90c2ca64-81bc-48ab-a6b2-980abfaea898   # saves to ~/.scrapercityrc (camelCase: apiKey)
export SCRAPERCITY_API_KEY=90c2ca64-81bc-48ab-a6b2-980abfaea898  # env var (preferred for subprocess)
```

**Verify:**
```bash
export PATH=/opt/data/home/.npm-global/bin:$PATH
scrapercity wallet
# Plan: Growth ($149.00/cycle), renews monthly
```

**⚠️ PATH trap:** Python `subprocess` and `xargs` do NOT inherit the npm global path. Always set `PATH=/opt/data/home/.npm-global/bin:$PATH` in the environment, or use the full binary path: `/opt/data/home/.npm-global/bin/scrapercity`.

## API Reference

**Base URL:** `https://app.scrapercity.com`
**Auth header:** `Authorization: Bearer {api_key}` (NOT `x-api-key`)

### Core Pattern (all scrapers)

Every scraper follows: **submit → poll status → download CSV**

```
POST /api/v1/scrape/{slug}        → { runId }
GET  /api/v1/scrape/status/{runId} → { status, handled, outputUrl }
GET  /api/downloads/{runId}        → CSV file
```

**Direct API via Python:**
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

def scrapercity_status(run_id):
    url = f"{BASE}/api/v1/scrape/status/{run_id}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())
```

**Direct API via Node.js (module import — best for debugging):**
```javascript
const { zillowAgents, status, download, wallet } = await import(
  '/opt/data/home/.npm-global/lib/node_modules/scrapercity/lib/client.mjs'
);
const result = await zillowAgents('Miami, FL', { searchLimit: 10 });
```

## All Scrapers

| Scraper | Slug | CLI Example | Cost | Speed | Status |
|---------|------|------------|------|-------|--------|
| Google Maps | `maps` | `scrapercity maps -q "plumbers" -l "Miami, FL"` | $0.01/place | 5-30 min | ✅ |
| Email Validator | `email-validator` | `scrapercity email-validate a@b.com c@d.com` | $0.0036/email | 1-10 min | ✅ |
| Email Finder | `email-finder` | `scrapercity email-find --first X --last Y --domain Z` | $0.05/contact | 1-10 min | ✅ |
| Mobile Finder | `mobile-finder` | `scrapercity mobile-find <linkedin/email>` | $0.25/input | 1-5 min | ✅ |
| People Finder | `people-finder` | `scrapercity people-find --name "X"` | $0.02/result | 2-10 min | ✅ |
| Store Leads | `store-leads` | `scrapercity store-leads --platform shopify` | $0.0039/lead | Instant | ✅ |
| BuiltWith | `builtwith` | `scrapercity builtwith "React"` | $4.99 flat | 1-5 min | ✅ |
| Criminal Records | `criminal-records` | `scrapercity criminal --name "X"` | $1.00 if found | 2-5 min | ✅ |
| Airbnb Email | `airbnb-email` | `scrapercity airbnb --city "Miami, FL"` | $0.0001/listing | 10-30 min | ✅ |
| YouTube Email | `youtube-email` | `scrapercity youtube-email @Channel` | Per channel | 5-15 min | ✅ |
| Website Finder | `website-finder` | `scrapercity website-finder acme.com` | Per domain | 5-15 min | ✅ |
| Angi | `angi-angies-list-scraper` | `scrapercity angi -q "plumbers" --zips 33101` | $0.01/listing | 5-15 min | ✅ |
| BizBuySell | `bizbuysell-scraper` | `scrapercity bizbuysell <url>` | $0.01/listing | 5-15 min | ✅ |
| Crexi | `crexi-scraper` | `scrapercity crexi <url>` | $0.029/listing | 5-15 min | ✅ |
| Property Lookup | `property-lookup` | `scrapercity property-lookup "123 Main St"` | $0.15/address | 2-10 min | ✅ |
| Apollo | `apollo` | `scrapercity apollo <url> --count N` | $0.0039/lead | ~4 days | ✅ |
| **Zillow Agents** | `zillow-agents` | `scrapercity zillow-agents -l "Denver, CO"` | Per agent | 5-15 min | ❌ BROKEN |
| **Yelp** | `yelp-scraper` | `scrapercity yelp -q "plumbers" -l "Miami, FL"` | $0.01/listing | 5-15 min | ❌ BROKEN |

### Google Maps — Email Limitation (Critical)

**Maps returns ZERO emails.** Confirmed across HVAC (200+) and MCA/lending (350+) listings. The `emails` field is empty for 100% of results. Maps provides: business name, address, phone, website, category, reviews, rating. Plan for downstream enrichment: Maps → extract domains → ScraperCity Website Finder → email-validate.

### BuiltWith — "Centrex" Failure

BuiltWith does NOT track Centrex CRM (MCA broker CRM). ScraperCity BuiltWith returned "Lookup failed." For industry-specific tech signals, BuiltWith is unreliable — verify the tech exists in their database before running paid scrapes.

### ⛔ Broken Endpoints (June 2, 2026)

- **Zillow Agents** — All submissions: HTTP 500 `{"error":"Launch failed"}`. Server-side issue.
- **Yelp Scraper** — Same 500 error.
- **Download 502** — When `handled: 0`, download returns 502 instead of empty CSV.

See `references/zillow-agents-outage.md` for full debugging transcript.

### Batch Maps Submission

For large-scale Maps scraping, use Node.js module imports — CLI too slow for sequential batch calls:

```javascript
import { maps } from '/opt/data/home/.npm-global/lib/node_modules/scrapercity/lib/client.mjs';
for (const city of cities) {
  const r = await maps('real estate agent', city, 10);
  await new Promise(r => setTimeout(r, 200));
}
```

Cost: `cities × limit × $0.01`. See `scripts/batch-maps-submit.mjs`.

## Operational Commands

```bash
scrapercity wallet                        # balance + plan info
scrapercity status <runId>                # check run progress
scrapercity download <runId>              # save CSV to CWD
scrapercity cancel <runId>                # cancel running scrape
scrapercity runs --hours 24               # recent runs (may return 500 intermittently)
```

### Polling Pattern (do NOT use `scrapercity poll`)

The `poll` command hangs. Use status polling:
```python
import time, subprocess, os
env = {**os.environ, 'PATH': '/opt/data/home/.npm-global/bin:' + os.environ.get('PATH','')}
for i in range(40):
    r = subprocess.run(['scrapercity', 'status', run_id], capture_output=True, text=True, env=env)
    if 'SUCCEEDED' in r.stdout: break
    if 'FAILED' in r.stdout or 'CANCELLED' in r.stdout: raise Exception(f"Failed: {r.stdout}")
    time.sleep(15)
```

## Status Values

`RUNNING` → `SUCCEEDED` or `FAILED` or `CANCELLED`

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Bad or missing API key |
| 402 | Insufficient balance |
| 403 | Account cancelled / charge processing |
| 409 | Duplicate request |
| 429 | Rate limited / duplicate within 30s |
| 500 | Server error / scraper broken upstream |
| 502 | Download unavailable (empty results) |
| 503 | Service temporarily unavailable |

## Relationship to ScrapeCreators

Same account (`jbellsolutions@gmail.com`), **different API keys**:
- **ScraperCity:** `90c2ca64-81bc-48ab-a6b2-980abfaea898` (UUID), `Authorization: Bearer`
- **ScrapeCreators:** `90c2ca64` (short key), `x-api-key`

Running `scrapercity login 90c2ca64` (the wrong key) silently breaks auth. Wallet check is the canary.

## Full Pitfalls

1. **PATH trap** — `subprocess`/`xargs` don't inherit npm global path.
2. **`poll` hangs** — use manual status loop instead.
3. **`--file` flag broken** for `email-validate`.
4. **Config key is `apiKey` (camelCase)** in `~/.scrapercityrc`.
5. **Zillow Agents and Yelp broken** (June 2026) — all submissions 500.
6. **Download 502** when 0 results — data doesn't exist.
7. **`scrapercity runs` returns intermittent 500**.
8. **Auth is `Bearer`, not `x-api-key`**.
9. **⚠️ KEY CONFUSION TRAP** — wrong key silently breaks auth.
10. **⚠️ Maps returns ZERO emails** — always needs enrichment.
11. **⚠️ BuiltWith fails silently on niche tech.**
12. **BuiltWith doesn't charge on "Lookup failed"** (confirmed June 2026).

## MCP Server Config

```yaml
scrapercity:
  command: npx
  args: [-y, --package, scrapercity, scrapercity-mcp]
  env:
    SCRAPERCITY_API_KEY: 90c2ca64-81bc-48ab-a6b2-980abfaea898
  timeout: 120
```