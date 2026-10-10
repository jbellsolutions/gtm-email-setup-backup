# Routines → Hermes jobs: complete 42-entry map

Source: `../Grok Bot Backup 2026-10-07/ROUTINES-FULL-2026-10-07.md` (24 with recovered prompts, 18 known without). All source routines are PAUSED (Justin's stop, 2026-10-07 ~11:35am ET); several failed that morning because the paying Cursor account had an unpaid invoice. Nothing here is enabled; every job starts **disabled** with an explicit timezone (America/New_York) and one owner.

Hermes job types used below: `scheduled` (cron), `webhook` (event), `no_agent` (script only, no model). Rule: predictable metric/count work is `no_agent` code; models wake for judgment, research, writing and ambiguous replies — and only when the record says there is something to judge.

## A. Keep (12 jobs, most collapsed from 42)

| # | Source routine(s) | Owner profile | Hermes job | Trigger | Notes |
|---|---|---|---|---|---|
| 1 | `instantly-inbox-health-am` + `instantly-inbox-health-pm` + MWF warmup extras | deliverability | `instantly-health` (one job, 2 fires/day) | `no_agent` snapshot 08:00 & 18:00 ET, every day | Keep 7-day warmup discipline, 50% warm reply floor, interval/limit checks. Model wakes **only on breach** (warmup mass-off, bounce ≥1%, suspends) → ops digest. Never sends. |
| 2 | `smtp-and-sin-warmup` | deliverability | `smtp-health` | `no_agent` daily 08:00 ET | Bird + Resend warm checks (SendFox once connected, Sendy stays idle-legacy). FROM/bounce-visibility blockers stay open. |
| 3 | `instantly-reply-wakes-reply-agent` | instantly → replies | `instantly-reply-webhook` | `webhook` (Instantly `reply_received`) | Core event-driven reply ingestion. Dedupe on event ID; enqueue to `replies` queue; **never** flood ops with per-reply chatter. |
| 4 | `outflo-inbound-wake` | linkedin → replies | `outflo-reply-webhook` | `webhook` (Outflo/bridge Reply Received) | Replies-only doctrine. Same dedupe rules; Justin still owns all Outflo campaign changes. |
| 5 | `instantly-reply-attio` (B14) | replies → crm | `reply-to-crm` | queue consumer (from #3/#4) | Interested/lead_interested → CRM record via sole `crm` writer; idempotency key = contact + campaign + action + artifact version. No second webhook needed. |
| 6 | `weekday-vault-batch` | ops (knowledge service) | `vault-batch` | `no_agent` git pull + batched PR, 18:00 ET weekdays | ONE comprehensive EOD update (never mid-day drips); PR review-gated before merge; Notion mirror one-way. Absorbs `single-brain-weekday-steward`. |
| 7 | Social-intent radar (B1) + job-boards radar (B2) + affiliate pull (B3) | lead-radar | `radar-social` (weekdays), `radar-jobs` (Mondays), `radar-affiliates` (weekly) | `scheduled`; **one scheduler owner** — hosted Railway trigger vs Hermes, decided in the deployment audit | Discovery only; results → handoff queue for `revenue-prospector`. On ScrapeCreators 402 → report top-up need, don't retry. Do **not** recreate HoOps `lead-radar-daily` duplicate. |
| 8 | Daily KPI reports ×5 (B8–B12: AI Guy, RevPartners, Agency, Home Services, Influencer) | ops | `metrics-snapshot` | `no_agent` weekdays ~09:30 ET | **Five model wakes → zero.** Pulls one versioned Instantly/warehouse snapshot, computes all charter KPIs in code, writes one exception digest. This is the single biggest cost collapse in the migration. |
| 9 | Daily prospecting report (B7) | revenue-prospector | `prospecting-daily` | `scheduled` weekdays ~09:20 ET, fed by #8's snapshot | Lean: only new Lead Radar leads get model work (offer match + channel plan); silent when nothing changed. |
| 10 | Dream weekly refresh (B15) + daily batch (B16) | dream-partners | `dream-refresh` (Mon), `dream-briefs` (weekdays) | `scheduled` | **Briefs only** (playbook overrides the old 10–20 emails/day prompt). Scoring per 7-criteria rubric; touches logged only when real; writes via `crm`. |
| 11 | `newsletter-operator-daily` + `daily-beehiiv-one-thing-draft` | newsletter-smtp / newsletter-flagship | `newsletter-draft-pass` | `scheduled` weekdays, stage-only | Draft/scaffold from Justin's dumps only; no publish without greenlight. Optional in pilot (tier two). |
| 12 | `linkedin-operator-daily` | linkedin | `linkedin-daily-pass` | `scheduled` weekdays 09:16 ET | ONE Unipile Engage/Inbox pass; help-first; no invented posts; dashboard link to Justin only on change. |

## B. Replace with ops skills / services (not jobs)

| Source | Replacement |
|---|---|
| `email-ops-daily-machine` (HoOps) | Retire the "ask Instantly Operator for a one-liner" loop. Its monitoring intent is covered by #1 (health), #8 (metrics) and the ops exception digest. |
| ClickUp daily summary / stale chase (B17) | `no_agent` stale-task detection (>2 business days) → one batched write through the sole ClickUp adapter; exceptions to ops digest. Prospects never in ClickUp. |
| Attio daily CRM summary (B18) | `no_agent` stage-move/win/commission summary → ops digest. |
| Call Prep weekday sweep (B6) | `no_agent` calendar scan creates a call-prep task **only when a real external Power Partner Discovery call exists** → wakes the call-prep skill with CRM + approved offer facts. No daily sweep. |
| `content-accountability-daily` | Ops skill, on-demand; outside the core revenue pilot (P3 tier). Calendar + brief nudge only. |
| `weekday-send-calendar` | Legacy Campaign Manager seat. Dead lanes (GYMS, Charles MSP, PR conferences) do not return. The go/no-go pattern becomes the ops **campaign-control skill**; charter first-launch GOs stay Justin's. |

## C. Do not recreate (16)

- `lead-radar-daily` (HoOps duplicate of Lead Radar's own runs) — explicitly banned by source.
- `unibox-reply-poll-reply-agent` — the 10-minute poll (`*/10 7-21 * * 1-5` = up to **90 runs/weekday**). Banned under the credit lock; webhook #3 is the primary.
- `luma-operator-daily`, `social-operator-daily`, `unipile-dashboard-daily` — target agents already deleted (2026-09-30) or redundant with #12.
- `solar-dbd68956-bounce-watch`, `solar-esp-daily-while-active` — solar/open-door is paused; it survives only as a lead source for the Men's Health waterfall.
- `gym-eod-sent-vs-2000` — gym lane paused; do not treat 2,000/day as live.
- Peptide routines ×3 (`daily-lead-and-order-review`, `daily-source-freshness`, `weekly-payout-reconciliation`) — deferred with the peptide project (Connect Med dead).
- NZ drainage radar (B4) — client-specific; **ask Justin** whether it's still wanted before porting anything. Not core revenue.
- Beehiiv "one thing" daily scaffold — folded into #11 as optional; only active if Justin re-approves that cadence.

## Cost shape before → after

- **10/05 snapshot:** 11 of 24 on-disk routines were enabled; the 18 post-10/05 additions (5 daily KPI wakes, prospecting report, newsletter pass, dream daily batch, radar runs, etc.) were heading toward ~25–30 scheduled model wakes per weekday, each replaying room/group context.
- **Hermes target:** ~12 jobs; ~8 are `no_agent` or deterministic; only ~4 wake a model, and then on events/exceptions (webhook replies, offer-match for new intent leads, dream briefs, QC). Nothing wakes to recount unchanged state.
- The credit lock ("≤10%/day of weekly usage") becomes a real enforced budget: per-job cost reservations in config, spend ceilings in adapters, provider-credit stops, one daily metrics+cost snapshot feeding all-in unit economics (cost per accepted lead / qualified reply / booked call).