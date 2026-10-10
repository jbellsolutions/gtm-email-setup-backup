# ListMonk SMTP Management & Multi-Server Configuration

Learned Jul 29, 2026. Covers SMTP setup, multi-server config, campaign headers, subscriber management, and common pitfalls.

## SMTP Settings

### Viewing current SMTP config
```
GET /api/settings → data.smtp (array of server objects)
```

Each SMTP server object:
```json
{
  "name": "",
  "uuid": "auto-generated",
  "enabled": true,
  "host": "smtp.resend.com",
  "port": 465,
  "auth_protocol": "login",
  "username": "resend",
  "password": "•••••• (masked on GET)",
  "hello_hostname": "",
  "email_headers": [],
  "max_conns": 2,
  "max_msg_retries": 2,
  "msg_retry_delay": "5s",
  "idle_timeout": "15s",
  "wait_timeout": "10s",
  "tls_type": "TLS",
  "tls_skip_verify": false,
  "from_addresses": []
}
```

### Updating SMTP settings
```
PUT /api/settings → full settings object (replaces everything)
```
**CRITICAL:** GET the full settings first, modify only the SMTP array, then PUT the entire settings object back. PUT replaces, it does not merge.

### Adding a second SMTP server
Append a new object to the `smtp` array and PUT. ListMonk auto-prefixes the `name` field with the messenger type (`email-`), so:
- `name: "resend"` → becomes `email-resend`
- `name: "bird"` → becomes `email-bird`

### Load balancing behavior
ListMonk **randomly load-balances** across all ENABLED SMTP servers. If a secondary server's domain isn't verified yet, **disable it** (`"enabled": false`) to prevent send failures on ~50% of emails.

### Checking SMTP health
```
GET /api/logs → look for "535 Authentication credentials invalid" errors
```
- `{"data":true}` from the test endpoint means QUEUED, not DELIVERED
- Always check logs after a test send — success at API level doesn't mean SMTP delivery worked
- Server restart logs show: `initialized email (SMTP) messenger: resend@smtp.resend.com`

## Campaign Management

### Campaign headers (Reply-To, custom)
The `headers` field expects an **array of objects** with `key`/`value` keys, NOT a plain dict:
```json
"headers": [{"key": "Reply-To", "value": "xander@usingaitoscale.com"}]
```
Using `{"Reply-To": "..."}` returns: `Unmarshal type error: expected=models.Headers, got=object`

### Updating campaigns
- Only **draft** campaigns can be updated via `PUT /api/campaigns/{id}`
- **Finished** campaigns return: `Cannot update a running or a finished campaign.`
- To update content on a finished campaign: create a NEW campaign with the desired settings

### Deleting campaigns
```
DELETE /api/campaigns/{id}
```
Works on finished campaigns. Useful for cleaning up old test campaigns to prevent accidental sends.

### Creating campaigns with full settings
```json
{
  "name": "Newsletter — Issue Title",
  "subject": "Subject line",
  "lists": [6],
  "type": "regular",
  "content_type": "html",
  "body": "<html>...",
  "from_email": "Display Name <newsletter@domain.com>",
  "template_id": 6,
  "tags": ["newsletter"],
  "messenger": "email",
  "headers": [{"key": "Reply-To", "value": "reply@domain.com"}]
}
```

## Subscriber Management

### Finding a subscriber by email
```
GET /api/subscribers?query=email%20%3D%20'user@email.com'
```
The query param uses SQL syntax. URL-encode the entire query string. Example:
- `email = 'justin@usingaitoscale.com'` → URL-encode as `email%20%3D%20%27justin%40usingaitoscale.com%27`
- Wildcard: `email LIKE '%justin%'`

### Adding existing subscriber to additional lists
```
PUT /api/subscribers/lists
Body: {"ids": [subscriber_id], "action": "add", "target_list_ids": [1,2,3], "status": "confirmed"}
```
This is for adding an ALREADY-EXISTING subscriber to more lists. If the subscriber doesn't exist yet, use `POST /api/subscribers`.

### Adding a new subscriber
```
POST /api/subscribers
Body: {"email": "...", "name": "...", "status": "enabled", "lists": [6], "preconfirm_subscriptions": true}
```
Returns 409 if the email already exists in the system.

## Analytics

### Campaign stats (summary)
```
GET /api/campaigns/{id} → status, sent, views, clicks, bounces
```

### Detailed analytics (requires date range)
```
GET /api/campaigns/analytics/views?id={id}&from=2026-07-29&to=2026-07-31
GET /api/campaigns/analytics/clicks?id={id}&from=2026-07-29&to=2026-07-31
```
Without `from` and `to` params, returns: `Invalid 'from' or 'to' dates.`

### Tracking configuration
- Template `{{ TrackView }}` → open tracking pixel (views)
- Template `{{ TrackLink "url" }}` → explicit click tracking on a specific link
- Global setting `privacy.disable_tracking: false` → enables all tracking
- In practice, ListMonk auto-wraps links in HTML campaign bodies at send time when tracking is enabled — no need for explicit `{{ TrackLink }}` tags

## Common Pitfalls

1. **Test endpoint returns `{data:true}` even when SMTP fails** — always check `/api/logs` after sending
2. **Finished campaigns can't be updated** — create a new one instead
3. **Headers must be `[{"key":"...","value":"..."}]`** — not a flat dict
4. **Multiple enabled SMTP servers = random load balancing** — disable unverified servers
5. **PUT /api/settings replaces the entire settings object** — GET first, modify, PUT back
6. **Subscriber query needs URL encoding** — SQL syntax with special characters
7. **409 on subscriber creation** means email exists — use PUT /api/subscribers/lists to add to more lists instead
