# Owned Audiences Lead Tracking Spreadsheet

## Overview

Justin wants a Google Sheet tracking ALL Owned Audiences leads across all three campaigns (#3617053 Coaching, #3652623 HVAC, #3652624 Recruiting) with daily updates. This reference documents the schema, the heat system, and the cron-driven update workflow.

## Sheet Structure

One tab per campaign: `Coaching`, `HVAC`, `Recruiting`. Each tab has identical columns:

### Columns

| Col | Header | Type | Source |
|-----|--------|------|--------|
| A | Name | text | Instantly lead_first_name + lead_last_name |
| B | Email | text | Instantly lead_email |
| C | Company | text | Instantly company_name |
| D | Reply Date | date | Instantly last_reply_time |
| E | Classification | dropdown | Classifier: positive_interested, positive_soft, neutral_question, negative_notfit, negative_notnow, hostile, unsubscribe, ooo, auto_responder |
| F | Status | dropdown | booked, replied, plan_built, awaiting_followup, declined_after_positive, dead |
| G | Heat | computed | See heat system below |
| H | Phone | text | From email signature or ScraperCity lookup |
| I | Website | text | From email signature or Instantly company_url |
| J | LinkedIn | text | From Instantly linkedin_profile |
| K | Called 1 | checkbox/date | First call attempt |
| L | Called 2 | checkbox/date | Second call attempt |
| M | Called 3 | checkbox/date | Third call attempt |
| N | Called 4 | checkbox/date | Fourth call attempt |
| O | Called 5 | checkbox/date | Fifth call attempt |
| P | Booked | checkbox | Meeting booked on Cal.com |
| Q | Notes / Behaviors | text | Free-form: follow-up dates, call outcomes, behaviors tracked |

### Heat System

- 🔥 **BOOKED**: status = "booked"
- ⭐ **HOT**: status = "plan_built" or "replied" (case study/plan sent, awaiting response)
- 🟡 **WARM**: classification starts with "positive" but not yet replied to
- 📋 **NEUTRAL**: classification = "neutral_question" or unclassified
- 🤖 **AUTO**: classification = "auto_responder" or "ooo"
- ❄️ **COLD**: classification in ("negative_notfit", "hostile", "unsubscribe", "declined_after_positive")

## Source Data

### Primary: Instantly State File

`/tmp/owned_audiences_followups.json` — 91 tracked leads with status, classification, and timestamps. Updated by the monitoring pipeline.

### Secondary: Instantly Inbox

`Instantly inbox replies --format json` — live inbox entries. Used to discover new leads not yet in the state file. Paginate 5 pages (100 entries) for daily sweeps.

### Phone/Social Enrichment

Instantly leads lack phone/social data (`phone_number` is null, `linkedin_profile` is null). Two sources:
1. **Email signatures**: Parse reply bodies with regex for phone patterns (`(?:\+1[-\s]?)?\(?\d{3}\)?[-\s\.]?\d{3}[-\s\.]?\d{4}`) and LinkedIn URLs
2. **ScraperCity** (when available): Batch lookup by email domain

## Daily Cron Workflow

### Phase 1: Pull New Data (runs ~11 PM ET)

1. Pull Instantly inbox pages 0-4 (100 entries)
2. Filter to OA campaigns: #3617053, #3652623, #3652624
3. For each new entry not in the state file, pull message history and classify
4. Update `/tmp/owned_audiences_followups.json` with new leads

### Phase 2: Update Spreadsheet (runs after Phase 1)

1. Load current sheet data from Google Sheets
2. Load state file data
3. For each lead in state file:
   - If email exists in sheet → update row (status, classification, reply_date, heat)
   - If email NOT in sheet → append new row
4. Re-sort by heat (booked → hot → warm → neutral → auto → cold)
5. Write back to sheet

### Phase 3: Flag Changes

- New positives: highlight row yellow
- New bookings: highlight row green
- Status changes (e.g., replied → declined): highlight row orange
- Leads with Called 5 checked but no booking: mark for review

## Composio Implementation

Use the Composio MCP server to operate on Google Sheets. The server must be configured in `/opt/data/config.yaml`:

```yaml
mcp_servers:
  composio:
    url: https://connect.composio.dev/mcp
    timeout: 180
    headers:
      x-consumer-api-key: [REDACTED]
```

After Hermes restart, tools appear as `mcp_composio_*`. Key operations:
- `mcp_composio_google_sheets_create_spreadsheet` — create the tracking sheet
- `mcp_composio_google_sheets_write_values` — write initial data
- `mcp_composio_google_sheets_read_values` — read for comparison during updates
- `mcp_composio_google_sheets_append_values` — add new rows

### First-Run Setup

1. Create spreadsheet: "Owned Audiences Lead Tracking"
2. Create tabs: Coaching, HVAC, Recruiting
3. Write header rows
4. Populate with data from state file

## Duplicate Prevention

- Match by email (case-insensitive) — email is the primary key
- Before appending, read existing emails from column B
- If email exists, update row; if not, append
- Track `known_reply_message_ids` from state file to avoid re-processing the same reply