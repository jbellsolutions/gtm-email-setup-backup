# GrokBot → Hermes: working map

Two revenue engines, shared specialists, one controlled execution layer.

| Lane | What Hermes owns | What stays in existing tools |
|---|---|---|
| Cold email | Charter → sourced list → verified contact → custom copy → independent review → approved execution | Instantly mailboxes, sequences and delivery |
| Intent prospecting | Review buying signal → offer match → channel plan → conversation → CRM | Lead Radar discovery; approved email/social platforms |
| Dream 100 / 500 | Evidence scoring, relationship briefs and due-touch accountability | Justin writes messages; CRM records actual touches |
| Newsletters / SMTP | Reviewed drafts, eligible lists, release policy and health | Listmonk/SMTP delivery; optional Beehiiv flagship |

**The 32 → 22 math, in one line:** 32 source agents = 20 one-to-one keeps + 7 collapsed into `ops` (router, HoOps, ClickUp, Single Brain, Call Prep, legacy Campaign Manager, Content Accountability) + 2 collapsed into `linkedin` (Unipile + Outflo) + 2 dropped placeholders + 1 deferred peptide project. 20 + 1 + 1 = 22 profiles. The 10 group rooms are not agents at all — they become named queues and durable records: [room-mapping.csv](room-mapping.csv).

**What changes cost:** predictable API work runs as code (`no_agent` jobs — five daily KPI model wakes become one metrics snapshot); research and judgment use models; webhook-driven replies replace the banned 10-minute poll; one snapshot feeds all campaign metrics; every source run, paid pull and channel action carries a durable ID and a budget. The ask-another-agent-in-a-room pattern is retired: rooms become queues, answers become artifacts.

**Key corrections:** Dream playbook says briefs only. Lead Radar already has a hosted scheduler. Outflo is replies-only. Current source instructions conflict in 11 documented places and must be reconciled before porting (plan §"Conflicts to resolve").

**What else is in the fleet beyond agents+rooms:** 42 documented routines → 12 Hermes jobs ([map](routines-to-hermes-jobs.md)); 15 user skills → 6 port-first + defers ([map](skills-to-hermes-mapping.md)); ~40 MCP connectors of which ~15 are load-bearing; platform-managed skills replaced by Hermes jobs + Orgo browser seats.

**Next:** recover the 18 missing routine prompts from the live Routines panel → audit installed Hermes/Orgo → enrich the 22 role stubs with lane contracts → replay archived work → shadow one charter + the intent queue (Dream briefs read-only in parallel) → measure quality and all-in cost → controlled cutover after Justin's GO. Full double-check of done/missing/improved: [gap-audit-2026-10-07.md](gap-audit-2026-10-07.md). Jev workforce and Bops stay phase two.

Full evidence, workflow details, profile contracts, cost controls and acceptance gates: [migration plan](hermes-migration-plan.md). Lane-by-lane placement and cost-amplifier→fix table: [deep dive](deep-dive-32-to-22-reconciliation.md). Every source agent: [mapping CSV](agent-mapping.csv). Draft roles: `profile-specs/`.