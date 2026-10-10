---
name: agi-1-framework
description: "AGI-1 self-healing/self-learning framework: genome, healing patterns, learning pipeline, Notion+vault sync."
version: 1.0.0
author: jbellsolutions
metadata:
  hermes:
    tags: [AGI-1, Self-Healing, Self-Learning, Genome, Framework]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# AGI-1 Framework Operations

Self-healing, self-learning, autorecursive AI development framework. Repo: `jbellsolutions/agi-1`.

## Three Layers

| Layer | Mode | Timescale | Trigger |
|---|---|---|---|
| **Healing** | Reactive | Seconds | Error occurs |
| **Learning** | Reflective | Sessions | Every N sessions |
| **Genome** | Propagative | Repos | Cross-repo sync |

## The Flywheel

Error → Healer catches → Pattern reaches 0.8+/5+ → Genome promotion → Next repo inherits → Auto-heals → Learns → Loop repeats.

## Confidence Gates

- **≥0.8 + 5 fixes**: Genome promotion candidate
- **0.6-0.79**: Auto-fix, normal trust
- **0.3-0.59**: Low confidence, flag for review
- **<0.3 after 10+**: Auto-demoted
- **0 after 3 fails**: Removed

## Notion Databases (under Operations Hub)

| Database | ID | Purpose |
|---|---|---|
| 🩹 Healing Patterns | `3543fa00-4c9d-8137-b4d5-f59e9acf6d23` | All error patterns with confidence scores |
| 👁️ Learning Observations | `3543fa00-4c9d-81a6-9d08-fe6eb642d045` | Raw signals from every agent |
| 💡 Learning Insights | `3543fa00-4c9d-817d-9557-cf322fa44ba0` | Processed insights with evidence |
| 🧬 Genome Changelog | `3543fa00-4c9d-8156-a614-e83a0fe1f022` | Every genome mutation logged |
| 🫀 Agent Health | `3543fa00-4c9d-81e2-914d-c25a1d11f6bd` | Daily per-repo health metrics |

## Sync Engine

Script: `/opt/data/obsidian-vault/scripts/agi1_sync.py`

```bash
PYTHONPATH=/opt/data/home/.local/lib/python python3 /opt/data/obsidian-vault/scripts/agi1_sync.py
```

Scans repos for `.claude/healing/`, `.claude/learning/`, `.agi1/` directories.
Syncs to Notion + writes vault report.

## Meditation Council

Script: `/opt/data/obsidian-vault/scripts/meditation_council.py`

```bash
PYTHONPATH=/opt/data/home/.local/lib/python python3 /opt/data/obsidian-vault/scripts/meditation_council.py
```

The council reflects on ALL data across repos and produces suggestions. It **never takes action** — only observes and recommends. Analyzes:
- Pattern health (category distribution, genome candidates, failing patterns, cross-repo patterns)
- Learning signals (repeated errors, ignored instructions, corrections)
- Skill & process meta-improvements (unused skills, fix strategy distribution, insight quality)

Runs daily alongside the sync engine. Reports go to Slack.

## Cron Jobs

| Job | Schedule | Delivers To |
|---|---|---|
| AGI-1 Sync + Meditation Council | Daily 7AM ET | Slack (#agi-1-reports or #single-brain) + Telegram summary |

## Vault Location

`/opt/data/obsidian-vault/domains/agi-1/`
- `dashboard.md` — current state overview
- `daily-report-YYYY-MM-DD.md` — daily sync reports
- `meditation-YYYY-MM-DD.md` — council reflections and suggestions

## 17 Skills (Claude Code slash commands)

| Command | Purpose |
|---|---|
| `/agi-1` | Full 8-phase pipeline |
| `/agi-heal` | Fix known error pattern |
| `/agi-learn` | Extract insights from observations |
| `/agi-sync` | Sync to/from genome |
| `/agi-audit` | Score repo (0-250) |
| `/agi-council` | 3-agent critique |
| `/agi-debug` | Root cause analysis |
| `/agi-verify` | Quality gates |
| `/agi-tdd` | Test-driven development |
| `/agi-research` | Autorecursive research |
| `/agi-dream` | Memory consolidation |
| `/agi-clean` | Remove AI bloat |
| `/agi-skill-master` | Improve/create skills |

## Meditation Council

Script: `/opt/data/obsidian-vault/scripts/meditation_council.py`

Reflects on all healing patterns, observations, and insights across repos. Produces suggestions only — never takes action. Finds:
- Cross-cutting pattern themes (what error categories dominate)
- Genome promotion/demotion candidates
- Skill improvements (unused skills, popular skills)
- Process improvements (fix strategy distribution, insight quality)

Runs daily at 7AM alongside the sync. Reports to `#agi-1-reports` in Slack.

## Report Routing

| Report | Slack Channel | Vault | Telegram |
|---|---|---|---|
| Sync + Health | `#agi-1-reports` | daily-logs + [[agi-1]] | Summary |
| Meditation Council | `#agi-1-reports` | meditation file + [[meditation-council]] | Suggestion count |
| Knowledge Graph | `#agi-1-reports` (weekly Mon) | analysis file + [[knowledge-graph]] | Summary |

## Adding a New Repo to AGI-1

1. Add repo path to `REPO_PATHS` in `agi1_sync.py`
2. Run `/agi-1` in the repo with Claude Code (or manually scaffold `.agi1/`)
3. Sync engine auto-discovers healing/learning data
4. Daily cron reports include the new repo

## Onboarding a Repo Manually (Without Claude Code)

Create `.agi1/` directory with:
```
.agi1/
├── healing/
│   ├── patterns.json    # Copy from agi-1/templates/healing/patterns.json
│   └── history.json     # Empty: {"entries": []}
├── learning/
│   ├── observations.json # Empty: {"observations": []}
│   └── insights.json     # Empty: {"insights": []}
└── state.json            # {"session_count": 0}
```
