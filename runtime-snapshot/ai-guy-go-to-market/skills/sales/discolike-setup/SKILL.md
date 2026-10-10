---
name: discolike-setup
description: One-time DiscoLike onboarding. Use when the user is connecting to DiscoLike for the first time, needs OAuth, hasn't authenticated yet, or asks about setup, BYOM/BYOS, LLM providers, search providers, account status, or initial configuration. Walks through MCP connection, OAuth, plan-tier check, BYOM/BYOS configuration, and a free smoke test.
---

# DiscoLike — Setup

One-time onboarding. Walks the user through every step so they end with a working, verified connection.

## Sequence (do these in order)

### 1. Confirm the MCP is registered
The DiscoLike MCP server should be registered in `~/.hermes/config.yaml` under `mcp_servers.discolike`:
```yaml
  discolike:
    url: https://api.discolike.com/v1/mcp
    timeout: 120
```
If not present, add it:
```bash
hermes config set mcp_servers.discolike.url https://api.discolike.com/v1/mcp
hermes config set mcp_servers.discolike.timeout 120
```
Then restart the gateway: `hermes gateway restart` (or `/restart` in Slack).

### 2. Complete OAuth
The first time you call a DiscoLike MCP tool, it will prompt for authentication. The user needs to authenticate via OAuth at app.discolike.com. In Hermes without Claude Code's native OAuth widget, the flow may differ — the tool may return an OAuth URL the user needs to visit in a browser.

If the MCP tools report an auth error, direct the user to:
1. Visit https://app.discolike.com and sign in
2. The MCP token is tied to the account session
3. Try a free call like `mcp__discolike__account-status` to verify the connection

### 3. Account status (FREE)
Call `mcp__discolike__account-status` — surface plan tier (Starter/Team/Pro/Company/Enterprise), credit balance, rate-limit multiplier.

### 4. Usage check (FREE)
Call `mcp__discolike__usage-statistics` — show month-to-date spend and request volume.

### 5. BYOM — set up LLM provider (optional)
Recommended: **Grok 4.3** (xAI overcapacity makes it cheap). Defaults (OpenAI/Anthropic) work too.

Call `mcp__discolike__llm-providers` to list current config. If the user wants to add Grok:
- Get their xAI API key
- Configure via the dashboard at app.discolike.com → Settings → Integrations → AI Providers

### 6. BYOS — set up search provider (optional)
Currently Serper. A built-in SerpAPI ~3× cheaper is coming — recommend waiting if cost matters.

### 7. Free smoke test
Ask the user for one trivial query they care about ("US dentists", "SaaS in Spain", whatever). Run:
```
mcp__discolike__count-matching-domains
  phrase_match: "<their query>"
  country: "US"
```
Confirms the whole chain works with zero spend.

### 8. Done — hand off
Suggest they next use `discolike-walkthrough` with their real ICP to learn the filter grammar.

## What to save to memory
After setup, record:
- Plan tier (gates tools like segment-domains)
- BYOM provider + model
- BYOS provider
- Whether OAuth is working