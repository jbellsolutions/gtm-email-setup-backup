---
name: bird-email-api
description: Send and manage marketing/transactional email via Bird.com Email API (formerly MessageBird/SparkPost). Transmissions, sending domains, metrics, events, and suppression list management.
---

# Bird Email API

Bird (bird.com, formerly MessageBird/SparkPost) provides email sending through two API generations. This skill covers both, plus SMTP relay, sending domains, metrics, and provisioning diagnostics.

## Trigger conditions

Use this skill when the user wants to:
- Send emails (single or bulk) via Bird
- Set up or verify sending domains
- Check email metrics or delivery stats
- Manage suppression lists (unsubscribes, bounces)
- Query email events or webhook configuration
- Diagnose Bird email provisioning/activation issues
- Configure Bird SMTP relay for third-party tools (ListMonk, etc.)

## Two API Generations — Read This First

Bird has **two completely different APIs**. Identify which one your key supports before doing anything else.

| Generation | Key Format | Auth Header | Host (EU) | Host (US) |
|---|---|---|---|---|
| **Current (Bird Platform)** | `bk_eu1_...` / `bk_us1_...` | `Authorization: Bearer <key>` | `https://eu1.platform.bird.com` | `https://us1.platform.bird.com` |
| **Legacy (SparkPost/MessageBird)** | Short alphanumeric (`dqp8Ykhz...`) | `Authorization: AccessKey <key>` | `https://email.eu-west-1.api.bird.com/api` | `https://email.us-west-1.api.bird.com/api` |

**How to tell which key you have:** Keys with `bk_` prefix are current platform keys. Short alphanumeric strings without a prefix are legacy keys. The legacy root (`email.eu-west-1.api.bird.com/`) returns 200 with a careers page — this is NOT email functionality, just the host existing.

**⚠️ Critical:** A legacy key may authenticate on the legacy root (200 OK) but still get 401 on all email/Reach endpoints. This means the key exists but has no email product permissions. See "Provisioning Diagnostics" below.

## Prerequisites

Before any operation, confirm these with the user:

1. **API Key** — stored as `BIRD_API_KEY` in `~/home/.env` (NOT the main `.env`)
2. **Workspace ID** — UUID, found at `app.bird.com → Settings → General` or in the dashboard URL
3. **Region** — EU or US (determines base URL). Key prefix tells you: `bk_eu1_` = EU, `bk_us1_` = US
4. **Sending Domain** — must be verified in Bird before sending
5. **Email channel installed** — Email must be activated as a channel in the Bird dashboard. If DKIM won't generate or default domains show "Not healthy," email is not provisioned. See "Provisioning Diagnostics."

## Current API (Bird Platform)

### Send Email

**POST** `/v1/email/messages`

```json
{
  "from": "sender@yourdomain.com",
  "to": ["recipient@example.com"],
  "subject": "Hello World",
  "html": "<h1>Hello</h1><p>Email body</p>"
}
```

Response: `202 Accepted` with message ID (`em_...`). Delivery is async — check status via GET or webhooks.

### Sandbox Testing

No domain verification needed for testing:
- **From:** `onboarding@messagebird.dev` (Bird's shared onboarding domain)
- **To:** `delivered@messagebird.dev` (always delivers, deterministic)
- **Bounce test:** `bounce@messagebird.dev`

### Other Current Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/email/messages` | List messages |
| GET | `/v1/email/messages/{id}` | Get message status |
| GET | `/v1/email/messages/{id}/recipients` | List recipients |
| GET | `/v1/email/messages/{id}/events` | List events for a message |
| GET | `/v1/email/stats/summary` | Aggregate stats |
| GET | `/v1/email/stats/daily` | Daily sending stats |
| GET | `/v1/email/stats/hourly` | Hourly stats |
| GET | `/v1/suppressions` | List suppressions |
| POST | `/v1/suppressions` | Add suppression |
| DELETE | `/v1/suppressions/{id}` | Remove suppression |

Sending domains, inbound email, contacts, and audiences are managed via the dashboard, not the public API (per Bird docs).

## Legacy API (SparkPost/MessageBird)

All endpoints require `{workspaceId}` as a path parameter.

### Transmissions

**POST** `/workspaces/{workspaceId}/reach/transmissions`

```json
{
  "content": {
    "from": "sender@yourdomain.com",
    "subject": "Hello World",
    "html": "<h1>Hello</h1>",
    "text": "Hello"
  },
  "recipients": [
    {"address": {"email": "recipient@example.com", "name": "Name"}}
  ]
}
```

### Sending Domains

- `GET /workspaces/{workspaceId}/reach/sending-domains` — list
- `POST /workspaces/{workspaceId}/reach/sending-domains` — create (`{"domain":"...", "generate_dkim":true, "dkim_key_length":1024}`)
- `POST /workspaces/{workspaceId}/reach/sending-domains/{domain}/verify` — verify

### Metrics & Suppressions

- `GET /workspaces/{workspaceId}/reach/metrics` — aggregate stats
- `GET /workspaces/{workspaceId}/reach/suppression-list` — list suppressed

## SMTP Relay

Bird's email product supports SMTP relay (confirmed in Bird docs). Based on the SparkPost backend:

| Setting | Value |
|---|---|
| Host (EU) | `smtp.eu.sparkpostmail.com` |
| Host (US) | `smtp.sparkpostmail.com` |
| Port | `587` or `2525` (alt if 587 blocked) |
| Encryption | `STARTTLS` |
| Auth protocol | `AUTH LOGIN` |
| Username | `SMTP_Injection` |
| Password | API key with "Send via SMTP" permission |

The SMTP password is an API key (not a separate SMTP password). Create it from the Bird/SparkPost dashboard with "Send via SMTP" scope enabled.

**For ListMonk integration:** Set ListMonk → Settings → SMTP to the Bird SMTP relay values. The password field gets the API key with SMTP permission. See `references/smtp-setup-listmonk.md` for the full migration procedure.

## Provisioning Diagnostics

If you suspect Bird's email product is not fully activated, check these signals:

1. **API 401 on all email endpoints** — Key authenticates on root but gets 401 on every `/reach/` or `/v1/email/` endpoint. Means email product is not provisioned for the workspace or the key lacks email scope.
2. **Default domains unhealthy** — `birdemailbox.com` domains show "Not healthy" in dashboard. Bird controls these — if email were active, they'd be healthy.
3. **DKIM won't generate** — Adding a sending domain shows DKIM as "Unavailable" with a Retry button. Retrying, changing key size, waiting — none of it works. The key-generation backend is not running.
4. **Old-style key without `bk_` prefix** — Legacy keys may not work with the current platform API at all.

### What's Needed to Activate

This is a dashboard/billing task for the account owner (Justin):
1. Check `Channels → Email` for an "Install" or "Activate" button
2. Check `Settings → Billing` for plan requirements
3. Create a NEW API key at `Developers → API Keys` (will have `bk_eu1_` prefix) with email scopes
4. If nothing obvious: contact `support@bird.com` with workspace UUID and the three symptoms above

Do NOT purchase anything — hand the diagnosis to the user.

## DNS Records for Sending Domains

When Bird generates DNS records for a sending domain, you get 4 records:

| Record | Type | Example |
|---|---|---|
| Bounce | CNAME | `bounce.yourdomain.com` → `eu.sparkpostmail.com` (EU) or `sparkpostmail.com` (US) |
| Tracking | CNAME | `track.yourdomain.com` → `v2.spgo.io` |
| DKIM | TXT/CNAME | `selector._domainkey.yourdomain.com` → key material (fails to generate if not provisioned) |
| DMARC | TXT | `_dmarc.yourdomain.com` → `v=DMARC1; p=none;` |

Publish all 4 at the DNS provider (Hostinger for this account). DKIM will only appear after email product is fully activated.

## Core Endpoints

All endpoints require `{workspaceId}` as a path parameter (UUID format).

### Transmissions (send email)

**POST** `/workspaces/{workspaceId}/reach/transmissions`

Send email to one or thousands of recipients. Each transmission is a collection of recipients + content.

**Minimal payload (inline content):**

```json
{
  "content": {
    "from": "sender@yourdomain.com",
    "subject": "Hello World",
    "html": "<h1>Hello</h1><p>Email body</p>",
    "text": "Hello - Email body"
  },
  "recipients": [
    {"address": {"email": "recipient@example.com", "name": "Recipient Name"}}
  ]
}
```

**Key fields:**
- `content.from` — must use a verified sending domain; can be string or `{email, name}`
- `content.subject` — UTF-8, no RFC2047 encoding
- `content.html` / `content.text` — at least one required
- `content.reply_to` — optional Reply-To address
- `recipients[].address.email` — valid email
- `recipients[].rcpt_type` — `"to"` (default), `"cc"`, or `"bcc"`
- `options.open_tracking` / `options.click_tracking` — engagement tracking (bool)
- `options.transactional` — `true` for transactional (avoids suppression)
- `options.sandbox` — use sandbox domain for testing
- `campaign_id` — tag transmissions for reporting (max 64 chars)
- `metadata` — arbitrary key/value, available in webhooks
- `substitution_data` — key/value pairs for template personalization

**Content limit:** 20MB total (text + html + attachments + inline images)

**Response (200):**
```json
{
  "results": {
    "id": "transmission-id",
    "total_accepted_recipients": 1,
    "total_rejected_recipients": 0
  }
}
```

**DELETE** `/workspaces/{workspaceId}/reach/transmissions?campaign_id=<id>`
Cancel all scheduled transmissions in a campaign. Returns 204, processes async.

### Sending Domains

**GET** `/workspaces/{workspaceId}/reach/sending-domains` — list all
**POST** `/workspaces/{workspaceId}/reach/sending-domains` — create
**GET** `/workspaces/{workspaceId}/reach/sending-domains/{domain}` — retrieve
**PUT** `/workspaces/{workspaceId}/reach/sending-domains/{domain}` — update
**DELETE** `/workspaces/{workspaceId}/reach/sending-domains/{domain}` — delete
**POST** `/workspaces/{workspaceId}/reach/sending-domains/{domain}/verify` — verify (DKIM, CNAME, mailbox)

**Create payload:**
```json
{
  "domain": "mail.yourdomain.com",
  "generate_dkim": true,
  "dkim_key_length": 1024
}
```

**Verification methods:**
- `dkim_verify: true` — checks DKIM DNS record
- `cname_verify: true` — checks CNAME record pointing to `sparkpostmail.com` (US) or `eu.sparkpostmail.com` (EU)
- Mailbox verification — sends verification link to abuse@/postmaster@/custom mailbox

Domains must be verified within 2 weeks or they're auto-removed.

### Metrics

**GET** `/workspaces/{workspaceId}/reach/metrics` — aggregate stats
**GET** `/workspaces/{workspaceId}/reach/metrics/time-series` — time-bucketed stats

40+ metrics available: `count_targeted`, `count_injected`, `count_sent`, `count_accepted`, `count_delivered`, `count_rendered`, `count_clicked`, `count_bounce`, `count_spam_complaint`, etc.

Data retained for 6 months. Supports filtering by campaign, domain, template, etc.

### Events

Webhook-based event tracking for delivery, open, click, bounce, spam complaint, etc.

### Suppression List

Manage unsubscribes and bounces — list, add, delete suppressed addresses.

Sending domains, inbound email, contacts, and audiences are managed via the dashboard, not the public API (per Bird docs).

## Testing Connectivity

Test BOTH API generations to determine which one your key supports:

```python
import urllib.request, json

BIRD_API_KEY = "your-key"
WORKSPACE_ID = "your-workspace-uuid"

# Test 1: Current platform API (Bearer auth)
for host, region in [("https://eu1.platform.bird.com", "EU"), ("https://us1.platform.bird.com", "US")]:
    try:
        req = urllib.request.Request(f"{host}/v1/email/messages?limit=1")
        req.add_header("Authorization", f"Bearer {BIRD_API_KEY}")
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"{region} Platform API: {resp.status} — WORKS")
    except urllib.error.HTTPError as e:
        print(f"{region} Platform API: {e.code} — {e.read().decode()[:100]}")

# Test 2: Legacy API (AccessKey auth)
base = "https://email.eu-west-1.api.bird.com/api"
try:
    req = urllib.request.Request(f"{base}/workspaces/{WORKSPACE_ID}/reach/sending-domains")
    req.add_header("Authorization", f"AccessKey {BIRD_API_KEY}")
    resp = urllib.request.urlopen(req, timeout=10)
    print(f"Legacy API: {resp.status} — WORKS")
except urllib.error.HTTPError as e:
    print(f"Legacy API: {e.code} — {e.read().decode()[:100]}")

# Test 3: Root check (host exists ≠ email works)
try:
    req = urllib.request.Request("https://email.eu-west-1.api.bird.com/")
    req.add_header("Authorization", f"AccessKey {BIRD_API_KEY}")
    resp = urllib.request.urlopen(req, timeout=10)
    body = resp.read().decode()
    if "careers" in body.lower():
        print("Legacy root: 200 but only returns careers page — NOT email functionality")
except Exception as e:
    print(f"Legacy root: {e}")
```

If both APIs return 401 on email endpoints, email is not provisioned. See "Provisioning Diagnostics."

## Pitfalls

1. **Two API generations** — Always check if your key has `bk_` prefix (current) or not (legacy). Old keys get 401 on the new platform API; new keys won't work on legacy endpoints.
2. **Legacy root 200 ≠ email working** — `email.eu-west-1.api.bird.com/` returns 200 with a careers page. This only means the host exists, NOT that your key has email permissions. Test an actual email endpoint.
3. **US endpoint unreachable from some VPS networks** — always test both regions; fall back to EU if US times out.
4. **Workspace ID is required for every legacy call** — no global discovery endpoint; user must provide it. There is NO programmatic way to list workspaces or discover the ID from the API key alone. The user must find it at `app.bird.com → Settings → General` or in the dashboard URL.
5. **Sending domain must be verified before use** — transmissions with unverified domains are rejected.
6. **DKIM generation requires email provisioning** — If DKIM shows "Unavailable" in the dashboard, the email product is not fully activated. No amount of retrying or key-size changes will fix it. See "Provisioning Diagnostics."
7. **Email channel must be installed** — Bird treats email as a channel that gets activated per workspace. Check `Channels → Email` in the dashboard. If it's not installed or shows errors, email won't work regardless of API key validity.
8. **Content is capped at 20MB** — total across html, text, attachments, inline images.

## Credentials Location

Bird API key is stored in `~/home/.env` (NOT the main `/opt/data/.env`), as `BIRD_API_KEY`. AutoSend key is in the same file as `AUTOSEND_API_KEY`.
