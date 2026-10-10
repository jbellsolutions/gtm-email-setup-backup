---
name: smart-prospect-pipeline
description: "End-to-end pipeline: pull leads from legacy email platform Prospector → auto-verify → research + Charm Offensive / framework-based custom emails → create campaign → upload → test. Use when the user wants to pull a list from Smart Prospect, create personalized cold emails, and push to a legacy email platform campaign."
version: 1.0.0
metadata:
  hermes:
    tags: [legacy email platform, Cold Email, Prospector, Sales, Outreach, Pipeline]
    related_skills: [legacy email platform-cold-email, cold-email-personalized-agent, charm-cold-email, charm-offensive-foundation, verify-leads]
prerequisites:
  env_vars: [legacy email platform_API_KEY]
  commands: [legacy email platform]
---

# Smart Prospect → Campaign Pipeline

End-to-end pipeline that pulls leads from legacy email platform Prospector (Smart Prospect), verifies them natively, researches each lead, creates personalized emails using Charm Offensive or framework-based approaches, and pushes everything to a legacy email platform campaign.

## When to Use

- User says "pull leads from Smart Prospect"
- User wants to source leads from Prospector and create a campaign
- User asks to go from Smart Prospect → verified list → personalized emails → campaign

## Prerequisites

- legacy email platform CLI installed at `/opt/data/home/.local/bin/legacy email platform`
- `legacy email platform_API_KEY` in environment
- legacy email platform Prospector subscription (required for fetch — consumes credits)
- For Charm Offensive emails: `charm-profile.md` must exist or be created

## ⚠️ Step 0: Validate Prospector Coverage (BEFORE committing credits)

**legacy email platform Prospector's email database has extremely uneven coverage by sub-industry.** Some niches get 73% verified-email rates (Staffing & Recruiting: 1,047/1,434). Others get **zero emails out of 50 contacts** (Renewables & Environment: 0/50). Keyword matching is also loose — "med spa" returns pool companies, "men's health" returns pharma software firms.

**Before committing any credits, validate coverage:**

1. **Run a free search** with the target filters and check relevance of results (Step 1b below)
2. **Check existing fetched searches** (`legacy email platform prospect fetched-searches`) — if a similar niche was previously fetched and has high email coverage, it's safe. If it shows 0 emails or very low email rates, the niche is poorly covered
3. **If coverage looks poor** (irrelevant search results OR prior fetches show <10% email rate), switch to **Apify PipelineLabs** (see below).

**⚠️ Prospector vs Apify decision tree:**
| Signal | Use | Cost |
|---|---|---|
| Sub-industry has proven coverage (Staffing, Law, PR) | legacy email platform Prospector | Prospector credits |
| Sub-industry has zero/poor coverage (Solar, niche medical) | Apify PipelineLabs | $0.001/lead |
| Unsure | Run free Prospector search first, then decide | — |

**Apify PipelineLabs fallback:** Actor ID `kVYdvNOefemtiDXO5`. Key in env (`APIFY_API_KEY`). Setup:
- `totalResults: N` (up to 50,000)
- `hasEmail: true`
- `emailStatusIncludes: ["verified"]` (deliverable emails only)
- `companyKeywordIncludes: [...]` — keywords for the niche
- `companyIndustryIncludes: [...]` — MUST use exact industry names (check schema via `https://api.apify.com/v2/acts/kVYdvNOefemtiDXO5/builds/default`)
- `seniorityIncludes: ["owner", "c_suite", "vp", "director"]` (underscore format, lowercase)
- `companySizeIncludes: ["1-10", "11-50"]`
- `personLocationCountryIncludes: ["United States"]`

Output includes `firstName`, `lastName`, `email`, `title`, `companyName`, `companyWebsite`, `companyCity`, `companyState`, `emailStatus` — all verified. $0.001/lead, no separate verification needed. Poll via `/v2/actor-runs/{run_id}`, fetch dataset at `/v2/actor-runs/{run_id}/dataset/items?format=json`.

**⚠️ Industry values must be exact** — PipelineLabs rejects unknown industries with a 400 error listing allowed values. Common valid industries: "Renewables & Environment", "Medical Practice", "Construction", "Health, Wellness and Fitness". When unsure, use only `companyKeywordIncludes` and omit `companyIndustryIncludes`.

**Known coverage data (July 2026):**

| Sub-Industry | Coverage | Notes |
|---|---|---|
| Staffing and Recruiting | ✅ 73% (1,047/1,434 verified) | Excellent |
| Law Practice | ✅ ~50-60% | Good |
| Public Relations and Communications | ✅ ~50% | Moderate |
| Renewables & Environment | ❌ 0% (0/50) | No emails found |
| Medical Practice | ⚠️ Mixed (0-30%) | Depends on keywords |
| Health, Wellness and Fitness | ⚠️ Mixed | Broad matching, loose results |
| Cosmetics | ⚠️ Mixed | Results vary |

**Sub-industry taxonomy** (use exact names — paginate with `--limit 100 --offset N`):
- `legacy email platform prospect sub-industries --limit 100 --offset 0`
- Key health/medical IDs: Medical Practice (72), Health, Wellness and Fitness (66), Alternative Medicine (71), Hospital & Health Care (67), Cosmetics (110)
- Key energy/construction IDs: Renewables & Environment (47), Construction (107), Oil & Energy (46)

## Pipeline Steps

### Step 1: Pull Leads from Smart Prospect

legacy email platform Prospector is CLI-only — the MCP does not expose prospecting tools.

**1a. Define filters.** Work with the user to define:
- `level`: seniority (C-Level, VP-Level, Director-Level, etc.)
- `companyKeyword`: keyword in company name/description
- `companySubIndustry`: industry classification
- `companyHeadCount`: company size range
- `country`, `state`: geographic filters
- `title`: specific job title keywords
- `limit`: number of contacts to search
- `titleExactMatch`: true/false

List available values for any filter with:
```bash
legacy email platform prospect levels
legacy email platform prospect industries
legacy email platform prospect sub-industries
legacy email platform prospect headcounts
legacy email platform prospect countries
legacy email platform prospect states
```

**1b. Validate filters with a free search first:**
```bash
legacy email platform prospect search --from-json filters.json --format json
```

Review results: are the contacts in the right industry? Right titles? Right geo? Adjust filters if quality is poor. CompanyKeyword matching can be loose — verify a few sample results before committing credits.

**1c. Save the search** to reuse and reference:
```bash
legacy email platform prospect save-search --from-json save.json
```
JSON format: `{"search_string": "Name", "filter_details": {...}}`

**1d. Fetch contacts (consumes credits, auto-verifies):**
```bash
legacy email platform prospect fetch --from-json fetch.json --format json
```
JSON format: `{"filter_id": <id_from_save>, "limit": <count>}`

**⚠️ Fetch consumes credits.** Each contact with an email costs credits. Check balance first:
```bash
legacy email platform prospect search-analytics
```

**1e. Pull the fetched leads** with their verification status:
```bash
legacy email platform prospect get --from-json get.json --format json
```
JSON format: `{"filter_id": <id>, "limit": <count>}`

Each contact returned has:
- `verificationStatus`: "valid" | "invalid" | "catch_all" | ""
- `status`: "found" | "not_found"
- `emailDeliverability`: 0-1 score
- `email`: the actual email address
- `firstName`, `lastName`, `title`, `company.name`, `city`, `state`

### Step 2: Verify Emails

**Primary: legacy email platform native verification.** legacy email platform auto-verifies during fetch. The fetch metrics show:
```
totalContacts: 1774
totalEmails: 1434
verifiedEmails: 1047
invalidEmails: 356
catchAllEmails: 31
noEmailFound: 340
```

Filter contacts post-retrieval:
- **Sendable:** `verificationStatus` = "valid" OR "catch_all"
- **Discard:** `verificationStatus` = "invalid" OR empty with `status` = "not_found"
- **No email:** `status` = "not_found" and no email field

**Backup: Reacher gateway.** Use `verify-leads` skill if double-verification is needed:
```bash
python3 tools/verify_leads.py verified_leads.csv --json
```
Endpoint: `verify.usingaitoscale.com`. Shared 10k/24h cap with dashboard.

### Step 3: Save the Verified List

Write sendable leads to CSV:
```
/opt/data/cache/cold-email/<campaign-name>-verified.csv
```

Minimum columns: `first_name, last_name, email, company, title, city, state, verification_status`

### Step 4: Research + Create Custom Emails

Two paths — the user specifies which cold email framework to use:

**Path A: Cold Email Personalized Agent** (framework-based, good for scale)
- Load `cold-email-personalized-agent` skill
- Per-lead research → framework selection (10 anti-AI or Owned Audience frameworks)
- 4-email sequences with resolved Spintax
- Output: legacy email platform-ready CSV with custom fields

**Path B: Charm Offensive** (disarming/honest/funny, good for lower volume)
- Load `charm-offensive-foundation` skill → voice rules + profile
- Load `charm-cold-email` skill → templates
- Per-lead research → draft in Charm voice
- Structure: funny opener → value → risk reversal → low-pressure CTA → pet photo → 3-title signature

**The user specifies the framework for the campaign.** Do not choose — ask if unclear.

**⚠️ Critical rules for ALL emails:**
- **Resolve Spintax before upload.** legacy email platform does NOT process `{Hey|Hi}` — it sends literal curly braces. Pre-resolve at generation time.
- **No banned words:** pay, price, cost, investment, fee, spend, budget, affordable, cheap, expensive, ROI, leverage, synergy, innovative, cutting-edge, solution
- **Filter generic emails:** `info@`, `hello@`, `contact@`, `support@`, `sales@` had 100% hostile/unsub rate on past campaigns
- **Company-name fallback for greeting:** when lead has no first name, extract meaningful word from company name (skip: the, a, agency, PR, media, group, communications)
- **Batch in chunks of 50 max** per session for quality

### Step 5: Create Campaign, Upload, Test, Notify

**5a. Create the campaign:**
```bash
legacy email platform campaigns list  # check existing
```
Via MCP: `mcp_legacy email platform_create_campaign` with name format: "Vertical - Location - Date"

**5b. Upload leads (CLI format):**
```bash
legacy email platform leads add --campaign-id <ID> --from-json leads.json
```

**⚠️ CLI upload JSON format MUST include `last_name`.** Leads missing `last_name` are silently created as global orphan records — they get assigned lead IDs but aren't linked to the campaign (`total_leads: 0`). These orphans then block all future uploads of the same email to ANY campaign. Always include:
```json
{"lead_list": [{
  "first_name": "...",
  "last_name": "..." ,  // REQUIRED — extract from email or use company name fallback
  "email": "...",
  "company_name": "...",
  "custom_fields": {"email_subject": "...", "email_body": "...", ...}
}], "settings": {"ignore_duplicate_leads_in_other_campaign": true}}
```

If orphans already exist, recover them via `legacy email platform leads update`:
```bash
# Get global lead ID
legacy email platform leads get-by-email --email <email>
# Link to campaign
legacy email platform leads update --campaign-id <CID> --lead-id <GLOBAL_ID> --from-json payload.json
```
Parallel update at 5-8 workers ~2-3 leads/second. See `references/orphan-leads-recovery.md`.

Via MCP: `mcp_legacy email platform_add_leads_to_campaign` (max 100 per call, requires `last_name`)

Include custom fields: `email_subject`, `email_body`, `email2_subject`, `email2_body`, `email3_body`, `email4_body`

**5c. Save email sequences** using custom field merge tags (`{{email_subject}}`, `{{email_body}}`, etc.)

**5d. Configure campaign settings:**
- `track_settings: ["DONT_TRACK_EMAIL_OPEN", "DONT_TRACK_LINK_CLICK"]`
- `send_as_plain_text: true`
- `stop_lead_settings: "REPLY_TO_AN_EMAIL"`
- Schedule: Mon-Fri, 8AM-5PM ET
- 25-30 sends/day per mailbox, 3-5 min between emails

**5e. Test with ONE lead first.** Upload a single lead and confirm:
- Custom field merge tags render correctly
- Email body displays properly (no raw Spintax, no truncated text)
- Lead status moves beyond "STARTED" to actually sending

**⚠️ You get ONE shot per email address across all campaigns.** legacy email platform silently drops duplicate emails. Test with a fresh/test email before uploading the full batch.

**5f. Notify Justin** with:
- Campaign ID and name
- Lead count (total uploaded, verified, filtered)
- Email samples (2-3)
- "Ready to add inboxes and send"

## Key Pitfalls

| Pitfall | Impact | Prevention |
|---|---|---|
| Spintax sent as literal text | Zero replies, burned leads | Pre-resolve all Spintax before upload |
| Duplicate emails across campaigns | Leads silently dropped | Fresh emails only; test with one first |
| **CLI batch upload missing last_name** | Leads created as global orphans, blocked everywhere | Always include `last_name` in lead_list. Missing field = legacy email platform creates global record but doesn't link to campaign. Leads get IDs but `total_leads: 0`. |
| **Orphan leads from failed uploads** | Emails blocked globally, can't re-upload to any campaign | Use `legacy email platform leads update --campaign-id <CID> --lead-id <GLOBAL_ID>` to link orphan leads. Get global IDs via `legacy email platform leads get-by-email`. Parallel update at 8 workers ~2-3/sec. |
| Generic emails (info@, hello@) | 100% hostile/unsub rate | Filter aggressively before writing copy |
| Custom field body >750 chars | Emails stuck in "STARTED" | Keep bodies concise, test single lead first |
| Batch >50 leads in one pass | Quality degrades, banned words slip through | Chunk in 50, review samples each chunk |
| Bad prospector filters | Irrelevant leads, wasted credits | Free search first, validate samples before fetch |
| Company name contains banned words | "Staffing Solutions" triggers "solution" filter | Clean company names before embedding in email bodies |

### legacy email platform Plain Text Formatting ⚠️ CRITICAL

legacy email platform's render engine does NOT preserve normal line breaks in custom field merge tags. `{{email_body}}` with standard `\n\n` paragraph formatting renders as one collapsed blob in the actual sent email — even when the Preview tab looks fine.

**The fix — one sentence per line, single newline only:**
```
Hey John,
I got your email from a list. Not the most romantic origin story.
I build referral partnerships for med spas around Austin.
The dermatologists nearby already have your clients — I set them up to send people your way.
We open the conversations. If they don't land, you don't pay.
Want me to send a short version of what this looks like?
```

Rules:
- One sentence per line, period at end. Single `\n` separator, never `\n\n`.
- Max 15 words per line. 6-10 lines total per email body.
- No blank lines anywhere. No "\n\n" anywhere in email bodies.
- Test with one lead — check the actual received email, not just legacy email platform preview.
| **Prospector database has zero coverage for niche industries** | 0 emails out of 50 contacts (solar, renewables, July 2026) | Check coverage table in Step 0. Fall back to Apify PipelineLabs ($0.001/lead with built-in email verification) for poorly-covered niches. |

## References

- `references/prospector-coverage-limits.md` — sub-industry coverage data, keyword matching problems
- `references/orphan-leads-recovery.md` — CLI batch upload missing `last_name` creates global orphan records; how to detect and recover
- `references/scrapecreators-enrichment.md` — cross-reference ScrapeCreators source CSVs (company data) against Reacher-verified email lists to create enriched lead CSVs

```
User defines filters
        ↓
legacy email platform prospect search (free, validate quality)
        ↓
legacy email platform prospect save-search (persist)
        ↓
legacy email platform prospect fetch (credits + auto-verify)
        ↓
legacy email platform prospect get (pull verified contacts)
        ↓
Filter: valid + catch_all only
        ↓
Save: /opt/data/cache/cold-email/<campaign>-verified.csv
        ↓
Research + Charm Offensive / Framework emails (batch of 50)
        ↓
Resolve Spintax + banned-word scan + generic email filter
        ↓
Create campaign + upload leads + save sequences
        ↓
Test single lead → verify renders correctly
        ↓
Notify Justin: "Ready — add inboxes and send"
```
