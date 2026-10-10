# Cross-platform ZIP and locked-template QA reference

## Archive extraction

A ZIP created on Windows may expose member names such as `template\\TEMPLATE.html` instead of normal directory paths. A portable extraction pattern is:

```python
import os, zipfile
src = "kit.zip"
out = "work-kit"
with zipfile.ZipFile(src) as z:
    for name in z.namelist():
        if name.endswith("/"):
            continue
        normalized = name.replace("\\\\", "/")
        path = os.path.join(out, normalized)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(z.read(name))
```

Inspect `os.listdir()` after extraction if reads unexpectedly report missing files. Do not assume a successful archive command created nested folders.

## Deterministic template substitution

Read the template as text, enumerate slot names with `\\[\\[[A-Z0-9_]+\\]\\]`, construct a complete mapping, replace each exact token once or as specified, and assert that no `[[` remains. Never use a model-generated rewrite of the HTML.

## Invariants

For the Credit Memo-style template, verify:

- 145 `style="` attributes
- 15 `<table` tags
- 8 `border-collapse:separate`
- 15 `#9a5f1d`
- 18 `#0f0f0f`
- `{{ MessageURL }}` ×2, `{{ UnsubscribeURL }}` ×2, `{{ FirstName }}` ×1
- identical sets of `style="..."` attributes in both directions
- two occurrences of each news-card source URL
- exactly three occurrences of the fixed offer URL

Run an HTML parser after substitution. Pending image URLs are acceptable only as an explicit draft blocker, never as send-ready output.

## Evidence ledger

For every load-bearing figure, record the exact browser-opened URL, publisher, page date/title, primary or secondary status, and the supporting passage. If the official source is blocked or missing, record the failed primary lookup and clearly label the secondary fallback in both copy and handover notes. This is safer than presenting a plausible but unsupported official citation.
