# Lead Upload Pitfalls & Workarounds

Captured: July 13, 2026

## Lead credit limit — silent rejection (CRITICAL)

When Instantly's lead credit limit is exhausted, the upload API returns:
```json
{
  "ok": true,
  "upload_count": 1000,
  "total_leads": 0,
  "is_lead_limit_exhausted": true,
  "error": "The lead credit limit has been reached, preventing any further lead imports."
}
```

**The trap:** The API call succeeds (`ok: true`) and shows the upload count, but `total_leads: 0` and `is_lead_limit_exhausted: true`. Leads are silently discarded. Every batch after the limit will show the same pattern.

**Symptom:** Every batch upload to a NEW campaign shows `total_leads: 0` despite `upload_count` showing correct numbers. Leads never appear in the campaign.

**Detection:** Always check the response JSON for `is_lead_limit_exhausted` after every batch upload. Never assume `ok: true` means success.

**Fix:** Purchase more lead credits on Instantly, then re-upload all batches.

## CLI vs MCP batch sizes

| Method | Max leads/call | Use case |
|---|---|---|
| Instantly CLI (`~/.local/bin/Instantly`) | 1000 | Bulk uploads, 100+ leads |
| MCP tool (`mcp_Instantly_add_leads_to_campaign`) | 100 | Small operations, testing |

For bulk uploads (100+ leads), always use the CLI with 1000-lead chunk files. Combine 10×100-lead batches into one 1000-lead file.

## CLI upload pattern

```bash
# Generate 1000-lead chunk files from CSV
python3 scripts/generate_leads.py --csv leads.csv --campaign-id 3617053

# Upload each chunk
~/.local/bin/Instantly leads add --campaign-id 3617053 --from-json /tmp/chunk_01.json
```

## New campaign setup checklist

1. Create campaign via MCP (GETs the ID)
2. Add email accounts
3. Set schedule (timezone, days, hours, max/day)
4. Set settings (send_as_plain_text, follow_up_percentage, stop_lead_settings)
5. Update status to START
6. Upload leads via CLI (1000/chunk)
7. Verify lead count
8. Save sequences if needed

## `block_count` > 0

Some leads may be blocked on upload. The `block_count` field shows how many. Blocked leads may be due to:
- Previously bounced
- On global block list
- Invalid email format

First batch often shows blocks (34/1000 on July 13 men's health batch). Subsequent batches typically show 0 once blocked addresses are filtered.