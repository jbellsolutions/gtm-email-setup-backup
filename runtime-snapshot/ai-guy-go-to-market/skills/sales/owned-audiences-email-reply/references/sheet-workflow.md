# Sheet Workflow — Owned Audiences Lead Tracker

## Master Sheet

- **URL:** https://docs.google.com/spreadsheets/d/1Pnllx-9B9QWUZYa-3Bj36nbve_dhBfCmx2mt5ZhHYrs/edit
- **Account:** justin@usingaitoscale.com (via Composio MCP)
- **Created:** July 20, 2026

## Tabs

| Tab | Campaign | Lead Count |
|---|---|---|
| All Leads | All OA campaigns | 133 |
| Coaching | #3617053 | 125 |
| HVAC | #3652623, #3652624 | 8 (combined) |
| Recruiting | #3652624 | 6 |
| Solar | #3691319 | 200 |

## Columns

Name | Email | Company | Campaign | Reply Date | Classification | Status | Heat | Phone | Website | LinkedIn | Called 1 | Called 2 | Called 3 | Called 4 | Called 5 | Booked | Notes

## Adding New Leads via Composio MCP

```python
import json, subprocess

SID = "<mcp-session-id>"
API_KEY = "[REDACTED]"
SPREADSHEET_ID = "1Pnllx-9B9QWUZYa-3Bj36nbve_dhBfCmx2mt5ZhHYrs"

def mcp_call(tool_slug, args, call_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "COMPOSIO_MULTI_EXECUTE_TOOL",
            "arguments": {
                "session_id": "goes",
                "current_step": "update leads",
                "tools": [{"tool_slug": tool_slug, "arguments": args}]
            }
        },
        "id": call_id
    }
    # ... curl to https://connect.composio.dev/mcp with x-consumer-api-key and mcp-session-id headers
    # Parse SSE response from data: lines

# Write new lead
mcp_call("GOOGLESHEETS_VALUES_UPDATE", {
    "spreadsheet_id": SPREADSHEET_ID,
    "range": "Coaching!A126",  # Append after last row
    "values": [[name, email, company, ...]],
    "value_input_option": "USER_ENTERED",
    "auto_expand_sheet": True
}, 100)
```

## Daily Cron: Update Pipeline

Every night, pull Instantly inbox → classify replies → update sheet:

1. `Instantly inbox replies --format json` (paginate pages 0-3)
2. Filter for OA campaign IDs (3617053, 3652623, 3652624)
3. Pull message history for real (non-auto) replies
4. Classify using rules from `owned-audiences-email-reply` skill
5. Check `our_replies_after` to determine handling status
6. Write new leads to sheet, update existing rows with new reply dates/classifications

See `scripts/update_sheet.py` for the automation script (pending).
