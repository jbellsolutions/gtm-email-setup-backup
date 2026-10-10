---
name: job-scraper-pipeline
description: "AI Integraterz job scraper pipeline: Apify scraping → DeepSeek scoring → contact enrichment → legacy email platform + Airtable sync. Targets Railway deployment (not yet verified running)."
version: 1.1.0
author: jbellsolutions
metadata:
  hermes:
    tags: [Apify, Job Scraping, Pipeline, DeepSeek, LinkedIn, Indeed, Enrichment]
---

# Job Scraper Pipeline

Automated job lead generation pipeline. Scrapes Indeed + LinkedIn via Apify, scores with DeepSeek, finds decision-maker contacts, discovers emails, syncs to legacy email platform.

## Infrastructure

- **Repo:** `jbellsolutions/ai-integraterz-job-scraper` at `/tmp/ai-integraterz-job-scraper` (GitHub — needs to be made private)
- **Target runtime:** Railway (auto-deploys on push to `main`). Verify at `https://ai-integraterz-job-scraper.up.railway.app/health`
- **Current status:** Railway deployment unverified (health check times out May 2026). Scheduler off by default (`ENABLE_EMBEDDED_SCHEDULER=false`). No leads ever scraped from production.
- **Scheduler:** Embedded APScheduler, daily 6 AM ET (set `ENABLE_EMBEDDED_SCHEDULER=true` in Railway env vars)
- **LLM:** DeepSeek first priority (via `claude_client.py` `_call_deepseek`), then OpenAI, then Anthropic
- **Database:** SQLite at `/tmp/ai-integraterz-job-scraper/backend/job_scraper.db`
- **Airtable sync:** Built-in service at `backend/app/integrations/airtable_sync.py` — fires automatically after each pipeline run. Standalone script also at `sync_to_airtable.py`.

## Start / Stop / Restart

```bash
# Kill existing
pkill -f "uvicorn app.main:app" 2>/dev/null

# Start fresh
cd /tmp/ai-integraterz-job-scraper/backend
rm job_scraper.db 2>/dev/null  # clean start
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Trigger manual run
curl -s -X POST http://localhost:8000/runs/daily \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual"}'

# Check status
curl -s http://localhost:8000/runs/1

# Health
curl -s http://localhost:8000/health
```

## Pipeline Stages

1. **Ingestion** — Apify actors scrape Indeed + LinkedIn job listings → `JobRaw` records
2. **Qualification** — DeepSeek scores each job (relevance + quality + recency). Score ≥60 → qualified
3. **Enrichment** — For each qualified lead: derive company domain → LinkedIn employees scraper → Claude ranks contacts → email discovery (website finder → LinkedIn profile scraper → leads finder)
4. **Outreach** — Generate email sequences via DeepSeek → sync to legacy email platform campaign
5. **Apply** — Queue apply tasks for non-email sources (Upwork, OnlineJobs)

## Apify Actor Reference

All actor IDs must be verified against the user's installed actors (`GET /v2/acts?token=...`). For general Apify platform operations (store search, input schema discovery, running actors), see the `apify` skill.

### Scraping Actors

| Source | Actor ID | Input Params | Field Mapping (actor → connector) |
|---|---|---|---|
| **Indeed** | `hMvNSpz3JnHgl5jkh` (miscere/indeed-scraper) | `position`, `location`, `country`, `maxItems` | `positionName` → title, `id` → external_id, `company` → company_name, `description` → description |
| **LinkedIn** | `JkfTWxtpgfvcRQn3p` (worldunboxer/rapid-linkedin-scraper) | `position`, `location`, `rows` | `job_id` → external_id, `job_title` → title, `company_name` → company, `apply_url`/`job_url` → url, `job_description` → description |

### Enrichment Actors

| Actor | ID | Purpose | Required Params | Field Mapping |
|---|---|---|---|---|
| **LinkedIn Employees Scraper** | `9Qmr7CUJ3fVH6bAmC` | Find employees at company | `companyUrls` (LinkedIn URLs, **NOT** company names), `maxResults` | `name` → full_name, `link` → linkedin_url, `designation` → title |
| **Website Email & Phone Finder** | `mD5Xdfj9XeMS5FWPc` | Discover emails from domain | `domains` (array), `maxEmailsPerDomain` | `emails[]` → email strings |
| **LinkedIn Profile Scraper** | `dev_fusion/Linkedin-Profile-Scraper` | Get email from profile URL | `profileUrls` (array), `maxItems` | `email`/`workEmail`/`businessEmail` |
| **LinkedIn Profile Enrichment** | `AgfKk0sQQxkpQJ1Dt` (anchor/linkedin-profile-enrichment) | Enrich individual LinkedIn profile URLs | `profileUrls` (array) | `email`, `title`, `company`, `location` |
| **Leads Finder** | `heLL6fUofdPgRXZie` | Fallback email lookup | `companyName`, `contactName`, `maxItems` | `email`/`workEmail`/`businessEmail` |

**Actor ID verification**: Actor IDs can go 404 if renamed or removed. Always verify against the user's installed actors: `GET /v2/acts?token=...`. The actor `harvestapi/linkedin-profile-search` returns 404 — it's not installed and doesn't exist in this account. Use the alternatives above.

## Critical Pitfalls

### Connector Field Mapping (TOP PITFALL)
Apify actors return different field names than the code expects. When a connector maps 700 jobs but the DB shows 0-1 saved, the field mapping is wrong. Check a single raw payload:

```python
import sqlite3, json
conn = sqlite3.connect('job_scraper.db')
c = conn.cursor()
c.execute("SELECT payload FROM jobraw WHERE source='linkedin' LIMIT 1")
payload = json.loads(c.fetchone()[0])
print(sorted(payload.keys()))
```

**LinkedIn actor returns:** `job_id`, `job_title`, `company_name`, `company_url`, `apply_url`, `job_url`, `job_description`, `location`, `salary_range`, `time_posted`

**Indeed actor returns:** `id`, `positionName` (NOT `position`), `company`, `externalApplyLink`, `url`, `description`, `location`, `salary`, `postingDateParsed`

### The Normalizer Also Needs Updates

After fixing `_from_actor_item`, the orchestrator's `_normalize_and_qualify` must also read the new field names — it extracts `company_name` from `raw.payload`:

```python
company_name = (
    raw.payload.get("company_name")  # LinkedIn actor
    or raw.payload.get("company")     # Indeed actor
    or raw.payload.get("companyName") # legacy
    or "Unknown company"
)
```

### How to Discover Actual Field Names

**Never guess field names.** When a connector returns 0 stored jobs but the pipeline reports high ingest counts, the field mapping is wrong.

**First option — get the input schema directly (fastest):**
```python
# Apify input schemas live at builds/default, NOT /input-schema
resp = requests.get(f"https://api.apify.com/v2/acts/{actor_id}/builds/default")
schema = resp.json()["data"]["inputSchema"]
# schema["properties"] → all input fields with types and descriptions
```
See the `apify` skill for general platform operations (store search, input schema discovery, running actors).

**Second option — check raw payloads in the DB:**

```bash
# Option 1: Check raw payloads in the DB
cd /tmp/ai-integraterz-job-scraper/backend
python3 -c "
import sqlite3, json
conn = sqlite3.connect('job_scraper.db')
c = conn.cursor()
c.execute(\"SELECT payload FROM jobraw WHERE source='linkedin' LIMIT 1\")
payload = json.loads(c.fetchone()[0])
print('Keys:', list(payload.keys()))
for k, v in payload.items():
    print(f'  {k}: {str(v)[:80]}')
"

# Option 2: Test-run the actor with 1 result via Apify API
curl -s -X POST "https://api.apify.com/v2/acts/JkfTWxtpgfvcRQn3p/runs?token=$APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"position":"AI engineer","location":"United States","rows":1}'
# Poll until SUCCEEDED, then fetch dataset items
```

### Symptom: 0 Qualified / 0 Stored Despite High Ingest Count

Two causes:
1. **Wrong field mapping** → all jobs get same `external_id` → dedup collapses to 1 record → 0 leads scored
2. **Actor returns 404** → enrichment stage runs but produces `Hiring team` placeholders → all leads `contact_needed`

### LinkedIn Employees Scraper Parameters
The actor `9Qmr7CUJ3fVH6bAmC` requires `companyUrls` (LinkedIn company page URLs), NOT `companies` or `companyName`. Example:

```python
{"companyUrls": ["https://www.linkedin.com/company/mindrift-ai"], "maxResults": 5}
```

The LinkedIn scraper provides `company_url` in its payload — pass this through to the enrichment service.

### Company Domain Derivation
LinkedIn `company_url` is a LinkedIn page (e.g., `https://www.linkedin.com/company/mindrift-ai`), NOT the actual company website. For Indeed, only `companyIndeedUrl` (Indeed company page) is available. Without the real domain:
- `website-email-phone-finder` cannot work
- `_derive_domain` must look for `company_url` in direct_fields but recognize it as a LinkedIn URL
- The email discovery chain falls back to LinkedIn profile scraper + leads finder when no domain is available

### 700 Jobs → 0 Qualified
When `source_counts` shows jobs scraped but `qualified: 0` with no errors:
1. Check connector field mapping (above)
2. Check `_derive_domain` — are company domains None?
3. Check `categorize_role` — does it recognize the job titles?
4. Check audit events for hidden errors

### No Contacts / All "Hiring Team"
When all contacts show as "Hiring team" with "No LinkedIn contact candidates were returned":
1. Verify the employees scraper actor ID is correct in config (`linkedin_people_search_actor_id`)
2. Verify the actor params match what it expects (`companyUrls` vs `companies`)
3. Check that `company_url` is being passed through from the raw job payload

### All Leads Downgraded to `contact_needed`
The pipeline creates leads with `qualified` status during qualification, but enrichment downgrades them to `contact_needed` when contact finding or email discovery fails. After a run completes, query `status IN ('qualified', 'contact_needed')` to find all qualified leads — NOT just `status = 'qualified'`.

### LinkedIn Scraper 502 Flakiness
The LinkedIn actor `JkfTWxtpgfvcRQn3p` frequently returns 502 Bad Gateway from Apify's infrastructure. When this happens, Indeed-only scraping still works. Run batch enrichment (below) on the Indeed leads while waiting for LinkedIn to recover.

### Database Reset Between Test Runs
When iterating on fixes, delete the DB between runs to avoid stale data and dedup issues:
```bash
rm /tmp/ai-integraterz-job-scraper/backend/job_scraper.db
```

### Dead External Actor IDs
Apify actor IDs can go 404 if renamed or removed from the user's account. When enrichment produces zero contacts and logs show repeated 404s, the actor ID needs replacing. Check the user's installed actors via the Apify API: `GET /v2/acts?token=...` then verify the target actor exists before running the pipeline. Known dead actor: `harvestapi/linkedin-profile-search` (returns 404 on this account).

## Batch Enrichment Fallback

When the pipeline's enrichment stage can't find contacts (no LinkedIn URLs for Indeed jobs, no domains), use the batch processor at `/tmp/ai-integraterz-job-scraper/batch_enrich.py`. It:

1. Reads `contact_needed` leads from the DB
2. Guesses domains from company names (`Company Name Inc` → `companyname.com`)
3. Calls Apify `website-email-phone-finder` (`mD5Xdfj9XeMS5FWPc`) — ~7 seconds/domain
4. Filters out generic emails (info@, sales@, press@, careers@, etc.)
5. Optionally generates email sequences via DeepSeek
6. Updates DB contact records and lead status

```bash
cd /tmp/ai-integraterz-job-scraper
DEEPSEEK_API_KEY="$(grep DEEPSEEK_API_KEY backend/.env | cut -d= -f2)" \
  python3 batch_enrich.py
```

**Performance**: 54% hit rate on Indeed leads. 113 companies → 61 emails in ~15 minutes.

### DeepSeek Integration
DeepSeek is first priority in `claude_client.py` `_call()`. Uses `httpx.AsyncClient` to post to `https://api.deepseek.com/v1/chat/completions`. Model: `deepseek-chat`. Temperature: 0.3. Timeout: 60s.

## Enrichment Email Discovery Chain

Priority order in `find_best_contact()`:
1. Primary search — email from LinkedIn employees scraper results
2. Fallback 0 — Website Email & Phone Finder (`mD5Xdfj9XeMS5FWPc`) from company domain
3. Fallback 1 — LinkedIn Profile Scraper (`dev_fusion/Linkedin-Profile-Scraper`) from profile URL
4. Fallback 2 — Leads Finder (`heLL6fUofdPgRXZie`) from company name + contact name

Generic emails (info@, contact@, hello@, support@, admin@, sales@, hr@, careers@, jobs@, hiring@) are rejected at every stage.

**Firecrawl is optional**: `enrich_company()` works without Firecrawl — it derives the domain from job payload data and uses Claude + funding intel for company research. No `FIRECRAWL_API_KEY` needed.

## Airtable Sync

Airtable sync is integrated into the pipeline orchestrator. After each completed run, `sync_pipeline_run()` fires automatically.

**Service:** `backend/app/integrations/airtable_sync.py` — async function called from `orchestrator.py` `run_daily()`

**Configuration (env vars):**
```
AIRTABLE_PERSONAL_ACCESS_TOKEN=[REDACTED]
AIRTABLE_BASE_ID=[REDACTED]
AIRTABLE_ALL_JOBS_TABLE=[REDACTED]
AIRTABLE_QUALIFIED_TABLE=[REDACTED]
AIRTABLE_CONTACTED_TABLE=[REDACTED]
```

**Base:** `[REDACTED]` — Recruitment Master 2026 Clean
**PAT:** `[REDACTED]`

Standalone sync script also at `sync_to_airtable.py` for manual runs:
```bash
cd /tmp/ai-integraterz-job-scraper && AIRTABLE_PERSONAL_ACCESS_TOKEN=<token> AIRTABLE_BASE_ID=<base> python3 sync_to_airtable.py [run_id]
```

## References

- `references/justin-communication.md` — Justin's communication preferences (direct answers, no unnecessary setup)
- `references/session-debug-2026-05-04.md` — Session debugging notes: actor field samples, performance data, pipeline run stats

## Scripts

- `scripts/batch_enrich.py` — Batch processor for domain guessing + Apify email finding (fallback when pipeline enrichment fails)


## File Locations

| File | Purpose |
|---|---|
| `app/core/config.py` | Settings from env vars (actor IDs, API keys, Airtable config) |
| `app/integrations/sources/connectors.py` | Indeed/LinkedIn connector field mapping |
| `app/services/enrichment.py` | Company/contact enrichment, email discovery |
| `app/services/orchestrator.py` | Pipeline orchestration (all stages) |
| `app/integrations/claude_client.py` | LLM client (DeepSeek → OpenAI → Anthropic) |
| `app/integrations/apify_client.py` | Apify actor runner with polling |
| `backend/.env` / `.env.example` | Runtime config (API keys, scheduler, caps). `.env.example` at repo root documents all 40+ vars. |
