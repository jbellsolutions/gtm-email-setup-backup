---
name: here-now
description: "here.now lets agents publish websites and files to live URLs in seconds. Publish HTML, documents, images, PDFs, videos, and static files to live URLs at {slug}.here.now or custom domains."
---

# here.now

Publish files and folders to live URLs via here.now — instant web hosting for agents.

**Install:** `npx skills add heredotnow/skill --skill here-now -g -y`

## Quick Publish

```bash
bash /opt/data/skills/here-now/scripts/publish.sh /path/to/file --title "Title" --client hermes
```

## Requirements

- `curl`, `jq`, `file`

## Pitfalls

- **Missing jq/file in minimal environments:** In containers or slim VPS without package managers, `jq` and `file` may be unavailable. Use the Python fallback in `references/publish-fallback-python.md` — it reproduces the full create→upload→finalize flow using only curl + Python stdlib.
- **Bundled jq may not exist:** The skill ships with a bundled `bin/jq` but it may not be present after npx install. Check `ls /opt/data/skills/here-now/bin/jq` first.
- **Anonymous sites expire in 24h.** Share the claim URL so users can make sites permanent.
