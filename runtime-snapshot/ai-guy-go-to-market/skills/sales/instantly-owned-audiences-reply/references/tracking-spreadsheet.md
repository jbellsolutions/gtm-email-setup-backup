# Owned Audiences Tracking Spreadsheet

Justin's Google Sheets tracking for all Owned Audiences leads across all three campaigns (#3617053 Coaching, #3652623 HVAC, #3652624 Recruiting).

## Sheet Structure

### Columns (in order)

| Column | Description |
|---|---|
| Name | Lead full name |
| Email | Lead email address |
| Company | Company/org name |
| Campaign | Which OA campaign (Coaching / HVAC / Recruiting) |
| Reply Date | Date of first reply (YYYY-MM-DD) |
| Classification | positive_interested / positive_soft / neutral_question / negative_notfit / hostile / unsubscribe / ooo / auto_responder |
| Status | booked / replied / plan_built / awaiting_followup / declined_after_positive / dead |
| Heat | 🔥 BOOKED / ⭐ HOT / 🟡 WARM / 📋 NEUTRAL / ❄️ COLD / 🤖 AUTO |
| Reply Body | Condensed reply body (first 100 chars) |
| Phone | Phone number if available |
| Website | Company website |
| LinkedIn | LinkedIn profile URL |
| Called 1 | Date/timestamp of first call attempt |
| Called 2 | Date/timestamp of second call attempt |
| Called 3 | Date/timestamp of third call attempt |
| Called 4 | Date/timestamp of fourth call attempt |
| Called 5 | Date/timestamp of fifth call attempt |
| Booked | YES/NO — whether a meeting was booked |
| Notes / Behaviors | Any tracked behavior (opened links, replied again, timezone issues, etc.) |

### Tabs

- **Coaching (#3617053)** — all coaching leads
- **HVAC (#3652623)** — all HVAC leads
- **Recruiting (#3652624)** — all recruiting leads
- **HOT** — filtered view of 🔥 and ⭐ leads across all campaigns

### Heat Scoring

| Heat | Criteria |
|---|---|
| 🔥 BOOKED | Meeting booked / confirmed |
| ⭐ HOT | Status is replied or plan_built — active conversation |
| 🟡 WARM | Positive classification but unhandled or awaiting follow-up |
| 📋 NEUTRAL | Neutral/unclassified replies |
| 🤖 AUTO | Auto-responders (support@, info@, OOO) |
| ❄️ COLD | Hostile, unsubscribe, negative_notfit, declined |

## Publishing (here.now fallback)

If Composio MCP isn't available (Hermes hasn't restarted), publish the HTML tracker to here.now as a live URL instead:
1. Build the HTML table (see above schema)
2. Publish via here.now REST API (NOT the publish.sh script — the `file` command is missing on this VPS)
3. Share the live URL

The REST API flow (when `publish.sh` fails due to missing `file`):
```bash
# 1. Create publish
SHA=$(sha256sum /tmp/oa_sheet/index.html | cut -d' ' -f1)
BODY=$(jq -n --argjson files '[{"path":"index.html","size":50016,"contentType":"text/html","hash":"'$SHA'"}]' \
  '{files: $files, title: "Owned Audiences Lead Tracker"}')
RESP=$(curl -sS -X POST "https://here.now/api/v1/publish" \
  -H "authorization: Bearer $HERENOW_API_KEY" \
  -H "content-type: application/json" \
  -d "$BODY")

# 2. Upload file to the pre-signed URL
UPLOAD_URL=$(echo "$RESP" | jq -r '.upload.uploads[0].url')
curl -sS -X PUT "$UPLOAD_URL" -H "Content-Type: text/html" --data-binary @index.html

# 3. Finalize
VERSION_ID=$(echo "$RESP" | jq -r '.upload.versionId')
FINALIZE_URL=$(echo "$RESP" | jq -r '.upload.finalizeUrl')
curl -sS -X POST "$FINALIZE_URL" \
  -H "authorization: Bearer $HERENOW_API_KEY" \
  -H "content-type: application/json" \
  -d "{\"versionId\":\"$VERSION_ID\"}"
```

## Daily Cron Workflow

### Schedule
Run at end of each day (e.g., 11 PM ET / 3 AM UTC).

### Update Logic

1. **Pull Instantly inbox** — pages 0-3 for all OA campaigns
2. **Filter auto-responders** — email prefix heuristic (support@, info@, etc.)
3. **Pull message history** — for remaining real leads
4. **Classify replies** — using the classify_reply() pipeline
5. **Read existing sheet** — via Composio `READ_VALUES`
6. **Deduplicate** — match by email; if lead exists, UPDATE the row; if new, APPEND
7. **Update columns** — new reply date, updated classification, status changes
8. **Recalculate heat** — based on latest status and classification
9. **Write back** — `WRITE_VALUES` or `APPEND_VALUES` via Composio

### Update vs Append

- **Match by email** — case-insensitive email comparison against existing sheet
- **Update existing rows:** If lead is already in sheet, update their Reply Date, Classification, Status, Heat, Reply Body columns. Do NOT overwrite Called 1-5 or Booked columns (manually maintained).
- **Append new rows:** If email not found, append a fresh row with all available data.

### Cron Pitfall Prevention
- The cron MUST use the same classification pipeline as the monitoring cron to avoid mismatches
- Do NOT overwrite manually maintained columns (Called 1-5, Booked, Notes)
- If a lead that was previously dead/hostile replies again positively, flag prominently — this is rare and worth attention

## Composio Integration

The Google Sheet lives in Justin's Google Drive, accessed via Composio (never native Google OAuth). The Sheet ID is stored in state. All read/write/append operations go through the Composio Python SDK:

```python
import sys, os
sys.path.insert(0, '/opt/data/home/.local/lib/python3.13/site-packages')
from composio import Composio
client = Composio(api_key=os.environ["COMPOSIO_API_KEY"])
```

## Initial Data (July 20, 2026)

Built from `owned_audiences_followups.json` (91 leads) + Instantly inbox sweep (42 additional). Total: 133 leads.

| Metric | Value |
|---|---|
| Total leads | 133 |
| Booked | 1 (Gina Tucci) |
| Hot (plan_built/replied) | 7 |
| Auto-responders | 50 |
| Cold (hostile/unsub/declined) | 33 |
| Positives that later declined | 2 (Kareem, Shira) |
| HVAC positives | 0 |
| Recruiting positives | 0 |