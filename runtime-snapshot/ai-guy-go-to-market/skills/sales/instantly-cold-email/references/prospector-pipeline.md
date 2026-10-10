# Instantly Prospector End-to-End Pipeline

Source leads from Instantly's built-in Prospector (requires Prospector subscription). Preferred over Apify for niche-targeted B2B lead sourcing.

## Filter Discovery (Always Run First)

Prospector uses **string-based** filter values, not numeric IDs. Discover available values before constructing a search:

```bash
Instantly prospect industries --format json        # industry names
Instantly prospect sub-industries --industry-id <ID>  # sub-industry names
Instantly prospect headcounts --format json        # "0 - 25", "25 - 100", etc.
Instantly prospect revenue --format json           # "$0 - 1M", "$1 - 10M", etc.
Instantly prospect levels --format json            # "C-Level", "VP-Level", etc.
Instantly prospect countries --query "United States" --format json
Instantly prospect keywords --query "fractional cfo" --format json
```

## Correct Filter JSON Format

The filter fields use **string arrays**, NOT numeric IDs. Discovered from `Instantly prospect recent-searches` output (July 2026):

```json
{
  "country": ["United States"],
  "companyHeadCount": ["0 - 25"],
  "companyRevenue": ["$0 - 1M", "$1 - 10M"],
  "level": ["C-Level", "VP-Level", "Director-Level"],
  "companySubIndustry": ["Accounting", "Management Consulting"],
  "companyKeyword": ["Fractional Cfo", "Bookkeeper", "CPA"],
  "limit": 200,
  "dontDisplayOwnedContact": true
}
```

**CRITICAL:** These filter fields are CASE-SENSITIVE string values. `"0 - 25"` not `"0-25"`. `"United States"` not `"united states"`. `"C-Level"` not `"c-level"`. `"Professional Training & Coaching"` must include the ampersand.

Sub-industries that matter for partner categories:
- Financial Services → Accounting (49), Investment Banking
- Business Services → Management Consulting (28), Marketing and Advertising (29), Professional Training & Coaching (30), Design (7), Graphic Design (18)

## The Pipeline (search → fetch → get → upload)

```bash
# Step 1: Search (free, returns filter_id + total_count)
Instantly prospect search --from-json /tmp/search.json --format json
# Returns: {"data": {"filter_id": 123456, "total_count": 25000}}

# Step 2: Fetch (consumes credits, max 10K per call, enriches emails)
echo '{"filter_id": 123456, "limit": 10000}' > /tmp/fetch.json
Instantly prospect fetch --from-json /tmp/fetch.json --format json
# Check results via: Instantly prospect fetched-searches

# Step 3: Get contacts (max 1000 per page, paginate with offset)
echo '{"filter_id": 123456, "limit": 1000, "offset": 0}' > /tmp/get.json
Instantly prospect get --from-json /tmp/get.json --format json

# Step 4: Filter to verified (verificationStatus == "valid") and upload
# Max 500 leads per batch via Instantly leads add
```

## ⚠️ PITFALL: `total_count` ≠ Fetchable Leads

The `search` command's `total_count` is the raw database match count — NOT the number of contacts with usable emails. After fetching, check actual metrics:

```bash
Instantly prospect fetched-searches --format json
# Real numbers: fetch_details.metrics.verifiedEmails
```

Example: CMO search showed `total_count: 25,138` but across 7 keyword-varied fetches only ~5,000 verified emails were available. The remaining ~20K either had no emails in the enrichment system or were duplicates excluded by `dontDisplayOwnedContact`.

## ⚠️ PITFALL: Zero-Email Filters

Some keyword combinations fetch contacts but produce **zero emails**. If `fetched-searches` shows `totalEmails: 0`, the keyword combo is too broad or the enrichment system has no data. Retry with different keywords.

**Working CMO combos:** `["Fractional CMO", "Marketing Consultant", "Marketing Strategist"]`
**Non-working:** `["Marketing Agency"]`, `["Growth Marketing"]`, `["Outsourced Marketing"]`

## ⚠️ PITFALL: `prospect get` limit max is 1000

The `limit` parameter on `prospect get` must be ≤ 1000. Use offset-based pagination:
```python
offset = 0
while True:
    get_json = {"filter_id": fid, "limit": 1000, "offset": offset}
    # ... fetch page
    if not data["data"]["pagination"]["hasMore"]:
        break
    offset += 1000
```

## ⚠️ PITFALL: Background fetch piping loses output

`Instantly prospect fetch` piped through background processes consistently produces empty stdout (the fetch succeeds but output isn't captured). Always verify results via `Instantly prospect fetched-searches` rather than relying on piped output.

## Lead Filtering Rules

Filter fetched contacts by these criteria before uploading:
- `verificationStatus == "valid"` AND `status == "found"`
- Email contains `@` and is non-empty
- Skip emails from obviously wrong domains (e.g., `@duke.edu` for a CPA at a different company)

## Upload Pattern

```python
# Batch size: 500 leads max per Instantly leads add
for i in range(0, len(leads), 500):
    batch = leads[i:i+500]
    upload = {
        "lead_list": batch,
        "settings": {
            "ignore_duplicate_leads_in_other_campaign": True,
            "ignore_global_block_list": True,
            "ignore_unsubscribe_list": True
        }
    }
    # Write to file, then:
    # Instantly leads add --campaign-id <ID> --from-json /tmp/upload.json
```

## Full Campaign Launch Checklist

1. `Instantly prospect search` → get filter_id
2. `Instantly prospect fetch` → enrich with emails (consumes credits)
3. `Instantly prospect fetched-searches` → verify metrics
4. `Instantly prospect get` (paginated) → download contacts
5. Filter to verified emails only
6. `mcp_Instantly_create_campaign` → create campaign
7. `Instantly campaigns save-sequence` (CLI, NOT MCP) → save email sequences
8. `Instantly campaigns update-settings` → plain text, follow_up 100%, stop on reply
9. `Instantly campaigns update-settings` → disable tracking
10. `mcp_Instantly_add_campaign_email_accounts` → attach inboxes
11. Update `/opt/data/scripts/auto_reply_daemon.py` CAMPAIGN_CONTEXT
12. `Instantly leads add` → upload leads in 500-batches
13. `mcp_Instantly_update_campaign_status(status="START")` → launch

## Sequence Save Format

MCP `save_campaign_sequences` is unreliable (400). Always use CLI:
```bash
Instantly campaigns save-sequence --id <ID> --from-json /tmp/seq.json
```

JSON format:
```json
{"sequences": [{
  "seq_number": 1,
  "seq_delay_details": {"delay_in_days": 0},
  "seq_variants": [{
    "subject": "your pipeline",
    "email_body": "line one\n\nline two\n\nline three",
    "variant_label": "A"
  }]
}]}
```

`seq_delay_details` only accepts `delay_in_days` — NOT `delay_in_hours` or `delay_in_minutes`.
