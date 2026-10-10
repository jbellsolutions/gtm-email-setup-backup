---
name: positive-reply-scoring
description: "Classify Instantly campaign replies and compute the north-star metric: positive reply rate. Trigger on 'score my replies', 'how's campaign X doing', 'positive reply rate', 'is this campaign working', 'reply analysis'."
version: 1.4.0
source: Adapted from GrowthEngineX coldoutboundskills
---

# Positive Reply Scoring

**Reply rate tells you if people are paying attention. Positive reply rate tells you if they want what you're buying.**

```
positive_reply_rate = (interested + soft + referral) / total_sent
```

## Classification Schema

Every reply gets exactly one label:

| Label | Meaning | Count as positive? |
|---|---|---|
| positive_interested | "Yes, tell me more" / booked meeting | ✅ |
| positive_soft | "Send info" / "reach out in Q3" | ✅ |
| positive_referral | "Not me, but talk to X" | ✅ |
| neutral_question | Clarifying question, no commitment | ❌ |
| negative_notnow | "Not right now" | ❌ |
| negative_notfit | "Not a fit" / "don't need this" | ❌ |
| negative_hostile | Angry, complaint, report | ❌ (risk signal) |
| unsubscribe | Explicit opt-out | ❌ |
| ooo | Out-of-office auto-reply | ❌ (exclude from denominator) |
| bounce | Technical bounce | ❌ (exclude from denominator) |

## How to Run

### Step 1: Fetch all inbox replies (CLI — primary method)

MCP tools may not be available. Use the Instantly CLI:

```bash
export PATH=/opt/data/home/.local/bin:$PATH
export Instantly_API_KEY=$(grep Instantly_API_KEY /opt/data/.env | cut -d= -f2)
Instantly inbox replies --format json > /tmp/inbox_all.json
```

**Response format:** `{"ok": true, "data": [...], "offset": 0, "limit": 20}` — replies are under the `data` key as a list, NOT a bare array or `items` key.

**Key fields per inbox item:**
- `last_reply_time` — ISO timestamp (e.g. `2026-05-13T12:07:31.000Z`). This is the reply time.
- `email_campaign_id` — which campaign the reply belongs to
- `email_lead_id` — numeric lead ID (use this for message history, NOT `email_lead_map_id`)
- `email_lead_map_id` — inbox entry ID (for `inbox lead --id`, NOT for `leads messages`)
- `lead_email`, `lead_first_name`, `lead_last_name` — who replied
- `lead_status` — COMPLETED, BLOCKED, INPROGRESS, etc.
- `has_new_unread_email` — true if unread

### Step 2: Fetch message history for each reply

For every reply, get the actual reply body text:

```bash
Instantly leads messages --campaign-id <campaign_id> --lead-id <email_lead_id> --format json > /tmp/msg_<lead_id>.json
```

**CRITICAL:** Use `email_lead_id` (from inbox), NOT `email_lead_map_id`. Using `email_lead_map_id` returns `{"history": []}` silently.

**Response format:** `{"history": [...], "from": "...", "to": "..."}` — messages are nested under the `history` key, not a bare array.

**Key fields per message:**
- `type`: `SENT` or `REPLY` — filter for REPLY
- `email_body`: HTML content of the reply (strip tags with regex for classification)
- `from`: sender email (mailer-daemon = bounce, human sender = real reply)
- `time`: ISO timestamp
- `stats_id`: for replying via Instantly API

### Step 3: Classify each reply

Read each reply body and classify using the schema below. **Classify only the FIRST reply per lead** — later messages are conversation, not signal.

**⚠️ CRITICAL — strip quoted email BEFORE classification.** The cold email copy contains positive-sounding language. If the quoted original email leaks into classification, ~47% of positives will be false. Use the canonical `strip_quotes()` function from `references/quote-stripping-patterns.md` — it handles Outlook, Apple Mail, Gmail web/mobile, and Exchange formats. The one-line `re.split(r'On .+ wrote:')` is NOT sufficient.

**Hermes security note:** Pipe-to-interpreter (`Instantly | python3`) and heredoc (`python3 << 'EOF'`) are blocked by the security scanner. Workaround: write JSON to file with `> /tmp/file.json`, then read with Python script saved to file.

**Reusable classifier**: `scripts/classify.py` — classifies Instantly message history JSON files. Fixed for one-word agreement + quoted email and STOP MAIL edge cases (June 2026). Usage: `python3 /opt/data/skills/sales/positive-reply-scoring/scripts/classify.py /tmp/msg_<lead_id>.json` (use full path — CWD may not be the skill directory).

**⚠️ `scripts/classify.py` has ~30% error rate.** As of July 2026, three consecutive sweeps (June 24, July 8 weekly, July 8 SpeakerAgent) all found ~31% misclassification. For high-stakes campaign monitoring where every positive matters, use inline classification rules instead (see `references/campaign-slack-push.md` for the canonical inline rule set). The script is still suitable for broad analytics sweeps where individual misclassifications are tolerable.

Classification rules (apply in order — first match wins). **CRITICAL: person-left-with-referral (rule 10) MUST be checked before dead-email bounce (rule 3).** "X is no longer with company, contact Y" is a referral, not a bounce. See `references/classification-edge-cases.md` for full ordering rationale and additional edge cases discovered in live sweeps.

> 1. OOO auto-replies ("out of office", "on vacation", "away from my desk", "return on", "parental leave", "maternity leave") → `ooo`
> 2. Bounces ("mail delivery failed", "undeliverable", "mailer-daemon", "address not found", "mailbox full") → `bounce`
> 3. **Person-left-with-referral — CHECK BEFORE DEAD-EMAIL:** "X is no longer with company, contact Y" → `positive_referral` (must come before rule 3b — if you check "no longer" as bounce first, you'll misclassify referrals)
> 3b. **Dead-email responses (no referral given):** "email no longer exists", "email address no longer monitored", "message blocked" → `bounce`
> 4. **Form auto-responders / contact acknowledgments:** "Thank you for contacting", "we will respond within", "we'll get back to you" → `neutral_question` or `ooo` (auto-reply — exclude from denominator). **NOT** positive_referral — "we will contact you" is NOT a referral.
> 5. "Unsubscribe", "remove me", "take me off your list", "STOP MAIL", "STOP EMAIL", "remove our email", "please stop", single-word "Stop" reply, "remove from" → `unsubscribe`
> 6. "Not interested", "not a fit", "don't need this", "no thank you", "no thanks", "no thx", "not intrested" (typo), "we're good", "do not email", "do not contact", "would you hire you" → `negative_notfit` (⚠️ "no thx" is an abbreviated rejection — must be explicitly checked since substring "no thanks" won't match "no thx"; "not intrested" is a common typo for "not interested"; "would you hire you" is a snarky rejection — reader is pointing out the irony of the pitch)
> 7. "Not right now, circle back in Q3" → `negative_notnow`
> 8. **Pricing inquiries:** "What's the cost", "Please share fees", "How much", "Can you let me know the fees", "upfront payment", "your website" → `positive_soft` (interest signal — asking about cost or checking out the business is pre-purchase behavior)
> 9. "Try [other person]", "contact [name] instead", "not me but talk to X" → `positive_referral` — **BUT** exclude "contact you"/"contact me"/"contact us"/"try you"/"try me": auto-responders and form acknowledgments are NOT referrals. **⚠️ July 9, 2026: also exclude "reaching out" (as in "thanks for reaching out")** — the word "reach" alone is too greedy and matches polite openers. Only count "reach [person]" / "reach out to [person]" with an actual target name/email as referral; "reaching out" alone is a greeting, not a referral signal.
> 10. **Person-left-with-referral:** "X is no longer with company, contact Y" → `positive_referral`
> 11. **⚠️ "Send that over" / "send it over":** `\bsend that over\b` and `\bsend it over\b` → `positive_soft`. A lead saying "Yes, please send that over" is asking for the promised material — same as "send more info." (Added Jul 20, 2026 — Gina replied "Yes, please send that over. I'm not quite sure I understand your service fully" and was classified as neutral.) Also expand `\bnot sure\b` to `\bnot\b.{0,20}\bsure\b` to catch "not quite sure" / "not even sure."
> 12. "Yes, let's book a call", "book an appointment", "feel free to book", "interested", "let's talk", "suggest some times", "suggest a time", "happy to chat", "open to hearing what", "how can we connect", standalone one-word agreements ("Sure", "OK", "Yep", "Absolutely", "Definitely", "Indeed") → `positive_interested` (⚠️ July 9, 2026: "book an appointment" and "feel free to book" — Ron @ ShyMarketing replied "Feel free to book an appointment... open to hearing what you do" and was classified as skip. "book a call" didn't catch "book an appointment". Also: "open to hearing what" is a positive-interest phrase from prospects who want to explore.) (⚠️ June 3, 2026: "Sure" was misclassified as neutral_question — one-word agreement to a cold email pitch IS positive intent. **June 11, 2026: extract the FIRST non-quoted segment BEFORE checking one-word agreements.** Replies often have the quoted original email on the SAME line: `"Sure    On Wed, Jun 3, 2026, 10:42 AM ..."` — `body.split('\n')[0]` still includes the quote. Fix: split on common quote markers (`On ... wrote:`, `-----Original Message-----`, `From:.*Sent:`) with regex, take segment[0], strip, THEN check first word. Pattern: `re.split(r'(On .+ wrote:|-----Original Message-----)', body, maxsplit=1)[0].strip()`)
> 13. Insults, reports, legal threats, profanity ("fuck off", "fuck you"), "do not contact me", "do not email me again" → `negative_hostile`
> 14. Everything else → `neutral_question`

**⚠️ Borderline cases:** Dead emails that redirect to generic addresses (info@, contact@) are `bounce`, NOT `positive_soft` or `positive_referral`. Only named-person referrals count as positive. See `references/classification-edge-cases.md` for the full catalog.

### July 20, 2026 — Classifier Gaps Found in Owned Audiences Sweep

| Bug | Root Cause | Fix |
|---|---|---|
| "Yes, please send that over. I'm not quite sure I understand" → `neutral_question` | "Yes, please send that over" is a clear positive directive but `\bsend (?:me )?(?:more |some )?info\b` doesn't match "send that over." Also `\bnot sure\b.*\bunderstand\b` fails on "not **quite** sure" — the word "quite" inserts between "not" and "sure". | ✅ Rule 11: add `\bsend that over\b` and `\bsend it over\b` as positive_soft signals. ✅ Expand "not sure" to `\bnot\b.{0,20}\bsure\b` to catch "not quite sure," "not even sure," etc. |
| Auto-responder "Thank you for contacting Strive Rx! We truly care about your health..." → `positive_interested` | The auto-responder guard gates on `\bthank you for (?:your email|contacting|reaching out)\b` and then checks for human signals in the remainder. But `re.split` on this pattern leaves a remainder that sometimes doesn't match any human signal check, causing fall-through to positive pattern matching. Florida Strivepharmacy (florida@strivepharmacy.com) was classified as `positive_interested` but is 100% an auto-responder. | ✅ After `\bthank you for (?:your email|contacting|reaching out)\b` matches, also check for auto-responder signals in the body remainder before falling through: `\bwill get back\b`, `\b(?:have )?safely received\b`, `\bcurrently assisting\b`, `\bplease know\b` → if present, return `auto_responder` even if no human signal is found. |
| "unsubscribe" (standalone) + "Remove me permanently" from recruiting leads → missed by ad-hoc classifier | `\bunsubscribe\b` is in hostile patterns but the word "unsubscribe" in Eric Edelsberg's reply matched the hostile check only because it was caught by the early hostile block. The Anna Spearman "Remove me permanently from your email list" pattern is unambiguous hostile. | ✅ These were caught by the inline classifier rules from the skill. The standalone `scripts/classify.py` script would need the same patterns. |

### Step 4: Compute rates

```
positive_reply_rate = (interested + soft + referral) / total_sent
positive_percent_of_replies = (interested + soft + referral) / net_replies
hostile_risk = negative_hostile / total_sent
unsub_rate = unsubscribe / total_sent
```

### Step 5: Flag Action Items

- **Top 10 positive_interested**: list lead names + reply bodies. Respond within 30 seconds.
- **Referrals**: add referred contacts to new outreach list
- **Hostile flags**: investigate, consider pausing inbox if genuinely angry
- **Unsubscribes**: confirm globally suppressed in Instantly

## Campaign Naming Clarification (July 2026)

**"Owned Audiences" campaigns are COLD email.** The name refers to the lead list source (owned/proprietary list), not audience warmth. These are cold prospects who have never interacted with the brand — same as SpeakerAgent or any other cold campaign. Do NOT frame Owned Audiences as "warm" in case studies, analytics, or Slack reporting. All campaigns in this system are pure cold outbound unless explicitly stated otherwise.

## Benchmarks

- **Good** positive reply rate: ≥1%
- **Great**: ≥2%
- **Hostile >0.3% or unsub >2%**: deliverability risk — pause campaign

## Important Gotchas

- Don't trust reply rate alone. 5% reply rate from spam-traps is worse than 2% from real buyers.
- Exclude OOO + bounce from denominators (not real replies).
- Small samples lie: <500 sent → too much noise. Wait for more volume.
- Classify only FIRST reply per lead. Later messages are conversation, not signal.

### CLI Data Pipeline Gotchas

- **Inbox response is wrapped:** `Instantly inbox replies` returns `{"ok": true, "data": [...]}` — parse `data` key, not top-level.
- **Reply timestamp field:** Use `last_reply_time`, not `replied_at` or `created_at`.
- **Lead ID for messages:** Must use `email_lead_id` from inbox, NOT `email_lead_map_id`. The map ID returns empty `{"history": []}`.
- **Message history is nested:** Response is `{"history": [...]}` not a bare array.
- **Reply body is HTML:** Strip tags with `re.sub(r'<[^>]+>', ' ', body)` for classification.
- **Security scan blocks pipes:** `Instantly | python3` gets blocked — write to file first. Heredocs also blocked — write scripts to files.
- **Rate limit Instantly:** Add 0.3-0.5s delay between `leads messages` calls.
- **Cross-reference with auto-reply daemon:** Check `/opt/data/scripts/auto_reply_state.json` to see if the daemon already handled each reply (by `email_lead_map_id`). Don't flag as "needs response" if already replied.
- **🚨 CLI "Authentication failed" is ambiguous — two distinct failure modes.** The Instantly CLI reports `"Error: Authentication failed. Check your API key."` for BOTH plan expiry AND invalid/rotated API key. The raw API response body distinguishes them: `{"message":"Plan expired!"}` (plan needs renewal) vs `{"message":"Invalid API Key"}` (401, key needs rotating in Instantly dashboard). **Diagnostic step when CLI reports auth failure:** make a raw HTTP GET to `https://server.Instantly/api/v1/campaigns?api_key=<key>` and read the JSON body. If the pipeline scans 0 inbox entries with no error, suspect this — the pipeline script silently returns empty when the API rejects the key. Confirmed Jul 28, 2026.
- **Daemon state file bloat:** The `replied_ids` list can grow to 100KB+ with massive duplication. The `replied_ids` key should have been removed in the May 18, 2026 fix but may persist. If the state file is huge, reset it to use only `replied_message_ids`: `{"replied_message_ids": [], "hostile_senders": [], "unsub_senders": []}`.
- **🚨 Cron campaign IDs go stale — verify before every sweep.** Scheduled cron jobs that hardcode campaign IDs (e.g., "pull replies from campaigns 3249954, 3249956") will silently sweep the wrong campaigns once campaigns complete and new ones launch. The Wednesday sweep should fetch ALL inbox replies unfiltered (`Instantly inbox replies`) and post-filter by `email_campaign_id` locally — Step 1 already prescribes this. If the cron prompt specifies specific campaign IDs, cross-check them against the active campaign list in `Instantly-cold-email` skill's campaign table before running. Confirmed Jul 29, 2026: cron specified 3249954/3249956 — neither is in the active campaign list (active IDs: 3577260, 3639259, 3652623, 3652624, 3691319, 3692104, 3607306). A stale-ID sweep = blind sweep = missed positives.

## What to Do Next

Respond to positive_interested immediately. Then load `experiment-design` to plan next iteration based on what worked.

**If <1% after 200+ sends**: the 1% rule failed. Run `email-deliverability-audit` next.

**Ongoing**: this is the Wednesday task in `cold-email-weekly-rhythm`. Run weekly.

**Campaign-specific monitoring**: see `references/campaign-slack-push.md` for the pattern to monitor a specific campaign and push positives to a dedicated Slack channel (live: SpeakerAgent → C0AFU5EH56X).

**⚠️ NOTE (July 11, 2026):** The `Instantly-cold-email` skill's campaign table is at 100KB and can no longer be patched. The live campaign tracking for the SpeakerAgent #3577260 campaign is now HERE in positive-reply-scoring (see Classifier Maintenance below). Until `Instantly-cold-email` is refactored, use this skill for all campaign #3577260 reply classification and monitoring.

## Phone Numbers & Enrichment (Jul 2026)

**Instantly MASKES all phone numbers for scraped/API-imported leads.** The `phone_number` field returns values like `+120****3289` — always masked. When asked for phone numbers, don't try Instantly. The only real phones come from email reply signatures (extracted from reply bodies via `re.findall` on stripped HTML). For bulk enrichment, ScraperCity (reconnect pending) or Composio contact search are the paths.

## Google Sheet Tracker (Jul 2026)

A master sheet tracks all campaigns at `https://docs.google.com/spreadsheets/d/1Pnllx-9B9QWUZYa-3Bj36nbve_dhBfCmx2mt5ZhHYrs/edit`. Updated via Composio MCP (`composio` skill → `COMPOSIO_MULTI_EXECUTE_TOOL` → `GOOGLESHEETS_VALUES_UPDATE`). Columns include Called 1-5 and Booked tracking. See `owned-audiences-email-reply` skill → `references/sheet-workflow.md`.

## here.now Publish (Jul 2026)

The `publish.sh` script requires the `file` binary which may not be installed on the VPS. If `publish.sh` fails with "requires file", use the REST API directly: POST to `/api/v1/publish` with `{"files":[...]}`, PUT to R2 presigned URL, POST to `finalizeUrl`. The `sha256sum` and `jq` binaries are available.

**SpeakerAgent campaign #3577260 now has an automated detection → classification → tracking → auto-reply pipeline.** The old cron `06848dd70c52` (silent-delivery failure to C0AFU5EH56X) is **PAUSED**. The new pipeline runs every 30 minutes.

### Architecture

```
Inbox (paginated) → Filter by campaign → Fetch message history
→ Filter operator replies → Classify (inline rules) → Track in state file
→ Auto-reply (high-confidence positives) → Dashboard
```

### Key Files

| File | Purpose |
|---|---|
| `/opt/data/scripts/speakeragent_pipeline.py` | Pipeline runner: paginate, classify, track, auto-reply |
| `/opt/data/scripts/speakeragent_dashboard.py` | Visualization dashboard: status counts, aging, flagging |
| `/opt/data/scripts/followup_engine.py` | Follow-up cadence: 3 biz day rotation, calendar check, both pipelines |
| `/tmp/speakeragent_followups.json` | State file: tracks every detected positive through lifecycle |
| Cron `148920b114d6` | Runs pipeline + dashboard every 30 min. Delivers to Slack thread. |
| Cron `ac18c07f72f9` | Runs follow-up cadence every 30 min. Sends next message in rotation. |

### Lifecycle Statuses

Every detected positive gets a status that tracks its journey:

- `awaiting_followup` — just detected, needs operator confirmation or auto-reply
- `replied` — auto-reply or follow-up sent via Instantly CLI, waiting for response. Tracked with `followup_count` (how many follow-ups sent so far) and `followup_sent_at` (last contact timestamp). Follow-up cadence engine advances this every 3 business days.
- `booked` — meeting booked (manually set by operator, OR auto-detected by Cal.com calendar check)
- `dead` — no response after follow-up, or lead backed out

Statuses are advanced manually by editing the state file or via the `speakeragent_pipeline.py` script. The dashboard reads status from the file.

### Auto-Reply Behavior

The pipeline auto-replies to high-confidence positives:

- **`positive_interested`** → Calendar booking link: `https://cal.com/usingaitoscale/power-partnerships-brainstorm-and-discovery`
- **`positive_soft`** → Info site + booking link: `https://aiintegraterz.com/stop-renting`

Replies are sent via Instantly CLI (`Instantly leads reply`) and tracked with `followup_message_id` in the state file. The lead's status advances to `replied` automatically.

### Running Manually

```bash
# Full pipeline run (10 inbox pages, ~200 entries)
python3 /opt/data/scripts/speakeragent_pipeline.py

# Dashboard only (no Instantly API calls)
python3 /opt/data/scripts/speakeragent_dashboard.py
```

### Gotchas

- **The bot is NOT in C0AFU5EH56X (#speakeragent-ai).** The cron delivers to the main Slack thread instead. Invite `@Hermes` to #speakeragent-ai to enable channel delivery.
- **Inline classifier rules are the canonical classification method.** The `scripts/classify.py` script has a ~30% error rate. The pipeline uses inline rules from `references/campaign-slack-push.md`, which are continuously hardened from sweep findings.
- **Tracked by message_id, not lead_id.** The pipeline's dedup uses `known_reply_message_ids` (per-message), so new replies from already-tracked leads are caught.
- **State file seeds from known positives.** After a reset or cold start, seed the file with known positive lead IDs from previous sweeps to avoid re-processing.

See `references/speakeragent-pipeline.md` for full architecture, auto-reply templates, and troubleshooting.

## Follow-Up Cadence (July 2026)

After the initial auto-reply or operator reply, leads enter a 3-business-day follow-up cadence. See `Instantly-cold-email` skill → `references/followup-cadence-engine.md`.

**How it works:**
1. Check calendar (Cal.com API, needs `CALCOM_API_KEY`) — if booked, mark `booked` and stop
2. Count business days (Mon-Fri only) since last contact
3. If >= 3 business days, send next message in 4-msg rotation
4. Different message each time, best-practices escalation

**Cron:** `ac18c07f72f9` (every 30 min)
**Engine:** `/opt/data/scripts/followup_engine.py`
**Dashboard:** `python3 /opt/data/scripts/followup_engine.py --dash`

Covers both SpeakerAgent (3577260) and Owned Audiences (3617053, 3607306) with separate message rotations.

## Classifier Maintenance

### June 24, 2026 — Classifier Bug Sweep (4 bugs fixed)

After running the weekly sweep on HVAC TX (#3442703), 4 out of 13 classifications were wrong (31% error rate). All fixed in `scripts/classify.py`:

| Bug | Root Cause | Fix |
|---|---|---|
| Form auto-responder → `positive_referral` | No Rule 4 check existed. "Thank you for contacting... we will contact you within" matched `"contact "` in referral patterns. | Added `form_auto_patterns` list returning `ooo` before unsubscribe check. |
| One-word "Sure" on same line as quote → `positive_soft` | `extract_reply_content()` required `\n` before `On ... wrote:`. HTML-stripped bodies have everything on one line. | Changed to `re.search()` without newline anchor. Added `match.start() > 0` guard to avoid splitting at position 0. |
| "Remove our email from list" → `neutral_question` | Pattern `"remove from"` requires contiguous match; "remove [our email] from" doesn't match. | Added `"remove our email"`, `"remove this email"`, `"remove email"`, `"no solicitation"` to unsub_patterns. |
| "not intrested" typo → `neutral_question` | Typo variant not in `notfit_patterns`. | Added `"not intrested"` and `"not intersted"`. |

**Lesson**: Always spot-check classifier output after a sweep — don't trust it blindly. Look for form auto-responders, "contact you" language, and typos that slip through.

### Austral HVAC — Missed Positive (June 8, 2026)

`services@australhvac.com` replied "Hi, send more info, please" on June 8. The daemon marked the message ID as processed but never generated a draft or sent a reply. Discovered June 24 — **16 days late**. 

**Root cause**: The daemon's `classify()` function differs from `scripts/classify.py`. It uses regex-based positive interest detection (`re.search(r'\binterested\b', body)` type patterns), which may not catch "send more info" as a soft positive. When the daemon silently misses a positive, there's no alert — the reply just sits unhandled.

**Pitfall**: Always cross-reference the daemon's `replied_message_ids` with actual reply classification when running the sweep. A message ID in the state file only means the daemon *scanned* it — not that it classified it correctly or generated a reply. Check `our_replies_after` count (SENT messages with timestamp AFTER the reply timestamp, excluding regular sequence emails) to confirm a reply was actually sent.

### Alpha Mechanical — Missed Positive (June 29, 2026) — SECOND OCCURRENCE — STILL UNHANDLED JUL 1

`jeff@alphamechanical.us` replied "Ok. Send me to information including cost please." on June 29. The daemon marked the message ID as processed but never generated a draft or sent a reply. Discovered July 1 — **2 days late, still unhandled as of July 1 evening sweep.**

**⚠️ Also unhandled: Source Rentals (jason@1sourcerentals.com)** — "Jason is no longer at the company. If you have any additional needs, please..." → referral to Nichole. Both TX HVAC positives need manual replies via Instantly CLI.

**Same root cause as Austral HVAC**: The daemon's `classify()` function uses simple regex patterns and does not catch "send me information including cost" or "no longer with company, contact..." as positive interest. `scripts/classify.py` correctly classifies both.

**Pattern**: Three missed positives now share the same structure — info/pricing/referral requests without the keyword "interested":
- Austral HVAC (Jun 8): "Hi, send more info, please" → missed
- Alpha Mechanical (Jun 29): "Ok. Send me to information including cost please." → missed  
- Source Rentals (Jun 29): "Jason is no longer at the company... please..." → missed (referral to Nichole)

**🚨 P0 RECOMMENDATION**: The daemon's classifier should delegate to `scripts/classify.py` rather than maintaining a separate, simpler regex-based classifier. Three confirmed misses in one month is a systemic gap, not an edge case. Every sweep finds another missed positive.

### July 9, 2026 — SpeakerAgent Campaign Monitoring Sweep (5 edge cases found)

Ran the SpeakerAgent Slack push workflow on campaign #3577260 (PR Agencies v2). Processed 68 leads (all new since last run), found **0 genuine positives**. But the inline classifier flagged several edge cases that need to be in the rules:

| Bug | Root Cause | Fix |
|---|---|---|
| Jayne Levy "no longer active... please resend this communication" → `positive_referral` | "is no longer" matched "is no longer active", then "reach" matched "reaching out" in "thanks for reaching out!". Dead-email redirect (same person, different email) got classified as referral. | ✅ Rule 9: exclude "reaching out" from the "reach" check. "Reach" should only match "reach [person]" / "reach out to [person]" with a target name/email. |
| "Fuck off and do not contact me again" → `skip` | Hostile patterns (rule 13) didn't include "fuck off" or "do not contact me". | ✅ Added "fuck off", "fuck you", "do not contact me" to hostile patterns. |
| "Thanks for your message! ... parental leave through June 2026" → `skip` | OOO patterns (rule 1) didn't include "parental leave". | ✅ Added "parental leave" to OOO patterns. |
| "Read over what you wrote. Would you hire you?" → `skip` | Notfit patterns (rule 6) didn't include this snarky rejection variant. | ✅ Added "would you hire you" to notfit patterns. |
| Multiple "out of the office" / "OOO" / "I am OOO" / "out of the office starting" → `skip` | "out of office" substring does match "out of the office" in most cases, but HTML entity artifacts (`&apos;`, `&#39;`) in some bodies may break the match. Adding explicit "out of the office" as a backup pattern would help. | 📝 Recorded for next sweep — not patched yet (low impact since these are non-positives regardless of classification). |

**Lesson**: The "reach" substring in referral detection is dangerously greedy — it matches "reaching out", "reach out if", "please reach", and dozens of polite email conventions that have nothing to do with referrals. The referral check should require a person-target context, not just bare substrings. Also: dead-email redirects to the SAME person at a different address are NOT referrals. Only redirects to a DIFFERENT person count.

After running the Wednesday sweep across 131 replies (all campaigns, last 7 days), 12 out of 39 positive-classified replies were wrong (31% error rate — same as June 24). All fixes implemented in `scripts/classify.py` same evening:

| Bug | Root Cause | Fix |
|---|---|---|
| "away from my email... back in office July 27" → `positive_interested` | OOO patterns missing "away from my email" and "taking time off" | ✅ Added to OOO patterns |
| "I will reply to your email as soon as I can" → `positive_referral` | OOO patterns missing this auto-reply phrasing | ✅ Added to OOO patterns |
| "thank you for reaching out. Can you send me some info about SpeakerAgent?" → `ooo` | `form_auto_patterns` caught "thank you for reaching out" BEFORE positive checks. Real human replies start politely then ask questions. | ✅ Gated: if interest signals follow ("send me info", "sounds interesting", "fees", etc.), fall through instead of returning OOO |
| "Thanks for reaching out. This sounds interesting. Please give me more info." → `ooo` | Same as above — "thanks for reaching out" in form_auto blocks positive recognition | ✅ Same gate fix |
| "delete whatever AI agent you're using for this slop" → `positive_referral` | Hostile patterns missing "slop" and "delete whatever" | ✅ Already in hostile patterns (added pre-Jul 8) |
| "Stop contacting me psycho!" → `unsubscribe` | Hostile patterns missing "psycho"; hostile check after unsubscribe | ✅ Added "psycho" to insult pre-check BEFORE unsubscribe |
| "no interested" (typo) → `positive_referral` | Notfit missing this typo variant | ✅ Added to notfit_patterns |
| "taking some time off with my kids" → `positive_referral` | OOO patterns missing "taking time off" | ✅ Already in OOO patterns |
| "Stop Ann Pitcher Pitcher Communications 630.234.4150" → `neutral_question` | Standalone "Stop" followed by proper noun not caught by `b_trim.startswith("stop ")` | ✅ Added `b_trim.split()[0] == "stop"` fallback |
| "I've officially retired... it's been a great ride" → `positive_soft` | Retirement auto-replies not in OOO patterns | ✅ Added retirement patterns to OOO |
| "I have no money for lead generation" → `neutral_question` | "no money" not in notfit_patterns | ✅ Added to notfit_patterns |
| `info@mbandassociatespr.com` holiday OOO → `positive_referral` | "office is closed for the July 4th holiday" — OOO patterns already had "office is closed" but referral patterns were matching before OOO | ✅ Already caught by OOO patterns (verified Jul 8)

### July 9, 2026 — Deep-Page Sweep (3 classification gaps + tracking blind spot)

Second pass through campaign #3577260 inbox pages 20-100 found 85 entries not in the posted_ids tracking file. Among them were 3 known positives that had been correctly identified in the July 8 sweep but never added to `/tmp/speakeragent_posted_ids.json`:

| Lead | Reply | Bug |
|---|---|---|
| Ron @ ShyMarketing | "Feel free to book an appointment... open to hearing what you do" | "book an appointment" not in rule 12 (only "book a call"). "open to hearing what" also missing. |
| Ben Bloch @ Venture PR | "do you have a demo video of how it works? Some examples or case studies?" | "how it works" not in rule 11 (only "how does it work"). "demo video", "case studies", "some examples" also missing. |
| Spark @ Campfire Group | "Tell me more" | ✅ Correctly caught by "tell me more" in rule 11 |

**Fixes applied:**
- Rule 11: added "how it works", "demo video", "case studies", "some examples"
- Rule 12: added "book an appointment", "feel free to book", "open to hearing what"

**Tracking blind spot discovered:** The posted_ids file only contained 34 IDs from inbox page 0. Pages 20-100 had 85 more entries from the July 1-3 launch burst, including 3 positives (Ron, Ben, Spark) that were never posted to Slack via this workflow. The operators knew about them from the July 8 sweep, but the automated Slack push silently skipped them.

**Lesson:** When doing the SpeakerAgent Slack push workflow, paginate through ALL inbox pages, not just page 0. The posted_ids tracking file accumulates entries from active monitoring but deep-page entries from launch bursts are easily missed. After a new monitoring run, verify that known positives (from the skill's campaign table) are present in the tracking file.

**Also — API key line number:** `Instantly_API_KEY` is at line 404 of `/opt/data/.env`. Commands that use `head -N` to read the file will truncate the key. Use `grep Instantly_API_KEY /opt/data/.env | cut -d= -f2` without line limits, or use the `search_files` tool to find the exact line.

### July 9, 2026 (second session) — Cron Silent Failure + Missing Positive Pattern

North Star Consults replied to SpeakerAgent campaign #3577260 with "Yes, that would be great. How can we connect?" (from nsconsultingli@gmail.com, replying on behalf of info@northstarconsults.com). The cron job didn't post it to Slack channel C0AFU5EH56X.

**Root cause — two bugs:**

1. **Missing classification pattern:** "How can we connect?" was not in the `positive_interested` patterns in either SKILL.md rule 12 or campaign-slack-push.md. The phrase is a direct call-to-action equivalent to "let's talk" / "book a call." Fixed in both locations.

2. **Bot not in target Slack channel:** The cron `06848dd70c52` has `deliver: local` — it uses `send_message` internally to push to `slack:C0AFU5EH56X`. But the bot hasn't been invited to that channel, so `send_message` returns `channel_not_found` silently. The dedup file grows (141 IDs tracked) and no positives reach the channel. The cron status shows `ok` with no delivery error because errors from `send_message` inside the cron prompt aren't surfaced. **Fix:** Added pre-flight channel verification to `references/campaign-slack-push.md` recipe (step 1) and a dedicated pitfall documenting the silent-failure pattern.

**4 overnight replies analyzed (Jul 9 8:05-8:23 AM ET):** ① info@theformeytouch.com — spam verification challenge → bounce. ② info@northstarconsults.com — "Yes, that would be great. How can we connect?" → 🔥 BOOKED (missed). ③ kerry@kerrybarrett.com — "I'm traveling" OOO auto-reply → OOO. ④ team@internetmarketingbiz.com — "Thank you for reaching out" auto-responder → OOO.

### July 11, 2026 — Campaign Sweep Cron Run (7 false positives + operator-reply filtering bug)

Full inbox sweep (200 entries, pages 0-9) of campaign #3577260. 148 campaign entries total. posted_ids file was empty (first run after reset) → all 148 classified fresh. **5 genuine positives found** (North Star Consults "How can we connect?", Steve Kayser "send me info on your company", Luke Joerger "send me info and meeting link", Deborah Brosseau "send me info about SpeakerAgent", Karen Steele "Sure"). **7 false positives caught:**

| Bug | Root Cause | Fix |
|---|---|---|
| Kerry Barrett "I'm traveling, book a call" → `positive_interested` | "book a call" matched BEFORE OOO check. "I'm traveling" not in OOO patterns. Also: Calendly link in auto-reply signature triggered "calendar link" match. | ✅ Added "traveling" + "limited access" to OOO. **Rule ordering: OOO MUST be checked before positive patterns** — auto-reply Calendly links are NOT booking signals. |
| WebHEQ empty reply → `positive_interested` | Reply body contained only the quoted operator message — no lead-authored text. After stripping quotes, body was empty but one-word match in quoted text triggered. | ✅ Added empty-body check: if body after quote stripping is empty/whitespace-only, skip. |
| MBarnett "office closed for holiday... I will be OOO" → `positive_referral` | "will be OOO" didn't match "i am ooo" pattern. Holiday OOO matched referral because "reach" in "reaching me" triggered. | ✅ Added "will be ooo" / "i will be ooo" to OOO patterns. |
| Catalyst Media Factory "out of office Thu-Fri... contact [colleague]" → `positive_referral` | Temp 2-day OOO with colleague coverage matched "contact [name]" as referral. Person still works there — this is NOT a referral. | ✅ Rule: if "out of office" / OOO signal present, colleague coverage ≠ referral. Only "no longer with" / permanent departure counts as referral. |
| Sam Ideadecanter "out of office until Jul 7... contact laura@" → `positive_referral` | Same as above. Vacation OOO with temp coverage. | ✅ Same fix. |
| Offleash PR "canned.response... contact Robin Bulanti" → `positive_referral` | Form auto-responder from `info+canned.response@offleashpr.com`. "contact Robin" is generic template language. | ✅ "canned.response" in from-address is an auto-responder signal. Skip. |
| Jayne Pinktree "no longer active... resend to jayne@youvegotjayne.com" → `positive_referral` | Dead-email redirect to SAME person (Jayne → Jayne) at different address. Already documented July 9, re-confirmed. | ✅ Already fixed in July 9 sweep. |

**Operator-reply filtering bug:** Several leads had operator follow-up replies (e.g., Lynn @ pkpublicrelations — operator followed up after her vacation OOO). The latest REPLY in history was the operator's, not the lead's. Classifying the latest REPLY picks up the operator's message instead of the lead's original reply. **Fix:** Before classification, filter out all REPLY messages whose `message_id` contains our sending domains. Use the EARLIEST remaining REPLY (the original lead reply), not the latest. If no non-operator REPLY remains, skip the lead.

**OOO pattern gaps filled:** "traveling" + "travelling" (UK spelling) + "limited access", "will be ooo", "i will be ooo", "currently away", "summer hours", "away from my email", "i will reply to your email as soon".

**posted_ids initialization:** File was empty → 148 leads all treated as new on first run. After a reset or first run, the posted_ids file must be seeded with all previously known lead IDs (from the skill's campaign table or prior manual sweeps) to prevent mass re-posting.

### July 11, 2026 — Second Sweep (1 new positive + 6 keyword-driven false positives)

Second full sweep of campaign #3577260 (148 entries, posted_ids now at 34 from first sweep). 114 new leads processed. **1 genuine positive found** (Sam Frontera — adjacent-service interest). **6 keyword-driven false positives caught** — all from greedy positive_soft/interested keyword matching that fired before auto-responder/negative context checks:

| Bug | Root Cause | Fix |
|---|---|---|
| Dragons 88 "check our website to learn more about us" → `positive_soft` | "learn more" keyword matched form auto-responder boilerplate. Every form response says "learn more about us." | ✅ Gated: "learn more" only counts as positive_soft if NOT preceded by form-auto language ("thank you for reaching out", "we will respond", "check out our website to learn more"). If the body has auto-responder signals, "learn more" is NOT a positive. |
| Jim Bogert "my prices are reasonable because I moved" → `positive_soft` | "price" keyword matched not-fit context. He's explaining why he doesn't need sales help, not asking about pricing. | ✅ Gated: "price"/"pricing"/"cost"/"fees" only counts as positive_soft when it's a QUESTION or REQUEST ("what's your pricing?", "can you let me know the fees?"). Declarative statements about one's own prices ("my prices are...", "our pricing is...") are NOT positive. |
| Brandignity "Before I hop on any calls, is this an AI agent campaign?" → flagged for "call" | "call" keyword matched skeptical neutral question. He's questioning legitimacy, not booking. | ✅ "call" alone is too broad — requires proximity to positive intent ("let's hop on a call", "book a call", "set up a call"). Bare "call" in a skeptical/defensive context is neutral. |
| Pressfinity/ExpertizeMe unsolicited counter-pitch "We publish 300+ articles... we organize 100+ awards" → flagged for "calendly/meeting/call" | Prospect is pitching HER service back, not expressing interest. "calendly"/"meeting" appear in signature/outro of an unsolicited sales pitch. | ✅ If the body reads like a sales pitch (multiple service descriptions, "we offer", "we provide", "we organize"), it's a counter-pitch, not interest. The keywords are in the seller's boilerplate, not the buyer's inquiry. |
| Melinda Jackson "I'm at the beach with my family... I'll still be checking email" → flagged for "calendar/sure" | Beach vacation OOO with "sure" in quoted original message. OOO already caught but positive keyword scan ran anyway. | ✅ Existing OOO-first ordering should prevent this — but if OOO check uses "vacation" and body says "beach" instead, it can miss. Added "beach" to OOO patterns. |
| Arianna Smith "please complete this form to request a custom proposal" → flagged for "website" | Form auto-responder directing to a proposal form. "website" keyword is too broad. | ✅ "website" in a form/auto-responder context ("complete this form", "request a proposal") is NOT positive_soft. Only "what's your website?" (question format) counts. |

**New genuine positive pattern — adjacent-service interest:**
Sam Frontera (sfrontera@exclusivepr.biz): "Not sure if this means you help with sales but that's what I am looking for. I don't need help booking interviews." — She's not interested in the PR/podcast pitch but IS interested in sales help. This is adjacent-service interest — a soft positive because she's engaging and expressing a need the company might fill, just not the one pitched.

**Keywords that need context gates (too greedy as bare substrings):**
- `learn more` — only positive if NOT in a form auto-responder
- `price` / `pricing` / `cost` / `fees` — only positive in QUESTION format, not declarative
- `call` — only positive with positive-intent proximity ("book a call", "hop on a call"), not bare
- `website` — only positive in question format ("what's your website?"), not in form CTAs
- `calendly` / `meeting` — only positive in buyer inquiry context, not seller counter-pitch

**Rule ordering reinforcement:** Auto-responder detection (form language, "thank you for reaching out", "we will respond") MUST run before ANY positive keyword matching. The July 11 morning sweep already established OOO-first ordering; this extends it to all auto-responder patterns. A reply that starts with "Thank you for reaching out" and then says "learn more" or "contact us" is an auto-responder, period — no positive keywords in the body override that.

**posted_ids file reached full coverage:** 148/148 campaign #3577260 entries now tracked.

### July 11, 2026 (evening cron run) — Cold-start detection gap + posted_ids format fragility

Scheduled cron run (23:38 UTC) found posted_ids file with only 5 entries after a prior reset. All 144 remaining leads were treated as "new," triggering 144 API calls for message history. **0 genuinely new positives found** — all 9 known positives from July 7-8 were already handled by operators, and the 7 July 9+ leads were all non-positive (unsubscribe, notfit, hostile, OOO/skip).

**Root cause — two issues:**

1. **posted_ids file format changed:** The file contained `["posted_ids", "last_run", 4102214369, ...]` — string metadata keys mixed with numeric IDs. This indicates the file was reset by a process that wrote metadata alongside IDs rather than a clean list. The parser must handle both formats (pure list and mixed list-with-keys).

2. **No cold-start detection:** When posted_ids has < 10% of expected entries (5 entries vs 148 known campaign entries), the cron should recognize this as a cold-start/reset condition and warn. Rather than silently re-processing all 144 leads, it should seed the tracking file from known data or report the anomaly.

**Also confirmed:** Inbox across pages 0-180 (10 pages) contains ~200 total entries, with ~148 for campaign #3577260. The pagination through page 180 is sufficient for full coverage.

### July 20, 2026 — Owned Audiences Sweep (2 classification gaps found)

Cross-campaign sweep of all three Owned Audiences campaigns (#3617053, #3652623, #3652624). 100 inbox entries → 72 OA → 16 real leads after auto-prefix filtering. 12 confirmed positives total, 1 booking (Gina). Two classification gaps found:

| Bug | Root Cause | Fix |
|---|---|---|
| "not quite sure I understand" → `neutral_question` | `\bnot sure\b` requires "not" and "sure" adjacent. "not quite sure" breaks the adjacency. Also `\bsend (?:me )?(?:more \|some )?info\b` doesn't match "send that over." | ✅ Added `\bnot quite (?:sure\|understand)\b` to positive_soft patterns. "not quite sure" is always a clarification request, never a rejection. |
| "will get back to you" auto-responder → `positive_interested` | `\bwe.ll get back\b` matches "we'll" (`.` = apostrophe) but NOT "will" — "will get back" is a non-contracted auto-responder variant used by customer-service teams. Also: "safely received your email" is a CS signal not in OOO/auto patterns. | ✅ Added `\bwill get back\b`, `\bsafely received\b`, and `\bassisting other\b` to auto-responder patterns. **Rule ordering**: auto-responder detection MUST run before positive keyword matching — CS auto-replies contain words like "care," "help," and "phone" that greedy positive patterns match. |

Podcast campaign #3639259 launched today (13 replies in first 8 hours). Classification sweep found:

| Bug | Root Cause | Fix |
|---|---|---|
| "I'm travelling with limited bandwidth" → `neutral_question` | "travelling" (UK spelling, two L's) not in OOO patterns. Only "traveling" (US spelling) was covered. Chris @ entrepreneursforimpact.com misclassified. | ✅ Added "travelling" to OOO patterns (see July 11 OOO gap list above). |

**Also confirmed:** Forwarded SENTs mislabeled as REPLY — Mike Billoni (#3577260) inbox entry showed `last_reply_time` today, but the actual message was Ephraim's operator follow-up from speakeragent.ai, not a new lead reply. Already documented in `Instantly-cold-email` pitfalls.

### July 20, 2026 (evening) — Legitimacy-Concern False Positive + Thread-Context Issue

Daily cross-campaign sweep of 6 today replies across 4 campaigns. Two classifier gaps found:

| Bug | Root Cause | Fix |
|---|---|---|
| Aknanda "the link is still not working, which raises some concerns for me about the legitimacy... could you please send me some case studies" → `positive_soft` | `classify.py` saw "send me" + "case studies" and flagged as positive. But "raises concerns about legitimacy" is a **skepticism/suspicion signal** — the person is questioning whether the business is real. Requesting proof when you doubt legitimacy is NOT interest, it's a demand for evidence. The `\braises (?:some )?concerns\b` or `\blegitimacy\b` pattern indicates the person's guard is up. | ✅ Added pre-check: if body contains `\braises (?:some )?concerns?\b` near `\blegitimacy\b` or `\bprofessionalism\b`, classify as `neutral_question` (skeptical) BEFORE any "send me" positive_soft matching. A person demanding proof because they think you might be a scam is not expressing interest. |
| Nicole Wald 2-reply thread: first reply "Happy to chat" (positive_interested), latest reply "I'll be able to get to this at the start of August" (deferral/positive_soft) → classification shifts depending on which reply body is pulled | `classify.py` classifies a single reply body. In multi-reply threads, the latest reply can change the classification (from interested to soft/deferred). The skill already says "classify only the FIRST reply per lead" but automation scripts often pull the latest. | 📝 Workflow reminder: always classify the **earliest non-operator, non-OOO REPLY** in the thread, not the latest. The first human reply is the cold-email signal; everything after is conversation. If the first reply is OOO/bounce and a later reply is human, classify the later one. Nicole's first reply "Happy to chat" = positive_interested; her deferral doesn't undo that. |

**Also noted:** `classify.py` has ~30% error rate (confirmed again — 1 of 6 misclassified: Aknanda). The inline rules in this SKILL.md remain the canonical classification method.

### July 22, 2026 — Quote-Stripping Failure (47% false positive rate in Wednesday sweep)

Cross-campaign Wednesday sweep across 81 non-SpeakerAgent replies. The inline classifier's `strip_quotes()` function failed to remove quoted original email content from multiple common reply formats, causing the classifier to match keywords from the *original cold email* rather than the lead's reply. **8 of 17 classifier positives (47%) were false positives.** All 8 false positives showed `\bcase stud(?:y|ies)\b` as the reason — the cold email copy mentions "case studies" and the quoted email leaked through.

**Root cause:** `re.split(r'(On .+ wrote:|-----Original Message-----|From:.*Sent:)', body, maxsplit=1)` misses three common reply formats:

| Format | Example | Why missed |
|---|---|---|
| **Outlook reply** | `Yes, I'd be open to see what you have. Jeff From: Aubrey Scott <aubrey@strategybasesc.info> Date: Thursday, July 16, 2026 at 8:39 AM To: jeff.dillon@usmenshealth.com Subject: [Ext] nearby...` | `From:.*Sent:` requires "Sent:" but Outlook format uses "Date:" / "To:" / "Subject:" without "Sent:" |
| **Apple Mail / Gmail compact** | `Sure! On Thu, Jul 16, 2026, 9:00 AM Julia Castillo < julia@horizonstepfl.info > wrote:` | This DOES match `On .+ wrote:` but the `<` in email breaks when HTML entities (`&lt;`) are present — `re.sub(r'<[^>]+>', ' ', body)` stripping leaves angle brackets as spaces, and the regex can't find the close |
| **Gmail mobile** | `yes On Wed, Jul 15, 2026 at 8:20 AM Penelope Sanchez < penelope@scaledeskct.info > wrote:` | Same HTML-stripping issue with angle brackets becoming spaces |

**Also affected:** support@ and info@ shared-inbox auto-acknowledgments ("Sure!", "yes", "Sure feel free to send it") from ticket systems were classified as positive because the bare reply word survived quote-stripping. These are likely auto-responders, not human replies.

**Fix pattern (to apply in inline classifiers):**
```python
def strip_quotes(body):
    """Extract lead-authored text, removing quoted original email in all common formats."""
    markers = [
        r'On .+ wrote:',                              # Gmail web, Apple Mail
        r'-----Original Message-----',                 # Outlook/Exchange classic
        r'From:.*?Date:.*?(?:To:|Subject:)',           # Outlook without "Sent:"
        r'> On .+',                                     # Quoted in plain text reply
        r'On .+ at \d{1,2}:\d{2} [AP]M',              # Gmail/Apple compact (no "wrote:")
    ]
    for marker in markers:
        parts = re.split(marker, body, maxsplit=1, flags=re.IGNORECASE)
        body = parts[0].strip()
    # Also strip "From: ... Sent:" if still present
    body = re.split(r'From:.*?Sent:', body, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    return body
```

**After applying the fix:** 8 false positives eliminated. The corrected classification: 0 positive_interested, 8 positive_soft (all from individual or semi-individual leads), 1 positive_referral, 1 negative_notfit, 5 unsubscribes, 4 ooo auto-responders reclassified from false positives.

**Lesson:** Always apply `strip_quotes()` to the FULL reply body BEFORE running any pattern matching. The quoted original email contains the cold email copy itself — and that copy is designed to sound positive. Classifying based on keywords from the cold email rather than the lead's actual reply is the single biggest source of false positives. See `references/quote-stripping-patterns.md` for the full catalog of reply formats and the canonical `strip_quotes()` implementation.

**⚠️ Also discovered — shared-inbox "Sure!" replies may be ticket-system auto-acks.** When `support@`, `info@`, or `contactus@` addresses reply with one-word agreements like "Sure!" or "yes," cross-reference with other replies from the same campaign. If multiple shared inboxes all reply with similar short acknowledgments in the same time window, they're likely auto-responders, not human replies. The Coaching OA campaign (#3617053) had 6 such replies in a 3-day window — all from support@/info@/contactus@ addresses, all with one-word or very short acknowledgments.
