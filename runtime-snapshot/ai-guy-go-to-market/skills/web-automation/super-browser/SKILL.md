---
name: super-browser
version: "2.0"
description: Five-tier browser and desktop automation stack — Browser Use Cloud (anti-detection), Hyperbrowser (scale), Airtop (no-code), Rtrvr (MCP), Orgo Machines (full desktop VMs), Decodo (raw proxies). Strategic routing by task type and protection level.
---

# Super Browser — Multi-Layer Automation Stack

Five-tier automation architecture. From quick single-page extraction to full desktop VM control, with Decodo residential proxies as the raw proxy backbone.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   SUPER BROWSER STACK                    │
├─────────────┬─────────────┬──────────┬────────┬─────────┤
│  TIER 1     │  TIER 2     │ TIER 3   │ TIER 4 │ TIER 5  │
│  Browser    │  Hyper-     │ Airtop   │ Rtrvr  │ Orgo    │
│  Use Cloud  │  browser    │          │        │ Machines│
├─────────────┼─────────────┼──────────┼────────┼─────────┤
│ Anti-detect │ Scale       │ No-code  │ MCP    │ Full    │
│ Hardened    │ Headless    │ SaaS     │ Auth   │ Desktop │
│ Chromium    │ Sessions    │ Backup   │ Sessions│ VMs     │
├─────────────┼─────────────┼──────────┼────────┼─────────┤
│ $29/mo      │ Usage-based │ $26/mo   │ BYOK   │ $29/mo  │
└─────────────┴─────────────┴──────────┴────────┴─────────┘
                      │
              ┌───────┴───────┐
              │    DECODO     │
              │  Raw Proxies  │
              │   $2/GB       │
              └───────────────┘
```

## Quick Decision Matrix

| Site Type | Primary | Fallback | Cost |
|-----------|---------|----------|------|
| **Google Maps local business scraping** | Built-in browser (browser_navigate + snapshot) | Browser Use Cloud | $0 (built-in) / $0.02/hr (cloud) |
| **Meta/Facebook** | Browser Use Cloud | Hyperbrowser | $0.02/hr + $5/GB proxy |
| **LinkedIn** | Browser Use Cloud | Rtrvr Extension | $0.02/hr + $5/GB proxy |
| **Anti-bot protected (Cloudflare, PerimeterX)** | Browser Use Cloud | Airtop | $0.02/hr + $5/GB proxy |
| **JS-heavy SPAs** | Browser Use Cloud | Hyperbrowser | $0.02/hr + $5/GB proxy |
| **Quick single-page** | Hyperbrowser | Rtrvr scrape | Free tier |
| **Authenticated sites (OAuth, cookies)** | Browser Use Cloud Profiles | Rtrvr Extension | $29/mo |
| **Scheduled GTM workflows** | Airtop | Browser Use Cloud cron | $26/mo |
| **Raw API calls (JSON endpoints)** | curl + Decodo proxy | requests + Decodo | $2/GB |
| **Local development/testing** | Browser Use open-source | Playwright + stealth | Free (bring LLM keys) |

| **Full desktop automation** | Orgo Machines | Manual fallback | $29/mo (5 VMs) |
| **When browser isn't enough** | Orgo Machines | Manual intervention | $29/mo |

## Tier 1: Browser Use Cloud (PRIMARY WORKHORSE)

### Why It's #1

Browser Use Cloud runs a **hardened, forked Chromium** with anti-detect fingerprinting that passes CreepJS and BrowserLeaks. Canvas, WebGL, fonts, and navigator properties are randomized per session. It auto-bypasses Cloudflare, PerimeterX, and most anti-bot challenges. This is the only tool that consistently worked against Meta Ad Library in our testing.

Built-in **US residential proxies** (195+ countries available) — no separate proxy service needed for most use cases. Ad and cookie banner auto-dismissal included.

### Pricing

- **Dev plan: $29/mo** ($29 credits)
- Browser: $0.02/hr
- Proxy bandwidth: $5/GB
- LLM tokens: 1.2x provider rates (Claude Sonnet 4.6 at $3.60/$18.00 per 1M)
- Free tier: 10 tasks/mo, 3 concurrent sessions

### Python SDK (v3) — Primary Integration

```python
from browser_use_sdk.v3 import BrowserUse, BuModel, ProxyCountryCode

# Initialize (reads BROWSER_USE_API_KEY from env)
client = BrowserUse()

# Create a persistent profile (saves cookies/localStorage across sessions)
profile = client.profiles.create(name="my-profile")

# Create a session with the profile
session = client.sessions.create(
    model=BuModel.claude_sonnet_4_6,
    proxy_country_code=ProxyCountryCode.us,
    keep_alive=True,
    profile_id=str(profile.id),
)

# Run a task
result = client.run(
    session_id=str(session.id),
    task="Go to facebook.com/ads/library, search for 'bath remodel'...",
    max_steps=20,
)
print(result.status, result.output)

# Run with structured output (Pydantic model)
from pydantic import BaseModel

class Advertiser(BaseModel):
    name: str
    page_url: str
    ad_count: int

result = client.run(
    session_id=str(session.id),
    task="Extract all advertisers and their ad counts",
    output_schema=Advertiser,  # Returns typed list[Advertiser]
)

# Stop session when done (profile persists for reuse)
client.sessions.stop(session_id=str(session.id))
```

### CDP WebSocket (Direct Browser Control)

Connect Playwright/Puppeteer/Selenium directly to Browser Use's cloud browsers:

```python
from playwright.async_api import async_playwright

# Get CDP URL from Browser Use
browser = client.browsers.create(
    proxy_country_code=ProxyCountryCode.US,
    keep_alive=True,
)
cdp_url = browser.cdp_url  # wss://connect.browser-use.com?apiKey=...&sessionId=...

# Connect Playwright
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(cdp_url)
    page = browser.contexts[0].pages[0]
    await page.goto("https://facebook.com/ads/library")
    # ... full Playwright control ...
```

### MCP Server (AI Agent Integration)

Add to Hermes `config.yaml`:

```yaml
mcp_servers:
  browser-use:
    type: http
    url: https://api.browser-use.com/v3/mcp
    headers:
      Authorization: "Bearer bu_live_YOUR_API_KEY"
```

### CLI

```bash
# Install
uvx browser-use install

# Interactive
browser-use open https://example.com
browser-use state
browser-use click "Login"
browser-use type "username" "hello@example.com"
browser-use screenshot page.png
```

### Key Features

- **Profiles**: Persistent cookies/localStorage across sessions
- **2FA handling**: Agent Mail (auto-enabled inbox), TOTP via pyotp, human-in-the-loop
- **Recording**: MP4 video recording of sessions
- **Live preview**: `live_url` for real-time observation
- **Structured output**: Pydantic/Zod schemas
- **Deterministic rerun**: Cache workflows, ~99% cheaper re-runs
- **Workspaces**: Upload/download files for agent use
- **Streaming**: `for await` pattern for real-time agent messages

### Limitations

- Session timeout: 15 min inactivity, max 4 hours
- Recording URLs expire in 1 hour
- Custom proxy requires **enterprise plan** (above Scaleup) — can't use Decodo directly
- v3 agent is cloud-only, not in open-source
- $5/GB proxy bandwidth can add up for data-heavy scraping

---

## Tier 2: Hyperbrowser (SCALE & SPEED)

### Why It's #2

Hyperbrowser provides usage-based headless browser sessions with fast startup and scalable parallel execution. Best for bulk extraction tasks that don't need anti-detection hardening.

- **Usage-based pricing** — pay per session, no monthly minimum
- **Fast session startup** — optimized for parallel bulk work
- **Headless by default** — good for SPA scraping, PDF generation, screenshots
- **API key**: `HYPERBROWSER_API_KEY`

### When to Use

- Bulk scraping of unprotected or moderately-protected sites
- Quick single-page extraction at scale
- Parallel data collection (multiple sessions concurrently)
- Sites where anti-detection isn't the primary concern

### When NOT to Use

- Meta/Facebook, LinkedIn, Cloudflare-protected sites → use Browser Use Cloud (Tier 1)
- Authenticated OAuth flows → use Browser Use Cloud Profiles + `keep_alive=True`

### Docs

https://www.hyperbrowser.ai/docs/home

---

## Tier 3: Airtop (NO-CODE BACKUP)

### When to Use

Browser Use Cloud is the primary tool, but Airtop fills gaps:
- **Non-developer workflows** — marketing/sales can build agents without code
- **Pre-built templates** — faster than coding from scratch for common GTM patterns
- **Scheduled monitoring** — built-in scheduling vs coding cron + Browser Use
- **SOC2/HIPAA compliance** — enterprise requirements Browser Use doesn't meet

### Setup

- Sign up at airtop.ai
- Starter plan: $26/mo (30K-150K credits)
- API key from portal.airtop.ai/api-keys
- Base URL: `https://api.airtop.ai/api/`

### REST API

```bash
# Trigger an agent
curl -X POST "https://api.airtop.ai/api/hooks/agents/{agentId}/webhooks/{webhookId}" \
  -H "Authorization: Bearer at_..." \
  -H "Content-Type: application/json" \
  -d '{"configVars": {"url": "https://target.com"}}'

# Get results
curl "https://api.airtop.ai/api/invocations/{invocationId}" \
  -H "Authorization: Bearer at_..."
```

### Proxy Support

- Built-in residential proxy (Starter+)
- Custom proxy (Professional+): Oxylabs, Smartproxy, IPRoyal supported
- Decodo could work as custom proxy on Professional plan ($170/mo)

---

## Tier 4: Rtrvr (MCP + AUTH SESSIONS)

Already documented in `rtrvr` skill. Key use cases in this stack:

- **Authenticated sessions**: Chrome Extension preserves login state
- **MCP integration**: 8 MCP tools available to any MCP client
- **BYOK (Gemini)**: Free usage with your own Gemini API key

### When to Prefer Rtrvr Over Browser Use Cloud

- Task requires logged-in session to a service you already have auth for
- Need MCP-native tool calling (not wrapping a REST API)
- Cost-sensitive: BYOK Gemini = free, vs Browser Use Cloud at $0.02/hr + LLM costs

---

---

## Tier 5: Orgo Machines (FULL DESKTOP VMs)

### Why It Exists in This Stack

Sometimes browser automation isn't enough. You need a real computer — a full Linux desktop with applications, file systems, terminals, and multi-window workflows. Orgo provides sub-500ms boot cloud VMs that AI agents can fully control. When Browser Use Cloud or Hyperbrowser can't handle a task because it requires:

- Desktop applications (not web apps)
- Multi-window workflows
- File system operations + browser simultaneously
- Local development environments
- GPU-accelerated workloads
- Complex software that doesn't expose a web interface

### Pricing

| Plan | Price/mo | VMs | vCPU | RAM | Disk | AI Credits |
|------|----------|-----|------|-----|------|------------|
| **Hacker** | $29 | 5 | 1 | 4GB | 20GB | $10 |
| Team | $112 | 20 | 2 | 8GB | 30GB | $50 |
| Scale | $224 | 50 | 4 | 16GB | 50GB | $100 |

Annual billing: ~10% discount. All plans include AI credits for LLM usage.

### Python SDK

```python
from orgo import OrgoClient

client = OrgoClient(api_key="org_...")

# Create a VM
vm = client.vms.create(
    template="ubuntu-desktop",
    plan="hacker",
)

# Wait for boot (sub-500ms)
vm.wait_ready()

# Execute commands
result = vm.execute("ls -la /home/agent")
print(result.stdout)

# Run browser automation inside the VM
vm.execute("playwright test --headed")

# Take screenshot of the desktop
screenshot = vm.screenshot()
with open("desktop.png", "wb") as f:
    f.write(screenshot)

# Transfer files
vm.upload("script.py", "/home/agent/script.py")
vm.download("/home/agent/output.csv", "output.csv")

# Clean up
vm.terminate()
```

### WebSocket API (Real-time Control)

```python
import asyncio
import websockets

async with websockets.connect("wss://api.orgo.ai/v1/vms/{vm_id}/ws") as ws:
    # Send mouse click
    await ws.send(json.dumps({"type": "click", "x": 500, "y": 300}))

    # Type text
    await ws.send(json.dumps({"type": "type", "text": "hello world"}))

    # Receive desktop stream
    async for msg in ws:
        frame = json.loads(msg)
        # frame["screenshot"] = base64 PNG
```

### Key Features

- **Sub-500ms cold boot** — fastest in the industry, instant agent dispatch
- **Full Linux desktop** — Xfce/Fluxbox with xdotool for mouse/keyboard control
- **Firecracker micro-VMs** — hardware-level isolation, secure by default
- **Double encryption at rest** — rotating credentials per session
- **File transfer** — upload/download between host and VM
- **Template system** — pre-built Docker images, custom templates
- **GPU roadmap** — NVIDIA MIG partitioning on A100, whole-GPU A10/L40s
- **Multi-model**: Claude Computer Use, OpenAI CUA, OpenClaw, LangChain

### When to Use Orgo Over Browsers

```
Browser Use Cloud can't do these. Orgo can:

• Install and run desktop software → browsers can't install apps
• Multi-window workflows → browsers are single-window
• Local file processing → browsers are sandboxed
• GPU compute → browsers have no GPU access
• Full terminal access → browsers have no shell
• Run Playwright/Selenium locally → full control, no CDP limits
```

### Open-Source Alternative

There is an open-source clone at `github.com/Julianb233/orgo-clone`:
- Fastify/PostgreSQL/Drizzle/Dockerode/BullMQ
- Xvfb/Fluxbox/x11vnc/xdotool for headless desktop
- Self-hosted with your own Docker infrastructure
- 85 commits, active development

### Limitations

- **Cost per VM** — $29/mo for 5 VMs means ~$5.80/VM, but only 5 concurrent
- **Not a browser tool** — you bring your own browser automation (Playwright, Puppeteer)
- **No built-in stealth** — VMs use standard Linux, no anti-detection out of the box
- **GPU not yet available** — roadmap, not production
- **Proprietary** — closed-source SaaS (use the clone for self-hosting)

---

## Decodo Proxy Integration

### Where Decodo Fits

Browser Use Cloud has built-in residential proxies, so Decodo is NOT needed for primary browser automation. Decodo's role in this stack:

1. **Raw HTTP scraping**: curl/requests through residential IPs for API endpoints
2. **Cost optimization**: $2/GB vs Browser Use Cloud's $5/GB for high-volume data extraction
3. **Playwright fallback**: When you need full control of the browser stack
4. **Geo-targeting that Browser Use doesn't support**

### Decodo Proxy Details

```
Proxy: http://spo2nwl1tw:***@us.decodo.com:10001
Ports: 10001-10007 (round-robin for IP rotation)
Type: Residential, sticky 10-minute sessions
Cost: $2/GB
```

### Usage Patterns

#### Pattern 1: curl + Decodo

```bash
curl -x "http://spo2nwl1tw:***@us.decodo.com:10001" \
  "https://api.target.com/data" \
  -H "User-Agent: Mozilla/5.0 ..."
```

#### Pattern 2: Python requests + Decodo

```python
import requests

proxies = {
    "http": "http://spo2nwl1tw:***@us.decodo.com:10001",
    "https": "http://spo2nwl1tw:***@us.decodo.com:10001",
}
resp = requests.get("https://api.target.com/data", proxies=proxies)
```

#### Pattern 3: Playwright + Decodo + Stealth

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(
        headless=True,
        proxy={
            "server": "http://us.decodo.com:10001",
            "username": "spo2nwl1tw",
            "password": "***",
        }
    )
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
        viewport={"width": 1920, "height": 1080},
    )
    page = await context.new_page()
    await page.goto("https://target.com")
```

**Warning**: Playwright + Decodo + playwright-stealth was tested against Facebook Ad Library and **failed** — Facebook's headless detection still blocks it. Use Browser Use Cloud for Meta.

#### Pattern 4: Browser Use open-source + Decodo

The open-source `browser-use` library has **no built-in stealth**. To use Decodo with it:

```python
from browser_use.agent.service import Agent
from browser_use import Browser

# Use cloud mode for built-in stealth + proxies
browser = Browser(
    use_cloud=True,                    # Cloud = hardened Chromium + stealth
    cloud_proxy_country_code="us",     # US residential proxy
    headless=False,                    # Non-headless reduces detection further
)

# Or for local open-source (no stealth):
browser = Browser(
    headless=False,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
)

agent = Agent(
    task="Extract data from...",
    llm="anthropic/claude-sonnet-4-6",
    browser=browser,
)
result = await agent.run()
```

**Warning**: This will NOT bypass advanced anti-bot detection (Cloudflare, Facebook). For those, use Browser Use Cloud.

---

## Strategic Routing Algorithm

When Hermes needs to browse the web, route based on these checks:

```
1. Does the task require a full desktop OS? (install apps, multi-window, GPU, file system)
   → YES: Orgo Machines (Tier 5)
   → NO: Go to 2

2. Is the site known to block bots? (Meta, LinkedIn, Cloudflare-protected, Google Maps data extraction)
   → YES: Browser Use Cloud (Tier 1). For Google Maps specifically, the built-in Hermes browser (browser_navigate + browser_snapshot) also works — but Browser Use Cloud enables parallel sessions for scale.
   → NO: Go to 3

3. Is Google OAuth or authenticated session needed?
   → YES: Browser Use Cloud with profile_id and keep_alive=True (Tier 1)
   → NO: Go to 4

4. Is it a quick single-page extraction or bulk scraping?
   → YES: Hyperbrowser (Tier 2)
   → NO: Go to 5

5. Does the task need logged-in session with existing auth (non-OAuth)?
   → YES: Rtrvr Extension (Tier 4)
   → NO: Go to 6

6. Is this a recurring scheduled workflow for GTM/sales?
   → YES: Airtop (Tier 3)
   → NO: Go to 7

7. Is it a raw API/JSON endpoint?
   → YES: curl + Decodo
   → NO: Hyperbrowser (Tier 2) as default
```

---

## Installation Status

| Tool | Installed | Version | Notes |
|------|-----------|---------|-------|
| `browser-use` | ✅ | 0.12.9 | Python package |
| `browser-use-sdk` | ✅ | 3.8.4 | v3 cloud SDK — `bu_HqLadi8g...` configured via env var |
| `playwright` (chromium) | ✅ | 1.60.0 | `~/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome` — executable path must be explicit in code. Hermes venv (`/opt/hermes/.venv`) does NOT have playwright; use system python (`/usr/bin/python3`). |
| `rtrvr` CLI | ✅ | 0.2.1 | Global npm, 1,490 credits |
| `super-browser` CLI | ✅ | 0.3.1 | `~/.local/bin/super-browser`, venv at `~/./super-browser/` |
| `super-browser` MCP | ✅ | 0.3.1 | Registered in `config.yaml` w/ all provider keys |
| Decodo proxy | ✅ | N/A | `us.decodo.com:10001-10007` |
| Browser Use API key | ✅ | — | `BROWSER_USE_API_KEY` set, $17.16 credits remaining |
| Airtop API key | ✅ | — | Configured |
| Hyperbrowser API key | ⚠️ | — | Configured but needs `HYPERBROWSER_API_KEY` env var |
| Steel API key | ✅ | — | Configured |
| Orgo Machines | ⚠️ | — | Has API key, needs `ORGO_COMPUTER_ID` |
| Rtrvr API key | ❌ | — | Needs `RTRVR_API_KEY` |
| Browserless | ❌ | — | Needs `BROWSERLESS_TOKEN` |
---

## Account Setup Needed

### Browser Use Cloud ($29/mo Dev plan recommended)

1. Sign up at https://browser-use.com
2. Get API key from dashboard
3. Set env: `export BROWSER_USE_API_KEY=bu_live_...`
4. Test: `python3 -c "from browser_use_sdk.v3 import BrowserUse; c = BrowserUse(); print(c.billing.account())"`

### Airtop (optional, $26/mo Starter)

1. Sign up at https://airtop.ai
2. API key from https://portal.airtop.ai/api-keys
3. Build first agent via conversational UI or API

---

## Cost Comparison (Scraping 1,000 Pages)

| Tool | Browser Cost | Proxy Cost | LLM Cost | **Total** |
|------|-------------|------------|----------|-----------|
| Browser Use Cloud | $2.00 (100h) | $50 (10GB) | ~$5 | **~$57** |
| Hyperbrowser | Usage-based | Included | $0 | **Varies** |
| Airtop | — | Included | Included | **~$26/mo** (credit-based) |
| Playwright + Decodo | Free | $20 (10GB) | $0 | **$20** (but blocked on protected sites) |
| Rtrvr | Free tier | Included | BYOK (Gemini free) | **$0** (250 credits) |
| Orgo Machines | $29/mo flat | N/A | $0 (manual control) | **$29/mo** (5 VMs) |

**Verdict**: For protected sites (Meta, LinkedIn, Google OAuth), Browser Use Cloud with profiles is the only option that works reliably. For bulk unprotected scraping, Hyperbrowser with usage-based pricing. When browser automation hits a wall, Orgo Machines at $29/mo gives you a real computer.

---

## Known Anti-Detection Results

| Protection | Browser Use Cloud | Hermes Built-in Browser | Hyperbrowser | Playwright + Decodo | Rtrvr | Airtop |
|------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Google Maps data | ✅ Should pass | ✅ Works (5 results/view) | ⚠️ Unknown | ❌ Blocked (empty DOM) | Untested | Untested |
| Cloudflare | ✅ Pass | ❌ Blocked (most sites) | ⚠️ Moderate | ❌ Blocked | ⚠️ Partial | ✅ Pass |
| Meta Ad Library | ✅ Should pass | ⚠️ Moderate | ❌ Blocked | Untested | Untested |
| PerimeterX | ✅ Pass | ❌ Blocked | ❌ Blocked | Untested | ✅ Claimed |
| Google OAuth | ✅ Pass (profiles) | ❌ No profile persistence | ❌ 2FA breaks flow | Untested | Untested |
| Generic bot detection | ✅ Pass | ✅ Pass | ⚠️ With stealth | ✅ Pass | ✅ Pass |
| CreepJS fingerprint | ✅ Pass | ✅ Pass | ❌ Fail | Untested | Untested |

---

## Integration with Hermes Cron

### Daily scraping job (Browser Use Cloud)

```python
# cron-script: scrape_protected_site.py
from browser_use_sdk.v3 import BrowserUse, BuModel, ProxyCountryCode

client = BrowserUse()
session = client.sessions.create(
    model=BuModel.claude_sonnet_4_6,
    proxy_country_code=ProxyCountryCode.us,
)

result = client.run(
    session_id=str(session.id),
    task="Go to {url}, extract {what}, return JSON",
)

client.sessions.stop(session_id=str(session.id))
print(result.output)  # stdout → captured by cron
```

Register with:
```bash
hermes cron create --name "daily-meta-scrape" \
  --schedule "0 6 * * *" \
  --script "scripts/scrape_protected_site.py" \
  --toolsets "terminal" \
  --deliver "slack"
```

---

## Pitfalls & Gotchas

1. **Google OAuth triggers fresh 2FA per browser context** — Google requires device verification for every new browser fingerprint, even with correct credentials. **Definitive finding (Jun 11): 9+ consecutive poll attempts showed the 2FA page NEVER advances after user approval on cloud browsers.** The device prompt approval does not propagate to cloud browser instances. **Workaround: Always use email/password login instead of Google OAuth when available.** Browser Use Cloud profiles persist cookies inside a session, but a new session = new fingerprint = new 2FA challenge. If email/password is not available, create a `keep_alive=True` session ONCE with user present for 2FA approval, then reuse that session_id. When the session eventually times out (max 4 hours), you'll need user interaction again.
2. **Browser Use Cloud returns 502 Bad Gateway on session expiry** — When a session times out (15 min inactivity) or crashes, subsequent `client.run()` calls may return 502. Catch `BrowserUseError`, check if the session still exists with `client.sessions.get()`, and create a new session if needed.
3. **Browser Use Cloud custom proxy requires enterprise plan** — can't use Decodo directly with Browser Use Cloud. Use Decodo for raw HTTP/Playwright fallback.
4. **Session state lost on timeout** — 15 min inactivity kills the session. Use `keep_alive=True` and poll actively.
5. **$5/GB proxy bandwidth** is Browser Use Cloud's biggest hidden cost. For data-heavy extraction, consider extracting only what you need.
6. **`ProxyCountryCode.us` (lowercase)** — The SDK enum uses lowercase country codes. `ProxyCountryCode.US` is an AttributeError. Also `client.billing.account()` not `client.account.get()`.
7. **Rtrvr credit costs are 80% proxy** — residential proxy overhead makes it $0.035/page. Only use for JS-heavy SPAs.
8. **Orgo Machines are infrastructure, not automation** — you get a cloud VM, not a browser agent. You bring your own Playwright/Puppeteer/Selenium.
9. **Orgo has no built-in stealth** — standard Linux VMs are detectable.
10. **Decodo residential proxies trigger anti-bot on major platforms** — Google APIs return 429, Amazon returns empty results, Goodreads is intermittent. For public APIs, use direct HTTP without proxy. For protected sites, use Browser Use Cloud (Tier 1).
11. **Decodo $2/GB is for raw HTTP that doesn't need stealth** — best for: PRLog RSS, Craigslist, public government databases. Not for: Google, Amazon, Meta, LinkedIn.
13. **Google Maps "limited view" caps results at 5-8 per search** — without Google sign-in, Maps only shows 5-8 sidebar results. To get phone numbers and websites, click into each listing's detail panel (displays full address, phone button, website link). For volume (1,000+ leads), plan 150-200 category×location combos. Browser Use Cloud parallel sessions are the fastest path.
14. **Google Maps blocks Playwright headless** — returns empty DOM even with anti-detection flags (`--disable-blink-features=AutomationControlled`, custom UA). Non-headless fails on headless VPS (no X server). Only the built-in Hermes browser (`browser_navigate`) or Browser Use Cloud reliably loads Google Maps.

---

## Reference Files

- `references/facebook-headless-detection.md` — Root cause analysis: why Playwright + Decodo fails against Facebook's headless detection.
- `references/provider-research-notes.md` — Condensed subagent research findings: Browser Use architecture deep-dive, Airtop pricing/API details, Orgo Machines capabilities, Rtrvr credit analysis, Decodo proxy patterns.
- `references/browser-use-sdk-v3-api.md` — Live-verified v3 SDK API (Jun 2026): correct method signatures, enums (lowercase `ProxyCountryCode.us`), error handling for 502, Google OAuth 2FA pattern.

---

## Related Skills

- `sales/meta-ad-library-scraping` — Meta Ad Library scraping with Browser Use Cloud (primary), Playwright fallback
- `sales/listkit` — ListKit B2B lead gen platform (Browser Use Cloud profiles for Google OAuth)
- `web-automation/rtrvr` — Rtrvr.ai MCP integration (Tier 4 in this stack)
- `sales/scrapecreators-cli` — Free Facebook Ad Library API (15-result cap)
