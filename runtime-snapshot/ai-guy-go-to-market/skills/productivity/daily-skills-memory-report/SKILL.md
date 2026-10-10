---
name: daily-skills-memory-report
description: "Use for daily Skills & Memory reports."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, memory, daily-report, session-search, vault, cron]
    related_skills: [hermes-agent-skill-authoring]
---

# Daily Skills & Memory Reporting

## Overview

This skill governs the recurring report that audits the previous calendar day's sessions for skill changes, saved memories, and reusable lessons. It produces two artifacts: a complete Markdown report in the Obsidian vault and a short delivery message suitable for Slack or the cron origin channel.

The report is an evidence audit, not a speculative retrospective. Count only changes and lessons supported by session messages or verified skill/memory state. Preserve important negative findings, such as a memory write rejected by the capacity limit, without presenting them as successful saves.

## When to Use

- A scheduled job asks for the daily Skills & Memory report.
- The user asks what skills, memories, or reusable lessons emerged yesterday.
- A recurring operational report needs to inspect session history and write a vault daily log.

Do not use this skill for a one-off task summary that does not inspect skills, memories, or durable workflow lessons.

## Procedure

### 1. Establish the reporting date

Report the prior calendar day in the timezone specified by the job prompt, normally US Eastern. Use a date command or an equivalent timezone-aware calculation; never infer the date from the current message timestamp alone. Derive both the ISO date (`YYYY-MM-DD`) and compact search form (`YYYYMMDD`).

Completion criterion: the report date is explicit and consistent in the filename, heading, and delivery summary.

### 2. Search sessions with broad, independent queries

Use `references/session-search-query-playbook.md` for the canonical query set and evidence rules. Search session history for the reporting date using several queries rather than relying on one exact phrase. At minimum, cover:

- the ISO or compact date;
- skill operations: `skill_manage`, `skill_created`, `skill_updated`, or `skill_patched`;
- memory operations: `memory add`, `memory replace`, or equivalent tool activity;
- reusable lessons: `lesson`, `workaround`, `bug`, `fix`, `patch`, `workflow`, `solved`, or `discovered`.

Prefer the session-search discovery shape first. When a result identifies a relevant session and message ID, use the scroll shape with that real message ID to inspect context. Do not repeatedly pass a fabricated or zero message ID; if a scroll call fails, return to discovery with a narrower query or use the session ID-only read shape if supported.

Search tool messages when exact operation names are absent from user/assistant prose. Treat search results as leads: verify the surrounding messages before counting a change.

Completion criterion: every counted item has a session/message evidence trail, and the search covered skills, memories, and lessons independently.

### 3. Classify findings conservatively

Separate the report into:

- **Skills:** created, patched, edited, archived, restored, or otherwise materially updated. Include the skill name and a concise description of the change.
- **Memories:** successful writes only, with target (`user` or `memory`) and a content summary. Record rejected, over-capacity, or failed writes as an attempted change or lesson, not as a saved memory.
- **Lessons Learned:** reusable techniques, corrections, workflow gates, or provider/tool quirks that would change future behavior. Exclude transient setup failures, unverified guesses, and one-off narratives.

When the same event appears in multiple sessions, deduplicate it. Prefer the final verified outcome over an intermediate attempt. If no evidence survives verification, report `None` rather than filling the section with plausible but unsupported content.

### 4. Write the full vault report

Write to `/opt/data/obsidian-vault/daily-logs/{date}.md` using this structure:

```markdown
## Skills & Memory Report — {date}
### Skills
- ...

### Memories
- ...

### Lessons Learned
- ...
```

Use `None` for empty sections. Keep the full detail in the file, including evidence-qualified caveats and failed writes that matter operationally. Do not truncate the file merely to fit the delivery channel.

Completion criterion: the file exists at the exact date path and contains all three headings with counts that match the classified findings.

### 5. Deliver only a compact summary

Return a short message, normally under 300 characters:

```text
📊 Daily Report — {date}
Skills: {count}
Memories: {count}
Lessons: {count}
Full report → vault daily-logs/{date}.md
```

Do not paste the full report into Slack or the final response. If there is genuinely nothing new, use the scheduler's exact silent marker only when the job explicitly requests it; otherwise report zero counts and the vault path.

## Common Pitfalls

1. **Counting attempted writes as saves.** A memory call rejected for the 2,200-character limit is not a saved memory. State the rejection separately.
2. **Searching only assistant prose.** Tool calls often contain the authoritative `skill_manage` or `memory` operation; include tool messages when needed.
3. **Using invalid scroll anchors.** Scroll requires a real message ID from discovery, not `0` or a guessed ID. Retry with discovery, not the same failing arguments.
4. **Confusing loaded/used with updated.** A skill being viewed or used is not a skill patch. Count it under lessons only if it produced a durable, verified workflow improvement.
5. **Over-reporting transient infrastructure errors.** Capture the reusable workaround or confirmed fix, not a temporary command failure or an unavailable binary.
6. **Sending the full report through a narrow channel.** The vault file is the primary artifact; delivery is only the compact index.
7. **Claiming delivery side effects without evidence.** In a cron context, produce the final summary and let the scheduler deliver it; do not invoke a separate messaging tool unless explicitly required by the job.

## Verification Checklist

- [ ] Prior-day date and timezone are explicit.
- [ ] Skill, memory, and lesson searches were performed independently.
- [ ] Findings were deduplicated and evidence-checked.
- [ ] Failed or rejected writes are not counted as successful memories.
- [ ] Full report contains Skills, Memories, and Lessons Learned sections.
- [ ] Vault path uses the exact reporting date.
- [ ] Final delivery is compact and does not duplicate the full report.
