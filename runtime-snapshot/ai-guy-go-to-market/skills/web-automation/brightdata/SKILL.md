---
name: brightdata
description: Use Bright Data scrapers and APIs via brightdata-pp-cli. Triggers when the user mentions Bright Data, web scraping, datasets marketplace, Web Unlocker, SERP API, Scraper Studio, proxy zones, or needs to discover/run Bright Data scrape jobs.
---

# Bright Data Agent Skill

## CLI location
`~/.local/bin/brightdata-pp-cli`

## Setup on Justin's VPS (June 2026)

**CLI:** `/opt/data/home/.local/bin/brightdata-pp-cli` — installed and authenticated.
**Token:** NOT in `/opt/data/.env`. Must be set each session: `export BRIGHT_DATA_API_TOKEN="..."` 
**Catalog:** NOT downloaded. Run `brightdata-pp-cli catalog download` first to populate the local catalog before using `catalog --query` or `which` commands.
**Status:** `brightdata-pp-cli doctor` returns all green (Config, Auth, Env Vars, API, Credentials) but catalog is missing — `which` returns empty `{\"matches\": []}` until catalog is populated.

## First turn: credentials

Ask the user for **`BRIGHT_DATA_API_TOKEN`** if not already in the environment. Source: https://brightdata.com/cp/setting/users

Ask for these **only when needed**:
- `dataset_id` — from `brightdata-pp-cli datasets list`
- `BRIGHT_DATA_UNLOCKER_ZONE` — for `unlock`
- `BRIGHT_DATA_SERP_ZONE` — for `serp`
- `collector_id` — for Scraper Studio

Run `brightdata-pp-cli doctor` after setting the token.

## Pick the right product

| Goal | Command |
|------|---------|
| Prebuilt site scraper (Amazon, LinkedIn, etc.) | `datasets list` → `datasets trigger` or `datasets scrape` |
| Poll / download async job | `snapshot progress`, `snapshot download`, or `workflow scrape-and-wait` |
| One URL with anti-bot | `unlock --url ...` |
| Google/Bing SERP | `serp --query ...` |
| Custom Scraper Studio collector | `collector trigger` → `collector dataset` |
| Unsure which command | `which "<capability>"` or `catalog --query ...` |

Offline catalog: `catalog/brightdata-library.json` (805 entries, source https://docs.brightdata.com/llms.txt).

## End-to-end async scrape

```bash
export BRIGHT_DATA_API_TOKEN="..."
brightdata-pp-cli datasets list --agent --select id,name
brightdata-pp-cli workflow scrape-and-wait \
  --dataset-id DATASET_ID \
  --input '[{"url":"https://example.com/page"}]' \
  --agent
```

## Docs

- API reference index: https://docs.brightdata.com/llms.txt
- For agents: https://docs.brightdata.com/ai/for-agents/
- Marketplace list API: https://docs.brightdata.com/api-reference/marketplace-dataset-api/get-dataset-list.md

Always use `--agent` and `--dry-run` when exploring paid endpoints.
