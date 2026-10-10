# Efficient Inbox Monitoring (Cron Job)

When monitoring a large campaign (100+ inbox entries), checking every lead's full message history is expensive (~2s per lead × 100 leads = 3+ minutes). Use this targeted approach instead.

## Two-Phase Strategy

### Phase 1: Date/Campaign Filter (cheap)
Pull all inbox pages and filter in-memory before any API calls to `leads messages`:

```python
# Collect all inbox entries from pages 1-N
target_leads = []
for entry in all_inbox_entries:
    cid = entry.get('email_campaign_id')
    reply_time = entry.get('last_reply_time', '')
    
    # Only check: today's replies OR non-default campaigns
    is_today = reply_time.startswith('2026-07-08')  # today's date
    is_other_campaign = cid not in [3577260]  # default/primary campaign
    
    if is_today or is_other_campaign:
        target_leads.append(entry)
```

This typically reduces 100+ entries to ~15-20 — whatever landed today plus entries from secondary campaigns.

### Phase 2: Message History Check (expensive, only on targets)
For each target lead, fetch message history and compare message IDs against `replied_message_ids` in state file:

```python
for lead in target_leads:
    result = subprocess.run([
        'Instantly', 'leads', 'messages',
        '--campaign-id', str(lead['campaign_id']),
        '--lead-id', str(lead['lead_id']),
        '--format', 'json'
    ], ...)
    
    history = json.loads(result.stdout).get('history', [])
    for msg in reversed(history):
        if msg.get('type') != 'REPLY':
            continue
        # Skip bounces, our own replies, already-processed
        ...
```

## Key Patterns

### Reading API keys safely (avoid SQL TRUNCATE false positive)
```python
env_data = {}
with open('/opt/data/.env') as f:
    for line in f:
        line = line.strip()
        if line.startswith('Instantly_API_KEY='):
            env_data['Instantly'] = line.split('=', 1)[1].strip().strip('"').strip("'")
            break
```

### Stripping message ID brackets for comparison
State file entries may or may not have angle brackets. Normalize:
```python
clean_id = msg_id.strip('<>') if msg_id else ''
already_processed = any(clean_id in pid for pid in processed_ids)
```

### Skipping our own replies (domain-based)
```python
our_domains = [
    'speakeragent.ai', 'useaiintegraterz.com', 'joinaiintegraterz.com',
    'horizonedgenv.info', 'successcrestco.info', 'growthmapar.info',
    'strategyvistaaz.info', 'pinnaclepathway.info', 'nexuscorestrategies.info'
]
if any(d in (msg_id or '') for d in our_domains):
    continue  # skip our sent replies
```

### SILENT rule
If Phase 1 produces zero targets, respond `[SILENT]` immediately — no message history calls needed.

## Real-World Results (July 8, 2026)
- Inbox: 120 entries across 7 pages (campaign #3577260: 103, #3442703: 15, #3520103: 2)
- Phase 1 filter: 37 targets (20 from page 1 all-today + 17 from page 7 other-campaigns)
- Actually checked: 37 leads (20 page 1 + 17 page 7 targeted) — skipped 80 leads on pages 2-6
- Result: 0 new replies, all already in state file → `[SILENT]`
- Time saved: ~160 seconds (80 leads × 2s each) vs exhaustive check