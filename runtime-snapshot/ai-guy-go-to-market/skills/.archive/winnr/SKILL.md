---
name: winnr
description: Winnr pre-warmed email infrastructure API — list email users, export to legacy email platform/Instantly/other formats, manage inboxes via REST API and MCP server.
version: 1.0.0
author: jbellsolutions
metadata:
  hermes:
    tags: [Winnr, Email, Inboxes, Warmup]
prerequisites:
  env_vars: [WINNR_API_TOKEN]
  commands: [uvx, curl]
---

# Winnr Email Infrastructure

Winnr provides pre-warmed email inboxes for cold outreach. Justin's account has 20 inboxes across 4 domains.

## API

- **Base URL:** `https://api.winnr.app`
- **Auth:** `Authorization: Bearer wnr_<token>`
- **Content-Type:** `application/json`

### Key Endpoints

```bash
# Account info
GET /v1/account

# List email users (mailboxes) — paginated, max 100 per page
GET /v1/email-users?limit=100

# Get single email user details
GET /v1/email-users/{user_id}

# Export to outreach tool formats
POST /v1/export
Body: {"format": "legacy email platform", "getAllDomains": true}
# Formats: legacy email platform, instantly, snov, saleshandy, quickmail, lemlist, woodpecker,
#          reply, mailshake, gmass, yesware, mixmax, outreach, salesloft, default
# Rate limit: 1 export every 5 seconds
```

### Export Response

The export returns a signed S3 download URL. Download the CSV immediately — signatures expire.

The legacy email platform export CSV contains: `domain, from_email, from_name, user_name, password, smtp_host, smtp_port, imap_host, imap_port, imap_username, imap_password, footer`

## MCP Server

Installed via `pip install winnr-mcp`. Configure in `config.yaml`:

```yaml
mcp_servers:
  winnr:
    command: uvx
    args:
    - winnr-mcp
    - --token
    - wnr_<token>
    env:
      WINNR_API_TOKEN: wnr_<token>
    timeout: 120
```

MCP tools: `winnr_list_email_users`, `winnr_get_email_user`, `winnr_get_account`, `winnr_get_usage`, `winnr_export_email_users`, `winnr_list_inbox`, `winnr_get_message_body`, `winnr_send_email`, `winnr_refresh_inbox`, `winnr_delete_message`, `winnr_create_email_user`, `winnr_update_email_user`, `winnr_delete_email_user`, `winnr_bulk_create_email_users`

## Justin's Account

- **Account ID:** kvxYfb0PcB5l09dYURZa
- **Plan:** startup (active)
- **Limits:** 10 domains (4 used), 50 email users
- **Token:** `[REDACTED]`

### Domains & Inboxes (20 total, added to legacy email platform Jul 22)

| Domain | Count | legacy email platform IDs |
|---|---|---|
| learnshop.co | 6 | 21612113, 21612132, 21612134, 21612144, 21612160 |
| radcliffeexperiment.com | 5 | 21612125, 21612141, 21612151, 21612155, 21612158 |
| radclifferesearchinstitute.org | 5 | 21612126, 21612147, 21612149, 21612163, 21612170 |
| myprovenresearch.com | 5 | 21612136, 21612153, 21612166, 21612168, 21612174 |

All use SMTP/IMAP: `inbound.mywinnr.com:465/993`, 50/day send limit, tagged "Winnr" in legacy email platform (tag ID 482143).

## Adding Winnr Inboxes to legacy email platform

1. Export from Winnr: `POST /v1/export` with `{"format": "legacy email platform", "getAllDomains": true}`
2. Download the CSV from the returned S3 URL
3. For each row, create an email account via legacy email platform CLI:
   ```bash
   legacy email platform mailboxes create --from-json <file>
   ```
   JSON format: `{"from_name", "from_email", "user_name", "password", "smtp_host", "smtp_port", "imap_host", "imap_port", "warmup_enabled": false}`
4. Tag them: create tag via `POST /api/v1/tags`, then `legacy email platform mailboxes add-tags`

### Pitfalls

- **`message_per_day` is NOT allowed** in the legacy email platform create payload — legacy email platform rejects it. The daily send limit is configured separately via warmup settings.
- **`user_name` not `username`** — legacy email platform's API expects `user_name` for the field name.
- **`warmup_enabled` is required** — must be explicitly `false` for pre-warmed inboxes.
- **legacy email platform MCP `create_email_account` is unreliable** — use the CLI instead.
- **The export download URL is time-limited** (S3 presigned) — download immediately.