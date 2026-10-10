---
name: autosend
description: AutoSend email platform — send transactional/marketing emails, manage campaigns, domains, contacts, templates, automations. Direct REST API access.
category: email
---

# AutoSend Email Platform

AutoSend is a SendGrid alternative with volume-based pricing. Use this skill for all AutoSend operations via REST API.

## Quick Reference

| Item | Value |
|------|-------|
| Base URL | `https://api.autosend.com/v1` |
| Auth header | `Authorization: Bearer $AUTOSEND_API_KEY` |
| Content-Type | `application/json` |
| API key prefix | `ASA_` = org admin (needs `x-project-id`), `AS_` = project-scoped |
| Dashboard | https://autosend.com/dashboard |
| API Keys page | https://autosend.com/account/api-key |
| MCP Server URL | `https://mcp.autosend.com/` (remote, streamable HTTP, OAuth) |

## Authentication

Our key is an **org admin key** (`ASA_` prefix). It requires `x-project-id` header on most calls. Get the project ID from `https://autosend.com/dashboard` → select project → URL contains the ID.

If `x-project-id` is unknown, ask Justin which project to target. For day-to-day operations, consider creating a project-scoped key (`as_` prefix) from https://autosend.com/account/api-key.

## API Operations

### Mail (Send Email)

**Send single email:** `POST /v1/mails/send`
```json
{
  "from": {"email": "hello@domain.com", "name": "Sender Name"},
  "to": {"email": "recipient@example.com", "name": "Recipient"},
  "subject": "Subject line",
  "html": "<p>HTML body</p>",
  "text": "Plain text fallback",
  "cc": [{"email": "cc@example.com", "name": "CC Name"}],
  "bcc": [{"email": "bcc@example.com"}],
  "replyTo": {"email": "reply@domain.com"},
  "templateId": "tmpl_xxx",
  "dynamicData": {"var1": "value1"},
  "attachments": [{"filename": "file.pdf", "content": "base64..."}]
}
```

**Bulk send (max 100):** `POST /v1/mails/bulk`
```json
{
  "from": {"email": "hello@domain.com", "name": "Sender"},
  "subject": "Subject",
  "html": "<p>Body</p>",
  "templateId": "tmpl_xxx",
  "dynamicData": {"sharedVar": "value"},
  "recipients": [
    {"email": "one@example.com", "name": "One", "dynamicData": {"custom": "val1"}},
    {"email": "two@example.com", "name": "Two"}
  ]
}
```
Response: `{"success": true, "data": {"batchId": "batch_xxx", "totalRecipients": N, "successCount": N, "failedCount": N}}`

### Domains

**List domains:** `GET /v1/domains`
**Add domain:** `POST /v1/domains` — `{"domain": "example.com", "regionKey": "us-east-1"}`
**Get domain:** `GET /v1/domains/:id`
**Verify domain:** `POST /v1/domains/:id/verify`
**Delete domain:** `DELETE /v1/domains/:id`

After adding a domain, configure DNS records (DKIM, SPF, DMARC) shown in the response, then call verify.

### Domain Warmup (Gradual Send)

Domain warmup is handled when creating/scheduling campaigns via the `sendMode: "gradual"` option and Gradual Send settings. Key parameters:
- `warmupStartVolume`: 25, 50, 100, 250, or 500 emails on day 1
- `warmupIncrement`: `"fixed"`, `1.25`, `1.5`, `1.75`, or `2.0` (multiplier)
- `safetyThreshold`: `"conservative"` (2% bounce / 0.05% complaint), `"balanced"` (3% / 0.07%), `"aggressive"` (5% / 0.1%)

Warmup tips:
- Start low (50 emails, 1.25x increment) for brand new domains
- Clean your list before starting
- Disable open tracking during warmup (tracking pixels can trigger spam filters)
- AutoSend auto-pauses if bounce/complaint thresholds exceeded

### Campaigns

**List:** `GET /v1/campaigns?status=draft&page=1&limit=20`
**Get:** `GET /v1/campaigns/:id`
**Create:** `POST /v1/campaigns`
```json
{
  "name": "Campaign Name",
  "subject": "Subject line",
  "previewText": "Preview text (max 140 chars)",
  "from": {"email": "hello@domain.com", "name": "Sender Name"},
  "replyTo": "reply@domain.com",
  "templateId": "tmpl_xxx",
  "toLists": ["list_id_1"],
  "toSegments": ["segment_id_1"],
  "excludeLists": ["list_id_2"],
  "sendMode": "immediate",      // "immediate", "scheduled", or "gradual"
  "scheduledAt": "2026-07-20T14:00:00Z",
  "publish": true,
  "sendNow": true,              // true = send immediately when publish=true
  "trackingClick": true,
  "trackingOpen": true
}
```
**Update:** `PATCH /v1/campaigns/:id`
**Delete:** `DELETE /v1/campaigns/:id`
**Duplicate:** `POST /v1/campaigns/:id/duplicate`
**Send:** `POST /v1/campaigns/:id/send`
**Pause:** `POST /v1/campaigns/:id/pause`
**Resume:** `POST /v1/campaigns/:id/resume`
**Abort:** `POST /v1/campaigns/:id/abort`
**Analytics:** `GET /v1/campaigns/:id/analytics`

### Contacts

**Create:** `POST /v1/contacts`
```json
{
  "email": "user@example.com",
  "firstName": "Jane",
  "lastName": "Smith",
  "userId": "ext_123",
  "listIds": ["list_abc"],
  "customFields": {"plan": "pro"}
}
```
**Upsert (by email):** `POST /v1/contacts/email` — same payload, creates or updates
**Get by ID:** `GET /v1/contacts/:id`
**Get by email:** `POST /v1/contacts/search` — `{"emails": ["a@b.com", "c@d.com"]}`
**Bulk upsert (max 100):** `POST /v1/contacts/bulk` — `{"contacts": [{...}, {...}]}`
**Delete by ID:** `DELETE /v1/contacts/:id`
**Delete by user ID:** `DELETE /v1/contacts/user-id/:userId`

### Contact Lists

**List:** `GET /v1/contact-lists`
**Create:** `POST /v1/contact-lists` — `{"name": "Newsletter Subscribers"}`
**Get:** `GET /v1/contact-lists/:id`
**Get contacts in list:** `GET /v1/contact-lists/:id/contacts`
**Bulk add:** `POST /v1/contact-lists/:id/contacts` — `{"contactIds": ["id1", "id2"]}`
**Remove contacts:** `DELETE /v1/contact-lists/:id/contacts` — `{"contactIds": ["id1"]}`
**Delete:** `DELETE /v1/contact-lists/:id`

### Templates

**List:** `GET /v1/templates`
**Search:** `GET /v1/templates/search?name=welcome`
**Get:** `GET /v1/templates/:id`
**Create:** `POST /v1/templates`
```json
{
  "name": "Welcome Email",
  "subject": "Welcome, {{firstName}}!",
  "html": "<p>Hi {{firstName}}, welcome to {{companyName}}!</p>",
  "templateType": "marketing"
}
```
**Update:** `PATCH /v1/templates/:id`
**Delete:** `DELETE /v1/templates/:id`

Template variables use Handlebars syntax: `{{variableName}}`. Variable names: letters, numbers, underscores only.

### Senders

**List:** `GET /v1/senders`
**Get:** `GET /v1/senders/:id`
**Create:** `POST /v1/senders` — `{"email": "hello@domain.com", "name": "Sender Name"}`
**Delete:** `DELETE /v1/senders/:id`

Sender email must be on a verified domain.

### Automations

**List:** `GET /v1/automations?status=active`
**Get:** `GET /v1/automations/:id`
**Create:** `POST /v1/automations`
**Activate:** `POST /v1/automations/:id/activate`
**Pause:** `POST /v1/automations/:id/pause`
**Resume:** `POST /v1/automations/:id/resume`
**Delete:** `DELETE /v1/automations/:id`

### Events

**List:** `GET /v1/events`
**Create:** `POST /v1/events` — `{"name": "order_placed", "description": "...", "properties": {"orderTotal": "number"}}`
**Send:** `POST /v1/events/send` — `{"eventName": "order_placed", "contactId": "...", "properties": {"orderTotal": 99.99}}`

### Webhooks

**List:** `GET /v1/webhooks`
**Create:** `POST /v1/webhooks` — `{"url": "https://...", "events": ["email.sent", "email.opened"]}`
**Get:** `GET /v1/webhooks/:id`
**Delete:** `DELETE /v1/webhooks/:id`
**Reveal secret:** `POST /v1/webhooks/:id/reveal-secret`

### Suppression Groups (Unsubscribe)

**List:** `GET /v1/suppression-groups`
**Create:** `POST /v1/suppression-groups` — `{"name": "Marketing", "description": "..."}`
**Bulk suppress:** `POST /v1/suppression-groups/:id/suppress` — `{"emails": ["a@b.com"]}`
**Bulk unsuppress:** `POST /v1/suppression-groups/:id/unsuppress`

### Inbound Email

**List messages:** `GET /v1/inbound-emails?domain=example.com&page=1&limit=20`
**Get message:** `GET /v1/inbound-emails/:id`
**Download attachment:** `GET /v1/inbound-emails/:id/attachments/:index?download=true`
**Reply:** `POST /v1/inbound-emails/:id/reply` — `{"from": {"email": "..."}, "html": "..."}`

### Projects (admin key only)

**List:** `GET /v1/projects` (requires ASA_ key, no x-project-id)
**Create:** `POST /v1/projects` — `{"name": "New Project"}`
**Get:** `GET /v1/projects/:id`

### Contact Properties (Custom Fields)

**List:** `GET /v1/contact-properties`
**Create:** `POST /v1/contact-properties` — `{"name": "plan", "type": "string"}`
**Delete:** `DELETE /v1/contact-properties/:name`

## Known Issues

### Cloudflare IP Block (error code 1010) — RESOLVED via curl (Jul 27 2026)

**Status:** Python `urllib` still gets 1010. `curl` from the same VPS works — Cloudflare's bot detection treats curl differently. The API key authenticates successfully via curl (returns 400 "x-project-id header required" which means auth passed).

**Confirmed working (Jul 27 2026):**
```bash
# Bare connectivity test — Python gets 403/1010, curl gets 404 (works)
curl -s -o /dev/null -w "HTTP %{http_code}" https://api.autosend.com/
# → HTTP 404 (Cloudflare let it through)

# Authenticated endpoint — needs x-project-id header
curl -s -H "Authorization: Bearer $AUTOSEND_API_KEY" https://api.autosend.com/v1/projects
# → {"success":false,"error":{"message":"x-project-id header is required...","code":"PROJECT_ID_REQUIRED"}}
# This 400 means the API KEY WORKS — it's asking for the project ID, not rejecting the key
```

**Still needed:** Project ID from AutoSend dashboard (`autosend.com/dashboard → select project → URL contains ID`). Once we have it, add `x-project-id` header to all curl calls.

| Status | Code | Meaning |
|--------|------|---------|
| 400 | `VALIDATION_FAILED` | Invalid parameters |
| 401 | `UNAUTHORIZED` | Bad/missing API key |
| 402 | `PAYMENT_REQUIRED` | Plan upgrade needed |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 429 | `RATE_LIMIT_EXCEEDED` | Back off and retry |
| 500 | `SERVER_ERROR` | AutoSend internal error |

## Common Workflows

### Setting up a new domain for cold email
1. Add domain: `POST /v1/domains` with domain name + region
2. Get DNS records from response (DKIM, SPF, DMARC)
3. Configure DNS with domain registrar
4. Verify: `POST /v1/domains/:id/verify`
5. Create sender: `POST /v1/senders` for each sending address
6. Warm up: create campaign with `sendMode: "gradual"`

### Sending a marketing campaign
1. Verify sender exists: `GET /v1/senders`
2. Verify list/segment exists: `GET /v1/contact-lists`
3. Create template (or use existing): `POST /v1/templates`
4. Create campaign: `POST /v1/campaigns` with template, list, sender
5. Send test: `POST /v1/campaigns/:id/send-test` with test email
6. Publish + send: `POST /v1/campaigns/:id/send`

### Bulk importing contacts
1. Create list: `POST /v1/contact-lists`
2. Bulk upsert: `POST /v1/contacts/bulk` (max 100 per call, loop for larger)
3. Add to list: `POST /v1/contact-lists/:id/contacts`

## MCP Server

AutoSend provides a remote MCP server at `https://mcp.autosend.com/` with 34 tools across 10 categories. It uses streamable HTTP transport with OAuth 2.0. This is NOT configured as a native MCP server in Hermes — we use the REST API directly.

## Scripts

No scripts bundled yet. Create helper scripts as needed at `~/./scripts/autosend/`.
