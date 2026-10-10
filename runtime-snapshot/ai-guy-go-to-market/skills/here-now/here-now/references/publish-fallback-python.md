# here.now Python Publish Fallback

Use when `publish.sh` fails with `error: requires file` (the `file` binary is missing in minimal containers) or `jq` is unavailable. This reproduces the full create → upload → finalize flow with Python stdlib only.

## Requirements

- `python3` (stdlib only: urllib, hashlib, json, mimetypes)
- here.now API key in `~/.herenow/credentials` (single line) or `HERENOW_API_KEY` env var
- Authenticated publishes are permanent; anonymous (no key) expire in 24h

## Tested script

A working copy lives at `/opt/data/scripts/herenow-publish.py` (Hermes box):

```bash
python3 /opt/data/scripts/herenow-publish.py /path/to/dir-or-file "Title"
```

Core flow if rewriting from scratch:

```python
import hashlib, json, mimetypes, os, sys, urllib.request

BASE = "https://here.now"
API_KEY = open(os.path.expanduser("~/.herenow/credentials")).read().strip()
TARGET = sys.argv[1]

def req(url, data=None, headers=None, method=None):
    r = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(r, timeout=120) as resp:
        return resp.status, resp.read()

# 1. Build manifest: walk TARGET, for each file emit
#    {"path": relpath, "size": bytes, "contentType": mime, "hash": sha256hex}
files = []
for root, dirs, names in os.walk(TARGET):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for n in sorted(names):
        if n == ".DS_Store": continue
        p = os.path.join(root, n)
        rel = os.path.relpath(p, TARGET)
        files.append({
            "path": rel, "size": os.path.getsize(p),
            "contentType": mimetypes.guess_type(p)[0] or "application/octet-stream",
            "hash": hashlib.sha256(open(p, "rb").read()).hexdigest(),
        })

# 2. CREATE - POST {BASE}/api/v1/publish
#    headers: authorization "Bearer <key>", content-type json,
#             x-herenow-client "hermes/python-fallback"
#    body: {"files": files, "viewer": {"title": "..."}}  (add "slug" to update)
#    response: {slug, siteUrl, upload: {versionId, finalizeUrl,
#               uploads: [{path, url, headers: {"Content-Type": ...}}]}}

# 3. UPLOAD - for each entry in upload.uploads: PUT the local file bytes
#    to entry["url"] with header Content-Type from entry["headers"]
#    (pre-signed storage URLs; no Bearer auth on these)

# 4. FINALIZE - POST upload["finalizeUrl"] with {"versionId": upload["versionId"]}
#    Same Bearer auth as step 2. Response confirms the site is live.
```

## Verification gate

After finalize, verify before reporting success:

```bash
curl -s -o /dev/null -w '%{http_code}' https://<slug>.here.now/            # expect 200
curl -sL https://<slug>.here.now/<file> | sha256sum                        # compare to local
```

## Pitfalls

- `/tmp` writes may be blocked by HERMES_WRITE_SAFE_ROOT — stage scripts under `/opt/data/scripts/`.
- Content-Type for `.md`/`.txt`: send `text/plain; charset=utf-8`; the viewer lists them as browsable text.
- A single-file publish (the tarball alone) works too and is the right choice when the recipient only needs the archive; publishing the extracted directory gives agents a browsable index.
