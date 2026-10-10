# AgentMail — Email Inboxes for AI Agents

AgentMail (agentmail.to) is a YC-backed email inbox API built for AI agents. It gives agents their own email inboxes via REST API — like Gmail for humans, but designed for autonomous agent workflows.

When a user says "agentmail," "set up agentmail," or "create an agentmail account," they mean **this service**, not a generic Gmail/IMAP account. Do NOT create a Google account or configure IMAP/SMTP — the user will push back.

## Key Details

- **URL:** https://www.agentmail.to/
- **Signup:** https://console.agentmail.to/sign-up
- **Docs:** https://docs.agentmail.to/
- **SDKs:** Python (`pip install agentmail`), TypeScript (`npm install agentmail`), CLI
- **Features:** Inboxes API, threads + replies, attachments, realtime events (webhooks), custom domains, semantic search, data extraction, MCP integration
- **Pricing:** Free tier available, no credit card required to start
- **Status:** YC-backed, SOC 2 compliant

## vs. Hermes Email Gateway (IMAP/SMTP)

| | Hermes Email Gateway | AgentMail |
|---|---|---|
| Protocol | IMAP/SMTP (standard email) | REST API |
| Setup | Needs email account + app password | Sign up on website, API key |
| Inbox creation | One account = one inbox | Create multiple inboxes via API |
| Use case | Chat with agent via email | Agent sends/receives email programmatically |
| Dependencies | None (Python stdlib) | SDK or direct HTTP |

The Hermes Email Gateway lets humans email the agent and get replies. AgentMail lets the agent operate email inboxes programmatically — sign up for services, extract 2FA codes, handle support emails, etc.

## Integration with Hermes

AgentMail can be used as:
1. **An MCP server** — AgentMail provides an MCP server for tool integration
2. **Direct API calls** — Use `execute_code` with the AgentMail Python SDK or HTTP requests
3. **CLI tool** — `agentmail` CLI for terminal-based inbox management

### Quick Start (Python SDK)

```python
from agentmail import AgentMail

client = AgentMail(api_key="am_...")

# Create an inbox
inbox = client.inboxes.create(name="hermes-inbox")
print(inbox.email_address)  # e.g., hermes-inbox@agentmail.to

# List messages
messages = client.messages.list(inbox_id=inbox.id)

# Send a message
client.messages.send(
    inbox_id=inbox.id,
    to="someone@example.com",
    subject="Hello from Hermes",
    body="This is an automated message."
)
```

## Signup Requirements

There are two ways to sign up:

### Human Signup (via Console)
- Go to https://console.agentmail.to/sign-up
- Requires: first name, last name, email, password (or "Sign up with Google")
- **Pitfall:** The console is behind Cloudflare — browser automation tools can't get past the security challenge. The sign-up form is also a JS-heavy React SPA that often renders as a blank page in headless browsers.

### Agent Self-Signup (via API — preferred for Hermes)
The agent registers itself programmatically using the human's email. An OTP is sent to that email for verification.

**CLI:**
```bash
# Install
npm install -g agentmail-cli
# Sign up
npx agentmail-cli agent sign-up \
  --human-email you@example.com \
  --username my-agent
# Returns: api_key (am_...), inbox_id, organization_id
# Then verify with OTP sent to the human email
export AGENTMAIL_API_KEY="am_..."
npx agentmail-cli agent verify --otp-code 123456
```

**Python SDK:**
```python
from agentmail import AgentMail
client = AgentMail()  # No API key needed for sign-up
result = client.agent.sign_up(
    human_email="you@example.com",
    username="my-agent"
)
# result.api_key, result.inbox_id, result.organization_id
# Then verify:
client.agent.verify(otp_code="123456")
```

**Pitfall — keyword-only args:** `agent.sign_up()` uses keyword-only arguments. Passing positional args raises `TypeError: AgentClient.sign_up() takes 1 positional argument but 3 were given`. Always use `human_email=...` and `username=...`.

**Pitfall — PYTHONPATH:** If `agentmail` was installed with `pip install --break-system-packages` (required on this VPS due to PEP 668), it goes to `~/.local/lib/python3.13/site-packages/` which is NOT on the default Python path when using `python3 -c`. Either run from that directory or set `PYTHONPATH`.

**Pitfall — AlreadyExistsError (403):** If the account already exists, the sign-up endpoint returns `403 Forbidden: {"name": "AlreadyExistsError", "message": "Organization already exists"}`. This means the human email is already registered — the API key already exists and must be retrieved from the console or the original confirmation email. The sign-up is NOT idempotent for verified accounts (contrary to the docs which say it rotates the key).

**Pitfall — OTP delivery:** The OTP goes to the human email, not the agent. The agent must ask the human for the code before it can verify and get an API key.

## Message Reading API (Python SDK) — Discovered Patterns

The SDK response objects use Pydantic models. Key field name gotchas:

### Listing inboxes
```python
result = client.inboxes.list()
# result.inboxes (NOT result.data) — list of Inbox objects
# result.count — total count
for inbox in result.inboxes:
    inbox.inbox_id   # e.g., "singlebrainslack@agentmail.to" — this IS the email
    inbox.email      # e.g., "singlebrainslack@agentmail.to"
    inbox.display_name
    inbox.pod_id
    # NOT: inbox.email_address (AttributeError)
```

### Listing messages
```python
result = client.inboxes.messages.list("inbox_id_or_email", limit=10)
# result.messages (NOT result.data)
# result.count — total count
for msg in result.messages:
    msg.message_id    # e.g., "<CAGS5zv...@mail.gmail.com>" — use for get()
    msg.subject
    msg.from_         # NOT msg.from_address (AttributeError)
    msg.preview       # short preview text
    msg.labels        # e.g., ['received', 'unread']
```

### Getting full message content
```python
full = client.inboxes.messages.get("inbox_id", msg.message_id)
# full.text          — plain text body
# full.html          — HTML body (use for newsletters)
# full.extracted_text — cleaned text (best for reading)
# full.extracted_html — cleaned HTML
# full.from_         — sender
# full.to            — list of recipients
# full.subject
# full.attachments   — list or None
```

### Creating an inbox
```python
new = client.inboxes.create(display_name="My Agent")
# new.inbox_id — email address string
# new.email    — same as inbox_id
```

### API key storage
Store in `.env` as `AGENTMAIL_API_KEY=am_...` and `AGENTMAIL_INBOX=inbox_id@agentmail.to`.
The Python SDK client is initialized with `AgentMail(api_key="am_...")`.