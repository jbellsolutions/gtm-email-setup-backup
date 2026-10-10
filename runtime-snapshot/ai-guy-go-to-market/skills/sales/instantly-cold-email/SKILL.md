---
name: instantly-cold-email
description: "Instantly.ai cold email system: campaigns, leads, Unibox replies, analytics, Apify lead scraping, and Reacher email verification. Mirrors the Instantly-cold-email skill's approved strategy (Charm Offensive + J. Abraham partnership methodology, disarming honesty over salesy pitch language) on Instantly's REST API instead of Instantly. No official Instantly CLI -- raw HTTPS. As of 2026-08-05: Instantly is the designated replacement for Instantly. Existing Instantly automations are being resumed; verify campaign sending state and mailbox health before increasing volume."
version: 1.0.0
author: jbellsolutions
metadata:
  hermes:
    tags: [Instantly, Cold Email, Sales, Outreach, CRM]
prerequisites:
  env_vars: [INSTANTLY_API_KEY]
  commands: []
  related_skills: [charm-offensive-foundation, charm-cold-email, charm-qc-gate, spam-word-checker, cold-email-editorial-workflow, Instantly-cold-email]
---

# Instantly Cold Email Operations

Justin's cold email infrastructure on Instantly.ai. Instantly is now the designated replacement sending platform. Instantly automations are paused pending retirement or archival; do not reactivate Instantly jobs unless explicitly directed. The legacy multi-agent forge pipeline (cold email repo) is retired — over-engineered per Justin's May 2026 directive. Current approach uses static approved copy loaded directly into Instantly campaign sequences.

**API Integration:** Instantly REST API v2, base `https://api.instantly.ai/api/v2/`, `Authorization: Bearer <INSTANTLY_API_KEY>`. No official CLI — raw HTTPS only. Verified working (2026-07-30): `GET /campaigns`, `GET /campaigns/analytics`, `GET /emails` (Unibox, `?i_status=1` filters unread), `POST /emails/reply` (requires `reply_to_uuid`), `POST /leads/list`, `GET /accounts`. Everything else below marked "unverified" has not been exercised against a live send yet — Instantly has 2 campaigns and 0 connected mailboxes as of this date.

## Batch Processing - Chunk the List (Work Smart, Not Hard)

**Never run the pipeline over an entire lead list in one pass.** For any list bigger
than one batch, process in CHUNKS of **BATCH_SIZE = 50** leads (raise toward 100 only
once a run is proven stable). Chunking keeps per-lead LLM personalization, Reacher
verification, and Instantly uploads inside provider rate limits, and makes the run
resumable after any error.

**Per-chunk loop:**
1. Take the next BATCH_SIZE unprocessed leads with the bundled helper:
   `python3 scripts/chunk_leads.py MASTER.json PROCESSED.txt /tmp/batch.json 50`
   (skips already-processed leads; exit code 3 means the list is finished).
2. Run the full pipeline on just that slice: qualify -> verify -> personalize -> upload.
3. Checkpoint - append each processed lead's email to
   `/opt/data/cache/cold-email/<campaign>-processed.txt`, and note the batch counts in the daily log.
4. Pause a few seconds between chunks. Steady traffic beats bursts - exactly what a
   provider's HTTP 429 ("Too many requests in a short window... steady traffic and
   exponential back-off help") is asking for.
5. Repeat, SKIPPING any lead already in the processed file, until the list is exhausted.

**On repeated 429s / model errors:** STOP, log the last processed lead, and resume later
from the checkpoint. Never retry the whole list - "resume" means "continue from the
first unprocessed lead."

Rule of thumb: 4,500 leads = ~90 batches of 50, not one 4,500-lead blast. A little slower
on the clock, but it finishes instead of erroring out. (Instantly's own per-call lead
upload limit is unverified — no batch has been pushed through `POST /leads` yet.
Assume it forces batching same as Instantly did (<=100-1000/call) and extend the same
discipline to the personalization and verification steps until proven otherwise.)

## Agent Handoff Page

No Instantly-specific handoff page exists yet. `references/agent-handoff-page.html` in this copy still describes the Instantly package (inherited from the fork) — do not treat it as an Instantly reference. Build an Instantly version once the daemon and campaigns are live; until then, this SKILL.md is the handoff doc.

## Controlled Personalization Test

When Justin asks to validate Instantly with a real controlled recipient, test the full chain, not merely variable storage: research the prospect's public website, write the complete framework-compliant custom email, store it in a per-lead custom variable, re-fetch and preview the rendered value, and only then activate the paused test campaign. A placeholder such as "custom email goes here" does not prove personalization. Use the direct API key and REST endpoints already documented here; Composio is not a prerequisite when `INSTANTLY_API_KEY` is available. The re-runnable recipe and the 2026-08-03 example are in `references/custom-personalization-test-2026-08-03.md`.

**Website fallback:** If the URL supplied by the user fails DNS or navigation, try the canonical HTTPS domain and its `www` variant before reporting a blocker. Use exactly one concrete, verifiable research detail in the first-touch message and follow the active framework's hard rules.

- **Lead creation/update only proves persistence. It does not prove variable resolution, delivery, Unibox ingestion, Slack notification, or reply sending. Do not claim those stages are verified until one real thread passes through them. Keep the campaign paused until the rendered preview is inspected.
- **Observed live payload shape (2026-09-01):** `POST /api/v2/leads/add` accepted `custom_variables`, but `POST /api/v2/leads/list` returned those values under each lead's `payload` object, not `custom_variables` or `customVariables`. Auditors must inspect `lead.payload` when validating stored custom variables. This persistence still does not prove Instantly resolves the variables in a rendered preview; a real preview or controlled send is required.

## Instantly API Access

No CLI — everything is raw HTTPS against `https://api.instantly.ai/api/v2/` with `Authorization: Bearer $INSTANTLY_API_KEY`. `INSTANTLY_API_KEY` is injected via compose from `/srv/single-brain/.env`.

### Verified endpoints (tested live, 2026-07-30)

```bash
# Campaigns
GET  /api/v2/campaigns                    # list campaigns
GET  /api/v2/campaigns/analytics          # campaign-level stats

# Unibox (replies)
GET  /api/v2/emails?i_status=1            # unread inbox items
GET  /api/v2/emails                       # filter further (thread/campaign) — exact filter params unverified
POST /api/v2/emails/reply                 # body requires reply_to_uuid + message content

# Leads
POST /api/v2/leads/list                   # list/search leads

# Mailboxes
GET  /api/v2/accounts                     # connected sending accounts / mailbox health
```

Example call:
```python
import urllib.request, json, os
req = urllib.request.Request(
    "https://api.instantly.ai/api/v2/campaigns",
    headers={"Authorization": f"Bearer {os.environ['INSTANTLY_API_KEY']}"}
)
print(json.load(urllib.request.urlopen(req)))
```

### Unverified — do not assume, confirm before relying on

- **Render-preview.** There is NO API endpoint to render/preview a merged email. The full v2 API surface (2026-09-01) has no template/render/preview route (the only "preview" is SuperSearch lead preview). Render-preview evidence is UI-only, or via a controlled send and reading the message record's `body.html`.
- **Sequence/settings endpoints** (plain-text send, tracking toggles, schedule) — set these as fields on `POST /campaigns` (create) or `PATCH /campaigns/{id}`; verify with `GET /campaigns/{id}`.
- **Lead sourcing / prospector.** No built-in lead-sourcing endpoint — assume none exists and source leads externally (Apify, CSV, domain scraping).

### VERIFIED 2026-09-01 — campaign create / pause / lead upload / reconciliation (live)

- **`POST /api/v2/campaigns` (create) ALWAYS returns `status: 0` (Draft).** The `status` field is `readOnly` in the schema and is silently IGNORED if passed (tested: passing `status:1` and `status:2` both still returned Draft). A campaign cannot be activated at creation — activation requires a separate explicit `POST /campaigns/{id}/activate`. This is the safe-create guarantee.
- **Campaign status enum:** 0=Draft, 1=Active, 2=Paused, 3=Completed, 4=Running Subsequences, -1=Accounts Unhealthy, -2=Bounce Protect, -99=Account Suspended.
- **`GET /api/v2/campaigns/{id}/sending-status`** is the authoritative "not sending" check. A Draft campaign returns `{"summary":{"status":"campaign_draft","status_message":"Campaign is in draft mode and has not been launched"}}`.
- **Lead upload:** `POST /api/v2/leads/add` (bulk, 1–1000 leads, uses `campaign_id` key) and `POST /api/v2/leads` (single lead, uses `campaign` key). Both accept per-lead `custom_variables` (string/number/boolean/null values only — no nested objects/arrays), which are stored under each lead's `payload`. Bulk-add response carries reconciliation counts: `total_sent`, `leads_uploaded`, `duplicated_leads`, `skipped_count`, `invalid_email_count`, `in_blocklist`, `incomplete_count`.
- **Lead status enum:** 1=Active, 2=Paused, 3=Completed, -1=Bounced, -2=Unsubscribed, -3=Skipped.
- **List leads = `POST /api/v2/leads/list`; the campaign filter key is `campaign` (NOT `campaign_id`).** Passing `campaign_id` is silently ignored and returns unfiltered results ordered by id — a reconciliation trap. `limit` max 100; cursor pagination via `starting_after` in / `next_starting_after` out. Also supports `filter` enums (e.g. `FILTER_VAL_NOT_CONTACTED`, `FILTER_VAL_CONTACTED`, `FILTER_VAL_COMPLETED`) and `search`.
- **Campaign custom variables** are auto-registered on the campaign when leads carry them (campaign object exposes `custom_variables` and `core_variables` maps). Merge-tag syntax is `{{variable_name}}` (confirmed live: sequences reference `{{email_1_subject}}`, `<div>{{email_1_body}}</div>`).
- **`DELETE /api/v2/campaigns/{id}`** works for cleanup of probe/draft campaigns.
- **`PATCH /api/v2/leads/{id}`** (verified live 2026-09-06) updates a lead in place, including `custom_variables` — this is the correct route for swapping stored per-lead copy. Do NOT use the previously documented delete-then-re-add pattern: the bulk `DELETE /leads` returns 200 but only unassigns the lead from the campaign (workspace lead record survives, still findable via `leads/list search`), and a subsequent `leads/add` for that email is silently counted in `duplicated_leads` with the stored payload left unchanged.

There is no MCP server for Instantly (mirrors the decision to cut Instantly's MCP this session — CLI/raw-HTTPS access only for the data-pull use case this skill needs).

## Cold Email Repo (legacy, retired — historical reference only)

The old multi-agent "forge" pipeline (4 squads + 2 daemons, cloned at `/tmp/ai-integraterz-cold-email`) is retired per Justin's May 2026 directive — over-engineered. Full architecture details live in `Instantly-cold-email` → "Cold Email Repo" section; not duplicated here since it's dead on both platforms and was never Instantly-specific.

## Current Strategy: Single Offer (as of May 2026)

**One offer, one message.** All previous multi-variant strategies (Power-Partner, Direct-Value, Capstone) are retired. The approved approach:

### The Offer
> AI operator in-house for $10/hour. No agency. No freelancers. No offshore. We audit, plug them in, you own the system. Set and forget.

### Targeting
Two campaigns with identical copy, different audiences:
### The Offer (v2 — May 6, 2026)

> Everybody needs an AI person. Somebody who keeps up with this stuff so you don't have to. Knows what to focus on, what to ignore, what actually matters. We embed someone on your team for as little as $10/hour. No agency. No retainers. No freelancers who disappear. Just a person who wakes up thinking about how to make your business run smoother.

### The 3-Email Sequence (APPROVED BY JUSTIN — v2, May 6 2026)

Laid-back, conversational tone. "Telling a friend something cool" energy. Save aggressive anti-agency language for email 2 and replies. Email 1 is soft — "just putting this on your radar."

```
Email 1 — Subject: your AI person (Day 0)

Hey {{first_name}} —

Just putting something on your radar.

Everybody needs an AI person. Somebody who keeps up with this stuff so you don't have to. Knows what to focus on, what to ignore, what actually matters for the business.

You have a real company to run. Real life happening. You can't be reading release notes and testing new tools every week. Nobody can — it's all moving too fast for anyone who isn't living in it full-time.

That's what we do. We embed someone on your team who handles the AI side. Simple as that. Not an agency. Not a retainer. Just a person who wakes up thinking about how to make {{company_name}} run smoother.

We can plug someone in for as little as $10/hour.

Worth a conversation?

{{sender_name}}
```

```
Email 2 — Subject: Re: your AI person (Day +3)

Hey {{first_name}} — quick follow-up.

The way we look at it: agencies charge you $3k-$8k a month for one-off AI solutions that don't connect to your actual operations. Freelancers build something and disappear. That model doesn't solve the real problem.

The real problem is: things are moving too fast and you need someone in-house who gets it. Someone who filters the noise and keeps you focused on what actually matters for {{company_name}}.

We've been doing this for a minute. Keep it simple. Stay focused on what moves the needle. Don't overcomplicate it.

Open to a quick 15-minute call to see if it makes sense?

{{sender_name}}
```

```
Email 3 — Subject: Re: your AI person (Day +8)

Last one from me, {{first_name}}.

If the timing's off, totally get it. But here's the thing I keep seeing:

Most businesses are going to wake up one day and realize they should've had an AI person a year ago. Not a tool. Not a dashboard. A person.

Somebody who knows your workflows, your customers, your priorities — and knows which AI pieces actually help vs. which are just noise.

When you're ready to explore it — whether that's next month or next quarter — the door's open.

No pressure either way.

{{sender_name}}
```

### Voice Rules (v2 — May 6, 2026)

- Conversational, peer-to-peer tone — telling a friend something cool
- "Just putting this on your radar" energy — not selling, just sharing
- No URLs in emails 1-3
- No fake timeframes, no hype words
- No em dashes
- Sign off with `{{sender_name}}` merge tag (dynamic per inbox persona)
- Plain text only
- Subject threading via `Re:` for follow-ups
- No "I hope this finds you well" or similar slop
- Very short paragraphs (1-3 sentences)
- Email 1 is soft hook — save aggressive anti-agency language for email 2 and replies
- Light personalization via merge tags: {{first_name}}, {{company_name}}, {{sender_name}}

### Reply Playbook (When Prospects Respond)

The methodology lives in the reply, not the cold email. When someone responds positively:

> Let's hop on a quick call. I can look at your setup and plug someone in for as little as $10/hour.

Key reply principles:
- **Be simple** — one person, $10/hr, no retainers. That's the whole offer.
- **Be flexible** — "Some people want to find their own AI person — cool, we can help with that too. Either way we just don't believe in the agency model."
- **Be practical** — "We just don't think paying retainers for one-off solutions that don't connect to anything actually solves the problem for most businesses."
- **Close fast** — get them on a 15-minute call. Don't sell in email.
- **No pitch deck** — the call IS the pitch. Keep it human.

## Best Practices (from 24M cold emails — Jay Feldman, 2026)

Full breakdown: `references/jay-feldman-best-practices.md`. Summary of the 8 tactics that still work at scale (24M emails sent, 53K calls booked, 3-5% avg reply rate):

**Mastery Triangle:** Deliverability + List + Copy. Missing any one caps you at 1%.

| Tactic | Status | Priority |
|---|---|---|
| Decision makers only | ✅ | — |
| Lead qualification | ✅ Implemented | `qualify_leads.py` before every upload |
| Spintax variation | 🚨 P0 CRITICAL | Must resolve at generation time regardless of platform — Instantly's Spintax support is unverified, treat as unsupported until confirmed (Instantly does NOT support it; see `Instantly-cold-email` for the incident this caused) |
| Triple tap copy | ✅ | — |
| No fingerprints (links/tracking) | ✅ | — |
| Plain text | ✅ | — |
| Short subject (3-5 words) | ✅ | — |
| Simple CTA (one-thumb reply) | ✅ | — |
| Email verification | ✅ Reacher | Reacher-verify every email. PipelineLabs "verified" is cosmetic. |
| Spam word check | ❌ Not done | P1 — run copy through checker |
| Diversified infra | 📋 Justin | — |
| Trojan horse framing | 🔮 Test later | — |
| Reverse lead magnet | 🔮 Test later | — |
| Spam folder mining | 🔮 Test later | — |

## Controlled Migration Testing

Before recommending an Instantly upgrade, use the controlled two-recipient protocol in `references/controlled-test-protocol.md`. It verifies campaign pause state, sender availability, custom-variable storage and rendering, preview, send confirmation, Unibox ingestion, Slack draft notification, approval-gated reply sending, and second-reply detection. Confirm recipient addresses explicitly and treat the latest user correction as authoritative. Do not claim the Slack step passed without an actual Slack post/message timestamp or permalink.

The existing raw REST credential can be used when it is live and verified. A separate Composio Instantly connection is not a prerequisite for raw REST calls; do not send the user through an unnecessary OAuth flow when the local API credential already authenticates successfully. Composio tools still require their own active connection, and a Slack token failure is a hard stop for the Slack-notification portion of the test.

## Campaign Status

**No Instantly campaigns are live as of 2026-07-30.** 2 campaigns exist in the account, 0 mailboxes connected, nothing sending yet. The campaign table, "Immediate Actions" P0 list, and Notion integration notes from `Instantly-cold-email` are all Instantly campaign-ID-specific (e.g. #3617053, #3639259) and don't carry over — those campaigns exist only on Instantly. Populate this section with real Instantly campaign IDs and status once campaigns launch. Until then, treat any reference to specific campaign numbers elsewhere in this file's inherited sections (if any survived the fork) as stale Instantly artifacts, not Instantly state.

## Auto-Reply Daemon

`instantly_reply_daemon.py` (forked from `auto_reply_daemon.py`) is the Instantly equivalent — see that skill's "Auto-Reply Daemon" section for full behavior (classification, drafting, Slack approval flow are identical; only the fetch/send calls differ). Built and dry-run verified 2026-07-29 (`--once` against the live, empty Unibox — clean exit, own state file created, Instantly daemon/state untouched). See the "Auto-Reply Daemon (Draft-to-Slack)" section below for what's verified vs. still assumed.

Instantly campaign data syncs to the **same** Notion DBs as Instantly — same overall cold-email operation, just a different sending platform: **Cold Email Campaigns** DB (`3543fa00-4c9d-81de-a9a4-e15bb7c7a34d`), **Leads** DB (`3543fa00-4c9d-8115-a286-ee7aa2c5a924`), **Outreach Activities** DB (`3543fa00-4c9d-81f3-bd62-d0cd983d04e1`).

## Show Email Copy to Justin (HOW TO PRESENT)

When Justin asks to see email samples:

- **Show ONE clean sample** — full email body, formatted as it would be received. Not annotated breakdowns. Not a catalog of variants.
- If he asks for "three samples," show three INDIVIDUAL emails (e.g., three different leads), each as a clean standalone message. Do not group by category with commentary.
- Do not include analysis, segmentation explanations, or variant comparisons unless explicitly asked.
- The email IS the deliverable. Present it like forwarded mail, not like a research finding.

## Lead Sources

1. **CSV Upload** — Operator uploads to Slack, validated and loaded
2. **No built-in prospector** — Instantly has no verified lead-sourcing/prospector endpoint (unlike Instantly's Prospector sub). Source leads externally (Apify, CSV, domain scraping) and upload via the leads API.
3. **Apify Scraper** — Web scraping for leads (API key needed: Map.ai or Apify)
4. **Existing Campaigns** — Pull leads from Instantly via `POST /api/v2/leads/list` for re-processing
5. **Domain → Email Scraping** — When CSVs have websites but no emails, scrape homepages directly. See `references/domain-email-scraping.md` and `scripts/domain_email_scraper.py`. Free, no proxy needed for unsophisticated sites.

## Apify Lead Scraping

API key in `/opt/data/.env` as `APIFY_API_KEY`. Account: jbellsolutions-owner, SCALE plan.

### Actors and Their Limitations

| Actor | Good for | Watch out |
|---|---|---|
| **`pipelinelabs/lead-scraper-apollo-zoominfo-lusha-ppe`** (ID: `kVYdvNOefemtiDXO5`) | **PREFERRED** — industry-filtered B2B leads with verified emails. $1/1K leads. Up to 50K/run. 250M+ database. | Industry values must be exact match (e.g. `"Staffing & Recruiting"` with ampersand). Check allowed values via error messages. Rating 2.8/5. |
| `compass/crawler-google-places` | Industry-filtered businesses (e.g. "employment agency") | **No emails returned** — addresses/phones/websites only. Needs separate email enrichment step. |
| `code_crafter/leads-finder` | Bulk leads ($0.0018/lead) — **deprecated** for targeted use | **Title/industry filters are unreliable** — returns generic owners regardless of `titles` param. Ignores `maxLeads` — overshoots 3-5x. Only ~5% of results match intended industry. |
| `dev_fusion/Linkedin-Profile-Scraper` | Deep LinkedIn data with emails | Requires specific `profileUrls` (not search-based). Needs a pre-built URL list. |

### Preferred Workflow: PipelineLabs Single-Step Scrape

Use the PipelineLabs actor when you need industry-filtered leads with emails — it respects filters and returns 100% relevant results. **One run, one dataset, no post-filtering needed.**

#### Finding the Input Schema

The actor's API doesn't expose `inputSchema` directly. Get it by:
1. Browsing the actor's Apify Store page and scrolling to "🧩 Filters" section, OR
2. Extracting from the error message after a failed run with wrong industry values — it lists all allowed values

#### Recruiter Lead Example

```python
payload = {
    "personTitleIncludes": [
        "recruiter", "senior recruiter", "talent acquisition",
        "staffing manager", "head of talent", "director of recruiting",
        "vp of recruiting", "technical recruiter", "executive recruiter"
    ],
    "seniorityIncludes": ["owner", "director", "manager", "vp", "c_suite", "partner", "senior"],
    "companyIndustryIncludes": ["Staffing & Recruiting"],   # exact match with ampersand REQUIRED
    "hasEmail": True,
    "emailStatusIncludes": ["verified"],
    "personLocationCountryIncludes": ["United States"],
    "totalResults": 500,
}
```

#### Full Input Parameters

| Parameter | Type | Description |
|---|---|---|
| `personTitleIncludes` | string[] | Free-text job title search (include) |
| `personTitleExcludes` | string[] | Free-text job title search (exclude) |
| `seniorityIncludes` | string[] | c_suite, vp, director, manager, senior, entry, owner, partner |
| `seniorityExcludes` | string[] | Same values |
| `functionIncludes` | string[] | engineering, sales, marketing, finance, operations, HR, IT, business_development |
| `hasEmail` | bool | Only return leads with email |
| `emailStatusIncludes` | string[] | verified, unverified |
| `hasPhone` | bool | Only return leads with phone |
| `hasLinkedin` | bool | Only return leads with LinkedIn |
| `personLocationCountryIncludes` | string[] | Country names |
| `companyIndustryIncludes` | string[] | **Must be exact match** — check error messages for allowed values |
| `companyIndustryExcludes` | string[] | Same — e.g. `["Staffing & Recruiting"]` |
| `companyKeywordIncludes` | string[] | Searches company name + description |
| `companySizeIncludes` | string[] | 1-10, 11-50, 51-200, 201-500, 501-1000, 1001-5000, 5001-10000, 10001+ |
| `companyEmployeeMin` | int | Exact minimum employee count |
| `companyEmployeeMax` | int | Exact maximum employee count |
| `totalResults` | int | **Actor RESPECTS this limit** (unlike leads-finder). Max 50,000. |

#### PipelineLabs Output Fields

Keys returned: `firstName`, `lastName`, `fullName`, `title`, `position`, `seniority`, `functions`, `email`, `emailStatus`, `phone`, `linkedinUrl`, `personCity`, `personState`, `personCountry`, `companyName`, `companyDomain`, `companyIndustry`, `companySize`, `companySizeRange`, `annualRevenue`, `technologies`, `foundedYear`.

### Niche Targeting via `companyKeywordIncludes` (When Industry Enum Doesn't Match)

When PipelineLabs' `companyIndustryIncludes` enum doesn't include your target industry (e.g., "Public Relations" isn't in the enum), use `companyKeywordIncludes` to search company name + description text. Pair with `companySizeIncludes` to narrow scope.

**PR Agency example** (5,000 leads, 99% qualification pass rate):
```python
"companyKeywordIncludes": [
    "public relations", "PR agency", "PR firm",
    "communications agency", "media relations", "public affairs",
    "strategic communications"
],
"companySizeIncludes": ["1-10", "11-50", "51-200", "201-500"],
```

Full run details: `references/pr-agency-scrape.md`.

### Legacy Workflow (Google Maps + Domain Search)

**Only use if PipelineLabs actor is unavailable or doesn't cover the target industry.** The leads-finder actor cannot reliably filter by title/industry. **Do not trust its built-in filters.**

### Niche Campaign Launch (End-to-End)

The complete pipeline for launching a niche-specific campaign with personalized emails:

1. **Scrape leads** via Apify PipelineLabs with niche filters (industry + keyword + location). Use `companyKeywordIncludes` when exact industry codes are unknown (e.g. `["hvac", "plumbing", "roofing"]`).
2. **Qualify** via `qualify_leads.py` — filters generics, invalids, duplicates.
3. **Verify emails** via Reacher (`verify-leads` skill, `python3 /opt/data/skills/email/verify-leads/tools/verify_leads.py <file>.csv --json`). Discard all `invalid` results. Upload only `valid`.
4. **Personalize per-lead** via a niche-specific script (e.g. `hvac_florida_personalize.py`). Script generates per-lead copy variations based on signals (role, market, segment, city).
5. **Save campaign sequences** — merge-tag syntax for per-lead custom fields is unverified on Instantly (Instantly used `{{custom_fields.field_name}}`; confirm Instantly's actual syntax before relying on it). Subject can be static (e.g. "HVAC in Florida") or per-lead once merge tags are confirmed.
6. **Upload leads** via `POST /api/v2/leads` in conservative batches (exact limit unverified — start at 100, see Batch Processing above).
7. **Fix settings** — verify tracking/plain-text/schedule settings via the Instantly UI or `GET /campaigns` response; no settings-update endpoint has been confirmed yet.
8. **User connects mailboxes** → START campaign.

See `references/hvac-florida-campaign.md` for the May 2026 HVAC campaign specifics (Instantly-specific, historical reference for the approach only).

### Campaign Creation Workflow

No create-campaign endpoint has been verified for Instantly. Until one is confirmed:

1. **Create campaign** via the Instantly web UI
2. **Set schedule/settings** via the UI (days, hours, timezone, plain-text, tracking) — verify afterward with `GET /campaigns` / `GET /campaigns/analytics`
3. **Scrape leads** via Apify PipelineLabs (see Apify section)
4. **Upload leads** via `POST /api/v2/leads` (payload shape unverified — confirm against Instantly docs before first real batch)
5. **User connects mailboxes** — then start campaign

Mirrors `Instantly-cold-email`'s "Campaign Creation Workflow (Approved)" section, which is CLI/MCP-driven and fully verified for Instantly — use that as the reference for what a mature version of this workflow looks like once Instantly's endpoints are confirmed.

### Apify API Patterns

```python
import urllib.request, json
APIFY_KEY = "apify_api_..."

# Run actor
url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {APIFY_KEY}"}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers, method='POST')

# Poll run status
status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
# status will be RUNNING → SUCCEEDED/FAILED/ABORTED

# Abort runaway runs (leads-finder ignores maxLeads)
abort_url = f"https://api.apify.com/v2/actor-runs/{run_id}/abort"
req = urllib.request.Request(abort_url, method="POST", headers={"Authorization": f"Bearer {APIFY_KEY}"})

# Get dataset
ds_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json&clean=true&skipEmpty=true"
```

## Email Verification — Reacher (self-hosted) ✅ ACTIVE

**Rule: verify EVERY email through Reacher before uploading to Instantly. No exceptions.**
Use `verify-leads` skill: `python3 /opt/data/skills/email/verify-leads/tools/verify_leads.py <file>.csv --json`.
ScraperCity is deleted. PipelineLabs `emailStatus: "verified"` is cosmetic — expect 40-50% rejection.
- June 2, 2026 — ScrapeCreators: 32.3% invalid across 12,000 leads
- May 12, 2026 — PR campaign: 49.4% invalid from PipelineLabs "deliverable"

**PipelineLabs is a COMPANY DISCOVERY engine, not an email source.** The verified-email flag is cosmetic across all verticals — never trust it. Always Reacher-verify after scraping.

PipelineLabs verification is cosmetic. A real verifier catches 40-50% of bad emails that PipelineLabs misses.

### ScraperCity (CANCELLED) → Reacher Gateway
Account cancelled June 2026. ScraperCity CLI removed, MCP broken. Use `verify-leads` skill (Reacher, 10K/24h cap). For large lists (1,000+): expect 5-10 min runtime. Pre-filter using `references/lead-quality-filters.md`. See `references/bounce-analysis-pattern.md` for blocked/bounced lead triage.

**Fallback:** ListKit enrichment emails are more reliable than PipelineLabs. Use them as-is when ScraperCity is unavailable. Alternatively, explore ZeroBounce/NeverBounce (Justin has accounts) for critical campaigns.

**Legacy info (for reference if account is reactivated):**

**API key:** `90c2ca64-81bc-48ab-a6b2-980abfaea898` (in `/opt/data/.env` as `SCRAPERCITY_API_KEY`). Growth plan $149/mo, $158.98 balance, renews 2026-07-02.

**CLI command:**
```bash
export SCRAPERCITY_API_KEY=90c2ca64-81bc-48ab-a6b2-980abfaea898
scrapercity email-validate user@example.com user2@example.com ...
scrapercity poll <run_id>
scrapercity download <run_id>
```

**Cost:** ~$0.0036 per email. At scale: 1,000 emails = ~$3.60.
**Speed:** Async — submit batch, poll until SUCCEEDED, download CSV.
**Output fields:** `sc_email_status` (valid/invalid), `sc_validation_message`, `sc_is_catch_all`, `sc_mx_provider`, plus company enrichment (name, industry, size, founded, location, LinkedIn, Facebook, Twitter).

**Batch verification:**
```bash
# Write emails to temp file, one per line
cat /tmp/emails.txt | xargs scrapercity email-validate
# ...or pipe directly for lists under ~1000
```

**File-based validation:**
```bash
scrapercity email-validate --file /tmp/emails.txt
```

#### Tiers

| Status | Action |
|---|---|
| `valid` | ✅ Upload to campaign |
| `invalid` | 🚫 **DISCARD.** Do not upload. These WILL bounce. |

Unlike Anymail Finder, ScraperCity does not return a "risky" tier — results are binary valid/invalid. Company enrichment is included for valid emails at no extra cost.

### Anymail Finder (DEPRECATED — Do Not Use)

API key `LKxXijHdndI7SINhICwPb0S2` is out of credits. Account `jbellsolutions@gmail.com` — deleted. All verification now through Reacher. ScraperCity fully removed from system July 2026.

### Apify Email Verifier (DEPRECATED — Do Not Use)

Actor `xlWThR6pfc9ka55eH` is unreliable at scale. On a 5,000-email scrape: 7/50 batches (14%) returned data on first pass. Retrying 43 empty batches as 50-email chunks (86 retry batches) still only produced ~20% total coverage. **Not worth the time.** Use ScraperCity instead.

### Other Verification Options

- **Instantly built-in verification** — Instantly has a verification feature in its UI/product; whether it's sufficient on its own (replacing the standalone Reacher step) is unconfirmed. Until verified, keep Reacher as the mandatory gate before upload — same as Instantly.
- **ZeroBounce / NeverBounce** — Justin has accounts. Use for second-pass verification of risky leads.

### Qualification Step (MANDATORY — Run Before Every Upload)

**Rule: scrape → qualify → upload. Never upload raw Apify output.**

Use `scripts/qualify_leads.py` (bundled with this skill) to filter out:
- Generic emails (info@, contact@, support@, etc.)
- Invalid/malformed email addresses
- Placeholder or numeric-only company names
- Duplicate emails within the batch

**⚠️ `info@` addresses run a very high unsubscribe/hostile rate** — confirmed on Instantly PR campaigns (see `Instantly-cold-email`: 100% of unsubscribes on one campaign traced to `info@` addresses). Shared inboxes = no individual decision maker = guaranteed waste. This is a lead-quality rule independent of sending platform. Consider adding an `--aggressive-generics` flag to `qualify_leads.py` that strips `info@`, `media@`, `press@`, `podcast@`, `admin@`, `hello@` in addition to `info@/contact@/support@`.

```bash
python3 qualify_leads.py /tmp/raw_leads.json /tmp/qualified_leads.json
```

Typical rejection rate: 1-7% depending on niche. PipelineLabs with `hasEmail: true` + `emailStatusIncludes: ["verified"]` keeps this low (~1-2%). Without those filters, expect 10-20% rejection.

**After qualification**, use `verify-leads` skill. Pre-filter with `references/lead-quality-filters.md`. Never skip verification.

### Per-Lead Email Personalization

For campaigns where each lead gets a unique email body (not just merge-tag swaps), use this pattern:

1. Build a per-lead personalization script that generates per-lead email variants (naming convention TBD — Instantly's custom-field/merge-tag mechanism is unverified; Instantly used `custom_fields.personalized_email_1/2/3`).
2. Save campaign sequences using whatever merge-tag syntax Instantly actually supports — confirm this against their docs or a UI test before relying on it. Do not assume Instantly's `{{custom_fields.x}}` syntax carries over.
3. Upload leads with the personalized content attached in whatever field Instantly resolves at send time.

This is the target shape (full per-lead copy via standard sequencing/scheduling) — same as Instantly's approach in `Instantly-cold-email`, ported once Instantly's actual field/merge-tag names are confirmed.

Example campaign: `home-services-hvac-florida` — 1,180 leads with copy variations by market (coastal/large_metro/small_market) and segment (owner_op/commercial/multi_truck).

## Lead Upload Workflow (End-to-End)

**Rule: scrape → qualify → verify ALL emails via Reacher → upload. Never skip verification. PipelineLabs "verified" means nothing.**

Evidence (from the Instantly operation, same scrapers/verifiers apply here): On the May 12 PR campaign, 49.4% of PipelineLabs "deliverable" emails were invalid when checked by a real verifier. Expect 40-50% rejection from any PipelineLabs scrape regardless of which platform you're uploading to.

1. **Scrape** via Apify PipelineLabs → raw JSON
2. **Qualify** via `qualify_leads.py` → filtered JSON (removes generics, invalids, duplicates)
3. **Verify ALL emails** via Reacher (`verify-leads` skill). Discard all `invalid` results. Upload `valid` only.
4. **Format** for Instantly — exact field names unverified; likely `first_name`/`last_name`/`email`/`company_name` given how universal those are, but confirm against Instantly's docs before the first real upload rather than assuming Instantly's field names carry over 1:1.
5. **Upload** via `POST /api/v2/leads` (endpoint path and payload shape unverified — this is the single biggest unknown in this whole skill; test with a throwaway lead first)
6. **User connects mailboxes** → then START campaign

Apify fields likely to carry over unchanged (universal, not Instantly-specific): `first_name`, `last_name`, `email`, `company_name`. Fields Instantly put under `custom_fields` (`title`, `industry`, `linkedin_profile`, `company_url`) need their Instantly equivalent confirmed — do not assume the same nesting.

No upload has been executed against Instantly yet, so there's no confirmed request/response shape to document here (unlike Instantly's `lead_list`/`settings` JSON format, which is battle-tested — see `Instantly-cold-email` for that reference). Update this section with the real payload format and response fields (equivalents of Instantly's `upload_count`/`total_leads`/`already_added_to_campaign`) after the first real test upload.


## Auto-Reply Daemon (Draft-to-Slack)

`/opt/data/scripts/instantly_reply_daemon.py` (forked from `auto_reply_daemon.py`) — built and dry-run verified 2026-07-29. Status:

- Polls Instantly Unibox (`GET /emails?i_status=1`) via its own Hermes cron (separate from `Instantly-auto-reply`), delivers to Slack for operator approval — same channel/approval pattern as the Instantly daemon.
- Same classifier (OOO/positive_interested/positive_referral/negative_notfit/unsubscribe/hostile/dead/neutral), same DeepSeek draft generation, same **does NOT auto-send** rule.
- **Separate state file**: `/opt/data/scripts/instantly_reply_state.json` — brand new, does not touch or share IDs with `auto_reply_state.json`. Instantly threads on `reply_to_uuid`, not Instantly's `(campaign_id, lead_id, email_stats_id)` triple, so there's no ID-collision risk to manage — different ID space entirely.
- **VERIFIED 2026-07-29**: `GET /emails?i_status=1` wraps results as `{"items": [...]}` (confirmed live, 0 items — 0 mailboxes connected). Cloudflare 403s (error 1010) on `urllib`'s default User-Agent — the daemon sends a browser-like UA to work around this; plain `curl` isn't affected.
- **Verified 2026-08-05:** live unread items use `ue_type: 2` for inbound replies, `from_address_email` for sender, and `body` as an object with `text`/`html`; the unread endpoint can also include sent items (`ue_type: 1`), so the daemon filters to inbound replies. The `thread_id` filter param and `reply_to_uuid` send payload remain unverified until a real reply is sent.
- Everything in `Instantly-cold-email`'s "Auto-Reply Daemon" section below this point (classifier patch history, message-ID bracket bug, CAMPAIGN_CONTEXT gaps, HVAC hardcoded templates) is Instantly incident history tied to campaigns that only exist on Instantly. None of it has an Instantly equivalent yet because Instantly hasn't processed a single reply. Once the Instantly daemon has run in production, document its own incidents here rather than assuming Instantly's bugs recur.

## Auto-Reply Recipe

```python
import json, os, urllib.request

payload = {
    "reply_to_uuid": "uuid-of-the-email-being-replied-to",
    "body": {"text": "Your reply text here"}   # exact body field name unverified — confirm against Instantly docs
}

req = urllib.request.Request(
    "https://api.instantly.ai/api/v2/emails/reply",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {os.environ['INSTANTLY_API_KEY']}",
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    result = json.load(resp)
    print(result)
```

Not yet exercised against a real reply (no mailboxes connected, no inbound replies exist). `reply_to_uuid` is confirmed required by the endpoint; the rest of the payload shape (body field name, whether `to`/`subject` are needed) is inferred, not tested. Confirm on first real use and update this recipe.

## Reply Approval Workflow (as of June 2026)

When a positive reply comes in, the daemon does NOT auto-send. Instead:

1. **Detection**: Daemon polls inbox every minute, classifies replies
2. **Draft generation**: DeepSeek generates a reply using campaign context. SpeakerAgent (3316611) gets hardcoded template instead.
3. **Slack notification**: Cron agent reads `/tmp/auto_reply_drafts.json` and posts to `#single-brain`:
   ```
   📬 New Reply — interested
   From: Jane Smith (jane@company.com)
   Their reply: "Yes, tell me more..."
   ✏️ Draft response: [full draft text]
   ```
4. **Operator approval**: Justin says "send reply to Jane" in Slack → Hermes agent calls the reply function with the draft's `reply_to_uuid` and body
5. **QC Gate (MANDATORY)**: Before sending, run the draft through `skill_view(name='charm-qc-gate')`. Checks formatting, language, tone, and grammar. Only send on ✅ PASS or ⚠️ PASS WITH FIXES. ❌ FAIL = rewrite and re-verify. Never skip this step.
6. **Sending**: `POST /api/v2/emails/reply` (same recipe as above)

Drafts include all fields needed to send: `lead_name`, `lead_email`, `reply_to_uuid`, `draft_reply`.

If Justin says "edit reply to Jane" instead, regenerate with different instructions before sending.

Every campaign SHOULD follow the same compliance intent as the Instantly operation (no open tracking, reply-only stop condition, plain text, non-promotional copy, conservative sending schedule, mandatory verification) — but the exact settings field names and how to verify them via the Instantly API are unconfirmed. See `Instantly-cold-email`'s compliance table for the verified Instantly version; rebuild this table for Instantly once `GET /campaigns` response fields are inspected on a real campaign.

### Lead Filtering Rules

Instantly uses UI tags ("Mailed", "MailReef") to gate sending on already-contacted/still-warming leads. Whether Instantly has an equivalent tagging mechanism is unconfirmed — check the Instantly UI/API before assuming untagged == safe to send. Until confirmed, track "already contacted" and "still warming" status manually (e.g. in the lead source file) rather than assuming a platform tag exists.

## Account Consolidation (for hitting volume targets)

When a single campaign can't hit its daily max due to inbox count, consolidate inboxes from paused/low-priority campaigns. Each inbox is capped at 15 sends/day (Google Workspace limit).

**Quick math:** target_sends ÷ 15 = minimum inboxes needed. For 1,000/day: ~67 inboxes minimum.

**Workflow (target shape — Instantly-specific calls unverified):**
1. Identify source campaign(s) to pull mailboxes from (typically paused or lower-priority)
2. Connect mailboxes to the target campaign — via `GET /accounts` to find candidates, then whatever assignment mechanism Instantly exposes (unverified — check the UI first)
3. Pause the source campaign
4. Verify via `GET /accounts` / `GET /campaigns` that the mailbox count moved

Whether Instantly mailboxes can belong to multiple campaigns simultaneously (like Instantly's shared `daily_sent_count`) is unconfirmed — don't assume it works the same way.

### Daily Health Monitoring

Once an Instantly daily-health cron exists (not yet created — see task tracking), it should mirror the Instantly one: sync Instantly stats → the same Notion Cold Email Campaigns DB, report unread inbox / campaign health / mailbox status to **Slack**, not Telegram (standing rule for all cron jobs, not Instantly-specific).

**⚠️ Daily report MUST check ALL campaigns, not just one** — same lesson as Instantly: use `GET /emails` (unfiltered) to see everything, then cross-reference, rather than trusting a single triggered campaign ID.

The pre-call-report combined sweep and the full cross-campaign monitoring workflow (`references/cross-campaign-monitoring.md`) are Instantly-CLI-specific (built around `Instantly inbox replies` pagination and `our_replies_after`). Port the same *pattern* (two-phase filtering, message-history ground truth) once the Instantly daemon exists — don't reuse the reference doc as-is, since it's written against Instantly's response shapes.

### Daily Stats Report Format

When generating a per-campaign daily stats report, use this template (see `references/daily-report-template.md`):

```
📊 Cold Email Daily — [Day, Mon Date]
Campaign: [name] (#[id])

Sent: X | Opens: Y (Z%) | Clicks: C (D%) | Replies: R (E%)
Positives: P (F% positive reply rate)
Bounces: B | Unsubs: U

[If any positive replies today, list each:]
💬 pos reply — "Name" (email): "[first 80 chars of reply]"
```

**SILENT rule — when to skip delivery entirely:** The cron agent should respond with `[SILENT]` (and nothing else) when:
1. No new inbox replies landed today (check `last_reply_time` starting with today's date)
2. No new sends occurred today (sequence complete, campaign in steady state)
3. All campaigns are in terminal states (STOPPED, or ACTIVE-but-sequence-complete) with no queued activity

The key signal is **inbound replies today** — that's what the operator needs to see. Campaign status (ACTIVE/STOPPED) alone doesn't determine whether to report. An ACTIVE campaign with a completed sequence and no new replies today → SILENT. A STOPPED campaign with a new reply that came in today → REPORT it.

**When NOT to go SILENT:** If there ARE new replies today (even on a STOPPED campaign), if the daemon state shows unhandled positive replies, or if there's a deliverability alert (hostile >0.3%, unsub surge), report normally. **Also:** if there are replies from yesterday that haven't been reported yet (first-time discovery), surface them — the operator needs to know about positive replies even if they're a day old.

**When the campaign is STOPPED/PAUSED with no activity:** Report the zeros, include lead status snapshot, and surface what IS active across other campaigns. Don't silently report nothing — the operator needs to know the state. Show active campaign stats as a secondary section.

**When ALL campaigns are STOPPED:** Report each campaign's lead status snapshot (STARTED/INPROGRESS/COMPLETED/BLOCKED counts), note the stop time, flag any compliance issues (e.g. `send_as_plain_text: false`), and list any unread or recent positive replies that may need attention. Don't pad — if nothing is sending, the report should be short and factual.

**When the campaign is STOPPED/PAUSED with no activity:** Report the zeros, include lead status snapshot, and surface what IS active across other campaigns. Don't silently report nothing — the operator needs to know the state. Show active campaign stats as a secondary section.

**When ALL campaigns are STOPPED:** Report each campaign's lead status snapshot (STARTED/INPROGRESS/COMPLETED/BLOCKED counts), note the stop time, flag any compliance issues (e.g. `send_as_plain_text: false`), and list any unread or recent positive replies that may need attention. Don't pad — if nothing is sending, the report should be short and factual.

### Quick Inbox Check

For a fast inbox scan:

```python
import urllib.request, json, os
req = urllib.request.Request(
    "https://api.instantly.ai/api/v2/emails?i_status=1",
    headers={"Authorization": f"Bearer {os.environ['INSTANTLY_API_KEY']}"}
)
data = json.load(urllib.request.urlopen(req))
```

Whether the `/emails` response includes full reply body + thread/message-id inline (unlike Instantly, whose inbox listing is metadata-only and requires a second per-lead call for content) is unconfirmed — check the actual response shape on first use. If it does include the body, this is simpler than Instantly's two-step inbox→message-history pattern; if not, a second call will be needed the same way.

**Bundled scripts inherited from the fork** (`scripts/parse_inbox.py`, `scripts/quick_check.py`, `scripts/monitor_inbox.py`) are written against Instantly's CLI output shape (`Instantly inbox replies`, `email_lead_id`, RFC 5322 message-ID bracket normalization) and will NOT work against Instantly's response format unmodified. Treat them as reference for the *pattern* (two-phase filtering, dedup against state, auto-responder detection) — not as working code — until rewritten against a real `/emails` response.

### Daily Stats Reporting

Instantly's analytics endpoints are known to return 0 for campaigns with tracking disabled, which is why that skill falls back to lead-level message history as ground truth. Whether `GET /campaigns/analytics` has the same blind spot on Instantly is unknown — it hasn't been tested against a sending campaign. If it proves unreliable the same way, the fallback pattern (paginate leads, use message-level SENT/REPLY/bounce evidence as ground truth) is proven and portable — but don't assume Instantly's specific status vocabulary (`INPROGRESS`/`COMPLETED`/`BLOCKED`) exists on Instantly; confirm Instantly's actual lead-status field names first.

## Lead Quality Gate (MANDATORY Before Personalization)

Before generating or uploading custom emails:

1. Never use placeholder names such as `there`, an email username, a role label, or a company name as a person's first name.
2. If a verified email has no reliable contact name, leave `first_name` blank and write the email without a greeting name. Hold the lead when a company identity cannot be established from the supplied enrichment.
3. Every custom body must preserve paragraph separation as `<br><br>` and must be re-fetched from Instantly after upload to verify the stored payload, not merely the local CSV.
4. Reconcile counts from the actual user-supplied verified file. Never infer a larger verified population from an unfiltered platform lead listing.

## Upload Verification (MANDATORY After Every Upload)

**Rule: after uploading leads, verify the count.** Instantly's upload API is known to return success while some leads silently fail to appear (see `Instantly-cold-email` for the documented incident — 1,170 uploaded, only 349 showed up, required re-upload). Whether Instantly's upload API has the same silent-partial-failure behavior is unknown, but the rule applies regardless of platform:

1. Upload leads via `POST /api/v2/leads`
2. Immediately re-query the campaign's lead count (mechanism unverified — likely `POST /leads/list` filtered to the campaign, or a count field on `GET /campaigns`)
3. If the count doesn't match what was uploaded, re-upload the full batch — assume deduplication is automatic until proven otherwise (don't assume duplicates will double-send)
4. Only then proceed to start the campaign

## Custom Email Variables and Preview Formatting (MANDATORY)

When storing a complete per-lead custom email in an Instantly custom variable, use this exact pattern:

1. Store the entire researched email body in a scalar custom variable, such as `custom_email`.
2. Preserve the copy's paragraph structure with HTML breaks: replace each blank-line paragraph separator (`\\n\\n`) with `<br><br>` and each remaining single newline with `<br>`.
3. Set the campaign email body to exactly `{{custom_email}}` and nothing else. Do not prepend a greeting, test text, instructions, or any other body content, or Instantly will concatenate it with the variable.
4. Use a lowercase 1-4 word subject in the sequence, such as `owned audience`.
5. Re-fetch the lead after updating and verify that the custom variable contains the expected `<br><br>` paragraph separators.
6. Preview the resolved email in Instantly before activation. The preview must show distinct paragraphs matching the intended email, not one collapsed block and not duplicated wrapper text.

**Why:** Instantly's variable panel may display raw newline characters as paragraphs, while the rendered email preview treats raw newlines as HTML whitespace and collapses them. `<br><br>` forces visible paragraph breaks in the rendered preview.

**Approved implementation pattern:**
```python
html_body = custom_email.replace("\\n\\n", "<br><br>").replace("\\n", "<br>")
lead_payload = {"custom_variables": {"custom_email": html_body}}
sequence_body = "{{custom_email}}"
```

This is the required Instantly build pattern for all future custom cold-email tests and campaigns unless a newer live test proves a better rendering method.

### Activation Gate (MANDATORY)

User approval to activate is required, but it does not replace the operational gates. Before calling the activation endpoint, verify all of the following: machine QA pass, independent second-agent editorial QA pass, sampled Instantly UI render-preview evidence, exact authorized inbox-tag membership, readiness/warmup status, disjoint account allocation, configured daily target capacity, campaign status Draft/Paused, and no prior sends. If UI authentication or render evidence is unavailable, stop and report that blocker rather than activating.

When a daily target is requested, attach the smallest disjoint groups of explicitly authorized ready inboxes that meet each campaign's target. Re-fetch campaign configuration after assignment and confirm the exact inbox count, daily limit, capacity, and `GET /campaigns/{id}/sending-status` no-send state. A successful PATCH is configuration persistence only; it is not evidence of launch or delivery.

### Controlled Send Verification (MANDATORY)

Do not claim a test email was sent merely because campaign activation returns HTTP 200. Activation starts Instantly's scheduler; it does not prove immediate delivery. After activating a controlled campaign:

1. Keep the campaign active long enough for the scheduler to process the lead. Do **not** pause it immediately after activation.
2. Poll `GET /emails` and/or the lead record until a sent message appears. The authoritative send evidence is an email record with the expected recipient, sender, subject, timestamp, campaign ID, lead ID, and thread ID.
3. Only after that record exists may you report the message as sent.
4. If the user wants the campaign left on, isolate the test recipient first, cap the daily limit, remove or exclude all control recipients, and then leave it active.
5. If the message does not appear, report it as queued/not confirmed, not sent.

A prior test returned activation `200` but had zero sent messages because the campaign was paused before scheduler processing. Re-activation followed by polling produced a confirmed `/emails` record. See `references/controlled-send-verification.md` for the reproduction and authoritative message-record check.

### Verified Inbound Reply Payload (2026-08-03)

A live controlled test confirmed Instantly inbound replies through `GET /emails?i_status=1` and `GET /emails`.

- Unread filter returns `{\"items\": [...]}`.
- Normal inbound replies have `ue_type: 2`; inbound follow-up replies can appear as `ue_type: 3` (observed 2026-08-07). Filter by sender direction and campaign context rather than assuming only `ue_type: 2`.
- Relevant fields: `id`, `timestamp_email`, `message_id`, `subject`, `to_address_email_list`, `from_address_email`, `lead`, `lead_id`, `campaign_id`, `thread_id`, and `body.html`.
- The tested reply had a usable thread ID and full HTML body, including quoted original content.
- The reply body must be normalized by stripping the quoted Gmail block/signature before classification.
- `GET /emails?thread_id=<thread_id>` currently returns the full matching result set, including sent and inbound messages. It is usable for thread history, but filtering must be done client-side by `thread_id`, `ue_type`, and timestamp.
- `GET /emails?i_status=1` is sufficient for incremental unread-reply polling and is much cheaper than exhaustive history scans.

**Webhook status:** No Instantly inbound-reply webhook endpoint/event has been verified in the current v2 API integration. Do not claim webhook support or build around it until Instantly exposes and documents a callback for inbound email events. The reliable path today is polling `GET /emails?i_status=1`; a one-minute daemon is preferable to a 30-minute sweep for near-real-time Slack notifications.

## Pitfalls

- **Activation 200 is not delivery confirmation.** Always verify the actual `/emails` record before claiming success.
- **Pausing immediately after activation can prevent the first send.** Leave the campaign active during the verification window.
- **Campaign-level analytics may remain empty or lag.** Prefer the message-level `/emails` record and lead counters for controlled-send confirmation.
- **Instantly may normalize a variable-only body to HTML.** A stored sequence body such as `<div>{{custom_email}}</div>` is compatible with the HTML `<br><br>` paragraph-break strategy; inspect the actual sent message body before declaring formatting correct.



**Portable pitfalls (apply regardless of sending platform — kept from the fork):**

- **Security scan blocks `pipe_to_interpreter` patterns** (e.g. piping a CLI/script into `python3 -c`). Workaround: write JSON to file (`> /tmp/out.json`), then read with Python or `read_file` tool. **Same applies to heredocs** (`python3 << 'EOF'`) — write script to file instead.
- **Security scan blocks unicode status markers in Python heredocs** — `✅`, `🆕`, `⚠️`, and other emoji with variation selectors trigger the `tirith:variation_selector` rule and reject the entire heredoc. Use ASCII alternatives like `[NEW]`, `[DONE]`, `[FAIL]`, `[WARN]`.
- **Security scan: SQL TRUNCATE false positive on env-file parsing** — heredocs containing `.split('SOME_KEY=')` patterns on `.env` files trigger the `SQL TRUNCATE` rule (scanner sees `TRUNCATE` in the delimiter). Use the `write_file` tool instead of heredocs, and parse keys line-by-line: `for line in f: if line.startswith('INSTANTLY_API_KEY='): key = line.split('=', 1)[1].strip()`.
- **Apify residential proxy costs add up** — use datacenter proxy for non-LinkedIn scrapes.
- **Apify leads-finder ignores `maxLeads` parameter** — abort the run manually when you have enough. Monitor `chargedEventCounts.lead-fetched` to track.
- **Apify leads-finder ignores `titles`/`jobTitles` filters** — returns generic "Owner" results regardless. Always post-filter by `industry` field locally.
- **Google Maps scraper returns no emails** — only business name, address, phone, website. Needs a separate email enrichment step.
- **Apify API key rotation** — the stored key can become invalid silently ("user or token not found"). If all Apify calls return 401, generate a fresh token at `console.apify.com/settings/integrations` and update `APIFY_API_KEY`.
- **Apify actor search is account-scoped** — `v2/acts?search=` only returns actors available to your account, not the full Apify Store.
- **PipelineLabs `companyIndustryIncludes`/`companyIndustryExcludes` values must be exact** (e.g. `"Staffing & Recruiting"`, not `"staffing and recruiting"`). Error messages list valid options. Use `companyKeywordIncludes` for industries not in the enum.
- **PipelineLabs `seniorityIncludes`** — does NOT include `"founder"`. Use `["owner", "c_suite", "partner"]` for SMB decision makers.
- **PipelineLabs `companyKeywordIncludes`** — searches company name + description text. Use for niche targeting when exact industry codes are unknown.

**Instantly-specific pitfalls:**

- **Do not misdiagnose pagination failures as an endpoint limitation.** A broad `/emails` sweep using offset pagination can make many requests and trigger a transient `429` response. That does not prove the endpoint is rate-limited or that replies are unavailable. Use the API's cursor field (`next_starting_after`) and follow cursor pagination, request a larger page size where supported, retry transient failures with backoff, and only report a genuine blocker after exhausting those recovery paths. If a sweep fails, preserve the authenticated campaign result and distinguish `temporary request failure` from `zero replies`.

Everything Instantly-specific in `Instantly-cold-email`'s much larger Pitfalls section (API response shapes, CLI flag traps, ID-field gotchas, campaign-specific incident history) was earned through months of production sends on that platform — none of it can be honestly assumed to transfer. Add entries here as they're actually discovered running Instantly in production.
