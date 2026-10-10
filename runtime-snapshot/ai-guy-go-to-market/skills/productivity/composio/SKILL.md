---
name: composio
description: "⚠️ REQUIRED for all Google integrations — Sheets, Drive, Gmail, Docs. LOAD THIS SKILL FIRST before attempting any Google Workspace task. One API key, 250+ apps, no OAuth dance. Justin's mandated path since July 20, 2026. Do NOT use google-workspace skill's native OAuth."
version: 1.0.0
---

# Composio

Justin's required integration layer for Google Workspace and other SaaS apps. One API key. 250+ pre-built integrations. No per-app OAuth.

## Why Composio Over Native OAuth

| Native OAuth | Composio |
|---|---|
| 10-minute Google Cloud project setup | 30-second API key paste |
| Enable individual APIs in Console | All apps pre-enabled |
| OAuth consent screen + test users | One-click connect in dashboard |
| Token refresh management | Managed by Composio |
| 5+ steps to create a Sheet | 1 API call |

**Justin's directive (July 20, 2026):** "Use Composio and force Use Composio moving forward so we don't run into this embarrassing error." When a task requires Google Sheets, Gmail, Drive, or any Google integration, reach for Composio FIRST. Only fall back to the native `google-workspace` skill's OAuth path if Composio is genuinely unavailable.

## Setup

### Step 1: Get the API key

Go to https://app.composio.dev → Settings → API Keys. Copy the API key. There are TWO key types that work, but for different access paths:

- **MCP access (preferred):** The key shown in the dashboard as "API Key" — use this in the `x-consumer-api-key` header when connecting via the MCP server at `connect.composio.dev/mcp`. Keys with any prefix work here. **This is what Justin's other agents use.**
- **REST API access:** The key shown under Settings → API Keys. Used with `x-api-key` header to hit `backend.composio.dev/api/v3.1/*`.

**Justin's key (July 20, 2026):** `[REDACTED]` — valid for MCP access via `x-consumer-api-key` header.

### Step 2: Add to environment

```bash
# In /opt/data/.env:
COMPOSIO_API_KEY=comp_xxxxxxxxxxxxxxxxxxxx
```

### Step 3: Install the Python SDK

The old `composio_core` package (v0.7.21) is deprecated. Install the new `composio` package:

```bash
pip install --break-system-packages composio
```

Hermes runs inside a virtualenv at `/opt/hermes/.venv`. The package may need to be accessible from both the system Python and the venv. If the venv Python can't find `composio`, use `sys.path.insert(0, '/opt/data/home/.local/lib/python3.13/site-packages')` before importing.

**Quick test after install:**
```python
import sys
sys.path.insert(0, '/opt/data/home/.local/lib/python3.13/site-packages')
from composio import Composio
client = Composio(api_key="your_key_here")
print(client.connected_accounts.list())
```

### Step 4: Connect Google Sheets (one-time)

In the Composio dashboard → Apps → Google Sheets → Connect. Authorize with Justin's Google account. This is a one-click OAuth — no Cloud Console, no API enablement.

### Step 5: Verify connection

```python
client.connected_accounts.list()
# Look for 'google_sheets' or 'google-sheets' in the list
```

## Usage: Google Sheets (Python SDK)

Once authenticated, use the Composio Python SDK to operate on Google Sheets:

```python
import sys, os
sys.path.insert(0, '/opt/data/home/.local/lib/python3.13/site-packages')
from composio import Composio
client = Composio(api_key=os.environ["COMPOSIO_API_KEY"])

# List toolkits
toolkits = client.toolkits.list()
sheets_toolkit = next(t for t in toolkits if 'sheet' in t.name.lower())

# Create spreadsheet
result = client.tools.execute(
    toolkit=sheets_toolkit.name,
    action="CREATE_SPREADSHEET",
    input={"title": "Owned Audiences Tracking"}
)
```

### Key operations
- `CREATE_SPREADSHEET` — new sheet with optional sheet names
- `WRITE_VALUES` — write to a range (include header row)
- `APPEND_VALUES` — add rows at bottom (for daily cron updates)
- `READ_VALUES` — read from a range

## CLI is Unreliable — Use Python SDK

The `composio` CLI (`composio login`, `composio integrations`) hits deprecated v2 API endpoints and returns 400 errors. **Do not use the CLI.** Use the Python SDK (`from composio import Composio`) instead. The CLI may be fixed in future versions but is broken as of July 2026.

## MCP Protocol: Raw JSON-RPC (What Actually Works)

The Python SDK is unreliable due to venv/import conflicts. The raw MCP JSON-RPC protocol is the **definitive integration path**. Here's the exact pattern:

### Step 1: Initialize session

```bash
SESSION_RESP=$(curl -s -D - -X POST "https://connect.composio.dev/mcp" \
  -H "x-consumer-api-key: $API_KEY" \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"hermes","version":"1.0.0"}},"id":1}')

# Extract session ID
SID=$(echo "$SESSION_RESP" | grep -oP 'mcp-session-id: \K[^\r\n]+')
```

### Step 2: Search for tools

```bash
curl -s -X POST "https://connect.composio.dev/mcp" \
  -H "x-consumer-api-key: $API_KEY" \
  -H "mcp-session-id: $SID" \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"COMPOSIO_SEARCH_TOOLS","arguments":{"query":"google sheets create spreadsheet"}},"id":2}'
```

### Step 3: Execute tools via MULTI_EXECUTE

**All app tools (GOOGLESHEETS_*, GMAIL_*, etc.) MUST be called through `COMPOSIO_MULTI_EXECUTE_TOOL`.** Direct tool calls return "Tool not found."

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "COMPOSIO_MULTI_EXECUTE_TOOL",
    "arguments": {
      "session_id": "goes",
      "current_step": "Description of current operation",
      "tools": [
        {
          "tool_slug": "GOOGLESHEETS_CREATE_GOOGLE_SHEET1",
          "arguments": {"title": "My Spreadsheet"}
        }
      ]
    }
  },
  "id": 3
}
```

### Step 4: Parse SSE response

Responses are SSE streams. Parse `data:` lines:

```python
for line in response.split('\n'):
    if line.startswith('data: '):
        outer = json.loads(line[6:])
        if 'result' in outer:
            content = outer['result']['content'][0]['text']
            inner = json.loads(content)
            # inner['data']['results'][0]['response'] has the tool result
```

### CRITICAL Pitfalls

**`arguments` not `parameters`:** Inside each tool object in the `tools` array, the key IS `arguments` (NOT `parameters`, NOT `params`). Using `parameters` silently produces "required field missing" errors. This is the #1 failure mode — wasted 20+ minutes on this in the July 20 session.

**session_id must be `"goes"`:** The COMPOSIO_SEARCH_TOOLS response returns `"session":{"id":"goes",...}`. Use this exact value in all MULTI_EXECUTE calls.

**MCP session ID is per-initialize:** If calls start returning auth/timeout errors, re-initialize to get a fresh `mcp-session-id` header.

**Cell values must be strings (NEW Jul 20):** Writing non-string values (null, None, booleans) to Google Sheets causes `Input should be a valid string on parameter 'values.0.N.str'` errors. Always sanitize: `str(v) if v is not None else ""`.

**Batch write in 50-row chunks (NEW Jul 20):** Google Sheets rate limits are 60 writes/min. Large writes (200+ rows) can fail silently. Batch writes into 50-row chunks with a 0.3s delay between batches.

**`here.now` publish requires `file` command (NEW Jul 20):** The `publish.sh` script requires the `file` binary. It is NOT installed on the VPS by default and `apt-get` requires root. Workaround: use the here.now REST API directly — POST to `/api/v1/publish` with `{"files": [...], "title": "..."}`, PUT the file to the returned pre-signed R2 URL, then POST to `finalizeUrl`.

## Google Sheets Tool Reference

Connected account: `justin@usingaitoscale.com` (connected 2026-07-20). The search query "google sheets create spreadsheet write" returns a plan with these tools:

| Tool | Purpose |
|---|---|
| `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` | Create new spreadsheet |
| `GOOGLESHEETS_VALUES_UPDATE` | Write values to a range |
| `GOOGLESHEETS_VALUES_GET` | Read values from a range |
| `GOOGLESHEETS_GET_SHEET_NAMES` | List worksheet names |
| `GOOGLESHEETS_ADD_SHEET` | Add new worksheet |
| `GOOGLESHEETS_GET_SPREADSHEET_INFO` | Get spreadsheet metadata |
| `GOOGLESHEETS_UPDATE_VALUES_BATCH` | Batch write multiple ranges |
| `GOOGLESHEETS_SPREADSHEETS_VALUES_BATCH_CLEAR` | Clear ranges |

**Rate limits:** 60 reads/min, 60 writes/min. Batch operations through MULTI_EXECUTE to stay under limits.

**`arguments` not `parameters`:** Inside each tool object in the `tools` array for MULTI_EXECUTE, the key is `arguments` — NOT `parameters`. Using the wrong key silently fails.

## Pitfalls

This is the **primary integration path** — what Justin's other agents use. Add to `~/.hermes/config.yaml` or `/opt/data/config.yaml` under `mcp_servers:`:

```yaml
  composio:
    url: https://connect.composio.dev/mcp
    timeout: 180
    headers:
      x-consumer-api-key: [REDACTED]
```

After adding, restart Hermes. Tools appear as `mcp_composio_*` across Google Sheets, Gmail, Drive, GitHub, and 250+ apps. No Python SDK imports needed — tools are first-class Hermes functions.

**Verify the endpoint is live:**
```bash
curl -s -H "x-consumer-api-key: YOUR_KEY" "https://connect.composio.dev/mcp" | head -1
# Returns: {"jsonrpc":"2.0","error":{"code":-32000,"message":"Mcp-Session-Id header is required"}...}
```
The "Mcp-Session-Id header is required" response means the endpoint is live and the key is valid — the MCP client handles session negotiation automatically.

## Supported Apps

Google Sheets, Google Drive, Gmail, GitHub, Notion, HubSpot, Linear, Slack, and 250+ more. Once the API key is set and apps are connected in the dashboard, all tools become available.

## Gmail recruiting workflow

For mailbox triage, applicant review, and draft-only replies:

1. Confirm the connected account identity before reading mail. A connection to `justin@usingaitoscale.com` does not grant access to `hiring@usingaitoscale.com`; do not infer mailbox access from a label or email address mentioned by the user.
2. Search/list labels on the selected account and resolve the exact custom label ID. User-created labels require opaque IDs such as `Label_857...` for API filters, while Gmail search may accept the display name.
3. Fetch all messages, following `nextPageToken` until it is absent, and hydrate messages when previews are incomplete. Do not classify a thread as unanswered from unread state alone: inspect the full thread or message direction and check for a reply from the recruiting mailbox.
4. Review replied examples before drafting so tone and structure are grounded in the mailbox, not invented.
5. Create in-thread drafts with `GMAIL_CREATE_EMAIL_DRAFT`, passing `thread_id` and leaving `subject` empty to preserve threading. Never call a send tool until the user explicitly approves the displayed drafts.
6. Report inaccessible accounts or zero-result searches precisely, including the connected account and label-resolution result. Do not claim applicant triage or draft creation when the requested mailbox is not connected.

## Pitfalls

- **Wrong key format:** Keys starting with `ak_` or `ck_` are NOT invalid — they ARE valid API keys when used with the correct header. For the MCP endpoint (`connect.composio.dev/mcp`), use `x-consumer-api-key: YOUR_KEY`. For the REST API (`backend.composio.dev/api/v3.1/*`), use `x-api-key: YOUR_KEY`. **Do NOT use `Authorization: Bearer`** with Composio — that's for internal dashboard auth, not the API. Confirmed July 20, 2026: `[REDACTED]` works with `x-consumer-api-key` on the MCP endpoint.
- **CLI is broken:** `composio login` and `composio integrations` hit deprecated v2 endpoints. Use the Python SDK.
- **`composio_core` is deprecated:** Remove old `composio-core` package and install `composio` (singular).
- **Venv conflicts:** Hermes runs in `/opt/hermes/.venv`. The `composio` package may install to the system site-packages. Use `sys.path.insert` as a workaround. **The `execute_code` sandbox also can't import composio** — run Python via terminal with `sys.path.insert` instead.
- **Dependency collision (NEW Jul 20, 2026):** Installing `composio` uninstalls `composio_core` and upgrades `openai` (2.16.0 → 2.46.0), `pydantic` (2.12.5 → 2.13.4), and `Pillow` (12.2.0 → 12.3.0), which breaks `browser-use` 0.12.9. Check `pip list | grep browser-use` after install. If broken, re-pin: `pip install --break-system-packages browser-use openai==2.16.0 pydantic==2.12.5 pillow==12.2.0`.
- **Not logged in:** `composio integrations` returns "User not logged in" — the `composio` CLI uses its own auth, separate from the API key. Ignore the CLI entirely.
- **Don't block on OAuth:** If a Google Sheets task comes up and Composio isn't configured, ask for the API key (2 min) rather than guiding through the native Google Cloud OAuth flow (10 min).
- **MCP URL in Slack strips token:** When Justin shares a `connect.composio.dev/mcp` link via Slack, the link formatting strips any embedded Bearer token. Ask for the raw URL. The MCP connection page expects `Authorization: Bearer` on the request.

## References

- `references/composio-setup.md` — Full Composio dashboard setup walkthrough, app connection steps, and API key management
- `references/api-endpoints.md` — API version matrix and v3.1 endpoint discovery (Jul 20, 2026)
- `scripts/run_composio.py` — Wrapper that handles the venv/sys.path issue and returns a configured client. Run with `--check` to verify API key validity.
