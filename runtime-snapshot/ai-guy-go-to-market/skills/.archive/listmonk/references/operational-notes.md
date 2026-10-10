# ListMonk Operational Notes (Jul 28, 2026)

## API Authentication

### Admin credentials do NOT work for API
- Admin user "List Monk One" / "ListMonk2026$" returns `403 {"message":"invalid API credentials"}` on ALL API endpoints
- ListMonk separates UI auth from API auth by design

### Creating an API user
Run in browser console while logged in as admin:
```javascript
fetch(window.location.origin + '/api/users', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'apiuser', email: 'apiuser@yourdomain.com', name: 'API User',
    type: 'api', password: 'SomePassword!', status: 'enabled', user_role_id: 1
  })
}).then(r => r.json()).then(d => console.log(d));
```

Required fields (error messages are misleading):
- `username` — required
- `type: 'api'` — must be exactly this string
- `status: 'enabled'` — required (error: "invalid input value for enum user_status")
- `user_role_id` — required (error: "null value in column user_role_id"). Get IDs from `GET /api/users` → `user_role.id`
- `password` — becomes the token. Response returns it in the `password` field — copy immediately

### Current API credentials
- API user: `apiuser`
- Token: `[REDACTED]`
- Usage: `Authorization: token apiuser:[REDACTED]`

## Browser Session Pitfalls

- Session expires within minutes on Railway-hosted ListMonk
- `browser_console` `fetch()` fails with "Failed to parse URL" when browser drops to `about:blank`
- **Always prefer terminal** (`lm.sh` or Python `urllib`) with API user token over browser-based API calls
- If you must use browser: login → immediately run fetch() → don't navigate elsewhere first

## Template Tags (Go templates)

Correct ListMonk template tags for campaign HTML:
- `{{ UnsubscribeURL }}` — unsubscribe link (NOT `{{.UnsubURL}}`)
- `{{ MessageURL }}` — view-in-browser link (NOT `{{.TrackView}}`)
- `{{ TrackLink "https://..." }}` — tracked external link
- `{{ .Subscriber.Email }}`, `{{ .Subscriber.Name }}`, `{{ .Subscriber.FirstName }}` — personalization

## Campaign Creation and Updates

### Create draft
```python
import json, urllib.request

payload = json.dumps({
    'name': 'Campaign Name',
    'subject': 'Subject line',
    'from_email': 'Scale Vertical AI <email@scaleverticalwithai.com>',
    'body': html_content,
    'content_type': 'html',
    'lists': [1],
    'template_id': 1,
    'messenger': 'email',
    'type': 'regular',
    'tags': ['newsletter']
}).encode('utf-8')

req = urllib.request.Request(
    'https://listmonk-production-2930.up.railway.app/api/campaigns',
    data=payload,
    headers={
        'Authorization': 'token apiuser:[REDACTED]',
        'Content-Type': 'application/json'
    },
    method='POST'
)
resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
```

### Update campaign body (PUT)
```python
# Same payload but with PUT method and /api/campaigns/{id}
req = urllib.request.Request(
    'https://listmonk-production-2930.up.railway.app/api/campaigns/4',
    data=payload,  # same JSON as create
    headers={...},
    method='PUT'
)
```

### Large HTML bodies
- HTML up to ~57K chars works fine via Python `urllib.request` with API user auth
- No need for browser console chunking — terminal API calls handle full HTML in one request
- No need for base64 encoding or chunked uploads — just JSON body with the HTML as a string

## JangoMail → ListMonk HTML Conversion

When reusing newsletter HTML from JangoMail campaigns in ListMonk:

| JangoMail | ListMonk | Notes |
|---|---|---|
| `https://track.scaleverticalwithai.com/u.z?***uniqueid****` | `{{ UnsubscribeURL }}` | JangoMail system link → ListMonk template tag |
| `https://track.scaleverticalwithai.com/w.z?***uniqueid****` | `{{ MessageURL }}` | View-online link |
| `https://track.scaleverticalwithai.com/c.z?***uniqueid****&u=ENCODED_URL` | Decode `u=` param back to raw URL | Manual /c.z wrapping is broken in JangoMail — restore raw links for ListMonk |
| `https://img.jangomail.com/2606407/Images/...` | Keep as-is | JangoMail CDN images are public, work in ListMonk campaigns |

Conversion script:
```python
import re, urllib.parse, json

def convert_jangomail_to_listmonk(html):
    # Swap system links
    html = html.replace(
        'https://track.scaleverticalwithai.com/u.z?***uniqueid****',
        '{{ UnsubscribeURL }}'
    )
    html = html.replace(
        'https://track.scaleverticalwithai.com/w.z?***uniqueid****',
        '{{ MessageURL }}'
    )
    
    # Restore raw editorial links from broken /c.z wrapping
    cz_prefix = 'https://track.scaleverticalwithai.com/c.z?***uniqueid****&u='
    while cz_prefix in html:
        idx = html.index(cz_prefix)
        url_start = idx + len(cz_prefix)
        # Find end of URL (next quote char)
        end = len(html)
        for i in range(url_start, len(html)):
            if html[i] in '"\'<>& ':
                end = i
                break
        encoded = html[url_start:end]
        decoded = urllib.parse.unquote(encoded)
        html = html[:idx] + decoded + html[end:]
    
    return html
```

## SMTP Status

- **Current:** Broken. Resend SMTP configured but `send.usingaitoscale.com` not verified since Jul 22, 2026
- **Migration target:** Bird/SparkPost (`smtp.eu.sparkpostmail.com:587`, STARTTLS, `SMTP_Injection`)
- **Blocker:** Bird email product not provisioned — DKIM won't generate, API 401s on email endpoints
- **Impact:** No campaigns can send from ListMonk until SMTP is fixed
- **Workaround:** JangoMail is carrying all newsletter sends in the meantime

See `references/bird-smtp-listmonk-migration.md` in the `email-platforms` skill for the migration procedure.
