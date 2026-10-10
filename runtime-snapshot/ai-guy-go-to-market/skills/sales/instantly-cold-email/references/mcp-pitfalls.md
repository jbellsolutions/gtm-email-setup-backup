# Instantly MCP Tool Reliability

Two Instantly MCP tools consistently fail with HTTP 400. Always use curl directly via the terminal tool instead. Both patterns are documented in `references/Instantly-api.md` and `references/sequence-json-template.md`.

## `mcp_Instantly_save_campaign_sequences`

**Failure:** Always returns 400.
**Root cause:** Auto-includes `distribution_percentage` in `seq_variants`, which the API rejects.
**Workaround:** Use curl with the `references/sequence-json-template.md` template.
**Verified:** July 2026 — three consecutive failures on campaign #3692104, then successful via curl.

## `mcp_Instantly_update_campaign_schedule`

**Failure:** Always returns 400.
**Root cause:** Unknown — fails regardless of payload correctness.
**Workaround:** Use curl:
```bash
curl -s -X POST "https://server.Instantly/api/v1/campaigns/{id}/schedule?api_key=$Instantly_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timezone":"America/New_York","days_of_the_week":[1,2,3,4,5],"start_hour":"08:00","end_hour":"17:00","max_new_leads_per_day":100,"min_time_btw_emails":9}'
```
**Field pitfalls:** `max_new_leads_per_day` (NOT `max_leads_per_day`), `min_time_btw_emails` is required.
**Verified:** July 2026 — two MCP failures on campaign #3692104, then successful via curl.

## Working MCP Tools (verified July 2026)

These work reliably:
- `mcp_Instantly_list_campaigns`
- `mcp_Instantly_get_campaign`
- `mcp_Instantly_get_campaign_analytics`
- `mcp_Instantly_get_campaign_statistics`
- `mcp_Instantly_list_campaign_leads`
- `mcp_Instantly_list_campaign_email_accounts`
- `mcp_Instantly_add_campaign_email_accounts`
- `mcp_Instantly_list_email_accounts`
- `mcp_Instantly_update_campaign_status`

## CLI Mailbox List Format

The `Instantly mailboxes list --limit 100` command outputs raw JSON array to stdout (stderr carries API call noise). Redirect stderr to /dev/null for clean JSON:

```bash
Instantly mailboxes list --limit 100 2>/dev/null > /tmp/mailboxes.json
```

Then parse with Python:
```python
import json
with open('/tmp/mailboxes.json') as f:
    data = json.load(f)
winnr = [a for a in data if any(t.get('tag_name')=='Winnr' for t in a.get('tags',[]))]
```
