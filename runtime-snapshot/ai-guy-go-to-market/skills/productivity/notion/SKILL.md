---
name: notion
description: "Notion Super Agent: full workspace ops — 30 DBs, email→DB routing, daily ingest, leads/growth/outreach tracking, idempotent writes."
version: 2.1.0
author: jbellsolutions
license: MIT
metadata:
  hermes:
    tags: [Notion, Productivity, CRM, Operations, Database, API]
    homepage: https://developers.notion.com
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Super Agent — AI Integraterz Operations Hub

Justin's Notion workspace is the central nervous system for AI Integraterz. **Everything we do should be documented in Notion in the right place.** This skill covers the full 25-database data model, write conventions, and API patterns.

## Prerequisites

1. `NOTION_API_KEY` in `/opt/data/.env` (starts with `ntn_` or `secret_`)
2. Integration must be shared with target pages/databases in Notion (click "..." → "Connect to" → integration name)
3. Operations Hub parent page ID: `3493fa00-4c9d-8105-8a4e-ccdb8f4700c9`

## API Basics

Use `execute_code` with `urllib.request` (curl is not installed on this VPS). Or use the helper script at `/opt/data/skills/productivity/notion/scripts/notion_api.py`.

Notion API version: `2022-06-28` (confirmed working). Load the API key from `/opt/data/.env`.

```python
import urllib.request, json
env_vars = {}
with open('/opt/data/.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            env_vars[key.strip()] = val.strip()
notion_key = env_vars['NOTION_API_KEY']

def notion_api(method, endpoint, body=None):
    url = f"https://api.notion.com{endpoint}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {notion_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    })
    return json.loads(urllib.request.urlopen(req).read())
```

## Quick Reference: Key Entry Points

| Page | URL / ID |
|---|---|
| **🏠 AI Integraterz HQ** | `34a3fa00-4c9d-81da-9e78-d59dcf52efaf` |
| **📂 Project Management** | `3533fa00-4c9d-81f5-b888-c01115a5b442` |
| ↳ Projects DB | `3533fa00-4c9d-818a-bd92-c9d91ceafc4c` |
| ↳ Tasks DB | `3533fa00-4c9d-81f7-a1bb-e4bbfc23ebcd` |

## Setting Up Notion Cron Digests

To create a recurring daily digest that queries Notion DBs and delivers to Slack:

1. **Cron prompt structure** — Include the DB IDs directly in the prompt (cron sessions are stateless), instructions for loading NOTION_API_KEY from `/opt/data/.env`, and the exact digest format you want. Be explicit: "read-only — do not create or modify anything in Notion."

2. **Digest format template** (standard 5-section layout):
   - 🔥 **URGENT** — Tasks with Urgent priority or blocked projects
   - 📌 **TODAY** — Items due today + daily-standing routines
   - 📅 **THIS WEEK** — Active items due within 7 days, grouped by priority
   - ⚠️ **OVERDUE / STALE** — Active items past due date
   - 📊 **PROJECT HEALTH** — Per-project: completion %, overdue count, next due

3. **Timezone note** — The server is Eastern (EDT/EST). 8 AM ET = 8 PM PH (Philippine). Use cron expression with Eastern hours; conversion is automatic.

4. **Existing digest job** — "Notion PM Daily Digest" (job `6d68be59459f`), runs `0 8 * * *` (8 AM ET / 8 PM PH), queries Projects + Tasks DBs.

## The Data Model: 25 Databases

### Phase 1 — Core Operations (12 DBs)

| DB | Key Properties | Relations |
|---|---|---|
| **Clients** | Company/Name, Contact Name/Email, Category, Offer, Industry, Status, Health Score (0-100), Onboarded Date, Upsell Ready ☑, NPS Score | → Projects, Meetings, Invoices, Tasks |
| **Projects** | Project Name, Status (Active/Completed/On Hold/Archived), Category, Offer, Start/End Date, PM, Priority | → Client, → Tasks |
| **Tasks** | Task Name, Status (Not started/In progress/Done), Priority (Urgent/High/Medium/Low), Assignee, Due Date, Source (Slack/Meeting/Agent), Tags, Sprint, Week | → Project, → Client |
| **Time Entries** | Duration, Date | → Project, → Team Member |
| **Invoices** | Invoice #, Amount, Status (Draft/Sent/Overdue/Paid/Payment Failed), Due Date, Paid Date, Category | → Client, → Project |
| **Meetings** | Title, Date, Type (Kickoff/Weekly/Strategy/Review/Sales Call), Sentiment (Positive/Neutral/Concerned/Negative), Attendees, Action Items Created ☑ | → Client, → Project |
| **Content Calendar** | Title, Type (LinkedIn/YouTube/Blog/Twitter Thread/Short-Form/Newsletter), Status, Publish Date, Platform, Author, Offer, Repurposed From | → Client |
| **Community Members** | Name, Status, Cert Level (Entry/Cert 1-3/Certified), Graduation Date, Client Landed ☑, Emails/DMs Sent, Jobs Applied | → Tasks, → Clients |
| **Team Members** | Name, Role, Status, Performance Score, Email | → Tasks, → Projects, → Time Entries |
| **Competitors** | Name, Website URL, LinkedIn URL, Last Checked, Threat Level | |
| **Agent Logs** | Agent, Action, Status (Success/Partial/Failed), Target DB, Target Row, Source, Timestamp, Error Details | |
| **Intel Briefings** | Date, Type (Daily/Weekly), Alert Level (Red/Yellow/Green), Content | |

### Phase 3 — Daily Ingest (8 DBs, under Operations Hub)

| DB | Key Properties | Volume | Relations |
|---|---|---|---|
| **Newsletter Archive** | Title, Source, Date, Type (AI/Crypto/Marketing/Community/Other), Sender, Subject, URL, Body Summary (≤500 chars), Read ☑, **full body in page content** | ~150/day | → AI Updates, → Content Ideas |
| **AI Updates** | Title, Date, Category (Tool/Feature/Model/Workflow/Trend), Summary, Link, Sentiment (Bullish/Neutral/Cautious) | ~10-20/day, deduped | → Source Newsletter(s) |
| **Content Ideas** | Title, Date, Idea Type (Tutorial/Hot Take/Case Study/Demo), Brief, Status (Inbox default) | ~3-10/day | → Source Newsletter, → Content Calendar |
| **Updates Log** | Title, Date, System (GitHub/Google Alerts/Bank/Vercel/Other), Severity (Info/Warn/Action), Summary, Resolved ☑ | ~5-15/day | |
| **Calendar Daily Brief** | Date (title), Yesterday Summary, Today Plan, Week Ahead | 1/day | → Past/Future Meetings |
| **EOD Reports** | Title ("{Author} EOD {Date}"), Date, Channel, Checklist % Complete, Wins, Blockers, Tomorrow Priorities, Source URL | ~1-3/day | → Author |
| **Tutor Curriculum** | Title, Day (number), Bucket (6 buckets), Concept, Exercise, Status | 90 rows (seeded once) | |
| **Tutor Lessons** | Title, Day (number), Date, Anchor Operation, Source (url) | 1/day | → Tutor Curriculum |

### Phase 4 — Sales & Growth (5 DBs, under Operations Hub)

| DB | Key Properties | ID |
|---|---|---|
| **🎯 Leads** | Name, Company, Title, Email, Phone, LinkedIn URL, Source (Skool/LinkedIn/Inbound/SDR Call/Cold Email/Referral/legacy email platform/Apify Scrape/Map.ai), Status (New→Researched→Contacted→Warm→Hot→Booked→Closed Won/Lost/Nurture/Unsubscribed), Campaign, Niche, Deal Value, Last Touch, Next Action, Emails Sent/Opened, Replied ☑, Reply Sentiment, Signal Tier (S/A/B/C), legacy email platform ID, Verified ☑ | `3543fa00-4c9d-8115-a286-ee7aa2c5a924` |
| **🌟 Influencers** | Name, Platform (multi: LinkedIn/X/YouTube/TikTok/Instagram/Substack/Skool/Podcast), Handle, Profile URL, Follower Count, Niche, Engagement Rate, Avg Likes/Comments, Collab Status (Identified→Reached Out→In Convo→Active Collab/Past Collab/Engagement Army/No Response), Collab Type (multi), Last Contact, Priority | `3543fa00-4c9d-8196-bd46-eb743053c9ac` |
| **📈 Growth Stats** | Week (title), Date, Platform, Followers, Followers Change, Impressions, Engagement Rate, Posts Published, New Leads, Meetings Booked, Emails Sent/Open Rate/Reply Rate, Calls Made/Connect Rate, Subscribers, Revenue | `3543fa00-4c9d-8199-b987-ee91f22b248b` |
| **📧 Cold Email Campaigns** | Campaign Name, legacy email platform ID, Offer (Power Partner/Direct Value/Capstone), Niche, Variant (A/B/C), Status (Drafted→Active→Paused→Stopped→Completed), Total Leads, Sent, Opens, Open Rate, Replies, Reply Rate, Bounces, Bounce Rate, Positive Replies, Meetings Booked, Start Date | `3543fa00-4c9d-81de-a9a4-e15bb7c7a34d` |
| **📡 Outreach Activities** | Activity, Type (Cold Email/Cold Call/LinkedIn DM/Follow-up/Meeting/Content Engagement/Referral Ask), Date, Channel (legacy email platform/Retell AI/LinkedIn/Manual), Outcome, Lead Email, Campaign Name | `3543fa00-4c9d-81f3-bd62-d0cd983d04e1` |

### Phase 5 — AGI-1 Self-Healing/Learning (5 DBs, under Operations Hub)

| DB | Key Properties | ID |
|---|---|---|
| **🩹 Healing Patterns** | Pattern ID, Category (import/syntax/runtime/build/test/network/permission/git/system/ai), Error Pattern, Fix Strategy, Fix Type, Confidence (%), Times Seen/Fixed, Source Repo, Genome Status (Local/Promoted/Demoted/Review), Agent | `3543fa00-4c9d-8137-b4d5-f59e9acf6d23` |
| **👁️ Learning Observations** | Observation, Type (instruction_ignored/repeated_error/skill_unused/correction/etc.), Repo, Agent, Evidence, Session ID, Processed ☑ | `3543fa00-4c9d-81a6-9d08-fe6eb642d045` |
| **💡 Learning Insights** | Insight, Type (rewrite_instruction/new_pattern/deprecate_pattern/etc.), Confidence (%), Evidence Count, Trace Evidence, Status (Pending/Applied/Deferred/Rejected) | `3543fa00-4c9d-817d-9557-cf322fa44ba0` |
| **🧬 Genome Changelog** | Mutation, Type (pattern_promoted/demoted/instruction_improved/etc.), Genome Version, Before/After, Source Repo, Agent, Pattern ID, Confidence (%) | `3543fa00-4c9d-8156-a614-e83a0fe1f022` |
| **🫀 Agent Health** | Report, Agent, Repo, Date, Patterns Active, Heals Today, Heal Success Rate, Observations Today, Insights Generated, Genome Contributions, G-Stack Score, AI Readiness Score, Session Count, Status (Healthy/Degraded/Unhealthy) | `3543fa00-4c9d-81e2-914d-c25a1d11f6bd` |

## Write Conventions (CRITICAL)

### Tier Ordering
Always write in dependency order to resolve relations:
1. **Tier 1 (primaries):** Team Members, Community Members, Clients, Projects, Competitors, Newsletter Archive, Influencers
2. **Tier 2 (extracts):** AI Updates, Content Ideas, EOD Reports, Leads (relate back to Tier 1)
3. **Tier 3 (events):** Meetings, Tasks, Invoices, Time Entries, Updates Log, Cold Email Campaigns, Outreach Activities
4. **Tier 4 (snapshots):** Calendar Daily Brief, Intel Briefings, Agent Logs, Growth Stats

### Idempotency
- **Always query before creating** — search by title/date/unique key to avoid duplicates
- **Never delete rows** — soft-delete only (archive or set Status)
- Use 7-day rolling dedup window for AI Updates (check title similarity)

### Property Gotchas
- **Checkboxes:** Use boolean `true`/`false` in the API
- **Dates:** Use ISO format `{"date": {"start": "2026-05-01"}}`
- **Rich text cap:** ~2000 chars max in properties — overflow goes to page body via two-phase write
- **Rate limiting:** Max 3 requests/sec. Batch 50 items with 1s pause between batches

### Two-Phase Writes (for content-heavy items)
For Newsletter Archive and other high-content DBs:
1. Create page with properties
2. Then PATCH `/v1/blocks/{page_id}/children` to add full body content

## Email → DB Routing Map

When ingesting email/content, route to the correct DB:

| Category | Target DB |
|---|---|
| `actionable_client` | Tasks (+ Clients update / Meetings) |
| `actionable_lead` | Clients (as Lead) + Tasks |
| `actionable_billing` | Invoices |
| `actionable_internal` | Tasks / Intel Briefings |
| `ai_newsletter` | Newsletter Archive (Type=AI) → extract to AI Updates + Content Ideas |
| `crypto_newsletter` | Newsletter Archive (Type=Crypto) — no extraction |
| `marketing_promo` | Newsletter Archive (Type=Marketing) |
| `automated_update` | Updates Log |
| `community_notification` | Newsletter Archive (Type=Community) |
| `personal_excluded` | DROPPED — never reaches Notion |

## Common API Operations

### Search
```python
# POST /v1/search
{"query": "page title", "filter": {"property": "object", "value": "page"}}
```

### Query Database
```python
# POST /v1/databases/{database_id}/query
{
  "filter": {"property": "Status", "select": {"equals": "Active"}},
  "sorts": [{"property": "Date", "direction": "descending"}]
}
```

### Create Page in Database
```python
# POST /v1/pages
{
  "parent": {"database_id": "xxx"},  # Use database_id here, NOT data_source_id
  "properties": {
    "Name": {"title": [{"text": {"content": "New Item"}}]},
    "Status": {"select": {"name": "Todo"}},
    "Date": {"date": {"start": "2026-05-01"}},
    "Priority": {"select": {"name": "High"}},
    "Done": {"checkbox": true}
  }
}
```

### Update Page Properties
```python
# PATCH /v1/pages/{page_id}
{"properties": {"Status": {"select": {"name": "Done"}}}}
```

### Add Content Blocks to Page
```python
# PATCH /v1/blocks/{page_id}/children
{
  "children": [
    {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Summary"}}]}},
    {"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Full content here..."}}]}},
    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Key point"}}]}}
  ]
}
```

### Get Database Schema
```python
# GET /v1/databases/{database_id}
# Returns all property definitions — use to validate before writes
```

## Property Type Formats

| Type | JSON Format |
|---|---|
| Title | `{"title": [{"text": {"content": "..."}}]}` |
| Rich text | `{"rich_text": [{"text": {"content": "..."}}]}` |
| Select | `{"select": {"name": "Option"}}` |
| Multi-select | `{"multi_select": [{"name": "A"}, {"name": "B"}]}` |
| Date | `{"date": {"start": "2026-01-15", "end": "2026-01-16"}}` |
| Checkbox | `{"checkbox": true}` |
| Number | `{"number": 42}` |
| URL | `{"url": "https://..."}` |
| Email | `{"email": "user@example.com"}` |
| Relation | `{"relation": [{"id": "page_id"}]}` |
| People | `{"people": [{"id": "user_id"}]}` |
| Status | `{"status": {"name": "In Progress"}}` |

## Documentation Philosophy

**Everything we do gets documented in Notion.** When completing any task:
1. Determine which DB(s) it belongs in
2. Check for existing entries (dedup)
3. Create/update with full context — titles, dates, summaries, links, relations
4. If content is long, use two-phase write (properties + body blocks)
5. Always set proper Status, Date, and Category fields
6. Link related items via Relations when possible

The goal: anything in Notion should be **findable later** by searching title, date, category, or status. Write as if future-you needs to reconstruct what happened from these records alone.
