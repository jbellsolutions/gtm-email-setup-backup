---
name: python-service-deployment
description: "Deploy and run Python/FastAPI services on this VPS — pip paths, dependency installation, uvicorn startup, env sourcing, background process management. Also covers cron job diagnostics: error classification, credit exhaustion patterns, triage, and script verification."
category: devops
triggers:
  - Deploying any Python service on this VPS
  - Starting a FastAPI/uvicorn app in background
  - Installing Python dependencies in this environment
  - Adding a new LLM provider to an existing Python client
---

# Python Service Deployment (VPS)

Deploy and run Python services on the AI Integraterz VPS. This skill covers the environment quirks, dependency management, and startup patterns unique to this host.

## Environment Facts

| Fact | Value |
|------|-------|
| Python | `/usr/bin/python3` (3.13) |
| Pip | `/opt/data/home/.local/bin/pip` |
| System packages flag | `--break-system-packages` (required — no venv isolation) |
| Global .env | `/opt/data/.env` (source of truth for API keys) |
| Service .env | Place in backend/ directory, app reads from cwd |

**Key sourcing rule**: When a service's local `.env` has truncated or placeholder values, check `/opt/data/.env` for the full key. Never trust a value that ends in `...` or looks shortened.

## Dependency Installation

```bash
/opt/data/home/.local/bin/pip install --break-system-packages -r requirements.txt
```

All packages install system-wide. No virtualenv needed. The `--break-system-packages` flag is mandatory on Python 3.13+.

## Starting a FastAPI Service

Always use background mode for long-running services:

```bash
cd /path/to/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 2>&1
```

- Use `python3 -m uvicorn`, not bare `uvicorn` — avoids PATH issues
- Port 8000 is the convention
- Background with `terminal(background=true)` for non-blocking

## Health Check

```bash
curl -s http://localhost:8000/health
# Expected: {"status":"ok"}
```

If `/health` returns raw "OK" (text/plain), a Railway proxy is intercepting. Check the real app via other endpoints.

## Adding a New LLM Provider

When adding a new LLM provider (e.g. DeepSeek) to an existing Python client that already supports Anthropic and/or OpenAI:

### 1. Config — add the API key field
```python
deepseek_api_key: str = ""
```

### 2. Client class — accept the key and model
```python
def __init__(
    self,
    # ... existing params ...
    deepseek_api_key: str = "",
    deepseek_model: str = "deepseek-chat",
) -> None:
    self.deepseek_api_key = deepseek_api_key
    self.deepseek_model = deepseek_model
```

### 3. Priority chain in the call method
DeepSeek uses the standard Chat Completions API (not Anthropic's Messages API or OpenAI's Responses API):

```python
async def _call(self, system: str, user: str, max_tokens: int) -> str:
    if self.deepseek_api_key:
        return await self._call_deepseek(system, user, max_tokens)
    if self.openai_api_key:
        return await self._call_openai(system, user, max_tokens)
    # fall through to Anthropic...
```

DeepSeek goes first because it's cheapest/fastest. OpenAI second. Anthropic last as fallback.

### 4. DeepSeek implementation — uses httpx (already installed everywhere)
```python
async def _call_deepseek(self, system: str, user: str, max_tokens: int) -> str:
    import httpx
    payload = {
        "model": self.deepseek_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if choices and choices[0].get("message", {}).get("content"):
            return choices[0]["message"]["content"].strip()
        return ""
```

### 5. Wire in the DI container
```python
claude = ClaudeClient(
    settings.anthropic_api_key,
    openai_api_key=settings.openai_api_key,
    openai_model=settings.openai_model,
    deepseek_api_key=settings.deepseek_api_key,
)
```

## Restarting After .env Changes

The settings are cached with `@lru_cache`. After changing `.env`:
1. Kill the uvicorn process
2. Restart it — the cache clears on new process

## Pitfalls

- **Truncated API keys**: `.env` files sometimes contain display-truncated values like `apify_...o9ri`. Always check `/opt/data/.env` for the real key.
- **Bare `pip` not on PATH**: Always use the full path `/opt/data/home/.local/bin/pip`.
- **Missing `--break-system-packages`**: pip will refuse to install without this flag on modern Python.
- **sqlmodel import**: FastAPI apps using SQLModel need it installed separately — it's not always in requirements.txt.
- **Playwright browsers**: If the service uses Playwright, `playwright install` may be needed (but the job scraper runs headless and the browsers are pre-installed).
- **legacy email platform MCP stdio transport**: The `legacy email platform-mcp-server` binary does not exist on this VPS. The stdio transport will silently fail. Prefer Hermes' native legacy email platform MCP tools or implement a REST API fallback instead.

## Cron Job Management

Diagnose and manage cron jobs running on the Hermes agent. This section covers the diagnostic flow, common failure patterns, and triage procedures.

### Diagnostic Flow

1. **List all jobs:** `cronjob(action='list')` — look at schedule frequency, `last_status`, `deliver` target, `enabled` state
2. **Check error log:** `tail -100 /opt/data/logs/errors.log` — the canonical source of truth for cron failures. Check rotated logs too: `errors.log.1`, `errors.log.2`, `agent.log`, `agent.log.1`
3. **Classify the failure** (see below)
4. **Triage:** pause worst offenders with `cronjob(action='pause', job_id='...')`

### Common Root Causes (in order of likelihood)

**Provider credits exhausted (HTTP 402):**
- Two patterns: **soft limit** ("can only afford 2534 tokens" — some credits remain, large prompts fail) vs **hard limit** ("Insufficient credits" — complete exhaustion, everything fails)
- Every job fails because each cron run spawns its own agent session needing LLM access
- Early warning in `agent.log`: `credential pool: no available entries (all exhausted or empty)` appears before the hard 402
- Fix: add credits to the provider dashboard (e.g., openrouter.ai/settings/credits)
- Mitigation: pause high-frequency jobs first — they're hammering a dead account

**Missing environment variables:**
- Symptom: `KeyError` or `NoneType` in script output
- The cron session may not inherit shell env vars
- Fix: ensure API keys are in `~/.hermes/.env` or gateway process environment

**Script-level failure:**
- Symptom: error occurs even when running script manually
- Isolate: `python3 /path/to/script.py --once` from terminal to confirm
- If it works manually but not via cron, it's an env issue

### High-Frequency Jobs to Pause First

| Job ID | Name | Schedule | Impact |
|--------|------|----------|--------|
| `2929988f4269` | legacy email platform-auto-reply | Every minute | 1,440 calls/day wasted |
| `a643d0095232` | Vault Auto-Sync | Every 30 min | 48 calls/day |
| `752557ddcabf` | Ops Checklist | Every 4 hours | 6 calls/day |

### Post-Mortem: Verify Scripts Independently

After fixing the provider, verify scripts still work:
```bash
python3 /opt/data/scripts/<script>.py --once
bash /opt/data/obsidian-vault/scripts/vault-sync.sh
```

### Cron Pitfalls

- **Don't trust `last_status: ok`** — a job may have succeeded on its last run but the next will fail if credits ran out since then
- The legacy email platform-auto-reply job (`2929988f4269`) runs every minute — if credits are out, pause it immediately
- Session search often won't find recent cron run transcripts; rely on `/opt/data/logs/errors.log` instead
- Scripts in `/opt/data/scripts/` may depend on env vars (`legacy email platform_API_KEY`, `DEEPSEEK_API_KEY`) — always check `echo ${VAR_NAME}` before assuming they're set

See `references/cron-error-patterns.md` for full credit-exhaustion log patterns with examples.

## Railway Deployment Authentication Gate

For Railway deployments, verify authentication before touching the project or service:

```bash
npx @railway/cli whoami
npx @railway/cli project list
```

If the CLI reports `Unauthorized`, start device login with `npx @railway/cli login` in a PTY and give the user the exact current device URL and one-time code from that process. The URL is normally `https://railway.com/activate`, but the code is ephemeral and must be regenerated if it expires. Do not report deployment progress until `whoami` succeeds and the target project is confirmed.

## Railway Static Python Service Deployment

For a supplied ZIP that must be deployed exactly as-is to an existing Railway project:

1. Extract it to a deployment directory and link the exact project/environment:
   ```bash
   npx @railway/cli link --project <project-name-or-id> --environment production
   ```
2. Confirm the target environment has no unexpected services, then create exactly one empty service:
   ```bash
   npx @railway/cli add --service <service-name> --json
   ```
3. Upload the extracted directory with `--path-as-root`. Omitting this flag can archive the parent directory, causing Railpack to see only that directory and fail to detect Python:
   ```bash
   npx @railway/cli up /path/to/extracted --path-as-root \\
     --service <service-name> --environment production --detach --yes --json
   ```
4. Poll `npx @railway/cli deployment list --json` until the deployment is `SUCCESS`; inspect build logs with `npx @railway/cli logs <deployment-id> --build --lines 100 --json` if needed.
5. Generate the public domain:
   ```bash
   npx @railway/cli domain --service <service-name> --json
   ```
6. Verify every route using a no-redirect HTTP client: expected clean routes must be 200, legacy paths must be 301 with the exact `Location`, and requested third-party iframe URLs must be checked independently.
7. For immutable page bundles, compare SHA-256 and byte lengths of each deployed HTML response with the corresponding ZIP member. This proves the deployment did not alter the HTML.

The `--path-as-root` flag changes only the upload archive layout, not the application files. Report the actual deployment status and HTTP results, not merely the CLI upload response.

After deployment, verify the generated domain with HTTP checks for every required route and redirect, and verify embedded third-party URLs separately when requested.

## References

- `references/railway-static-deploy.md` — concise command sequence and verification checklist for exact-as-is Railway static Python deployments


- `references/cron-error-patterns.md` — Known cron error patterns: OpenRouter 402 soft/hard limits, log rotation locations, script verification procedures
