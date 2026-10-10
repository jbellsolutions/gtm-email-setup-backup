# Composio Setup Walkthrough

## Dashboard Setup

1. Go to https://app.composio.dev
2. Sign in (Google/GitHub)
3. Navigate to **API Keys** in the sidebar
4. Click **Create API Key** → copy it
5. Add to `/opt/data/.env`: `COMPOSIO_API_KEY=pk_...`

## Connecting Google Sheets

1. In the Composio dashboard, go to **Apps** or **Integrations**
2. Search for "Google Sheets"
3. Click **Connect** → you'll be redirected to Google's OAuth consent screen
4. Authorize with Justin's Google account
5. Back in the dashboard, confirm the connection shows as **Active**

## Connecting Other Apps

Same flow as Google Sheets — search, connect, authorize. Each app connection is independent. Connect only what you need.

## Verifying

After connecting apps, run:

```bash
# Check connected integrations via the CLI
composio integrations
```

Or check via the API:

```bash
curl -H "X-Api-Key: $COMPOSIO_API_KEY" https://backend.composio.dev/api/v1/integrations
```

## API Key vs CLI Login

The `composio` CLI has its own auth (`composio login`). This is separate from the API key. For Hermes agent usage, the API key via MCP server is the correct path — no CLI login needed.

## MCP Server Setup

Add to Hermes MCP config:

```json
{
  "mcpServers": {
    "composio": {
      "command": "composio-mcp",
      "args": ["--api-key", "${COMPOSIO_API_KEY}"]
    }
  }
}
```

This exposes all connected app tools (google_sheets_create, google_sheets_read, etc.) as native Hermes tools. The tools appear automatically once the MCP server connects — no additional configuration needed per tool.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Integration not found" | App not connected in dashboard. Go to Apps → connect. |
| "Unauthorized" | API key invalid or expired. Rotate in dashboard. |
| Tool not appearing in Hermes | Check MCP server config. Restart Hermes. |
| CLI "not logged in" | Ignore — use API key path, not CLI login. |
