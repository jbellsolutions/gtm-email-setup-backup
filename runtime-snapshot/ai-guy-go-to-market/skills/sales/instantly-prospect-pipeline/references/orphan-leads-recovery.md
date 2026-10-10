# Orphan Leads Recovery

When `Instantly leads add` creates leads globally but doesn't link them to a campaign (shows `upload_count: N, total_leads: 0`), the emails are blocked from ALL future campaigns.

## Root Cause

CLI batch upload silently creates global lead records when the JSON payload is missing the `last_name` field. Instantly accepts the upload (`upload_count: N`) but refuses to link orphan records to the campaign (`total_leads: 0`). The `already_added_to_campaign` and `duplicate_count` fields stay at 0 — the leads simply vanish.

Instantly's global dedup then blocks these emails from being uploaded to any campaign, including fresh ones. `ignore_duplicate_leads_in_other_campaign: true` doesn't help — the block is system-level.

## Detection

Upload returns:
```json
{"ok": true, "upload_count": 200, "total_leads": 0, "block_count": 0, "duplicate_count": 0}
```

The lead exists globally but isn't linked:
```bash
Instantly leads get-by-email --email <email>
# Returns: {"id": 4163798930, "email": "lead@example.com", ...}
```

But `Instantly leads list --campaign-id <CID>` shows nothing.

## Recovery

### Single lead
```bash
# 1. Get global ID
Instantly leads get-by-email --email <email> --format json

# 2. Create update payload with custom fields
cat > payload.json << 'EOF'
{"email": "lead@example.com", "first_name": "Name",
 "custom_fields": {"email_subject": "...", "email_body": "...", ...}}
EOF

# 3. Link to campaign
Instantly leads update --campaign-id <CID> --lead-id <GLOBAL_ID> --from-json payload.json
```

### Bulk recovery (parallel)

Python with ThreadPoolExecutor at 5-8 workers:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_lead(row):
    email = row['email']
    # Get lead ID (with retry)
    r1 = subprocess.run(["Instantly", "leads", "get-by-email", 
                         "--email", email, "--format", "json"],
                        capture_output=True, text=True, timeout=20)
    lid = json.loads(r1.stdout).get('id')
    if not lid:
        return False
    
    # Update
    payload = {"email": email, "first_name": row['firstName'],
               "custom_fields": {k: row[k] for k in row if k not in ('firstName','email','company')}}
    with open(f"/tmp/up-{lid}.json", "w") as f:
        json.dump(payload, f)
    
    r2 = subprocess.run(["Instantly", "leads", "update", "--campaign-id", str(cid),
                         "--lead-id", str(lid), "--from-json", f"/tmp/up-{lid}.json"],
                        capture_output=True, text=True, timeout=15)
    return r2.returncode == 0

with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(process_lead, row): row['email'] for row in leads}
    for f in as_completed(futures):
        # Count results
```

**Throughput:** 5 workers = ~2/sec. 8 workers = ~3/sec. For 1,152 leads: ~6 minutes.

**Retry on timeout:** Some `get-by-email` calls hang. Wrap in a 3-attempt retry with 1s backoff and 20s timeout.

## Prevention

Always include `last_name` in CLI batch uploads. Extract from email local part or fall back to company name:
```python
def extract_last_name(email, company):
    local = email.split('@')[0].lower()
    parts = re.split(r'[.\-_0-9]', local)
    for p in parts[1:]:  # skip first part (usually first name)
        p = re.sub(r'[^a-z]', '', p)
        if len(p) >= 2:
            return p.capitalize()
    # Fallback to company
    if company:
        return company.split()[-1].strip('.,\'"')
    return "Contact"
```
