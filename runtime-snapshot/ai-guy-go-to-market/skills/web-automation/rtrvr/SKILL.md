---
name: rtrvr
version: "1.0"
description: Rtrvr.ai AI web agent — browser automation, web scraping, and MCP server for AI agents. DOM-native agents with 81.4% WebBench accuracy. Three execution modes (cloud, extension, auto). Apache 2.0.
---

# rtrvr.ai — AI Web Agent Platform

Browser automation platform that runs AI agents in real browsers. Execute tasks in plain English — clicking, typing, navigating, extracting data autonomously. Built by ex-Google engineers. 81.4% WebBench accuracy (#1). 30,000+ users.

## Quick Reference

| Concept | Detail |
|---------|--------|
| **CLI** | `rtrvr` — global npm binary (`@rtrvr-ai/cli` v0.2.1) |
| **Cloud API** | `https://api.rtrvr.ai` |
| **MCP Server** | `https://mcp.rtrvr.ai` |
| **Control Plane** | `https://cli.rtrvr.ai` |
| **License** | Apache 2.0 |
| **GitHub** | `rtrvr-ai/rtrvr-cli` |
| **Pricing** | Free 250 credits + BYOK. Pro $29.99/mo (4K credits) |
| **⚠️ SDK Status** | `@rtrvr-ai/sdk` and `@rtrvr-ai/core` are DEPRECATED on npm. Only the CLI is actively published. |

## When to Use Rtrvr

- **Web scraping at scale** — dynamic JS SPAs, pagination, infinite scroll
- **Browser automation** — form filling, multi-step workflows, file uploads
- **Lead enrichment** — visit company sites row-by-row, extract contacts/tech stack
- **E-commerce monitoring** — competitor pricing, stock checks, product data
- **QA testing** — adaptive testing without brittle selectors
- **Authenticated workflows** — logged-in sessions via Chrome Extension
- **Scheduled monitoring** — recurring web checks with alerts
- **MCP integration** — expose browser tools to any MCP client

## Installation

```bash
npm install -g @rtrvr-ai/cli
```

Verify:
```bash
rtrvr --version
rtrvr doctor
```

## Authentication

### Method 1: OAuth (browser-based, recommended)
```bash
rtrvr auth login --oauth
```

### Method 2: API Key (headless/servers)
```bash
rtrvr auth login --api-key rtrvr_...
```

### Method 3: Environment Variable
```bash
export RTRVR_API_KEY=rtrvr_...
# or
export RTRVR_AUTH_TOKEN=mcp_at_...
```

Token prefixes: `rtrvr_` (full cloud + CLI), `mcp_at_` (MCP-only OAuth).

Check status:
```bash
rtrvr auth status
```

## CLI Commands

### `rtrvr run` / `rtrvr agent` — Run AI Agent Tasks

Execute browser tasks in plain English.

```bash
# Basic task
rtrvr run "Extract the top 10 products and prices" --url https://example.com

# From file
rtrvr run --input-file ./task.txt --url https://example.com

# From stdin
echo "Summarize this page" | rtrvr run --url https://example.com

# Structured output with JSON schema
rtrvr run "Extract products" --url https://example.com --schema-file schema.json --json

# Force cloud (no local browser needed)
rtrvr run "task" --url https://example.com --cloud

# Force local extension (auth sessions)
rtrvr run "task" --url https://example.com --extension

# Target specific extension device
rtrvr run "task" --url https://example.com --device-id my-device

# Disable streaming
rtrvr run "task" --url https://example.com --no-stream
```

### `rtrvr scrape` — Web Scraping

```bash
rtrvr scrape --url https://example.com
rtrvr scrape --url https://example.com --target cloud --json
rtrvr scrape --url https://example.com --extension --device-id my-device
```

### `rtrvr raw` — Direct MCP Tool Access

Low-level access to individual MCP tools:

```bash
# Extract structured data
rtrvr raw extract --param user_input="all product names and prices" --param tab_urls='["https://example.com"]'

# Multi-page crawl
rtrvr raw crawl --param user_input="extract contact info" --param tab_urls='["https://example.com"]' --param max_pages=10

# Interact with page
rtrvr raw act --param user_input="click login, fill form" --param tab_urls='["https://example.com"]'

# Call any tool directly
rtrvr raw tool planner --param user_input="..." --param tab_urls='["..."]'
```

### `rtrvr extension` — Extension Planner

```bash
rtrvr extension "Click the login button and fill the form" --url https://example.com
```

### `rtrvr devices` — Device Management

```bash
rtrvr devices list
```

### `rtrvr skills` — Local Skill Templates

```bash
rtrvr skills templates              # Built-in templates
rtrvr skills install-template agent-web
rtrvr skills add ./my-skill.md
rtrvr skills list
rtrvr skills apply my-skill "task" --target auto
```

### `rtrvr mcp` — MCP Configuration

```bash
# Generate MCP config for Claude Code
rtrvr mcp init --client claude

# For Cursor
rtrvr mcp init --client cursor

# Generic config
rtrvr mcp init --client generic

# OAuth mode
rtrvr mcp init --client claude --oauth

# Print MCP endpoint URL
rtrvr mcp url
```

### Utility Commands

```bash
rtrvr doctor           # Diagnose connectivity, auth, capabilities
rtrvr capabilities     # Check feature access
rtrvr profile          # Account identity
rtrvr config get       # View config
rtrvr config set defaultTarget cloud
```

## Re-Routable Execution via Direct Fetch

For when you don't have/want the CLI installed — universal endpoint:

```
https://agent.rtrvr.ai/v1/a2w/runs
```

Parameters (POST JSON):
```json
{
  "url": "https://target-site.com",
  "prompt": "Extract all pricing information",
  "execution": "cloud",
  "format": "markdown"
}
```

Or GET:
```
https://agent.rtrvr.ai/v1/a2w/runs?url=https://target.com&prompt=extract+prices&execution=cloud&format=markdown
```

`execution` values: `cloud`, `browser`, `device`
`format` values: `markdown`, `json`

## REST API (Direct)

### Agent API — Full end-to-end browser tasks
```
POST https://api.rtrvr.ai/agent
Authorization: Bearer rtrvr_...
Content-Type: application/json

{
  "input": "Extract all pricing plans and features",
  "urls": ["https://example.com/pricing"],
  "target": "cloud",
  "json": true
}
```

### Scrape API — Raw DOM extraction
```
POST https://api.rtrvr.ai/scrape
Authorization: Bearer rtrvr_...
Content-Type: application/json

{
  "urls": ["https://example.com"],
  "target": "cloud"
}
```

Responses return inline (no polling needed). Streaming via SSE for long tasks.

## MCP Server — Native Integration with AI Tools

### MCP Tools (8 total)

| Tool | Description | Best For |
|------|-------------|----------|
| `planner` | Multi-step browser automation planner | Complex workflows |
| `act_on_tab` | Interact with a web page (click, type, navigate) | Single-page interaction |
| `extract_from_tab` | Extract structured data from a page | Data extraction |
| `crawl_and_extract_from_tab` | Crawl and extract across multiple pages | Multi-page scraping |
| `cloud_agent` | Run a cloud AI agent | End-to-end cloud tasks |
| `cloud_scrape` | Cloud-based page scraping | Simple scraping |
| `list_devices` | List online extension devices | Extension routing |
| `get_current_credits` | Check credit balance | Billing monitoring |

### Configuring for Hermes (Native MCP Client)

Add to Hermes `config.yaml`:

```yaml
mcp_servers:
  rtrvr:
    type: http
    url: https://mcp.rtrvr.ai
    headers:
      Authorization: "Bearer rtrvr_YOUR_API_KEY"
    # Or OAuth:
    # headers:
    #   Authorization: "Bearer mcp_at_YOUR_OAUTH_TOKEN"
```

After restart, all 8 rtrvr tools appear as MCP tools in Hermes.

### Configuring for Claude Desktop

```json
{
  "mcpServers": {
    "rtrvr": {
      "command": "npx",
      "args": ["-y", "@rtrvr-ai/cli", "mcp", "init", "--client", "claude"]
    }
  }
}
```

## Execution Modes

| Mode | Flag | Uses | Pros | Cons |
|------|------|------|------|------|
| **Auto** | `--target auto` (default) | Extension-first, cloud fallback | Smart routing | Extension must be online |
| **Cloud** | `--cloud` | Managed browsers via API | No local setup, scalable | No auth sessions by default |
| **Extension** | `--extension` | Local Chrome Extension | Logged-in sessions, cookies | Requires browser open |

Response metadata tells you which mode won:
```json
{
  "metadata": {
    "selectedMode": "cloud",
    "fallbackApplied": true,
    "fallbackReason": "no extension devices online"
  }
}
```

## Configuration

Config file: `~/.config/rtrvr/config.json`

| Key | Default | Description |
|-----|---------|-------------|
| `defaultTarget` | `auto` | Default routing mode |
| `preferExtensionByDefault` | `false` | Prefer extension in auto |
| `retryMaxAttempts` | `1` | Max retry attempts |
| `retryBaseDelayMs` | `250` | Base retry delay |
| `retryMaxDelayMs` | `4000` | Max retry delay |

Set via CLI:
```bash
rtrvr config set defaultTarget cloud
rtrvr config set retryMaxAttempts 3
```

Or environment variable override: `RTRVR_API_KEY`

## Credit Cost Analysis (Tested June 2026)

Every cloud operation consumes credits. Here is the real breakdown:

| Operation | Cost | Breakdown | $ Equivalent |
|-----------|------|-----------|-------------|
| `rtrvr scrape` (simple page) | 5 credits | 1 browser + 4 proxy | ~$0.035 |
| `rtrvr run` (agent task) | 5+ per step | 1 browser + 4 proxy per tool call | ~$0.035+ per step |
| `rtrvr raw extract` (MCP tool) | TBD | probably similar | ~$0.03-0.04 |

**Key insight: 80% of cost is proxy credits.** The residential proxy layer is the expensive part. For pages that don't need anti-detection, you're paying for proxy you may not need.

### Credit Efficiency Strategies

1. **Use `rtrvr scrape` over `rtrvr run` whenever possible** — agent tasks burn credits per tool call. A simple scrape costs 5 credits. An agent run that does planning + act + extract could cost 15+.
2. **The `--no-stream` flag doesn't reduce credits** — it only affects output format. Credits are per-operation regardless.
3. **Batch static pages** — use `rtrvr scrape` for simple extraction. Only use agent mode (`rtrvr run`) when you need multi-step interaction (clicking, form filling, navigation).
4. **Extension mode might bypass proxy credits** — the Chrome Extension uses your local browser, so no residential proxy needed. But requires the extension to be online.
5. **BYOK (Gemini) for extension mode** — bring your own Gemini API key from ai.studio and extension mode uses your key, not rtrvr credits.
6. **REST API is same cost as CLI** — both hit the same cloud endpoint. Use whatever is more convenient.
7. **For high-volume scraping**: At $0.035/page, 1,000 pages = $35. Compare to ScraperCity ($2-5/run for 100s of leads) or Browserbase (free tier). Rtrvr is competitive for JS-heavy sites but expensive for simple static pages.

### When Rtrvr Is Worth It vs Alternatives

| Scenario | Best Tool | Why |
|----------|-----------|-----|
| Static HTML pages | ScraperCity or `curl` | No proxy needed, cheaper |
| JS-heavy SPAs | **Rtrvr** | DOM-native, handles JS rendering |
| Anti-bot protected sites | **Rtrvr** | Residential proxies, Chrome Extension APIs |
| Meta Ad Library | **Rtrvr** (test) | Non-CDP, may avoid detection |
| Bulk lead lists | ScraperCity | Better $/lead ratio |
| Multi-step form filling | **Rtrvr** | Agent mode handles complex workflows |
| Authenticated/logged-in sites | **Rtrvr Extension** | Cookie sync, session-aware |
| Scheduled monitoring | **Rtrvr** + cron | Built-in scheduling, webhooks |

## Account Status (Justin — June 2026)

- **Email:** jbellsolutions@gmail.com
- **Plan:** Starter (free tier)
- **Credits:** 1,490 remaining (of 1,500 starting)
- **Renewal:** June 30, 2026
- **Google Auth:** Linked (Drive, Sheets, Docs, Slides)
- **Extension devices:** 6 registered (all "Chrome on MacIntel"), last seen April 2026
- **Recommended target:** Extension (preferExtensionByDefault: true)

To upgrade: rtrvr.ai → Dashboard → Pricing

## Chrome Extension Status

**NOT discontinued.** The extension is alive and well on the Chrome Web Store:
- Name: "Retriever: AI Web Agent"
- 10,000+ users, 3.9 stars (57 ratings), Featured badge
- Follows Chrome Web Store recommended practices
- Publisher: rtrvr.ai (good standing, no violations)
- Category: Workflow & Planning

The 6 registered devices haven't been online since April 2026. To reconnect:
1. Install the extension from Chrome Web Store
2. Sign in with your rtrvr account
3. The device will appear in `rtrvr devices list`

No open-source alternative for the extension exists — the extension is proprietary (only the CLI/SDK is Apache 2.0). The `rover-preview-helper` repo is for developers testing Rover Embed, not a user-facing extension.

## Built-in Skill Templates

4 templates shipped with the CLI:

| Template | Target | Tools | Use |
|----------|--------|-------|-----|
| `agent-web` | auto | planner, act_on_tab, extract_from_tab, crawl | General web agent |
| `extension-session` | extension | planner, act_on_tab, extract | Authenticated workflows |
| `bulk-scrape` | auto | cloud_scrape, scrape, extract, crawl | Multi-URL batch jobs |
| `agent-api-first` | cloud | cloud_agent | Deterministic API execution |

## Pricing

| Tier | Price/mo | Credits | Best For |
|------|----------|---------|----------|
| Free | $0 | 250 | Trying it out (~50 tasks) |
| Basic | $9.99 | 1,000 | Individual automation |
| **Pro** | **$29.99** | **4,000** | **Cloud API + scaling** |
| Enterprise | $99.99 | 12,500 | Rover Embed + private mode |
| Scale | $499.99 | 60,000 | Business automation |

BYOK: Bring your own Gemini API key from ai.studio for free usage with extension.

Credit consumption: ~0.1-5 credits per action depending on model (Gemini Flash Lite → Pro).

## Use Cases & Patterns

### 1. Web Scraping at Scale
```bash
# Single page
rtrvr scrape --url https://example.com --json | jq '.result'

# Batch URLs
for url in $(cat urls.txt); do
  rtrvr scrape --url "$url" --json >> results.jsonl
done

# Structured extraction
rtrvr raw extract --param user_input="product name, price, rating" --param tab_urls='["https://shop.com"]'
```

### 2. Lead Enrichment
```bash
rtrvr run "Visit this company website and extract CEO name, employee count, and funding info" \
  --url https://company.com --cloud --json
```

### 3. E-commerce Monitoring
```bash
rtrvr run "Check if this product is in stock and note the current price" \
  --url https://store.com/product --cloud --json
```

### 4. Form Automation
```bash
rtrvr run "Fill out the contact form with: name=John, email=john@test.com, message=Hello" \
  --url https://example.com/contact --extension
```

### 5. Multi-Page Crawl
```bash
rtrvr raw crawl \
  --param user_input="extract all blog post titles and dates" \
  --param tab_urls='["https://blog.com"]' \
  --param max_pages=20
```

### 6. Scheduled Monitoring (Hermes Cron)
```bash
# In a cron job
rtrvr scrape --url https://competitor.com/pricing --cloud --json > /tmp/pricing.json
# Parse and alert on changes
```

### 7. MCP-Agent Integration
```
# From any MCP client, call rtrvr tools directly:
- cloud_agent: "Monitor this page for changes every hour"
- extract_from_tab: "Get all job listings from this page"
- crawl_and_extract_from_tab: "Get contact info from all about pages"
```

## Pitfalls & Warnings

1. **SDK DEPRECATED**: `@rtrvr-ai/sdk` and `@rtrvr-ai/core` are deprecated on npm. Do NOT install them. Only use `@rtrvr-ai/cli`.
2. **Auth required for most commands**: Even `mcp init` and `mcp url` require auth. Run `rtrvr auth login` first.
3. **Cloud mode has no user cookies by default**: Use `--extension` for authenticated sites, or set up cookie sync.
4. **Credit costs vary by model**: Gemini Pro costs 1-5 credits per action vs Flash Lite at 0.1-0.5.
5. **Streaming is on by default**: Use `--no-stream` for scripted use. Use `--json` for machine-readable output.
6. **Extension must be online**: Auto mode silently falls back to cloud if no extension devices are online.
7. **Small project**: 13 GitHub stars, 4 forks as of June 2026. Active but young. Expect API changes.
8. **npm deprecation**: The deprecation of SDK/core packages suggests they may be moving to a different distribution model or the SDK is being restructured.

## Troubleshooting

```bash
# Full diagnostics
rtrvr doctor

# Check auth
rtrvr auth status

# Check capabilities
rtrvr capabilities

# View config
rtrvr config get

# MCP endpoint health
curl https://mcp.rtrvr.ai/health

# Cloud API health
curl https://api.rtrvr.ai/health
```

## Integration with Hermes

### Pattern 1: CLI via Terminal
Use `terminal()` to call `rtrvr` commands directly.

### Pattern 2: REST API via curl
Use `curl` with the API key for programmatic calls.

### Pattern 3: Native MCP (Recommended)
Configure in `config.yaml` and use all 8 MCP tools directly.

### Pattern 4: A2W Universal Endpoint
Use `https://agent.rtrvr.ai/v1/a2w/runs` for no-auth-needed routing when the site has Rover installed.
