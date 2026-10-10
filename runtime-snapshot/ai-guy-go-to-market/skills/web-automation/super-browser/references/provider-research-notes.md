# Provider Research Notes — Super Browser Stack

**Date:** June 2026
**Source:** Subagent research via browser navigation, docs scraping, and GitHub review

## Browser Use (Open-Source + Cloud)

### Architecture (Deep)
- **Open-source** (`browser-use` pip, MIT): Uses custom `cdp_use` library — direct CDP WebSocket connections to Chromium. Event-driven `SessionManager` tracks all targets (pages, iframes, workers) via `Target.attachedToTarget` events. NOT Playwright-based.
- **Cloud** (`browser-use-sdk` v3): Hardened Chromium fork in managed sandboxes. CDP WebSocket exposed at `wss://connect.browser-use.com`. Playwright/Puppeteer/Selenium can connect to it.
- **v2 vs v3**: v3 is cloud-only premium agent. v2 is the open-source experience. Open-source is equivalent to the "Browser Harness" on cloud.

### Anti-Detection (Detailed)
- Canvas, WebGL, fonts, navigator — all randomized per session
- Passes CreepJS, BrowserLeaks fingerprint detectors
- Cloudflare / PerimeterX auto-bypass
- Ad/cookie banner auto-dismissal
- Residential proxies enabled by default (195+ countries)

### LLM Support
- OpenAI, Anthropic, Google, Groq, Mistral, Azure, OCI, Ollama (local), Vercel AI SDK
- Browser Use's own custom LLM: $0.60 input / $3.50 output per 1M tokens
- BYOK: connect your own Anthropic/OpenAI/Google keys, pay provider + 0.2x orchestration

### Key Limitations
- Custom proxy requires enterprise plan (can't use Decodo)
- Session timeout: 15 min inactivity, max 4 hours
- Recording URLs expire in 1 hour
- v3 agent is cloud-only, closed-source
- Profile state only saved on clean `sessions.stop()` — timeouts lose changes

---

## Airtop

### Platform Model
- Cloud-only SaaS. No self-hosted option.
- No-code conversational agent builder
- Target: GTM teams (sales, marketing, lead gen)
- Competes with 11x, AiSDR, Clay, Copy.ai — not with Browser Use directly

### Architecture
- Real Chromium-based browsers in cloud (NOT headless)
- Each agent session runs in its own isolated, encrypted environment
- Agent Builder (conversational UI) → deployed agents → cloud browser infrastructure

### API Surface
- REST only: `https://api.airtop.ai/api/`
- Bearer token auth (API keys from portal)
- Webhook trigger: `POST /hooks/agents/{id}/webhooks/{wid}`
- Result retrieval: `GET /invocations/{id}`
- No WebSocket, no streaming, no session control APIs
- No native SDKs (Python, JS, etc.) — REST only
- Make.com, n8n, Zapier native integrations

### Pricing (Credit-Based)
- Free: 1,000 credits/mo + 10,000 one-time bonus
- Starter: $26/mo (30K-150K)
- Professional: $170/mo (225K-500K)
- Enterprise: $502/mo (775K-1.5M)
- Credits roll over up to 2x monthly limit
- Custom proxy on Professional+

### Key Limitations
- Cloud-only, no self-hosted
- Credit unpredictability for complex agents
- No native SDKs — REST only
- Anti-detection is a black box — users can't customize
- Limited programmable control — natural language, not code
- Vendor lock-in: agents, profiles, credentials all in Airtop's platform
- Very new: blog posts from Jan-Jun 2026

---

## Anchor Browser

### What It Is
- Cloud browser automation platform for AI agents
- "Secure Infrastructure for Computer Use Agents"
- Custom Anchor Chromium fork
- Deterministic-first approach: AI plans, deterministic runs, AI only when needed

### Anti-Detection Claims
- Web-Bot-Auth Verified — officially verified by bot protection mechanisms
- Cloudflare "Signed Agents" program partner
- Partnered with Fingerprint.com for authorized AI agent identity
- Partnered with 1Password for agentic browser credentialing

### Why We Skipped It
- **No public pricing** — pricing page returns 404
- Sales-led model — "Talk to an Expert"
- Raised $6M seed (Blumberg Capital, Gradient Ventures)
- Opaque enterprise procurement
- Browser Use Cloud does the same thing at known $29/mo
- 80X fewer tokens, 12X faster claims are self-benchmarked and unverifiable

---

## Orgo Machines

### What It Is
- Cloud Linux VMs for AI agents ("Computers for Agents")
- Full desktop environments: apps + browser + terminal + files
- Sub-500ms cold boot (primary technical moat)
- Firecracker micro-VMs for isolation

### Architecture
- Docker-based templates (pre-built + custom)
- Xfce/Fluxbox desktop with xdotool for input
- Python + TypeScript SDKs
- WebSocket for terminal, audio, desktop events
- File transfer between VMs and host

### Pricing (Annual)
- Hacker: $29/mo — 5 VMs, 1 vCPU, 4GB RAM, 20GB disk, $10 AI credits
- Team: $112/mo — 20 VMs, 2 vCPU, 8GB RAM, 30GB disk, $50 AI credits
- Scale: $224/mo — 50 VMs, 4 vCPU, 16GB RAM, 50GB disk, $100 AI credits

### Why We Added It
- Fills the gap when browser automation hits a wall
- Desktop apps, multi-window, file processing, local dev
- Browser Use Cloud can't install apps or run multi-window workflows
- Open-source clone available (`github.com/Julianb233/orgo-clone`)

### Key Limitations
- Not a browser automation tool — you bring your own Playwright/Puppeteer
- No built-in stealth — standard Linux VMs, no anti-detection
- GPU not yet available (roadmap)
- Proprietary SaaS (use clone for self-hosting)
- Founder: Spencer (spencer@orgo.ai), San Francisco

---

## Rtrvr

### Already Documented
Full skill at `web-automation/rtrvr`. Key notes for this stack:

### Credit Cost Analysis
- Every cloud operation consumes credits
- 80% of cost is proxy credits (residential proxy layer)
- `rtrvr scrape`: 5 credits (~$0.035)
- `rtrvr run` (agent): 5+ per step (~$0.035+ per step)
- Extension mode BYOK Gemini = free (uses your own key)

### Chrome Extension Status
- NOT discontinued — 10,000+ users, 3.9 stars
- "Retriever: AI Web Agent" on Chrome Web Store
- 6 registered devices, last seen April 2026
- Extension preserves login state for authenticated sessions

---

## Decodo Proxies

### Configuration
- Host: `us.decodo.com`
- Ports: 10001-10007 (round-robin for IP rotation)
- Auth: `spo2nwl1tw:***`
- Type: Residential, sticky 10-minute sessions
- Cost: $2/GB

### Where It Works
- ✅ Raw API calls (curl, requests) through residential IPs
- ✅ Playwright-based scraping on non-aggressively-protected sites
- ✅ Cost optimization vs Browser Use Cloud's $5/GB
- ✅ Geo-targeting with country-specific exit nodes

### Where It Doesn't
- ❌ Facebook/Meta — headless detection blocks it regardless of proxy
- ❌ Cloudflare-protected sites — browser fingerprint gives you away
- ❌ PerimeterX — detects headless Chromium fingerprints
- ❌ Any site with advanced browser fingerprinting
