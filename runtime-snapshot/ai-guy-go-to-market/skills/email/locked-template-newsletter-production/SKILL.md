---
name: locked-template-newsletter-production
description: Use for locked-template newsletter production and QA.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [newsletter, locked-template, source-verification, html, qa]
    related_skills: [newsletter-pipeline, newsletter-creation-qa-guide, grounded-citations]
---

# Locked-Template Newsletter Production

Use when a publication says the design never changes and supplies a template, token guide, rules, brand constants, checklist, and example. Produce content substitution files, never a redesign or send.

## Inspect the kit

1. Extract into a dedicated working directory and inspect archive member names first. Cross-platform ZIPs may contain backslash-separated names. Use Python `zipfile`, normalize `\\` to `/`, and create parent directories.
2. Read the template, token contract, binding rules, brand constants, checklist, and complete example. Rules override prompt prose.
3. Enumerate `[[TOKEN]]` slots and distinguish them from merge tags such as `{{ MessageURL }}`. Confirm issue number, month, topics, and exclusions.

## Research with evidence

1. Choose current, operator-relevant stories. For finance, prefer official releases, regulators, central-bank data, SBA material, and credible trade reporting.
2. Open every exact source page in a real browser in the current session. Search snippets and HTTP output identify candidates but do not support article claims.
3. Maintain a ledger with URL, title, publisher, date, primary/secondary status, and verbatim evidence for every statistic or load-bearing claim.
4. If a primary page is inaccessible, label that fact and any secondary source in copy and handover notes. Never silently upgrade secondary reporting.
5. Never invent, estimate, round, or recall figures. Drop unsupported claims or flag the gap.

## Draft and build mechanically

1. Fill only declared slots. Preserve fixed copy, markup, whitespace, inline styles, merge tags, footer/legal text, hardcoded links, and entities.
2. Follow slot length rules and write for the actual audience. Keep native/house content within offer-discipline rules.
3. Use `PENDING-IMAGE-URL-N` when images are not hosted. Never invent URLs, use relative email paths, or call placeholder mode send-ready.
4. Write four visibly different image prompts, varying color, light/time, location, people, and framing. Ban legible text, logos, signage, screens, and readable paperwork.
5. Copy the template and perform deterministic substitution. Keep the HTML with image prompts, source table, QA output, and unresolved-items note.

## Verification gates

- No remaining `[[...]]` slots.
- Required merge tags retain exact counts.
- Style-attribute sets match the template in both directions.
- Required style/table/card/color invariants match.
- News source URLs appear where required, commonly twice per card.
- Offer link appears only in authorized placements.
- No banned phrases, residue, prohibited emojis, raw placeholders, or unsupported claims.
- HTML parses successfully.
- Image sources are hosted absolute HTTPS URLs or visibly marked placeholders; placeholders block send-readiness.
- No send, test-send, scheduling, or platform load without explicit authorization.

## Deliverables

Provide the filled HTML, `IMAGE-PROMPTS.md`, source ledger/evidence table, QA report, and unresolved-items note. In Slack, use native file attachments when available and do not claim an upload without a verifiable path or attachment.

## Publication workspace setup

When a locked-template publication needs a durable Obsidian workspace, scaffold a publication-level folder before issue production. Include a hub, publication identity, copy system, design lock, research/sourcing rules, image system, production instructions, QA/handoff rules, and README files for `issues/`, `research/`, `assets/`, and `archive/`. Copy the complete source kit into `assets/<kit-name>/`; a README pointer to a temporary work directory is insufficient. Preserve the template, QA script, reference issue, and reference images. Record the current issue brief, CTA, approval gate, and draft-only/no-send rule.

Run five setup checks before handoff: (1) inventory and paths, (2) Markdown headings/tags and local links, (3) publication-rule and brief consistency, (4) approval/no-send/source/image safeguards, and (5) final readability and kit completeness. Fix failures before reporting setup complete.

## Cross-platform archive pitfall

Python ZIP extraction may preserve Windows backslashes as literal characters on Linux. Inspect member names first, normalize `\\` to `/`, and create parent directories explicitly before writing files. This keeps the kit's intended hierarchy usable for later QA and browser rendering.

## References

See `references/cross-platform-zip-and-template-qa.md` for reusable extraction, substitution, evidence, and verification details.
