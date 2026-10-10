# Test Sends, SMTP Key Rotation, and Subscriber Management

Learned Jul 29, 2026 during People Person newsletter test via ListMonk + Resend SMTP.

## Test Campaign Endpoint — Two Pitfalls

### 1. Payload must include messenger, from_email, and template_id

`POST /api/campaigns/{id}/test` requires more than just the content fields. The test payload must include:

```json
{
  "name": "...",
  "subject": "...",
  "lists": [6],
  "type": "regular",
  "content_type": "html",
  "body": "<html>...",
  "messenger": "email",           // REQUIRED — omit → 400 "Unknown messenger ."
  "from_email": "Name <addr>",    // REQUIRED
  "template_id": 6,               // REQUIRED
  "subscribers": ["a@b.com"]      // one or more recipients
}
```

The `scripts/lm.sh test-campaign` command was patched Jul 2026 to include these fields and accept multiple email addresses.

### 2. Test sends may not actually deliver

Even when the test endpoint returns `{"data":true}` and no error appears in `GET /api/logs`, the email may never arrive. Test sends use a different code path than the campaign manager pipeline. SMTP auth failures during test sends may not generate log entries.

**Symptom:** API says success, logs show nothing, inbox never receives the email.

### Reliable alternative: real campaign send to test list

Instead of the test endpoint, create a new campaign targeting a small test list (2-4 subscribers), then start it:

```bash
# Create campaign on test list
scripts/lm.sh create-campaign "Test Name" "Subject" 6 body.html

# Start sending
scripts/lm.sh start-campaign <new_id>
```

This goes through the normal campaign manager pipeline (`manager.go`), generates log entries on both success and failure, and increments `sent`/`views`/`clicks`/`bounces` counters you can verify via `GET /api/campaigns/{id}`.

**Verification pattern:**
- `GET /api/campaigns/{id}` → check `sent > 0` and `bounces == 0`
- `GET /api/logs` → look for `start processing campaign` and `campaign ... finished` with no `error sending message` lines
- `GET /api/campaigns/analytics/views?id={id}&from=YYYY-MM-DD&to=YYYY-MM-DD` → open tracking

## SMTP Password Rotation (Resend API Key)

When the Resend API key expires or needs rotation:

1. **GET current settings:** `GET /api/settings` → grab the full settings JSON
2. **Modify SMTP password:** In the `smtp` array, set `smtp[0].password` to the new Resend API key
3. **PUT entire settings:** `PUT /api/settings` with the **complete** settings object (PUT replaces — must send everything back, not just the changed field)
4. **Auto-reinit:** ListMonk reinitializes the SMTP messenger automatically after a settings PUT (server restarts)
5. **Verify:** `GET /api/logs` → look for `initialized email (SMTP) messenger: resend@smtp.resend.com` with no error lines

**Key detail:** The password field in `GET /api/settings` is masked (bullet characters `••••`). You cannot read the actual current password from the API. If SMTP auth fails (`535 Authentication credentials invalid` in logs), the only fix is to PUT a new password.

**Common error pattern:** `535 Authentication credentials invalid` in `GET /api/logs` means the SMTP password is wrong/expired. Every campaign test before Jul 29 showed this error until the Resend key was updated.

## Subscriber List Management

### Add existing subscriber to a new list

When a subscriber already exists in ListMonk but isn't on the target list:

```bash
# PUT /api/subscribers/lists
scripts/lm.sh raw PUT /api/subscribers/lists \
  '{"ids":[3],"action":"add","target_list_ids":[6],"status":"confirmed"}'
```

- `ids`: subscriber IDs (not emails)
- `action`: "add" | "remove" | "unsubscribe"
- `target_list_ids`: list IDs to add to
- `status`: "confirmed" skips opt-in confirmation

Response: `{"data": true}` on success.

### Search for a subscriber by email

```bash
# URL-encode the SQL query
scripts/lm.sh raw GET \
  '/api/subscribers?per_page=100&query=email%20%3D%20%27justin%40example.com%27'
```

Supports SQL `LIKE '%pattern%'` for fuzzy matching. Returns subscriber ID, email, name, and current lists.

### Common flow: find subscriber → add to test list → send campaign

1. Search by email → get subscriber ID
2. Add to target list via `PUT /api/subscribers/lists`
3. Create campaign on that list
4. Start campaign
5. Verify sent/bounces via `GET /api/campaigns/{id}`

## Analytics Endpoints Require Date Params

`GET /api/campaigns/analytics/{views|clicks|bounces|links}` require `from` and `to` date params in YYYY-MM-DD format. Without them: `400 "Invalid from or to dates."`

```bash
scripts/lm.sh raw GET \
  '/api/campaigns/analytics/clicks?id=12&from=2026-07-29&to=2026-07-30'
```
