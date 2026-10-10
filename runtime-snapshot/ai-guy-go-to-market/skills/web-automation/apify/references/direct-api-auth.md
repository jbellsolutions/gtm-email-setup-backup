# Direct Apify API authentication

When a user asks to retrieve Apify runs and a local `APIFY_API_KEY` is provisioned, use the Apify REST API directly. Do not substitute Composio.

## Probe

```bash
python3 - <<'PY'
import os, requests
key = os.environ['APIFY_API_KEY']
r = requests.get(
    'https://api.apify.com/v2/users/me',
    headers={'Authorization': f'Bearer {key}'},
    timeout=30,
)
print(r.status_code, r.text[:300])
PY
```

A successful probe authorizes follow-up calls such as `/v2/actor-runs`. A `401 user-or-token-not-found` response is a hard authentication blocker. Do not retry the same token indefinitely, expose the token, or redirect the user into an unrelated Composio connection flow. State that the local key must be replaced or renewed.

## Session lesson

A local key was present in `/opt/data/.env`, but direct calls to both `/v2/users/me` and `/v2/actor-runs` returned 401. The initial workflow incorrectly tried Composio first; future runs must validate and use the local credential directly.