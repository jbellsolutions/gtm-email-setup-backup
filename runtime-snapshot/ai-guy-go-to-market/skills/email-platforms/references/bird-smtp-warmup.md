# Bird SMTP Warmup & Provider Switching

Operational procedures for running Bird-only warmup batches through ListMonk, and for switching SMTP providers without downtime.

## Bird SMTP Config (verified working Jul 30 2026)

| Setting | Value |
|---|---|
| Host | `us1.smtp.bird.com` |
| Port | `587` (Railway can reach this) |
| Alt port | `2525` (use if 587 blocked from your network) |
| TLS | `STARTTLS` |
| Auth protocol | `AUTH LOGIN` |
| Username | `bird` |
| Password | `[REDACTED]` |
| Category | marketing (set in Bird dashboard, not ListMonk) |
| Open/click tracking | OFF (ListMonk owns tracking via `{{ TrackView }}` and `{{ TrackLink }}`) |

**Resend SMTP Config (primary):**

| Setting | Value |
|---|---|
| Host | `smtp.resend.com` |
| Port | `465` |
| TLS | `SSL/TLS` |
| Username | `resend` |
| Password | `re_gPeMATEq_P9WcyfFwGRz9yDKqhHgEfqvA` |

## Provider Switching via API

ListMonk stores SMTP config in PostgreSQL. The API masks passwords (all bullet characters on output), so you can't read the current password back — but you CAN set it.

### Switch to Bird-only (disable Resend)

```python
import json, subprocess, time

LISTMONK_URL = "https://listmonk-production-2930.up.railway.app"
AUTH = "Authorization: token apiuser:[REDACTED]"

# 1. Read current settings
r = subprocess.run(["curl", "-sS", "--fail-with-body", "-H", AUTH,
                     f"{LISTMONK_URL}/api/settings"], capture_output=True, text=True)
settings = json.loads(r.stdout)["data"]

# 2. Flip providers — disable Resend, enable Bird
for s in settings["smtp"]:
    if s["name"] == "email-resend":
        s["enabled"] = False
    elif s["name"] == "email-bird":
        s["enabled"] = True
        s["password"] = "[REDACTED]"  # must set explicitly

# 3. Write back (PUT replaces the full settings object)
subprocess.run(["curl", "-sS", "--fail-with-body", "-H", AUTH,
                 "-H", "Content-Type: application/json", "-X", "PUT",
                 "-d", json.dumps(settings), f"{LISTMONK_URL}/api/settings"],
                capture_output=True, text=True)

# 4. Wait for server restart (~5s), then verify
time.sleep(5)
r = subprocess.run(["curl", "-sS", "--fail-with-body", "-H", AUTH,
                     f"{LISTMONK_URL}/api/logs"], capture_output=True, text=True)
# Look for: "initialized email (SMTP) messenger: bird@us1.smtp.bird.com"
```

### Switch back to Resend (after Bird batch completes)

Same procedure, but set `email-resend.enabled = True` and `email-bird.enabled = False`.
Verify logs show: `"initialized email (SMTP) messenger: resend@smtp.resend.com"`.

**⚠️ Critical:** You MUST set the Bird password explicitly when enabling Bird. ListMonk masks passwords on API output, so reading settings gives you bullet characters. If you write those bullets back, the password is corrupted. Always set the real key when modifying Bird SMTP settings.

## Bird Warmup Protocol (Day-by-day ramp)

ListMonk round-robins randomly across all enabled SMTP servers (no weighting). To send via Bird only, you MUST disable all other providers first.

### Pre-send gate (mandatory)

1. `GET /api/logs` — scan for any `error` entries. If any SMTP errors exist, STOP and fix.
2. After switching to Bird-only, verify logs show `initialized email (SMTP) messenger: bird@us1.smtp.bird.com` with no errors.
3. Confirm the campaign targets the correct list with the correct subscriber count.

### Send procedure

1. Switch to Bird-only (see above)
2. Verify pre-send gate passes
3. `PUT /api/campaigns/{id}/status` with `{"status":"running"}`
4. Poll `GET /api/campaigns/{id}` until `status: finished`
5. Check `/api/logs` for any errors during the send
6. Switch back to Resend primary

### Post-send verification (via Bird API)

```python
BIRD_KEY = "[REDACTED]"
BASE_US = "https://us1.platform.bird.com"

# Get all messages, filter by subject
r = subprocess.run(["curl", "-sS", "--fail-with-body",
                     "-H", f"Authorization: Bearer {BIRD_KEY}",
                     f"{BASE_US}/v1/email/messages?limit=100"],
                    capture_output=True, text=True)
messages = json.loads(r.stdout).get("data", [])

# Filter for this campaign's subject
campaign_msgs = [m for m in messages if "YOUR SUBJECT" in m.get("subject", "")]

# Count per recipient — verify exactly 1 copy each
from collections import Counter
recipient_counts = Counter()
statuses = Counter()
for m in campaign_msgs:
    for to in m.get("to", []):
        recipient_counts[to.get("email", "?")] += 1
    statuses[m.get("status", "?")] += 1

# Verify: len(recipient_counts) == expected_count, all counts == 1
```

### Warmup schedule

| Day | Volume | Notes |
|---|---|---|
| 1 | 50 | Bird Free tier daily cap = 50. Fits exactly. |
| 2-3 | 100 | Exceeds free tier daily cap — need paid plan or split across 2 days |
| 4-5 | 250 | Requires paid plan |
| 6-7 | 500 | Requires paid plan |

**Bird Free tier limits:** 50 emails/day, 1,000/month. Check dashboard (app.bird.com → Billing) for current plan and upgrade options.

### Bounce handling

After each batch, check Bird API for bounced messages. Hard bounces should be suppressed from future sends. Bird API returns bounce status per message:

```
status=bounced → check the specific message for bounce reason
```

ListMonk also tracks bounces in the campaign object (`GET /api/campaigns/{id}` → `bounces` field).

## Domain Health (send.usingaitoscale.com)

Verified via `GET /v1/email/domains` on Bird API:

| Record | Type | Status | Required for sending? |
|---|---|---|---|
| DKIM | TXT | ✅ verified (selector `bird-536-0726`, 2048-bit RSA) | Yes |
| Return path | CNAME | ✅ verified (`bounce.send` → `us1.bounce.bird.com`) | Yes |
| DMARC | TXT | ✅ verified (`p=none`) | Yes |
| Tracking | CNAME | ⏳ pending (`links.send` → `us1.links.bird.com`) | No — optional, Bird tracking is OFF |
| Inbound MX | MX | ⏳ pending (3 records) | No — for inbound email only |

## Bird API Endpoints (current platform, US region)

Base URL: `https://us1.platform.bird.com`
Auth: `Authorization: Bearer bk_us1_...`

| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/email/messages?limit=N` | List recent emails (filter by subject in code) |
| GET | `/v1/email/messages/{id}` | Single message status |
| GET | `/v1/email/stats/summary` | Aggregate delivery stats (all-time) |
| GET | `/v1/email/stats/daily?limit=N` | Daily breakdown |
| GET | `/v1/email/domains` | Sending domain health + DNS records |
