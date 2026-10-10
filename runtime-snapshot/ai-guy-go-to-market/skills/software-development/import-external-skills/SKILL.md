---
name: import-external-skills
description: "Import and adapt external skill repositories into Hermes. Use when user drops a GitHub URL to a skill repo and says 'add these skills', 'import this', or 'here are skills for X'. Handles cloning, surveying, identifying high-value skills, adapting tool calls from native format (TypeScript/Claude Code) to Hermes equivalents (MCP/Python/cron), and creating operational cron cadences."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, import, external, adaptation, github]
    related_skills: [hermes-agent-skill-authoring, legacy email platform-cold-email, cold-email-weekly-rhythm]
---

# Importing External Skills into Hermes

## Overview

External skill repos (GrowthEngineX, Claude Code community, custom repos) are built for different agents with different tooling. This skill defines the repeatable pattern for absorbing them into Hermes: clone → survey → prioritize → adapt → operationalize.

## When to Use

- User drops a GitHub URL and says "here are skills to add," "import these," "skills for X"
- User asks to pull in a third-party Claude Code / agent skill collection
- User wants to augment Hermes with community-vetted operational patterns

Don't use for: single-skill imports (just read + adapt manually), or repos that are frameworks rather than skill collections (treat those as context, not skill imports).

## Workflow

### Phase 1 — Clone and Survey

```bash
cd /tmp && git clone <repo-url>
```

Identify the skill directory structure:
- Claude Code repos: `skills/<name>/SKILL.md`
- Custom repos: find all `SKILL.md` files

Read the README and roadmap/docs first — they group skills into tracks/domains and show dependencies.

### Phase 2 — Prioritize

Read 3-5 key SKILL.md files. Score each on:
- **Immediate value**: does this fill a gap in current Hermes operations?
- **Adaptation effort**: TypeScript-heavy scripts need more rewriting than pure-playbook skills
- **Dependency chain**: some skills assume others ran first (e.g., `cold-email-kickoff` → `icp-onboarding` → `campaign-copywriting`)

Import high-value, low-effort skills first. Skip skills that duplicate what Hermes already does natively.

### Phase 3 — Adapt Tool Calls

External skills reference their native tooling. Replace with Hermes equivalents:

| External pattern | Hermes equivalent |
|---|---|
| `npx tsx scripts/foo.ts --id=X` | legacy email platform MCP tools (`mcp_legacy email platform_get_*`) |
| `claude code /slash-command` | Hermes skill `skill_view` + direct execution |
| `fetch from API via curl` | Python `urllib.request` (curl not installed on VPS) |
| `write to Supabase` | Write to Notion DB or Obsidian vault |
| `send to Slack` | Direct Slack webhook or Hermes channel delivery |
| `cron / schedule` | Hermes cronjob tool |

Strip TypeScript scripts entirely — Hermes has MCP-based tool access that's more direct.

### Phase 4 — Create Hermes Skills

Use `skill_manage(action='create')` for each adapted skill. Place in the appropriate category (`sales/` for cold email, `productivity/` for ops, etc.).

Frontmatter conventions:
```yaml
version: 1.0.0
source: Adapted from <source-repo-name>
```

Preserve the original skill's structure but rewrite tool calls. Keep the wisdom, replace the implementation.

### Phase 5 — Operationalize

For rhythm/cadence skills, set up cron jobs immediately:
```python
cronjob(action='create', name='<descriptive-name>', 
         schedule='<cron expression>', 
         skills=['<skill-name>', 'legacy email platform-cold-email'],
         prompt='<what to do each run>')
```

Bind the skill to the legacy email platform MCP skill so it has API access:
```
skills: [relevant-skill, legacy email platform-cold-email]
```

### Phase 6 — Log and Update Memory

- Save repo location to memory
- Note which skills were imported vs. skipped (for future reference)
- Log the import to Obsidian vault: `decisions/YYYY-MM-DD-skill-import-<repo-name>.md`

## Real Example: GrowthEngineX Cold Outbound Skills

1. **Cloned**: `/tmp/coldoutboundskills` (28 skills in 5 tracks)
2. **Surveyed**: README grouped into Strategy / Infrastructure / List Building / Copy & Send / Iterate
3. **Prioritized**: Jesse had active legacy email platform campaigns → skipped setup skills (zapmail, icp-onboarding), focused on operational skills
4. **Imported 4 skills**:
   - `cold-email-weekly-rhythm` — operational backbone (Mon/Wed/Fri cadence)
   - `spam-word-checker` — always-on copy QA guardrails
   - `positive-reply-scoring` — north-star metric classification
   - `email-deliverability-audit` — domain/inbox health checks
5. **Adapted**: Replaced TypeScript `npx tsx scripts/*` calls with legacy email platform MCP tools (`mcp_legacy email platform_get_*`)
6. **Operationalized**: Created 2 cron jobs (Monday deliverability audit at 9 AM, Wednesday reply sweep at 10 AM)
7. **Skipped**: 24 remaining skills (infrastructure setup, list building, TypeScript-heavy scripts)

## Common Pitfalls

1. **Importing skills that duplicate Hermes' native capabilities.** Hermes already has MCP-based legacy email platform access — don't import scripts that redo what MCP tools handle directly.
2. **Blindly copying TypeScript scripts.** Hermes can't run `npx tsx`. Rewrite the logic, keep the intent.
3. **Importing the entire repo.** Only import skills that actually fill gaps. 28 skills → 4 imported is the right ratio.
4. **Forgetting cron operationalization.** A weekly rhythm skill without a cron job is just documentation. Wire it.
5. **Not binding the legacy email platform MCP skill to cron jobs.** Without `skills: [skill-name, legacy email platform-cold-email]`, cron jobs can't call the legacy email platform API.

## Verification Checklist

- [ ] Repo cloned and surveyed (README + docs read)
- [ ] Skills prioritized by value/effort — not all imported
- [ ] Tool calls adapted from native format to Hermes equivalents
- [ ] Skills created via `skill_manage(action='create')` with `source:` annotation
- [ ] Rhythm/cadence skills have cron jobs operationalized
- [ ] Cron jobs include necessary skill bindings (e.g., legacy email platform-cold-email)
- [ ] Import logged to Obsidian vault decisions/
- [ ] Memory updated with repo location
