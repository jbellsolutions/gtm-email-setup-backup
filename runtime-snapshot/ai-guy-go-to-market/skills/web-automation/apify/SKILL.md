---
name: apify
description: "Apify platform: search actors in the store, discover input schemas, run actors via API, fetch results. Platform-level skill for all Apify-based scraping and automation. Includes the AI Integraterz Job Scraper Pipeline (Indeed + LinkedIn scraping → DeepSeek scoring → contact enrichment → legacy email platform + Airtable sync)."
version: "1.0"
category: web-automation
triggers:
  - apify
  - apify actor
  - apify scraper
  - run actor
  - apify api
  - scrape with apify
---

# Apify

Platform operations for running Apify actors — searching the store, discovering input schemas, triggering runs, and fetching results. The Job Scraper Pipeline section below covers the full AI Integraterz pipeline built on top of Apify.

## Setup

- **API key:** `/opt/data/.env` → `APIFY_API_KEY`
- **Account:** jbellsolutions-owner (SCALE plan)
- **Auth:** `Authorization: Bearer $APIFY_API_KEY` for authenticated endpoints

### Authentication workflow and pitfall

Use the locally provisioned `APIFY_API_KEY` with direct HTTPS requests first. Do **not** route Apify through Composio or initiate an OAuth/token connection when a local key is available. Before attempting the requested operation, validate the key with `GET https://api.apify.com/v2/users/me`; a 401 means the stored key is invalid, expired, revoked, or for another account. Report that exact blocker rather than repeatedly retrying or asking the user to connect a different integration. Never print the full token in logs or responses.

For the direct-auth probe and the 401 handling recipe, see `references/direct-api-auth.md`.

## Searching for Actors

Search the public Apify Store without auth:

```python
import requests
resp = requests.get(
    "https://api.apify.com/v2/store",
    params={"search": "skool", "offset": 0, "limit": 20}
)
for item in resp.json()["data"]["items"]:
    print(f"{item['username']}/{item['name']}: {item['title']}")
```

Returns `name`, `username`, `title`, `description`, `stats.totalRuns`, `currentPricingInfo`.

**⚠ Do NOT use Bearer auth on store search** — returns 401. This endpoint is public.

## Getting Input Schema

**This is the non-obvious endpoint.** The input schema is NOT at `/v2/acts/{actorId}/input-schema` (404) and NOT embedded in the actor metadata from `/v2/acts/{actorId}`.

Correct endpoint:

```python
resp = requests.get(f"https://api.apify.com/v2/acts/{actor_id}/builds/default")
schema = resp.json()["data"]["inputSchema"]
# schema["properties"]  → input fields with types, descriptions, defaults
# schema["required"]    → list of required field names
# data["readme"]        → actor documentation
```

Actor IDs use format `username~name` (e.g., `memo23~skool-members-scraper`), not `username/name`.

## Running an Actor

```python
resp = requests.post(
    f"https://api.apify.com/v2/acts/{actor_id}/runs",
    headers={
        "Authorization": f"Bearer {apify_key}",
        "Content-Type": "application/json"
    },
    json={"input": {...}}
)
run = resp.json()["data"]
# run["id"]     → run ID for polling
# run["status"] → "READY" / "RUNNING" / "SUCCEEDED" / "FAILED"
```

## Retrieving and Combining Historical Lead Runs

When asked to assemble lists from a prior day, use the direct API and treat run selection as a classification task, not a blind export:

1. Compute the requested calendar-day UTC window explicitly using `startedAfter` and `startedBefore` on `GET /v2/actor-runs`.
2. Inspect every candidate run's actor ID, dataset, item count, search strings, categories, and run cost. Do not aggregate every run from the day or trust server ordering.
3. Classify lead-scrape runs from actual dataset fields. For Google Maps outputs, use `searchString`, `categoryName`, `categories`, and `leadsEnrichment`. Exclude unrelated campaigns.
4. Fetch each selected dataset with pagination until a page is shorter than the limit. Validate list versus nested `data.items` responses.
5. Deduplicate businesses by stable `placeId`, falling back to normalized company/address. Deduplicate contacts by normalized lowercase email.
6. Keep business records, enriched contacts, and verifier records separate. An email found by enrichment is not verified merely because it exists.
7. Match verifier output by normalized email. Treat only explicit `good`/valid status as verified. Keep `risky`/catch-all, `bad`/invalid, and missing email in the enrichment list.
8. Report scrape and verification costs separately, then the combined total. State whether verification spend is per submitted email/run rather than implying it is only for verified emails.
9. Deliver separate CSVs for each requested list and a separate enrichment CSV for each list; package multiple files in a ZIP.

For the Solar/Gyms run-selection and status-mapping lessons, see `references/historical-lead-runs.md`.

## Polling & Fetching Results

```python
# Check status
resp = requests.get(
    f"https://api.apify.com/v2/actor-runs/{run_id}",
    headers={"Authorization": f"Bearer {apify_key}"}
)

# Fetch dataset when SUCCEEDED
resp = requests.get(
    f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?format=json",
    headers={"Authorization": f"Bearer {apify_key}"}
)
items = resp.json()  # array of result objects
```

## Skool Actors

Common actors for Skool.com scraping. Full input schemas in `references/skool-actors.md`.

| Actor | Cost | Members | Emails | Needs Auth |
|-------|------|---------|--------|------------|
| `memo23/skool-members-scraper` | $0.02/member | ✅ Full profiles | ✅ (linked websites) | ✅ cookies |
| `crustapi/skool-community-scraper` | Per-result | ❌ | Owner only | ❌ |
| `gordian/skool-group-scraper` | Per-event | ❌ | Owner only | ❌ |

## Pitfalls

1. **Input schema endpoint**: `/v2/acts/{id}/input-schema` → 404. Use `/v2/acts/{id}/builds/default` → `data.inputSchema`.
2. **Skool members require cookies**: `memo23/skool-members-scraper` mandates a `cookies` array. Export from browser (EditThisCookie extension → copy JSON).
3. **Actor IDs use `~` not `/`**: `memo23~skool-members-scraper`, not `memo23/skool-members-scraper`.
4. **Store search + auth = 401**: Public endpoint, no Bearer header.

## Job Scraper Pipeline

The AI Integraterz job scraper pipeline is built on top of Apify actors. It scrapes Indeed + LinkedIn job listings, scores them with DeepSeek, enriches contacts, and syncs to legacy email platform + Airtable.

### Infrastructure

- **Repo:** `jbellsolutions/ai-integraterz-job-scraper` at `/tmp/ai-integraterz-job-scraper`
- **Target runtime:** Railway (auto-deploys on push to `main`). Health: `https://ai-integraterz-job-scraper.up.railway.app/health`
- **Current status:** Railway deployment unverified. Scheduler off by default (`ENABLE_EMBEDDED_SCHEDULER=false`). No leads ever scraped from production.
- **Scheduler:** Embedded APScheduler, daily 6 AM ET
- **LLM:** DeepSeek first priority, then OpenAI, then Anthropic
- **Database:** SQLite at `/tmp/ai-integraterz-job-scraper/backend/job_scraper.db`
- **Airtable sync:** Built-in at `backend/app/integrations/airtable_sync.py` — fires automatically after each pipeline run

### Pipeline Stages

1. **Ingestion** — Apify actors scrape Indeed + LinkedIn → `JobRaw` records
2. **Qualification** — DeepSeek scores each job (relevance + quality + recency). Score ≥60 → qualified
3. **Enrichment** — derive company domain → LinkedIn employees scraper → Claude ranks contacts → email discovery chain
4. **Outreach** — Generate email sequences via DeepSeek → sync to legacy email platform campaign
5. **Apply** — Queue apply tasks for non-email sources (Upwork, OnlineJobs)

### Start / Stop / Restart

```bash
pkill -f "uvicorn app.main:app" 2>/dev/null
cd /tmp/ai-integraterz-job-scraper/backend
rm job_scraper.db 2>/dev/null  # clean start
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Trigger manual run
curl -s -X POST http://localhost:8000/runs/daily -H "Content-Type: application/json" -d '{"trigger":"manual"}'

# Check status / health
curl -s http://localhost:8000/runs/1
curl -s http://localhost:8000/health
```

### Scraping Actor IDs

| Source | Actor ID | Key Input Params |
|---|---|---|
| **Indeed** | `hMvNSpz3JnHgl5jkh` (miscere/indeed-scraper) | `position`, `location`, `country`, `maxItems` |
| **LinkedIn** | `JkfTWxtpgfvcRQn3p` (worldunboxer/rapid-linkedin-scraper) | `position`, `location`, `rows` |

### Enrichment Actor IDs

| Actor | ID | Purpose | Required Params |
|---|---|---|---|
| **LinkedIn Employees Scraper** | `9Qmr7CUJ3fVH6bAmC` | Find employees at company | `companyUrls` (LinkedIn URLs, NOT names), `maxResults` |
| **Website Email & Phone Finder** | `mD5Xdfj9XeMS5FWPc` | Discover emails from domain | `domains` (array), `maxEmailsPerDomain` |
| **LinkedIn Profile Scraper** | `dev_fusion/Linkedin-Profile-Scraper` | Get email from profile URL | `profileUrls` (array), `maxItems` |
| **LinkedIn Profile Enrichment** | `AgfKk0sQQxkpQJ1Dt` (anchor/linkedin-profile-enrichment) | Enrich LinkedIn profiles | `profileUrls` (array) |
| **Leads Finder** | `heLL6fUofdPgRXZie` | Fallback email lookup | `companyName`, `contactName`, `maxItems` |

**Actor ID verification:** Actor IDs can go 404 if renamed or removed. Always verify against installed actors: `GET /v2/acts?token=...`. Known dead actor: `harvestapi/linkedin-profile-search` (404 on this account).

### Critical Pitfall: Connector Field Mapping

Apify actors return different field names than the code expects. When a connector maps 700 jobs but the DB shows 0-1 saved, the field mapping is wrong.

**LinkedIn actor returns:** `job_id`, `job_title`, `company_name`, `company_url`, `apply_url`, `job_url`, `job_description`, `location`, `salary_range`, `time_posted`

**Indeed actor returns:** `id`, `positionName` (NOT `position`), `company`, `externalApplyLink`, `url`, `description`, `location`, `salary`, `postingDateParsed`

The normalizer must read both: `raw.payload.get("company_name") or raw.payload.get("company") or raw.payload.get("companyName") or "Unknown company"`.

**How to discover actual field names:** Never guess. Either get the input schema (`GET /v2/acts/{actor_id}/builds/default` → `data.inputSchema`) or check raw payloads in the DB: `SELECT payload FROM jobraw WHERE source='linkedin' LIMIT 1`.

### Email Discovery Chain (priority order)

1. Email from LinkedIn employees scraper results
2. Website Email & Phone Finder (`mD5Xdfj9XeMS5FWPc`) from company domain
3. LinkedIn Profile Scraper (`dev_fusion/Linkedin-Profile-Profile-Scraper`) from profile URL
4. Leads Finder (`heLL6fUofdPgRXZie`) from company name + contact name

Generic emails (info@, contact@, hello@, support@, admin@, sales@, hr@, careers@, jobs@, hiring@) are rejected at every stage.

### Batch Enrichment Fallback

When pipeline enrichment fails (no LinkedIn URLs for Indeed jobs, no domains), use `/tmp/ai-integraterz-job-scraper/batch_enrich.py`:

```bash
cd /tmp/ai-integraterz-job-scraper
DEEPSEEK_API_KEY="$(grep DEEPSEEK_API_KEY backend/.env | cut -d= -f2)" python3 batch_enrich.py
```

Performance: 54% hit rate on Indeed leads. 113 companies → 61 emails in ~15 minutes.

### Airtable Sync

Integrated into the pipeline orchestrator. After each completed run, `sync_pipeline_run()` fires automatically.

**Config (env vars):**
```
AIRTABLE_PERSONAL_ACCESS_TOKEN=[REDACTED]
AIRTABLE_BASE_ID=[REDACTED]
AIRTABLE_ALL_JOBS_TABLE=[REDACTED]
AIRTABLE_QUALIFIED_TABLE=[REDACTED]
AIRTABLE_CONTACTED_TABLE=[REDACTED]
```

Standalone sync: `cd /tmp/ai-integraterz-job-scraper && AIRTABLE_PERSONAL_ACCESS_TOKEN=<token> AIRTABLE_BASE_ID=<base> python3 sync_to_airtable.py [run_id]`

### Pipeline Pitfalls

- **0 Qualified / 0 Stored despite high ingest count:** wrong field mapping → all jobs get same `external_id` → dedup collapses to 1 record
- **All "Hiring Team" contacts:** employees scraper actor ID wrong, or `companyUrls` not `companies`/`companyName`
- **All leads downgraded to `contact_needed`:** enrichment fails → query `status IN ('qualified', 'contact_needed')` to find all qualified leads
- **LinkedIn scraper 502 flakiness:** `JkfTWxtpgfvcRQn3p` frequently returns 502; Indeed-only still works
- **Database reset between test runs:** `rm /tmp/ai-integraterz-job-scraper/backend/job_scraper.db`
- **Company domain derivation:** LinkedIn `company_url` is a LinkedIn page, NOT the actual company website

### File Locations

| File | Purpose |
|---|---|
| `app/core/config.py` | Settings from env vars (actor IDs, API keys, Airtable config) |
| `app/integrations/sources/connectors.py` | Indeed/LinkedIn connector field mapping |
| `app/services/enrichment.py` | Company/contact enrichment, email discovery |
| `app/services/orchestrator.py` | Pipeline orchestration (all stages) |
| `app/integrations/claude_client.py` | LLM client (DeepSeek → OpenAI → Anthropic) |
| `app/integrations/apify_client.py` | Apify actor runner with polling |
| `backend/.env` / `.env.example` | Runtime config (API keys, scheduler, caps) |

### References

- `references/job-scraper-session-debug.md` — Session debugging notes: actor field samples, performance data, pipeline run stats
- `references/job-scraper-justin-communication.md` — Justin's communication preferences (direct answers, no unnecessary setup)
- `scripts/batch_enrich.py` — Batch processor for domain guessing + Apify email finding (fallback when pipeline enrichment fails)

## Quick Reference: Common Operations

```bash
# Search store
curl -s "https://api.apify.com/v2/store?search=skool&limit=10" | jq '.data.items[] | {name, username, title}'

# Get input schema (set APIFY_KEY and ACTOR_ID first)
curl -s "https://api.apify.com/v2/acts/$ACTOR_ID/builds/default" | jq '.data.inputSchema'

# Run actor
curl -s -X POST "https://api.apify.com/v2/acts/$ACTOR_ID/runs" \
  -H "Authorization: Bearer $APIFY_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {...}}' | jq '.data.id'

# Fetch results
curl -s "https://api.apify.com/v2/actor-runs/$RUN_ID/dataset/items?format=json" \
  -H "Authorization: Bearer $APIFY_KEY" | jq '.'
```