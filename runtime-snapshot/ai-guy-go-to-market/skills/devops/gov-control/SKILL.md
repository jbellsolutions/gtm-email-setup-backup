---
name: gov-control
description: Programmatic + conversational control of the Paperclip board — companies, agents, routines, projects, issues, imports. Full API reference with patterns, gotchas, Python client, and Go CLI.
---

# Governance Control Layer — Paperclip Board

Board URL: `https://137-184-151-136.sslip.io`
Auth: `Authorization: Bearer $PAPERCLIP_API_KEY`
Content-Type: `application/json`

## Key IDs
- **Governance HQ company**: `bab0fbf1-ccec-427a-a3ce-0aee70b4baf8`
- **Architect agent**: `1ea8fa51-a804-456c-8661-7f3dcbe9f47e`

## Env Setup
```bash
export PAPERCLIP_API_URL="https://137-184-151-136.sslip.io"
export PAPERCLIP_API_KEY="pcp_board_…"
export OPENROUTER_API_KEY="sk-or-…"
export GOV_MODEL="openrouter/anthropic/claude-sonnet-4.5"
```

## API Reference

### Companies
| Operation | Method | Path |
|-----------|--------|------|
| List all | GET | /api/companies |
| Get one | GET | /api/companies/{id} |
| Create | POST | /api/companies |
| Update | PATCH | /api/companies/{id} |
| Archive | PATCH | /api/companies/{id} → `{"status":"archived"}` |

### Agents
| Operation | Method | Path |
|-----------|--------|------|
| List (by company) | GET | /api/companies/{C}/agents |
| Get one | GET | /api/agents/{id} |
| Create | POST | /api/companies/{C}/agents |
| Update | PATCH | /api/agents/{id} |
| Pause/Resume | PATCH | /api/agents/{id} → `{"status":"paused"/"active"}` |
| Terminate | PATCH | /api/agents/{id} → `{"status":"terminated"}` |
| Delete (hard) | DELETE | /api/agents/{id} (may 500 if has reports) |

### Projects
| Operation | Method | Path |
|-----------|--------|------|
| List/Get/Create/Update | - | /api/companies/{C}/projects, /api/projects/{id} |

### Routines
| Operation | Method | Path |
|-----------|--------|------|
| List/Get/Create/Update/Delete | - | /api/companies/{C}/routines, /api/routines/{id} |

### Issues
| Operation | Method | Path |
|-----------|--------|------|
| List/Get/Create/Update | - | /api/companies/{C}/issues, /api/issues/{id} |
| Add comment | POST | /api/issues/{id}/comments |

### Imports
- POST `/api/companies/{C}/imports/apply` — import from GitHub preset or inline package
- Available presets: `paperclip/companies/_template`, `paperclip/companies/lead-gen-agency`, `paperclip/companies/governance-hq`
- GitHub URL must use `.../tree/<branch>/<path>` format

## Patterns (Flows A-E)

### Flow A — New Company (from scratch/template)
1. Gather: company name, purpose, team shape, template choice
2. Plan: list what will be created, confirm with user
3. Import: use `imports/apply` with GitHub source + `adapterOverrides` for every agent slug
4. Verify: GET company, list agents, list routines, confirm `triggers[].nextRunAt`
5. Report: company ID, agent IDs, first run time, follow-ups

### Flow B — New Team inside existing company
1. Find company by name → get ID
2. Plan: N agents + routines, show hierarchy
3. Create agents: POST each with `opencode_local` + `reportsTo`
4. Create routines: POST with cron + `assigneeAgentId`
5. Verify: list agents, routines, confirm `nextRunAt`

### Flow C — Pivot/Change (model, budget, status, cron)
1. Find target by name
2. Show current state (GET)
3. Plan the PATCH
4. Confirm + execute
5. Verify with GET

### Flow D — Inspect / Retrieve
1. Find company/agent by name
2. Fetch full state: company + agents + routines + issues
3. Summarize: budget vs spend, agent statuses, open issues, next routine fire

### Flow E — Retire / Archive
- Company: PATCH `{"status":"archived"}`
- Agent (leaf): PATCH `{"status":"terminated"}` or DELETE if no reports
- Agent (manager): PATCH `{"status":"terminated"}` — NEVER delete
- Routine: DELETE safely

## Pre-Flight Check

Before any API call, verify env vars are set:
```bash
echo "KEY_SET=${PAPERCLIP_API_KEY:+yes}  URL_SET=${PAPERCLIP_API_URL:+yes}"
```
If `KEY_SET` is empty, stop — the board is unreachable. Ask the user for the key.

## Python Client (`core/gov_client.py`) — MAY NOT BE PRESENT

The Python client lives at `core/gov_client.py` relative to the working directory. It may not exist on every system. If `from core.gov_client import GovClient` fails with `ModuleNotFoundError`, fall back to raw curl — the API reference tables above have every endpoint. All operations work via curl with the same env vars.

When the client IS available:
```python
from core.gov_client import GovClient, GovAPIError
client = GovClient()
# Board: board_summary()
# Companies: list_companies(), find_company("name"), create_company(), archive_company()
# Agents: list_agents(), find_agent(), create_agent(), change_model(), pause/resume/terminate_agent()
# Routines: list_routines(), create_routine(cid, title, agent_id, cron)
# Issues: list_issues(), create_issue(), add_comment()
# Imports: import_github_preset("preset/path", "New Co Name")
```

## Go CLI (`gov-pp-cli`) — MAY NOT BE PRESENT

60+ commands if installed. Check with `which gov-pp-cli`. If missing, use curl — all operations are documented above.

## Critical Gotchas
1. **GitHub import URL**: Must be `.../tree/<branch>/<path>` — no separate `path` field
2. **Adapter**: Always `opencode_local` — safe imports reject `process`. `adapterConfig.model` is required.
3. **Collision strategy**: Always `"rename"` — `"replace"` is rejected
4. **Routine frequency**: `daily` + weekday filters rejected. Use cron: `0 8 * * 1,2,3,4,5`
5. **Hard delete disabled**: Archive companies, terminate agents. DELETE agents only if no direct reports.
6. **Teams without routines won't run**: Always verify `triggers[].nextRunAt`
7. **Agent instructions**: Filesystem files only — `instructionsFilePath`, not raw text via API

## Find by Name (no name-search endpoint)
```bash
# Find company by name fragment
curl -sS "$B/api/companies" "${H[@]}" | python3 -c \
  "import sys,json;q=sys.argv[1].lower();xs=[c for c in json.load(sys.stdin) if q in c['name'].lower()];print(json.dumps(xs,indent=2))" "acme"
```
