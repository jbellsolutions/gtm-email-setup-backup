---
name: obsidian
description: Read, search, and create notes in the Obsidian vault.
---

# Obsidian Vault

**Location:** `/opt/data/obsidian-vault` (set via `OBSIDIAN_VAULT_PATH` in `/opt/data/.env`).

This vault follows the single-brain structure (git repo: `jbellsolutions/single-brain`).

## Vault Layout
```
vault/
├── agents/          Agent identities (CLAUDE.md, HERMES.md, voice.md)
├── sops/            Standard operating procedures per domain
├── decisions/       Append-only log of major decisions
├── daily-logs/      One .md file per day (YYYY-MM-DD.md)
├── domains/         Work product organized by domain
│   ├── ai-integraterz/   AI Integraterz operations docs
│   └── agi-1/            AGI-1 framework reports + dashboard
└── scripts/         vault-sync.sh, agi1_sync.py, meditation_council.py, vault_graph_analyzer.py
```

## Tagging Convention

Every vault file gets Obsidian wikilink tags at the bottom:
```markdown
---
Tags: [[ai-integraterz]] [[cold-email]] [[Instantly]]
```

Core tags: `[[ai-integraterz]]` `[[agi-1]]` `[[sop]]` `[[daily-log]]` `[[decisions]]`
`[[cold-email]]` `[[Instantly]]` `[[notion]]` `[[healing]]` `[[learning]]` `[[genome]]`
`[[ops-checklist]]` `[[knowledge-graph]]` `[[meditation-council]]` `[[vault-health]]`

Always tag new files. This powers the Obsidian graph view and the knowledge graph analyzer.
```

## CRITICAL: Log Everything
Every significant action, decision, or outcome MUST be logged to the vault:
- **Daily logs:** Append to `daily-logs/YYYY-MM-DD.md`
- **Decisions:** Append to `decisions/decisions.md`
- **New SOPs:** Create in `sops/`
- **Domain work:** Create in `domains/<domain>/`
The vault syncs via git every 30 minutes (cron job). Both Hermes and OpenClaw (single-brain) share this vault.

## End-of-Session Recap & Backup (Triple-Redundant)

After any major session (new skills created, infrastructure wired, campaigns launched, repos cloned), do this automatically — don't wait to be asked:

### Step 1: Write comprehensive daily log
Write to `daily-logs/YYYY-MM-DD.md` with full detail: what changed, skills created, cron jobs added, repos active, open items. Use the standard template:

```markdown
# Daily Note — YYYY-MM-DD
## Status
## Done Today
### 1. Category — What happened
### 2. Category — What happened
## Full Cron Schedule
## Repos Active
## Open Items
- [ ] Pending item
## Notes
```

### Step 2: Git commit + push
```bash
cd /opt/data/obsidian-vault
git add -A
git commit -m "daily-log: YYYY-MM-DD — <one-line summary>"
git push origin master:main
```

### Step 3: Append summary to Notion Operations Hub
The Ops Hub is a PAGE (not a database) at ID `3493fa00-4c9d-8105-8a4e-ccdb8f4700c9`. Append blocks via PATCH:

```python
PATCH https://api.notion.com/v1/blocks/{OPS_HUB_ID}/children
```

Include: strategy split, skills created, cron schedule, open items, link to full vault log.

### Trigger conditions
- User says "recap", "summarize the day", "back up", "make sure it's saved"
- After creating 3+ new skills or cron jobs
- After wiring major infrastructure (new repos, runtimes, integrations)
- At the natural end of a long session (15+ turns)

## Multi-Agent Shared Brain Pattern

The vault serves as shared memory between multiple AI agents. Git repo: `jbellsolutions/single-brain`.

### How Agents Integrate
1. Each agent gets an identity file in `agents/` (e.g. `HERMES.md`, `CLAUDE.md`)
2. Each reads SOPs from `sops/` before domain-specific work
3. Each appends to `daily-logs/YYYY-MM-DD.md` and `decisions/decisions.md`
4. Git auto-sync (cron every 30min via `scripts/vault-sync.sh`) keeps all agents current
5. Domain work products go in `domains/<domain>/`

### Adding a New Agent to the Vault
1. Create `agents/<AGENT_NAME>.md` with identity, responsibilities, tool access
2. Write relevant SOPs to `sops/`
3. Push to the single-brain repo
4. On the agent's machine: clone repo, set `OBSIDIAN_VAULT_PATH` in `.env`
5. Set up cron for `scripts/vault-sync.sh` (commit + pull + push)

### Vault Handshake Protocol (INBOX/OUTBOX)

When two Hermes agents on separate VPSes coordinate, the vault acts as the message bus. No MCP or HTTP API needed — git is the transport.

**Directory structure per project:**
```
vault/projects/<project-name>/
├── INBOX/          ← Coordinator writes tasks → Worker reads
├── OUTBOX/         ← Worker writes results → Coordinator reads
├── specs/          ← Architecture docs, PRDs, AGENTS.md
├── events/         ← Both agents log significant events
├── sprints/        ← Sprint plans, retrospectives
├── health/         ← Agent health reports (also synced to Notion)
└── HANDSHAKE.md    ← Protocol documentation
```

**INBOX format (task assignment):**
Create files as `INBOX/TASK-YYYY-MM-DD-NNN.md` with YAML frontmatter:
```yaml
---
task_id: TASK-2026-05-02-001
created: 2026-05-02T10:00:00-04:00
priority: P0  # P0-P3
repo: frontend|backend|infra
type: feature|bug|refactor|infra|docs|design
estimate: 4h
notion_task_id: xxx
---
# Task title

**Context:** Why this matters
**Acceptance Criteria:** Checklist of what done looks like
**Files to start with:** Path hints
```

**OUTBOX format (task completion):**
Create files as `OUTBOX/TASK-{id}-DONE.md` with frontmatter:
```yaml
---
task_id: TASK-2026-05-02-001
completed: 2026-05-02T14:30:00-04:00
status: done|blocked|failed
pr_url: https://github.com/.../pull/N
files_changed: 3
tests: 7 passed, 0 failed
---
# Done: Task title

**What changed:** Summary of work done
**PR:** Link to pull request
**Notes:** Any caveats
```

**Workflow:**
1. Coordinator writes task to `INBOX/`, pushes to git
2. Worker's cron (every 5min) pulls vault, scans `INBOX/` for new tasks
3. Worker executes, writes result to `OUTBOX/`, pushes
4. Coordinator's cron reads `OUTBOX/`, reports to user

**Setup script:** `scripts/speaker-agent-setup.sh` in the vault repo is a template for provisioning a new VPS with Hermes, an isolated profile, vault clone, sync cron, and Notion DB links. Adapt per project.

**AGENTS.md:** Each new agent gets a template from `projects/<name>/specs/AGENTS-template.md` that defines its identity, project scope, workflow, git conventions, and isolation boundaries (what it can/cannot access).

**Key principle:** The vault is a public channel between agents. Never put secrets, API keys, or sensitive data in vault files — those stay in each agent's isolated `config.yaml` and `.env`.

### Single-Brain Docker Integration
The single-brain `compose.yml` mounts `/srv/single-brain/vault/` as `/vault` in both the OpenClaw and Hermes containers. Both see the same files in real-time. Git sync only matters for cross-VPS agents.

## Knowledge Graph Analysis

A custom InfraNodus-style analyzer lives at `scripts/vault_graph_analyzer.py`. It builds a text co-occurrence network from all vault docs, detects topic clusters, finds structural gaps (blind spots), and identifies orphan topics.

```bash
PYTHONPATH=/opt/data/home/.local/lib/python python3 \
  /opt/data/obsidian-vault/scripts/vault_graph_analyzer.py \
  /opt/data/obsidian-vault \
  --output /opt/data/obsidian-vault/domains/ai-integraterz/knowledge-graph-analysis.md
```

Dependencies: `networkx`, `numpy`, `scikit-learn` (installed to `/opt/data/home/.local/lib/python`).

Weekly cron runs Mondays 9AM ET and delivers a report to Telegram.

Note: Vault paths may contain spaces - always quote them.

## Read a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat "$VAULT/Note Name.md"
```

## List notes

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# All notes
find "$VAULT" -name "*.md" -type f

# In a specific folder
ls "$VAULT/Subfolder/"
```

## Search

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# By filename
find "$VAULT" -name "*.md" -iname "*keyword*"

# By content
grep -rli "keyword" "$VAULT" --include="*.md"
```

## Create a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat > "$VAULT/New Note.md" << 'ENDNOTE'
# Title

Content here.
ENDNOTE
```

## Append to a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
echo "
New content here." >> "$VAULT/Existing Note.md"
```

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
