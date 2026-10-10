---
name: super-agent-bootstrap
description: "Bootstrap the Hermes Super Agent operating system distribution. Clone the repo, initialize vendor submodules (fixing HTTPS→SSH auth), build the system graph via manifest aggregator, wire nightly upgrader and weekly AGI audit cron jobs. Trigger when user wants to 'set up Super Agent', 'wire agent-os', 'bootstrap the agent operating system', or when setting up a new VPS with the full agent stack."
version: 1.0.0
---

# Super Agent Bootstrapping

The Hermes Super Agent is the Agent OS distribution — Hermes orchestrator + 13 specialist runtimes + 7 vendored submodules + AGI-1 quality flywheel + nightly upgrader. This skill covers the repeatable bootstrap sequence.

## When to Use

- Setting up a new VPS with the full agent stack
- User says "wire Super Agent," "bootstrap agent-os," "set up the agent operating system"
- After cloning the repo and needing to initialize everything
- When submodules fail to clone (HTTPS auth issues)

## Prerequisites

- Git with SSH key configured for GitHub (`jbellsolutions` account)
- `uv` package manager installed
- Notion API key (for backup logging)
- Obsidian vault path configured

## Bootstrap Sequence

### 1. Clone the Repo

```bash
GIT_SSH_COMMAND="ssh -i /opt/data/.ssh/id_ed25519 -o StrictHostKeyChecking=no" \
  git clone git@github.com:jbellsolutions/hermes-super-agent.git /tmp/hermes-super-agent
```

### 2. Fix Submodule Auth (Critical)

The `.gitmodules` uses HTTPS URLs which fail without a credential helper. Fix globally:

```bash
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

Then initialize all 7 submodules:

```bash
cd /tmp/hermes-super-agent
git submodule update --init --recursive
```

Submodules initialized:
- `vendor/hermes-agent` (NousResearch)
- `vendor/openclaw` (openclaw)
- `vendor/browser-use` (browser-use)
- `vendor/aider` (Aider-AI)
- `vendor/agi-1` (jbellsolutions — self-healing flywheel)
- `vendor/awesome-hermes-agent` (community extensions)
- `vendor/nemoclaw` (NVIDIA — sandboxed execution)

### 3. Verify Submodules

```bash
ls vendor/*/README.md   # Each should have a README
```

### 4. Build the System Graph

```bash
cd /tmp/hermes-super-agent
uv run agent-os manifest
```

Expected output: `{"nodes": 19, "edges": 57}` — plus any validation warnings (non-blocking).

The graph writes to `vault/graph/system.yaml`. 19 nodes = core components + 13 specialist runtimes + 3 vertical apps.

### 5. Wire Nightly Upgrader Cron

Create a cron job that runs at 2 AM ET daily:

```
cronjob create:
  name: super-agent-nightly-upgrader
  schedule: 0 2 * * *
  command: cd /tmp/hermes-super-agent && VAULT_ROOT=/opt/data/obsidian-vault uv run python -m agent_os.upgrader.daemon
```

The upgrader runs 10 streams sequentially: hermes, openclaw, browser_use, aider, codex, agi1, awesome_hermes, nemoclaw, mcp_registry, vendor_health. Each pulls upstream + runs smoke tests.

Also run manifest aggregation after upgrader:
```
cd /tmp/hermes-super-agent && uv run agent-os manifest
```

### 6. Wire Weekly AGI Audit Cron

```
cronjob create:
  name: weekly-agi-audit
  schedule: 0 10 * * 1    (Monday 10 AM ET)
  skills: [agi-audit]
  prompt: Score all 3 core repos (cold-email, flywheel, super-agent) on 250-point scale
```

### 7. Verify

- [ ] All 7 vendor submodules have README files
- [ ] `uv run agent-os manifest` outputs 19 nodes / 57 edges
- [ ] Nightly upgrader cron visible in `cronjob list`
- [ ] Weekly AGI audit cron visible
- [ ] System graph file exists: `vault/graph/system.yaml`

## What the Graph Shows

19 nodes with 57 dependency edges. Key relationships:

- **agent-os.orchestrator** (Hermes/me) — all 13 runtimes + 3 vertical apps depend on me
- **Specialist runtimes** (openclaw, browser_use, computer_use, terminal, e2b, claude_managed, exa, codex_cli, livekit, claude_subagents, aider) — each produces `vault_run_artifact`
- **Vertical apps** (sdr-fleet, coo-control-room, content-engine) — consume agent-os via manifest.yaml
- **Quality** (agi-1) — consumes vault runs, produces scores and prompt variations

## Ecosystem Architecture

After bootstrapping, the full layer stack is:

| Layer | Tool | Role |
|---|---|---|
| 1 | Claude Code + Opus 4.7 | Direct, at-keyboard |
| 2 | **Hermes** (me) | Always-on orchestrator |
| 3 | OpenClaw | Long shell/file/browser grind |
| 4 | browser-use | Structured browser automation |
| 5 | Computer Use | Raw desktop / native apps |
| 6 | Claude Code subagents | Interactive coding |
| 7 | Codex CLI / Aider | Background coding |
| 8 | Claude Managed | Long-running cloud (>1hr) |
| 9 | E2B | Sandboxed code execution |
| 10 | Exa | Search-to-artifact |
| 11 | LiveKit | Voice / realtime |

## Pitfalls

1. **HTTPS submodule auth fails**: Use `git config --global url."git@github.com:".insteadOf` before `git submodule update`.
2. **AGI-1 submodule is private**: Requires SSH key for `jbellsolutions` account. If key is missing, AGI-1 will be the only submodule that fails.
3. **uv may warn about VIRTUAL_ENV mismatch**: Ignore — it resolves automatically.
4. **Manifest validation warnings**: Non-blocking. The aggregator skips invalid manifests and still builds the graph.
5. **VAULT_ROOT must point to Obsidian vault**: Set `VAULT_ROOT=/opt/data/obsidian-vault` when running upgrader.
