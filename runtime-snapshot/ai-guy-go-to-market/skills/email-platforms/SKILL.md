---
name: email-platforms
description: "Email infrastructure and campaign operations: Bird API (transactional/marketing send), ListMonk (self-hosted newsletter server), Winnr (pre-warmed inboxes for cold outreach), and My Claw-style newsletter content creation. Load this skill for any email sending, newsletter, mailing list, SMTP, or inbox infrastructure task."
version: 1.0.0
category: email
triggers:
  - bird email api
  - bird.com email
  - sparkpost
  - messagebird email
  - listmonk
  - newsletter
  - mailing list
  - winnr
  - pre-warmed inboxes
  - cold email infrastructure
  - email sending
  - smtp relay
  - email newsletter creation
  - my claw newsletter
---

# Email Platforms

Umbrella skill for all email infrastructure and campaign operations on the AI Integraterz stack. Four platforms, each with a dedicated section below:

1. **Bird Email API** — transactional/marketing email via Bird.com (formerly MessageBird/SparkPost)
2. **ListMonk** — self-hosted newsletter/mailing list server on Railway
3. **Winnr** — pre-warmed email inboxes for cold outreach, exportable to legacy email platform
4. **Newsletter Content Creation** — My Claw-style newsletter format with HTML + plain text dual output

---

## Bird Email API

Bird (bird.com, formerly MessageBird/SparkPost) provides email sending through two API generations. This section covers both, plus SMTP relay, sending domains, metrics, events, and suppression list management.

### Two API Generations — Read This First

| Generation | Key Format | Auth Header | Host (EU) | Host (US) |
|---|---|---|---|---|
| **Current (Bird Platform)** | `bk_eu1_...` / `bk_us1_...` | `Authorization: Bearer <key>` | `https://eu1.platform.bird.com` | `https://us1.platform.bird.com` |
| **Legacy (SparkPost/MessageBird)** | Short alphanumeric (`dqp8Ykhz...`) | `Authorization: AccessKey <key>` | `https://email.eu-west-1.api.bird.com/api` | `https://email.us-west-1.api.bird.com/api` |

**How to tell which key you have:** Keys with `bk_` prefix are current platform keys. Short alphanumeric strings without a prefix are legacy keys.

**⚠️ Critical:** The current working key is `[REDACTED]` (US region, 10 scopes, stored in `~/.env`). The legacy `dqp8Ykhz...` key in the old `~/.env` was replaced on Jul 30. Always use the `bk_` key for API calls. The legacy key returns 401 on all email endpoints.

### Prerequisites

1. **API Key** — stored as `BIRD_API_KEY` in `~/home/.env` (NOT the main `.env`)
2. **Workspace ID** — UUID, found at `app.bird.com → Settings → General` (no programmatic way to discover it)
3. **Region** — EU or US (determines base URL). Key prefix tells you: `bk_eu1_` = EU, `bk_us1_` = US
4. **Sending Domain** — must be verified in Bird before sending
5. **Email channel installed** — Email must be activated as a channel in the Bird dashboard

### Current API (Bird Platform) — Key Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/email/messages` | Send email |
| GET | `/v1/email/messages` | List messages |
| GET | `/v1/email/messages/{id}` | Get message status |
| GET | `/v1/email/stats/summary` | Aggregate stats |
| GET | `/v1/email/stats/daily` | Daily sending stats |
| GET | `/v1/suppressions` | List suppressions |
| POST | `/v1/suppressions` | Add suppression |
| DELETE | `/v1/suppressions/{id}` | Remove suppression |

**Sandbox testing:** From `onboarding@messagebird.dev`, To `delivered@messagebird.dev` (always delivers), bounce test: `bounce@messagebird.dev`.

**Domain health check (current platform API):** `GET /v1/email/domains` — returns sending domain status including DKIM, return path, DMARC, tracking, and inbound MX verification status, plus full DNS record details. Use this to verify domain health programmatically (the legacy `/workspaces/{id}/reach/sending-domains` endpoint is deprecated).

### Legacy API (SparkPost/MessageBird)

All endpoints require `{workspaceId}` as a path parameter.

- **Send:** POST `/workspaces/{workspaceId}/reach/transmissions`
- **Sending Domains:** GET/POST/DELETE `/workspaces/{workspaceId}/reach/sending-domains`
- **Verify domain:** POST `/workspaces/{workspaceId}/reach/sending-domains/{domain}/verify`
- **Metrics:** GET `/workspaces/{workspaceId}/reach/metrics`
- **Suppression list:** GET `/workspaces/{workspaceId}/reach/suppression-list`

See `references/bird-api-schema.md` for full transmission request schema, recipient format, sending domain status, DKIM configuration, and metrics reference.

### SMTP Relay (US Region — confirmed working Jul 29 2026)

| Setting | Value |
|---|---|
| Host (US) | `us1.smtp.bird.com` |
| Port | `587` (or `2525` alt if 587 blocked) |
| Encryption | `STARTTLS` |
| Auth protocol | `AUTH LOGIN` |
| Username | `bird` |
| Password | API key with "Send via SMTP" scope (e.g. `bk_us1_...`) |

**Workspace region: US** (key prefix `bk_us1_`). Previous docs incorrectly said EU. All DNS records use US endpoints (`us1.bounce.bird.com`, `us1.links.bird.com`).

**Domain health (send.usingaitoscale.com):**
- ✅ DKIM: verified (selector `bird-536-0726`, 2048-bit RSA, TXT record)
- ✅ Return path: verified (`bounce.send.usingaitoscale.com` → `us1.bounce.bird.com`)
- ✅ DMARC: verified (`_dmarc.send.usingaitoscale.com`, `p=none`)
- ⏳ Tracking CNAME: pending (`links.send.usingaitoscale.com` → `us1.links.bird.com`) — OPTIONAL, Bird tracking is OFF, ListMonk owns tracking
- ⏳ Inbound MX: pending — not needed for sending

**Bird API key (current):** `[REDACTED]` — 36 chars, 10 scopes, US region, no expiry. Stored in `~/.env` as `BIRD_API_KEY`. Also stored in ListMonk Bird SMTP password field (masked on API output).

**Bird send history:** 4 test emails sent Jul 29 2026 via Bird SMTP (3 delivered, 1 OOB bounce). Warmup Day 1 sent Jul 30: 50 emails (49 delivered, 1 bounce). Category=marketing, track_clicks=false, track_opens=false.

**Bird send limits:** Free tier = 50 emails/day, 1,000/month. Need dashboard (app.bird.com → Billing/Plans) for plan tier and upgrade options. Total all-time sends: 54.

**Bird warmup & provider switching:** See `references/bird-smtp-warmup.md` for the full protocol — how to switch ListMonk to Bird-only (disable Resend), send a controlled batch, verify per-recipient delivery via Bird API, and switch back. Includes pre-send gate, post-send verification code, and warmup ramp schedule.

### Provisioning Diagnostics

If Bird's email product is not fully activated (this was the case on Jul 27 with the wrong key, but is RESOLVED as of Jul 30 with the correct `bk_us1_` key):
1. **API 401 on all email endpoints** — check if you're using a legacy key (no `bk_` prefix). Legacy keys authenticate on the legacy root but get 401 on all current platform email endpoints. Replace with a `bk_` key from the Bird dashboard.
2. **Default domains unhealthy** — `birdemailbox.com` domains show "Not healthy"
3. **DKIM won't generate** — "Unavailable" with Retry button; backend not running
4. **Old-style key without `bk_` prefix** — legacy keys do not work with current platform API

**What's needed:** Nothing — Bird email IS provisioned and working with the `[REDACTED]` key (US region). Previous diagnosis was based on the wrong API key (legacy `dqp8Ykhz...` key).

### DNS Records for Sending Domains

| Record | Type | Example |
|---|---|---|
| Bounce | CNAME | `bounce.yourdomain.com` → `eu.sparkpostmail.com` (EU) or `sparkpostmail.com` (US) |
| Tracking | CNAME | `track.yourdomain.com` → `v2.spgo.io` |
| DKIM | TXT/CNAME | `selector._domainkey.yourdomain.com` (fails if not provisioned) |
| DMARC | TXT | `_dmarc.yourdomain.com` → `v=DMARC1; p=none;` |

### Bird SMTP/API Credential Diagnostic (no-campaign-send gate)

When Bird's HTTP API accepts a message but ListMonk's SMTP relay returns `535 5.7.8 Authentication failed`, treat the paths as separate until proven otherwise. Do not resume a campaign to test the fix.

1. Keep every campaign paused and verify the named campaign status with a fresh GET.
2. Run one standalone Bird HTTP API diagnostic to an internal seed only. Record HTTP status, accepted, rejected, bounced, and message ID. A 202 proves the HTTP API credential works, not SMTP.
3. Run one SMTP-only diagnostic to the same internal seed using the exact relay settings. Do not claim SMTP success unless the SMTP server greeting, EHLO, STARTTLS, AUTH LOGIN, and message acceptance are observed. If the socket itself times out, report SMTP auth as unverified, not successful.
4. Read ListMonk's `/api/settings` and report only non-secret fields plus whether username/password values are present. ListMonk masks SMTP passwords; a masked field does not prove the stored secret is correct.
5. Verify Bird's SMTP credential requirements separately from the HTTP API credential. For the current US relay, the known settings are `us1.smtp.bird.com:587`, STARTTLS, username `bird`, and a key with the provider's SMTP-send permission. HTTP API acceptance does not establish that the key is valid for SMTP AUTH.
6. Check Bird account/domain status and metrics for suspension, rejection, abuse, or rate-limit signals. Do not infer suspension from SMTP 535 alone.
7. Never send a campaign or use the campaign test endpoint during this diagnostic. The only permitted recipient is the explicitly named internal seed, and only for the standalone provider probe.

If the direct SMTP path cannot be reached from the execution environment, distinguish network timeout from credential rejection. If ListMonk has already logged a 535, preserve that exact evidence while reporting the direct probe as incomplete.

See `references/bird-smtp-api-diagnostic.md` for the reproducible probe sequence and evidence format.

### Bird Pitfalls

1. **Two API generations** — check key prefix for `bk_` (current) vs not (legacy)
2. **Legacy root 200 ≠ email working** — `email.eu-west-1.api.bird.com/` returns 200 with a careers page
3. **US endpoint unreachable from some VPS networks** — always test both regions
4. **Workspace ID required for every legacy call** — no global discovery endpoint
5. **DKIM generation requires email provisioning** — retrying won't fix it
6. **Email channel must be installed** — check `Channels → Email` in dashboard
7. **Content capped at 20MB** — total across html, text, attachments, inline images

---

## ListMonk

Self-hosted Listmonk instance (v6.2.0) on Railway — newsletter and mailing list manager driven through REST API or browser automation.

### Instance Details

| Item | Value |
|---|---|
| URL | `https://listmonk-production-2930.up.railway.app` |
| Version | v6.2.0 (linux/amd64) |
| Admin user | `List Monk One` |
| Admin password | `ListMonk2026$` |
| Default from | `Justin <justin@send.usingaitoscale.com>` |

### SMTP Configuration

Two SMTP providers configured in ListMonk — only one should be enabled at a time (ListMonk round-robins randomly across all enabled servers, no weighting). SMTP selection is global to the ListMonk instance, not pinned per campaign; when campaigns require different providers, switch providers sequentially, verify the initialization log, run and verify one test, then switch for the next.

| Provider | Host | Port | TLS | Username | Status |
|---|---|---|---|---|---|
| Resend (primary) | `smtp.resend.com` | 465 | SSL/TLS | `resend` | Enabled |
| Bird (warmup/secondary) | `us1.smtp.bird.com` | 587 | STARTTLS | `bird` | Disabled |

**⚠️ Domain verification pitfall:** Resend blocks sends if `send.usingaitoscale.com` is not verified in the Resend dashboard at `https://resend.com/domains`. A campaign that starts as `running` and immediately becomes `finished` with `sent: 0` is almost certainly a domain verification or SMTP auth failure. Check `/api/logs` for the exact SMTP rejection.

**⚠️ SMTP password masking:** ListMonk masks all SMTP passwords as bullet characters (`•••••`) on API output. You cannot read the current password back. When modifying SMTP settings via `PUT /api/settings`, you MUST explicitly set the password field to the real key — do NOT write back the masked bullets, or the password becomes corrupted.

**Bird SMTP:** PROVISIONED and WORKING (tested Jul 29, campaign 17 sent 4/4; warmup Day 1 sent 50/50 on Jul 30). Domain `send.usingaitoscale.com` verified with DKIM, return path, and DMARC all active. Region is US (not EU — previous docs were wrong). See `references/bird-smtp-warmup.md` for the full Bird warmup protocol, provider switching procedure, and post-send verification via Bird API.

### Authentication

Listmonk uses TWO different auth systems:

1. **Admin UI (browser):** Login at `/admin/login` — creates session cookie
2. **REST API:** Requires dedicated API user token (admin credentials do NOT work). Create at Users → + New → Type: API → Generate

**Primary method — Browser Console:** When API credentials fail (which they often do — ListMonk's API user creation is buggy), use the `browser_console` tool to make `fetch()` calls from a logged-in browser session. Session cookie authenticates all calls.

**⚠️ Browser session pitfall (discovered Jul 28 2026):** The ListMonk session cookie drops frequently — navigating to a new page or after ~2 minutes of inactivity can log you out. When the browser falls back to `about:blank` (which happens after long `browser_console` evaluations), `fetch('/api/...')` fails with `TypeError: Failed to parse URL` because there's no origin. Two fixes:
1. Always use absolute URLs in fetch calls: `fetch('https://listmonk-production-2930.up.railway.app/api/campaigns', ...)` — this works even from `about:blank` IF the session cookie is still valid
2. Re-navigate to `/admin/campaigns` before making API calls to ensure the session is alive

**Passing large HTML via browser_console:** ListMonk campaign bodies can be 38K–57K chars. To pass this to `browser_console`:
1. Check the HTML for backticks and `${` — if absent (common for email HTML), use a JS template literal: `window.__html = \`...38K chars...\`; window.__html.length`
2. If backticks exist, use base64: encode in Python, pass in chunks via `window.__b64 += '...'; `, then `window.__html = atob(window.__b64)`
3. After loading HTML into a JS variable, create/update the campaign: `fetch('/api/campaigns', {method:'POST', body:JSON.stringify({body: window.__html, ...})})`
4. Two-step approach for very large bodies: create the campaign with placeholder HTML first (`POST /api/campaigns` with `body: '<h1>placeholder</h1>'`), then update with real HTML (`PUT /api/campaigns/{id}` with `body: window.__html`)

### ListMonk Template Tags (Go Templates)

ListMonk uses Go template syntax for dynamic content. When converting HTML from another ESP (JangoMail, Mailchimp, etc.), swap their placeholders:

| External ESP Placeholder | ListMonk Tag | Purpose |
|---|---|---|
| JangoMail `/u.z?***uniqueid****` | `{{.UnsubURL}}` | Unsubscribe link |
| JangoMail `/w.z?***uniqueid****` | `{{.TrackView}}` | View-as-webpage link |
| Mailchimp `*|UNSUB|*` | `{{.UnsubURL}}` | Unsubscribe link |
| Mailchimp `*|ARCHIVE|*` | `{{.TrackView}}` | View-as-webpage link |
| Generic `{{UNSUBSCRIBE_LINK}}` | `{{ UnsubscribeURL }}` | Unsubscribe link |
| Generic `{{VIEW_ONLINE_LINK}}` | `{{ MessageURL }}` | View-as-webpage link |

Subscriber data: `{{.Subscriber.Name}}`, `{{.Subscriber.Email}}`, `{{.Subscriber.Attribs.fieldName}}`

### JangoMail → ListMonk HTML Conversion

When reusing newsletter HTML from JangoMail campaigns in ListMonk:

1. Pull the HTML from JangoMail: `GET https://api-v2.jangomail.com/campaigns/{id}/stats/content` → `html_content` field
2. Replace JangoMail unsubscribe: `https://track.scaleverticalwithai.com/u.z?***uniqueid****` → `{{.UnsubURL}}`
3. Replace JangoMail view-online: `https://track.scaleverticalwithai.com/w.z?***uniqueid****` → `{{.TrackView}}`
4. If the JangoMail campaign had manual `/c.z` link wrapping (broken — see jangomail-api skill), restore raw editorial URLs by extracting the `u=` parameter and URL-decoding it
5. Image URLs from JangoMail CDN (`https://img.jangomail.com/2606407/Images/...`) are public — they render in ListMonk campaigns without re-uploading
6. Verify: 0 JangoMail placeholders remaining, correct count of ListMonk tags (2× `{{.UnsubURL}}`, 2× `{{.TrackView}}`), all editorial links are raw URLs

ListMonk handles click tracking natively — no manual link wrapping needed. Editorial links stay raw in the HTML; ListMonk wraps them at delivery time.

### REST API Quick Reference

All endpoints prefixed with `/api/`. Responses are `{"data": ...}`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Liveness check |
| `/api/logs` | GET | Recent server log lines (SMTP failures show here) |
| `/api/lists` | GET/POST | List / create mailing lists |
| `/api/subscribers` | GET/POST | List / add subscribers |
| `/api/subscribers?list_id={id}` | GET | Subscribers filtered by list |
| `/api/campaigns` | GET/POST | List / create campaigns |
| `/api/campaigns/{id}/status` | PUT | Update status (`running` sends immediately) |
| `/api/campaigns/{id}/test` | POST | Send test email |
| `/api/import/subscribers` | POST | Bulk CSV import (multipart form) |

### Workflow: Send a Newsletter

1. Verify SMTP: check `/api/logs` for prior errors
2. Create/verify list: `GET /api/lists`
3. Import subscribers: `POST /api/import/subscribers` or `POST /api/subscribers`
4. Create campaign: `POST /api/campaigns` with HTML body, list IDs, subject
5. Send test (optional): `POST /api/campaigns/{id}/test`
6. Confirm recipient count: check `to_send` in campaign response
7. Start: `PUT /api/campaigns/{id}/status` with `{"status":"running"}`
8. Monitor: `GET /api/campaigns/{id}` — check `sent`, `views`, `bounces`

### Reporting and Provider Reconciliation

For a warmup or newsletter report that uses both ListMonk and Bird, separate application-level engagement from transport-level delivery.

**Operational reconciliation rules:** Treat ListMonk `sent`, `to_send`, `bounces`, `views`, and `clicks` as application-level fields. Bird `accepted`, `delivered`, `bounced`, `deferred`, `rejected`, and `complained` are transport-level fields. They will not necessarily share a denominator. A completed ListMonk campaign can leave an audience-to-sent gap; that gap is unresolved until provider records are filtered by exact sender, subject, and send window. Do not call it bounced or retry it blindly.

For Bird bounce exports, paginate `/v1/email/messages` (including `status=bounced` where supported), filter by exact campaign sender/subject/time window, deduplicate recipients, and preserve message ID/timestamp/status in a detailed CSV. Produce a one-column unique-email CSV for suppression review. Do not delete or suppress deferred recipients automatically, and do not classify a bounce as hard/soft unless the provider record exposes the reason. Account aggregate endpoints are useful health snapshots but are not campaign-specific ledgers.

For opens/clicks, check both ListMonk campaign fields and dated analytics endpoints. Empty analytics plus `views: 0`/`clicks: 0` means unavailable instrumentation, not proof that nobody engaged. Bird tracking flags and ListMonk tracking settings must be checked before reporting rates. ListMonk's campaign view supplies native views/opens and clicks. Bird's `/v1/email/messages` or summary endpoint supplies per-message delivered/bounced status. If ListMonk shows `sent N / N` but Bird reports a bounce, report Bird's delivered count and explicitly note the discrepancy rather than treating ListMonk's denominator as delivered. When Bird tracking is disabled, do not expect Bird open/click counts to populate; use ListMonk's native tracking for those fields.

### Cross-Platform Email Operations Registry

ListMonk is not a universal campaign ledger. It only contains campaigns created and launched in ListMonk. JangoMail, legacy email platform/Winnr, Bird API-direct sends, and Resend-direct sends must be inventoried separately.

For a single source of truth, maintain four linked operational records in Notion or an equivalent system:

1. **Email Platforms** — provider, purpose, status, route, sending domain, tracking owner, health, and owner. Never store credentials or API keys.
2. **Email Campaign Registry** — campaign name/ID, platform, transport, audience, owner, status, planned volume, actual attempted/sent volume, delivered, bounces, opens, clicks, replies, and source link.
3. **Email Daily Stats** — dated per-platform/per-campaign snapshots with attempted, sent, delivered, bounces, opens, clicks, replies, reconciliation status, and discrepancy notes.
4. **Email Ops Tasks** — owner, action, due date, blocker, priority, and related campaign/platform.

Always separate:
- **Application-level stats:** campaign manager counts, opens, clicks, and campaign status.
- **Transport-level stats:** SMTP/API attempts, accepted, delivered, bounced, blocked, and provider usage/quota.

Do not infer total sending volume from ListMonk. Reconcile each campaign against the platform that actually initiated it. A provider's stronger open rate is only a hypothesis until the send count, delivered denominator, tracking settings, and comparable audience are recorded.

When onboarding a new platform, first perform a read-only inventory: account usage/quota, campaign list, campaign IDs, dates, recipients, delivery failures, engagement, and route. Record the platform even if it has no current campaigns. A plan-limit result is an operational blocker and must become an explicit task before additional sends.

Session-specific implementation details and the Green Room Campaign 4 reconciliation record are in `references/cross-platform-email-ops-registry.md`.

### ListMonk Pitfalls

- **`PUT /api/campaigns/{id}/status` with `status: running` is irreversible** — sends to every subscriber. Always confirm recipient count and get explicit approval first.
- **Admin credentials do NOT work for API access** — use API token or browser console technique
- **Campaign `finished` + `sent: 0`** = SMTP rejection (domain not verified, auth failed, etc.)
- **Session cookie drops on navigation and after ~2 min inactivity** — re-navigate to `/admin/campaigns` before API calls, or use absolute URLs in fetch
- **`fetch('/api/...')` fails from `about:blank`** — browser_console evaluations that take >5s can leave the page at `about:blank`, breaking relative URL fetch. Always use `fetch('https://listmonk-production-2930.up.railway.app/api/...')` with absolute URLs
- **Large HTML bodies (>30K chars)** — cannot be passed as a single browser_console string argument. Use template literals (backticks) if HTML has no backticks/`${`, or base64 encode in chunks. See "Passing large HTML via browser_console" above
- **Two-step campaign creation for large bodies** — create with placeholder HTML first (`POST`), then update with real HTML (`PUT`), to avoid timeout on the initial create call

---

## Winnr

Winnr provides pre-warmed email inboxes for cold outreach. Justin's account has 20 inboxes across 4 domains.

### API

- **Base URL:** `https://api.winnr.app`
- **Auth:** `Authorization: Bearer wnr_<token>`
- **MCP Server:** Install via `pip install winnr-mcp`, configure with `uvx winnr-mcp --token wnr_<token>`

### Key Endpoints

```bash
# Account info
GET /v1/account

# List email users (mailboxes) — paginated, max 100 per page
GET /v1/email-users?limit=100

# Export to outreach tool formats (legacy email platform, instantly, snov, etc.)
POST /v1/export
Body: {"format": "legacy email platform", "getAllDomains": true}
# Rate limit: 1 export every 5 seconds
# Returns signed S3 download URL — download immediately, signatures expire
```

### Justin's Account

- **Account ID:** `kvxYfb0PcB5l09dYURZa`
- **Plan:** startup (active)
- **Limits:** 10 domains (4 used), 50 email users
- **Token:** `[REDACTED]`

| Domain | Count | legacy email platform IDs |
|---|---|---|
| learnshop.co | 6 | 21612113, 21612132, 21612134, 21612144, 21612160 |
| radcliffeexperiment.com | 5 | 21612125, 21612141, 21612151, 21612155, 21612158 |
| radclifferesearchinstitute.org | 5 | 21612126, 21612147, 21612149, 21612163, 21612170 |
| myprovenresearch.com | 5 | 21612136, 21612153, 21612166, 21612168, 21612174 |

All use SMTP/IMAP: `inbound.mywinnr.com:465/993`, 50/day send limit, tagged "Winnr" in legacy email platform (tag ID 482143).

### Adding Winnr Inboxes to legacy email platform

1. Export from Winnr: `POST /v1/export` with `{"format": "legacy email platform", "getAllDomains": true}`
2. Download CSV from returned S3 URL
3. For each row, create email account via legacy email platform CLI
4. Tag them: create tag via `POST /api/v1/tags`, then `legacy email platform mailboxes add-tags`

### Winnr Pitfalls

- **`message_per_day` is NOT allowed** in legacy email platform create payload — rejected
- **`user_name` not `username`** — legacy email platform API expects `user_name`
- **`warmup_enabled` is required** — must be explicitly `false` for pre-warmed inboxes
- **legacy email platform MCP `create_email_account` is unreliable** — use CLI instead
- **Export download URL is time-limited** (S3 presigned) — download immediately

---

## Newsletter Content Creation (My Claw Format)

Create email newsletters modeled on the My Claw newsletter format — clean, scannable style with emoji headlines, TL;DR story summaries, and integrated sponsor CTA. Produces both HTML and plain text versions.

### Format Structure

1. **Subject line:** Single emoji + punchy headline (no date, no issue number)
2. **Subtitle:** "Plus: " followed by 2-3 secondary story headlines (email preview text)
3. **Header:** Logo, date, "Read Online | Unsubscribe" links
4. **Greeting:** "Good Morning, [audience name]!"
5. **Tagline sentence:** One provocative sentence setting the theme
6. **Stories (5-7):** Horizontal rule → bold linked headline → "TL;DR:" 2-3 sentence summary with concrete number → "Read more →"
7. **Sponsor CTA:** 2 paragraphs (what sponsor does + value prop) + bold CTA line
8. **Keep Reading:** 2-3 previous issues as linked headlines
9. **Footer:** Brand name, copyright, unsubscribe link

### HTML Template

See `templates/newsletter.html` for the full HTML template (600px centered, navy header, amber accents). See `templates/story-snippet.html` for the per-story repeating block.

### Workflow

1. Research stories using `web-article-research` skill or Google News RSS
2. For each story: extract headline, source link, 2-3 sentence summary with concrete number
3. Write sponsor section: 2 paragraphs + bold CTA line
4. Generate HTML version from template
5. Generate plain text version
6. Save both to `/tmp/` — HTML for email sending, text for review

### Newsletter Pitfalls

- Every story needs a real source link — no fake/placeholder URLs
- At least one concrete number per story (stats, dollar amounts, percentages, dates)
- Sponsor CTA should feel like a natural section, not a banner ad
- No em dashes (user preference)
- The "Plus: " subtitle matters — it's the email preview text
- Keep stories tight: 2-3 sentences each

### Example Variables

See `references/newsletter-speakeragent-variables.md` for example variable values for a SpeakerAgent podcast newsletter.