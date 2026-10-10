# Combined Part A + Part B Cron Workflow

The `Instantly-auto-reply` cron (job ID `2929988f4269`) runs two phases in sequence:

## Phase A: Inbox Reply Monitoring (always runs first)

1. **Pull Instantly inbox** — pages 0-1 minimum (40 entries, 2 API calls). Continue until empty page or entries older than 48h.
2. **Group by campaign** — `email_campaign_id` field. Inbox is shared across ALL campaigns (#3617053, #3639259, #3577260, #3520103, #3607306).
3. **Pre-filter auto-responders** — `support@`, `info@`, `privacy@`, `contact@`, `hello@`, `admin@`, `compliance@`, `care@`, `podcast@`, `partnerships@`, etc. Skip message history pulls for these. Exception: `info@` from small-business domains can be real (e.g., Aknanda Productions, Everwellusa).
4. **Pull message history** — for real leads only. Batch with `&&` chaining (4 leads per batch, 90-120s timeout). Extract reply body, strip HTML, decode entities, remove quoted original.
5. **Classify** — positive_interested, negative_notfit, hostile, auto_responder, neutral. Check `our_replies_after` count (SENT messages after lead's reply timestamp, excluding auto-sequence emails).
6. **Flag unhandled positives** — `our_replies_after == 0` means no response was sent. Surface these in the report.
7. **Add to state** — `known_reply_message_ids` for ALL classifications, not just positives.

### Campaign-specific reply handling

- **#3617053 (Coaching Owned Audiences):** Positive replies → `owned-audiences-email-reply` skill. Case study + booking link. Locked bottom template verbatim.
- **#3639259 (Podcasters - SpeakerAgent v2):** Hardcoded SpeakerAgent reply template — no pricing, no white label. Refer to Tony's Calendly. Template at `Instantly-cold-email` skill → `references/speakeragent-podcaster-reply-template.md`.
- **#3577260 (PR Agencies - SpeakerAgent v2):** Same SpeakerAgent template pattern as #3316611. Refer to Tony's Calendly → `cal.com/speakeragent/catch-up`, CC `tony@speakeragent.ai`.
- **#3520103 / #3607306 (AI Guy):** AI operator $10/hr offer. Standard daemon handles these.
- **All other legacy campaigns:** Standard daemon with CAMPAIGN_CONTEXT.

### Classification quirks per campaign type

- **#3639259 podcaster replies** have different signal patterns: "Thank you for your email. I would love to chat" is positive (NOT auto-responder), "out of the country" is OOO, ticket-system bodies from `partnerships@`/`podcasts@` are auto-responders, "blacklist" is negative_notfit.
- **#3617053 coaching replies:** "Not sure I understand" → positive_interested (asking for info, not rejecting).

## Phase B: Pre-Call Reports (runs after monitoring)

1. **Check `/tmp/cal_bookings.json`** — primary automated source. Fallback: Cal.com REST API via curl.
2. **Filter to upcoming** — calls within next 24h (or same-day within 2h priority).
3. **For each call without a report** at `clients/{slug}/pre-call-report.md`:
   - Search Instantly by email (`get-by-email`, global — no campaign ID)
   - Pull message history if found
   - Research the business (25 min cap)
   - Generate the one-page report
   - Save to `clients/{slug}/pre-call-report.md`
4. **For existing reports with TBD dates:** patch the header and Section 7 with confirmed Cal.com details only. Don't regenerate.
5. **Same-day calls get priority** — process within the current run.

## SILENT Decision

After BOTH phases complete:

- **[SILENT]** if: zero unhandled positives in Phase A AND zero new calls needing reports in Phase B
- **[REPORT]** if: any unhandled positive found OR any new pre-call report generated
- **Never combine [SILENT] with content** — either report everything or say nothing.

## Typical Timing

| Phase | API Calls | Expected Time |
|---|---|---|
| Inbox pull (pages 0-1) | 2 | ~60s |
| Message history (4-8 leads) | 4-8 | ~45-90s |
| Classification + state update | 0 | ~5s |
| Pre-call check + report generation | 2-5 | ~30s per new report |
| **Total** | **8-15** | **~2-4 min** |

For runs with only auto-responders and existing pre-call reports: <60s, typically [SILENT].
