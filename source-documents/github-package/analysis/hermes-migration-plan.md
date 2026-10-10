# GrokBot → Hermes workforce: phase one analysis

Prepared October 7, 2026. Status: planning and draft profile specifications only. No installation, campaign activation, paid pull, outreach, SaaS write or production database change was performed.

## Recommendation

Preserve the business workflows and their charters. Replace GrokBot's routing, prompts, routines and computer dependency with Hermes profiles, versioned skills, bounded jobs and explicit tool adapters. Retain Instantly, Lead Radar, Data Box, the contact warehouse and existing channel services where they work. Use Orgo for a persistent Hermes runtime and the browser work that actually needs a desktop.

Separate three things: the profile owns a role; the model supplies judgment; the computer supplies execution. A profile is not a requirement for an always-running model loop or a dedicated computer. Open-source model quality and lower total cost must be demonstrated on your tasks before rollout.

Jev workforce and Bops remain phase two integration choices. The contracts below should travel to either implementation. No assessment of either repository or your existing Orgo installations has been made in this pass.

## What was examined, and what is established

- The split full-box archive was streamed for selected evidence without restoring its OS, credentials or browser state. Its SHA-256 was checked against the manifest.
- Recovered all 42 `profile.json` files: 32 agent entries and 10 rooms. Two agents are placeholders/retired duplicates; one is a dormant peptide project. The handoff counts 29 substantive specialist/leadership prompts plus the Grok router.
- Read the v2 handoff, routine inventory, TODO, recovered profile prompts, selected charters/samples, Dream criteria/playbook, Data Box operating notes, Lead Radar README/AGENTS/runbook, and available recent companion Markdown exports.
- There are 42 documented routine entries: 24 with recovered prompts and 18 reconstructed from notes. Some are disabled, duplicated, obsolete or potentially the same routine described twice. This is not a count of 42 active jobs.
- The snapshot states all fleet routines were paused at your request. Instantly snapshot: 0 active, 21 paused, 15 draft and 1 completed. These are October 7 backup facts, not live API observations.
- This is a workflow and migration analysis using backup evidence. Hosted services, API auth, current balances, code execution, mail delivery and model performance have not been re-tested.
- Recent chat exports are partial. For example, the HoOps export includes summaries; the companion archive has selected agents and partial transcript chunks. It does not close every recovery gap claimed in the handoff.

Evidence references: `../Grok Bot Backup 2026-10-07/HANDOFF-2026-10-07-v2.md` sections 2–7 and Appendix A; `ROUTINES-FULL-2026-10-07.md`; selected files in `evidence/`. Source directories are retained so every claim can be traced.

## The two revenue engines

### 1. Charter-driven cold email (tier one)

Justin's objective/charter → campaign owner → data pull → identity/dedupe/suppression → email verification → evidence research → custom copy → independent editorial review → Instantly draft/load → approved first launch → campaign execution → replies → CRM → booked calls, partners and attributable revenue.

Instantly remains the sending system and mailbox manager. Hermes should build, review, route and monitor work through it. Campaign goals are not instructions to reproduce a mail scheduler inside Hermes.

Shared components: Data Agent, List Manager, ESP, Writer, Editorial, Instantly Operator, Reply Agent, CRM. Each campaign owns its offer, audience, proof, calendar, inbox reservation and results. The five large internal campaign reservations total 800 inboxes in the planning targets: AI Guy 100, RevPartners 300, Agency 100, Home Services 200, Influencer 100. At the baseline 10/day this represents about 8,000 send capacity/day, not 8,000 new verified leads/day or evidence of actual sends. Provider-specific caps and risk holds change usable capacity.

| Campaign | Purpose | Behavior that must survive migration |
|---|---|---|
| AI Guy | Be their AI guy; open-source lease | Copy derives from Justin's frameworks; approved claims only |
| Agency | Recruit frontend agency partners | Backend lead generation / profit split; From-name signature convention |
| Revenue Partnerships | Niche revenue partners; Men's Health flagship | One charter per niche; waterfall source tracking and cooldown decisions |
| Home Services | Leads Mastermind then Revenue Partnerships | Sequential enrollment; prevent two active pitches to one person |
| Influencer | Creator sponsorships, collaborations and monetization | Audience filters and concrete proof assets before launch |
| Francois | Funding offers to credit/mortgage professionals | Separate client assets and identity; events only when requested |
| Affiliate recruitment | Find affiliates and list/audience owners | Distinct from selling creator monetization services; dedupe overlapping people |

These can be separate named Hermes profiles instantiated from a shared campaign-owner specification, without duplicating the entire pipeline or waking each one merely to recount metrics.

### 2. Intent and relationship prospecting

**Intent lane:** Lead Radar discovers a public buying signal → review actual quote/source and fit → Revenue Prospector matches the approved offer → Data resolves identity/contact where necessary → verified email and evidence-backed copy → dedicated `Lead Radar | <offer>` Instantly campaign, plus approved native-platform/LinkedIn actions → replies → CRM.

Lead Radar is discovery only. Its README and runbook already expose a hosted API, contact-card jobs and a Railway daily trigger. Hermes should initially consume results from that hosted instance. The local `scripts/radar_daily.sh` database is separate. Do not start both for the same offer/window. The one scheduler owner must be chosen from actual deployment state, since the fleet notes still describe local weekday routines.

The archived classifier has not passed its M3 gate: overall High precision about 0.69 and seller leakage 29%; reported non-job-ad precision is about 0.96. Job-listing precision and other offers remain unmeasured. These are historical evaluation results. A High label must not automatically trigger outreach; preserve a review outcome with rejection reasons and the original verdict unchanged.

**Dream lane:** discover audience owners/referral authorities → public-evidence scoring → Dream 100 or Dream 500 → recent-content research brief → due relationship action → Justin writes the message → log only actual touches → reply/meeting/partner tracking.

The concrete working playbook overrides the old profile prompt that called for 10–20 agent-written emails/day. It says **briefs only; Justin writes all messages**. Do not accidentally turn this into bulk cold email during migration. If you want a new drafting policy later, make that an explicit change.

Dream scoring: seven 0–5 criteria, weighted audience overlap 25, reach 15, engagement/trust 10, partner openness 15, reachability 10, warmth 10, strategic leverage 15. Total = sum(score × weight)/5.

- Dream 100: score ≥70 AND audience overlap ≥4; about 100 real whales, quality over filling a quota.
- Dream 500: generally 55–69 plus documented exceptions for strong reach/nurture; about 500 over time. No overlap with Dream 100.
- Unknowns remain unknown/low, with evidence and re-score date. High total with insufficient overlap requires review, not automatic whale admission.
- Working cadence: 3–5 genuine engagement touches over about two weeks, then Justin's DM, email about 3–5 days later if appropriate, fresh-value follow-ups every 7–10 days, 3–4 unanswered follow-ups then Not Now/90-day revisit.
- Only real completed touches update `last_touch`. CRM writes go through the sole CRM owner; prospects never become ClickUp tasks.

## Newsletter and SMTP lane (tier two)

Keep two different operational queues: SMTP/Listmonk campaigns and the flagship Beehiiv publication. They can share research/editorial capabilities but require separate audience eligibility, asset reservations, templates, release policy and outcomes. The backup mentions Sendy, Bird, Resend and SendFox too; inventory what is actually used before porting every legacy transport.

Listmonk owns subscriber/campaign delivery; Hermes stages content, resolves list readiness, respects a configured throttle and reports results. Beehiiv issues use Justin's ideas and remain release-controlled. The 1M inbox-delivered/day figure in the ESP prompt is a long-term aspiration, not a migration target.

Keep Instantly inboxes and sending assets out of Listmonk/Beehiiv/SMTP. Existing assumptions that every list is permissioned must not overwrite factual source or eligibility records. Preserve actual provenance and lane eligibility rather than turning a prompt assertion into data.

## Target Hermes profile organization

The complete 32-entry source mapping is in `agent-mapping.csv`. Draft role specifications are in `profile-specs/`; they are not installed Hermes profiles.

Recommended full scope: 22 named role/campaign profiles. Consolidate Grok router + HoOps + legacy calendar into Ops; make ClickUp reporting, knowledge stewardship, content reminders and call prep skills/services under Ops; merge Outflo/Unipile channel ownership into LinkedIn while preserving platform restrictions. Exclude placeholders, group rooms and dormant peptide work. Retain distinct Writer and Editorial responsibilities.

First pilot: Ops, Data, Lead Radar, List Manager, Deliverability, Writer, Editorial, Instantly, Revenue Prospector, Replies, CRM and Dream Partners, plus **one** campaign-owner profile. Optional affiliate, LinkedIn execution, SMTP and Beehiiv capabilities can be activated once the first lane proves itself. The pilot is a scoped workflow, not a demand to launch thirteen persistent processes.

Dream 100 and 500 should initially be queues in one `dream-partners` profile using the same rubric. Split into separate profiles later only if throughput or operator permissions justify it.

Profiles scope Hermes state: SOUL, config, secrets, memories, sessions and cron. They do **not** sandbox filesystem access or enforce SaaS permissions. See [Hermes profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles). Define OS/container access and scoped adapters separately. Do not put a full shared credential set into every profile.

## Adaptation contract

| GrokBot element | Hermes adaptation | Migration check |
|---|---|---|
| profile description | Reviewed `SOUL.md` role, plus concise policy references | Remove old agent IDs, dead offers and conflicting duties |
| agent memories | Curated `memories/MEMORY.md` and `USER.md` | Facts carry source/date; archive old chat rather than loading it all |
| user workflows | Profile-local `skills/<name>/SKILL.md` with scripts/references | Replace Grok tools/computerUse and absolute box paths |
| routines | Reviewed scheduled/event jobs | One owner; disabled initially; explicit timezone |
| group chats and handoff messages | Durable task records and artifact references | No dependency on room chat history |
| MCP/OAuth connectors | Hermes MCP/tool adapters or direct APIs | Reconnect and verify auth; backup did not preserve server grants |
| CSVs, lists and reports | Private evidence store + normalized contact/action records | Preserve IDs/source; suppressions survive |
| store.db/conversation blobs | Historical audit/search material | No assumption these import as Hermes sessions |
| box OS/browser | Selective Orgo setup and necessary authenticated browser seats | No wholesale filesystem/credential restore |

Hermes skills provide reusable procedures and scripts; review the existing six central email skills first: formatting, unused inbox pool, Overdeliver doctrine, referral-partner build, newsletter voice and Listmonk. Review Lead Radar's own portable skill. Grok-managed signing-in, routine and send-on-behalf skills are platform dependencies that need replacement, not omissions. See [Hermes skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/).

Proposed profile package after adaptation:

```text
profiles/<role>/
  SOUL.md
  config.yaml               # generated against the installed Hermes version
  memories/MEMORY.md        # curated stable facts
  memories/USER.md
  skills/<capability>/SKILL.md
  skills/<capability>/scripts/
  references/charters/      # versioned approved campaign briefs
```

Secrets, sessions and contact datasets stay outside a distributable package. Do not copy a Grok database or `profile.json` into Hermes and call it migrated. Create/import supported Hermes profiles after a version audit; profile creation/cloning may bring bundled skills and identity state that need review.

## Execution and handoff design

Use API/CLI work for predictable operations; use the model for intent judgment, offer matching, relevant research, custom writing and ambiguous replies. Use Orgo desktop/browser execution only for a platform action without a suitable API.

Each work item should carry: task ID, contact ID, campaign/charter version, source run/post ID, stage, assigned role, artifact reference, attempt count, cost reservation, deadline, approval reference and result. A proposed lifecycle:

`discovered → reviewed → enriched → verified → drafted → qc_passed → staged → approved → executed → replied → CRM_updated`

Also represent rejected, blocked, suppressed, not_now and failed. Do not force all leads through an email-only path: missing email can leave an approved native-channel action viable. Staging is not sending; acceptance by an API is not delivery; a drafted reply is not a completed touch.

For irreversible channel actions, record an idempotency key derived from contact + campaign + action + approved artifact version. Replayed webhook events must not resend or double-create CRM entities. Unsubscribes update shared suppression before other channel decisions. Stop-on-reply and cross-sequence rules must consult current state before execution.

Keep sole writer boundaries: Instantly adapter, CRM adapter, ClickUp adapter, and channel-specific send executors. Reply Agent chooses the text; the correct channel executor sends and records it. This resolves the archived contradiction between sole Instantly ownership and Reply Agent sending directly.

Model prompts are guidance, not enforcement. The adapter/queue must enforce spend ceilings, permitted actions, suppression, approval scope and asset locks. If an API has no per-role credential scopes, put its full key behind the one writer service rather than distributing it to research profiles.

## Orgo deployment considerations

Orgo supplies a persistent computer; Hermes supplies the agent runtime; model inference is a separate dependency. The official [Orgo introduction](https://docs.orgo.ai/introduction) documents API/CLI/MCP access and running agent software inside a computer. It does not establish that any chosen open-source model is capable of your workflow.

Start with existing Orgo capacity rather than one new computer per profile. Keep isolated browser sessions for distinct accounts; serialize actions that share a browser/desktop. Split heavier research or separate client credentials later if measurements justify it.

The [Orgo Hermes guide](https://docs.orgo.ai/guides/hermes) documents an 8GB Hermes template, an environment without systemd and special gateway supervision requirements. It also says there is no public inbound computer hostname and its Desktop API proxy cannot forward Hermes gateway webhooks. Therefore Instantly/Outflo callbacks need a reachable authenticated receiver, durable deduplicating queue, and an outbound consumer on Orgo, unless your existing setup already has a verified ingress bridge. The bridge is proposed work, not a built-in migration result.

Hermes supports scheduled jobs, webhook-triggered jobs and script-only `no_agent` jobs. Use the latter for metric snapshots and predictable scheduled scripts; configure the runtime that actually executes them. See [Hermes scheduled tasks](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron). Avoid two schedulers managing the same source or job.

Open-source inference can be hosted behind a compatible endpoint rather than on the desktop VM. Audit your chosen endpoint, tool calling, context, structured output and any vision needs. Hermes documents custom endpoint configuration in its [configuration guide](https://hermes-agent.nousresearch.com/docs/user-guide/configuration). Orgo desktop RAM alone does not prove adequate inference throughput or economical hosting.

## Cost diagnosis and control

No invoice, token ledger or per-model pricing record was analyzed. We cannot attribute the one-day bill or promise a savings percentage. The backup establishes plausible amplification mechanisms:

1. The Writer prompt allows as many parallel research/writing subagents as needed, with fully custom research per record. Concurrency and per-lead depth need explicit limits.
2. Many daily KPI agents can wake shared operators for the same inventory. Cache one versioned snapshot and produce metrics in code.
3. Lead Radar's hosted schedule overlaps local/HoOps routine descriptions. Verify real run IDs to measure duplication before deleting/replacing schedules.
4. The legacy safety-poll expression would produce 90 polls per weekday during its 7–21 inclusive hours if enabled. It was disabled and later banned; it is not evidence of 90 actual model wakes today.
5. Multi-channel discovery and enrichment can repeat across Dream, Influencer, Agency, affiliate recruitment and intent prospecting without durable identity and evidence caching.
6. Group-room coordination and repeated status turns add possible overhead. The archive alone does not measure it.

Controls: dollar/credit reservations shared across the fleet; per-run/lead caps; bounded concurrency/retries; stop on provider credit errors; cached research with timestamps; refresh only stale evidence; event-driven replies; one daily metric collector and exception digest; idle jobs do no LLM work. Keep paid data preflight and execution separately metered: Data Box planning itself can spend credits.

Treat the old “10% of weekly usage/day” instruction as historical. It is not an enforceable dollar ceiling until a total budget and accounting period are defined. The historical $10/pull stop remains a policy input to reconcile with approved prepaid-provider allowances; do not copy conflicting limits into different profiles.

Track at least:

- model tokens and dollars, by role/task/retry;
- source/provider credits and verification cost;
- Orgo computer cost and separately hosted inference;
- accepted verified lead count and false-positive rejection rate;
- approved custom-copy count, factual-error rate and rewrite rate;
- real sends/delivery, qualified replies, booked calls, signed partners and revenue.

All-in cost per accepted lead = attributable operating cost / accepted leads. Cost per qualified reply and per booked call use the same principle. Report fixed subscription costs separately from marginal usage, then include both in total unit economics. Compare both task quality and business outcomes with GrokBot.

## Conflicts to resolve before enabling jobs

| Evidence conflict | Proposed migration behavior |
|---|---|
| Dream old prompt drafts emails; criteria/playbook says no pitches | Briefs only; retain a recorded conflict and source references |
| Lead Radar old prompt contacts leads; later routine/runbook is discovery only | Radar discovery only; Revenue Prospector owns follow-on planning |
| Railway hosted trigger vs fleet local routines | One production scheduler after deployment audit |
| Outflo old prompt/prospecting handoff changes campaigns; current doctrine replies-only | Stage LinkedIn target artifacts; campaign changes stay owner-managed |
| GetLeads five-search trial cap vs October 7 unlimited/fair-use note | Fetch current plan and counters; don't hardcode either historical number |
| Data Box provider catalog vs “not wired” operating brief | Probe each capability; direct-provider adapters remain explicit |
| “Every list permissioned” assertion vs missing actual provenance | Record source and actual lane eligibility; do not fabricate status |
| ESP owns SMTP but Instantly health duties route through Operator | ESP sets policy; sole Instantly owner supplies snapshots and applies changes |
| Reply Agent direct sends vs sole platform writer rules | Replies produce approved action; executor sends exactly once |
| Old Connect Med/solar/gym routines vs retired/paused lanes | Do not revive them during migration |
| 24 disk enabled flags vs October 7 global stop | Import definitions disabled; none are resume authorization |

The recent companion HoOps summary says a campaign or channel needs first-launch GO only once; other summaries retain replies-only Outflo restrictions. Recover exact permissions before granting ongoing native-channel execution. This phase-one request authorizes analysis, not launch.

## Ordered migration plan and acceptance gates

### A. Finish recoverable inventory

Already done: checksum, selected evidence extraction, 42-folder roster, 32-source-agent mapping and initial profile specifications. Remaining: exact missing routine definitions, partial recent chats, current campaign charter/proof versions, current inbox/domain reservations and your installed Orgo profile/runtime inventory. Keep uncertainties explicit rather than inventing missing routines.

### B. Audit the existing Hermes/Orgo installations

Record installed version/commit, profile list, configs without secret values, skill inventory, model endpoints, running jobs, browser identity and supervision. Back up profile state before adaptation. Map existing seats to the proposed roles; avoid overwriting working profiles. Verify a reachable reply receiver and restart behavior. Choose the production Lead Radar scheduler once.

### C. Adapt a small core package

Port reviewed role prompts into SOUL and shared operating skills. Start with read-only tools and staging outputs. Add typed tool contracts for Data Box, direct approved data providers, Lead Radar, verification, Instantly, CRM and ClickUp. Implement contact identity, suppression, artifact-version approvals, inbox/domain reservations, cost accounting and idempotent jobs before enabling writers.

### D. Replay representative archived work

Suggested initial evaluation set: 30 cold-email contacts across the intended first charter, 30 intent records including sellers/job relays, 10 Dream research subjects across tiers, and 20 reply threads covering interest, question, OOO, unsubscribe, wrong-person, soft-no and escalation. Private contact data remains private. Choose examples blind enough that models cannot merely reproduce the reference copy.

Compare candidate open-source models with the archived workflow and human review: correct offer, source-backed personalization, missing-data handling, usable tools, formatting, suppression and action-boundary compliance. Record cost, latency and retries. Hard failures include invented claims, unauthorized actions, double sends, suppression misses and changed source verdicts. Report quality distributions; averages alone hide harmful mistakes. Separate writer and editor sessions and avoid treating agreement as proof of factual truth.

### E. Shadow one end-to-end lane

Run one chosen Instantly charter and one intent queue to draft/stage only. Run Dream as briefs-only alongside it. A proposed readiness gate is five business days of complete artifacts and trustworthy cost records, with zero unauthorized actions and no duplicated runs/writes. Thresholds are proposed, not proven business benchmarks. Capture the exact list count, sender pool, approved samples and blockers for review.

### F. Controlled cutover after launch authorization

Activate only the reviewed campaign/channel, with the existing campaign first-GO and batch policies preserved. Keep provider-owned sequences where they are. Validate webhook delivery/replay and measured human review before expanding to other charters. Keep old fleet paused. Rollback pauses new schedulers/consumers, freezes pending sends and reconciles action state before any former runtime is re-enabled; never run both writers during rollback.

### G. Phase two: Jev workforce versus Bops

Evaluate both repositories against the same role, task, approval, spend and artifact contracts. Determine where each already has queueing, UI, identity, CRM, budget and deployment capabilities. Jev already appears in the archived Lead Radar/Data Box decision layers; this does not establish anything about the separate Jev workforce repository. Bops was not inspected. Decide the control surface after the Hermes pilot demonstrates quality and unit economics.

## Concrete launch blockers in the snapshot

Preserve these as dated blockers, then recheck live before execution: missing postal footer information; DNS/seed/placement checks; four DBL-listed domains and shared-domain risks; verification of creator contacts rather than trusting provider flags; unresolved creator proof/ICP; Men's Health waterfall cooldown and pool decisions; Lead Radar classifier failures; incomplete routines; authentication grants not backed up. The archive contains live secrets, so the selected planning package must be reviewed before any publication or Git distribution.

## Next working session

Audit your existing Orgo/Hermes profiles and adapt **one charter plus the intent queue** to the core contracts. The first target should be a charter with complete offer/proof and healthy reserved sending assets; the backup alone cannot select a live-ready winner. Dream briefs can be ported in parallel as a read-only research workflow. Defer Jev/Bops implementation choice until the pilot measures quality and cost.
