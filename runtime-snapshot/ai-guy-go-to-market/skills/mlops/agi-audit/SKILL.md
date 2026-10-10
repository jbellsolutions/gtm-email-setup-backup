---
name: agi-audit
description: "Dual-scoring audit for any repo: G-Stack quality (0-100) + AI-readiness (0-100), optional self-healing bonus (0-50). Total out of 250. Evidence-based scoring — every point references a specific file or result. Trigger on 'audit this repo', 'score this repo', 'agi audit', 'quality check'."
version: 1.0.0
source: Adapted from AGI-1 v2.2.1 (jbellsolutions/agi-1)
---

# AGI Audit — Dual Quality + AI-Readiness Scoring

## Iron Law

**SCORES MUST BE EVIDENCE-BASED.** Every point awarded must reference a specific file, line, or test result. No guessing. No rounding up.

## Pre-flight: Verify repo paths

Before scoring, verify every target path exists. Repos may be specified at `/tmp/<name>` but the local clone may not be present (common in cron environments where repos weren't cloned, or on VPSes where only the vault has documentation). If a path is missing:

1. Search broadly: `find /tmp /opt /home -maxdepth 3 -type d -iname "*<repo-keyword>*" 2>/dev/null`
2. Check the vault for architecture docs: `find /opt/data/obsidian-vault/domains -type f -name "*.md" | sort`
3. Check `domains/ai-integraterz/systems-inventory.md` — it tracks GitHub repo names and expected local paths
4. See `references/vault-doc-paths.md` for a complete map of vault documentation paths per repo
5. If vault documentation exists but source is absent → produce a **documentation-only audit** (see below)
6. If nothing exists → report unscorable and move on

## Documentation-only audit (when source code is unavailable)

If a repo's architecture is documented in the Obsidian vault but the local clone is missing, produce a partial assessment:

- **Score what you can** from the architecture docs (agent topology, pipeline design, validation gates, daemon structure)
- **Mark unscorable categories** clearly with "❌ Source unavailable"
- **Include operational state** from vault snapshots (deliverability audits, campaign state, system inventories)
- **Flag the missing clone** as a finding — recommend cloning for the next audit cycle
- **Do NOT fabricate scores** for categories that require source code (code quality, testing, security, hardcoded secrets)
- **Use the modified output format** below with a ⚠️ DOCUMENTATION-ONLY header

### Documentation-only output format
```markdown
## Repo: <repo-name> ⚠️ DOCUMENTATION-ONLY
**Expected path:** <path>
**Status:** ❌ LOCAL CLONE NOT FOUND
**Documentation source:** <vault path>
**What's known:** <summary from vault docs>
**Known operational issues:** <from deliverability audits, state snapshots>
**Cannot score:** <list categories requiring source access>
**Recommendation:** Clone the repo to <path> for a proper source-level audit.
```

## Audit log location

After completing audits, write the full report to:
`/opt/data/obsidian-vault/domains/agi-1/audits/YYYY-MM-DD.md`

This ensures the shared brain (Obsidian + Notion bidirectional sync) captures audit history for cross-session reference and regression tracking.

## Delta Analysis (for recurring audits)

If this is a recurring cron audit, **load the previous audit first** from `/opt/data/obsidian-vault/domains/agi-1/audits/` (most recent dated file) before scoring. Use it to:

- **Flag regressions:** Score dropped? Why? (e.g., MCP server removed, test suite degraded)
- **Flag stagnation:** Same gap unfixed across 2+ cycles? (e.g., empty genome, missing clone)
- **Track action follow-through:** Did the previous audit's top 3 actions get addressed? Note which were done and which were ignored.
- **Surface new findings:** What's different this cycle vs last?

The delta analysis goes at the top of the final report as a "Trend Analysis" block, and per-repo scorecards include a Δ column showing change from the prior audit.

## Phase 1: G-Stack Quality Audit (0-100)

Score across 5 categories:

### Documentation (25 points)
| Item | Points | Check |
|---|---|---|
| README exists with purpose + setup | 5 | File present + contains setup instructions |
| ARCHITECTURE.md or equivalent | 5 | High-level system design documented |
| Inline docstrings on public API | 5 | grep for `"""` or `///` on exported functions |
| CHANGELOG or version history | 5 | Tracked changes over time |
| Decision records in vault | 5 | `decisions/` directory with dated entries |

### Code Quality (25 points)
| Item | Points | Check |
|---|---|---|
| Linter configured + passing | 5 | ruff/pylint/eslint config present |
| Type hints present | 5 | python: mypy passing; typescript: strict mode |
| Test suite with >50% coverage | 5 | pytest or vitest configured |
| No commented-out code | 5 | grep for large comment blocks |
| Consistent code style | 5 | formatter config (black, prettier) |

### Testing (20 points)
| Item | Points | Check |
|---|---|---|
| Unit tests exist | 5 | test files present |
| Integration tests exist | 5 | Tests that cross module boundaries |
| Smoke tests run green | 5 | Quick sanity tests pass |
| CI/CD configured | 5 | GitHub Actions or similar |

### Self-Healing Readiness (15 points)
| Item | Points | Check |
|---|---|---|
| Error patterns catalogued | 5 | Known error → fix mappings exist |
| Restart/retry logic present | 5 | Exponential backoff, circuit breakers |
| Health checks defined | 5 | `/health` endpoint or heartbeat |

### Security (15 points)
| Item | Points | Check |
|---|---|---|
| No hardcoded secrets | 5 | No API keys in source files |
| Input validation present | 5 | Request/argument validation |
| Dependency scanning | 5 | Dependabot or similar |

## Phase 2: AI-Tool Readiness (0-100)

### Agent Discoverability (30 points)
| Item | Points | Check |
|---|---|---|
| CLAUDE.md or AGENTS.md at root | 10 | Agent-first documentation |
| Manifest file present | 10 | manifest.yaml or pyproject.toml with metadata |
| Skills directory structure | 10 | SKILL.md files with frontmatter |

### Tool Integration (25 points)
| Item | Points | Check |
|---|---|---|
| MCP server/connector present | 10 | MCP endpoint for external tool access |
| API with structured output | 10 | JSON schema or Pydantic models |
| Logging/tracing configured | 5 | Structured logs, Langfuse or similar |

### Autonomy Readiness (25 points)
| Item | Points | Check |
|---|---|---|
| Idempotent operations | 10 | Safe to re-run without side effects |
| Dry-run mode available | 5 | Preview changes before applying |
| Rollback capability | 5 | Can undo applied changes |
| Progressive disclosure | 5 | Complex actions broken into steps |

### Memory & Learning (20 points)
| Item | Points | Check |
|---|---|---|
| Vault/conversation logging | 10 | Session output saved to vault |
| Pattern learning | 5 | Extracts learnings from runs |
| Cross-session memory | 5 | Persistent memory across sessions |

## Phase 3: Self-Healing Bonus (0-50)

| Item | Points | Check |
|---|---|---|
| Known error patterns with fixes | 10 | Error → fix mapping present |
| Auto-retry on transient failures | 10 | Retry logic for network/timeout |
| Self-diagnostic capability | 10 | Can detect own issues |
| Upgrade/sync automation | 10 | Nightly or periodic upstream pulls |
| Learning propagation | 10 | Learnings shared across sessions/repos |

## Total: 0-250

- **200+**: Elite. AI-native, self-healing, production-ready.
- **150-199**: Strong agent foundation. Close gaps in documentation + autonomy.
- **100-149**: Agent can operate but needs guardrails. Missing discovery + tool integration.
- **50-99**: Agent-hostile. Add CLAUDE.md, manifest, structured output.
- **<50**: Not agent-ready. Start with documentation + basic structure.

## Output Format

```markdown
## AGI Audit: <repo-name>
**Date:** YYYY-MM-DD
**Score:** X/250 (Δ +/-Y from prior audit — only if recurring)

### G-Stack Quality: X/100
| Category | Score | Max | Δ |
|---|---|---|---|
| Documentation | X | 25 | ±Y |
| Code Quality | X | 25 | ±Y |
| Testing | X | 20 | ±Y |
| Self-Healing | X | 15 | ±Y |
| Security | X | 15 | ±Y |

### AI-Readiness: X/100
| Category | Score | Max | Δ |
|---|---|---|---|
| Agent Discoverability | X | 30 | ±Y |
| Tool Integration | X | 25 | ±Y |
| Autonomy Readiness | X | 25 | ±Y |
| Memory & Learning | X | 20 | ±Y |

### Self-Healing Bonus: X/50

### Top 3 Improvement Actions
1. [Highest-impact gap] — impact: +X points
2. [Second-highest] — impact: +X points
3. [Third-highest] — impact: +X points

### Path to Elite (if <200)
Fix [top-gap] (+X) + [second-gap] (+X) = current → target score.
```

### Multi-repo Summary (when auditing >1 repo)

```markdown
## Summary

| Repo | Score | Δ | Status |
|---|---|---|---|
| **repo-1** | **X/250** | ±Y | Source audited |
| **repo-2** | Unscorable | — | ⚠️ Docs-only |

### Trend Analysis
[What moved: regressions, stagnation, new findings, action follow-through from last cycle]
```

## What to Do Next

Score <150: load `agi-1` orchestrator skill for full pipeline upgrade.
Score 150-199: close specific gaps identified in audit.
Score 200+: maintain, run quarterly audits to prevent drift.

**For recurring audits:** cross-check the prior audit's "Top 3 Improvement Actions" — did any get addressed? Flag undone actions that persist across multiple cycles as stagnation risks. A gap that survives 2+ audit cycles without action is itself a finding worth surfacing in the trend analysis.
