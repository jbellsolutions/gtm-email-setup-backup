# Cloud agent handoff

## Objective

Continue the GrokBot → Hermes migration using the preserved working map and evidence. Build a controlled runtime that keeps the proven workflows, removes redundant coordination/model wakes, and measures quality and total cost. This handoff is for the next implementation agent; no deployment was performed while preparing the archive.

## Read in this order

1. [Working map](../analysis/working-map.md).
2. [Deep reconciliation](../analysis/deep-dive-32-to-22-reconciliation.md), [agent mapping](../analysis/agent-mapping.csv), and [room mapping](../analysis/room-mapping.csv).
3. [Gap audit](../analysis/gap-audit-2026-10-07.md).
4. [Full migration plan](../analysis/hermes-migration-plan.md).
5. [Routine map](../analysis/routines-to-hermes-jobs.md), [skill map](../analysis/skills-to-hermes-mapping.md), and [draft roles](../analysis/profile-specs/).
6. [Source v2 handoff](../Grok%20Bot%20Backup%202026-10-07/HANDOFF-2026-10-07-v2.md), [TODO](../Grok%20Bot%20Backup%202026-10-07/TODO-2026-10-07.md), and [routine inventory](../Grok%20Bot%20Backup%202026-10-07/ROUTINES-FULL-2026-10-07.md).
7. [Conversation coverage](../provenance/chat-coverage.json), [Cloudroom histories](../history/cloudroom/), and [GrokBot histories](../history/grokbot/). Fetch the recovery release only when deeper evidence is needed.

## What you have

All locally available analysis documents and selected evidence; sanitized original handoff/TODO Word files; recovered archive Markdown and primary fleet specs; three available Cloudroom thread snapshots; agent database transcript exports; larger sanitized data/code/transcript evidence in the private recovery release. See the inventory for exact paths and exclusions.

The role specifications are drafts. This repo has no executable application, Docker image, deployed API, operational webhook bridge, configured Hermes fleet, or production credentials. Do not label the package cloud-ready software. It is ready for a cloud implementation agent to clone and continue.

## First session: establish actual state

- Clone and run `python3 scripts/check_package.py`.
- Audit the chosen cloud computer: Hermes/Orgo versions, installed profiles, existing jobs, supervision, memory/disk, browser seats and ingress constraints. Use the destination's current official documentation before generating runtime configuration.
- Inspect existing source service repos with authorized GitHub access: [Lead Radar](https://github.com/jbellsolutions/lead-radar), [Data Box](https://github.com/jbellsolutions/data-box). The archived copies are evidence, not proof of current default branches or health.
- Check the hosted Lead Radar scheduler and local cron read-only. Choose one owner per offer/window; do not duplicate scheduling.
- Request scoped credentials through the cloud environment's secret mechanism. Never retrieve credentials by loading the raw backup into model context.
- Record missing source access: 18 routine prompts, incomplete recent chats, unavailable Cloudroom predecessor, cost invoices, and live campaign/list/suppression state. Do useful independent implementation while access is resolved.

## Implement in order

1. **Contracts and artifacts.** Contact identity, provenance, suppression, charter versions, task stages, approvals, reservations, spend ceilings, and durable idempotency records. Keep source verdicts intact.
2. **Queue and adapters.** Enforce sole writers for Instantly, Attio and ClickUp in code. Reply judgment produces text; the channel executor sends exactly once. Review current contact state and suppression before any action.
3. **Role definitions.** Enrich the 22 role drafts with lane contracts; generate supported SOUL/config/skills only after the version audit. A profile is not a security boundary or a requirement for a dedicated computer.
4. **Skills.** Port the six core skills and Lead Radar skill identified in the skill map. Replace old absolute paths and Grok-only tools. Keep disabled/retired work out of the active set.
5. **Jobs and metrics.** Create the reviewed job skeleton with all jobs disabled and explicit timezones. Prefer deterministic snapshots and event-driven replies over repeated idle model wakes.
6. **Webhooks.** If needed, build a reachable authenticated receiver plus durable dedupe queue and outbound consumer. Verify actual Orgo ingress support; do not assume the desktop proxy forwards gateway callbacks.
7. **Replay.** Use the migration plan's historical replay gate: 30 cold contacts, 30 intent records, 10 Dream subjects and 20 reply threads. Measure correctness, suppression, artifact traceability, idempotency and spend.
8. **Shadow.** One charter plus intent queue, Dream briefs read-only, five-day shadow gate. Report observed quality and total cost; do not claim savings from structural estimates alone.
9. **Cutover.** Prepare a concrete reviewed rollout and rollback. First-launch GOs and the fleet pause require Justin's explicit release; database mutations require separate approval.

## Policies that must survive

- Preserve draft/stage-only migration and the current pause.
- Dream 100/500: briefs only; Justin writes messages.
- Outflo: replies only; Justin controls campaign changes.
- First launch: one scoped GO per campaign; newsletter release is separately controlled.
- Writer and Editorial remain independent.
- Instantly sending assets stay separate from SMTP/Listmonk/Beehiiv assets.
- Suppressions and cross-lane dedupe precede execution; only real touches update `last_touch`.
- Never invent proof, consent, contact identities or completed work. Preserve the source ban on “no upfront cost.”
- Deliverability holds and missing required launch inputs remain blocking; 800 reserved inboxes / ~8,000 daily capacity are historical planning figures, not live sends.

## Done means

A version-audited runtime, reviewed role/skill contracts, disabled jobs, enforced writer/approval/spend/suppression boundaries, a verified webhook path where required, passing replay evidence, measured shadow outcomes and a reviewed rollback. A clone, a collection of prompts, or 22 running processes alone does not satisfy the migration.

## Prompt to give the next agent

> Continue from the private repo https://github.com/jbellsolutions/grokbot-hermes-migration. Read AGENTS.md, docs/CLOUD_AGENT_HANDOFF.md, analysis/working-map.md, analysis/gap-audit-2026-10-07.md and the migration plan. Verify the archive, audit the actual cloud Hermes/Orgo runtime, then implement the queue, scoped adapters, role/skill contracts and disabled job skeleton. Preserve existing pause, campaign GOs, Dream briefs-only, Outflo replies-only, sole writers, suppression and budgets. Recover missing evidence where access permits; do not invent it. Use replay and five-day shadow gates before proposing cutover. No production sends or database writes are authorized by this handoff. Record what you changed, what you verified, and what needs Justin's decision.
