# SMTP Settings, Campaign Headers & Tracking

Lessons from live ListMonk v6.2.0 operation (Jul 2026).

## Multi-SMTP Server Setup

ListMonk supports multiple SMTP servers for load-balancing/failover. Configure via `PUT /api/settings`.

### Adding a Second SMTP Server

1. `GET /api/settings` — returns the full settings object including `smtp` array
2. Append a new SMTP server object to the `smtp` array
3. `PUT /api/settings` with the ENTIRE settings object (it's a full replace, not a patch)

```python
import urllib.request, json

# GET current settings
req = urllib.request.Request(f"{LM_URL}/api/settings", headers=headers)
settings = json.loads(urllib.request.urlopen(req, timeout=20).read())["data"]

# Append new SMTP server
settings["smtp"].append({
    "name": "bird",           # ListMonk auto-prefixes with "email-" → "email-bird"
    "uuid": "",               # empty = ListMonk generates
    "enabled": True,
    "host": "us1.smtp.bird.com",
    "hello_hostname": "",
    "port": 587,
    "auth_protocol": "login",  # "login" or "plain"
    "username": "bird",
    "password": "bk_...",
    "email_headers": [],
    "max_conns": 2,
    "max_msg_retries": 2,
    "msg_retry_delay": "5s",
    "idle_timeout": "15s",
    "wait_timeout": "10s",
    "tls_type": "STARTTLS",   # "TLS" for implicit TLS (port 465), "STARTTLS" for port 587
    "tls_skip_verify": False,
    "from_addresses": []      # empty = handles all from addresses
})

# PUT back the entire settings object
put_data = json.dumps(settings).encode("utf-8")
req = urllib.request.Request(f"{LM_URL}/api/settings", data=put_data, headers=headers, method="PUT")
urllib.request.urlopen(req, timeout=20)
```

### Pitfalls
- **PUT /api/settings is a FULL REPLACE.** Always GET first, modify, PUT back. Never send a partial object.
- **ListMonk auto-prefixes SMTP names** with the messenger type. Naming a server `"bird"` produces `"email-bird"` in the stored config. Naming it `""` (empty) produces `"email-resend"` etc.
- **SMTP password is masked** in GET responses (`"•••••"`). When PUTting back, the masked password is accepted as-is (ListMonk detects it's masked and keeps the original). To CHANGE the password, set the plaintext value.
- **Server restarts on settings PUT.** The ListMonk process restarts (visible in logs: `init.go: reading config`). This is normal.
- **DNS verification required.** A new SMTP server can be added and enabled, but sends will fail with `535 Authentication credentials invalid` until the sending domain's DNS (SPF/DKIM) is verified at the SMTP provider.

## Campaign Headers (Reply-To, Custom Headers)

Campaigns support custom email headers via the `headers` field.

### Format — Array of Key-Value Objects (NOT a Plain Object)

```json
// ✅ CORRECT
"headers": [{"key": "Reply-To", "value": "xander@usingaitoscale.com"}]

// ❌ WRONG — causes: "Unmarshal type error: expected=models.Headers, got=object"
"headers": {"Reply-To": "xander@usingaitoscale.com"}
```

### Setting Reply-To on Campaigns

```python
campaign_data = {
    "name": "...",
    "subject": "...",
    "lists": [6],
    "type": "regular",
    "content_type": "html",
    "body": html_content,
    "from_email": "The People Person <newsletter@send.usingaitoscale.com>",
    "template_id": 6,
    "messenger": "email",
    "headers": [{"key": "Reply-To", "value": "xander@usingaitoscale.com"}],
}
```

### Pitfall — Finished Campaigns Cannot Be Updated

`PUT /api/campaigns/{id}` returns `400: "Cannot update a running or a finished campaign."` for campaigns with status `finished` or `running`. To change from_email/headers on a finished campaign, create a NEW campaign with the desired settings.

## Test Send Endpoint — Required Fields

`POST /api/campaigns/{id}/test` requires MORE fields than the API docs imply.

### Minimum Required Payload

```json
{
  "name": "...",
  "subject": "...",
  "lists": [6],
  "type": "regular",
  "content_type": "html",
  "body": "<html>...</html>",
  "messenger": "email",
  "from_email": "Name <addr@domain.com>",
  "template_id": 6,
  "subscribers": ["a@b.com", "c@d.com"]
}
```

### Pitfalls
- **Omitting `messenger`** → `400: {"message":"Unknown messenger ."}`
- **Omitting `from_email`** → may use default from settings, but unreliable
- **`subscribers` accepts multiple emails** — no need to send one at a time
- **`{"data":true}` means QUEUED, not delivered.** Always check `GET /api/logs` for SMTP errors after a test send. A successful API response can still result in `535 Authentication credentials invalid` at SMTP time.
- **Test sends don't appear in campaign stats** — `sent`, `views`, `clicks` on the campaign are NOT incremented by test sends. Only `start-campaign` (real send) updates stats.

### Reliable Alternative: Create + Start a Real Campaign

For verification that SMTP actually works, create a new campaign targeting a small test list and start it:

```python
# 1. Create campaign
campaign = {"name": "SMTP Verify", "subject": "Test", "lists": [test_list_id],
            "type": "regular", "content_type": "html", "body": "<h1>Test</h1>",
            "from_email": "Name <addr@domain.com>", "template_id": 6,
            "messenger": "email",
            "headers": [{"key": "Reply-To", "value": "reply@domain.com"}]}
# POST /api/campaigns → get new_id
# 2. Start it
# PUT /api/campaigns/{new_id}/status {"status":"running"}
# 3. Wait 5-10s, check GET /api/campaigns/{new_id} → sent, bounces
# 4. Check GET /api/logs for errors
```

This goes through the full SMTP pipeline and updates `sent`/`bounces`/`views` stats.

## Click Tracking & Open Tracking

### Open Tracking — Automatic via Template

ListMonk tracks opens when the campaign template includes `{{ TrackView }}` (an invisible 1x1 pixel). The default template includes this. Verify with `GET /api/templates/{id}` — look for `{{ TrackView }}` in the body.

Open tracking is globally enabled when `privacy.disable_tracking` is `false` (check via `GET /api/settings`).

### Click Tracking — Auto-Wrapped at SMTP Time

ListMonk **automatically wraps raw editorial links** (`<a href="https://example.com">`) at SMTP delivery time with tracking redirects. You do NOT need `{{ TrackLink "url" }}` tags in the HTML body.

- **Stored HTML** shows raw links (expected — wrapping happens at send time, not in the template)
- **Delivered email** has wrapped links pointing through ListMonk's tracking domain
- **Click data** appears in `GET /api/campaigns/analytics/clicks?id={id}&from=YYYY-MM-DD&to=YYYY-MM-DD`

### Analytics Endpoints — Date Range REQUIRED

```
GET /api/campaigns/analytics/views?id={id}&from=2026-07-29&to=2026-07-31
GET /api/campaigns/analytics/clicks?id={id}&from=2026-07-29&to=2026-07-31
```

Without `from` and `to` params (in `YYYY-MM-DD` format): `400: {"message":"Invalid 'from' or 'to' dates."}`

### Campaign-Level Stats (No Date Range)

For quick top-line numbers, `GET /api/campaigns/{id}` returns `sent`, `views`, `clicks`, `bounces` directly — no date params needed.

## Subscriber Management

### Search Subscribers

```
GET /api/subscribers?query=email%20%3D%20'xander%40usingaitoscale.com'
```

Query uses SQL WHERE-clause syntax (URL-encoded). Examples:
- `email = 'xander@usingaitoscale.com'`
- `email LIKE '%justin%'`
- `subscribers.email LIKE '%@gmail.com'`

### Bulk Add Subscribers to Lists

```python
# PUT /api/subscribers/lists
payload = {
    "ids": [3, 5],              # subscriber IDs
    "action": "add",            # "add" | "remove" | "unsubscribe"
    "target_list_ids": [1, 2, 6],  # lists to add to
    "status": "confirmed"       # subscription status
}
```

This is the fastest way to ensure seed emails (owner, team) are on every list.

### Pitfall — 409 on Duplicate Subscriber Creation

`POST /api/subscribers` returns `409: {"message":"E-mail already exists."}` if the email is already in the system (even on a different list). Use `PUT /api/subscribers/lists` to add existing subscribers to new lists instead of re-creating.
