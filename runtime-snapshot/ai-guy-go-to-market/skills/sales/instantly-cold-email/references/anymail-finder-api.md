# Anymail Finder API Reference

## Verify Email

**Endpoint:** `POST https://api.anymailfinder.com/v5.1/verify-email`
**Auth:** Header `Authorization: <API_KEY>`
**Content-Type:** `application/json`
**Body:** `{"email": "person@domain.com"}`
**Cost:** 0.2 credits per verification (free if same email verified within 30 days)

### Response

```json
{
  "credits_charged": 0.2,
  "email_status": "valid"
}
```

### Status values

| Status | Meaning | Action |
|---|---|---|
| `valid` | Deliverable and verified | ✅ Upload to campaign |
| `risky` | May exist but inconclusive | ⚠️ Upload but flag |
| `invalid` | Does not exist / will bounce | 🚫 Discard |

### Performance

- Single-email API only — no bulk endpoint
- ~1.5 seconds per email
- 12 concurrent workers: ~5,000 emails in ~10 minutes
- Rate limit: safe at 15 concurrent, no hard cap observed

### Credit management

- Check credits: `GET https://api.anymailfinder.com/v5.1/account` (Authorization header)
- Response: `{"credits_left": 1668, "email": "user@domain.com"}`
- Repeated verifications of the same email within 30 days are free

### Python example

```python
import urllib.request, json, concurrent.futures

KEY = "<api_key>"

def verify_email(email):
    url = "https://api.anymailfinder.com/v5.1/verify-email"
    data = json.dumps({"email": email}).encode()
    req = urllib.request.Request(url, data=data,
        headers={"Authorization": KEY, "Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return {"email": email, "status": json.loads(resp.read().decode()).get("email_status")}
    except:
        return {"email": email, "status": "error"}

emails = ["a@b.com", "c@d.com"]
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    futures = {ex.submit(verify_email, e): e for e in emails}
    for f in concurrent.futures.as_completed(futures):
        results.append(f.result())
```

Full docs: https://anymailfinder.com/email-finder-api/docs/verify-email
