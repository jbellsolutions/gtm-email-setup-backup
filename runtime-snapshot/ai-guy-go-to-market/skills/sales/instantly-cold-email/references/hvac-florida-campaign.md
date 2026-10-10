# HVAC Florida Campaign — May 2026

## Campaign Summary

| Field | Value |
|---|---|
| **Campaign Name** | `home-services-hvac-florida` |
| **Instantly ID** | 3318534 (replaced 3314165 on May 11) |
| **Created** | May 11, 2026 (recreated after custom-fields bug) |
| **Status** | PAUSED |
| **Leads** | 1,170 (from 1,200 scraped, 1,180 qualified) |
| **Inboxes** | TBD (none assigned yet to recreated campaign) |
| **Schedule** | Mon-Fri 8AM-5PM ET |
| **Strategy** | Florida-only HVAC contractors with per-lead personalized copy |

**⚠️ ISSUE:** Recreated campaign (3318534) has `send_as_plain_text: false` — must be changed to `true` before starting. Instantly also auto-capped `max_leads_per_day` to 500 on the recreated campaign.

**⚠️ HISTORY:** Original campaign 3314165 was deleted on May 11 after the custom-fields bug silently killed all sends for 7+ hours. Leads were re-uploaded to 3318534 but no inboxes assigned yet. All leads in 3318534 are STARTED/notStarted with no message history.

## Lead Scraping

- **Actor:** PipelineLabs (`kVYdvNOefemtiDXO5`)
- **Filters:** `companyKeywordIncludes: ["hvac", "heating", "air conditioning", "ac repair", "plumbing", "roofing"]`, `seniorityIncludes: ["owner", "c_suite", "partner"]`, Florida
- **Initial batch:** 200 leads scraped May 10 (dataset `zWccLQI31IzKi2RYe`)
- **Full batch:** 1,200 leads scraped May 11 (run `OAsW4AitUKh6jf66T`, dataset `N5X7B3QmFxNr3APgH`)
- **City distribution:** Fort Lauderdale (175), Orlando (155), Tampa (147), Jacksonville (96)

## Qualification

- **Script:** `/opt/data/scripts/qualify_leads.py`
- **1,200 raw → 1,180 qualified (98% pass rate)**
- Rejected: 19 generic emails, 1 bad company name

## Email Verification

- **Apify verifier:** `xlWThR6pfc9ka55eH`
- **12 parallel batches of 100** launched, ~50% returned results
- **600 verified:** 240 good (70+), 360 risky (40-69), 0 bad (<40)
- **580 unverified** included with flag — PipelineLabs quality is high for HVAC niche

## Personalization

- **Script:** `/opt/data/scripts/hvac_florida_personalize.py`
- **Signals:** role (owner/vp/manager) → segment (owner_op/commercial/multi_truck), location → market (coastal/large_metro/small_market), city name for local hooks
- **Variant hooks:**
  - Coastal: "Salt air. Hurricanes. 10-month season."
  - Large metro: "Tighter margins. Higher stakes. The systems matter more."
  - Small market: "Reputation is everything. One bad review and the whole town knows."
  - Owner-op: "Build repeatable systems" angle
  - Commercial: "Margins + systems" angle
- **Spam check:** Built-in, with city-name whitelist (e.g., "New Port Richey" no longer flagged for "new")
- **Output format:** `custom_fields.personalized_email_1/2/3` per lead

## Sequences (Campaign-Level)

- **Email 1:** Subject "HVAC in Florida", body `{{custom_fields.personalized_email_1}}`
- **Email 2:** Subject "Re: HVAC in Florida", body `{{custom_fields.personalized_email_2}}`
- **Email 3:** Subject "Re: HVAC in Florida", body `{{custom_fields.personalized_email_3}}`
- **Sequence IDs:** 8529854, 8529855, 8529856

## Settings (Current — May 11 Post-Recreation)

- `send_as_plain_text`: **false** ⚠️ MUST FIX TO true BEFORE STARTING
- `track_settings`: DONT_EMAIL_OPEN, DONT_LINK_CLICK ✅
- `stop_lead_settings`: REPLY_TO_AN_EMAIL ✅
- `enable_ai_esp_matching`: true ✅
- `max_leads_per_day`: 500 (auto-capped from default, may need adjustment)
- `follow_up_percentage`: 100 ✅
- `scheduler_cron_value`: Mon-Fri 8AM-5PM ET ✅

## Settings (Original 3314165 — DELETED)**

- `send_as_plain_text`: true
- `track_settings`: DONT_EMAIL_OPEN, DONT_LINK_CLICK
- `stop_lead_settings`: REPLY_TO_AN_EMAIL
- `enable_ai_esp_matching`: true
- `max_leads_per_day`: 500 (auto-capped from 1,000)
- `follow_up_percentage`: 50 (auto-capped from 100)
- `scheduler_cron_value`: Mon-Fri 8AM-5PM ET

**⚠️ THE BUG:** Original campaign 3314165 had the full email body stored in `{{custom_fields.personalized_email_1/2/3}}` custom fields (900+ chars each). Instantly's render engine cannot handle large custom field values as sequence email body content — ALL leads stayed STARTED with zero sends, no error anywhere. This was the custom-fields-silent-kill bug.

## Upload

- **Batch 1:** 1,000 attempted → 993 uploaded
- **Batch 2:** 180 attempted → 177 uploaded
- **Total unique leads:** 1,170

## Key Files

- Raw leads: `/tmp/florida_hvac_raw.json`
- Qualified: `/tmp/florida_hvac_qualified_v2.json`
- Email scores: `/tmp/hvac_email_scores.json`
- Upload JSON: `/tmp/florida_hvac_upload.json`
- Personalization script: `/opt/data/scripts/hvac_florida_personalize.py`
