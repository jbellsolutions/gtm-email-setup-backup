---
name: pre-call-report
description: "Generate pre-call reports for sales calls. Triggered when new bookings appear on the calendar or before scheduled calls. Pulls email threads, researches leads, and produces a one-page markdown report formatted for Justin's pre-call prep."
version: 1.0.0
author: jbellsolutions
metadata:
  hermes:
    tags: [Sales, Pre-Call, CRM, Research, Reporting]
---

# Pre-Call Report Agent

Generate one-page pre-call reports for Justin before every sales call. Pulls the email thread, researches the lead, and produces a markdown report in the exact format below. Also flags when the prospect-facing game plan needs to be built.

## Trigger

A new booking appears on the sales calendar. In the integrated cron workflow, this runs as part of the broader operations check — scan for upcoming calls within 24h (or same-day within 2h) and generate reports for any that don't already have one. Re-run a refresh pass 24h before the call if anything was missing the first time.

## Inputs (gather in this order)

1. **The booking:** name, email, company, call time, timezone, booking-form answers
2. **The thread:** every email/DM exchanged with this lead. Their exact words matter most — quote them, never paraphrase.
3. **What we already sent:** which cold email framework/angle got the reply, which case study or plan went out, which booking link.
4. **Research (cap at 25 min):** their website, LinkedIn (person + company), socials, **content marketing presence (podcast, newsletter, YouTube, blog — high-signal: tells you what they care about and gives Justin a natural conversation opener)**, ad footprint, reviews, team size, niche/vertical, city/metro.
5. **The full game plan:** check `clients/{slug}/` — if the full build (partner map, influencer graph, SpeakerAgent podcast plan) doesn't exist yet, flag it. The report references the plan, never substitutes for it.

## Report Format (exact, one page, markdown)

```markdown
# PRE-CALL REPORT — {Name}, {Business} · {Call date/time + their timezone}

## 1. THE THREAD IN 30 SECONDS
Source: {framework/angle that landed them} · Sent so far: {plan/case study links}
What THEY said (verbatim quotes, 2-4 lines): "..."
Their word for new business: {searches/orders/patients/clients/installs}
Read on warmth: {hot/warm/curious/skeptical} because {one line}

## 2. WHO YOU'RE TALKING TO
{2-3 lines: person, tenure, how they talk online, one personal hook — BJJ, kids, college team, whatever's real}
Decision-makers: {solo owner / partner / spouse mentioned?} → on the call: {yes/no/unknown}

## 3. THE BUSINESS
{3-4 lines: what they sell, size, market, who their customer is}
Ad footprint: {running ads where, roughly what} · Visible referral sources: {any}
Metro/niche exclusivity check: {OPEN / CONFLICT — flag hard if conflict}

## 4. PREDICTED PAINS (map to script stages 3-5)
1. {pain} — evidence: {what you saw/what they said}
2. {pain} — evidence: ...
3. {pain} — evidence: ...

## 5. THE THREE WALKTHROUGH PICKS (from their game plan)
Partner deal to feature: {named business + the win/win in one line}
Podcast lane: {top GREEN show from SpeakerAgent + the pitch angle}
Owned asset: {their newsletter concept / dormant list size if visible}

## 6. LIKELY OBJECTIONS + THE LOOP
{2-3 predicted objections from the script's table, each with the loop question pre-written using THEIR numbers/words}

## 7. LOGISTICS
Game plan sent to prospect: {sent date / QUEUE NOW}
Morning-of confirmation: {scheduled}
Open items: {anything unverified — flag, don't guess}
```

## Delivery Rules

- **To Justin:** the report lands in Slack (`cold-email-control`) or saved to `clients/{slug}/pre-call-report.md`
- **To the prospect:** the full game plan (prospect-facing version) goes out 24h before the call. Never send the internal report.
- **Morning of:** confirmation touch queued.

## Report Freshness & Refresh Thresholds

Not every existing report needs a full regeneration. Match the refresh depth to staleness:

| Report Age | Call Window | Action |
|---|---|---|
| ≤24h old | Call in ≤24h | **Verify only** — confirm call time/link still valid, check for cancellations, AND check that all required Section 7 LOGISTICS fields are PRESENT (Zoom link, game-plan status, morning-of confirmation). "Verify only" means verify existing values are correct — it does NOT skip adding required fields that were never written. A report generated in haste for a cold-inbound booking can have `## 7. OPEN ITEMS / FLAGS` instead of `## 7. LOGISTICS` and be missing the Zoom link entirely. The "verify only" pass must backfill missing required fields, not just validate existing ones. **Jul 27, 2026:** Irena Pawlowski (Prelint) report was 9h old (created 13:04 UTC, checked at 22:00 UTC) — header said "10:00 AM ET (4:00 PM CET)" matching the live API, but Section 7 was missing the Zoom link, game-plan status, and morning-of confirmation. The "verify only" pass had to add the full `## 7. LOGISTICS` block (`meetingUrl` from Cal.com API) rather than just confirming the time. **Also grep the report body for stale time-relative phrases** ("N days out", "N hours away", "~N hours", "call is X days out") and update them — these are accurate at generation time but rot as the call approaches. The header stamp and Section 7 get re-verified, but Open Items and other body sections often retain the original time-relative language. **Jul 29, 2026:** Irena (Prelint) verify-only pass — header and Section 7 were current, but Open Items still said "Booking is Thu Jul 30, 3 days out" when the call was now ~31 hours away. Patched to "TOMORROW (~31 hours away)". |
| 2-4 days old | Call in ≤48h | **Light refresh** — update Section 7 logistics, verify time, 5-min research boost for any new signals |
| 5-7+ days old | Same-day call | **Targeted refresh** — light refresh + deeper research pass (re-check website, look for content marketing signals, update objection loops if business context changed). Don't regenerate from scratch unless the original was thin. |
| Any age | Call time TBD → now confirmed | **Patch date-bearing fields** — update header and Section 7 only |

**What a "light refresh" includes:**
- Re-verify call time, meeting link, and timezone from live Cal.com API
- Update Section 7 logistics (morning-of confirmation, game plan status)
- Add `[REFRESHED {date}]` tag to the header
- If any new website/social signal found (podcast episode, blog post, hiring announcement), weave it into Sections 2-5

**What triggers a FULL regeneration:**
- The original report was marked as "thin" or had major gaps in Open Items
- New Instantly thread data became available (plan was expired, now renewed)
- The lead's business context changed significantly (new funding, pivot, acquisition)

**Jul 24, 2026:** Erin Todus (Strativis) report was 7 days old on a same-day call. Targeted refresh: updated logistics (game plan past due → same-day flag), added podcast content marketing signal (Jon Smucker / Sherlock AI interview), swapped objection #3 to reflect their AI-curious positioning. Full regeneration not needed — core business research was still valid.

## Hard Rules

- Verbatim quotes over summaries. Justin should hear their voice in section 1.
- Never invent research. Anything unverified goes in Open Items with a flag.
- Exclusivity conflict = stop and alert immediately, before any more prep runs. Then run the **three-framing decision tree** with Justin before prepping any pitch: (a) **partner** — cross-referral or revenue-share model, pitch the partnership not the product; (b) **competitor** — reframe the call as peer/collaboration, do NOT pitch the standard deck; (c) **client** — pitch only the non-overlapping part of our offering (e.g., for a podcast-booking service prospect, pitch the AI operator embedding into their production workflow, NOT SpeakerAgent). **Pause the game plan build** until the framing is decided — don't build a pitch deck for a potential competitor. Jul 28, 2026: Mark Hayward (markjhayward.com, host of Business Growth Talks, 615 episodes) runs Podcast Introduction Group — a podcast guest placement service overlapping with SpeakerAgent's core offering. Report at `clients/markjhayward/pre-call-report.md` flags the conflict; game plan build paused pending Justin's framing decision (partner / competitor / client).
- The three walkthrough picks must come from real research — if the plan build is thin, say so in Open Items rather than padding.
- Report stays one page. The game plan carries the depth; the report carries the call.

## Cron Integration

The cron runs TWO phases in sequence: inbox reply monitoring (Part A) then pre-call reports (Part B). Full combined workflow documented in `references/combined-cron-workflow.md`.

### Part B: Pre-Call Report Steps

Integrated into the `Instantly-auto-reply` cron (job ID `2929988f4269`). Each run:

**⚠️ STEP 0 IS NON-NEGOTIABLE — run `python3 scripts/cal_triple_endpoint_check.py` before doing ANYTHING else in Part B.** This script pulls all three Cal.com endpoints (upcoming + cancelled + past) in one call, filters internal meetings, outputs prospect-facing bookings with attendee emails for slug derivation, and gives you the cancelled/past context needed for same-day call disambiguation. Do NOT write ad-hoc curl + Python parser code — the script already handles the v2 response shape, `status=upcoming` enum, internal-meeting filtering, and three-endpoint decision tree. Exit codes: 0=success, 1=no API key, 2=curl error, 3=JSON parse error. If it fails (exit 2/3), fall back to manual curl. **This has been violated twice (Jul 29 AM and Jul 29 PM sessions) — both times the agent wrote a from-scratch `/tmp/parse_cal.py` or `/tmp/cal_check.py` instead, wasting 5+ min and hitting security-scan blocks. The script is ready to run. Use it.**

0. **Run the bundled triple-endpoint script FIRST.** `python3 scripts/cal_triple_endpoint_check.py` pulls upcoming + cancelled + past in one call, filters internal meetings, and outputs prospect-facing bookings with attendee emails for slug derivation. Do NOT write ad-hoc curl/API-pulling code — the script already handles the v2 response shape, `status=upcoming` enum, internal-meeting filtering, and three-endpoint decision tree. Exit codes: 0=success, 1=no API key, 2=curl error, 3=JSON parse error. If the script fails (exit 2/3), fall back to manual curl calls using the patterns documented below. **Jul 29, 2026:** Agent wrote a from-scratch `/tmp/cal_check.py` re-implementation instead of using the bundled script — wasted 5+ min on a Python default-arg bug and security-scan blocks. The bundled script was ready to run the whole time.
1. **Check BOTH sources and merge — live API is authoritative.** `/tmp/cal_bookings.json` is a snapshot that can go stale (past bookings linger, new bookings may be missing). The **live Cal.com REST API** (`CALCOM_API_KEY`, curl via subprocess — Cloudflare blocks urllib with 403) returns only current upcoming bookings and is the ground truth. Pull BOTH: the live API first (primary), then `cal_bookings.json` (supplement — catches bookings the API query might miss due to attendee-email filtering). Deduplicate by meeting URL or attendee email. **Jul 21, 2026:** `cal_bookings.json` showed 5 bookings including 2 past calls (Gina Jul 21, Samar Jul 20) but missed the new Josh Hamilton (Jul 22) booking — only the live API had it. Always trust the live API for what's upcoming.
2. **⚠️ ALSO scan Instantly message threads for verbally-confirmed bookings.** Calls arranged via email ("Got something on the books for Tuesday") may NOT appear in Cal.com or cal_bookings.json. Pull message history for positive leads on active campaigns (#3639259, #3577260, #3617053) and check for "booked" / "on the books" / "talk Tuesday" / "see you" patterns. These are real calls — generate reports even without Cal.com data.
3. For each call without an existing report in `clients/{slug}/pre-call-report.md`, generate one.
4. For existing reports where the call date was previously unconfirmed (TBD): if Cal.com now has a real date/time, update the header and Section 7 logistics with the confirmed details. Don't regenerate the entire report — just patch the date-bearing fields.
5. For same-day calls, generate within the same run.
6. Reports saved to `clients/{slug}/pre-call-report.md` (typically `/opt/data/clients/{slug}/`).
7. **When call time/meeting link is unknown** (email-thread confirmed but no Cal.com entry): flag in Section 7 as "⚠️ Call time and meeting link UNKNOWN — check Justin's primary calendar." Generate the report anyway — research (Sections 2-6) is still valuable and the operator needs to know the gap exists. See `references/email-thread-bookings.md` for the detection pattern.

## Calendar Sources

See also: `references/cross-cal-account-bookings.md` — SpeakerAgent podcaster bookings use a separate Cal.com account (`cal.com/speakeragent`) and won't appear in Justin's API.

Two sources, merged and deduplicated:
1. **Live Cal.com REST API** — authoritative. Returns only upcoming bookings. Endpoint: `GET /v2/bookings?status=upcoming&take=20`. **⚠️ Do NOT append `filters[hostEmail]=justin@usingaitoscale.com` — this can return empty/error (curl exit code 3, 0-byte response).** Use the bare endpoint and post-filter in Python if needed. **Jul 22, 2026:** `filters[hostEmail]` query returned empty — retrying without it returned 5 bookings including a new one `cal_bookings.json` missed.
2. **`/tmp/cal_bookings.json`** — snapshot file, can be stale (lingering past bookings, missing new ones). Use as supplement only — catches bookings the API query might filter out. Also scan `clients/*/pre-call-report.md` headers for date references as a third check. **Jul 22, 2026:** `cal_bookings.json` missed John Compton's Jul 23 booking (created at 14:42 UTC) — only the live API caught it.

## Lead Sources

1. **Instantly campaigns** — search by email across all campaigns, pull message history. Use `Instantly leads get-by-email --email <email> --format json` (no `--campaign-id` flag — searches globally). If the lead isn't found (returns `{}`), they're a direct booking, not a campaign lead.
2. **LinkedIn** — lead originated from LinkedIn outreach; no email thread available. Flag in Section 1.
3. **Direct booking** — lead booked via Cal.com or referral with no Instantly thread. This is the most common case for `aiintegraterz` event-type bookings. The Section 1 format changes significantly:

### Section 1 for Direct / Cold-Inbound Bookings

When there's NO Instantly thread (lead not found via `get-by-email`), Section 1 becomes:

```
Source: Direct Cal.com booking ({event_type_slug}) — NOT in Instantly. No prior email thread.
Sent so far: Nothing. Lead booked directly — no prior engagement.
What THEY said: No pre-call messages. Pure inbound booking — intent unknown.
Read on warmth: COLD-INBOUND — discovery call only. Don't pitch until you understand why they booked.
```

**Critical flags for cold-inbound bookings:**
- Search Instantly BY EMAIL first — `get-by-email` searches globally, no campaign ID needed. If it returns `{}`, they're truly cold.
- Timezone check: Cal.com `attendees[].timeZone` may differ from the call time. If the call is at an unusual hour for their timezone (e.g., 5:30 AM), flag it in Open Items — could be a timezone selection error.
- **⚠️ Timezone mismatch pitfall:** A booking at a normal ET hour (e.g., 12:30 PM) with `attendees[].timeZone` set to a far-flung timezone like `Pacific/Auckland` means the call is at 4:30 AM their local time. This is almost certainly a timezone selection error — the attendee probably meant to select their actual timezone. Flag prominently in Section 7 Open Items as "⚠️ TIMEZONE ANOMALY: attendee timezone X means call at Y local time. CONFIRM before call." **Jul 22, 2026:** Josh Hamilton (School for Men) booked 12:30 PM ET with timezone Pacific/Auckland → 4:30 AM NZST. Likely error — flagged in report. **Jul 24, 2026:** Owais Tariq (SalesRobot) booked 1:30 PM ET with timezone Asia/Calcutta → 11:00 PM IST. Same pattern, different continent. Any timezone UTC+4 or greater (India, Dubai, Singapore, Australia, NZ) combined with a normal ET business-hours slot = local time between 9 PM and 5 AM. Flag every time.
- Game plan is ALWAYS missing for direct bookings. Flag as "QUEUE NOW" — build after the call if it's a real opportunity.
- No verbatim quotes available — don't invent them. The "What THEY said" line is simply "No pre-call messages."
- Research cap still applies (25 min) but spend more of it on their website/business since there's no thread to mine.

- **Duplicate pre-call reports under different slugs** — When a lead has both a personal-name slug (`clients/chris-warrick/`) and a business-name slug (`clients/primary-business/`), two reports can exist for the same call. This happens when one cron generates a basic report under the person's name, then a later cron with better research generates a more detailed report under the business name. The older report isn't cleaned up, and future agents scanning `clients/*/` find both — they may use the stale one. **Fix:** Before generating a new report, check ALL existing reports for matching email/name in Section 1, not just the slug directory. If a match is found under a different slug, overwrite the better-researched version at the existing path rather than creating a duplicate. **Jul 17, 2026:** Chris Warrick had reports at both `clients/chris-warrick/` (basic, wrong day name "Wed Jul 16") and `clients/primary-business/` (detailed, correct "Thu Jul 16"). **Jul 29, 2026:** Thomas K. Johnston (Synova Search, synovasearch.com) had reports at both `clients/synova-search/` (detailed, Jul 28) and `clients/synovasearch/` (thinner, Jul 29) — a **hyphen-vs-no-hyphen slug variant**. Different agents derived the slug differently from the same domain. **Slug normalization rule:** when checking for existing reports, derive the slug from the domain TLD portion directly (e.g., `synovasearch.com` → `synovasearch`, NOT `synova-search`). If the domain contains a hyphen (e.g., `cross-roads-consulting.com`), the slug preserves hyphens. But domains WITHOUT hyphens should never get hyphens added — `synovasearch.com` → `synovasearch`, not `synova-search`. When consolidating duplicates, keep the more detailed report and rename the directory to the canonical (no-false-hyphen) slug.

- **`cal_bookings.json` format is `{"status":"success","data":[...]}`** — NOT a bare JSON array. The file is a dict with `status` and `data` keys where `data` is the array of booking objects. Use this parser pattern for robustness:
  ```python
  data = json.load(f)
  if isinstance(data, dict) and 'data' in data:
      bookings = data['data']
  elif isinstance(data, list):
      bookings = data   # fallback in case format changes
  else:
      print(f'UNKNOWN FORMAT: {type(data)}')
      return []
  ```
  Confirm: Jul 21, 2026 sweep parsed 5 bookings correctly with this pattern. When the file is missing or empty, fall back to: (1) scanning `clients/*/pre-call-report.md` headers for today's/tomorrow's dates, and (2) the live Cal.com REST API call via curl.

- **⚠️ UTC-to-ET timezone conversion — DO NOT read the raw hour as ET.** Cal.com API returns UTC timestamps with `Z` suffix (e.g., `2026-07-22T16:30:00.000Z`). A common and catastrophic mistake: seeing `16:30` and writing "4:30 PM ET" without subtracting the timezone offset. **16:30 UTC = 12:30 PM ET (UTC-4 during EDT), NOT 4:30 PM ET.** Always compute: `utc_hour - 4 = et_hour` (during EDT, Mar-Nov). If `et_hour < 0`, add 12 and change AM/PM. This mistake can cause Justin to miss a same-day call by 4 hours. **Jul 22, 2026:** Josh Hamilton report had "4:30 PM ET" but live API showed `16:30 UTC` = 12:30 PM ET — a 4-hour error. Fixed at 02:00 AM ET sweep. **Always verify:** if the raw hour looks like a PM time (13-23), it's almost certainly the UTC hour, not ET. Write a verification script that explicitly converts with `datetime.fromisoformat(start).astimezone(timezone(timedelta(hours=-4)))` rather than eyeballing the hour.

**Required conversion step before writing ANY call time:** after pulling the Cal.com live API, run this verification:
```python
from datetime import datetime, timezone, timedelta
utc_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
et_time = utc_time.astimezone(timezone(timedelta(hours=-4)))
# Use et_time for the report header — NEVER the raw UTC hour directly.
```
This removes the human error of misreading `16:30Z` as 4:30 PM. — When a lead says "Got something on the books for Tuesday" and our operator confirms ("Talk Tuesday!"), the call is real but won't appear in any calendar API. The cron's Part B steps 1-2 will miss these entirely if they only check Cal.com sources. **Detection:** scan Instantly message history for positive leads on active campaigns (#3639259, #3577260, #3617053) looking for "on the books", "booked", "talk [day]", "see you [day]", "looking forward to it". If found with a future date reference and no Cal.com entry exists, generate the report anyway with call time/meeting link flagged as unknown. **Jul 20, 2026:** Peter Vera (peter@bizexitgrow.com, #3639259) confirmed his SpeakerAgent call for Tue Jul 21 via email — zero Cal.com records, but the call is real. Report created at `clients/bizexitgrow/pre-call-report.md` with Section 7 flagging the missing logistics. See `references/email-thread-bookings.md`. — Cloudflare blocks Python's urllib. Use curl via subprocess instead. Working pattern:
  ```python
  subprocess.run(["curl", "-s", "-f",
      "-H", f"Authorization: Bearer {api_key}",
      "-H", "cal-api-version: 2026-05-01",
      "-H", "User-Agent: followup-engine/1.0",
      "--max-time", "10", url], ...)
  ```
  The API key is `cal_live_...` stored at `CALCOM_API_KEY` in `/opt/data/.env`. Endpoint: `GET /v2/bookings?status=upcoming&attendeeEmail=...`. Response: `{"status":"success","data":[...]}` where each booking has `attendees[].email`, `start`, `title`.

## Pitfalls

### ⚠️ Cal.com v2 `status` query param ≠ response field — `status=accepted` is WRONG (Jul 25, 2026)

The v2 bookings endpoint query parameter `status` accepts only: `upcoming`, `recurring`, `past`, `cancelled`, `unconfirmed`. Using `status=accepted` returns `BadRequestException`: `"Invalid status. Allowed are upcoming, recurring, past, cancelled, unconfirmed"`.

**Correct:** `GET /v2/bookings?status=upcoming&take=20` — the query parameter is `upcoming`, even though response booking objects have `"status": "accepted"` internally. The query param and response field use different enum vocabularies — don't conflate them.

### ⚠️ Bookings can be cancelled BETWEEN API calls — don't assume a booking seen once is still real
The Cal.com `upcoming` endpoint only returns `status: "accepted"` bookings. If a lead cancels between calls (even seconds apart), the booking silently disappears from the result set. **Always re-verify a booking is still in the live API before generating a report** — if a booking was seen in the first API pull but missing in a second validation pull, it was cancelled. Don't generate a report for a cancelled booking. **Jul 23, 2026:** John Compton (Sunray Councils, john@sunraycouncils.com, id 22636084) appeared in the first API call but was gone in the second call seconds later — cancelled. The Agile Search John Compton (different person, different booking) was correctly identified as separate.

**Detection workflow:** Before generating a new report, pull the live API TWICE (second pull as validation). If the booking is in both, it's confirmed. If only in the first, it's likely cancelled — skip it.

**Positive cancellation confirmation via `status=cancelled` endpoint (Jul 27, 2026):** Absence from the `upcoming` list is inference, not proof — the booking could be in a transient API gap, filtered by a query param, or on a different Cal.com account. To **positively confirm** a cancellation (vs. a glitch), query the cancelled endpoint: `GET /v2/bookings?status=cancelled&sortStart=desc&take=20`. If the booking appears there with the matching attendee email and start time, it's definitively cancelled. This is the difference between "probably cancelled, skip it" and "confirmed cancelled, mark the report." Use it any time a report already exists for a booking that's missing from `upcoming` — the existing report needs to be patched, not silently dropped.

### ⚠️ Three-endpoint verification — use `status=past` to confirm same-day calls already happened

When a booking has a report on disk but is missing from BOTH `upcoming` and `cancelled`, it's ambiguous: cancelled without record, past and already happened, or on a different Cal.com account. **Query `status=past` to resolve the ambiguity before making any changes:**

```bash
curl -s "https://api.cal.com/v2/bookings?status=past&sortStart=desc&take=10" \
  -H "Authorization: Bearer $CALCOM_API_KEY" \
  -H "cal-api-version: 2024-08-13" --max-time 10
```

**Three-endpoint decision tree for same-day calls with existing reports:**
1. `upcoming` → booking still live, verify time/link
2. `cancelled` → confirmed gone, patch header with `**CANCELLED**`
3. `past` → call already happened, no action needed — report is now historical

**If the booking is in NONE of the three endpoints**, it was likely on a different Cal.com account (e.g., SpeakerAgent's account at `cal.com/speakeragent`). Flag as "⚠️ Not found in Justin's Cal.com — may be on SpeakerAgent account." Do NOT delete the report.

**Jul 27, 2026:** Johanna Watson (12:30 PM ET) and Binoy Perera (3:00 PM ET) — both had reports from Jul 26, both absent from `upcoming`, neither in `cancelled`. Querying `status=past` confirmed both had already occurred (past bookings at 16:30Z and 19:00Z respectively). Without the `past` endpoint, the ambiguity would have forced a full re-verification. This is the standard resolution pattern for same-day calls that disappear between cron runs.

**⚠️ When a report ALREADY EXISTS and the booking cancels before call day — patch the header, don't just skip.** A stale report sitting on disk with a "re-verified yesterday" header is dangerous: a future cron run or operator may see the report, assume the call is live, and prep for a call that won't happen. When you positively confirm a cancellation:
1. Patch the report header to flag `**CANCELLED**` with strikethrough on the original time
2. Add a note: `[Booking removed from Cal.com — confirmed via live API {date}, not in upcoming list, present in cancelled list]`
3. Leave the rest of the report intact for historical reference — do NOT delete the file
4. Surface the cancellation prominently in the cron report to Justin

**Format for cancelled report header:**
```
# PRE-CALL REPORT — {Name}, {Business} · ~~{original date/time}~~ **CANCELLED** [Booking removed from Cal.com — confirmed via live API {date}, not in upcoming list, present in cancelled list]
```

**⚠️ "Re-verified on prior day" does NOT guarantee the booking is still live today.** A booking confirmed via dual API pull at 11 PM ET on Jul 26 can be cancelled at 8 AM ET on Jul 27. Every cron run that touches same-day calls MUST re-pull the live API — never trust a prior run's "re-verified" stamp as proof the booking is still active. The "re-verified" header tag records when you last checked, not the booking's current status. **Jul 27, 2026:** Owais Tariq (SalesRobot) report showed "[REFRESHED Jul 26, 2026 — booking re-verified via dual Cal.com API pull, no changes]" but the booking was cancelled before Jul 27 09:30 AM ET — discovered only because the same-day cron re-pulled the live `upcoming` API and found it missing, then positively confirmed via the `cancelled` endpoint.

### ⚠️ Always pull the FULL API response — never truncate with `head`
The Cal.com live API can return 5-6+ bookings. Truncating the curl output with `head -c 3000` can clip off later bookings. **Jul 23, 2026:** first API pull was truncated at 3000 chars, showing 5 bookings but missing the 6th (Binoy Perera). Always save the full response to a file (`> /tmp/cal_live.json`) and parse from there. Never pipe to `head` before parsing.

### ⚠️ Deduplicate by email, not by name — same-name collisions are real

### ⚠️ Non-decision-maker bookers — flag prominently in Section 2
When the person who booked is NOT the founder/CEO/owner (e.g., an Account Executive, SDR, or marketing manager), flag this in Section 2 as "decision authority is LIMITED" and note who the actual decision-maker is (CEO, founder, etc.). The call may be a scouting/qualification mission rather than a buying conversation. **Jul 24, 2026:** Owais Tariq (AE at SalesRobot) booked a gameplan session — the real decision-maker is CEO Saurav Gupta. The AE is likely qualifying AI Integraterz as a prospect or partner, not buying.

### ⚠️ Skip internal meetings — only generate reports for prospect-facing calls
Bookings where Justin's own email (`justin@usingaitoscale.com`) is the ONLY attendee, or where the event type is "Customer Support Sync" / "30 Min Meeting" (internal) rather than "AI Integraterz Gameplan Session" (prospect-facing), are internal meetings. Do NOT generate pre-call reports for them. **Jul 24, 2026:** Binoy Perera (30 Min Meeting, Justin's email) and Evan Dantes (Customer Support Sync) were correctly skipped.

**Known prospect-facing event type slugs** (generate reports for these):
- `aiintegraterz` — "AI Integraterz Gameplan Session" — the $10/hr AI operator offer. Pitch the full AI Integraterz service (partner map, owned audience, SpeakerAgent podcast lane).
- `speaker-agent-beta` — "Speaker Agent Beta" — **SpeakerAgent product onboarding/qualification**, NOT the AI operator offer. Pitch the SpeakerAgent product (Scout Run, persona setup, $1k+ opportunities, free tier Scout Run + voice samples, IP protection). Do NOT pitch the $10/hr in-house AI operator unless the lead explicitly pivots there — if they do, route to a separate `aiintegraterz` gameplan booking. **Jul 28, 2026:** Geni (genicormedia@gmail.com, no company domain) booked a `speaker-agent-beta` call — report generated with explicit flag to pitch SpeakerAgent, not AI operator.

### ⚠️ Attendee-only search misses bookings where the person is title-only — search BOTH `attendees[].email` AND `title`
Some Cal.com bookings (especially internal/peer meetings like "30 Min Meeting" or "Customer Support Sync") list ONLY `justin@usingaitoscale.com` as an attendee — the other person's name appears only in the `title` field (e.g., "30 Min Meeting between Binoy Perera and Justin"). Searching `attendees[].email` for the person's email returns false negative. **Always search BOTH fields:** check `title` for the person's name AND `attendees[].email` for their email. A booking that matches in either field is relevant. **Jul 25, 2026:** Binoy Perera's booking showed only Justin as an attendee; searching attendees for "binoy" missed it. The `title` field contained "Binoy Perera" — matching both fields correctly identified the booking.

Two leads can share the same name (e.g., two John Comptons booked on the same day for different times). The Agile Search John Compton was at 10:00 AM ET; the Sunray Councils John Compton was at 3:00 PM ET. Deduplicate calendar entries by attendee email, not by name. Match existing reports by email address in Section 1, not by slug directory name.

**Research priority order for podcast host leads** (e.g., `speaker-agent-beta` bookings):
1. **Apple Podcasts Search API** (`scripts/apple_podcasts_search.py`) — fastest, no rate limits, returns host name + RSS feed
2. **RSS feed fetch** — channel description (host bio), episode titles, total episode count
3. **DDG HTML** — bare email handle as query (may be their brand name)
4. **Company website** — if domain is known
5. **DNS domain guessing** (`scripts/guess_company_domain.py`) — last resort

This priority order is specific to podcast host leads. For non-podcaster leads (e.g., `aiintegraterz` gameplan sessions), the standard order (company website → DDG HTML → Google → LinkedIn) still applies.

### ⚠️ Google + LinkedIn block automated browsers — use DuckDuckGo HTML as research fallback

When researching a lead for Section 2-3, automated browser sessions hit three blockers:
1. **Google search → CAPTCHA** — the browser gets a "sorry/index" redirect with IP-flagging. Google Cloud IPs (DigitalOcean, AWS) are rate-limited hard.
2. **LinkedIn → login wall** — `linkedin.com/search/results/people/` redirects to `linkedin.com/uas/login`. No public profile data accessible without authentication.
3. **DuckDuckGo API (`api.duckduckgo.com`)** — returns empty `Results` / `RelatedTopics` for most person-name queries. Not useful for lead research.

**The workaround: DuckDuckGo HTML search via curl.** The HTML endpoint (`html.duckduckgo.com/html/?q=...`) returns search result snippets that often include LinkedIn blurbs, Instagram bios, podcast descriptions, and company mentions — enough to build Sections 2-3 without ever hitting Google or LinkedIn directly:

```python
import subprocess, re

result = subprocess.run([
    'curl', '-s', '-L',
    f'https://html.duckduckgo.com/html/?q={quote(query)}',
    '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    '--max-time', '10'
], capture_output=True, text=True)

snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', result.stdout)
for s in snippets:
    clean = re.sub(r'<[^>]+>', '', s).strip()
    if clean and len(clean) > 10:
        print(clean)
```

**Jul 24, 2026:** Erin Todus (Strativis) — Google blocked the browser, LinkedIn required login, DuckDuckGo API returned nothing, but DuckDuckGo HTML returned 7+ rich snippets including her co-founder role, "Managing Director, Startup Practice," podcast mentions, Instagram bio, and a client testimonial. Enough to build a complete pre-call report without ever reaching Google or LinkedIn.

**When to use which path (priority order):**
1. Browser → company website (strativis.io) — always works, start here
2. Curl → DuckDuckGo HTML search — for person-specific research when Google/LinkedIn block
3. Browser → Google — only if the VPS IP isn't flagged (rare)
4. Browser → LinkedIn — only if authenticated session cookie exists (almost never)

**⚠️ DDG HTML frequently returns empty for employee-specific queries at small companies.** When researching a specific person at a small SaaS/startup (e.g., "Owais Tariq SalesRobot"), DDG HTML often returns zero results — the employee may have no public web presence beyond the company site. **If DDG returns nothing after one query, skip it immediately and go to the company's about/team page.** The company website is almost always more productive for team bios, roles, and company context than search engines. **Jul 24, 2026:** Owais Tariq (SalesRobot) — two DDG HTML queries returned 0 results, but salesrobot.co/about-us listed his exact role (Account Executive), CEO (Saurav Gupta), COO, and full team — everything needed for Sections 2-3. Don't chain DDG queries hoping for different results; one empty query is the signal to switch to the website.

**⚠️ DDG HTML rate-limits after 3-4 rapid queries — returns CAPTCHA challenge, not results.** DuckDuckGo's HTML endpoint detects bot-like traffic after ~3-4 consecutive queries within the same session and starts returning CAPTCHA/anomaly challenge pages instead of search results. Once rate-limited, subsequent queries all fail silently (the challenge page contains no `result__snippet` divs, so grep matches nothing — indistinguishable from a no-results query). **Detection:** if the response contains `anomaly-modal` or `challenge-form` instead of `result__body`, you've been rate-limited. **Mitigation:** batch queries early (2-3 max per session), space them 5+ seconds apart, and always hit the company website first — the website often obviates the need for DDG entirely. **Jul 25, 2026:** Owais Tariq refresh pass — DDG returned results for query #1 (main search), CAPTCHA for query #2 (LinkedIn-specific), and 0 results for queries #3-5. The first query plus salesrobot.co/about-us already had everything needed.

**⚠️ CRITICAL: Security-scanner blocked pipe-to-interpreter attempts STILL consume DDG rate limit.** When the security scanner blocks `curl | python3` (tirith:curl_pipe_shell or tirith:pipe_to_interpreter), curl has ALREADY fired and hit DDG's endpoint — the block only prevents the output from reaching Python. By the time you write the file-based workaround (curl → file → python), DDG may already be rate-limited from the blocked attempts. **Always go straight to the file-based `subprocess.run(['curl', ...])` approach on the first try.** Never attempt pipe-to-interpreter first and then fall back — the fallback will already be rate-limited. **Jul 26, 2026:** Light refresh for Johanna Watson and Owais Tariq — two pipe-to-interpreter attempts were blocked by security scan, both consumed DDG rate limit. The subsequent file-based subprocess approach returned CAPTCHA for both queries. Reports were already thorough enough from prior research — DDG wasn't needed — but the pattern confirms: blocked pipes ≠ zero cost to DDG.

**⚠️ Bing returns large but empty result pages for obscure handles — don't waste time parsing.** Bing does not always return a challenge/captcha page when blocked from VPS. For obscure email handles (e.g., `genicormedia`), Bing returns a **normal-looking 70KB+ HTML results page** with zero substantive snippets — the page looks like it worked but contains no actual search results, just boilerplate JS/CSS. If you parse the Bing HTML and find no `<p>` snippets longer than 20 chars containing the query term, treat it as a failed search and move on. Don't retry with different query formulations — Bing's VPS-side results for person-name queries are consistently empty even when the page renders. **Jul 28, 2026:** Bing query for "genicormedia" returned 74KB HTML, zero usable snippets. DDG was rate-limited (challenge page), DNS guesses all failed. The lead had no discoverable web presence — report was correctly marked "thin" with Open Items flags. **Jul 29, 2026 UPDATE:** This "thin" report was fully resolved the next session — see the "Apple Podcasts Search API" and "Bare email handle as DDG query" techniques below.

**⚠️ Apple Podcasts Search API — free, unauthenticated, no rate limits, ideal for podcaster/SpeakerAgent leads.** The iTunes Search API (`itunes.apple.com/search?media=podcast`) is a public endpoint that requires NO authentication and works reliably from VPS IPs where Google/LinkedIn/DDG all fail. It returns podcast name, host name, RSS feed URL, Apple Podcasts URL, and episode count. This is the **single best research tool** for leads who booked a `speaker-agent-beta` call — they're almost always podcast hosts, and this API finds them by podcast name or host name instantly.

```python
import subprocess, json
# Search by podcast name or host name
r = subprocess.run(['curl', '-s',
    'https://itunes.apple.com/search?term=house+of+impact&media=podcast&limit=5',
    '-H', 'User-Agent: Mozilla/5.0', '--max-time', '10'],
    capture_output=True, text=True)
data = json.loads(r.stdout)
for res in data.get('results', []):
    print(f"{res['collectionName']} | Host: {res['artistName']} | "
          f"RSS: {res.get('feedUrl','')} | "
          f"Apple: {res.get('trackViewUrl','')}")
```

Use `scripts/apple_podcasts_search.py` for the ready-made version. **Jul 29, 2026:** Geni Cor (genicormedia@gmail.com) was a "thin" report for 2+ days — DDG/Bing/Google/DNS all failed. One Apple Podcasts search for "house of impact" instantly returned: podcast name, host name (Geni Cor), RSS feed URL, Apple Podcasts ID (1777111021), and 39 episodes. Fetching the RSS feed gave full episode titles, descriptions, and her bio. Report went from all-UNKNOWN to fully complete Sections 2-6 in under 5 minutes.

**⚠️ RSS feed as a content research goldmine.** Once you find a podcast via Apple's API, fetch the RSS feed URL (`feedUrl` field) for episode-level detail. The RSS feed contains: channel description (host bio), episode titles, episode descriptions, publish dates, and total episode count. This gives you Justin's "content marketing presence" research input (Section 4, Input 4) for free — no browser needed. Strip HTML tags from descriptions with `re.sub(r'<[^>]+>', '', desc)`.

**⚠️ Bare email handle as a DDG query — the handle may BE the brand name.** When a lead has a Gmail address and no company domain, the email handle (part before `@`) is often their personal brand name. A bare DDG HTML search on JUST the handle (e.g., `genicormedia`, not `genicormedia@gmail.com` or `genicormedia podcast`) can return snippets where the handle appears in their own content — RSS feeds, podcast descriptions, social media bios. This works because the handle is a unique string that only appears in the person's own content. **Jul 29, 2026:** Searching DDG HTML for just `genicormedia` returned a snippet: "I'm Geni Cor host of House of Impact podcast. I am so thankful you're here." — that single snippet identified the lead's full identity. Adding qualifiers (`podcast`, `@gmail.com`) to the query caused rate-limiting on the second attempt — the bare handle was both the highest-signal and least likely to rate-limit.

**⚠️ DDG rate limits reset between sessions — "thin" reports on same-day calls warrant one more attempt.** DDG's rate limiting is per-session (per-IP, per-time-window), NOT permanent. A query that was rate-limited in a prior cron session (hours earlier) may succeed in the current session. When a same-day call has a "thin" report from a prior session where all research engines failed, always try ONE fresh DDG query before giving up — the rate limit may have expired. **Jul 29, 2026:** Geni's report was "thin" for 2+ days across 4+ sessions. On Jul 29, a fresh DDG session (rate limits reset overnight) immediately returned the key snippet. The prior "thin" status was a rate-limit timing issue, not a genuine absence of web presence.

**⚠️ Cap at 25 min regardless of path.** If DuckDuckGo HTML returns enough to fill Sections 2-5, stop. Don't burn time chasing LinkedIn profiles when DDG already gave you the signal. If DDG returns nothing, the company website is your next stop — not more DDG queries. For podcast host leads specifically, try the Apple Podcasts Search API before DDG — it's faster, has no rate limits, and returns structured data.

### ⚠️ `cal_cross_check.py` produces false "MISSING REPORTS" alarms — verify by slug, not by script output

The bundled `scripts/cal_cross_check.py` reports "MISSING REPORTS" for bookings that DO have reports on disk. Two root causes:

1. **Name matching, not email matching.** The script parses the person's name from the booking `title` field (e.g., "Johanna Watson" from "AI Integraterz Gameplan Session between Justin and Johanna Watson") and searches `clients/*/` directories by name. But report slugs are derived from the company domain (e.g., `artemis-hou` for artemishou.com, `salesrobot` for salesrobot.co), NOT from the person's name. So the script says "no report for Johanna Watson" when the report exists at `clients/artemis-hou/pre-call-report.md`.

2. **Internal meetings not filtered.** The script lists internal meetings (Customer Support Sync, 30 Min Meeting where Justin is the only attendee) as "MISSING REPORTS" even though they should be skipped per the "Skip internal meetings" pitfall above.

**Jul 25, 2026:** `cal_cross_check.py` reported 5 MISSING REPORTS. All 5 actually had reports on disk (artemis-hou, salesrobot, synova-search, agentmail) or were internal meetings (Evan Dantes Customer Support Sync). Zero reports actually needed generation. The false alarm forced a full manual re-verification of every report path.

**Fix for the cron workflow:** Do NOT trust `cal_cross_check.py`'s "MISSING REPORTS" list as a signal to generate. Instead, use `scripts/cal_triple_endpoint_check.py` — a reliable triple-endpoint script that pulls upcoming + cancelled + past in one run, filters internal meetings (Justin-only attendee, event type slug in `customer-support-sync`), and outputs prospect-facing upcoming bookings with attendee emails for slug derivation. Exit code 0 = success, 2 = curl/network error, 3 = JSON parse error.

The canonical workflow with `cal_triple_endpoint_check.py`:
1. Run `python3 scripts/cal_triple_endpoint_check.py` → get prospect-facing upcoming bookings with attendee emails
2. For each remaining prospect-facing booking, derive the slug from the attendee's company domain (not their name) and check `clients/{slug}/pre-call-report.md` directly
3. Only generate if the file is genuinely missing OR the report is stale beyond the refresh thresholds
4. Use the CANCELLED section to positively confirm any bookings missing from UPCOMING (patch report headers with `**CANCELLED**`)
5. Use the PAST section to resolve ambiguity for same-day calls that disappeared from upcoming (already happened = no action needed)

The old `cal_cross_check.py` is still useful as a quick "what's on the calendar" listing, but its report-existence check is unreliable. Treat its `[NO REPORT]` flags as prompts to verify, not as confirmed gaps.

### ⚠️ Save reports to slug-based directory, never flat paths

Reports MUST be saved to `clients/{slug}/pre-call-report.md` (typically `/opt/data/clients/{slug}/`). Never save to a flat path like `/opt/data/pre-call-{name}.md` — the cron sweep detection and refresh logic in Part B step 2 scans `clients/*/pre-call-report.md` and won't find reports saved elsewhere. The slug is derived from the company domain or business name (e.g., `salesrobot` for salesrobot.co, `strativis` for strativis.io). If the `clients/{slug}/` directory doesn't exist yet, create it.

**Jul 25, 2026:** Owais Tariq refresh pass wrote to `/opt/data/pre-call-owais-tariq.md` instead of `clients/salesrobot/pre-call-report.md` — the cron's Part B scan won't detect it for future refreshes. The report content is valid but the path is wrong.

### ⚠️ Gmail-only leads — slug derivation from email handle when no company domain exists

When a lead's booking has only a Gmail/personal address (e.g., `genicormedia@gmail.com`) and no company name on the booking, there is no company domain to derive a slug from. **Derive the slug from the email handle** (the part before `@`) — e.g., `genicormedia`. This keeps the report discoverable by the `clients/*/` glob and makes it easy to rename later if the lead reveals their business on the call.

**Research fallback when ALL search engines are blocked:** When DDG HTML rate-limits AND Google hits CAPTCHA AND Bing/Yandex return challenge pages (this happens during sustained VPS-side research bursts), the normal "company website → DDG HTML → Google → LinkedIn" priority order has no first step. **Try DNS-resolution domain guessing** as a last-ditch research technique — run `scripts/guess_company_domain.py <email>` to try resolving common TLD variants of the email handle (`genicormedia.com`, `genicormedia.co`, `genicor.media`, `geni-cormedia.com`, etc.). If any resolve, fetch that website via curl for Section 3 research. If none resolve, the lead has no discoverable business website and the report is "thin" — flag every Section 2-5 unknown in Open Items per the hard rule "Never invent research. Anything unverified goes in Open Items with a flag."

**Jul 28, 2026:** Geni (`genicormedia@gmail.com`) — DDG, Google, Bing, Yandex ALL blocked from VPS this session. DNS guesses for `genicormedia.com`/`.co`/`.media` all failed (exit code 6 — DNS resolution failure). Report generated at `clients/genicormedia/pre-call-report.md` with research explicitly marked UNKNOWN and a flag to re-run a research pass with a fresh VPS session or browser tool before the call. Run `scripts/guess_company_domain.py <email>` to automate the DNS-guessing pass — it tries common TLD variants (`genicormedia.com`, `genicor.media`, `geni-cormedia.com`, etc.) plus platform subdomains (`{handle}.substack.com`, `{handle}.medium.com`, `{handle}.youtube.com/c`). Exit 0 = at least one resolved (use `--fetch` to also curl the website), exit 1 = none resolved (report is thin).

**⚠️ Platform subdomain false positives — Medium returns HTTP 200 for ANY `*.medium.com` subdomain (Jul 28, 2026).** When DNS guessing resolves platform subdomains, you MUST verify the profile actually exists by fetching the URL and checking the page content — not just the HTTP status code. Different platforms behave differently:
- **Substack** (`{handle}.substack.com`) — returns HTTP 404 for non-existent profiles. Clear signal: 404 = no profile. Safe to trust the status code.
- **Medium** (`{handle}.medium.com`) — returns HTTP 200 with the generic Medium.com homepage for ANY subdomain, even non-existent ones. A 200 response does NOT mean the profile exists. You must check the page `<title>` — if it says "Medium" (the generic site title) rather than a person's name, the profile doesn't exist. This is a false positive trap: an agent sees HTTP 200 and assumes they found the lead's Medium profile, when in fact it's just Medium's catch-all homepage.
- **YouTube** (`{handle}.youtube.com/c`) — returns HTTP 200 but may be a "channel not found" page. Check page content for error text.

**Verification pattern after DNS resolution:**
```python
import subprocess, re
for domain in resolved_domains:
    r = subprocess.run(['curl', '-s', '-L', '-o', '/tmp/profile.html', '-w', '%{http_code}',
        f'https://{domain}', '-H', 'User-Agent: Mozilla/5.0', '--max-time', '12'],
        capture_output=True, text=True)
    status = r.stdout.strip()
    with open('/tmp/profile.html') as f:
        title = re.search(r'<title[^>]*>([^<]+)</title>', f.read())
    title_text = title.group(1).strip() if title else ''
    # Medium catch-all: HTTP 200 + title "Medium" = no real profile
    if 'medium.com' in domain and status == '200' and title_text == 'Medium':
        print(f"  {domain}: FALSE POSITIVE (Medium catch-all homepage)")
    elif status == '404':
        print(f"  {domain}: 404 (no profile)")
    else:
        print(f"  {domain}: {status} — {title_text[:80]} (VERIFY CONTENT)")
```

**Jul 28, 2026:** Geni research pass — `genicormedia.substack.com` resolved (DNS) but returned HTTP 404 (no Substack). `genicormedia.medium.com` resolved and returned HTTP 200 — looked like a hit — but the page `<title>` was just "Medium" (the generic homepage). No actual profile content existed. Both platform subdomains were false leads. Without the title check, an agent could have wasted 10+ minutes parsing the Medium homepage looking for Geni's articles that don't exist.

When `cal_bookings.json` has multiple bookings, each has its own `meetingUrl`. It's easy to grab the first booking's Zoom link and accidentally paste it into a different lead's report. **Jul 24, 2026:** Erin Todus's report initially had Samar's Zoom link because both bookings shared the same event type. Always extract the booking by attendee email match, and verify the `meetingUrl` field is from the correct booking object before writing into Section 7.

```python
# Match by attendee email, not by event type or booking order
target_email = "erin.todus@strativis.io"
for b in bookings:
    attendees = b.get("attendees", [])
    if any(a.get("email") == target_email for a in attendees):
        zoom_link = b.get("meetingUrl")
        tz = attendees[0].get("timeZone", "Unknown")
        break
```