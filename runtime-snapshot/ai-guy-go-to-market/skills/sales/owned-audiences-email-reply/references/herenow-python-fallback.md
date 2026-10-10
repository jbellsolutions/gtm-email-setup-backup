# here.now Python Publish Fallback

When `publish.sh` fails because the `file` binary isn't available (common on minimal VPS/container images), use this Python stdlib-only approach. Same three-step flow, zero shell dependency.

```python
import json, os, hashlib, urllib.request

BASE_URL = "https://here.now"
TARGET = "/path/to/file-or-dir"
API_KEY = None  # Set to permanent key string, or None for anonymous (24h)

# --- Step 0: Build file manifest ---
FILES = []
if os.path.isfile(TARGET):
    size = os.path.getsize(TARGET)
    sha = hashlib.sha256(open(TARGET, 'rb').read()).hexdigest()
    ext = TARGET.rsplit('.', 1)[-1].lower()
    ct_map = {'pdf': 'application/pdf', 'html': 'text/html', 'png': 'image/png',
              'jpg': 'image/jpeg', 'svg': 'image/svg+xml', 'json': 'application/json'}
    ct = ct_map.get(ext, 'application/octet-stream')
    FILES = [{"path": os.path.basename(TARGET), "size": size, "contentType": ct, "hash": sha}]
else:
    for fname in sorted(os.listdir(TARGET)):
        fpath = os.path.join(TARGET, fname)
        if not os.path.isfile(fpath):
            continue
        size = os.path.getsize(fpath)
        sha = hashlib.sha256(open(fpath, 'rb').read()).hexdigest()
        ext = fname.rsplit('.', 1)[-1].lower()
        ct_map = {'pdf': 'application/pdf', 'html': 'text/html', 'png': 'image/png',
                  'jpg': 'image/jpeg', 'svg': 'image/svg+xml'}
        ct = ct_map.get(ext, 'application/octet-stream')
        FILES.append({"path": fname, "size": size, "contentType": ct, "hash": sha})

# --- Build auth headers ---
headers = {"Content-Type": "application/json", "X-HereNow-Client": "hermes/publish-sh"}
if API_KEY:
    headers["Authorization"] = f"Bearer {API_KEY}"

# --- Step 1: Create publish ---
body = json.dumps({"files": FILES}).encode()
req = urllib.request.Request(f"{BASE_URL}/api/v1/publish", data=body, headers=headers)
resp = json.loads(urllib.request.urlopen(req).read())
slug = resp['slug']
site_url = resp['siteUrl']
print(f"Slug: {slug}  |  URL: {site_url}")
print(f"Expires: {resp.get('expiresAt', 'permanent')}")

# --- Step 2: Upload files ---
for up in resp['upload']['uploads']:
    fpath = os.path.join(TARGET if os.path.isdir(TARGET) else os.path.dirname(TARGET), up['path'])
    data = open(fpath, 'rb').read()
    req2 = urllib.request.Request(up['url'], data=data, method='PUT',
        headers={"Content-Type": up['headers']['Content-Type']})
    urllib.request.urlopen(req2)
    print(f"  Uploaded: {up['path']}")

# --- Step 3: Finalize ---
fin_body = json.dumps({"versionId": resp['upload']['versionId']}).encode()
fin_headers = {"Content-Type": "application/json", "X-HereNow-Client": "hermes/publish-sh"}
if API_KEY:
    fin_headers["Authorization"] = f"Bearer {API_KEY}"
req3 = urllib.request.Request(resp['upload']['finalizeUrl'], data=fin_body,
    headers=fin_headers,
    method='POST')
urllib.request.urlopen(req3)
print(f"\nLive: {site_url}")
```

**Auth:** Upload PUTs don't need auth headers — only the create and finalize calls do. For anonymous publishes, omit the `Authorization` header entirely.