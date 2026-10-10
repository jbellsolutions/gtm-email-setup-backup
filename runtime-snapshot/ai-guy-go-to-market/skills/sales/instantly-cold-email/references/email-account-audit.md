# Email Account Health Auditing

Audit all Instantly email accounts for deliverability issues. Instantly has no
explicit "blacklisted" flag. Warmup reputation is the closest proxy.

## Key Indicators

| Signal | Threshold | Meaning |
|---|---|---|
| `warmup_reputation` | < 90% | Poor domain/IP reputation. Accounts will land in spam. |
| `warmup_details.status` | != "ACTIVE" | Warmup disabled or paused — account not ready to send. |
| `is_smtp_success` | false | SMTP connection failure. Account can't send at all. |
| `is_imap_success` | false | IMAP failure. Can't receive replies. |
| `daily_sent_count >= message_per_day` | true | At daily limit. Won't send more today. |

## Quick Audit Command

Pull all accounts and analyze in one shot:

```bash
curl -s "https://server.Instantly/api/v1/email-accounts/?api_key=$Instantly_API_KEY&limit=200&offset=0" \
  -o /tmp/sl_accounts.json
```

Then process with Python (script at `scripts/audit-accounts.py`):

```bash
python3 scripts/audit-accounts.py /tmp/sl_accounts.json
```

## Manual One-Liner

For a quick at-a-glance view without the script:

```bash
curl -s "https://server.Instantly/api/v1/email-accounts/?api_key=$Instantly_API_KEY&limit=200&offset=0" | \
  python3 -c "
import json,sys
from collections import Counter
data=json.load(sys.stdin)
tags=Counter()
problems=[]
for a in data:
    t=[t.get('tag_name','') for t in a.get('tags',[])]
    for tag in t: tags[tag]+=1
    w=a.get('warmup_details') or {}
    rep=w.get('warmup_reputation','N/A')
    try:
        if int(rep.replace('%',''))<90:
            problems.append(f\"{a['from_email']} rep:{rep} tags:{','.join(t)}\")
    except: pass
print(f'Total: {len(data)} | Low rep (<90%): {len(problems)}')
for tag,c in tags.most_common():
    p=[1 for x in problems if tag in x]
    print(f'  {tag}: {c} total, {len(p)} problematic')
"

## Response Structure

The API returns a flat JSON array of account objects at the top level. Not wrapped
in pagination metadata. Key fields per account:

```json
{
  "id": 18592806,
  "from_email": "destiny@elevateaxisca.info",
  "from_name": "Destiny Cunningham",
  "type": "GMAIL",
  "is_smtp_success": true,
  "is_imap_success": true,
  "smtp_failure_error": null,
  "imap_failure_error": null,
  "message_per_day": 12,
  "daily_sent_count": 0,
  "campaign_count": 0,
  "tags": [{"tag_name": "PuzzleInbox"}],
  "warmup_details": {
    "status": "ACTIVE",
    "warmup_reputation": "96%",
    "total_sent_count": 0,
    "total_spam_count": 0
  }
}
```

## Domain Reputation Analysis

When multiple accounts share a domain and all have low reputation, the domain itself
is burned — not individual accounts. Look for clusters:

- All accounts on a domain below 80% rep → domain is flagged
- Mixed rep on same domain → some individual accounts may be salvageable
- Accounts with `type: SMTP` and low rep → these are custom SMTP (non-Google/Outlook)
  and the sending IP may be on blocklists

## Provider Identification

Instantly tags map to providers. Common tags in Justin's setup:

| Tag | Provider | Account Type |
|---|---|---|
| `PuzzleInbox` | Puzzle Inbox | GMAIL |
| `mailreef` | MailReef | SMTP (custom domains) |
| `home services` | Mixed | Mixed |

## Pitfalls

- **MCP truncation**: `mcp_Instantly_list_email_accounts` truncates large responses.
  Use direct `curl` via terminal for the full 200-account payload.
- **API auth**: Query param only. `?api_key=$Instantly_API_KEY`. Do NOT use Bearer
  or `api-key` header — 401 "API key is required".
- **No explicit blacklist API**: Instantly's API has no `is_blacklisted` field.
  Warmup reputation and connection status are the only signals available.