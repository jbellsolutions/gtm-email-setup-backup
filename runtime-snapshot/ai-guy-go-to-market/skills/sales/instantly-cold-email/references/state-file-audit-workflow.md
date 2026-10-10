# State File Audit Workflow

Repeatable process for finding missed replies not in `auto_reply_state.json`. Run weekly or whenever the daemon seems quiet while Instantly shows inbox activity.

## When to Run

- Weekly proactive audit (recommended)
- After any campaign launch (first 48 hours are highest-risk for gaps)
- When daemon reports zero positive replies for >24h but Instantly inbox shows entries
- When operator reports a reply that should have been caught

## Pre-requisites

- `Instantly_API_KEY` set from `/opt/data/.env`
- Instantly CLI at `/opt/data/home/.local/bin/Instantly`
- Write access to `/opt/data/scripts/auto_reply_state.json`

## Step 1: Paginate Full Inbox

Instantly inbox limit is 20 entries per call. For active campaigns with 500+ sends, the inbox can be 100-200+ entries.

```bash
export PATH=/opt/data/home/.local/bin:$PATH
export Instantly_API_KEY=$(grep Instantly_API_KEY /opt/data/.env | cut -d= -f2)

for offset in $(seq 0 20 300); do
  echo '{"offset": '$offset', "limit": 20}' > /tmp/inbox_payload.json
  Instantly inbox replies --from-json /tmp/inbox_payload.json --format json > /tmp/inbox_p${offset}.json
  count=$(python3 -c "import json; d=json.load(open('/tmp/inbox_p${offset}.json')); print(len(d.get('data', [])))")
  echo "Offset $offset: $count"
  [ "$count" -lt 20 ] && break
done
```

## Step 2: Filter to Targets

Not every inbox entry needs message history fetched. Filter to:

1. **Recent replies** (last 72h based on `last_reply_time`)
2. **Active campaigns** — all entries from ACTIVE campaigns regardless of timestamp
3. **Skip known auto-responder addresses** — `support@`, `help@`, `noreply@` can be pre-filtered

```python
from datetime import datetime, timezone, timedelta

cutoff = datetime.now(timezone.utc) - timedelta(hours=72)
active_campaigns = {3577260, 3520103, 3442703}  # update from campaigns table

targets = {}
for entry in all_entries:
    if entry['email_campaign_id'] in skip_campaigns:
        continue
    lrt = entry.get('last_reply_time', '')
    if lrt:
        dt = datetime.fromisoformat(lrt.replace('Z', '+00:00'))
        if dt < cutoff:
            continue
    targets[entry['email_lead_id']] = entry
```

## Step 3: Fetch Per-Lead Message History

For each target lead, fetch message history to get actual reply bodies and RFC 5322 message IDs.

```python
for lid, entry in targets.items():
    cid = entry['email_campaign_id']
    cmd = ['Instantly', 'leads', 'messages', '--campaign-id', str(cid),
           '--lead-id', str(lid), '--format', 'json']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
    hist = json.loads(result.stdout)
    # ... process history ...
```

**Pitfalls:**
- `lead-id` MUST be `email_lead_id` from inbox, NOT `email_lead_map_id` (returns empty history silently)
- Response is nested under `history` key: `hist['history']`
- 222 inbox entries × ~1s per API call = ~4 minutes. Budget accordingly.

## Step 4: Cross-Reference Against State

For each REPLY-type message (not SENT, not bounce), normalize the message ID and check against state:

```python
# Normalize: strip angle brackets for comparison
replied_normalized = set()
for mid in state['replied_message_ids']:
    m = mid.strip()
    if m.startswith('<') and m.endswith('>'):
        replied_normalized.add(m[1:-1])
    else:
        replied_normalized.add(m)

# Check each reply
for msg in history:
    if msg.get('type') != 'REPLY':
        continue
    msg_id = msg.get('message_id', '')
    
    # Skip bounces (mailer-daemon)
    if 'mailer-daemon' in msg.get('from_name', '').lower():
        continue
    if 'mailer-daemon' in msg.get('from_email', '').lower():
        continue
    
    # Normalize for comparison
    mid = msg_id.strip()
    if mid.startswith('<') and mid.endswith('>'):
        mid = mid[1:-1]
    
    if mid and mid not in replied_normalized:
        # NEW: not in state file → classify and report
```

**Key normalization gotcha:** State file entries sometimes lack angle brackets. Always strip brackets from both sides before comparison.

## Step 5: Classify, Draft, Report

For each new reply:
1. Strip HTML: `re.sub(r'<[^>]+>', ' ', body)`
2. Extract just the reply part (before "On ... wrote:" or "-----Original Message-----")
3. Classify using patterns from `reply-classifier-patterns.md`
4. For `positive_interested` / `positive_soft`: generate draft reply
5. Report ALL new replies to operator (format below)

## Step 6: Update State File

Add all new message IDs to state, plus any new hostile/unsub senders:

```python
state['replied_message_ids'].extend([r['message_id'] for r in new_replies])
for r in new_replies:
    if r['classification'] == 'hostile':
        state.setdefault('hostile_senders', []).append(r['email'])
    if r['classification'] == 'unsubscribe':
        state.setdefault('unsub_senders', []).append(r['email'])

with open('/opt/data/scripts/auto_reply_state.json', 'w') as f:
    json.dump(state, f, indent=2)
```

## Report Format

```
📬 Cold Email Reply Monitor — [Day, Date Time]

[N] missed replies discovered across [campaigns].

## 🔴 Campaign #ID — [N] Genuine Positives

### 1. Name @ domain.com — classification
> "reply text"

✏️ Draft: [draft text]

## 🟡 Campaign #ID — Other Notable Replies

| Lead | Reply | Type |
|---|---|---|
| ... | ... | ... |

## 📊 State File Update
- Before: N message IDs
- After: N message IDs (+N)
- New hostile: N
- New unsubs: N
```

## Historical Audit Results

| Date | Missed | Campaigns | Positives Found | State Before → After |
|---|---|---|---|---|
| Jul 7 (first) | 12 | TX HVAC, AI Guy, PR | Alpha Mechanical, Ben Bloch (2) | 83 → 95 |
| Jul 7 (second) | 55 | PR v2, TX HVAC | Ron, Spark, Point (3) + Austral (still unhandled) | 95 → 150 |

## Cost Estimate

- Inbox pagination: free (included in Instantly API)
- Per-lead message history: ~1s each, ~N seconds total
- Total for 200-entry inbox: ~4 minutes
- With classification + draft generation: ~5-6 minutes total