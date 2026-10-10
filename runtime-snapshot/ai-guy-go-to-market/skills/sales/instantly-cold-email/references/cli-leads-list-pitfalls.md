# Instantly CLI Leads List — Pagination Pitfalls

**Date:** July 2026

## Problem

`mcp_Instantly_list_campaign_leads` truncates large payloads — returns incomplete data for campaigns with rich `custom_fields` (like personalized emails). The CLI is the reliable alternative.

## Correct CLI Command

```bash
Instantly leads list --campaign-id $CID --limit 100 --offset 0 --format json > /tmp/leads_p0.json
```

## Critical Pitfalls

### `--format json` not `--json`
The `--json` flag does NOT exist. Using it produces: `error: unknown option '--json'`. Always use `--format json`.

### `--all` times out on large campaigns
The `--all` auto-pagination flag silently times out on campaigns with 500+ leads (returns empty output). Manual offset pagination is more reliable.

### Data structure
The CLI returns nested JSON: `{"total_leads": N, "data": [...]}`. Each item wraps the lead: `item["lead"]["email"]`, `item["lead"]["company_name"]`, etc. Always unwrap `lead` from `data[i]`.

### Rate limiting
Add 0.3-0.5s sleep between page requests to avoid 429 errors. For 10+ campaigns, use background terminal processes to parallelize.

## Reliable Pattern (Python)

```python
import json, time, subprocess

for offset in range(0, total, 100):
    cmd = f"Instantly leads list --campaign-id {cid} --limit 100 --offset {offset} --format json"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    data = json.loads(result.stdout)
    for item in data.get("data", []):
        lead = item["lead"]
        # Process lead: lead["email"], lead["company_name"], lead["custom_fields"], etc.
    time.sleep(0.3)
```

## File-Based Pattern (for Hermes terminal tool)

When running inside Hermes with limited subprocess access (no execute_code), use:
```bash
# Write each page to a numbered file
Instantly leads list --campaign-id $CID --limit 100 --offset 0 --format json > /tmp/leads_p0.json
Instantly leads list --campaign-id $CID --limit 100 --offset 100 --format json > /tmp/leads_p1.json
# ... then process files in Python
```

## Background Processing for Multiple Campaigns

For 10+ campaigns, run pulls in parallel:
```bash
for cid in 3441343 3442743 3442703; do
  Instantly leads list --campaign-id $cid --limit 100 --offset 0 --format json > /tmp/hvac_${cid}_p0.json
  Instantly leads list --campaign-id $cid --limit 100 --offset 100 --format json > /tmp/hvac_${cid}_p1.json
  # ...
done &
```