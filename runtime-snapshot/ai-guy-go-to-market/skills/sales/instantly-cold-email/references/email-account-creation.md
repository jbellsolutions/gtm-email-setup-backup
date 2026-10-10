# Email Account Creation & Winnr Integration

## Instantly MCP Unreliable for Account Creation

As of July 2026, `mcp_Instantly_create_email_account` returns 400 errors or the server becomes
unreachable. For creating email accounts, always fall back to the Instantly CLI.

## Creating Email Accounts via CLI

```bash
Instantly mailboxes create --from-json <file>
```

### Required JSON Format

```json
{
  "from_name": "Aaron Carter",
  "from_email": "aaron.carter@learnshop.co",
  "user_name": "aaron.carter@learnshop.co",
  "password": "[REDACTED]",
  "smtp_host": "inbound.mywinnr.com",
  "smtp_port": 465,
  "imap_host": "inbound.mywinnr.com",
  "imap_port": 993,
  "warmup_enabled": false
}
```

### Critical Pitfalls

| Pitfall | API Error |
|---|---|
| Use `username` instead of `user_name` | `"user_name" is required` |
| Include `message_per_day` in payload | `"message_per_day" is not allowed` |
| Omit `warmup_enabled` | `"warmup_enabled" is required` |
| Duplicate email address | `"Email account already exist. Please pass id to update it"` |

### Bulk Creation Pattern

For 20 accounts, create each JSON file and call the CLI in a loop with 300ms delay:

```python
import json, subprocess, os, time

env = os.environ.copy()
env["Instantly_API_KEY"] = "<key>"
env["PATH"] = "/opt/data/home/.local/bin:" + env.get("PATH", "")

for acct in accounts:
    payload = {
        "from_name": acct["from_name"],
        "from_email": acct["from_email"],
        "user_name": acct["user_name"],
        "password": acct["password"],
        "smtp_host": acct["smtp_host"],
        "smtp_port": int(acct["smtp_port"]),
        "imap_host": acct["imap_host"],
        "imap_port": int(acct["imap_port"]),
        "warmup_enabled": False
    }
    with open("/tmp/acct.json", "w") as f:
        json.dump(payload, f)
    result = subprocess.run(
        ["Instantly", "mailboxes", "create", "--from-json", "/tmp/acct.json"],
        capture_output=True, text=True, timeout=60, env=env
    )
    if result.returncode == 0:
        resp = json.loads(result.stdout)
        print(f"OK: {acct['from_email']} → ID {resp['emailAccountId']}")
    time.sleep(0.3)
```

## Winnr Pre-Warmed Inbox Import

When importing pre-warmed inboxes from [Winnr](https://winnr.app) into Instantly:

### Step 1: Export from Winnr

```bash
POST https://api.winnr.app/v1/export
Content-Type: application/json
Authorization: Bearer <WINNR_API_TOKEN>

{
  "format": "Instantly",
  "getAllDomains": true
}
```

Response includes a `download_url` with an S3 pre-signed CSV containing:
`from_email, from_name, user_name, password, smtp_host, smtp_port, imap_host, imap_port`

### Step 2: Download & Parse CSV

Fetch the download URL with httpx (curl with S3 pre-signed URLs often times out). Parse with csv.DictReader.

### Step 3: Create in Instantly

All Winnr inboxes share these values:
- `smtp_host`: `inbound.mywinnr.com`
- `smtp_port`: `465`
- `imap_host`: `inbound.mywinnr.com`
- `imap_port`: `993`
- `warmup_enabled`: `false` (already pre-warmed by Winnr)

Use the CLI bulk creation pattern above.

### Winnr MCP Server

Configured in `/opt/data/config.yaml` under `mcp_servers.winnr`:
```yaml
winnr:
  command: uvx
  args:
  - winnr-mcp
  - --token
  - [REDACTED]
  env:
    WINNR_API_TOKEN: [REDACTED]
  timeout: 120
```

Provides tools for listing email users (`/v1/email-users`), inbox management (`/v1/inbox`),
account info (`/v1/account`), and usage stats. Useful for inspecting account state but the
export endpoint is faster for bulk Instantly import.
