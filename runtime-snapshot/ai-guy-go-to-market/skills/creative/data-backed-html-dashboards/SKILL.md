---
name: data-backed-html-dashboards
description: "Use for data-backed HTML dashboards."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [html, dashboards, data, visualization, reporting, verification]
    related_skills: [claude-design, popular-web-designs]
---

# Data-Backed HTML Dashboards

Use when turning a structured inventory, tracker, scheduler export, or operational dataset into a self-contained HTML artifact that people need to read and understand. Prioritize comprehension and source fidelity over decoration.

## Composition

Treat the artifact as a **Monitor / Inspect** surface, not a marketing landing page. Include:

1. A concise title and plain-language orientation.
2. Summary counts computed from source data.
3. Search and filters over full record content.
4. Grouping by the most important state, such as enabled vs paused.
5. One readable card per source record.
6. Expandable raw configuration or provenance for auditability.
7. Responsive and print-friendly behavior.

Do not use generic feature-card filler, invented metrics, or unexplained abbreviations.

## Source-grounded content

Use the current structured source as the single source of truth. Preserve each stable ID, name, schedule, state, delivery target, last status, skills/tags, and relevant raw prompt/configuration.

Write descriptions that answer what the record does, when it runs, what systems or scripts it inspects, what processing it performs, what outputs it creates, where results are delivered, and what safeguards or failure behavior matters.

Translate configuration into plain language, but do not invent behavior. If a name or prompt is blank, explicitly label the record **unidentified** and explain that its purpose cannot be inferred reliably. Never assign a plausible old purpose based only on a schedule or historical backup.

When the user says descriptions are too brief, expand the actual workflow and constraints. Do not merely add visual decoration or generic prose.

## Implementation

Prefer one portable HTML file with embedded CSS and JavaScript. Use CSS variables, semantic sections, responsive grid layout, accessible controls, visible status badges, readable monospace schedule/ID labels, and `<details>` for raw prompt/configuration context. Escape source-derived strings before inserting them into HTML.

Search should include names, IDs, schedules, descriptions, and skills. Filters should update the visible count and maintain state grouping. Avoid remote dependencies unless explicitly needed.

## Three-round verification gate

Before delivery, perform all three rounds:

1. **Structure:** confirm the file exists, starts as valid HTML, includes required controls/sections, and passes JavaScript syntax checking.
2. **Completeness:** parse embedded records and compare them to the authoritative source. Verify total records, set equality of stable IDs, counts by state, and a detailed description or explicit unidentified explanation for every record.
3. **Rendered:** open the file in a browser and inspect title, filters, grouping, representative detailed cards, expandable source context, and visible totals. Check the console when available.

Do not claim all records are captured based on a manually typed list alone. If the live CLI is unavailable, use a local scheduler export or other authoritative structured source and state that provenance in the artifact.

## Delivery

Save with a descriptive filename in an accessible absolute path. Send the file using the platform's native file/media attachment mechanism, not merely a textual path. Final response should include the path, contents summary, and concrete verification results.

## Pitfalls

- A blank prompt is missing source information and must be marked unknown.
- Historical backups can explain a former job but do not prove the current job’s purpose.
- Display symbolic delivery targets accurately rather than pretending to resolve them.
- Do not hide errors or paused state behind a polished UI.
- Do not report a browser-render check unless the artifact was actually opened.

See `references/cron-dashboard-session.md` for the reusable cron-inventory example and verification checklist.
