# JangoMail v2 Campaign Creation — Working Payload (Jul 17 2026)

Discovered through trial/error. The blank schema (`GET /campaigns/new`) doesn't clearly
document the object shapes for `from` and `to_other`, nor the mandatory `character_set`/`encoding` fields.

## Working Python snippet

```python
import urllib.request, json, base64

USER = "UsingAIToScale"
PASS = "Jango123!"
auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
base = 'https://api-v2.jangomail.com'
headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/json; charset=utf-8'
}

with open('email.html', encoding='utf-8') as f:
    html = f.read()

data = {
    'from': {                                      # object, not string
        'email': 'email@scaleverticalwithai.com',
        'name': 'Synova Talent Solutions'
    },
    'subject': 'Subject line',
    'reply_to': 'reply@domain.com',
    'message_html': html,
    'message_plain': 'Plain text fallback',
    'to_other': [{'email': 'placeholder@domain.com'}],  # array of objects, not strings
    'tracking': {
        'click_track_html': True,
        'track_opens': True
    },
    'character_set': 'UTF-8',     # REQUIRED — omit → "Unsupported encoding"
    'encoding': 'Quoted Printable', # REQUIRED — '7 bit'|'Quoted Printable'|'Base64'
    'create_only': True            # draft — still needs at least one recipient
}

body = json.dumps(data, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(f'{base}/campaigns', data=body, headers=headers, method='POST')
resp = json.loads(urllib.request.urlopen(req).read())
# → {"campaign_id": 399259736}
```

## Error → Fix mapping

| Error | Cause | Fix |
|-------|-------|-----|
| `"The from field is required."` | `from` is a string, not object | Use `{"email": "...", "name": "..."}` |
| `"JSON value could not be converted to EmailAddressModel"` | `to_other` elements are strings | Use `[{"email": "..."}]` |
| `"Unsupported encoding"` | Missing `character_set` or `encoding` | Add both fields |
| `"No recipients specified"` | No `to_other`, `to_lists`, or `to_web_databases` | Add placeholder recipient |
| Response has no `id` field | Response uses `campaign_id`, not `id` | Read `result['campaign_id']` |