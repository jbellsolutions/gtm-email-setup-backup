---
name: outflo-linkedin
description: "OutFlo LinkedIn automation — campaigns, lead lists, messaging, accounts, analytics. Use for LinkedIn outreach at scale via REST API."
version: 1.0.0
author: jbellsolutions
metadata:
  hermes:
    tags: [OutFlo, LinkedIn, Outreach, Sales, Automation]
prerequisites:
  env_vars: [OUTFLO_API_KEY]
---

# OutFlo LinkedIn Automation

OutFlo supports LinkedIn content posting and related operations. The currently verified API for this workspace is the posting API at `https://api.outflo.io/api/public/v1/posting`. The older outreach endpoints documented below under `https://live.outflo.in/api/public/` are legacy/unverified and must not be used without re-verification.

## Current workspace verification

Verified endpoints include `/accounts`, `/posts`, `/usage`, `/entitlement`, and `/calendar` (calendar reads require ISO-8601 `from` and `to` query parameters). The safe workspace client is `/opt/data/linkedin-content-system/scripts/outflo_posting.py`. Draft-first and human approval are required before publication.

## Authentication

Every request needs an `x-api-key` header. The API key is workspace-scoped.

```
x-api-key: YOUR_API_KEY
```

Justin's key is stored in `OUTFLO_API_KEY` env var. Generate/rotate keys at Settings → Integration → OutFlo API in the OutFlo dashboard.

---

## Endpoints

### Campaigns

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/campaigns?status=&search_text=` | List campaigns (status: active, paused, draft, completed) |
| POST | `/campaigns` | Create campaign with sequence, senders, timezone |
| POST | `/campaigns/launch?campaign_id=ID` | Launch/activate a campaign |
| POST | `/campaigns/pause?campaign_id=ID` | Pause a running campaign |
| POST | `/campaigns/resume?campaign_id=ID` | Resume a paused campaign |
| PUT | `/campaigns/sequence?campaign_id=ID` | Update campaign sequence steps |
| GET | `/campaigns/ID/leads?search_text=` | List leads in a campaign |

#### Create Campaign

```bash
curl -X POST https://live.outflo.in/api/public/campaigns \
  -H "x-api-key: $OUTFLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Campaign Name",
    "senderUrls": ["https://www.linkedin.com/in/your-profile/"],
    "timeZone": "EST",
    "sequence": {
      "sequenceSteps": {
        "0": {
          "actionType": "SEND_CONNECTION_REQUEST",
          "delay": 0,
          "standardConnectionNote": "Hi {firstName}, would love to connect!"
        },
        "1": {
          "actionType": "SEND_MESSAGE",
          "delay": 1440,
          "messageText": "Thanks for connecting, {firstName}!"
        }
      }
    }
  }'
```

**Action types:** `SEND_CONNECTION_REQUEST`, `SEND_MESSAGE`
**Delay:** minutes (1440 = 1 day)
**Variables:** `{firstName}`, `{lastName}`, `{companyName}`, `{jobTitle}`, plus any custom fields

#### Launch / Pause / Resume

```bash
curl -X POST "https://live.outflo.in/api/public/campaigns/launch?campaign_id=CAMPAIGN_ID" \
  -H "x-api-key: $OUTFLO_API_KEY"
```

Identical pattern for pause/resume — just change the endpoint path.

---

### Lead Lists

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/lead-lists?page=1&limit=25` | List lead lists |
| POST | `/lead-lists` | Create lead list (multipart: name + optional CSV) |
| POST | `/lead-lists/leads` | Add leads to existing list (JSON or CSV) |

#### Create Lead List

```bash
curl -X POST https://live.outflo.in/api/public/lead-lists \
  -H "x-api-key: $OUTFLO_API_KEY" \
  -F "name=My Lead List" \
  -F "csv=@/path/to/leads.csv"
```

CSV requirements: max 50MB, must have a column with LinkedIn profile URLs. Auto-deduplicated by LinkedIn URL.

#### Add Leads to List

```bash
curl -X POST https://live.outflo.in/api/public/lead-lists/leads \
  -H "x-api-key: $OUTFLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "leadListId": "550e8400-e29b-41d4-a716-446655440000",
    "leads": [
      {
        "linkedinUrl": "https://www.linkedin.com/in/profile/",
        "firstName": "John",
        "lastName": "Doe",
        "company": "Acme Corp"
      }
    ]
  }'
```

---

### Add Leads to Campaign

```bash
curl -X POST "https://live.outflo.in/api/public/campaign/addleadtoactivecampaign/{campaignId}" \
  -H "x-api-key: $OUTFLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "linkedinUrl": "https://www.linkedin.com/in/profile-url/",
    "firstName": "John",
    "lastName": "Doe",
    "company": "TechCorp",
    "jobTitle": "VP Sales",
    "email": "john@techcorp.com",
    "phone": "+1-555-1234",
    "location": "New York"
  }'
```

Custom fields supported: `companySize`, `technologies`, `fundingStage`, `sourceSystem`, `leadPriority`, `leadScore`, etc. Pass any key-value pairs — they become template variables.

---

### LinkedIn Accounts (Login)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/accounts/login` | Connect a LinkedIn account |
| GET | `/accounts/status/:accountId` | Poll connection status |
| POST | `/accounts/checkpoint/resend` | Resend OTP code |
| POST | `/accounts/checkpoint/solve` | Submit OTP code |

---

### Send LinkedIn Messages

```bash
curl -X POST https://live.outflo.in/api/public/conversations/reply \
  -H "Content-Type: application/json" \
  -H "x-api-key: $OUTFLO_API_KEY" \
  -d '{
    "senderProfileUrl": "https://www.linkedin.com/in/SENDER_PROFILE",
    "receiverLinkedInUrl": "https://www.linkedin.com/in/RECEIVER_PROFILE",
    "text": "Hello from public API",
    "attachments": []
  }'
```

Works for both new conversations and replies to existing threads.

---

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/overview?start_date=&end_date=&campaign_id=&account_id=&status=&timezone=UTC` | Overview metrics |
| GET | `/analytics/timeseries?start_date=&end_date=&bucket=weekly&metric=replies_received&timezone=UTC` | Timeseries data |
| GET | `/analytics/campaigns?start_date=&end_date=&status=active` | Campaign table |
| GET | `/analytics/senders?start_date=&end_date=&rolling=false` | Sender performance |
| GET | `/campaigns/ID/analytics/overview?timezone=UTC` | Per-campaign overview |
| GET | `/campaigns/ID/analytics/funnel?reply_status=awaiting_reply` | Campaign funnel |
| GET | `/campaigns/ID/analytics/sequences` | Sequence analytics |
| GET | `/campaigns/ID/analytics/tags?tag_ids=&reply_status=` | Tag analytics |

---

## Campaign Lifecycle

1. **Create Lead List** (optional) — POST `/lead-lists`
2. **Create Campaign** — POST `/campaigns` with sequence, senders, timezone
3. **Update Sequence** (optional) — PUT `/campaigns/sequence`
4. **Launch Campaign** — POST `/campaigns/launch`
5. **Add Leads** — POST `/campaign/addleadtoactivecampaign/{id}` throughout
6. **Manage** — Pause/Resume as needed
7. **Monitor** — Analytics endpoints for performance

## Pitfalls

- Campaign IDs are UUIDs. Keep them after creation — you'll need them for everything.
- Sender URLs must be LinkedIn profiles already connected to OutFlo (via `/accounts/login`).
- Launch fails if no sender accounts are connected.
- `delay` is in minutes. 1440 = 1 day, 2880 = 2 days.
- Template variables like `{firstName}` in messages use the lead data you provide. Make sure firstName fields are populated when adding leads.
- Lead lists auto-deduplicate by LinkedIn URL. If you add the same URL twice, it's silently skipped.
- The add-leads endpoint accepts arbitrary custom fields — use them to enrich templates.