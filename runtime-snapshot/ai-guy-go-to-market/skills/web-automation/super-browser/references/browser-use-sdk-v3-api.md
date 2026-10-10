# Browser Use Cloud SDK v3 — Verified API (Jun 11, 2026)

API details verified against `browser-use-sdk` v3.8.4 with a live account.

## Client Methods

```python
from browser_use_sdk.v3 import BrowserUse, BuModel, ProxyCountryCode

client = BrowserUse()
# Available top-level methods:
# client.billing, client.browsers, client.close, client.profiles,
# client.run, client.sessions, client.stream, client.workspaces
```

## Account Info

```python
# ✅ CORRECT
acct = client.billing.account()
# Returns: name, total_credits_balance_usd, monthly_credits_balance_usd,
#          plan_info (plan_name, subscription_status), project_id

# ❌ WRONG (old API)
client.account.get()  # AttributeError
```

## Profiles (Persistent Cookies/LocalStorage)

```python
# List
profiles = client.profiles.list()

# Create
profile = client.profiles.create(
    name='listkit',
    description='ListKit Google OAuth login profile'
)
# Returns: id, name, last_used_at, created_at, updated_at, cookie_domains

# Get
p = client.profiles.get(str(profile.id))

# Update
client.profiles.update(str(profile.id), name='new-name')

# Delete
client.profiles.delete(str(profile.id))
```

## Sessions

```python
# Create with profile + keep_alive
session = client.sessions.create(
    model=BuModel.claude_sonnet_4_6,
    proxy_country_code=ProxyCountryCode.us,     # lowercase!
    keep_alive=True,
    profile_id=str(profile.id),                 # string, not UUID
)
# Returns: id, live_url, status

# Get
s = client.sessions.get(str(session.id))

# List
sessions = client.sessions.list()

# Stop
client.sessions.stop(str(session.id))

# Messages (chat history from agent)
msgs = client.sessions.messages(str(session.id))
```

## Running Tasks

```python
# ✅ CORRECT — client.run()
result = client.run(
    session_id=str(session.id),
    task="Go to https://example.com...",
    max_steps=15,
)
print(result.status)   # BuAgentSessionStatus (idle, running, completed, failed)
print(result.output)    # Agent's final message

# With structured output
from pydantic import BaseModel
class Lead(BaseModel):
    name: str
    email: str

result = client.run(
    session_id=str(session.id),
    task="Extract leads...",
    output_schema=Lead,
)
```

## ProxyCountryCode Enum

```python
# ✅ CORRECT (lowercase)
ProxyCountryCode.us
ProxyCountryCode.uk
ProxyCountryCode.de

# ❌ WRONG
ProxyCountryCode.US  # AttributeError: no attribute 'US'. Did you mean: 'us'?
```

## BuModel Enum

```python
BuModel.claude_sonnet_4_6    # Best for complex tasks
BuModel.claude_sonnet_4      # Older model
BuModel.gpt_4o               # OpenAI
```

## Error Handling

```python
from browser_use_sdk._core.errors import BrowserUseError

try:
    result = client.run(session_id=sid, task="...")
except BrowserUseError as e:
    # 502: Bad Gateway — session timed out or crashed
    # 404: Session not found
    # 429: Rate limited (free tier: 3 concurrent)
    print(f"{e.status_code}: {e}")
    # Recover: check session, create new if needed
```

## Known Issues

1. **502 Bad Gateway on stale sessions**: After 15 min inactivity or 4 hour max, `client.run()` returns 502. Solution: check with `client.sessions.get()`, create new session if needed.
2. **Google OAuth 2FA per session**: Each new session = new browser fingerprint = fresh 2FA. Profiles persist cookies within a session but don't carry 2FA approval across sessions. Keep `keep_alive=True` and reuse session_id.
3. **$17.16 credits remaining** on current account (Jun 11, 2026). Dev plan $29/mo.
4. **Live URLs**: `session.live_url` shows real-time browser view. Useful for debugging 2FA flows.
