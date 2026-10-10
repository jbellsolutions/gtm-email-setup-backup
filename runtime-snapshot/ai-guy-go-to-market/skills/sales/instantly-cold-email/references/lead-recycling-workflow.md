# Lead Recycling Workflow — Same Leads, New Angle

When you need to resend to the same lead list with a different offer/angle but Instantly blocks cross-campaign re-uploads.

## The Problem

Instantly globally blocks email addresses that exist in ANY campaign. You cannot:
- Upload the same email to a new campaign
- Delete from old campaign and re-upload (global block persists)
- Use `leads push` to move leads between campaigns (blocked by same global dedup)

## The Workaround: Update In-Place

Transform the existing campaign without creating a new one:

### Step 1: Pause the campaign
```bash
mcp_Instantly_update_campaign_status(campaign_id, "PAUSED")
```

### Step 2: Generate new email content
Use a generator script that reads existing lead signals and produces new personalized emails. Store in a CSV with columns: `email`, `email_subject`, `email_body`.

### Step 3: Bulk-update custom fields
The existing custom field names on the leads (set during initial upload) are the ONLY fields you can update. New field names are silently dropped.

```python
# Update via CLI (one lead at a time, ~1/sec):
Instantly leads update --campaign-id <ID> --lead-id <map_id> --from-json payload.json

# payload.json format:
{"email": "lead@example.com", "first_name": "Name",
 "custom_fields": {"email_subject": "...", "email_body": "..."}}

# The CLI returns "Not found / Invalid request" but the update succeeds.
# This is a cosmetic JSON parse error. Verify with leads get-by-email.
```

**Parallel bulk update pattern** (5 workers, ~2/sec for 4,500 leads = ~35 min):
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def update_one(email, map_id, first_name):
    payload = {"email": email, "first_name": first_name,
               "custom_fields": {"email_subject": subject, "email_body": body}}
    # write to temp file, run subprocess for leads update
    return 'ok'

with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(update_one, e, m, n): e for e, m, n in all_tasks}
    for f in as_completed(futures):
        result = f.result()
```

**Important:** Instantly API rate limits parallel calls. 5 workers achieved ~2/sec (not 5/sec). Each subprocess call takes ~0.8s. The bottleneck is likely server-side.

### Step 4: Save new sequence
```bash
Instantly campaigns save-sequence --id <ID> --from-json seq.json
```

**Sequence JSON format (single email):**
```json
{"sequences": [{"seq_number": 1, "seq_delay_details": {"delay_in_days": 0},
  "seq_variants": [{"subject": "{{email_subject}}", "email_body": "{{email_body}}", "variant_label": "A"}]}]}
```

**For visible preview in Instantly UI**, use a hardcoded body with short custom field:
```json
{"subject": "referral question",
 "email_body": "Hey {{first_name}},\n\nSaw {{signal}} \u2014 liked what we saw.\n\n...rest of body...",
 "variant_label": "A"}
```

This way Instantly's preview shows the actual email text. Only `{{signal}}` (a short string) needs per-lead custom field storage. However, `signal` must already exist as a custom field name on the leads or it will be silently dropped.

### Step 5: Restart
Operator adds inboxes → START campaign.

## Limitations

- **No new custom field names** — only existing fields can be updated
- **Leads keep old sequence position** — a lead that already got Email 1 of the old sequence will get Email 2 of the new sequence (mismatched context). Acceptable for Trojan horse / completely different angles
- **Completed leads don't get new emails** — only INPROGRESS leads get remaining sequence slots
- **Reply history preserved** — all old replies remain in the campaign

## When to Use

- Same lead list, different offer/angle
- A/B testing copy on the same audience
- Pivoting after poor initial results
- Time-sensitive follow-up to a previous campaign

## When NOT to Use

- When you need clean analytics per campaign
- When sequence position matters (Email 2 should logically follow Email 1)
- When you can source fresh emails for a new campaign (preferred)