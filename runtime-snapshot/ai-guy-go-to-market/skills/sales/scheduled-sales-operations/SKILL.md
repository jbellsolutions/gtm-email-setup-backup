---
name: scheduled-sales-operations
description: "Use for unattended sales-ops cron monitoring and prep."
version: 1.0.0
author: hermes-curator
metadata:
  hermes:
    tags: [Sales, Cron, legacy email platform, Cal.com, Pre-Call]
---

# Scheduled Sales Operations

Use this class-level workflow for unattended sales-operations runs that combine inbox monitoring, reply handling, calendar verification, and pre-call report maintenance.

## Core workflow

1. **Load governing domain skills first.** Use the legacy email platform/owned-audiences instructions for replies and pre-call-report for calendar prep. Do not invent a parallel classifier or calendar parser when a canonical script exists.
2. **Run a provider health gate before inbox work.** For legacy email platform, query the REST campaigns endpoint with the configured API key. Treat both `Plan expired!` and `Invalid API Key` as outage states. A zero-entry inbox is not evidence of an empty inbox unless the health gate passed.
3. **Separate dependent and independent work.** If legacy email platform is down, stop Part A: do not classify, draft, send, or mutate reply state. Continue Part B independently: Cal.com checks, report generation/refresh, and outage reporting.
4. **Run the canonical Cal.com triple-endpoint check first.** Pull `upcoming`, `cancelled`, and `past`; use live API as authoritative and `/tmp/cal_bookings.json` only as a supplement. Filter internal meetings. Convert UTC timestamps explicitly; never read raw UTC hours as local time.
5. **Deduplicate reports by attendee email and existing report content, not only directory name.** Derive canonical slugs from the company domain or, for Gmail/personal bookings, the email handle. Check all existing `clients/*/pre-call-report.md` files before creating a directory.
6. **Create or refresh reports in the exact pre-call format.** Include meeting URL, game-plan status, morning-of confirmation, and open items. Prioritize same-day/tomorrow calls. Refresh stale relative phrases such as “N days out.”
7. **Flag conflicts prominently.** If research reveals overlap with SpeakerAgent or another offer, pause the pitch/game-plan framing and surface the partner/competitor/client decision tree.
8. **Verify artifacts after writes.** Confirm each expected report exists at its slug-based path and spot-check headers/logistics. Never claim a report was created without a filesystem check.
9. **Report the outcome directly.** Include provider outages, report paths, refreshed reports, upcoming calls, and unresolved flags. Emit `[SILENT]` only when there is genuinely no new operational information.
10. **For Instantly inbox cron runs, treat the daemon summary as the source of truth only after a successful completion marker.** If the daemon crashes before `__SUMMARY__`, investigate the live payload shape, preserve the unread items, fix or rerun the parser, and report the failure rather than treating it as zero activity. See `references/instantly-daemon-live-payload-fix.md`.
11. **For Instantly daily reports, validate every response shape and pagination page before aggregating.** `campaigns` and `accounts` use `data.items`, while `campaigns/analytics` may use a list under `data`; `/emails` can mix sent and inbound records. Filter inbound records using verified direction evidence, not an over-broad `ue_type` assumption: the live payload showed `ue_type == 2` for inbound replies and `ue_type == 3` for an outbound/operator follow-up. Also exclude connected sending-account addresses, use `body.text`/`body.html`, strip quotes, and distinguish daemon-processed IDs from actual SENT follow-up evidence. See `references/instantly-daily-report-probe-2026-08-06.md`.
12. **For direct Instantly daemon execution, make the runner self-contained and test the real entry point.** A scheduled invocation may not inherit the gateway environment, so load the configured API credential through the approved local environment mechanism before constructing API headers. After changes, run the exact `--once` command, require a `__SUMMARY__` marker, verify sent/operator records are not classified as lead replies, and confirm state deduplication on a second run. See `references/instantly-daemon-live-payload-fix.md`.

## Instantly reply monitoring: cadence, direction, and send verification

- For the configured reply-monitoring window, use a 30-minute schedule (`*/30 8-18 * * *`) unless the operator specifies a different timezone or end boundary. The job should pull inbound replies, draft for approval, and never auto-send without explicit approval.
- This monitor is an inbox-reply monitor, not a general sales-ops reporting job. Do not include pre-call reports, calendar reports, analytics summaries, or unrelated operational reports when the operator asks for cold-email reply monitoring.
- Deliver cron output to the operator's main Slack channel when requested, not the originating thread. Use the explicit `slack:<channel_id>` destination and verify the job configuration after updating it. **Never use Composio, any MCP Slack connector, or any third-party Slack integration for delivery — Hermes has native Slack delivery built into the gateway and cron scheduler. A `token_revoked` Composio connection means the wrong delivery path was chosen, not that Slack is unavailable.**
- Scan a bounded recent paginated `/emails` window and use local processed-message state for deduplication. Do not rely only on `i_status=1`/`is_unread`: a prospect reply may be marked read in Instantly before the cron sees it, causing silent misses. **Follow every `next_starting_after` cursor until it is null; never stop pagination because a page has fewer than the limit — Instantly can return a short page while another cursor page still exists. This was a confirmed root cause of silently dropped replies (2026-08-12).** Unbounded historical pagination can also starve current replies and trigger rate limits, so cap at a reasonable recent-window page count (10 pages).
- `GET /emails` can include inbound prospect replies and outbound/operator records. Filter using sender direction plus connected sending-account exclusion. Live payloads have shown `ue_type == 2` for inbound replies and `ue_type == 3` for inbound follow-ups, so do not hard-code `ue_type == 2` as the only inbound value; never classify records sent from a connected sending account.
- Normalize `body.text` first, fall back to `body.html`, decode HTML entities, strip HTML, and remove quoted original content before classification. Read `from_address_email` for the prospect address; do not assume legacy email platform field names.
- Emit every newly discovered inbound reply to the channel, regardless of classification (positive, referral, neutral, OOO, unsubscribe, hostile, or dead). Positive/referral replies get approval-gated drafts; never auto-send from the unattended monitor.
- When replying, use the original sending account from the inbound record's `eaccount` field. Do not derive the sending account from `to_address_email_list`, which may include both the sender and the prospect and can cause `Email account not found` errors.
- After each approved send, verify the returned Instantly message ID and re-query the thread when possible. A successful `POST /emails/reply` response plus a distinct outbound record is the required evidence that the message was sent.
- Native Instantly “checked”/tag mutation is not part of the verified workflow. Local message-ID state is processing deduplication, not proof that an Instantly tag was applied. Never claim a platform tag was set unless the mutation endpoint and response are verified.
- Respect Instantly's 20-requests-per-minute limit with retry/backoff and pagination throttling. A 429 is not an empty inbox: preserve state, do not mark records processed, require a final `__SUMMARY__` completion marker, and report the scan as incomplete rather than emitting a definitive zero or complete list.

See `references/instantly-inbox-monitoring-runbook.md` for the live-payload, deduplication, delivery, and rate-limit checklist.

## Instantly weekly reply reconciliation

For retrospective missing-reply sweeps, use `references/instantly-weekly-reply-reconciliation.md`. It documents full `/accounts` and `/emails` cursor pagination, the 269-account discovery lesson, client-side thread filtering, `ue_type` direction handling, Notion/Obsidian archival, conservative triage, and the verified reply payload requiring `reply_to_uuid`, `eaccount`, `subject`, and both text/HTML body fields.

## Instantly reply-daemon monitoring

- `GET /emails` can return both inbound replies and sent messages. Filter to inbound records using the verified `ue_type == 2` and `ue_type == 3` markers before classification; `ue_type == 1` is a sent message and must not be drafted against.
- Normalize the live payload before text processing: `body` may be an object with `text` and/or `html`, not a string. Prefer `body.text`, fall back to `body.html`, then strip HTML and quoted content as appropriate.
- Use `from_address_email` as the sender field. Do not assume legacy email platform-style `from_email` or a string body.
- **Classification guardrails for OOO replies (confirmed missing patterns Aug 12, 2026):** the daemon's embedded `classify()` must detect OOO language BEFORE running positive-interest patterns. Missing patterns caused a false-positive draft on an OOO auto-reply. Required OOO signals: `ooo`, `o.o.o`, `limited internet access`, `limited access to email`, `limited bandwidth`, `currently out`, `slow to respond`, `will be slow to respond`. Employee-departure notices (`no longer a … employee`) and `automated reply` text must classify as `dead`, not neutral. See `references/instantly-daemon-classification-fixes.md`.
- **Positive-interest patterns for discursive replies (Aug 12, 2026):** some prospects express interest without using short command phrases. The classifier must catch `approach you described is interesting`, `approach is interesting`, and `especially as we continue` as `positive_interested` signals. A reply like "The partner-referral approach you described is interesting, especially as we continue expanding…" is a genuine positive, not neutral.
- A clean no-reply run is `[SILENT]`; a run with new replies, generated drafts, a parser failure, or a delivery blocker is reportable. Drafts remain approval-gated and must never be auto-sent.
- **Historical-reply reconciliation must be evidence-first:** when an operator asks to “grab all” replies or references a prior verification run, perform a fresh complete paginated scan and report the live count and every record from that scan. Do not reconstruct the roster from a partial cached JSON snapshot, prior Slack text, or daemon state; those artifacts may contain only one page or a different campaign. If rate limiting or pagination prevents a complete scan, stop and label the result incomplete rather than claiming all replies were retrieved.
- **Do not claim a draft or send exists without a live artifact.** A positive classification in an old report is not proof that a current draft was generated, and a solar-template rendering is not proof that it was posted or sent. Show the actual draft generated in the current run, and reserve “sent/posted” for a verified outbound ID or native delivery evidence. For the solar campaign, ordinary affirmatives may use the approved auto-send exception only after every hard-stop check; a discursive reply such as “I am interested in hearing more” remains approval-gated unless it exactly qualifies under the solar exception.
- **Do not save drafts to a sidecar JSON file** (`/tmp/instantly_reply_drafts.json`). Drafts must be printed inline in the daemon output so the Hermes cron agent delivers them directly to the Slack channel. The operator cannot see a JSON file on disk.
- If Slack delivery fails, use the native Hermes cron deliver target (`slack:<channel_id>`), never Composio or MCP. Report blockers inline.


## legacy email platform outage behavior

- `Invalid API Key` is an authentication/key-rotation problem, distinct from `Plan expired!` billing/plan expiry. Report the exact state and recovery owner.
- A CLI `Authentication failed` message is not sufficient to identify the cause: run the documented health probe and preserve the raw HTTP status/body. Do not silently convert an auth/transport failure into an empty inbox.
- Do not run the reply classifier, add message IDs, generate drafts, or send replies during an API outage. Preserving state is safer than treating the outage as “no replies.”
- Calendar and pre-call operations remain actionable while legacy email platform is down; mark thread-derived sections unavailable rather than guessing.

## Daily campaign-stat reporting

- For Instantly campaign reviews, explain the dashboard using separate fields: `emails_sent_count`/`contacted_count` = messages sent or contacts reached; `reply_count_unique` = unique prospect replies; `reply_count_automatic_unique` = automatic replies such as OOO or ticket acknowledgments; `completed_count` = leads that reached sequence completion, not replies. Never equate “completed” with “responded.” See `references/instantly-campaign-stats-interpretation.md` for the verified live example.
- Always distinguish cumulative campaign totals from current-day activity. Analytics totals are cumulative; current-day sends/replies require message-level timestamps and direction filtering. If the current-day result comes from a bounded `/emails` scan, label it observed rather than exact unless the provider supplied a date-filtered metric.
- An active campaign can have a lower actual send count than its daily limit. The daily limit is a ceiling, not a promise; report the observed send count and inspect schedule, start date, eligible leads, account capacity, and sequence delays before claiming a sending failure.
- For Instantly, classify inbound records only after direction filtering (`ue_type` 2/3 observed inbound; `ue_type` 1 observed outbound) and sender/account checks. Automatic OOO and ticket-system messages must remain visible but must not be presented as genuine prospect engagement.
- When a user asks why “nothing is happening,” provide a per-campaign reconciliation table first, then explain status vocabulary and identify the next actionable reply. Do not infer zero activity from a dashboard label or from a failed/partial API response.
- Treat daily analytics, campaign statistics, and reply-history pulls as provider-dependent facts. If the legacy email platform health gate or either required data pull fails, report `metrics unavailable` with the exact failure state; do not infer `0` sends/replies from a stopped campaign, stale cached campaign metadata, or an empty failed response.
- Never emit `[SILENT]` merely because a failed API call returned no rows. `[SILENT]` requires a successful current-day check showing no new activity.
- If the campaign is stopped and the provider query succeeds, report verified zeros for today and distinguish them from lifetime totals. If the provider query fails, include the last known campaign status only as context, not as today’s statistics.
- Positive-reply rate is undefined when total sent is zero; render it as `N/A` rather than `0%`, unless the reporting contract explicitly requires a zero convention.
- Keep the final outage note concise and operational: endpoint/tool attempted, exact error, and owner/action needed for recovery. Do not fabricate a Slack-formatted stats block with guessed numbers.

## Calendar/report quality rules

- Use the bundled triple-endpoint checker before ad-hoc curl/parser code.
- Keep SpeakerAgent Beta reports separate from AI Integraterz reports: SpeakerAgent calls should be framed around Scout Run, persona setup, voice samples, and podcast opportunities, not the $10/hour AI-operator offer unless the lead explicitly pivots.
- Direct bookings with no thread should say so plainly and use discovery-first language. Unknown business identity, authority, audience size, or ad footprint belongs in Open Items.
- Refresh existing reports in place; do not duplicate person-name and business-name slug variants.

## Instantly follow-up cadence checks

When the scheduled job targets Instantly, use REST-only inspection across every campaign. Do not run `/opt/data/scripts/followup_engine.py` or read/write `/tmp/speakeragent_followups.json` and `/tmp/owned_audiences_followups.json`; those are legacy email platform-specific and can create cross-platform sends. Enumerate campaigns, inspect native sequence delays and `stop_on_reply`, paginate leads with `POST /leads/list`, and inspect `/emails` records with client-side campaign and `ue_type` filtering. Treat any inbound reply, including a signature-only or unclear body, as a stop condition when `stop_on_reply` is enabled. If the native sequence owns the next touch or the campaign has not reached the manual threshold, report zero manual follow-ups due. Never call `POST /emails/reply` from an unattended cadence check; drafts remain approval-gated. Use `references/instantly-followup-cadence-check.md` for the verified payload observations, pagination behavior, and 20-request/minute rate-limit handling.

## Campaign-specific Instantly response routing

- When the operator names a campaign and asks for “all responses,” perform a fresh, campaign-filtered `/emails` scan and include **every inbound response**, not only positive/actionable replies. Preserve automatic acknowledgments, empty-body responses, ticket-system replies, unsubscribes, OOO messages, and negative replies, clearly labeled by classification.
- Use the exact live campaign UUID, not a name substring or stale cached campaign file. Confirm the campaign name/ID mapping from the live campaign response or a verified live record before reporting.
- Normalize and quote-strip each response, but do not over-summarize away the actual reply text. Include sender, timestamp, subject, and the cleaned body; use the lead/company fields only when present and verified.
- For a scheduled monitor, use a bounded cursor-paginated `/emails` scan with 429 backoff and a campaign-specific local message-ID state. Do not rely on unread status or a prior report as the historical roster.
- A direct-delivery watchdog must be tested against the real destination and must not silently lose records when delivery fails. Prefer a native Hermes `slack:<channel_id>:<thread_ts>` cron destination. If a script checkpoints records, do so only under a documented idempotency strategy; marking records before the scheduler confirms delivery can permanently suppress a response after a transient failure.
- Thread-targeted delivery requires the exact Slack channel ID and thread timestamp supplied by the operator. Verify the resulting cron configuration and run a controlled test before claiming future routing is active. See `references/instantly-campaign-response-routing.md`.

## References

- `references/instantly-campaign-response-routing.md` — campaign-only historical sweep, all-classification inclusion, exact UUID/thread routing, direct-delivery deduplication, and the verified Charles MSP example.
- `references/provider-outage-and-calendar-runbook.md` — tested outage classification, independent Part B procedure, and artifact verification checklist.
- `references/instantly-followup-cadence-check.md` — REST-only Instantly cadence workflow, stop-condition handling, payload quirks, and rate-limit recovery.
- `references/instantly-daemon-classification-fixes.md` — 2026-08-12: OOO classification patterns, positive-interest patterns for discursive replies, employee-departure detection, cursor-only pagination fix, Composio ban, and draft-inline delivery. Patches applied to `instantly_reply_daemon.py`.
- `references/solar-template-routing-gate.md` — exact campaign/record verification required before using the authorized solar auto-reply exception; includes the Mike Munter routing incident.
- `references/solar-sweep-and-routing.md` — solar-only campaign gate, no-neutral routing, complete pagination, operational exclusions, and pending-response verification.
- `references/revenue-partner-crm-inventory.md` — source-union inventory, deduplication, evidence-to-stage mapping, credential privacy gate, and read-before-write verification for Revenue Partner CRM migrations.
